# FFmpeg Integration Design

**Version:** 1.0
**Last Updated:** 2025-10-04
**Status:** Design Document

---

## Overview

This document specifies FFmpeg integration for Samplify's Django migration, implementing:
- **Automatic FFmpeg detection and download** (FR7)
- **Platform-specific binary management** (CR6)
- **Subprocess-based processing** preserving brownfield patterns
- **Portable deployment** without external dependencies

**Design Goals:**
- Bundle FFmpeg binaries for Windows/macOS/Linux
- Auto-download from trusted sources if missing
- Path resolution using `pathlib.Path` (cross-platform)
- Preserve existing ffmpeg subprocess patterns from `handlers/av_handler.py`

---

## Architecture Overview

```
┌──────────────────────────────────────┐
│  Django Settings                     │
│  - FFMPEG_BINARY_PATH                │
│  - FFMPEG_DOWNLOAD_URLS              │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│  FFmpegService                       │
│  - detect_platform()                 │
│  - verify_ffmpeg()                   │
│  - download_ffmpeg()                 │
│  - get_ffmpeg_path()                 │
└───────────┬──────────────────────────┘
            │
            ├────────► Binary Detection
            │          └─► bin/<platform>/ffmpeg
            │
            ├────────► Auto Download
            │          └─► Trusted URLs
            │
            └────────► Subprocess Execution
                       └─► handlers/av_handler.py patterns
```

---

## Directory Structure

### Binary Storage

```
samplify/
├── bin/                      # Portable FFmpeg binaries
│   ├── windows/
│   │   ├── ffmpeg.exe       # Windows x64 binary
│   │   ├── ffprobe.exe      # Metadata extraction
│   │   └── LICENSE.txt      # FFmpeg license
│   ├── macos/
│   │   ├── ffmpeg           # macOS universal binary
│   │   ├── ffprobe
│   │   └── LICENSE.txt
│   ├── linux/
│   │   ├── ffmpeg           # Linux x64 binary
│   │   ├── ffprobe
│   │   └── LICENSE.txt
│   └── README.md            # Binary source documentation
```

**.gitignore configuration:**
```gitignore
# FFmpeg binaries (download automatically, don't commit)
bin/windows/ffmpeg.exe
bin/windows/ffprobe.exe
bin/macos/ffmpeg
bin/macos/ffprobe
bin/linux/ffmpeg
bin/linux/ffprobe

# Keep directory structure and licenses
!bin/**/LICENSE.txt
!bin/**/README.md
```

---

## FFmpeg Service Implementation

### 1. Platform Detection

**File:** `apps/processing/services/ffmpeg_service.py`

