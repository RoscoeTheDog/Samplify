"""
File Scanning Service - Django Management Command

Scans input directories and populates database with file metadata using FFmpeg.

CRITICAL CR1 PRESERVATION:
- Search/filter algorithms from handlers/rules.py PRESERVED EXACTLY
- Only Django ORM adaptations allowed, NOT algorithm logic changes

Usage:
    python manage.py scan_input --schema-id=1
    python manage.py scan_input --schema-id=1 --force-rescan
"""

import json
import re
import subprocess
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from loguru import logger

from apps.catalog.models import DirectoryMapping, File, Schema
from samplify.utils.ffmpeg import get_ffmpeg_path


# ============================================================================
# Error Classification System
# ============================================================================


class FFmpegErrorType(Enum):
    """
    FFmpeg error classification for categorizing failure types.

    Used to distinguish between:
    - Transient errors that should be retried (network issues)
    - Permanent errors that should be skipped (corrupt files, unsupported formats)
    - Critical errors that should abort processing (permission denied, disk full)
    """
    CORRUPT_FILE = "corrupt_file"          # Permanently damaged file
    UNSUPPORTED_FORMAT = "unsupported"     # Format not supported by FFmpeg
    NETWORK_ERROR = "network"              # Network/timeout issues
    PERMISSION_ERROR = "permission"        # File access denied
    DISK_ERROR = "disk"                    # Disk full/IO error
    UNKNOWN = "unknown"                     # Unclassified error


def parse_ffmpeg_error(stderr_output: str) -> FFmpegErrorType:
    """
    Parse FFmpeg error output and categorize the error type.

    Uses pattern matching to identify error categories from FFmpeg stderr.
    This enables intelligent retry/skip/abort decisions based on error type.

    Args:
        stderr_output: FFmpeg stderr output string

    Returns:
        FFmpegErrorType: Categorized error type

    Examples:
        >>> parse_ffmpeg_error("Invalid data found when processing input")
        FFmpegErrorType.CORRUPT_FILE

        >>> parse_ffmpeg_error("Connection timed out")
        FFmpegErrorType.NETWORK_ERROR
    """
    stderr_lower = stderr_output.lower()

    # Pattern matching for error types
    if "invalid data found" in stderr_lower or "invalid" in stderr_lower:
        return FFmpegErrorType.CORRUPT_FILE
    elif "unknown format" in stderr_lower or "not supported" in stderr_lower:
        return FFmpegErrorType.UNSUPPORTED_FORMAT
    elif "connection" in stderr_lower or "timeout" in stderr_lower:
        return FFmpegErrorType.NETWORK_ERROR
    elif "permission denied" in stderr_lower or "access denied" in stderr_lower:
        return FFmpegErrorType.PERMISSION_ERROR
    elif "no space left" in stderr_lower or "i/o error" in stderr_lower:
        return FFmpegErrorType.DISK_ERROR
    else:
        return FFmpegErrorType.UNKNOWN


# Retry configuration for transient errors
MAX_RETRIES = 3
RETRY_DELAY = 2  # Base delay in seconds (will be multiplied by attempt number)


