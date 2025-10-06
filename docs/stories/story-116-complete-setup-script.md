# Story 1.16: Complete Setup Script

## Status
**Approved**

---

## User Story
As a **user**,
I want **a single setup script that configures everything**,
So that **I can clone the repository and run the application without manual steps**.

---

## Story Context
**Existing System Integration:**
- Integrates with: All previous stories (foundation, Django, FFmpeg, database)
- Technology: Python setup script, shell scripts, pip
- Follows pattern: FR15/FR16 clone-to-run deployment
- Touch points: Installation, configuration, validation

---

## Acceptance Criteria

**Functional Requirements:**
1. `setup.py` script checks prerequisites:
   - Python 3.10+ installed
   - Git installed
   - Disk space (500 MB minimum for FFmpeg)
2. Script creates virtual environment (if not exists)
3. Script installs requirements from `requirements.txt`
4. Script runs FFmpeg detection/download (Story 1.4)
5. Script runs Django migrations (`manage.py migrate`)
6. Script runs health check:
   - Database accessible (WAL mode verified)
   - FFmpeg binary works
   - Static files collectible
   - Loguru configured correctly
7. Script reports success/failure with actionable messages
8. Script creates `.env` file from `.env.template` (if exists)

**Integration Requirements:**
9. Integrates with all infrastructure stories (1.0-1.4)
10. Uses FFmpeg service (Story 1.4)
11. Runs Django migrations (Story 1.2)
12. Validates all configurations (NFR5)

**Quality Requirements:**
13. Setup completes in <5 minutes on fresh system
14. Error messages are clear and actionable (FR16)
15. Script is idempotent (safe to run multiple times)
16. Cross-platform support (Windows/macOS/Linux)

---

## Tasks / Subtasks

- [ ] **Task 1: Create main setup script** (AC: 1, 2, 3, 15, 16)
  - [ ] Create `setup.py` script at project root
  - [ ] Check Python version (3.10+)
  - [ ] Check git installed
  - [ ] Check disk space (500 MB minimum)
  - [ ] Create virtual environment if not exists
  - [ ] Install requirements from `requirements.txt`
  - [ ] Make script idempotent (safe to re-run)
  - [ ] Cross-platform compatibility (Windows/macOS/Linux)

- [ ] **Task 2: Integrate FFmpeg detection/download** (AC: 4, 10)
  - [ ] Call FFmpeg detection service (Story 1.4)
  - [ ] Download FFmpeg if not found
  - [ ] Verify FFmpeg binary works

- [ ] **Task 3: Run Django migrations** (AC: 5, 11)
  - [ ] Run `manage.py migrate`
  - [ ] Handle migration errors gracefully
  - [ ] Verify database created successfully

- [ ] **Task 4: Implement health check** (AC: 6, 12)
  - [ ] Check database accessible (SQLite file exists)
  - [ ] Verify WAL mode enabled (Story 1.2C)
  - [ ] Test FFmpeg binary execution
  - [ ] Check static files directory
  - [ ] Verify loguru configuration (Story 1.3)

- [ ] **Task 5: Create .env file** (AC: 8)
  - [ ] Check if `.env.template` exists
  - [ ] Copy to `.env` if not exists
  - [ ] Prompt user for configuration values (optional)

- [ ] **Task 6: Add error handling and reporting** (AC: 7, 14)
  - [ ] Clear, actionable error messages
  - [ ] Color-coded output (green=success, red=error)
  - [ ] Suggest fixes for common errors
  - [ ] Log all steps for debugging

- [ ] **Task 7: Add performance optimizations** (AC: 13)
  - [ ] Parallel installation where possible
  - [ ] Cache downloaded files (FFmpeg)
  - [ ] Skip completed steps on re-run

- [ ] **Task 8: Testing** (AC: 13, 14, 15, 16)
  - [ ] Test on fresh Windows VM
  - [ ] Test on fresh macOS VM
  - [ ] Test on fresh Linux VM
  - [ ] Test idempotency (run twice)
  - [ ] Test error handling (missing prerequisites)

---

## Dev Notes

### Previous Story Insights
**From Story 1.4 (FFmpeg Detection & Download Service):**
- FFmpeg detection at `samplify/utils/ffmpeg.py` [Source: Story 1.4 Dev Agent Record]
- Download function: `download_ffmpeg()`
- Detection function: `get_ffmpeg_binary_path()`

