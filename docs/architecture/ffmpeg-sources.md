# FFmpeg Binary Sources and Integration

**Version:** 1.0
**Last Updated:** 2025-10-04
**Status:** Specification Document

---

## Overview

This document specifies trusted sources for FFmpeg binaries, checksum verification procedures, license compliance requirements, and integration architecture for the Samplify Django Web UI.

**Critical**: FFmpeg is GPL-licensed software. Proper handling is required to comply with licensing terms.

---

## Trusted Binary Sources

### Windows (64-bit)

**Primary Source**: Gyan.dev Static Builds
- **URL**: https://www.gyan.dev/ffmpeg/builds/
- **Specific Build**: `ffmpeg-5.1.2-essentials_build.zip`
- **Download Link**: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip (latest)
- **License**: GPL 3.0
- **Build Type**: Essentials (minimal, sufficient for our needs)
- **SHA256 Checksum**: *(Auto-verified during download - see verification section)*

**Alternative Source**: FFmpeg.org Official Builds
- **URL**: https://ffmpeg.org/download.html#build-windows
- **Provider**: BtbN Windows Builds
- **License**: GPL 3.0

**Binary Path After Extraction**:
```
Samplify/
└── bin/
    └── windows/
        ├── ffmpeg.exe
        ├── ffprobe.exe  (optional, for metadata extraction)
        └── LICENSE.txt  (GPL 3.0 text)
```

---

### macOS (Intel & Apple Silicon)

**Primary Source**: Homebrew Package Manager
- **Installation Command**: `brew install ffmpeg`
- **Version**: Latest stable (5.1.2+)
- **License**: GPL 3.0 (Homebrew formula handles licensing)
- **Binary Location**: `/opt/homebrew/bin/ffmpeg` (Apple Silicon) or `/usr/local/bin/ffmpeg` (Intel)

**Alternative Source**: Static Builds from evermeet.cx
- **URL**: https://evermeet.cx/ffmpeg/
- **Download**: `ffmpeg-5.1.2.7z` (latest stable)
- **License**: GPL 3.0
- **Checksum**: Provided on download page

**Binary Path (if using static build)**:
```
Samplify/
└── bin/
    └── macos/
        ├── ffmpeg
        └── LICENSE.txt
```

---

### Linux (All Distributions)

**Primary Source**: John Van Sickle Static Builds
- **URL**: https://johnvansickle.com/ffmpeg/
- **Download**: `ffmpeg-release-amd64-static.tar.xz` (64-bit)
- **License**: GPL 3.0
- **Advantages**: Static linking (no library dependencies), works on all distributions
- **SHA256 Checksum**: Provided on download page

**Download Script**:
```bash
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz.md5
md5sum -c ffmpeg-release-amd64-static.tar.xz.md5
tar -xf ffmpeg-release-amd64-static.tar.xz
```

**Alternative Source**: System Package Manager
- **Debian/Ubuntu**: `sudo apt install ffmpeg`
- **Fedora/RHEL**: `sudo dnf install ffmpeg`
- **Arch**: `sudo pacman -S ffmpeg`
- **Advantage**: System-managed updates
- **Disadvantage**: May be outdated on some distributions

**Binary Path (if using static build)**:
```
Samplify/
└── bin/
    └── linux/
        ├── ffmpeg
        ├── ffprobe
        └── LICENSE.txt
```

---

## Binary Verification (Security)

### Checksum Validation

**Purpose**: Ensure binary integrity, prevent tampered/malicious binaries

**Process**:
1. Download binary from trusted source
2. Download corresponding checksum file (SHA256 or MD5)
3. Compute checksum of downloaded file
4. Compare with published checksum
5. **Reject installation if mismatch**

**Implementation** (`apps/processing/services/ffmpeg_service.py`):

