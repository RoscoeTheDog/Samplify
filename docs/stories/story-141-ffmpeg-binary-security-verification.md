# Story 1.4.1: FFmpeg Binary Security Verification

## Status
**Draft** - Awaiting implementation (BLOCKER for production)

---

## User Story
As a **system administrator**,
I want **FFmpeg binary downloads verified with SHA256 checksums**,
So that **I can trust the integrity of downloaded binaries and prevent malicious code execution**.

---

## Story Context
**Existing System Integration:**
- Integrates with: Story 1.4 (FFmpeg Detection & Download Service)
- Technology: Python hashlib, urllib/requests for downloads
- Follows pattern: Security best practices for external binary verification
- Touch points: `samplify/utils/ffmpeg.py` download logic

**Security Issue:**
- Story 1.4 downloads FFmpeg binaries from external URLs without verification
- **Risk:** Man-in-the-middle attacks, malicious binary injection, compromised download servers
- **PO Decision:** BLOCKER - must be resolved before production deployment

---

## Acceptance Criteria

**Security Requirements:**
1. SHA256 checksums documented for each platform/version combination:
   - Windows: ffmpeg-release-essentials.zip from gyan.dev
   - macOS: ffmpeg-<version>.zip from evermeet.cx
   - Linux: ffmpeg-release-amd64-static.tar.xz from johnvansickle.com
2. Checksum verification implemented before binary extraction
3. Download process fails with clear error if checksum mismatch detected
4. Checksums stored in configuration file (not hardcoded)
5. Checksum verification logged for audit trail

**Functional Requirements:**
6. Verification integrates seamlessly with Story 1.4 download logic
7. Manual installation instructions updated with checksum verification steps
8. Checksum configuration updatable without code changes
9. Fallback: Allow admin override for checksum verification (with warning)

**Quality Requirements:**
10. Verification completes within 5 seconds (minimal overhead)
11. Clear error messages guide user on checksum failure
12. Verification logic covered by unit tests
13. Documentation updated with security verification details

---

## Tasks / Subtasks

- [ ] **Task 1: Research and document FFmpeg checksums** (AC: 1)
  - [ ] Download current FFmpeg binaries from all three sources
  - [ ] Calculate SHA256 checksums for each platform
  - [ ] Document checksums in `docs/ffmpeg-checksums.md`
  - [ ] Verify checksums against official sources (if available)

- [ ] **Task 2: Create checksum configuration file** (AC: 4, 8)
  - [ ] Create `samplify/config/ffmpeg-checksums.json` with format:
    ```json
    {
      "windows": {
        "url": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        "sha256": "...",
        "version": "..."
      },
      "macos": { ... },
      "linux": { ... }
    }
    ```
  - [ ] Add configuration loading logic to `samplify/utils/ffmpeg.py`
  - [ ] Add validation for config file format

- [ ] **Task 3: Implement SHA256 verification** (AC: 2, 5, 10)
  - [ ] Add `verify_checksum()` function to `samplify/utils/ffmpeg.py`:
    ```python
    def verify_checksum(file_path: Path, expected_sha256: str) -> bool:
        """Verify file SHA256 checksum."""
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        calculated = sha256_hash.hexdigest()
        logger.info(f"Checksum verification: {calculated} vs {expected_sha256}")
        return calculated == expected_sha256
    ```
  - [ ] Integrate verification into download workflow (after download, before extract)
  - [ ] Log verification results to audit trail

- [ ] **Task 4: Add checksum failure handling** (AC: 3, 11)
  - [ ] Raise clear exception on checksum mismatch
  - [ ] Delete downloaded file if checksum fails
  - [ ] Provide actionable error message with:
    - Expected checksum
    - Calculated checksum
    - Instructions for manual verification
    - Link to official FFmpeg checksums (if available)

- [ ] **Task 5: Add admin override option** (AC: 9)
  - [ ] Add `--skip-checksum-verify` flag to download logic
  - [ ] Log WARNING if checksum verification skipped
  - [ ] Document override in manual installation instructions
  - [ ] Require explicit admin confirmation for override

