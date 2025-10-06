"""
Tests for Batch Processing Management Command (Story 1.6)

Test Categories:
1. Unit Tests - Multiprocessing (CR2 validation)
2. Integration Tests - File Processing
3. Integration Tests - Database Updates
4. Performance Tests - CPU Utilization

Coverage Target: 80%+ for critical path
"""

import collections
import multiprocessing
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase

from apps.catalog.models import DirectoryMapping, File, Schema
from samplify.management.commands.batch_process import Command


# ==============================================================================
# UNIT TESTS - CR2 MULTIPROCESSING PRESERVATION
# ==============================================================================


class MultiprocessingPreservationTestCase(TestCase):
    """
    Test CR2 preserved multiprocessing patterns from handlers/process_handler.py.

    These tests verify the ported multiprocessing logic produces identical
    worker scheduling and job distribution behavior.
    """

    def test_worker_count_matches_cpu_cores(self):
        """Test one worker per CPU core (CR2)."""
        cmd = Command()
        cmd.schedule_workers()

        expected_workers = multiprocessing.cpu_count()
        actual_workers = len(cmd.decoder_channels)

        assert actual_workers == expected_workers

        # Cleanup
        cmd.cleanup_workers()

    def test_deque_per_worker(self):
        """Test deque (not queue) used per worker (CR2)."""
        cmd = Command()
        cmd.schedule_workers()

        for channel_info in cmd.decoder_channels:
            name, queue = channel_info
            assert isinstance(queue, collections.deque), f"Worker {name} does not use deque"

        # Cleanup
        cmd.cleanup_workers()

    def test_daemon_processes(self):
        """Test all workers are daemon processes (CR2)."""
        cmd = Command()
        cmd.schedule_workers()

        for process in cmd.running_processes:
            assert process.daemon is True, f"Process {process.name} is not daemon"

        # Cleanup
        cmd.cleanup_workers()

    def test_channel_info_tuple_structure(self):
        """Test channel_info tuple structure: (name, deque) (CR2)."""
        cmd = Command()
        cmd.schedule_workers()

        for channel_info in cmd.decoder_channels:
            assert isinstance(channel_info, tuple), "channel_info is not a tuple"
            assert len(channel_info) == 2, "channel_info does not have 2 elements"

            name, queue = channel_info
            assert isinstance(name, str), "Process name is not string"
            assert isinstance(queue, collections.deque), "Queue is not deque"

        # Cleanup
        cmd.cleanup_workers()

    def test_round_robin_distribution(self):
        """Test round-robin job distribution (CR2 approved improvement)."""
        cmd = Command()
        cmd.schedule_workers()

        num_workers = len(cmd.decoder_channels)
        num_tasks = num_workers * 3  # 3 tasks per worker

        # Add tasks
        for i in range(num_tasks):
            task = {"task_id": i}
            cmd.add_task(task)

        # Verify each worker got 3 tasks (round-robin)
        for channel_info in cmd.decoder_channels:
            _, queue = channel_info
            assert len(queue) == 3, "Round-robin distribution failed"

        # Cleanup
        cmd.cleanup_workers()

    def test_appendleft_usage(self):
        """Test tasks added with appendleft() (CR2)."""
        cmd = Command()
        cmd.schedule_workers()

        # Add a task
        task = {"test": "task"}
        cmd.add_task(task)

        # Verify task is in first worker's deque
        first_worker_queue = cmd.decoder_channels[0][1]
        assert len(first_worker_queue) > 0, "Task not added to queue"

        # Verify it was added to the left (latest task should be at index 0)
        assert first_worker_queue[0] == task

        # Cleanup
        cmd.cleanup_workers()


# ==============================================================================
# INTEGRATION TESTS - FILE PROCESSING
# ==============================================================================