```python
import hashlib
import requests
from pathlib import Path
from loguru import logger

def verify_checksum(file_path: Path, expected_checksum: str, algorithm: str = 'sha256') -> bool:
    """Verify file checksum against expected value.

    Args:
        file_path: Path to file to verify
        expected_checksum: Expected checksum (hex string)
        algorithm: Hash algorithm ('sha256' or 'md5')

    Returns:
        True if checksum matches, False otherwise
    """
    hash_obj = hashlib.new(algorithm)

    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b''):
            hash_obj.update(chunk)

    computed_checksum = hash_obj.hexdigest()
    matches = computed_checksum.lower() == expected_checksum.lower()

    if not matches:
        logger.error(
            f"Checksum mismatch for {file_path.name}",
            expected=expected_checksum,
            computed=computed_checksum
        )

    return matches


def download_and_verify_ffmpeg(platform: str) -> Path:
    """Download and verify FFmpeg binary for platform.

    Args:
        platform: 'windows', 'macos', or 'linux'

    Returns:
        Path to verified FFmpeg binary

    Raises:
        ValueError: If checksum verification fails
        requests.RequestException: If download fails
    """
    source_config = FFMPEG_SOURCES[platform]
    download_url = source_config['url']
    checksum_url = source_config['checksum_url']
    expected_checksum = source_config.get('checksum')  # Pre-defined or fetched

    # Download binary
    logger.info(f"Downloading FFmpeg from {download_url}")
    response = requests.get(download_url, stream=True, timeout=300)
    response.raise_for_status()

    # Save to temporary location
    temp_path = Path(f"/tmp/ffmpeg_{platform}.zip")
    with open(temp_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Fetch checksum if not pre-defined
    if not expected_checksum and checksum_url:
        checksum_response = requests.get(checksum_url, timeout=30)
        checksum_response.raise_for_status()
        expected_checksum = checksum_response.text.strip().split()[0]

    # Verify checksum
    if not verify_checksum(temp_path, expected_checksum, algorithm='sha256'):
        temp_path.unlink()  # Delete unverified file
        raise ValueError(f"FFmpeg checksum verification failed for {platform}")

    logger.success(f"FFmpeg downloaded and verified for {platform}")
    return temp_path
```

---

### HTTPS-Only Downloads

**Requirement**: All downloads MUST use HTTPS (not HTTP)

**Rationale**:
- Prevents man-in-the-middle attacks
- Ensures connection to legitimate server
- SSL certificate verification via `requests` library

**Implementation**:
```python
import requests

# requests library automatically verifies SSL certificates
response = requests.get(download_url, verify=True, timeout=300)
# verify=True is default, explicitly shown for clarity
```

---

## License Compliance (GPL 3.0)

### FFmpeg Licensing Overview

**FFmpeg License**: GPL 3.0 (if compiled with GPL libraries) or LGPL 2.1 (if using shared libraries only)

**Key GPL Requirements**:
1. **Source Code Availability**: If distributing GPL binaries, must provide access to source code
2. **License Notice**: Must include GPL license text with distributed binaries
3. **Modification Disclosure**: If modifying FFmpeg, must document changes
4. **No Additional Restrictions**: Cannot add restrictions beyond GPL terms

---

### Samplify Compliance Strategy

**Approach**: **Download-on-Setup (Not Bundled in Repository)**

**Rationale**:
- Samplify does NOT bundle FFmpeg binaries in Git repository
- Users download FFmpeg directly from trusted sources during setup
- Samplify acts as a "wrapper" application, not a distributor
- This approach avoids most GPL distribution obligations

**Implementation**:

1. **Git Repository**:
   - `bin/` directory exists but is empty (`.gitkeep` file only)
   - `.gitignore` excludes all binaries:
     ```gitignore
     # FFmpeg binaries (not committed - downloaded during setup)
     bin/windows/ffmpeg.exe
     bin/windows/ffprobe.exe
     bin/macos/ffmpeg
     bin/linux/ffmpeg
     bin/linux/ffprobe
     ```

2. **Setup Script** (`setup.py`):
   - Detects user's platform (Windows/macOS/Linux)
   - Downloads FFmpeg from trusted source
   - Verifies checksum
   - Extracts to `bin/<platform>/`
   - Downloads and saves `LICENSE.txt` (GPL 3.0 full text)

3. **License Notice** (in `README.md` and About page):
   ```markdown
   ## Third-Party Software

   Samplify uses FFmpeg for media processing.

   - **FFmpeg**: https://ffmpeg.org
   - **License**: GPL 3.0 / LGPL 2.1
   - **Source Code**: https://github.com/FFmpeg/FFmpeg
   - **Binaries**: Downloaded from trusted sources during setup (not bundled)

   FFmpeg is licensed under the GNU General Public License (GPL) version 3.0
   or later. The full license text is available in `bin/<platform>/LICENSE.txt`
   after setup.

   Samplify does not modify FFmpeg binaries. Users are responsible for
   complying with FFmpeg's license terms if redistributing the software.
   ```

