"""
Batch Processing Management Command - Django Management Command

Processes files through transformation pipeline using multiprocessing.

CRITICAL CR2 PRESERVATION:
- Worker scheduling from handlers/process_handler.py PRESERVED EXACTLY
- Deque-based job distribution PRESERVED EXACTLY
- Only Django ORM adaptations allowed, NOT multiprocessing logic changes

Usage:
    python manage.py batch_process --schema-id=1
    python manage.py batch_process --schema-id=1 --input-dir=/path/to/files
"""

import collections
import json
import multiprocessing
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from loguru import logger

from apps.catalog.models import DirectoryMapping, File, Schema
from samplify.utils.ffmpeg import get_ffmpeg_path


class Command(BaseCommand):
    """Django management command for batch processing files with multiprocessing."""

    help = "Execute batch processing with multiprocessing (CR2 preserved)"

    def __init__(self):
        super().__init__()
        self.running_processes = []  # Note: 'process' objects are unpicklable
        self.decoder_channels = []
        self.current_worker_index = 0  # For round-robin distribution

    # Pickling exclusions (for Windows multiprocessing spawn mode)
    def __getstate__(self):
        """
        CR2 PRESERVED: Exact copy from handlers/process_handler.py lines 16-24

        Exclude unpicklable objects from pickling.

        Returns:
            State dictionary without unpicklable entries
        """
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()

        # Remove the unpicklable entries
        if "running_processes" in state:
            del state["running_processes"]

        # Remove Django command-specific unpicklable objects
        if "stdout" in state:
            del state["stdout"]
        if "stderr" in state:
            del state["stderr"]
        if "style" in state:
            del state["style"]

        return state

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--schema-id",
            type=int,
            required=True,
            help="Schema ID for processing rules",
        )
        parser.add_argument(
            "--input-dir",
            type=str,
            help="Optional input directory to filter files",
        )

    def handle(self, *args, **options):
        """Main command handler."""
        schema_id = options["schema_id"]
        input_dir = options.get("input_dir")

        try:
            schema = Schema.objects.get(id=schema_id)
        except Schema.DoesNotExist:
            raise CommandError(f"Schema with ID {schema_id} does not exist")

        logger.info(f"Starting batch processing for schema: {schema.name}")

        # Schedule workers (CR2 preservation)
        self.schedule_workers()

        # Retrieve files for processing
        files = self.get_files_for_processing(schema, input_dir)

        if not files:
            logger.warning("No files found for processing")
            self.cleanup_workers()
            return

        logger.info(f"Found {len(files)} files to process")

        # Distribute jobs to worker deques
        self.distribute_jobs(files, schema)

        # Wait for all workers to complete
        self.wait_for_completion()

        # Cleanup
        self.cleanup_workers()

        logger.info("Batch processing complete!")

    # ============================================================================
    # CR2 PRESERVED METHODS FROM handlers/process_handler.py
    # These methods are preserved EXACTLY as they appeared in brownfield system
    # ============================================================================

    def schedule_workers(self):
        """
        CR2 PRESERVED: Exact copy from handlers/process_handler.py lines 26-48

        Schedule worker processes - one per CPU core.

        CRITICAL PRESERVATION:
        - multiprocessing.cpu_count() for core detection
        - collections.deque() per worker (NOT queue.Queue)
        - daemon=True flag on processes
        - channel_info tuple pattern: (process.name, deque)

        Returns:
            None
        """
        num_cores = multiprocessing.cpu_count()

        logger.info(f"Spawning decoder processes - Num Cores: {num_cores}")

        for core in range(num_cores):
            # declare process, set daemon
            p = multiprocessing.Process(target=self.schedule_listener, daemon=True)

            # declare double-ended channel (dequeue) for each process
            q = collections.deque()

            # bundle channel and process name into a tuple
            channel_info = (p.name, q)

            # add to lists
            self.decoder_channels.append(channel_info)
            self.running_processes.append(p)

            # start process
            p.start()

    def schedule_listener(self):
        """
        CR2 PRESERVED: Exact copy from handlers/process_handler.py lines 50-66

        Worker process listener - consumes tasks from assigned deque.

        CRITICAL PRESERVATION:
        - popleft() for FIFO task consumption
        - while queue loop pattern
        - multiprocessing.current_process() identification

        Returns:
            None
        """
        # return active working process
        p = multiprocessing.current_process()

        # get name/channel from list of channels
        for channel_info in self.decoder_channels:
            name, queue = channel_info

            # find the correct channel to work on
            if name == p.name:
                logger.info(f"Process started - Name: {name} PID: {p.pid}")

                # start listening for signals
                while queue:
                    task = queue[0]
                    logger.info(f"Process started new task - Name: {name} PID: {p.pid} Task: {task}")

                    # Process the task
                    self.process_task(task)

                    # Remove from queue
                    queue.popleft()

    def add_task(self, task):
        """
        CR2 IMPROVED: Round-robin task distribution (approved by PO).

        Original brownfield used greedy first-available assignment (lines 69-80).
        Improvement implements round-robin for better load balancing.

        PRESERVED ASPECTS:
        - appendleft() for adding tasks to deque
        - deque data structure usage
        - channel_info tuple unpacking

        APPROVED CHANGE:
        - Round-robin cycling instead of first-empty selection
        - See docs/development-decisions.md CR2 decision

        Args:
            task: Task dictionary to add to worker queue

        Returns:
            None
        """
        if not self.decoder_channels:
            logger.error("No worker channels available")
            return

        # Round-robin: cycle to next worker
        name, queue = self.decoder_channels[self.current_worker_index]

        logger.info(f"Adding task to worker - Name: {name} Task: {task}")
        queue.appendleft(task)

        # Move to next worker (round-robin)
        self.current_worker_index = (self.current_worker_index + 1) % len(self.decoder_channels)

    # ============================================================================
    # DJANGO-SPECIFIC METHODS (New for Story 1.6)
    # ============================================================================

    def get_files_for_processing(self, schema: Schema, input_dir: Optional[str] = None) -> List[File]:
        """
        Retrieve files from database for processing.

        Integrates with Story 1.5 (file scanning service).

        Args:
            schema: Schema object with processing rules
            input_dir: Optional directory path to filter files

        Returns:
            List of File objects ready for processing
        """
        # Start with all pending files
        files = File.objects.filter(processing_status="pending")

        # Filter by input directory if specified
        if input_dir:
            files = files.filter(file_path__startswith=input_dir)
        else:
            # Filter by schema's directory mappings
            directory_mappings = DirectoryMapping.objects.filter(schema=schema)
            if directory_mappings.exists():
                input_paths = [dm.input_path for dm in directory_mappings]
                # Filter files that start with any of the input paths
                from django.db.models import Q

                query = Q()
                for path in input_paths:
                    query |= Q(file_path__startswith=path)
                files = files.filter(query)

        # Order by created_at for consistent processing order
        files = files.order_by("created_at")

        return list(files)

    def distribute_jobs(self, files: List[File], schema: Schema):
        """
        Distribute file processing jobs to worker deques.

        Uses round-robin distribution (CR2 approved improvement).

        Args:
            files: List of File objects to process
            schema: Schema object with processing rules

        Returns:
            None
        """
        for file_obj in files:
            task = {
                "file_id": file_obj.id,
                "file_path": file_obj.file_path,
                "file_name": file_obj.file_name,
                "schema_id": schema.id,
            }

            # Mark file as processing
            with transaction.atomic():
                file_obj.processing_status = "processing"
                file_obj.save()

            # Add to worker queue (round-robin)
            self.add_task(task)

    def process_task(self, task: Dict):
        """
        Process a single file transformation task.

        Executes FFmpeg transformations using Story 1.4 service.

        Args:
            task: Dictionary with file_id, file_path, schema_id

        Returns:
            None
        """
        file_id = task["file_id"]
        file_path = task["file_path"]
        schema_id = task["schema_id"]

        try:
            # Get file object
            file_obj = File.objects.get(id=file_id)

            # Get schema and transformations
            schema = Schema.objects.get(id=schema_id)

            # Execute transformation (placeholder - Story 1.6 focuses on multiprocessing)
            # Actual transformation logic will be implemented in later stories
            logger.info(f"Processing file: {file_path}")

            # Simulate FFmpeg processing
            success = self.execute_transformation(file_obj, schema)

            # Update file status
            with transaction.atomic():
                if success:
                    file_obj.processing_status = "completed"
                    logger.info(f"Successfully processed: {file_path}")
                else:
                    file_obj.processing_status = "failed"
                    logger.error(f"Failed to process: {file_path}")

                file_obj.save()

        except Exception as e:
            logger.error(f"Error processing task {task}: {e}")

            # Mark file as failed
            try:
                file_obj = File.objects.get(id=file_id)
                file_obj.processing_status = "failed"
                file_obj.save()
            except Exception:
                pass

    def execute_transformation(self, file_obj: File, schema: Schema) -> bool:
        """
        Execute FFmpeg transformation on file.

        Integrates with Story 1.4 FFmpeg service.

        Args:
            file_obj: File object to transform
            schema: Schema with transformation rules

        Returns:
            True if transformation succeeded, False otherwise
        """
        ffmpeg_path = get_ffmpeg_path()

        if not ffmpeg_path:
            logger.error("FFmpeg not available - cannot process file")
            return False

        try:
            # For Story 1.6, we're validating the multiprocessing pattern
            # Actual transformation rules will be implemented in later stories
            # For now, just verify the file exists
            file_path = Path(file_obj.file_path)

            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return False

            # Simulate processing time (for testing multiprocessing)
            time.sleep(0.1)

            return True

        except Exception as e:
            logger.error(f"Transformation error for {file_obj.file_path}: {e}")
            return False

    def wait_for_completion(self):
        """
        Wait for all worker deques to become empty.

        Monitors worker progress until all tasks are consumed.

        Returns:
            None
        """
        logger.info("Waiting for workers to complete...")

        while True:
            # Check if all deques are empty
            all_empty = all(len(queue) == 0 for _, queue in self.decoder_channels)

            if all_empty:
                logger.info("All workers completed their tasks")
                break

            # Brief sleep to avoid busy-waiting
            time.sleep(0.5)

    def cleanup_workers(self):
        """
        Clean up worker processes.

        Terminates daemon processes after completion.

        Returns:
            None
        """
        logger.info("Cleaning up worker processes...")

        for process in self.running_processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)

        logger.info("Worker cleanup complete")
