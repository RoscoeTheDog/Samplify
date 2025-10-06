# Story 1.17: Integration Testing & Validation

## Status
**Approved**

---

## User Story
As a **QA engineer**,
I want **comprehensive integration tests validating algorithm preservation and performance**,
So that **I can ensure the Django migration meets all requirements**.

---

## Story Context
**Existing System Integration:**
- Integrates with: All stories (end-to-end validation)
- Technology: pytest, Django TestCase, performance benchmarking
- Follows pattern: CR1/CR2 validation, NFR requirements
- Touch points: All components

---

## Acceptance Criteria

**Functional Requirements:**
1. Algorithm preservation tests (CR1):
   - Side-by-side comparison: original vs Django search/filter/dispatch
   - Test with sample files from existing system
   - Validate 100% identical output
2. Multiprocessing performance tests (CR2/NFR1):
   - Benchmark CPU utilization (50-70% target)
   - Validate worker pool scaling (one per CPU core)
   - Compare performance with original script
3. Compatibility tests (CR3/CR4):
   - ORM migration validated (SQLAlchemy → Django)
   - XML template import validated (all rule types)
4. FFmpeg integration tests (FR7/CR6):
   - Binary detection on all platforms
   - Media processing success rate (95%+ for common formats, NFR9)
5. Concurrent access tests (NFR2):
   - WAL mode validation
   - Multiprocessing + Django server simultaneous operation
6. UI integration tests:
   - Schema CRUD operations
   - Batch processing workflow
   - Watchdog controls
7. Setup script validation (FR15/FR16):
   - Clone-to-run on fresh systems

**Integration Requirements:**
8. Test suite covers all stories (1.0-1.16)
9. Tests run in CI/CD pipeline (if configured)
10. Tests validate against requirements (FR, NFR, CR, DW)
11. Performance benchmarks documented

**Quality Requirements:**
12. Test coverage >80% (critical paths 100%)
13. All tests pass on Windows/macOS/Linux
14. Performance benchmarks meet NFR requirements
15. Test reports are detailed and actionable

---

## Tasks / Subtasks

- [ ] **Task 1: Create algorithm preservation test suite (CR1)** (AC: 1)
  - [ ] Create `tests/integration/test_algorithm_preservation.py`
  - [ ] Port brownfield test files to test data directory
  - [ ] Implement side-by-side comparison (original vs Django)
  - [ ] Test contains_expression() algorithm
  - [ ] Test contains_extensions() algorithm
  - [ ] Test contains_audio/video() algorithms
  - [ ] Test dispatch logic (routing decisions)
  - [ ] Validate 100% identical output

- [ ] **Task 2: Create multiprocessing performance test suite (CR2/NFR1)** (AC: 2)
  - [ ] Create `tests/integration/test_performance.py`
  - [ ] Benchmark CPU utilization during batch processing
  - [ ] Validate worker pool scaling (one per CPU core)
  - [ ] Compare performance with original script
  - [ ] Test 50-70% CPU utilization target (NFR1)

- [ ] **Task 3: Create compatibility test suite (CR3/CR4)** (AC: 3)
  - [ ] Test SQLAlchemy → Django ORM migration
  - [ ] Test XML template import (all rule types)
  - [ ] Validate SchemaRule model compatibility
  - [ ] Validate SchemaTransformation model compatibility

- [ ] **Task 4: Create FFmpeg integration test suite (FR7/CR6)** (AC: 4)
  - [ ] Test FFmpeg binary detection on all platforms
  - [ ] Test media processing (WAV, MP3, FLAC, etc.)
  - [ ] Validate 95%+ success rate for common formats (NFR9)
  - [ ] Test error handling for unsupported formats

- [ ] **Task 5: Create concurrent access test suite (NFR2)** (AC: 5)
  - [ ] Test WAL mode enabled (PRAGMA journal_mode)
  - [ ] Test multiprocessing + Django server simultaneously
  - [ ] Test database locking behavior
  - [ ] Validate no corruption under load

- [ ] **Task 6: Create UI integration test suite** (AC: 6)
  - [ ] Test Schema CRUD operations (Story 1.10)
  - [ ] Test batch processing workflow (Story 1.6)
  - [ ] Test watchdog controls (Story 1.13)
  - [ ] Test directory management (Story 1.11)
  - [ ] Test properties panel (Story 1.12)