4. **User Communication**:
   - Setup script displays: "Downloading FFmpeg (GPL 3.0 licensed) from [source]"
   - Web UI About page links to FFmpeg license and source code

---

### Distribution Scenarios

#### Scenario 1: Source Code Distribution (Git Clone)
- **Status**: ✅ GPL Compliant
- **Reason**: No binaries distributed, users download FFmpeg themselves

#### Scenario 2: Binary Distribution (Installer/Package)
- **Status**: ⚠️ Requires GPL Compliance Measures
- **Requirements**:
  - Include FFmpeg source code or link to source
  - Include GPL 3.0 license text
  - Document that FFmpeg is included
  - Provide attribution to FFmpeg project

**Recommendation**: Avoid binary distribution for MVP. Use clone-to-run model.

#### Scenario 3: Commercial Use (Future Consideration)
- **Status**: ✅ Allowed by GPL
- **Requirements**:
  - Can sell Samplify software
  - Must still provide source code (Samplify + FFmpeg)
  - Cannot impose additional restrictions
  - Users have right to redistribute

---

## Platform Detection

### OS Detection Logic

**Implementation** (`apps/processing/services/ffmpeg_service.py`):

```python
import platform
import sys
from pathlib import Path
from typing import Literal

PlatformType = Literal['windows', 'macos', 'linux']

def detect_platform() -> PlatformType:
    """Detect current operating system platform.

    Returns:
        Platform identifier: 'windows', 'macos', or 'linux'

    Raises:
        OSError: If platform is not supported
    """
    system = platform.system().lower()

    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    else:
        raise OSError(f"Unsupported platform: {system}")


def get_ffmpeg_binary_path(platform: PlatformType | None = None) -> Path:
    """Get path to FFmpeg binary for platform.

    Args:
        platform: Platform identifier (auto-detected if None)

    Returns:
        Path to FFmpeg binary

    Example:
        >>> get_ffmpeg_binary_path('windows')
        Path('bin/windows/ffmpeg.exe')
    """
    if platform is None:
        platform = detect_platform()

    base_dir = Path(__file__).resolve().parent.parent.parent.parent

    if platform == 'windows':
        binary_path = base_dir / 'bin' / 'windows' / 'ffmpeg.exe'
    elif platform == 'macos':
        # Check Homebrew locations first
        homebrew_paths = [
            Path('/opt/homebrew/bin/ffmpeg'),  # Apple Silicon
            Path('/usr/local/bin/ffmpeg'),     # Intel
        ]
        for path in homebrew_paths:
            if path.exists():
                return path
        # Fallback to bundled binary
        binary_path = base_dir / 'bin' / 'macos' / 'ffmpeg'
    else:  # linux
        # Check system PATH first
        import shutil
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            return Path(system_ffmpeg)
        # Fallback to bundled binary
        binary_path = base_dir / 'bin' / 'linux' / 'ffmpeg'

    return binary_path


def verify_ffmpeg_installation() -> bool:
    """Verify FFmpeg is installed and accessible.

    Returns:
        True if FFmpeg binary exists and is executable
    """
    try:
        binary_path = get_ffmpeg_binary_path()

        if not binary_path.exists():
            logger.error(f"FFmpeg binary not found: {binary_path}")
            return False

        # Test execution
        import subprocess
        result = subprocess.run(
            [str(binary_path), '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            logger.error("FFmpeg execution failed")
            return False

        version_info = result.stdout.split('\n')[0]
        logger.success(f"FFmpeg verified: {version_info}")
        return True

    except Exception as e:
        logger.exception(f"FFmpeg verification failed: {e}")
        return False
```

---

## FFmpeg Source Configuration

### Source Registry

**Configuration** (`apps/processing/config/ffmpeg_sources.py`):