class Command(BaseCommand):
    """Django management command for scanning input directories and populating File model."""

    help = "Scan input directories and populate File model with media metadata"

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--schema-id",
            type=int,
            required=True,
            help="Schema ID to scan directories for",
        )
        parser.add_argument(
            "--force-rescan",
            action="store_true",
            help="Force rescan of all files, even if already in database",
        )

    def handle(self, *args, **options):
        """Main command handler."""
        schema_id = options["schema_id"]
        force_rescan = options["force_rescan"]

        try:
            schema = Schema.objects.get(id=schema_id)
        except Schema.DoesNotExist:
            raise CommandError(f"Schema with ID {schema_id} does not exist")

        logger.info(f"Starting file scan for schema: {schema.name}")

        if force_rescan:
            logger.info("Force rescan enabled - will rescan all files")

        # Get input directories for this schema
        directory_mappings = DirectoryMapping.objects.filter(schema=schema)

        if not directory_mappings.exists():
            logger.warning(f"No directory mappings found for schema {schema.name}")
            return

        total_files_scanned = 0
        total_files_added = 0
        total_files_updated = 0
        total_files_deleted = 0

        for mapping in directory_mappings:
            logger.info(f"Scanning directory: {mapping.input_path}")

            files_in_directory = self.scan_directory(mapping.input_path)

            for file_path in files_in_directory:
                try:
                    # Extract metadata using FFmpeg
                    metadata = self.extract_metadata(file_path)

                    if metadata:
                        # Create or update File record (with directory mapping for schema association)
                        file_obj, created = self.upsert_file(file_path, metadata, force_rescan, mapping)

                        if created:
                            total_files_added += 1
                        elif file_obj:
                            total_files_updated += 1

                        total_files_scanned += 1

                        if total_files_scanned % 100 == 0:
                            logger.info(f"Progress: {total_files_scanned} files scanned")

                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    continue

        # Delete File records for files that no longer exist
        deleted_count = self.cleanup_missing_files()
        total_files_deleted = deleted_count

        logger.info("Scan complete!")
        logger.info(f"  Total files scanned: {total_files_scanned}")
        logger.info(f"  Files added: {total_files_added}")
        logger.info(f"  Files updated: {total_files_updated}")
        logger.info(f"  Files deleted: {total_files_deleted}")

    def scan_directory(self, directory_path: str) -> List[Path]:
        """
        Scan directory for media files.

        CR1 PRESERVATION: Directory traversal algorithm preserved from __main__.py lines 206-469

        Args:
            directory_path: Path to directory to scan

        Returns:
            List of Path objects for discovered files
        """
        directory = Path(directory_path)

        if not directory.exists() or not directory.is_dir():
            logger.warning(f"Directory does not exist or is not a directory: {directory_path}")
            return []

        files = []

        # Supported media extensions
        media_extensions = {
            # Audio
            ".wav",
            ".mp3",
            ".flac",
            ".aiff",
            ".aif",
            ".m4a",
            ".ogg",
            ".wma",
            # Video
            ".mp4",
            ".mov",
            ".avi",
            ".mkv",
            ".wmv",
            ".flv",
            ".webm",
            # Image
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
        }

        # Recursive directory traversal (breadth-first, preserving brownfield pattern)
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in media_extensions:
                files.append(file_path)

        logger.info(f"Found {len(files)} media files in {directory_path}")
        return files

    def extract_metadata(self, file_path: Path) -> Optional[Dict]:
        """
        Extract media metadata using FFmpeg with intelligent error handling.

        Integration with Story 1.4 FFmpeg service, enhanced with:
        - Error classification (transient vs permanent vs critical)
        - Automatic retry for transient errors (network issues)
        - Structured logging with error categorization

        Args:
            file_path: Path to media file

        Returns:
            Dictionary with metadata or None if extraction failed
        """
        ffmpeg_path = get_ffmpeg_path()

        if not ffmpeg_path:
            logger.error("FFmpeg not available - cannot extract metadata")
            return None

        # Retry loop for transient errors
        for attempt in range(MAX_RETRIES):
            try:
                # Run FFmpeg probe to get metadata
                cmd = [
                    ffmpeg_path,
                    "-i",
                    str(file_path),
                    "-print_format",
                    "json",
                    "-show_format",
                    "-show_streams",
                    "-v",
                    "quiet",
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode != 0:
                    # Parse error type from stderr
                    error_type = parse_ffmpeg_error(result.stderr)

                    # Handle error based on type
                    if error_type == FFmpegErrorType.NETWORK_ERROR and attempt < MAX_RETRIES - 1:
                        # Transient error - retry with exponential backoff
                        delay = RETRY_DELAY * (attempt + 1)
                        logger.warning(
                            f"Network error processing {file_path} (attempt {attempt + 1}/{MAX_RETRIES}) - retrying in {delay}s"
                        )
                        time.sleep(delay)
                        continue

                    elif error_type in [FFmpegErrorType.CORRUPT_FILE, FFmpegErrorType.UNSUPPORTED_FORMAT]:
                        # Permanent error - skip file with warning
                        logger.warning(
                            f"Skipping {file_path}: {error_type.value}"
                        )
                        return None

                    elif error_type in [FFmpegErrorType.PERMISSION_ERROR, FFmpegErrorType.DISK_ERROR]:
                        # Critical error - abort processing
                        logger.error(
                            f"Critical error: {error_type.value} for {file_path}"
                        )
                        raise RuntimeError(f"Critical FFmpeg error: {error_type.value}")

                    else:
                        # Unknown error - log and skip
                        logger.error(
                            f"Unknown FFmpeg error for {file_path}: {result.stderr[:200]}"
                        )
                        return None

                # Parse JSON output
                ffmpeg_data = json.loads(result.stdout)

                # Get file size safely (file must exist for FFmpeg to have succeeded)
                try:
                    file_size = file_path.stat().st_size
                except Exception:
                    file_size = 0

                # Extract relevant metadata
                metadata = {
                    "file_path": str(file_path.resolve()),
                    "file_name": file_path.name,
                    "file_format": file_path.suffix.lstrip(".").upper(),
                    "file_size": file_size,
                }

                # Detect media type and extract type-specific metadata
                streams = ffmpeg_data.get("streams", [])

                if not streams:
                    return None

                # Check for video stream
                video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
                # Check for audio stream
                audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

                if video_stream:
                    metadata["media_type"] = "video"
                    metadata["codec"] = video_stream.get("codec_name", "")
                    # Video may also have audio - get sample rate from audio stream
                    if audio_stream:
                        metadata["sample_rate"] = int(audio_stream.get("sample_rate", 0) or 0)
                        metadata["bit_depth"] = int(audio_stream.get("bits_per_raw_sample", 0) or 0)
                elif audio_stream:
                    metadata["media_type"] = "audio"
                    metadata["codec"] = audio_stream.get("codec_name", "")
                    metadata["sample_rate"] = int(audio_stream.get("sample_rate", 0) or 0)
                    metadata["bit_depth"] = int(audio_stream.get("bits_per_raw_sample", 0) or 0)
                else:
                    # Assume image if no audio/video streams
                    metadata["media_type"] = "image"
                    metadata["codec"] = streams[0].get("codec_name", "")

                return metadata

            except subprocess.TimeoutExpired:
                # Treat timeout as network error - retry if attempts remain
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY * (attempt + 1)
                    logger.warning(
                        f"FFmpeg timeout for {file_path} (attempt {attempt + 1}/{MAX_RETRIES}) - retrying in {delay}s"
                    )
                    time.sleep(delay)
                    continue
                else:
                    logger.error(
                        f"FFmpeg timeout for {file_path} after {MAX_RETRIES} attempts"
                    )
                    return None

            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse FFmpeg JSON output for {file_path}: {e}"
                )
                return None

            except RuntimeError:
                # Re-raise critical errors (permission, disk full)
                raise

            except Exception as e:
                logger.error(
                    f"Error extracting metadata from {file_path}: {e}"
                )
                return None

        # All retries exhausted
        return None

    def upsert_file(
        self,
        file_path: Path,
        metadata: Dict,
        force_rescan: bool,
        directory_mapping: DirectoryMapping
    ) -> tuple:
        """
        Create or update File record in database.

        Uses atomic database transactions to prevent partial records.

        Args:
            file_path: Path to file
            metadata: Metadata dictionary from FFmpeg
            force_rescan: Whether to update existing records
            directory_mapping: DirectoryMapping this file belongs to (for schema association)

        Returns:
            Tuple of (File object or None, created boolean)
        """
        try:
            with transaction.atomic():
                # Check if file already exists
                existing_file = File.objects.filter(file_path=metadata["file_path"]).first()

                if existing_file:
                    if force_rescan:
                        # Update existing record
                        existing_file.file_name = metadata["file_name"]
                        existing_file.file_format = metadata["file_format"]
                        existing_file.file_size = metadata["file_size"]
                        existing_file.media_type = metadata["media_type"]
                        existing_file.codec = metadata.get("codec")
                        existing_file.sample_rate = metadata.get("sample_rate")
                        existing_file.bit_depth = metadata.get("bit_depth")
                        existing_file.directory_mapping = directory_mapping  # Associate with schema
                        existing_file.save()

                        logger.debug(f"Updated file record: {metadata['file_name']}")
                        return existing_file, False
                    else:
                        # Skip if already exists and not forcing rescan
                        logger.debug(f"Skipping existing file: {metadata['file_name']}")
                        return existing_file, False

                # Create new File record
                file_obj = File.objects.create(
                    file_path=metadata["file_path"],
                    file_name=metadata["file_name"],
                    file_format=metadata["file_format"],
                    file_size=metadata["file_size"],
                    media_type=metadata["media_type"],
                    codec=metadata.get("codec"),
                    sample_rate=metadata.get("sample_rate"),
                    bit_depth=metadata.get("bit_depth"),
                    directory_mapping=directory_mapping,  # Associate with schema
                )

                logger.debug(f"Created file record: {metadata['file_name']}")
                return file_obj, True

        except Exception as e:
            logger.error(f"Database error for file {file_path}: {e}")
            return None, False

    def cleanup_missing_files(self) -> int:
        """
        Delete File records for files that no longer exist on filesystem.

        Preserves brownfield behavior of removing stale database entries.

        Returns:
            Number of File records deleted
        """
        deleted_count = 0

        files = File.objects.all()

        for file_obj in files:
            file_path = Path(file_obj.file_path)

            if not file_path.exists():
                logger.info(f"Deleting missing file record: {file_obj.file_name}")
                file_obj.delete()
                deleted_count += 1

        return deleted_count


