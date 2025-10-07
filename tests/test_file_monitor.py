"""
Tests for File Monitor Watchdog (Story 1.7)

Test Categories:
1. Unit Tests - Event Handler Logic
2. Integration Tests - Watchdog Service
3. Integration Tests - Database Updates
4. Latency Tests (NFR10 validation)

Coverage Target: 80%+ for file monitoring service
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase, TransactionTestCase
from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileModifiedEvent

from apps.catalog.models import DirectoryMapping, File, Schema
from samplify.management.commands.file_monitor import Command, FileEventHandler
from samplify.management.commands.scan_input import Command as ScanCommand


# ==============================================================================
# UNIT TESTS - EVENT HANDLER LOGIC
# ==============================================================================


class EventHandlerTestCase(TestCase):
    """Test FileEventHandler event processing logic."""

    def setUp(self):
        """Set up test environment."""
        self.scan_command = ScanCommand()
        self.event_handler = FileEventHandler(self.scan_command)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_on_created_ignores_directories(self):
        """Test that directory creation events are ignored."""
        event = FileCreatedEvent(self.temp_dir)
        event.is_directory = True

        # Should not raise exception
        self.event_handler.on_created(event)

        # Verify no File records created
        assert File.objects.count() == 0

    def test_on_modified_ignores_directories(self):
        """Test that directory modification events are ignored."""
        event = FileModifiedEvent(self.temp_dir)
        event.is_directory = True

        # Should not raise exception
        self.event_handler.on_modified(event)

    def test_on_deleted_ignores_directories(self):
        """Test that directory deletion events are ignored."""
        event = FileDeletedEvent(self.temp_dir)
        event.is_directory = True

        # Should not raise exception
        self.event_handler.on_deleted(event)

    def test_on_created_ignores_non_media_files(self):
        """Test that non-media files are ignored."""
        # Create non-media file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("dummy")

        event = FileCreatedEvent(str(test_file))
        event.is_directory = False

        self.event_handler.on_created(event)

        # Verify no File records created
        assert File.objects.count() == 0

    @patch("samplify.management.commands.file_monitor.logger")
    def test_on_created_handles_extraction_failure(self, mock_logger):
        """Test graceful handling when metadata extraction fails."""
        # Create media file
        test_file = Path(self.temp_dir) / "test.wav"
        test_file.write_text("invalid audio data")

        # Mock extract_metadata to return None
        with patch.object(self.scan_command, "extract_metadata", return_value=None):
            event = FileCreatedEvent(str(test_file))
            event.is_directory = False

            self.event_handler.on_created(event)

            # Verify warning was logged
            assert any("Could not extract metadata" in str(call) for call in mock_logger.warning.call_args_list)

            # Verify no File record created
            assert File.objects.count() == 0


# ==============================================================================
# INTEGRATION TESTS - WATCHDOG SERVICE
# ==============================================================================


class WatchdogIntegrationTestCase(TransactionTestCase):
    """Test watchdog integration with file system and database."""

    def setUp(self):
        """Set up test environment."""
        self.scan_command = ScanCommand()
        self.event_handler = FileEventHandler(self.scan_command)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("samplify.management.commands.scan_input.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_on_created_creates_file_record(self, mock_run, mock_get_ffmpeg):
        """Test file creation event creates database record."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Mock FFmpeg output
        mock_ffmpeg_output = {
            "streams": [
                {
                    "codec_type": "audio",
                    "codec_name": "pcm_s24le",
                    "sample_rate": "44100",
                    "bits_per_raw_sample": "24",
                }
            ],
            "format": {"format_name": "wav", "size": "1024000"},
        }

        import json

        mock_run.return_value = Mock(returncode=0, stdout=json.dumps(mock_ffmpeg_output))

        # Create test file
        test_file = Path(self.temp_dir) / "kick.wav"
        test_file.write_text("dummy audio data")

        # Simulate file created event
        event = FileCreatedEvent(str(test_file))
        event.is_directory = False

        self.event_handler.on_created(event)

        # Verify File record was created
        assert File.objects.count() == 1

        file_obj = File.objects.first()
        assert file_obj.file_name == "kick.wav"
        assert file_obj.media_type == "audio"
        assert file_obj.processing_status == "pending"
        assert file_obj.sample_rate == 44100
        assert file_obj.bit_depth == 24

    @patch("samplify.management.commands.scan_input.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_on_modified_updates_file_record(self, mock_run, mock_get_ffmpeg):
        """Test file modification event updates existing record."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Create test file
        test_file = Path(self.temp_dir) / "kick.wav"
        test_file.write_text("dummy audio data")

        # Create existing File record
        file_obj = File.objects.create(
            file_path=str(test_file.resolve()),
            file_name="kick.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
            sample_rate=44100,
            bit_depth=16,  # Original bit depth
        )

        # Mock updated FFmpeg output (24-bit instead of 16-bit)
        mock_ffmpeg_output = {
            "streams": [
                {
                    "codec_type": "audio",
                    "codec_name": "pcm_s24le",
                    "sample_rate": "44100",
                    "bits_per_raw_sample": "24",  # Updated
                }
            ],
            "format": {"format_name": "wav"},
        }

        import json

        mock_run.return_value = Mock(returncode=0, stdout=json.dumps(mock_ffmpeg_output))

        # Simulate file modified event
        event = FileModifiedEvent(str(test_file))
        event.is_directory = False

        self.event_handler.on_modified(event)

        # Verify File record was updated
        file_obj.refresh_from_db()
        assert file_obj.bit_depth == 24  # Updated from FFmpeg
        assert file_obj.file_size == test_file.stat().st_size  # Updated from file stats

    def test_on_deleted_removes_file_record(self):
        """Test file deletion event removes database record."""
        # Create test file path (doesn't need to exist for deletion event)
        test_file = Path(self.temp_dir) / "kick.wav"

        # Create File record
        file_obj = File.objects.create(
            file_path=str(test_file.resolve()),
            file_name="kick.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
        )

        assert File.objects.count() == 1

        # Simulate file deleted event
        event = FileDeletedEvent(str(test_file))
        event.is_directory = False

        self.event_handler.on_deleted(event)

        # Verify File record was deleted
        assert File.objects.count() == 0

    @patch("samplify.management.commands.scan_input.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_on_created_duplicate_file(self, mock_run, mock_get_ffmpeg):
        """Test creating a file that already exists in database."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Mock FFmpeg output
        mock_ffmpeg_output = {
            "streams": [{"codec_type": "audio", "codec_name": "pcm_s24le", "sample_rate": "44100"}],
            "format": {"format_name": "wav"},
        }

        import json

        mock_run.return_value = Mock(returncode=0, stdout=json.dumps(mock_ffmpeg_output))

        # Create test file
        test_file = Path(self.temp_dir) / "kick.wav"
        test_file.write_text("dummy")

        # Create existing File record
        File.objects.create(
            file_path=str(test_file.resolve()),
            file_name="kick.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
        )

        initial_count = File.objects.count()

        # Simulate file created event
        event = FileCreatedEvent(str(test_file))
        event.is_directory = False

        self.event_handler.on_created(event)

        # Verify no duplicate record created
        assert File.objects.count() == initial_count


# ==============================================================================
# INTEGRATION TESTS - MANAGEMENT COMMAND
# ==============================================================================


class ManagementCommandTestCase(TestCase):
    """Test file_monitor management command."""

    def setUp(self):
        """Set up test schema and directory mappings."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_directories_to_monitor_with_monitor_enabled_true(self):
        """Test get_directories_to_monitor returns monitored directories."""
        # Create monitored directory
        monitored_dir = DirectoryMapping.objects.create(
            schema=self.schema, input_path=self.temp_dir, output_path="/output/", monitor_enabled=True
        )

        cmd = Command()
        directories = cmd.get_directories_to_monitor()

        assert len(directories) == 1
        assert directories[0].id == monitored_dir.id

    def test_get_directories_to_monitor_excludes_unmonitored(self):
        """Test get_directories_to_monitor excludes monitor_enabled=False directories."""
        # Create unmonitored directory
        DirectoryMapping.objects.create(
            schema=self.schema, input_path=self.temp_dir, output_path="/output/", monitor_enabled=False
        )

        cmd = Command()
        directories = cmd.get_directories_to_monitor()

        assert len(directories) == 0

    def test_get_directories_to_monitor_with_schema_filter(self):
        """Test filtering by schema_id."""
        schema2 = Schema.objects.create(name="Schema 2", is_active=False)

        # Create directory for schema 1
        dir1 = DirectoryMapping.objects.create(
            schema=self.schema, input_path="/input1/", output_path="/output1/", monitor_enabled=True
        )

        # Create directory for schema 2
        DirectoryMapping.objects.create(schema=schema2, input_path="/input2/", output_path="/output2/", monitor_enabled=True)

        cmd = Command()
        directories = cmd.get_directories_to_monitor(schema_id=self.schema.id)

        assert len(directories) == 1
        assert directories[0].id == dir1.id

    def test_get_directories_to_monitor_invalid_schema(self):
        """Test error handling for invalid schema_id."""
        from django.core.management.base import CommandError

        cmd = Command()

        with pytest.raises(CommandError) as exc_info:
            cmd.get_directories_to_monitor(schema_id=9999)

        assert "does not exist" in str(exc_info.value)


# ==============================================================================
# PERFORMANCE / LATENCY TESTS (NFR10)
# ==============================================================================


@pytest.mark.slow
class LatencyTestCase(TransactionTestCase):
    """
    Latency tests for file monitor.

    Target: <10 seconds file detection latency (NFR10)
    """

    @pytest.mark.skip(reason="Latency test - run manually with real watchdog observer")
    def test_file_detection_latency_under_10_seconds(self):
        """Test file detection latency < 10 seconds (NFR10)."""
        import threading

        from watchdog.observers import Observer

        temp_dir = tempfile.mkdtemp()
        schema = Schema.objects.create(name="Latency Test Schema", is_active=True)

        DirectoryMapping.objects.create(schema=schema, input_path=temp_dir, output_path="/output/", monitor_enabled=True)

        try:
            # Start observer
            scan_command = ScanCommand()
            event_handler = FileEventHandler(scan_command)
            observer = Observer()
            observer.schedule(event_handler, path=temp_dir, recursive=True)
            observer.start()

            # Create test file and measure latency
            start_time = time.time()

            test_file = Path(temp_dir) / "latency_test.wav"
            test_file.write_text("dummy audio data")

            # Wait for File record to appear
            timeout = 10
            file_detected = False

            while time.time() - start_time < timeout:
                if File.objects.filter(file_name="latency_test.wav").exists():
                    file_detected = True
                    break
                time.sleep(0.1)

            latency = time.time() - start_time

            # Stop observer
            observer.stop()
            observer.join()

            # Verify latency requirement
            assert file_detected, "File was not detected within timeout"
            assert latency < 10, f"Latency {latency:.2f}s exceeds 10s requirement (NFR10)"

        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)