- [ ] **Task 7: Create setup script validation test** (AC: 7)
  - [ ] Test clone-to-run on fresh Windows VM
  - [ ] Test clone-to-run on fresh macOS VM
  - [ ] Test clone-to-run on fresh Linux VM
  - [ ] Validate setup completes <5 minutes

- [ ] **Task 8: Document performance benchmarks** (AC: 11, 14, 15)
  - [ ] Create `docs/testing/performance-benchmarks.md`
  - [ ] Document CPU utilization results
  - [ ] Document processing speed (files/minute)
  - [ ] Compare with original script
  - [ ] Document NFR compliance

- [ ] **Task 9: Create test reports** (AC: 15)
  - [ ] Generate HTML coverage reports
  - [ ] Generate pytest reports with details
  - [ ] Create summary dashboard
  - [ ] Document test failures with fix recommendations

---

## Dev Notes

### Previous Story Insights
**From Story 1.5 (File Scanning Service):**
- Algorithm preservation critical (CR1) [Source: Story 1.5 Dev Notes]
- Side-by-side testing pattern established
- Brownfield files at `handlers/rules.py`

**From Story 1.6 (Batch Processing):**
- Multiprocessing implementation (CR2) [Source: Story 1.6 Dev Notes]
- CPU utilization target: 50-70%

### File Locations (Source Tree)
**Test Suite Location:** [Source: architecture/source-tree.md]
```
tests/
├── integration/
│   ├── test_algorithm_preservation.py    # Create this file
│   ├── test_performance.py               # Create this file
│   ├── test_compatibility.py             # Create this file
│   ├── test_ffmpeg_integration.py        # Create this file
│   ├── test_concurrent_access.py         # Create this file
│   ├── test_ui_integration.py            # Create this file
│   └── test_setup_validation.py          # Create this file
└── test_data/
    └── brownfield_samples/               # Port brownfield test files
```

**Documentation Location:**
```
docs/
└── testing/
    ├── performance-benchmarks.md         # Create this file
    └── test-reports/                     # Generated reports
```

### Data Models
**Test Data Structure:**
```
tests/test_data/
├── brownfield_samples/
│   ├── audio/
│   │   ├── kick_01_44k_24bit.wav
│   │   ├── snare_01_48k_16bit.wav
│   └── video/
│       ├── interview_01_1080p.mp4
└── expected_outputs/
    ├── routing_decisions.json
    └── transformation_results.json
```

### Implementation Patterns

**Algorithm Preservation Test (CR1):**
```python
import pytest
from handlers.rules import contains_expression  # Brownfield
from samplify.utils.search import contains_expression as django_contains_expression  # Django

class TestAlgorithmPreservation:
    def test_contains_expression_identical(self):
        """Test contains_expression() produces identical results."""
        test_files = [
            'kick_01.wav',
            'snare_heavy.wav',
            'hihat_closed.wav'
        ]

        pattern = 'kick'

        for file in test_files:
            brownfield_result = contains_expression(file, pattern)
            django_result = django_contains_expression(file, pattern)

            assert brownfield_result == django_result, \
                f"Algorithm deviation for {file}: {brownfield_result} != {django_result}"

    def test_dispatch_logic_identical(self):
        """Test file routing decisions identical to brownfield."""
        import json

        # Load expected outputs from brownfield
        with open('tests/test_data/expected_outputs/routing_decisions.json') as f:
            expected = json.load(f)

        # Run Django implementation
        from samplify.management.commands.scan_input import Command
        cmd = Command()
        actual = cmd.dispatch_files()

        # Compare
        assert actual == expected, "Dispatch logic deviation detected"
```

**Multiprocessing Performance Test (CR2/NFR1):**
```python
import pytest
import psutil
import multiprocessing
from django.test import TestCase

class TestMultiprocessingPerformance(TestCase):
    def test_cpu_utilization_50_70_percent(self):
        """Test batch processing uses 50-70% CPU (NFR1)."""
        from samplify.management.commands.batch_process import Command

        # Start monitoring CPU
        cpu_samples = []

        def monitor_cpu():
            for _ in range(10):  # Sample 10 times
                cpu_samples.append(psutil.cpu_percent(interval=1))

        import threading
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()

        # Run batch processing
        cmd = Command()
        cmd.handle()

        monitor_thread.join()

        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        assert 50 <= avg_cpu <= 70, f"CPU utilization {avg_cpu}% not in target range 50-70%"

    def test_worker_pool_scaling(self):
        """Test worker pool scales to CPU cores (CR2)."""
        from samplify.utils.process_handler import get_worker_count

        expected_workers = multiprocessing.cpu_count()
        actual_workers = get_worker_count()

        assert actual_workers == expected_workers, \
            f"Worker count {actual_workers} != CPU cores {expected_workers}"

    def test_performance_vs_brownfield(self):
        """Compare processing speed with original script."""
        # Benchmark brownfield
        import time
        start = time.time()
        # Run brownfield script on 1000 files
        brownfield_time = time.time() - start

        # Benchmark Django
        start = time.time()
        from samplify.management.commands.batch_process import Command
        cmd = Command()
        cmd.handle()
        django_time = time.time() - start

        # Django should be within 10% of brownfield performance
        assert django_time <= brownfield_time * 1.1, \
            f"Django slower than brownfield: {django_time}s vs {brownfield_time}s"
```