# ============================================================================
# CR1 PRESERVED ALGORITHMS FROM handlers/rules.py
# These functions are preserved EXACTLY as they appeared in brownfield system
# ============================================================================


def contains_expression(file, output):
    """
    CR1 PRESERVED: Exact copy from handlers/rules.py lines 10-23

    Check if file name matches regex pattern expression.

    Args:
        file: File object (Django model)
        output: Dictionary with 'expression' and 'path' keys

    Returns:
        Dictionary with output directory mapping or empty dict
    """
    output_directories = {}  # indicates where this file goes

    exp = output.get("expression")
    if exp:
        pattern = re.compile(exp)
        search = pattern.finditer(file.file_name)  # Look for expressions in file name (ADAPTED: Django model attribute)

        for match in search:
            output_directories["output_directory"] = output.get("path")
            output_directories["file_name"] = file.file_name
            output_directories["file_path"] = file.file_path

    return output_directories


def contains_extensions(file, output):
    """
    CR1 PRESERVED: Exact copy from handlers/rules.py lines 26-42

    Check if file extension matches specified extensions.

    CRITICAL: Line 33 preserved EXACTLY as-is (purpose unclear, see cr1-extension-bug-analysis.md)

    Args:
        file: File object (Django model)
        output: Dictionary with 'extensions' and 'path' keys

    Returns:
        Dictionary with output directory mapping or empty dict
    """
    entry = {}

    extension = output.get("extensions")

    if extension:

        # CR1: Purpose unclear - preserved for post-migration validation
        extension.translate({ord(c): None for c in extension})

        for e in extension.split(","):

            # ADAPTED: Use Django model file_format attribute instead of extension
            if file.file_format.lower() in extension.lower():
                entry["output_directory"] = output.get("path")
                entry["file_name"] = file.file_name
                entry["file_path"] = file.file_path

    return entry