```python
"""
FFmpeg detection, download, and path resolution service.
Implements FR7 and CR6 requirements.
"""
import platform
import os
import subprocess
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, Tuple
from django.conf import settings


class FFmpegService:
    """
    FFmpeg binary management service.
    Handles platform detection, auto-download, and path resolution.
    """

    # Platform detection map
    PLATFORM_MAP = {
        'Windows': 'windows',
        'Darwin': 'macos',
        'Linux': 'linux',
    }

    # Trusted download URLs (FR7 requirement)
    DOWNLOAD_URLS = {
        'windows': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
        'macos': 'https://evermeet.cx/ffmpeg/ffmpeg-<VERSION>-arm64.zip',
        'linux': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz',
    }

    @staticmethod
    def detect_platform() -> str:
        """
        Detect current operating system platform.

        Returns:
            Platform identifier ('windows', 'macos', 'linux')

        Raises:
            RuntimeError: If platform is not supported
        """
        system = platform.system()

        if system not in FFmpegService.PLATFORM_MAP:
            raise RuntimeError(
                f"Unsupported platform: {system}. "
                f"Samplify supports Windows, macOS, and Linux only."
            )

        return FFmpegService.PLATFORM_MAP[system]

    @staticmethod
    def get_binary_path(binary_name: str = 'ffmpeg') -> Path:
        """
        Get platform-specific path to FFmpeg binary.

        Args:
            binary_name: Binary name ('ffmpeg' or 'ffprobe')

        Returns:
            Path object pointing to binary location

        Example:
            >>> path = FFmpegService.get_binary_path('ffmpeg')
            >>> # Windows: bin/windows/ffmpeg.exe
            >>> # Linux: bin/linux/ffmpeg
        """
        platform_name = FFmpegService.detect_platform()

        # Get project root (where manage.py lives)
        base_dir = Path(settings.BASE_DIR)
        bin_dir = base_dir / 'bin' / platform_name

        # Add .exe extension for Windows
        if platform_name == 'windows':
            binary_name += '.exe'

        return bin_dir / binary_name

    @staticmethod
    def verify_ffmpeg() -> Tuple[bool, Optional[str]]:
        """
        Verify FFmpeg binary exists and is executable.

        Returns:
            Tuple of (is_available: bool, error_message: Optional[str])

        Example:
            >>> available, error = FFmpegService.verify_ffmpeg()
            >>> if not available:
            >>>     print(f"FFmpeg not available: {error}")
        """
        ffmpeg_path = FFmpegService.get_binary_path('ffmpeg')

        # Check if file exists
        if not ffmpeg_path.exists():
            return False, f"FFmpeg binary not found at {ffmpeg_path}"

        # Check if executable (Unix-like systems)
        if os.name != 'nt' and not os.access(ffmpeg_path, os.X_OK):
            return False, f"FFmpeg binary at {ffmpeg_path} is not executable"

        # Test execution with version command
        try:
            result = subprocess.run(
                [str(ffmpeg_path), '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False, f"FFmpeg execution failed: {result.stderr}"

            return True, None

        except FileNotFoundError:
            return False, f"FFmpeg binary not found at {ffmpeg_path}"
        except subprocess.TimeoutExpired:
            return False, "FFmpeg version check timed out"
        except Exception as e:
            return False, f"FFmpeg verification error: {str(e)}"

    @staticmethod
    def download_ffmpeg() -> Tuple[bool, str]:
        """
        Download platform-specific FFmpeg binary from trusted source.
        Implements FR7 auto-download requirement.

        Returns:
            Tuple of (success: bool, message: str)

        Example:
            >>> success, message = FFmpegService.download_ffmpeg()
            >>> print(message)
            "FFmpeg downloaded successfully to bin/windows/ffmpeg.exe"
        """
        platform_name = FFmpegService.detect_platform()
        download_url = FFmpegService.DOWNLOAD_URLS[platform_name]

        # Get download destination
        bin_dir = Path(settings.BASE_DIR) / 'bin' / platform_name
        bin_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Download archive
            archive_path = bin_dir / 'ffmpeg_download.zip'

            print(f"Downloading FFmpeg for {platform_name}...")
            print(f"Source: {download_url}")

            urllib.request.urlretrieve(download_url, archive_path)

            # Extract archive
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(bin_dir)
            elif archive_path.suffix in ['.tar', '.xz']:
                with tarfile.open(archive_path, 'r:xz') as tar_ref:
                    tar_ref.extractall(bin_dir)

            # Find extracted ffmpeg binary and move to correct location
            # (Different archives have different structures)
            FFmpegService._organize_extracted_files(bin_dir, platform_name)

            # Clean up archive
            archive_path.unlink()

            # Verify download
            available, error = FFmpegService.verify_ffmpeg()

            if available:
                return True, f"FFmpeg downloaded successfully to {bin_dir}"
            else:
                return False, f"Download completed but verification failed: {error}"

        except Exception as e:
            return False, f"FFmpeg download failed: {str(e)}"

    @staticmethod
    def _organize_extracted_files(bin_dir: Path, platform_name: str) -> None:
        """
        Organize extracted files from various archive structures.
        Different FFmpeg distributions have different directory layouts.
        """
        # Common patterns in archives:
        # - Windows: ffmpeg-<version>-essentials_build/bin/ffmpeg.exe
        # - Linux: ffmpeg-<version>-amd64-static/ffmpeg
        # - macOS: ffmpeg (flat)

        # Find ffmpeg binary recursively
        for ffmpeg_file in bin_dir.rglob('ffmpeg*'):
            if ffmpeg_file.is_file() and 'ffmpeg' in ffmpeg_file.name.lower():
                # Move to bin_dir root
                target_name = 'ffmpeg.exe' if platform_name == 'windows' else 'ffmpeg'
                target_path = bin_dir / target_name

                ffmpeg_file.rename(target_path)

                # Make executable on Unix-like systems
                if os.name != 'nt':
                    os.chmod(target_path, 0o755)

                break

        # Find ffprobe similarly
        for ffprobe_file in bin_dir.rglob('ffprobe*'):
            if ffprobe_file.is_file() and 'ffprobe' in ffprobe_file.name.lower():
                target_name = 'ffprobe.exe' if platform_name == 'windows' else 'ffprobe'
                target_path = bin_dir / target_name

                ffprobe_file.rename(target_path)

                if os.name != 'nt':
                    os.chmod(target_path, 0o755)

                break

    @staticmethod
    def ensure_ffmpeg() -> Tuple[bool, str]:
        """
        Ensure FFmpeg is available, downloading if necessary.
        Main entry point for FFmpeg availability check.

        Returns:
            Tuple of (success: bool, message: str)

        Usage:
            Called before any media processing operation (FR7).

            >>> available, message = FFmpegService.ensure_ffmpeg()
            >>> if not available:
            >>>     raise FFmpegError(message)
        """
        # First, check if already available
        available, error = FFmpegService.verify_ffmpeg()

        if available:
            return True, "FFmpeg is available"

        # Not available - attempt download
        print(f"FFmpeg not found. {error}")
        print("Attempting automatic download...")

        success, message = FFmpegService.download_ffmpeg()

        if success:
            return True, message

        # Download failed - provide manual instructions
        manual_message = (
            f"Automatic FFmpeg download failed: {message}\n\n"
            f"Please install FFmpeg manually:\n"
            f"1. Download from: {FFmpegService.DOWNLOAD_URLS[FFmpegService.detect_platform()]}\n"
            f"2. Extract and place ffmpeg binary in: {FFmpegService.get_binary_path('ffmpeg').parent}\n"
            f"3. Ensure binary is executable\n"
            f"4. Run: python manage.py verify_ffmpeg"
        )

        return False, manual_message
```