**From Story 1.2C (WAL Configuration):**
- WAL mode configuration in database settings [Source: Story 1.2C]
- Verification: Check PRAGMA journal_mode

### File Locations (Source Tree)
**Setup Script Location:** [Source: architecture/source-tree.md]
```
project_root/
├── setup.py                     # Create this file
├── requirements.txt             # Existing
├── .env.template               # Create this file (optional)
└── manage.py                    # Existing
```

**Test Location:**
```
tests/
└── test_setup.py                # Create this file
```

### Implementation Patterns

**Main Setup Script:**
```python
#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check Python 3.10+ installed."""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required. Current:", sys.version)
        sys.exit(1)
    print("✓ Python version:", sys.version)

def check_git_installed():
    """Check git installed."""
    if not shutil.which('git'):
        print("❌ Git not found. Install from: https://git-scm.com/")
        sys.exit(1)
    print("✓ Git installed")

def check_disk_space():
    """Check 500 MB disk space available."""
    stat = shutil.disk_usage('.')
    free_mb = stat.free / (1024 * 1024)
    if free_mb < 500:
        print(f"❌ Insufficient disk space. Need 500 MB, have {free_mb:.0f} MB")
        sys.exit(1)
    print(f"✓ Disk space: {free_mb:.0f} MB available")

def create_virtualenv():
    """Create virtual environment if not exists."""
    venv_path = Path('venv')
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return

    print("Creating virtual environment...")
    subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    print("✓ Virtual environment created")

def install_requirements():
    """Install requirements from requirements.txt."""
    python_exe = Path('venv/bin/python') if os.name != 'nt' else Path('venv/Scripts/python.exe')

    print("Installing requirements...")
    subprocess.run([str(python_exe), '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    print("✓ Requirements installed")

def setup_ffmpeg():
    """Setup FFmpeg using Story 1.4 service."""
    python_exe = Path('venv/bin/python') if os.name != 'nt' else Path('venv/Scripts/python.exe')

    print("Setting up FFmpeg...")
    result = subprocess.run(
        [str(python_exe), 'manage.py', 'setup_ffmpeg'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ FFmpeg setup failed: {result.stderr}")
        sys.exit(1)

    print("✓ FFmpeg configured")

def run_migrations():
    """Run Django migrations."""
    python_exe = Path('venv/bin/python') if os.name != 'nt' else Path('venv/Scripts/python.exe')

    print("Running database migrations...")
    subprocess.run([str(python_exe), 'manage.py', 'migrate'], check=True)
    print("✓ Database migrations complete")

def create_env_file():
    """Create .env from .env.template if exists."""
    template_path = Path('.env.template')
    env_path = Path('.env')

    if not template_path.exists():
        return

    if env_path.exists():
        print("✓ .env file already exists")
        return

    shutil.copy(template_path, env_path)
    print("✓ Created .env file from template")

def health_check():
    """Run system health checks."""
    print("\nRunning health checks...")

    # Check database
    db_path = Path('db.sqlite3')
    if not db_path.exists():
        print("❌ Database not found")
        sys.exit(1)
    print("✓ Database accessible")

    # Check FFmpeg
    from samplify.utils.ffmpeg import get_ffmpeg_binary_path
    ffmpeg_path = get_ffmpeg_binary_path()
    if not ffmpeg_path:
        print("❌ FFmpeg not configured")
        sys.exit(1)
    print(f"✓ FFmpeg binary: {ffmpeg_path}")

    # Check static files
    static_path = Path('static')
    static_path.mkdir(exist_ok=True)
    print("✓ Static files directory ready")

    print("\n✅ Setup complete! Run: python manage.py runserver")

def main():
    print("=== Samplify Setup ===\n")

    try:
        check_python_version()
        check_git_installed()
        check_disk_space()
        create_virtualenv()
        install_requirements()
        create_env_file()
        setup_ffmpeg()
        run_migrations()
        health_check()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Cross-Platform Helpers:**
```python
import platform

def get_python_executable():
    """Get platform-specific Python executable path."""
    if platform.system() == 'Windows':
        return Path('venv/Scripts/python.exe')
    else:
        return Path('venv/bin/python')

def get_pip_executable():
    """Get platform-specific pip executable path."""
    if platform.system() == 'Windows':
        return Path('venv/Scripts/pip.exe')
    else:
        return Path('venv/bin/pip')