def between_datetime(file, output):
    """
    CR1 PRESERVED: Exact copy from handlers/rules.py lines 45-72

    Check if file creation date falls between specified date range.

    Args:
        file: File object (Django model)
        output: Dictionary with 'datetimeStart', 'datetimeEnd', and 'path' keys

    Returns:
        Dictionary with output directory mapping or empty dict
    """
    output_directories = {}

    datetime_start = output.get("datetimeStart")
    datetime_end = output.get("datetimeEnd")

    if datetime_start:

        datetime_start = datetime.strptime(datetime_start, "%Y-%m-%d")
        datetime_end = datetime.strptime(datetime_end, "%Y-%m-%d")

        # time delta ( > 0 ) between start and end
        delta_t = datetime_end - datetime_start

        # If > 0, we know the thresholds are not inversed incidentally.
        if delta_t:

            # time delta between file creation date and end threshold.
            # ADAPTED: Use Django model created_at instead of creation_date
            file_creation_date = file.created_at.strftime("%Y-%m-%d")
            delta_f = datetime_end - datetime.strptime(file_creation_date, "%Y-%m-%d")

            # Time delta must be less than the users specified threshold delta.
            # Also: must validate positive values since would be neg if passed user end threshold.
            if delta_f and delta_f <= delta_t:
                output_directories["output_directory"] = output.get("path")
                output_directories["file_name"] = file.file_name
                output_directories["file_path"] = file.file_path

    return output_directories


def contains_video(file, output):
    """
    CR1 PRESERVED: Exact copy from handlers/rules.py lines 75-85

    Check if file contains video stream.

    Args:
        file: File object (Django model)
        output: Dictionary with 'containsVideo' and 'path' keys

    Returns:
        Dictionary with output directory mapping or empty dict
    """
    output_directories = {}

    condition = output.get("containsVideo")

    # ADAPTED: Check media_type instead of v_stream attribute
    if condition and file.media_type == "video":
        output_directories["output_directory"] = output.get("path")
        output_directories["file_name"] = file.file_name
        output_directories["file_path"] = file.file_path

    return output_directories


def contains_audio(file, output):
    """
    CR1 PRESERVED: Exact copy from handlers/rules.py lines 88-98

    Check if file contains audio stream.

    Args:
        file: File object (Django model)
        output: Dictionary with 'containsAudio' and 'path' keys

    Returns:
        Dictionary with output directory mapping or empty dict
    """
    output_directories = {}

    condition = output.get("containsAudio")

    # ADAPTED: Check media_type instead of a_stream attribute
    if condition and file.media_type == "audio":
        output_directories["output_directory"] = output.get("path")
        output_directories["file_name"] = file.file_name
        output_directories["file_path"] = file.file_path

    return output_directories


def contains_image(file, output):
    """
    CR1 PRESERVED: Exact copy from handlers/rules.py lines 101-111

    Check if file contains image stream.

    Args:
        file: File object (Django model)
        output: Dictionary with 'containsImage' and 'path' keys

    Returns:
        Dictionary with output directory mapping or empty dict
    """
    output_directories = {}

    condition = output.get("containsImage")

    # ADAPTED: Check media_type instead of i_stream attribute
    if condition and file.media_type == "image":
        output_directories["output_directory"] = output.get("path")
        output_directories["file_name"] = file.file_name
        output_directories["file_path"] = file.file_path

    return output_directories
