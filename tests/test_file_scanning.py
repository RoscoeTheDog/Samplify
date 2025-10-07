"""
Tests for File Scanning Service (Story 1.5)

Test Categories:
1. Unit Tests - Algorithm Preservation (CR1 validation)
2. Integration Tests - FFmpeg Service
3. Integration Tests - File Model CRUD
4. Performance Tests

Coverage Target: 80%+ for critical path
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management import call_command
from django.db import transaction
from django.test import TestCase

from apps.catalog.models import DirectoryMapping, File, Schema
from samplify.management.commands.scan_input import (
    Command,
    between_datetime,
    contains_audio,
    contains_expression,
    contains_extensions,
    contains_image,
    contains_video,
)


# ==============================================================================
# UNIT TESTS - CR1 ALGORITHM PRESERVATION
# ==============================================================================


class AlgorithmPreservationTestCase(TestCase):
    """
    Test CR1 preserved algorithms from handlers/rules.py.

    These tests verify the ported algorithms produce identical results
    to the original brownfield implementation.
    """

    def setUp(self):
        """Create test File object for algorithm tests."""
        self.test_file = File.objects.create(
            file_path="/media/audio/kick_01.wav",
            file_name="kick_01.wav",
            file_format="WAV",
            file_size=1024000,
            media_type="audio",
            sample_rate=44100,
            bit_depth=24,
        )

    def test_contains_expression_match_found(self):
        """Test contains_expression() matches pattern in filename (CR1)."""
        output = {"expression": "kick", "path": "/output/drums/"}

        result = contains_expression(self.test_file, output)

        assert result["output_directory"] == "/output/drums/"
        assert result["file_name"] == "kick_01.wav"
        assert result["file_path"] == "/media/audio/kick_01.wav"

    def test_contains_expression_no_match(self):
        """Test contains_expression() returns empty dict when no match."""
        output = {"expression": "snare", "path": "/output/drums/"}

        result = contains_expression(self.test_file, output)

        assert result == {}

    def test_contains_expression_no_expression(self):
        """Test contains_expression() returns empty dict when no expression specified."""
        output = {"path": "/output/drums/"}

        result = contains_expression(self.test_file, output)

        assert result == {}

    def test_contains_extensions_match_found(self):
        """Test contains_extensions() matches file extension (CR1)."""
        output = {"extensions": ".wav,.mp3", "path": "/output/audio/"}

        result = contains_extensions(self.test_file, output)

        assert result["output_directory"] == "/output/audio/"
        assert result["file_name"] == "kick_01.wav"
        assert result["file_path"] == "/media/audio/kick_01.wav"

    def test_contains_extensions_no_match(self):
        """Test contains_extensions() returns empty dict when no match."""
        output = {"extensions": ".mp3,.flac", "path": "/output/audio/"}

        result = contains_extensions(self.test_file, output)

        assert result == {}

    def test_contains_video_match_found(self):
        """Test contains_video() matches video media type (CR1)."""
        video_file = File.objects.create(
            file_path="/media/video/interview.mp4",
            file_name="interview.mp4",
            file_format="MP4",
            file_size=2048000,
            media_type="video",
        )

        output = {"containsVideo": True, "path": "/output/video/"}

        result = contains_video(video_file, output)

        assert result["output_directory"] == "/output/video/"
        assert result["file_name"] == "interview.mp4"

    def test_contains_video_no_match(self):
        """Test contains_video() returns empty dict for non-video file."""
        output = {"containsVideo": True, "path": "/output/video/"}

        result = contains_video(self.test_file, output)

        assert result == {}

    def test_contains_audio_match_found(self):
        """Test contains_audio() matches audio media type (CR1)."""
        output = {"containsAudio": True, "path": "/output/audio/"}

        result = contains_audio(self.test_file, output)

        assert result["output_directory"] == "/output/audio/"
        assert result["file_name"] == "kick_01.wav"

    def test_contains_audio_no_match(self):
        """Test contains_audio() returns empty dict for non-audio file."""
        image_file = File.objects.create(
            file_path="/media/images/photo.jpg",
            file_name="photo.jpg",
            file_format="JPG",
            file_size=512000,
            media_type="image",
        )

        output = {"containsAudio": True, "path": "/output/audio/"}

        result = contains_audio(image_file, output)

        assert result == {}

    def test_contains_image_match_found(self):
        """Test contains_image() matches image media type (CR1)."""
        image_file = File.objects.create(
            file_path="/media/images/photo.jpg",
            file_name="photo.jpg",
            file_format="JPG",
            file_size=512000,
            media_type="image",
        )

        output = {"containsImage": True, "path": "/output/images/"}

        result = contains_image(image_file, output)

        assert result["output_directory"] == "/output/images/"
        assert result["file_name"] == "photo.jpg"

    def test_between_datetime_within_range(self):
        """Test between_datetime() matches file within date range (CR1)."""
        # Create file with specific creation date
        from django.utils import timezone

        test_file = File.objects.create(
            file_path="/media/audio/test.wav",
            file_name="test.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
            created_at=timezone.datetime(2024, 6, 15, tzinfo=timezone.utc),
        )

        output = {
            "datetimeStart": "2024-06-01",
            "datetimeEnd": "2024-06-30",
            "path": "/output/june/",
        }

        result = between_datetime(test_file, output)

        assert result["output_directory"] == "/output/june/"
        assert result["file_name"] == "test.wav"


# ==============================================================================
# INTEGRATION TESTS - FFMPEG SERVICE
# ==============================================================================


class FFmpegIntegrationTestCase(TestCase):
    """Test FFmpeg metadata extraction integration."""

    def setUp(self):
        """Set up test schema and directory mapping."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("samplify.management.commands.scan_input.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_extract_metadata_audio_file(self, mock_run, mock_get_ffmpeg):
        """Test FFmpeg metadata extraction for audio file."""
        # Mock FFmpeg path
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Mock FFmpeg JSON output
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

        mock_run.return_value = Mock(returncode=0, stdout=json.dumps(mock_ffmpeg_output))

        # Create test file
        test_file = Path(self.temp_dir) / "test.wav"
        test_file.write_text("dummy content")

        command = Command()
        metadata = command.extract_metadata(test_file)

        assert metadata is not None
        assert metadata["media_type"] == "audio"
        assert metadata["sample_rate"] == 44100
        assert metadata["bit_depth"] == 24
        assert metadata["codec"] == "pcm_s24le"
        assert metadata["file_format"] == "WAV"

    @patch("samplify.management.commands.scan_input.get_ffmpeg_path")
    @patch("subprocess.run")
    def test_extract_metadata_video_file(self, mock_run, mock_get_ffmpeg):
        """Test FFmpeg metadata extraction for video file."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        mock_ffmpeg_output = {
            "streams": [
                {"codec_type": "video", "codec_name": "h264"},
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "sample_rate": "48000",
                    "bits_per_raw_sample": "16",
                },
            ],
            "format": {"format_name": "mp4", "size": "2048000"},
        }

        mock_run.return_value = Mock(returncode=0, stdout=json.dumps(mock_ffmpeg_output))

        test_file = Path(self.temp_dir) / "test.mp4"
        test_file.write_text("dummy content")

        command = Command()
        metadata = command.extract_metadata(test_file)

        assert metadata is not None
        assert metadata["media_type"] == "video"
        assert metadata["codec"] == "h264"

    @patch("samplify.management.commands.scan_input.get_ffmpeg_path")
    def test_extract_metadata_ffmpeg_not_available(self, mock_get_ffmpeg):
        """Test FFmpeg metadata extraction when FFmpeg unavailable."""
        mock_get_ffmpeg.return_value = None

        test_file = Path(self.temp_dir) / "test.wav"
        test_file.write_text("dummy content")

        command = Command()
        metadata = command.extract_metadata(test_file)

        assert metadata is None


# ==============================================================================
# INTEGRATION TESTS - FILE MODEL CRUD
# ==============================================================================


class FileCRUDTestCase(TestCase):
    """Test File model CRUD operations."""

    def setUp(self):
        """Set up test schema."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_upsert_file_create_new(self):
        """Test upserting a new file creates File record."""
        test_file = Path(self.temp_dir) / "test.wav"
        test_file.write_text("dummy content")

        metadata = {
            "file_path": str(test_file.resolve()),
            "file_name": "test.wav",
            "file_format": "WAV",
            "file_size": 1024,
            "media_type": "audio",
            "sample_rate": 44100,
            "bit_depth": 24,
            "codec": "pcm_s24le",
        }

        command = Command()
        file_obj, created = command.upsert_file(test_file, metadata, force_rescan=False)

        assert created is True
        assert file_obj is not None
        assert file_obj.file_name == "test.wav"
        assert file_obj.sample_rate == 44100

    def test_upsert_file_update_existing(self):
        """Test upserting existing file with force_rescan updates record."""
        # Create initial file
        existing_file = File.objects.create(
            file_path="/media/test.wav",
            file_name="test.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
            sample_rate=44100,
        )

        # Updated metadata
        metadata = {
            "file_path": "/media/test.wav",
            "file_name": "test.wav",
            "file_format": "WAV",
            "file_size": 2048,  # Changed
            "media_type": "audio",
            "sample_rate": 48000,  # Changed
            "bit_depth": 16,
        }

        command = Command()
        file_obj, created = command.upsert_file(Path("/media/test.wav"), metadata, force_rescan=True)

        assert created is False
        assert file_obj is not None
        assert file_obj.sample_rate == 48000  # Updated
        assert file_obj.file_size == 2048  # Updated

    def test_upsert_file_skip_existing_no_force(self):
        """Test upserting existing file without force_rescan skips update."""
        existing_file = File.objects.create(
            file_path="/media/test.wav",
            file_name="test.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
            sample_rate=44100,
        )

        metadata = {
            "file_path": "/media/test.wav",
            "file_name": "test.wav",
            "file_format": "WAV",
            "file_size": 2048,
            "media_type": "audio",
            "sample_rate": 48000,
        }

        command = Command()
        file_obj, created = command.upsert_file(Path("/media/test.wav"), metadata, force_rescan=False)

        assert created is False
        # Original values should be unchanged
        file_obj.refresh_from_db()
        assert file_obj.sample_rate == 44100

    def test_cleanup_missing_files(self):
        """Test cleanup_missing_files() deletes records for non-existent files."""
        # Create file record with non-existent path
        File.objects.create(
            file_path="/nonexistent/file.wav",
            file_name="file.wav",
            file_format="WAV",
            file_size=1024,
            media_type="audio",
        )

        command = Command()
        deleted_count = command.cleanup_missing_files()

        assert deleted_count == 1
        assert File.objects.count() == 0

    def test_database_atomicity_on_error(self):
        """Test database operations are atomic (rollback on error)."""
        from django.core.exceptions import ValidationError

        initial_count = File.objects.count()

        # This should fail due to invalid data
        with pytest.raises(ValidationError):
            with transaction.atomic():
                file_obj = File(
                    file_path="/test/file.wav",
                    file_name="test.wav",
                    file_format="WAV",
                    file_size=1024,
                    media_type="invalid_type",  # Invalid choice
                )
                file_obj.full_clean()  # Trigger validation
                file_obj.save()

        # Verify no record was created (rolled back)
        assert File.objects.count() == initial_count


