"""
Queue Processor Watchdog - Django Management Command

Continuously polls database for pending files and executes batch processing.

CRITICAL INTEGRATION:
- Coordinates with Story 1.7 file_monitor (no race conditions)
- Integrates with Story 1.6 batch_process (multiprocessing preserved)
- Uses atomic database transactions to prevent concurrent processing

Usage:
    python manage.py queue_processor
    python manage.py queue_processor --poll-interval=10
    python manage.py queue_processor --schema-id=1
"""

import signal
import sys
import time
from typing import List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from loguru import logger

from apps.catalog.models import File, Schema
from samplify.management.commands.batch_process import Command as BatchCommand


class Command(BaseCommand):
    """Django management command for queue processor watchdog service."""

    help = "Process queued files from database (Story 1.8)"

    def __init__(self):
        super().__init__()
        self.running = True
        self.batch_processor = None

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--poll-interval",
            type=int,
            default=5,
            help="Polling interval in seconds (default: 5)",
        )
        parser.add_argument(
            "--schema-id",
            type=int,
            help="Process only this schema (default: active schema)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10,
            help="Maximum files to process per batch (default: 10)",
        )

    def handle(self, *args, **options):
        """Main command handler - runs as blocking background service."""
        poll_interval = options["poll_interval"]
        schema_id = options.get("schema_id")
        batch_size = options["batch_size"]

        # Get schema
        try:
            if schema_id:
                schema = Schema.objects.get(id=schema_id)
            else:
                schema = Schema.objects.get(is_active=True)
        except Schema.DoesNotExist:
            if schema_id:
                raise CommandError(f"Schema with ID {schema_id} does not exist")
            else:
                raise CommandError("No active schema found. Please activate a schema first.")

        logger.info(f"Queue processor started for schema: {schema.name}")
        logger.info(f"Polling interval: {poll_interval} seconds, Batch size: {batch_size}")

        # Setup graceful shutdown handling
        self._setup_signal_handlers()

        # Initialize batch processor
        self.batch_processor = BatchCommand()

        # Main processing loop
        while self.running:
            try:
                # Poll and process pending files
                processed_count = self._poll_and_process(schema, batch_size)

                if processed_count > 0:
                    logger.info(f"Processed {processed_count} files in this iteration")

                # Sleep before next poll
                time.sleep(poll_interval)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received - shutting down...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                # Continue running after logging error
                time.sleep(poll_interval)

        # Cleanup
        if self.batch_processor:
            try:
                self.batch_processor.cleanup_workers()
            except Exception:
                pass

        logger.info("Queue processor stopped")

    def _setup_signal_handlers(self):
        """
        Setup graceful shutdown on SIGINT/SIGTERM.

        Ensures clean shutdown when service is interrupted.
        """

        def signal_handler(sig, frame):
            signal_name = "SIGINT" if sig == signal.SIGINT else "SIGTERM"
            logger.info(f"Received {signal_name} - initiating graceful shutdown...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _poll_and_process(self, schema: Schema, batch_size: int) -> int:
        """
        Poll database for pending files and process them.

        Uses select_for_update with skip_locked to prevent race conditions
        with file monitor or other queue processor instances.

        Args:
            schema: Schema to filter files by
            batch_size: Maximum number of files to process

        Returns:
            Number of files processed in this iteration
        """
        try:
            # Atomic transaction to prevent race conditions
            with transaction.atomic():
                # Query pending files with row-level locking
                # skip_locked=True prevents blocking on files locked by other transactions
                pending_files = list(
                    File.objects.select_for_update(skip_locked=True)
                    .filter(
                        processing_status="pending",
                    )
                    .order_by("created_at")[:batch_size]
                )

                if not pending_files:
                    # No pending files - nothing to do
                    return 0

                logger.info(f"Found {len(pending_files)} pending files to process")

                # Mark files as processing
                file_ids = [f.id for f in pending_files]
                File.objects.filter(id__in=file_ids).update(processing_status="processing")

            # Process files outside transaction (can take time)
            self._process_files(pending_files, schema)

            return len(pending_files)

        except Exception as e:
            logger.error(f"Error in poll_and_process: {e}")
            return 0

    def _process_files(self, files: List[File], schema: Schema):
        """
        Process files using batch processor from Story 1.6.

        Preserves multiprocessing patterns (CR2) by delegating to BatchCommand.

        Args:
            files: List of File objects to process
            schema: Schema with processing rules
        """
        try:
            # Schedule workers if not already running
            if not self.batch_processor.running_processes:
                self.batch_processor.schedule_workers()

            # Distribute jobs to worker deques
            self.batch_processor.distribute_jobs(files, schema)

            # Wait for completion
            self.batch_processor.wait_for_completion()

            logger.info(f"Batch processing completed for {len(files)} files")

        except Exception as e:
            logger.error(f"Error processing files: {e}")

            # Mark files as failed
            with transaction.atomic():
                File.objects.filter(id__in=[f.id for f in files]).update(processing_status="failed")