**WAL Mode Concurrent Access Test (NFR2):**
```python
import pytest
from django.test import TestCase
from django.db import connection

class TestConcurrentAccess(TestCase):
    def test_wal_mode_enabled(self):
        """Test WAL mode enabled (NFR2)."""
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode;")
            mode = cursor.fetchone()[0]

        assert mode.upper() == 'WAL', f"WAL mode not enabled: {mode}"

    def test_multiprocessing_and_django_server(self):
        """Test multiprocessing + Django server simultaneously."""
        import subprocess
        import requests

        # Start Django server
        server = subprocess.Popen(['python', 'manage.py', 'runserver', '8001'])

        # Start batch processing (multiprocessing)
        batch = subprocess.Popen(['python', 'manage.py', 'batch_process'])

        # Make requests to Django server
        for _ in range(10):
            response = requests.get('http://localhost:8001/api/processing/status/')
            assert response.status_code == 200

        # Clean up
        server.terminate()
        batch.terminate()
```

**FFmpeg Integration Test (FR7/CR6):**
```python
import pytest
from django.test import TestCase
from samplify.utils.ffmpeg import get_ffmpeg_binary_path, extract_metadata

class TestFFmpegIntegration(TestCase):
    def test_ffmpeg_detection_all_platforms(self):
        """Test FFmpeg binary detected on all platforms."""
        ffmpeg_path = get_ffmpeg_binary_path()

        assert ffmpeg_path is not None, "FFmpeg not detected"
        assert ffmpeg_path.exists(), f"FFmpeg binary not found at {ffmpeg_path}"

    def test_media_processing_success_rate(self):
        """Test 95%+ success rate for common formats (NFR9)."""
        test_files = [
            'tests/test_data/brownfield_samples/audio/test.wav',
            'tests/test_data/brownfield_samples/audio/test.mp3',
            'tests/test_data/brownfield_samples/audio/test.flac',
            # ... 100 test files
        ]

        success_count = 0
        for file in test_files:
            try:
                metadata = extract_metadata(file)
                if metadata:
                    success_count += 1
            except:
                pass

        success_rate = (success_count / len(test_files)) * 100
        assert success_rate >= 95, f"Success rate {success_rate}% < 95%"
```

**UI Integration Test:**
```python
import pytest
from django.test import Client
from apps.catalog.models import Schema

class TestUIIntegration:
    def test_schema_crud_workflow(self):
        """Test complete Schema CRUD workflow."""
        client = Client()

        # Create
        response = client.post('/schemas/create/', {
            'name': 'Test Schema',
            'description': 'Test',
            'is_active': True
        })
        assert response.status_code == 302  # Redirect

        # Read
        response = client.get('/schemas/')
        assert 'Test Schema' in response.content.decode()

        # Update
        schema = Schema.objects.get(name='Test Schema')
        response = client.post(f'/schemas/{schema.id}/edit/', {
            'name': 'Updated Schema',
            'description': 'Updated',
            'is_active': True
        })
        assert response.status_code == 302

        # Delete
        response = client.post(f'/schemas/{schema.id}/delete/')
        assert response.status_code == 302
        assert not Schema.objects.filter(id=schema.id).exists()
```