# ==============================================================================
# INTEGRATION TESTS - MANAGEMENT COMMAND
# ==============================================================================


class ManagementCommandTestCase(TestCase):
    """Test scan_input management command."""

    def setUp(self):
        """Set up test schema and directory mappings."""
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.temp_dir = tempfile.mkdtemp()

        self.mapping = DirectoryMapping.objects.create(
            schema=self.schema, input_path=self.temp_dir, output_path="/output/", is_watched=False
        )

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scan_directory_finds_media_files(self):
        """Test scan_directory() finds media files."""
        # Create test files
        (Path(self.temp_dir) / "test1.wav").write_text("dummy")
        (Path(self.temp_dir) / "test2.mp3").write_text("dummy")
        (Path(self.temp_dir) / "test.txt").write_text("dummy")  # Non-media

        command = Command()
        files = command.scan_directory(self.temp_dir)

        assert len(files) == 2
        assert any(f.name == "test1.wav" for f in files)
        assert any(f.name == "test2.mp3" for f in files)
        assert not any(f.name == "test.txt" for f in files)

    def test_scan_directory_recursive(self):
        """Test scan_directory() recursively scans subdirectories."""
        # Create nested structure
        subdir = Path(self.temp_dir) / "subdir"
        subdir.mkdir()
        (Path(self.temp_dir) / "root.wav").write_text("dummy")
        (subdir / "nested.mp3").write_text("dummy")

        command = Command()
        files = command.scan_directory(self.temp_dir)

        assert len(files) == 2
        assert any(f.name == "root.wav" for f in files)
        assert any(f.name == "nested.mp3" for f in files)

    def test_scan_directory_nonexistent_directory(self):
        """Test scan_directory() handles non-existent directory."""
        command = Command()
        files = command.scan_directory("/nonexistent/directory/")

        assert files == []