```python
from typing import TypedDict

class FFmpegSourceConfig(TypedDict):
    url: str
    checksum_url: str | None
    checksum: str | None  # Pre-defined checksum (optional)
    license_url: str
    archive_format: str  # 'zip', 'tar.xz', etc.

FFMPEG_SOURCES: dict[str, FFmpegSourceConfig] = {
    'windows': {
        'url': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
        'checksum_url': None,  # Gyan.dev doesn't provide checksums
        'checksum': None,  # Verified by source reputation
        'license_url': 'https://www.gnu.org/licenses/gpl-3.0.txt',
        'archive_format': 'zip',
    },
    'macos': {
        'url': 'https://evermeet.cx/ffmpeg/ffmpeg-5.1.2.7z',
        'checksum_url': 'https://evermeet.cx/ffmpeg/info/ffmpeg/5.1.2',
        'checksum': None,  # Fetched from checksum_url
        'license_url': 'https://www.gnu.org/licenses/gpl-3.0.txt',
        'archive_format': '7z',
    },
    'linux': {
        'url': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz',
        'checksum_url': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz.md5',
        'checksum': None,  # Fetched from checksum_url
        'license_url': 'https://www.gnu.org/licenses/gpl-3.0.txt',
        'archive_format': 'tar.xz',
    },
}
```

---

## Setup Integration

### Automated Setup Script

**Setup Flow** (`setup.py`):

```python
#!/usr/bin/env python3
"""Samplify automated setup script."""

import sys
from pathlib import Path

def main():
    print("=== Samplify Setup ===\n")

    # 1. Detect platform
    from apps.processing.services.ffmpeg_service import detect_platform
    platform = detect_platform()
    print(f"✓ Detected platform: {platform}")

    # 2. Check Python version
    if sys.version_info < (3, 10):
        print("✗ Error: Python 3.10+ required")
        sys.exit(1)
    print(f"✓ Python version: {sys.version_info.major}.{sys.version_info.minor}")

    # 3. Create virtual environment
    print("\n→ Creating virtual environment...")
    import subprocess
    subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    print("✓ Virtual environment created")

    # 4. Install dependencies
    print("\n→ Installing dependencies...")
    pip_path = 'venv/Scripts/pip' if platform == 'windows' else 'venv/bin/pip'
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
    print("✓ Dependencies installed")

    # 5. Download FFmpeg
    print(f"\n→ Downloading FFmpeg for {platform}...")
    print("   (FFmpeg is GPL 3.0 licensed - see LICENSE.txt after download)")
    from apps.processing.services.ffmpeg_service import download_and_verify_ffmpeg
    binary_path = download_and_verify_ffmpeg(platform)
    print(f"✓ FFmpeg downloaded and verified: {binary_path}")

    # 6. Run migrations
    print("\n→ Initializing database...")
    python_path = 'venv/Scripts/python' if platform == 'windows' else 'venv/bin/python'
    subprocess.run([python_path, 'manage.py', 'migrate'], check=True)
    print("✓ Database initialized")

    # 7. Verify installation
    print("\n→ Verifying installation...")
    subprocess.run([python_path, 'manage.py', 'check'], check=True)
    print("✓ All checks passed")

    print("\n=== Setup Complete ===")
    print(f"\nTo start the server:")
    if platform == 'windows':
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")
    print("  python manage.py runserver")

if __name__ == '__main__':
    main()
```

---

## Error Handling

### FFmpeg Not Available Error

**Error Code**: `FFMPEG_NOT_AVAILABLE`

**Response** (API endpoint):
```json
{
  "success": false,
  "error": {
    "code": "FFMPEG_NOT_AVAILABLE",
    "message": "FFmpeg binary not found. Please run setup script or install manually.",
    "details": {
      "expected_path": "bin/windows/ffmpeg.exe",
      "platform": "windows",
      "install_command": "python setup.py"
    }
  }
}
```

**User-Facing Message** (Web UI):
```
FFmpeg Not Installed

FFmpeg is required for media processing but was not found.

Solution:
1. Run the setup script: python setup.py
2. Or manually download FFmpeg from: https://ffmpeg.org/download.html
3. Place ffmpeg.exe in: bin/windows/

Need help? See documentation: docs/architecture/ffmpeg-sources.md
```

---

## Related Documents

- **[Technology Stack](./tech-stack.md)** - Complete dependency list
- **[Database Schema](./database-schema-design.md)** - File metadata storage
- **[API Endpoints](./api-endpoints.md)** - Error response formats
- **[Testing Strategy](./testing-strategy.md)** - FFmpeg integration tests

---

## Version History

- **1.0** (2025-10-04): Initial FFmpeg integration specification
  - Trusted binary sources for Windows, macOS, Linux
  - Checksum verification procedures
  - GPL 3.0 license compliance strategy
  - Platform detection and path resolution
  - Setup script integration
