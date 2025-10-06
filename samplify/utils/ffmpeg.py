"""
FFmpeg Detection & Download Service

Provides automated FFmpeg binary detection, download, and path resolution
for cross-platform media processing operations.

Usage:
    from samplify.utils.ffmpeg import get_ffmpeg_path

    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path:
        # Use ffmpeg_path for media operations
        pass
"""

import os
import platform
import subprocess
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import Optional
from django.core.cache import cache
from loguru import logger


# FFmpeg download URLs by platform
FFMPEG_URLS = {
    'Windows': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
    'Darwin': 'https://evermeet.cx/ffmpeg/ffmpeg-7.0.2.zip',  # macOS
    'Linux': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
}

# Platform-specific binary names
BINARY_NAMES = {
    'Windows': 'ffmpeg.exe',
    'Darwin': 'ffmpeg',
    'Linux': 'ffmpeg'
}

# Cache key for FFmpeg path
CACHE_KEY = 'ffmpeg_binary_path'
CACHE_TIMEOUT = 86400  # 24 hours


def get_platform() -> str:
    """
    Detect current operating system.

    Returns:
        str: 'Windows', 'Darwin' (macOS), or 'Linux'
    """
    return platform.system()


def get_bin_directory() -> Path:
    """
    Get platform-specific binary directory.

    Returns:
        Path: Directory path for platform-specific FFmpeg binaries
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    platform_name = get_platform()
    return project_root / 'bin' / platform_name


def get_expected_binary_path() -> Path:
    """
    Get expected FFmpeg binary path for current platform.

    Returns:
        Path: Expected path to FFmpeg binary
    """
    platform_name = get_platform()
    binary_name = BINARY_NAMES.get(platform_name, 'ffmpeg')
    return get_bin_directory() / binary_name


def verify_ffmpeg(ffmpeg_path: Path) -> bool:
    """
    Verify FFmpeg binary works by running 'ffmpeg -version'.

    Args:
        ffmpeg_path: Path to FFmpeg binary

    Returns:
        bool: True if FFmpeg works, False otherwise
    """
    try:
        result = subprocess.run(
            [str(ffmpeg_path), '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info(f"FFmpeg verified successfully: {ffmpeg_path}")
            return True
        else:
            logger.warning(f"FFmpeg verification failed: {ffmpeg_path}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.error(f"FFmpeg verification error: {e}")
        return False


def download_ffmpeg() -> bool:
    """
    Download and extract FFmpeg for current platform.

    Returns:
        bool: True if download successful, False otherwise
    """
    platform_name = get_platform()
    download_url = FFMPEG_URLS.get(platform_name)

    if not download_url:
        logger.error(f"No FFmpeg download URL configured for platform: {platform_name}")
        return False

    bin_dir = get_bin_directory()
    bin_dir.mkdir(parents=True, exist_ok=True)

    # Determine archive filename and type
    archive_name = download_url.split('/')[-1]
    archive_path = bin_dir / archive_name

    try:
        logger.info(f"Downloading FFmpeg from: {download_url}")

        # Download with timeout
        with urllib.request.urlopen(download_url, timeout=60) as response:
            with open(archive_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

        logger.info(f"Download complete: {archive_path}")

        # Extract archive
        logger.info("Extracting FFmpeg archive...")

        if archive_name.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(bin_dir)
        elif archive_name.endswith('.tar.xz'):
            with tarfile.open(archive_path, 'r:xz') as tar_ref:
                tar_ref.extractall(bin_dir)
        else:
            logger.error(f"Unsupported archive format: {archive_name}")
            return False

        logger.info("Extraction complete")

        # Find and move FFmpeg binary to expected location
        binary_name = BINARY_NAMES[platform_name]
        expected_path = get_expected_binary_path()

        # Search for ffmpeg binary in extracted files
        for root, dirs, files in os.walk(bin_dir):
            if binary_name in files:
                found_binary = Path(root) / binary_name
                if found_binary != expected_path:
                    logger.info(f"Moving FFmpeg binary: {found_binary} -> {expected_path}")
                    shutil.move(str(found_binary), str(expected_path))
                break

        # Make binary executable on Unix-like systems
        if platform_name in ['Darwin', 'Linux']:
            os.chmod(expected_path, 0o755)

        # Clean up archive
        archive_path.unlink()

        logger.info(f"FFmpeg installed successfully: {expected_path}")
        return True

    except urllib.error.URLError as e:
        logger.error(f"Failed to download FFmpeg: {e}")
        return False
    except Exception as e:
        logger.error(f"Error during FFmpeg installation: {e}")
        return False


def get_manual_install_instructions() -> str:
    """
    Get platform-specific manual installation instructions.

    Returns:
        str: Manual installation instructions
    """
    platform_name = get_platform()
    bin_dir = get_bin_directory()

    instructions = {
        'Windows': f"""
Manual FFmpeg Installation Instructions (Windows):
1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Extract the archive
3. Copy ffmpeg.exe to: {bin_dir}
4. Restart the application
""",
        'Darwin': f"""
Manual FFmpeg Installation Instructions (macOS):
1. Install via Homebrew: brew install ffmpeg
   OR
2. Download from: https://evermeet.cx/ffmpeg/
3. Copy ffmpeg binary to: {bin_dir}
4. Make executable: chmod +x {bin_dir / 'ffmpeg'}
5. Restart the application
""",
        'Linux': f"""
Manual FFmpeg Installation Instructions (Linux):
1. Install via package manager: sudo apt-get install ffmpeg
   OR
2. Download from: https://johnvansickle.com/ffmpeg/
3. Copy ffmpeg binary to: {bin_dir}
4. Make executable: chmod +x {bin_dir / 'ffmpeg'}
5. Restart the application
"""
    }

    return instructions.get(platform_name, "Please install FFmpeg manually for your platform.")


def get_ffmpeg_path(force_refresh: bool = False) -> Optional[str]:
    """
    Get FFmpeg binary path with automatic detection and download.

    This function:
    1. Checks cache for previously detected path
    2. Checks expected binary location
    3. Attempts automatic download if not found
    4. Returns path or None if unavailable

    Args:
        force_refresh: If True, bypass cache and re-detect FFmpeg

    Returns:
        str: Path to FFmpeg binary, or None if unavailable
    """
    # Check cache first
    if not force_refresh:
        cached_path = cache.get(CACHE_KEY)
        if cached_path and Path(cached_path).exists():
            logger.debug(f"Using cached FFmpeg path: {cached_path}")
            return cached_path

    # Check expected binary location
    expected_path = get_expected_binary_path()

    if expected_path.exists() and verify_ffmpeg(expected_path):
        # Cache the path
        cache.set(CACHE_KEY, str(expected_path), CACHE_TIMEOUT)
        return str(expected_path)

    # Try automatic download
    logger.info("FFmpeg not found, attempting automatic download...")

    if download_ffmpeg():
        # Verify downloaded binary
        if expected_path.exists() and verify_ffmpeg(expected_path):
            cache.set(CACHE_KEY, str(expected_path), CACHE_TIMEOUT)
            return str(expected_path)

    # Download failed - provide manual instructions
    logger.error("FFmpeg auto-download failed")
    logger.info(get_manual_install_instructions())

    return None


def check_ffmpeg_available() -> bool:
    """
    Check if FFmpeg is available and ready to use.

    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    ffmpeg_path = get_ffmpeg_path()
    return ffmpeg_path is not None