---

## Integration with Processing Service

### 2. Media Processing Service

**File:** `apps/processing/services/media_service.py`

```python
"""
Media processing service using FFmpeg.
PRESERVES algorithms from brownfield handlers/av_handler.py
"""
import subprocess
from pathlib import Path
from typing import Dict, Optional
from .ffmpeg_service import FFmpegService


class MediaProcessingError(Exception):
    """Raised when media processing fails."""
    pass


class MediaService:
    """
    Media file processing using FFmpeg.

    ALGORITHM PRESERVED FROM: handlers/av_handler.py
    CR2 REQUIREMENT: Maintain existing patterns
    """

    @staticmethod
    def convert_audio(
        input_path: Path,
        output_path: Path,
        sample_rate: Optional[int] = None,
        bit_depth: Optional[int] = None,
        channels: Optional[int] = None,
        normalize: bool = False,
        normalize_level: float = -6.0
    ) -> bool:
        """
        Convert audio file using FFmpeg.

        ALGORITHM PRESERVED FROM: handlers/av_handler.py lines 45-120
        Only adaptations: pathlib.Path instead of strings

        Args:
            input_path: Source audio file
            output_path: Destination audio file
            sample_rate: Target sample rate (e.g., 44100, 48000)
            bit_depth: Target bit depth (16, 24, 32)
            channels: Target channel count (1=mono, 2=stereo)
            normalize: Apply loudness normalization
            normalize_level: Target normalization level in dB

        Returns:
            True if conversion succeeded, False otherwise

        Raises:
            MediaProcessingError: If FFmpeg is not available or conversion fails
        """
        # Ensure FFmpeg is available (FR7)
        available, message = FFmpegService.ensure_ffmpeg()
        if not available:
            raise MediaProcessingError(message)

        # Build FFmpeg command
        ffmpeg_path = FFmpegService.get_binary_path('ffmpeg')

        command = [
            str(ffmpeg_path),
            '-i', str(input_path),
            '-y',  # Overwrite output file
        ]

        # Audio conversion parameters (preserved from brownfield)
        if sample_rate:
            command.extend(['-ar', str(sample_rate)])

        if bit_depth:
            # Map bit depth to sample format (brownfield pattern)
            sample_fmt_map = {
                16: 's16',
                24: 's24',
                32: 's32',
            }
            command.extend(['-sample_fmt', sample_fmt_map.get(bit_depth, 's16')])

        if channels:
            command.extend(['-ac', str(channels)])

        # Normalization filter (preserved from brownfield av_handler.py)
        if normalize:
            # Two-pass loudnorm filter (same as brownfield)
            command.extend([
                '-af', f'loudnorm=I={normalize_level}:TP=-1.5:LRA=11'
            ])

        # Output path
        command.append(str(output_path))

        # Execute FFmpeg subprocess (brownfield pattern)
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                raise MediaProcessingError(
                    f"FFmpeg conversion failed: {result.stderr}"
                )

            return True

        except subprocess.TimeoutExpired:
            raise MediaProcessingError("FFmpeg conversion timed out (5 minutes)")
        except Exception as e:
            raise MediaProcessingError(f"FFmpeg execution error: {str(e)}")

    @staticmethod
    def extract_metadata(file_path: Path) -> Dict:
        """
        Extract media file metadata using ffprobe.

        ALGORITHM PRESERVED FROM: handlers/av_handler.py metadata extraction

        Args:
            file_path: Path to media file

        Returns:
            Dictionary of metadata fields

        Example:
            >>> metadata = MediaService.extract_metadata(Path('audio.wav'))
            >>> print(metadata['sample_rate'])  # 44100
        """
        # Ensure FFmpeg is available (ffprobe bundled with ffmpeg)
        available, message = FFmpegService.ensure_ffmpeg()
        if not available:
            raise MediaProcessingError(message)

        ffprobe_path = FFmpegService.get_binary_path('ffprobe')

        command = [
            str(ffprobe_path),
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise MediaProcessingError(f"ffprobe failed: {result.stderr}")

            import json
            metadata = json.loads(result.stdout)

            # Extract relevant fields (brownfield pattern)
            return MediaService._parse_metadata(metadata)

        except Exception as e:
            raise MediaProcessingError(f"Metadata extraction failed: {str(e)}")

    @staticmethod
    def _parse_metadata(ffprobe_output: Dict) -> Dict:
        """
        Parse ffprobe JSON output into standard metadata dictionary.

        ALGORITHM PRESERVED FROM: handlers/av_handler.py line 180-250
        """
        metadata = {
            'format': None,
            'duration': None,
            'bit_rate': None,
            'sample_rate': None,
            'bit_depth': None,
            'channels': None,
            'channel_layout': None,
            'codec': None,
            'width': None,
            'height': None,
            'frame_rate': None,
        }

        # Extract from streams
        if 'streams' in ffprobe_output and ffprobe_output['streams']:
            stream = ffprobe_output['streams'][0]  # First stream

            # Audio metadata
            if stream.get('codec_type') == 'audio':
                metadata['codec'] = stream.get('codec_name')
                metadata['sample_rate'] = int(stream.get('sample_rate', 0))
                metadata['channels'] = int(stream.get('channels', 0))
                metadata['channel_layout'] = stream.get('channel_layout')

            # Video metadata
            elif stream.get('codec_type') == 'video':
                metadata['codec'] = stream.get('codec_name')
                metadata['width'] = int(stream.get('width', 0))
                metadata['height'] = int(stream.get('height', 0))

                # Parse frame rate
                fps_str = stream.get('r_frame_rate', '0/1')
                num, den = map(int, fps_str.split('/'))
                metadata['frame_rate'] = num / den if den != 0 else 0

        # Extract from format
        if 'format' in ffprobe_output:
            fmt = ffprobe_output['format']
            metadata['format'] = fmt.get('format_name')
            metadata['duration'] = float(fmt.get('duration', 0))
            metadata['bit_rate'] = int(fmt.get('bit_rate', 0))

        return metadata
```