```

**Error Messages (FR16):**
```python
ERROR_MESSAGES = {
    'python_version': """
❌ Python 3.10+ required

Current version: {current_version}

To fix:
- Windows: Download from https://www.python.org/downloads/
- macOS: brew install python@3.10
- Linux: sudo apt install python3.10
""",

    'git_not_found': """
❌ Git not installed

To fix:
- Windows: Download from https://git-scm.com/
- macOS: brew install git
- Linux: sudo apt install git
""",

    'disk_space': """
❌ Insufficient disk space

Required: 500 MB
Available: {available_mb} MB

To fix:
- Free up disk space
- Use different installation directory
"""
}
```

### Preservation Rules
**FR15/FR16 Compliance:** Clone-to-run deployment [Source: requirements.md FR15, FR16]
- Single command setup: `python setup.py`
- Clear error messages with fix instructions
- No manual configuration required

**NFR6 Compliance:** Cross-platform [Source: requirements.md NFR6]
- Works on Windows/macOS/Linux
- Platform-specific paths handled correctly
- Use pathlib.Path for all paths

---

## Dev Notes > Testing

### Test File Location
```
tests/
└── test_setup.py
```

### Testing Standards
**Framework:** pytest

**Test Coverage Target:** 80%+

**Test Categories:**
1. **Unit Tests - Prerequisite Checks**
   - Test Python version check
   - Test git detection
   - Test disk space check

2. **Integration Tests - Full Setup**
   - Test complete setup on fresh VM
   - Test idempotency (run twice)
   - Test error handling (missing prerequisites)

3. **Cross-Platform Tests**
   - Test on Windows (fresh VM)
   - Test on macOS (fresh VM)
   - Test on Linux (fresh VM, Ubuntu 20.04+)

4. **Performance Tests**
   - Test setup completes <5 minutes
   - Test cached setup (re-run) <1 minute

**Example Test:**
```python
import pytest
import subprocess
from pathlib import Path

class SetupTest:
    def test_python_version_check(self):
        """Test Python version check."""
        import sys
        from setup import check_python_version

        if sys.version_info >= (3, 10):
            check_python_version()  # Should not raise
        else:
            with pytest.raises(SystemExit):
                check_python_version()

    def test_idempotent_setup(self, tmp_path):
        """Test setup can be run multiple times."""
        # First run
        result1 = subprocess.run(['python', 'setup.py'], cwd=tmp_path, capture_output=True)
        assert result1.returncode == 0

        # Second run (should succeed, skip completed steps)
        result2 = subprocess.run(['python', 'setup.py'], cwd=tmp_path, capture_output=True)
        assert result2.returncode == 0

    def test_setup_performance(self):
        """Test setup completes <5 minutes."""
        import time
        start = time.time()

        subprocess.run(['python', 'setup.py'], check=True)

        elapsed = time.time() - start
        assert elapsed < 300  # 5 minutes
```

**Running Tests:**
```bash
# Run setup tests
pytest tests/test_setup.py -v

# Test on fresh VMs (manual)
# Windows: vagrant up windows && vagrant ssh windows -c "python setup.py"
# macOS: vagrant up macos && vagrant ssh macos -c "python setup.py"
# Linux: vagrant up ubuntu && vagrant ssh ubuntu -c "python setup.py"
```

---

## Definition of Done
- [ ] Setup script implemented
- [ ] All checks and tasks functional
- [ ] Health check validated
- [ ] Error messages tested
- [ ] Cross-platform tested (Windows/macOS/Linux)
- [ ] Documentation updated with setup instructions

---

## Risk Assessment
- **Primary Risk:** Setup script fails on specific platforms
- **Mitigation:** Test on clean VMs (Windows/macOS/Linux), provide manual fallback
- **Rollback:** Manual installation instructions

---

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-05 | 1.0 | Story completed by Scrum Master - added Status, Tasks, Dev Notes, Testing sections | SM (Bob) |

---

## Dev Agent Record

### Agent Model Used
(To be populated by dev agent during implementation)

### Debug Log References
(To be populated by dev agent during implementation)

### Completion Notes
(To be populated by dev agent during implementation)

### File List
(To be populated by dev agent during implementation)

---

## QA Results
(To be populated by QA agent after implementation)