# ==============================================================================
# PERFORMANCE TESTS
# ==============================================================================


@pytest.mark.slow
class PerformanceTestCase(TestCase):
    """
    Performance tests for file scanning.

    Target: 1000 files < 5 minutes (AC #12)
    """

    @pytest.mark.performance
    def test_scan_performance_1000_files(self):
        """
        Test scanning 1000 files completes within 5 minutes (NFR5).

        Performance Grading:
        - EXCELLENT: < 3 minutes (180 seconds)
        - GOOD: < 5 minutes (300 seconds) - NFR5 requirement
        - FAIL: >= 5 minutes

        Test Dataset:
        - 700 audio files (WAV format, various sample rates)
        - 200 video files (MP4 format, various resolutions)
        - 100 image files (JPEG format, various sizes)
        """
        import shutil
        import subprocess
        import time

        # Generate test dataset
        dataset_dir = Path(tempfile.mkdtemp(prefix="perf_test_"))
        generator_script = Path(__file__).parent / "fixtures" / "generate_test_dataset.py"

        try:
            # Run dataset generator
            print("\nGenerating 1000-file test dataset...")
            result = subprocess.run(
                ["python", str(generator_script), str(dataset_dir), "--quiet"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for generation
            )

            if result.returncode != 0:
                pytest.fail(f"Dataset generation failed: {result.stderr}")

            # Verify dataset created
            all_files = list(dataset_dir.rglob('*'))
            media_files = [f for f in all_files if f.is_file()]
            print(f"Dataset generated: {len(media_files)} files")

            # Setup Django models
            schema = Schema.objects.create(name="Perf Test Schema", is_active=True)
            DirectoryMapping.objects.create(
                schema=schema,
                input_path=str(dataset_dir),
                output_path="/output/"
            )

            # Run performance benchmark
            print("Starting performance benchmark...")
            start_time = time.perf_counter()

            command = Command()
            files = command.scan_directory(str(dataset_dir))

            end_time = time.perf_counter()
            duration = end_time - start_time

            # Calculate metrics
            throughput = len(files) / duration if duration > 0 else 0

            # Determine performance grade
            if duration < 180:
                grade = "EXCELLENT"
            elif duration < 300:
                grade = "GOOD"
            else:
                grade = "FAIL"

            # Print results
            print("\n" + "=" * 60)
            print("PERFORMANCE BENCHMARK RESULTS")
            print("=" * 60)
            print(f"Files scanned:  {len(files)}")
            print(f"Duration:       {duration:.2f} seconds ({duration/60:.2f} minutes)")
            print(f"Throughput:     {throughput:.2f} files/second")
            print(f"Grade:          {grade}")
            print(f"NFR5 Met:       {'YES' if duration < 300 else 'NO'}")
            print("=" * 60)

            # Assertions
            assert len(files) > 0, "No files were scanned"
            assert duration < 300, f"Performance requirement not met: {duration:.2f}s >= 300s (NFR5)"

        finally:
            # Cleanup
            shutil.rmtree(dataset_dir, ignore_errors=True)


# ==============================================================================
# ERROR CATEGORIZATION TESTS (GUIDE 8)
# ==============================================================================


class ErrorCategorizationTestCase(TestCase):
    """
    Test enhanced error categorization and retry logic for FFmpeg failures.

    Tests verify:
    - Error type classification (corrupt, unsupported, network, permission, disk)
    - Retry logic for transient errors
    - Skip logic for permanent errors
    - Abort logic for critical errors
    - Structured logging with error metadata
    """

    def setUp(self):
        """Setup test environment."""
        self.command = Command()
        self.test_file = Path("/test/sample.wav")

    @patch('samplify.management.commands.scan_input.get_ffmpeg_path')
    @patch('samplify.management.commands.scan_input.subprocess.run')
    def test_error_categorization_corrupt_file(self, mock_run, mock_get_ffmpeg):
        """Test corrupt file is detected and skipped without retry."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Simulate FFmpeg detecting corrupt file
        mock_run.return_value = Mock(
            returncode=1,
            stderr="Invalid data found when processing input",
            stdout=""
        )

        result = self.command.extract_metadata(self.test_file)

        assert result is None
        assert mock_run.call_count == 1, "Corrupt file should not trigger retry"

    @patch('samplify.management.commands.scan_input.get_ffmpeg_path')
    @patch('samplify.management.commands.scan_input.subprocess.run')
    def test_error_categorization_unsupported_format(self, mock_run, mock_get_ffmpeg):
        """Test unsupported format is detected and skipped without retry."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Simulate FFmpeg encountering unsupported format
        mock_run.return_value = Mock(
            returncode=1,
            stderr="Unknown format or codec not supported",
            stdout=""
        )

        result = self.command.extract_metadata(self.test_file)

        assert result is None
        assert mock_run.call_count == 1, "Unsupported format should not trigger retry"

    @patch('samplify.management.commands.scan_input.get_ffmpeg_path')
    @patch('samplify.management.commands.scan_input.subprocess.run')
    @patch('samplify.management.commands.scan_input.time.sleep')
    def test_error_categorization_network_error(self, mock_sleep, mock_run, mock_get_ffmpeg):
        """Test network error triggers retry with exponential backoff."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Simulate transient network error that succeeds on 2nd attempt
        mock_run.side_effect = [
            Mock(returncode=1, stderr="Connection timeout", stdout=""),  # Attempt 1: fail
            Mock(returncode=0, stdout=json.dumps({  # Attempt 2: success
                "streams": [{"codec_type": "audio", "codec_name": "pcm_s16le", "sample_rate": "44100"}],
                "format": {"size": "1024000"}
            }), stderr="")
        ]

        result = self.command.extract_metadata(self.test_file)

        assert result is not None
        assert result["codec"] == "pcm_s16le"
        assert mock_run.call_count == 2, "Should retry once after network error"
        assert mock_sleep.call_count == 1, "Should sleep between retries"
        mock_sleep.assert_called_with(2)  # First retry delay: RETRY_DELAY * (attempt + 1) = 2 * 1

    @patch('samplify.management.commands.scan_input.get_ffmpeg_path')
    @patch('samplify.management.commands.scan_input.subprocess.run')
    def test_error_categorization_permission_error(self, mock_run, mock_get_ffmpeg):
        """Test permission error aborts processing with RuntimeError."""
        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Simulate permission denied error
        mock_run.return_value = Mock(
            returncode=1,
            stderr="Permission denied: cannot access file",
            stdout=""
        )

        with pytest.raises(RuntimeError, match="Critical FFmpeg error: permission"):
            self.command.extract_metadata(self.test_file)

        assert mock_run.call_count == 1, "Critical error should not trigger retry"

    @patch('samplify.management.commands.scan_input.get_ffmpeg_path')
    @patch('samplify.management.commands.scan_input.subprocess.run')
    @patch('samplify.management.commands.scan_input.time.sleep')
    def test_retry_logic_exhaustion(self, mock_sleep, mock_run, mock_get_ffmpeg):
        """Test retry logic exhausts after MAX_RETRIES attempts."""
        from samplify.management.commands.scan_input import MAX_RETRIES

        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Simulate persistent network error
        mock_run.return_value = Mock(
            returncode=1,
            stderr="Connection timeout",
            stdout=""
        )

        result = self.command.extract_metadata(self.test_file)

        assert result is None
        assert mock_run.call_count == MAX_RETRIES, f"Should attempt {MAX_RETRIES} times"
        assert mock_sleep.call_count == MAX_RETRIES - 1, f"Should sleep {MAX_RETRIES - 1} times"

        # Verify exponential backoff delays: 2s, 4s, 6s (RETRY_DELAY * attempt)
        expected_delays = [2, 4]
        actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
        assert actual_delays == expected_delays, f"Expected delays {expected_delays}, got {actual_delays}"

    @patch('samplify.management.commands.scan_input.get_ffmpeg_path')
    @patch('samplify.management.commands.scan_input.subprocess.run')
    @patch('samplify.management.commands.scan_input.time.sleep')
    def test_timeout_treated_as_network_error(self, mock_sleep, mock_run, mock_get_ffmpeg):
        """Test subprocess timeout is treated as network error and triggers retry."""
        import subprocess

        mock_get_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Simulate timeout on first attempt, success on second
        mock_run.side_effect = [
            subprocess.TimeoutExpired(cmd="ffmpeg", timeout=30),  # Attempt 1: timeout
            Mock(returncode=0, stdout=json.dumps({  # Attempt 2: success
                "streams": [{"codec_type": "audio", "codec_name": "mp3", "sample_rate": "48000"}],
                "format": {"size": "2048000"}
            }), stderr="")
        ]

        result = self.command.extract_metadata(self.test_file)

        assert result is not None
        assert result["codec"] == "mp3"
        assert mock_run.call_count == 2, "Should retry after timeout"
        assert mock_sleep.call_count == 1, "Should sleep between retries"
