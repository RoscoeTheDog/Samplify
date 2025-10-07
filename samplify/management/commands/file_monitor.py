"""
File Monitor Watchdog - Django Management Command

Monitors input directories for file system events and updates database in real-time.

Integrates with:
- Story 1.5 (file scanning service) for metadata extraction
- Story 1.2A (File model) for database operations
- Story 1.2B (DirectoryMapping model) for directory configuration

Usage:
    python manage.py file_monitor
    python manage.py file_monitor --schema-id=1
"""

import os
import signal
import sys
import time
from pathlib import Path
from typing import List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from apps.catalog.models import DirectoryMapping, File, Schema
from samplify.management.commands.scan_input import Command as ScanCommand


class FileEventHandler(FileSystemEventHandler):
    """
    Handle file system events and update database.

    Processes created, modified, and deleted events for files in watched directories.
    """

    def __init__(self, scan_command: ScanCommand):
        """
        Initialize event handler.

        Args:
            scan_command: Instance of scan_input command for metadata extraction
        """
        self.scan_command = scan_command
        super().__init__()

    def on_created(self, event):
        """
        Handle file creation event.

        Creates new File record in database with metadata from FFmpeg.

        Args:
            event: FileSystemEvent with src_path
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Filter media files only
        media_extensions = {
            ".wav",
            ".mp3",
            ".flac",
            ".aiff",
            ".aif",
            ".m4a",
            ".ogg",
            ".wma",
            ".mp4",
            ".mov",
            ".avi",
            ".mkv",
            ".wmv",
            ".flv",
            ".webm",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
        }

        if file_path.suffix.lower() not in media_extensions:
            return

        logger.info(f"File created: {event.src_path}")

        try:
            # Extract metadata using scanning service
            metadata = self.scan_command.extract_metadata(file_path)

            if not metadata:
                logger.warning(f"Could not extract metadata for: {file_path}")
                return

            # Create File record atomically
            with transaction.atomic():
                file_obj, created = File.objects.get_or_create(
                    file_path=metadata["file_path"],
                    defaults={
                        "file_name": metadata["file_name"],
                        "file_format": metadata["file_format"],
                        "file_size": metadata["file_size"],
                        "media_type": metadata["media_type"],
                        "codec": metadata.get("codec"),
                        "sample_rate": metadata.get("sample_rate"),
                        "bit_depth": metadata.get("bit_depth"),
                        "processing_status": "pending",
                    },
                )

                if created:
                    logger.info(f"Created File record: {file_obj.file_name}")
                else:
                    logger.debug(f"File record already exists: {file_obj.file_name}")

        except Exception as e:
            logger.error(f"Error creating file record for {file_path}: {e}")

    def on_modified(self, event):
        """
        Handle file modification event.

        Updates existing File record metadata.

        Args:
            event: FileSystemEvent with src_path
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        logger.info(f"File modified: {event.src_path}")

        try:
            # Get existing file record
            file_obj = File.objects.get(file_path=str(file_path.resolve()))

            # Extract updated metadata
            metadata = self.scan_command.extract_metadata(file_path)

            if not metadata:
                logger.warning(f"Could not extract updated metadata for: {file_path}")
                return

            # Update record atomically
            with transaction.atomic():
                # Update file size from actual file stats
                if file_path.exists():
                    file_obj.file_size = file_path.stat().st_size

                # Update metadata from FFmpeg
                file_obj.sample_rate = metadata.get("sample_rate")
                file_obj.bit_depth = metadata.get("bit_depth")
                file_obj.codec = metadata.get("codec")
                file_obj.save()

                logger.info(f"Updated File record: {file_obj.file_name}")

        except File.DoesNotExist:
            logger.debug(f"File not in database (may be newly created): {file_path}")
            # Let on_created handle it if it's a new file
        except Exception as e:
            logger.error(f"Error updating file record for {file_path}: {e}")

    def on_deleted(self, event):
        """
        Handle file deletion event.

        Removes File record from database.

        Args:
            event: FileSystemEvent with src_path
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        logger.info(f"File deleted: {event.src_path}")

        try:
            deleted_count = File.objects.filter(file_path=str(file_path.resolve())).delete()[0]

            if deleted_count > 0:
                logger.info(f"Deleted File record: {file_path.name}")
            else:
                logger.debug(f"File was not in database: {file_path.name}")

        except Exception as e:
            logger.error(f"Error deleting file record for {file_path}: {e}")


class Command(BaseCommand):
    """Django management command for monitoring file system events."""

    help = "Monitor input directories for file system events (blocking service)"

    def __init__(self):
        super().__init__()
        self.observer = None
        self.shutdown_requested = False

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--schema-id",
            type=int,
            help="Optional: Monitor only this schema's directories",
        )

    def handle(self, *args, **options):
        """Main command handler - runs as blocking service."""
        schema_id = options.get("schema_id")

        # Get directories to monitor
        directories = self.get_directories_to_monitor(schema_id)

        if not directories:
            logger.warning("No directories to monitor (check monitor_enabled flag)")
            return

        # Create scanning service instance for metadata extraction
        scan_command = ScanCommand()

        # Create observer and event handler
        self.observer = Observer()
        event_handler = FileEventHandler(scan_command)

        # Schedule observers for each directory
        for directory_mapping in directories:
            input_path = directory_mapping.input_path

            if not Path(input_path).exists():
                logger.warning(f"Directory does not exist: {input_path}")
                continue

            # Always monitor recursively for comprehensive coverage
            self.observer.schedule(event_handler, path=input_path, recursive=True)

            logger.info(f"Monitoring: {input_path} (schema: {directory_mapping.schema.name})")

        # Setup graceful shutdown handling
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received - stopping file monitor...")
            self.shutdown_requested = True
            if self.observer:
                self.observer.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start monitoring (blocking)
        self.observer.start()
        logger.info(f"File monitor started (monitoring {len(directories)} directories)")
        logger.info("Press Ctrl+C to stop")

        try:
            # Keep running until shutdown requested
            while not self.shutdown_requested:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")

        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                logger.info("File monitor stopped")

    def get_directories_to_monitor(self, schema_id: Optional[int] = None) -> List[DirectoryMapping]:
        """
        Get list of directories to monitor.

        Args:
            schema_id: Optional schema ID to filter by

        Returns:
            List of DirectoryMapping objects with monitor_enabled=True
        """
        query = DirectoryMapping.objects.filter(monitor_enabled=True)

        if schema_id:
            try:
                schema = Schema.objects.get(id=schema_id)
                query = query.filter(schema=schema)
            except Schema.DoesNotExist:
                raise CommandError(f"Schema with ID {schema_id} does not exist")

        return list(query.select_related("schema"))