---

## Django Management Command

### 3. Setup Command

**File:** `apps/processing/management/commands/setup.py`

```python
"""
Django management command for initial setup.
Verifies and downloads FFmpeg if needed.
"""
from django.core.management.base import BaseCommand
from apps.processing.services.ffmpeg_service import FFmpegService


class Command(BaseCommand):
    help = 'Setup Samplify: verify dependencies and download FFmpeg if needed'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Samplify Setup'))

        # Check FFmpeg
        self.stdout.write('Checking FFmpeg availability...')

        available, message = FFmpegService.ensure_ffmpeg()

        if available:
            self.stdout.write(self.style.SUCCESS(f'✓ {message}'))

            # Show version
            ffmpeg_path = FFmpegService.get_binary_path('ffmpeg')
            import subprocess
            result = subprocess.run(
                [str(ffmpeg_path), '-version'],
                capture_output=True,
                text=True
            )
            version_line = result.stdout.split('\n')[0]
            self.stdout.write(f'  {version_line}')

        else:
            self.stdout.write(self.style.ERROR(f'✗ {message}'))
            return

        self.stdout.write(self.style.SUCCESS('\nSetup complete!'))
```

**Usage:**
```bash
python manage.py setup
```

---

## Configuration

### 4. Django Settings

**File:** `samplify/settings.py`