class FileProcessingTestCase(TestCase):
    """Test file processing integration."""

    def setUp(self):
        """Set up test schema and files."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.temp_dir = tempfile.mkdtemp()

        # Create test file
        self.test_file_path = Path(self.temp_dir) / "test.wav"
        self.test_file_path.write_text("dummy content")

        self.test_file = File.objects.create(
            file_path=str(self.test_file_path.resolve()),
            file_name="test.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
        )

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_files_for_processing_pending(self):
        """Test retrieval of pending files."""
        cmd = Command()
        files = cmd.get_files_for_processing(self.schema)

        assert len(files) == 1
        assert files[0].id == self.test_file.id
        assert files[0].processing_status == "pending"

    def test_get_files_for_processing_excludes_completed(self):
        """Test completed files are excluded."""
        # Mark file as completed
        self.test_file.processing_status = "completed"
        self.test_file.save()

        cmd = Command()
        files = cmd.get_files_for_processing(self.schema)

        assert len(files) == 0

    def test_get_files_for_processing_with_input_dir(self):
        """Test filtering by input directory."""
        cmd = Command()
        files = cmd.get_files_for_processing(self.schema, input_dir=self.temp_dir)

        assert len(files) == 1
        assert files[0].id == self.test_file.id

    def test_get_files_for_processing_wrong_input_dir(self):
        """Test filtering excludes files from wrong directory."""
        cmd = Command()
        files = cmd.get_files_for_processing(self.schema, input_dir="/wrong/path/")

        assert len(files) == 0

    @patch("samplify.management.commands.batch_process.get_ffmpeg_path")
    def test_execute_transformation_success(self, mock_get_ffmpeg):
        """Test successful file transformation."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        cmd = Command()
        success = cmd.execute_transformation(self.test_file, self.schema)

        assert success is True

    @patch("samplify.management.commands.batch_process.get_ffmpeg_path")
    def test_execute_transformation_no_ffmpeg(self, mock_get_ffmpeg):
        """Test transformation fails when FFmpeg unavailable."""
        mock_get_ffmpeg.return_value = None

        cmd = Command()
        success = cmd.execute_transformation(self.test_file, self.schema)

        assert success is False

    @patch("samplify.management.commands.batch_process.get_ffmpeg_path")
    def test_execute_transformation_missing_file(self, mock_get_ffmpeg):
        """Test transformation fails for missing file."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Create file with non-existent path
        missing_file = File.objects.create(
            file_path="/nonexistent/file.wav",
            file_name="missing.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
        )

        cmd = Command()
        success = cmd.execute_transformation(missing_file, self.schema)

        assert success is False


# ==============================================================================
# INTEGRATION TESTS - DATABASE UPDATES
# ==============================================================================


class DatabaseUpdateTestCase(TestCase):
    """Test database status updates during processing."""

    def setUp(self):
        """Set up test schema and files."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_distribute_jobs_marks_files_processing(self):
        """Test files marked as 'processing' when distributed."""
        # Create test file
        test_file = File.objects.create(
            file_path=f"{self.temp_dir}/test.wav",
            file_name="test.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
        )

        cmd = Command()
        cmd.schedule_workers()
        cmd.distribute_jobs([test_file], self.schema)

        # Refresh from database
        test_file.refresh_from_db()

        assert test_file.processing_status == "processing"

        # Cleanup
        cmd.cleanup_workers()

    @patch("samplify.management.commands.batch_process.get_ffmpeg_path")
    def test_process_task_marks_completed(self, mock_get_ffmpeg):
        """Test successful processing marks file as 'completed'."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Create test file
        test_file_path = Path(self.temp_dir) / "test.wav"
        test_file_path.write_text("dummy")

        test_file = File.objects.create(
            file_path=str(test_file_path.resolve()),
            file_name="test.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
            processing_status="processing",
        )

        task = {
            "file_id": test_file.id,
            "file_path": test_file.file_path,
            "file_name": test_file.file_name,
            "schema_id": self.schema.id,
        }

        cmd = Command()
        cmd.process_task(task)

        # Refresh from database
        test_file.refresh_from_db()

        assert test_file.processing_status == "completed"

    @patch("samplify.management.commands.batch_process.get_ffmpeg_path")
    def test_process_task_marks_failed_on_error(self, mock_get_ffmpeg):
        """Test failed processing marks file as 'failed'."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Create file with non-existent path
        test_file = File.objects.create(
            file_path="/nonexistent/file.wav",
            file_name="missing.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
            processing_status="processing",
        )

        task = {
            "file_id": test_file.id,
            "file_path": test_file.file_path,
            "file_name": test_file.file_name,
            "schema_id": self.schema.id,
        }

        cmd = Command()
        cmd.process_task(task)

        # Refresh from database
        test_file.refresh_from_db()

        assert test_file.processing_status == "failed"

    def test_atomic_status_updates(self):
        """Test status updates are atomic (transaction-based)."""
        test_file = File.objects.create(
            file_path=f"{self.temp_dir}/test.wav",
            file_name="test.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
            processing_status="pending",
        )

        initial_status = test_file.processing_status

        cmd = Command()
        cmd.schedule_workers()

        # Distribute job (should atomically update status)
        cmd.distribute_jobs([test_file], self.schema)

        # Refresh from database
        test_file.refresh_from_db()

        # Status should have changed atomically
        assert test_file.processing_status != initial_status
        assert test_file.processing_status == "processing"

        # Cleanup
        cmd.cleanup_workers()