**Setup Validation Test:**
```python
import pytest
import subprocess

class TestSetupValidation:
    @pytest.mark.slow
    def test_clone_to_run_windows(self):
        """Test clone-to-run on fresh Windows VM."""
        # Assumes Vagrant configured
        result = subprocess.run([
            'vagrant', 'up', 'windows',
            '&&', 'vagrant', 'ssh', 'windows', '-c',
            'git clone https://github.com/org/samplify && cd samplify && python setup.py'
        ], capture_output=True)

        assert result.returncode == 0, f"Setup failed: {result.stderr}"

    @pytest.mark.slow
    def test_setup_completes_under_5_minutes(self):
        """Test setup completes <5 minutes."""
        import time
        start = time.time()

        subprocess.run(['python', 'setup.py'], check=True)

        elapsed = time.time() - start
        assert elapsed < 300, f"Setup took {elapsed}s > 5 minutes"
```

### Performance Benchmarks Documentation
**Template for docs/testing/performance-benchmarks.md:**
```markdown
# Performance Benchmarks

## Test Environment
- CPU: Intel Core i7-9700K @ 3.60GHz (8 cores)
- RAM: 16 GB
- OS: Windows 10 / macOS 12 / Ubuntu 20.04
- Python: 3.10.5
- Django: 4.2.7

## CPU Utilization (NFR1)
**Target:** 50-70% during batch processing
**Actual:** 62% average (10 samples)
**Status:** ✅ PASS

## Processing Speed (NFR5)
**Target:** 1000 files < 5 minutes
**Actual:** 1000 files in 3m 42s
**Status:** ✅ PASS

## Algorithm Preservation (CR1)
**Test Cases:** 250 files tested
**Identical Results:** 250/250 (100%)
**Status:** ✅ PASS

## FFmpeg Success Rate (NFR9)
**Test Files:** 100 common formats
**Success Rate:** 97%
**Status:** ✅ PASS (>95%)

## Comparison with Brownfield
| Metric | Brownfield | Django | Delta |
|--------|------------|--------|-------|
| Processing Speed | 4m 10s | 3m 42s | +11% faster |
| CPU Utilization | 65% | 62% | -3% |
| Memory Usage | 512 MB | 480 MB | -6% |
```

### Preservation Rules
**CR1 Validation:** Algorithm preservation [Source: requirements.md CR1]
- Side-by-side testing with brownfield
- 100% identical output required

**CR2 Validation:** Multiprocessing preservation [Source: requirements.md CR2]
- CPU utilization 50-70%
- Worker pool scales to CPU cores

**NFR Requirements:** All NFRs validated [Source: requirements.md]
- NFR1: CPU 50-70% ✓
- NFR2: WAL mode ✓
- NFR9: FFmpeg 95%+ ✓

---

## Dev Notes > Testing

### Test File Location
```
tests/
├── integration/
│   └── (test files listed above)
└── test_data/
    └── brownfield_samples/
```

### Testing Standards
**Framework:** pytest + pytest-django

**Test Coverage Target:** 80%+ overall, 100% critical paths

**Test Categories:**
1. **Algorithm Preservation (CR1)**
   - Side-by-side comparison
   - 100% identical output

2. **Performance (CR2/NFR1)**
   - CPU utilization 50-70%
   - Worker pool scaling

3. **Compatibility (CR3/CR4)**
   - ORM migration
   - XML template import

4. **FFmpeg (FR7/CR6)**
   - Platform detection
   - 95%+ success rate

5. **Concurrent Access (NFR2)**
   - WAL mode validation
   - Multiprocessing + Django

6. **UI Integration**
   - CRUD workflows
   - Watchdog controls

7. **Setup Validation (FR15/FR16)**
   - Clone-to-run
   - <5 minute setup

**Running Tests:**
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/integration/ --cov=samplify --cov-report=html

# Run specific test suites
pytest tests/integration/test_algorithm_preservation.py -v
pytest tests/integration/test_performance.py -v

# Run slow tests (VMs)
pytest tests/integration/ -v --runslow
```

---

## Definition of Done
- [ ] Test suite implemented (80%+ coverage)
- [ ] Algorithm preservation validated (CR1)
- [ ] Multiprocessing performance validated (CR2/NFR1)
- [ ] Compatibility validated (CR3/CR4)
- [ ] FFmpeg integration validated (FR7/CR6)
- [ ] WAL mode validated (NFR2)
- [ ] All tests passing on all platforms
- [ ] Performance benchmarks documented
- [ ] Test reports generated
- [ ] Documentation updated with testing details

---

## Risk Assessment
- **Primary Risk:** Tests reveal algorithm or performance deviations
- **Mitigation:** Iterative testing during development, fix issues incrementally
- **Rollback:** Fix failing components, re-test, delay release if needed

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
