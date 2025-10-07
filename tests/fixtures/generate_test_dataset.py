#!/usr/bin/env python
"""
Test Dataset Generator for Performance Benchmarking

Generates 1000 realistic media files for Story 1.5 NFR5 validation:
- 700 audio files (WAV format, various sample rates)
- 200 video files (MP4 format, various resolutions)
- 100 image files (JPEG format, various sizes)

Requirements:
- FFmpeg must be installed and available in PATH
- Minimum 50MB free disk space

Usage:
    python tests/fixtures/generate_test_dataset.py [output_dir]

Output:
    Creates directory structure:
    - output_dir/audio/  (700 WAV files)
    - output_dir/video/  (200 MP4 files)
    - output_dir/images/ (100 JPEG files)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Audio configurations (700 files)
AUDIO_CONFIGS = [
    # Sample Rate, Duration, Frequency, Count
    (44100, 0.5, 440, 200),   # CD quality, A440 note
    (48000, 0.5, 523, 200),   # Professional audio, C note
    (96000, 0.5, 659, 150),   # High-res audio, E note
    (22050, 0.5, 349, 100),   # Lower quality, F note
    (8000, 0.5, 293, 50),     # Telephone quality, D note
]

# Video configurations (200 files)
VIDEO_CONFIGS = [
    # Width, Height, Duration, FPS, Count
    (1280, 720, 0.5, 24, 80),    # 720p 24fps
    (1920, 1080, 0.5, 30, 80),   # 1080p 30fps
    (640, 480, 0.5, 30, 40),     # SD 30fps
]

# Image configurations (100 files)
IMAGE_CONFIGS = [
    # Width, Height, Count
    (1920, 1080, 40),  # Full HD
    (1280, 720, 30),   # HD
    (3840, 2160, 20),  # 4K
    (640, 480, 10),    # SD
]


def check_ffmpeg() -> bool:
    """Check if FFmpeg is available."""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def generate_audio_file(output_path: Path, sample_rate: int, duration: float, frequency: int) -> bool:
    """Generate a WAV audio file using FFmpeg."""
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'sine=frequency={frequency}:duration={duration}:sample_rate={sample_rate}',
        '-ar', str(sample_rate),
        '-y',  # Overwrite output files
        str(output_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def generate_video_file(output_path: Path, width: int, height: int, duration: float, fps: int) -> bool:
    """Generate an MP4 video file using FFmpeg."""
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'testsrc=duration={duration}:size={width}x{height}:rate={fps}',
        '-pix_fmt', 'yuv420p',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '30',
        '-y',  # Overwrite output files
        str(output_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def generate_image_file(output_path: Path, width: int, height: int) -> bool:
    """Generate a JPEG image file using FFmpeg."""
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'testsrc=duration=1:size={width}x{height}',
        '-frames:v', '1',
        '-q:v', '5',  # JPEG quality (2-31, lower is better)
        '-y',  # Overwrite output files
        str(output_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def generate_dataset(output_dir: Path, verbose: bool = True) -> Tuple[int, int]:
    """
    Generate complete test dataset.

    Returns:
        Tuple of (files_created, files_failed)
    """
    if not check_ffmpeg():
        print("ERROR: FFmpeg not found. Please install FFmpeg first.")
        sys.exit(1)

    # Create output directories
    audio_dir = output_dir / 'audio'
    video_dir = output_dir / 'video'
    images_dir = output_dir / 'images'

    for directory in [audio_dir, video_dir, images_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    files_created = 0
    files_failed = 0

    # Generate audio files
    if verbose:
        print("Generating audio files...")

    file_counter = 0
    for sample_rate, duration, frequency, count in AUDIO_CONFIGS:
        for i in range(count):
            output_path = audio_dir / f"audio_{file_counter:04d}_{sample_rate}hz.wav"
            if verbose and file_counter % 50 == 0:
                print(f"  Audio: {file_counter}/700")

            if generate_audio_file(output_path, sample_rate, duration, frequency):
                files_created += 1
            else:
                files_failed += 1
                if verbose:
                    print(f"  FAILED: {output_path}")

            file_counter += 1

    # Generate video files
    if verbose:
        print("Generating video files...")

    file_counter = 0
    for width, height, duration, fps, count in VIDEO_CONFIGS:
        for i in range(count):
            output_path = video_dir / f"video_{file_counter:04d}_{width}x{height}.mp4"
            if verbose and file_counter % 20 == 0:
                print(f"  Video: {file_counter}/200")

            if generate_video_file(output_path, width, height, duration, fps):
                files_created += 1
            else:
                files_failed += 1
                if verbose:
                    print(f"  FAILED: {output_path}")

            file_counter += 1

    # Generate image files
    if verbose:
        print("Generating image files...")

    file_counter = 0
    for width, height, count in IMAGE_CONFIGS:
        for i in range(count):
            output_path = images_dir / f"image_{file_counter:04d}_{width}x{height}.jpg"
            if verbose and file_counter % 10 == 0:
                print(f"  Images: {file_counter}/100")

            if generate_image_file(output_path, width, height):
                files_created += 1
            else:
                files_failed += 1
                if verbose:
                    print(f"  FAILED: {output_path}")

            file_counter += 1

    return files_created, files_failed


def get_dataset_size(output_dir: Path) -> int:
    """Calculate total size of dataset in bytes."""
    total_size = 0
    for file_path in output_dir.rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    return total_size


def main():
    parser = argparse.ArgumentParser(
        description='Generate test dataset for performance benchmarking'
    )
    parser.add_argument(
        'output_dir',
        nargs='?',
        default='tests/fixtures/test_dataset',
        help='Output directory for generated files (default: tests/fixtures/test_dataset)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output'
    )

    args = parser.parse_args()
    output_dir = Path(args.output_dir)

    if not args.quiet:
        print(f"Generating test dataset in: {output_dir}")
        print("This will take 2-5 minutes...")
        print()

    # Generate dataset
    files_created, files_failed = generate_dataset(output_dir, verbose=not args.quiet)

    # Calculate dataset size
    total_size = get_dataset_size(output_dir)
    size_mb = total_size / (1024 * 1024)

    # Print summary
    print()
    print("=" * 60)
    print("DATASET GENERATION COMPLETE")
    print("=" * 60)
    print(f"Files created:  {files_created}")
    print(f"Files failed:   {files_failed}")
    print(f"Total size:     {size_mb:.2f} MB")
    print(f"Output dir:     {output_dir}")
    print()

    # Validate expected count
    expected_count = sum(config[-1] for config in AUDIO_CONFIGS) + \
                    sum(config[-1] for config in VIDEO_CONFIGS) + \
                    sum(config[-1] for config in IMAGE_CONFIGS)

    if files_created == expected_count:
        print(f"SUCCESS: All {expected_count} files generated")
        return 0
    else:
        print(f"WARNING: Expected {expected_count} files, created {files_created}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