- [ ] **Task 6: Update Story 1.4 integration** (AC: 6, 13)
  - [ ] Modify `samplify/utils/ffmpeg.py` download functions
  - [ ] Ensure backward compatibility (don't break existing calls)
  - [ ] Update Story 1.4 documentation with verification details
  - [ ] Update manual installation instructions

- [ ] **Task 7: Testing** (AC: 12)
  - [ ] Unit test: `verify_checksum()` with known file
  - [ ] Integration test: Download with valid checksum (passes)
  - [ ] Integration test: Download with invalid checksum (fails)
  - [ ] Test config file loading and validation
  - [ ] Test admin override flag
  - [ ] Performance test: Verification completes <5 seconds

---

## Dev Notes

### Previous Story Context
**From Story 1.4 (FFmpeg Detection & Download Service):**
- FFmpeg download implemented in `samplify/utils/ffmpeg.py`
- Platform detection: Windows/macOS/Linux
- Download URLs:
  - Windows: `https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip`
  - macOS: `https://evermeet.cx/ffmpeg/ffmpeg-<version>.zip`
  - Linux: `https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz`
- Binary extraction to `/bin/<platform>/`
- .gitignore excludes `/bin/` directory

### File Locations
**Configuration File:** (Create new)
```
samplify/
└── config/
    └── ffmpeg-checksums.json
```

**Existing File to Modify:**
```
samplify/
└── utils/
    └── ffmpeg.py  # Add verification logic here
```

**Documentation:**
```
docs/
└── ffmpeg-checksums.md  # Create: Document checksums and verification
```

**Test Location:**
```
tests/
└── test_ffmpeg_security.py  # Create: Checksum verification tests
```

### Security Best Practices

**SHA256 Checksum Verification Pattern:**
```python
import hashlib
from pathlib import Path
from loguru import logger

def verify_checksum(file_path: Path, expected_sha256: str) -> bool:
    """
    Verify file integrity using SHA256 checksum.

    Args:
        file_path: Path to file to verify
        expected_sha256: Expected SHA256 hash (hex string)

    Returns:
        True if checksum matches, False otherwise

    Example:
        >>> verify_checksum(Path("ffmpeg.zip"), "abc123...")
        True
    """
    sha256_hash = hashlib.sha256()

    # Read file in chunks to handle large files efficiently
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    calculated = sha256_hash.hexdigest()
    matches = calculated == expected_sha256

    logger.info(
        f"Checksum verification for {file_path.name}: "
        f"{'PASS' if matches else 'FAIL'}"
    )

    if not matches:
        logger.error(
            f"Checksum mismatch!\n"
            f"  Expected: {expected_sha256}\n"
            f"  Calculated: {calculated}"
        )

    return matches
```

**Integration into Download Workflow:**
```python
def download_and_verify_ffmpeg(platform: str) -> Path:
    """Download FFmpeg binary with checksum verification."""
    # Load checksum config
    config = load_checksum_config()
    platform_config = config[platform]

    # Download binary
    download_path = download_file(platform_config['url'])

    # Verify checksum BEFORE extraction
    if not verify_checksum(download_path, platform_config['sha256']):
        download_path.unlink()  # Delete potentially compromised file
        raise SecurityError(
            f"FFmpeg checksum verification failed for {platform}. "
            f"Downloaded file has been deleted for security. "
            f"Please check your network connection and try again."
        )

    # Extract binary (only if checksum valid)
    extract_path = extract_archive(download_path)
    return extract_path
```

### Checksum Configuration Format
**File:** `samplify/config/ffmpeg-checksums.json`
```json
{
  "windows": {
    "url": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
    "version": "6.0",
    "sha256": "TO_BE_CALCULATED_DURING_TASK_1",
    "updated": "2025-10-06"
  },
  "macos": {
    "url": "https://evermeet.cx/ffmpeg/ffmpeg-6.0.zip",
    "version": "6.0",
    "sha256": "TO_BE_CALCULATED_DURING_TASK_1",
    "updated": "2025-10-06"
  },
  "linux": {
    "url": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
    "version": "6.0",
    "sha256": "TO_BE_CALCULATED_DURING_TASK_1",
    "updated": "2025-10-06"
  }
}
```

**Note:** Checksums must be verified against official FFmpeg sources where available. For third-party distribution sites (gyan.dev, evermeet.cx, johnvansickle.com), checksums should be recalculated manually from known-good downloads.

### Error Handling

**Checksum Failure Error Message:**
```
ERROR: FFmpeg binary checksum verification FAILED!

  Platform: Windows
  Downloaded from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

  Expected SHA256:   abc123def456... (from config)
  Calculated SHA256: xyz789uvw012... (from download)

  SECURITY WARNING: Downloaded file may be compromised or corrupted.
  The file has been deleted for your protection.

  Recommended actions:
  1. Check your network connection for man-in-the-middle attacks
  2. Verify the download URL is correct
  3. Try downloading again
  4. If problem persists, manually download and verify FFmpeg:
     - Download from: https://ffmpeg.org/download.html
     - Place in: /bin/windows/ffmpeg.exe
     - Run: python manage.py verify_ffmpeg

  To skip verification (NOT RECOMMENDED):
     python manage.py setup_ffmpeg --skip-checksum-verify
```

### Admin Override Implementation
```python
def download_ffmpeg(skip_checksum_verify: bool = False) -> Path:
    """Download FFmpeg with optional checksum verification."""
    download_path = download_file(url)

    if skip_checksum_verify:
        logger.warning(
            "⚠️  SECURITY WARNING: Checksum verification SKIPPED!\n"
            "   This is NOT RECOMMENDED in production environments.\n"
            "   Downloaded binary integrity cannot be guaranteed."
        )
    else:
        if not verify_checksum(download_path, expected_sha256):
            download_path.unlink()
            raise SecurityError("Checksum verification failed")

    return extract_archive(download_path)
```

---

## Dev Notes > Testing

### Test File Location
```
tests/
└── test_ffmpeg_security.py  # Create this file
```

### Testing Standards
**Framework:** pytest + pytest-django

**Test Coverage Target:** 95%+ for security verification logic

**Test Categories:**
1. **Unit Tests - Checksum Verification**
   - Test `verify_checksum()` with known file/hash
   - Test checksum calculation accuracy
   - Test invalid checksum detection

2. **Integration Tests - Download Workflow**
   - Test download with valid checksum (passes)
   - Test download with invalid checksum (fails and deletes file)
   - Test download with missing checksum config (fails)

3. **Security Tests**
   - Test compromised download detection (mock checksum mismatch)
   - Test file deletion on verification failure
   - Test audit logging of verification results

4. **Performance Tests**
   - Benchmark: Checksum verification <5 seconds for 100MB file
   - Test memory efficiency with large files (chunk reading)

**Example Test:**
```python
import pytest
import hashlib
from pathlib import Path
from samplify.utils.ffmpeg import verify_checksum

class TestFFmpegSecurity:
    def test_valid_checksum_passes(self, tmp_path):
        """Test checksum verification passes with valid hash."""
        # Create test file
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"test content")

        # Calculate expected checksum
        expected = hashlib.sha256(b"test content").hexdigest()

        # Verify
        assert verify_checksum(test_file, expected) is True

    def test_invalid_checksum_fails(self, tmp_path):
        """Test checksum verification fails with invalid hash."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"test content")

        # Use wrong checksum
        wrong_hash = "0" * 64

        # Verify
        assert verify_checksum(test_file, wrong_hash) is False

    def test_download_deletes_file_on_checksum_failure(self, tmp_path, mocker):
        """Test compromised download is deleted."""
        from samplify.utils.ffmpeg import download_and_verify_ffmpeg

        # Mock download to return file with wrong checksum
        mocker.patch('samplify.utils.ffmpeg.download_file',
                     return_value=tmp_path / "ffmpeg.zip")
        mocker.patch('samplify.utils.ffmpeg.verify_checksum',
                     return_value=False)

        # Attempt download
        with pytest.raises(SecurityError, match="checksum verification failed"):
            download_and_verify_ffmpeg("windows")

        # Verify file was deleted
        assert not (tmp_path / "ffmpeg.zip").exists()
```

**Running Tests:**
```bash
# Run all security tests
pytest tests/test_ffmpeg_security.py -v

# Run with coverage
pytest tests/test_ffmpeg_security.py --cov=samplify.utils.ffmpeg --cov-report=html

# Run performance benchmark
pytest tests/test_ffmpeg_security.py::test_checksum_performance -v
```

---

## Definition of Done
- [ ] SHA256 checksums documented for all platforms
- [ ] Checksum configuration file created
- [ ] Verification logic implemented and integrated
- [ ] Checksum failure handling tested
- [ ] Admin override option implemented with warnings
- [ ] Story 1.4 updated with security verification
- [ ] Unit and integration tests passing (95%+ coverage)
- [ ] Performance validated (<5 second verification)
- [ ] Documentation updated with security details
- [ ] **Coding Standards**: All code adheres to CS1-CS13 (see coding-standards.md)
- [ ] **Code Quality**: Black, Pylint (≥8.5), mypy, isort pass without errors
- [ ] **Documentation**: All functions have Google-style docstrings with type hints
- [ ] **Security Review**: Code reviewed for security best practices
- [ ] **QA Validation**: QA agent confirms security verification works

---

## Risk Assessment
- **Primary Risk:** Checksums become outdated when FFmpeg releases new versions
- **Mitigation:** Document checksum update process, add version tracking to config
- **Rollback:** Remove verification (NOT RECOMMENDED), require manual FFmpeg installation

---

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Story created by PO - security verification for FFmpeg downloads (BLOCKER) | PO (Sarah) |

---

## Dev Agent Record
(To be populated by development agent during implementation)

---

## QA Results
(To be populated by QA agent after implementation)