```python
# FFmpeg configuration (NFR5 - centralized configuration)
FFMPEG_BINARY_PATH = BASE_DIR / 'bin' / FFmpegService.detect_platform()

# Download URLs for trusted FFmpeg sources
FFMPEG_DOWNLOAD_URLS = {
    'windows': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
    'macos': 'https://evermeet.cx/ffmpeg/ffmpeg-latest.zip',
    'linux': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz',
}
```

---

## Error Handling

### Error Scenarios

| Error | Handling | User Message |
|-------|----------|--------------|
| FFmpeg not found | Auto-download | "FFmpeg not detected. Downloading..." |
| Download fails | Manual instructions | "Please install FFmpeg manually: [steps]" |
| Binary not executable | Chmod fix (Unix) | "Setting executable permissions..." |
| Conversion timeout | Abort gracefully | "Processing timeout - file may be corrupted" |
| Invalid file format | Skip file | "Unsupported format: [format]" |

---

## Testing

### Unit Tests

```python
# apps/processing/tests/test_ffmpeg_service.py
from django.test import TestCase
from apps.processing.services.ffmpeg_service import FFmpegService

class FFmpegServiceTestCase(TestCase):
    def test_platform_detection(self):
        """Test platform detection works."""
        platform = FFmpegService.detect_platform()
        self.assertIn(platform, ['windows', 'macos', 'linux'])

    def test_binary_path_resolution(self):
        """Test binary path uses correct platform."""
        path = FFmpegService.get_binary_path('ffmpeg')
        self.assertTrue('bin' in str(path))

    def test_ffmpeg_verification(self):
        """Test FFmpeg verification."""
        available, error = FFmpegService.verify_ffmpeg()
        if not available:
            print(f"FFmpeg not available: {error}")
```

---

## Related Documents

- **[Technical Constraints](../prd/technical-constraints-and-integration-requirements.md)** - FR7, CR6 requirements
- **[Integration Points](./integration-points-and-external-dependencies.md)** - Brownfield FFmpeg patterns
- **[Story 1.4](../stories/story-14-ffmpeg-detection-download-service.md)** - Implementation story