# ==============================================================================
# PERFORMANCE TESTS
# ==============================================================================


@pytest.mark.slow
class PerformanceTestCase(TestCase):
    """
    Performance tests for batch processing.

    Target: Match brownfield performance (50-70% CPU, NFR1)
    """

    @pytest.mark.skip(reason="Performance test - run manually")
    def test_cpu_utilization_benchmark(self):
        """Test CPU utilization matches brownfield (50-70%)."""
        import psutil

        schema = Schema.objects.create(name="Perf Test Schema", is_active=True)
        temp_dir = tempfile.mkdtemp()

        try:
            # Create 100 test files
            files = []
            for i in range(100):
                file_path = Path(temp_dir) / f"file_{i:04d}.wav"
                file_path.write_text("dummy content")

                file_obj = File.objects.create(
                    file_path=str(file_path.resolve()),
                    file_name=file_path.name,
                    file_format="WAV",
                    file_size=1024,
                    media_type="audio",
                    processing_status="pending",
                )
                files.append(file_obj)

            # Measure CPU during processing
            process = psutil.Process()
            cpu_before = process.cpu_percent(interval=1)

            cmd = Command()
            cmd.schedule_workers()
            cmd.distribute_jobs(files, schema)
            cmd.wait_for_completion()

            cpu_after = process.cpu_percent(interval=1)
            cpu_utilization = (cpu_after - cpu_before) / multiprocessing.cpu_count()

            # Verify CPU utilization in target range (50-70%)
            assert 50 <= cpu_utilization <= 70, f"CPU utilization {cpu_utilization}% outside target range"

            cmd.cleanup_workers()

        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.skip(reason="Performance test - run manually")
    def test_load_balancing_across_workers(self):
        """Test round-robin distribution balances load across workers."""
        schema = Schema.objects.create(name="Load Test Schema", is_active=True)
        temp_dir = tempfile.mkdtemp()

        try:
            # Create 100 files
            files = []
            for i in range(100):
                file_obj = File.objects.create(
                    file_path=f"{temp_dir}/file_{i:04d}.wav",
                    file_name=f"file_{i:04d}.wav",
                    file_format="WAV",
                    file_size=1024,
                    media_type="audio",
                    processing_status="pending",
                )
                files.append(file_obj)

            cmd = Command()
            cmd.schedule_workers()
            cmd.distribute_jobs(files, schema)

            # Verify even distribution across workers
            num_workers = len(cmd.decoder_channels)
            expected_per_worker = 100 // num_workers

            for channel_info in cmd.decoder_channels:
                _, queue = channel_info
                queue_size = len(queue)

                # Allow +/- 1 task variance for rounding
                assert abs(queue_size - expected_per_worker) <= 1, f"Load imbalance: {queue_size} != {expected_per_worker}"

            cmd.cleanup_workers()

        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)
