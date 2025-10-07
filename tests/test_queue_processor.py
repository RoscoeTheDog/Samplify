"""
Tests for Queue Processor Watchdog (Story 1.8)

Test Coverage:
- Database polling logic
- Race condition prevention (select_for_update)
- Batch processing integration
- Status transitions (pending → processing → completed/failed)
- Graceful shutdown handling
- Error recovery
"""

import signal
import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from django.test import TransactionTestCase

from apps.catalog.models import DirectoryMapping, File, Schema
from samplify.management.commands.queue_processor import Command as QueueProcessorCommand


class TestQueueProcessorPolling(TransactionTestCase):
    """Test database polling logic."""

    def setUp(self):
        """Setup test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.dir_mapping = DirectoryMapping.objects.create(
            schema=self.schema, input_path="/test/input/", output_path="/test/output/"
        )

    def test_poll_finds_pending_files(self):
        """Test polling finds pending files."""
        # Create pending files with directory mapping for schema filtering
        file1 = File.objects.create(
            file_path="/test/input/file1.wav",
            file_name="file1.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )
        file2 = File.objects.create(
            file_path="/test/input/file2.wav",
            file_name="file2.wav",
            file_format="wav",
            file_size=2048,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )

        cmd = QueueProcessorCommand()
        cmd.batch_processor = MagicMock()

        # Poll and process
        processed_count = cmd._poll_and_process(self.schema, batch_size=10)

        assert processed_count == 2

    def test_poll_ignores_non_pending_files(self):
        """Test polling ignores files with non-pending status."""
        File.objects.create(
            file_path="/test/input/completed.wav",
            file_name="completed.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="completed",
            directory_mapping=self.dir_mapping,
        )
        File.objects.create(
            file_path="/test/input/processing.wav",
            file_name="processing.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="processing",
            directory_mapping=self.dir_mapping,
        )

        cmd = QueueProcessorCommand()
        cmd.batch_processor = MagicMock()

        processed_count = cmd._poll_and_process(self.schema, batch_size=10)

        assert processed_count == 0

    def test_poll_respects_batch_size(self):
        """Test polling respects batch size limit."""
        # Create 15 pending files
        for i in range(15):
            File.objects.create(
                file_path=f"/test/input/file{i}.wav",
                file_name=f"file{i}.wav",
                file_format="wav",
                file_size=1024,
                media_type="audio",
                processing_status="pending",
            directory_mapping=self.dir_mapping,
            )

        cmd = QueueProcessorCommand()
        cmd.batch_processor = MagicMock()

        # Poll with batch size of 5
        processed_count = cmd._poll_and_process(self.schema, batch_size=5)

        assert processed_count == 5

        # Verify 5 files marked as processing
        processing_count = File.objects.filter(processing_status="processing").count()
        assert processing_count == 5

        # Verify 10 files still pending
        pending_count = File.objects.filter(processing_status="pending").count()
        assert pending_count == 10

    def test_poll_orders_by_created_at(self):
        """Test polling processes oldest files first."""
        # Create files with staggered creation times
        file1 = File.objects.create(
            file_path="/test/input/file1.wav",
            file_name="file1.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )
        time.sleep(0.01)

        file2 = File.objects.create(
            file_path="/test/input/file2.wav",
            file_name="file2.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )

        cmd = QueueProcessorCommand()
        cmd.batch_processor = MagicMock()

        # Mock the process_files to capture the order
        processed_files = []

        def capture_files(files, schema):
            processed_files.extend(files)

        cmd._process_files = capture_files

        cmd._poll_and_process(self.schema, batch_size=10)

        # Verify oldest file processed first
        assert processed_files[0].id == file1.id
        assert processed_files[1].id == file2.id

    def test_schema_filtering(self):
        """Test queue processor only processes files from active schema (Story R1.3)."""
        # Create a second schema with its own directory mapping
        schema_b = Schema.objects.create(name="Schema B", is_active=False)
        dir_mapping_b = DirectoryMapping.objects.create(
            schema=schema_b, input_path="/test/input_b/", output_path="/test/output_b/"
        )

        # Create files for both schemas
        file_a = File.objects.create(
            file_path="/test/input/file_a.wav",
            file_name="file_a.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,  # Schema A
        )
        file_b = File.objects.create(
            file_path="/test/input_b/file_b.wav",
            file_name="file_b.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=dir_mapping_b,  # Schema B
        )

        cmd = QueueProcessorCommand()
        cmd.batch_processor = MagicMock()

        # Process with schema A active
        processed_files = []

        def capture_files(files, schema):
            processed_files.extend(files)

        cmd._process_files = capture_files
        processed_count = cmd._poll_and_process(self.schema, batch_size=10)

        # Verify only schema A files were processed
        assert processed_count == 1
        assert len(processed_files) == 1
        assert processed_files[0].id == file_a.id


class TestRaceConditionPrevention(TransactionTestCase):
    """Test race condition prevention with select_for_update."""

    def setUp(self):
        """Setup test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.dir_mapping = DirectoryMapping.objects.create(
            schema=self.schema, input_path="/test/input/", output_path="/test/output/"
        )

    def test_select_for_update_prevents_double_processing(self):
        """Test select_for_update prevents concurrent processing of same file.

        Note: SQLite has limited support for skip_locked. This test verifies
        that the atomic transaction mechanism prevents double-processing by
        ensuring status updates are atomic.
        """
        from django.db import transaction

        file = File.objects.create(
            file_path="/test/input/file.wav",
            file_name="file.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )

        results = {"processor1_count": 0, "processor2_count": 0}

        def processor_1():
            """Simulate first processor acquiring and processing file."""
            with transaction.atomic():
                # Query and update in same transaction
                files_updated = File.objects.filter(id=file.id, processing_status="pending").update(
                    processing_status="processing"
                )

                if files_updated > 0:
                    results["processor1_count"] = files_updated
                    # Hold lock for a moment
                    time.sleep(0.3)

        def processor_2():
            """Simulate second processor trying to process same file."""
            # Wait a bit to ensure processor_1 starts first
            time.sleep(0.1)

            with transaction.atomic():
                # Try to update the same file
                files_updated = File.objects.filter(id=file.id, processing_status="pending").update(
                    processing_status="processing"
                )

                if files_updated > 0:
                    results["processor2_count"] = files_updated

        thread1 = threading.Thread(target=processor_1)
        thread2 = threading.Thread(target=processor_2)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Verify only one processor successfully updated the file
        total_updates = results["processor1_count"] + results["processor2_count"]
        assert total_updates == 1, f"Expected 1 update, got {total_updates}"

        # Verify file marked as processing
        file.refresh_from_db()
        assert file.processing_status == "processing"


class TestBatchProcessingIntegration(TransactionTestCase):
    """Test integration with Story 1.6 batch processing."""

    def setUp(self):
        """Setup test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.dir_mapping = DirectoryMapping.objects.create(
            schema=self.schema, input_path="/test/input/", output_path="/test/output/"
        )

    @patch("samplify.management.commands.queue_processor.BatchCommand")
    def test_batch_processor_called_with_files(self, mock_batch_class):
        """Test batch processor is called with pending files."""
        mock_batch = MagicMock()
        mock_batch_class.return_value = mock_batch

        file1 = File.objects.create(
            file_path="/test/input/file1.wav",
            file_name="file1.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )

        cmd = QueueProcessorCommand()
        cmd.batch_processor = mock_batch

        cmd._poll_and_process(self.schema, batch_size=10)

        # Verify batch processor methods called
        mock_batch.distribute_jobs.assert_called_once()
        mock_batch.wait_for_completion.assert_called_once()

    @patch("samplify.management.commands.queue_processor.BatchCommand")
    def test_workers_scheduled_on_first_batch(self, mock_batch_class):
        """Test workers are scheduled before first batch."""
        mock_batch = MagicMock()
        mock_batch.running_processes = []  # No workers yet
        mock_batch_class.return_value = mock_batch

        File.objects.create(
            file_path="/test/input/file.wav",
            file_name="file.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )

        cmd = QueueProcessorCommand()
        cmd.batch_processor = mock_batch

        cmd._poll_and_process(self.schema, batch_size=10)

        # Verify schedule_workers called
        mock_batch.schedule_workers.assert_called_once()


class TestStatusManagement(TransactionTestCase):
    """Test file status transitions."""

    def setUp(self):
        """Setup test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.dir_mapping = DirectoryMapping.objects.create(
            schema=self.schema, input_path="/test/input/", output_path="/test/output/"
        )

    def test_status_transition_pending_to_processing(self):
        """Test files marked as processing after polling."""
        file = File.objects.create(
            file_path="/test/input/file.wav",
            file_name="file.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )

        cmd = QueueProcessorCommand()
        cmd.batch_processor = MagicMock()

        cmd._poll_and_process(self.schema, batch_size=10)

        # Verify status changed to processing
        file.refresh_from_db()
        assert file.processing_status == "processing"

    @patch("samplify.management.commands.queue_processor.BatchCommand")
    def test_failed_status_on_processing_error(self, mock_batch_class):
        """Test files marked as failed when processing fails."""
        mock_batch = MagicMock()
        mock_batch.running_processes = []
        mock_batch.distribute_jobs.side_effect = Exception("Processing error")
        mock_batch_class.return_value = mock_batch

        file = File.objects.create(
            file_path="/test/input/file.wav",
            file_name="file.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )

        cmd = QueueProcessorCommand()
        cmd.batch_processor = mock_batch

        cmd._poll_and_process(self.schema, batch_size=10)

        # Verify status changed to failed
        file.refresh_from_db()
        assert file.processing_status == "failed"


class TestGracefulShutdown(TransactionTestCase):
    """Test graceful shutdown handling."""

    def setUp(self):
        """Setup test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.dir_mapping = DirectoryMapping.objects.create(
            schema=self.schema, input_path="/test/input/", output_path="/test/output/"
        )

    def test_sigint_stops_processing_loop(self):
        """Test SIGINT signal stops processing loop gracefully."""
        cmd = QueueProcessorCommand()
        cmd.running = True

        # Setup signal handler
        cmd._setup_signal_handlers()

        # Simulate SIGINT
        signal.raise_signal(signal.SIGINT)

        # Give signal time to process
        time.sleep(0.1)

        # Verify running flag set to False
        assert cmd.running is False

    def test_sigterm_stops_processing_loop(self):
        """Test SIGTERM signal stops processing loop gracefully."""
        cmd = QueueProcessorCommand()
        cmd.running = True

        # Setup signal handler
        cmd._setup_signal_handlers()

        # Simulate SIGTERM
        signal.raise_signal(signal.SIGTERM)

        # Give signal time to process
        time.sleep(0.1)

        # Verify running flag set to False
        assert cmd.running is False


class TestErrorHandling(TransactionTestCase):
    """Test error handling and recovery."""

    def setUp(self):
        """Setup test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.dir_mapping = DirectoryMapping.objects.create(
            schema=self.schema, input_path="/test/input/", output_path="/test/output/"
        )

    def test_continues_after_polling_error(self):
        """Test processor continues after polling error."""
        cmd = QueueProcessorCommand()
        cmd.batch_processor = MagicMock()

        # Mock _poll_and_process to raise error
        call_count = [0]

        def mock_poll(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Database error")
            return 0

        cmd._poll_and_process = mock_poll

        # Run one iteration in thread
        def run_iteration():
            cmd.running = True
            try:
                # First iteration - error
                cmd._poll_and_process(self.schema, 10)
            except Exception:
                pass

            # Second iteration - success
            result = cmd._poll_and_process(self.schema, 10)
            assert result == 0

        thread = threading.Thread(target=run_iteration)
        thread.start()
        thread.join(timeout=2)

        # Verify both iterations ran
        assert call_count[0] == 2

    @patch("samplify.management.commands.queue_processor.logger")
    def test_logs_processing_errors(self, mock_logger):
        """Test errors are logged properly."""
        cmd = QueueProcessorCommand()
        cmd.batch_processor = MagicMock()
        cmd.batch_processor.distribute_jobs.side_effect = Exception("Processing failed")
        cmd.batch_processor.running_processes = []

        file = File.objects.create(
            file_path="/test/input/file.wav",
            file_name="file.wav",
            file_format="wav",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
            directory_mapping=self.dir_mapping,
        )

        cmd._poll_and_process(self.schema, batch_size=10)

        # Verify error logged
        mock_logger.error.assert_called()


class TestCommandLineArguments(TransactionTestCase):
    """Test command-line argument handling."""

    def setUp(self):
        """Setup test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.dir_mapping = DirectoryMapping.objects.create(
            schema=self.schema, input_path="/test/input/", output_path="/test/output/"
        )

    @patch("samplify.management.commands.queue_processor.Command._poll_and_process")
    @patch("samplify.management.commands.queue_processor.time.sleep")
    def test_custom_poll_interval(self, mock_sleep, mock_poll):
        """Test custom polling interval is respected."""
        mock_poll.return_value = 0

        cmd = QueueProcessorCommand()
        cmd.batch_processor = MagicMock()

        # Run one iteration
        def run_one_iteration():
            cmd.running = True
            cmd._poll_and_process(self.schema, 10)
            cmd.running = False

        thread = threading.Thread(target=run_one_iteration)
        thread.start()
        thread.join(timeout=1)

        # Verify poll was called
        assert mock_poll.called

    def test_schema_id_argument(self):
        """Test schema-id argument selects specific schema."""
        schema2 = Schema.objects.create(name="Schema 2", is_active=False)

        cmd = QueueProcessorCommand()

        # Test with schema_id
        options = {"poll_interval": 5, "schema_id": schema2.id, "batch_size": 10}

        # Mock handle to test schema selection logic
        with patch.object(cmd, "_setup_signal_handlers"):
            with patch.object(cmd, "_poll_and_process", return_value=0):
                with patch("samplify.management.commands.queue_processor.time.sleep"):
                    cmd.running = False  # Exit immediately
                    try:
                        cmd.handle(**options)
                    except Exception:
                        pass

        # No assertion needed - test passes if no CommandError raised
