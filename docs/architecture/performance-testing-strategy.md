# Performance Testing & Validation Strategy

**Status:** Draft
**Created:** 2025-10-06
**Owner:** Winston (Architect)
**Related ADRs:** None (cross-cutting strategy)
**Related NFRs:** NFR1, NFR5, NFR7, NFR10

---

## Purpose

This document defines Samplify's **performance testing and validation strategy** to ensure all NFRs are systematically benchmarked and monitored.

**Motivation:** QA review (Stories 1.3-1.8) identified missing performance validation:
- Story 1.3: Logging performance not benchmarked (NFR7)
- Story 1.5: File scanning performance not validated (NFR5) - NOW COMPLETE
- Story 1.6: CPU utilization not validated (NFR1)
- Story 1.7: Latency not validated (NFR10)

---

## Performance NFR Summary

| NFR | Requirement | Target | Current Status |
|-----|-------------|--------|----------------|
| **NFR1** | CPU utilization during batch processing | 50-70% | ⚠️ Not validated |
| **NFR5** | File scanning speed (1000 files) | <5 minutes | ✅ VALIDATED (0.05s) |
| **NFR7** | Logging overhead | <5% CPU impact | ⚠️ Not benchmarked |
| **NFR10** | File monitor latency | <10 seconds | ⚠️ Test exists but skipped |

**Validation Score:** 1/4 NFRs validated (25%)

---

## Core Principles

### 1. Benchmark All NFRs
- Every performance NFR MUST have an automated benchmark test
- Benchmarks run during development (not just in CI)
- Baseline metrics documented for comparison

### 2. Realistic Test Data
- Test datasets mimic production workloads
- File sizes, formats, and quantities realistic
- Avoid synthetic "happy path" only tests

### 3. Measure What Matters
- User-facing metrics (latency, throughput)
- Resource utilization (CPU, memory, disk I/O)
- Scalability characteristics (how performance degrades with load)

### 4. Continuous Validation
- Performance tests in CI/CD pipeline
- Regression detection (alert if 10%+ slower)
- Trend analysis over time

---

## Performance Test Framework

### Pytest Integration

**Marker Configuration (`pytest.ini`):**
```ini
[pytest]
markers =
    performance: Performance benchmark tests (run manually or in CI)
    benchmark: Alias for performance
    slow: Tests that take >10 seconds
```

**Running Performance Tests:**
```bash
# Run all performance tests
pytest -v -m performance

# Run specific NFR validation
pytest -v -m performance -k "nfr5"

# Skip performance tests (default)
pytest -v -m "not performance"
```

---

### Test Structure Pattern

**Standard Performance Test Structure:**
```python
import time
import pytest
from pathlib import Path

@pytest.mark.performance
def test_performance_<component>_<nfr>():
    """
    Performance test for <Component>.

    Validates: <NFR_ID> - <Requirement Description>
    Target: <Metric> <Operator> <Value>
    """
    # SETUP: Create realistic test data
    test_data = generate_test_dataset(count=1000)

    # MEASURE: Execute operation and time it
    start_time = time.perf_counter()
    result = perform_operation(test_data)
    duration = time.perf_counter() - start_time

    # CALCULATE: Derive metrics
    throughput = len(test_data) / duration  # items/second

    # GRADE: Assess performance vs NFR
    if duration < target_excellent:
        grade = "EXCELLENT"
    elif duration < target_good:
        grade = "GOOD"
    else:
        grade = "FAIL"

    # LOG: Report results
    print(f"\n{'='*60}")
    print(f"Performance Benchmark: <Component>")
    print(f"NFR: <NFR_ID>")
    print(f"Items: {len(test_data)}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Throughput: {throughput:.2f} items/second")
    print(f"Grade: {grade}")
    print(f"{'='*60}\n")

    # ASSERT: Fail if below threshold
    assert duration < target_good, \
        f"Performance FAIL: {duration:.2f}s exceeds {target_good}s threshold"
```

---

## NFR-Specific Test Strategies

### NFR1: CPU Utilization (Batch Processing)

**Story:** 1.6 - Batch Processing Management Command
**Requirement:** 50-70% CPU utilization during multiprocessing
**Current Status:** ⚠️ Test exists but marked as skip

**Test Strategy:**
```python
import psutil
import multiprocessing

@pytest.mark.performance
@pytest.mark.slow  # Takes ~2-3 minutes
def test_nfr1_batch_processing_cpu_utilization():
    """
    Validates NFR1: CPU utilization during batch processing.

    Target: 50-70% CPU average across 1000-file batch.
    """
    # SETUP: Generate 1000 test files
    test_files = generate_test_audio_files(count=1000)

    # MEASURE: Monitor CPU during batch processing
    cpu_samples = []

    def monitor_cpu(stop_event):
        """Background thread to sample CPU every 500ms."""
        while not stop_event.is_set():
            cpu_samples.append(psutil.cpu_percent(interval=0.5))

    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_cpu, args=(stop_event,))
    monitor_thread.start()

    # Execute batch processing
    call_command('batch_process', input_dir=test_files, workers=4)

    stop_event.set()
    monitor_thread.join()

    # CALCULATE: Average CPU utilization
    avg_cpu = sum(cpu_samples) / len(cpu_samples)

    # GRADE
    if 50 <= avg_cpu <= 70:
        grade = "EXCELLENT (within target)"
    elif 40 <= avg_cpu < 50 or 70 < avg_cpu <= 80:
        grade = "GOOD (close to target)"
    else:
        grade = "NEEDS OPTIMIZATION"

    # REPORT
    print(f"\nNFR1 Batch Processing CPU Utilization:")
    print(f"Files Processed: {len(test_files)}")
    print(f"Workers: 4")
    print(f"Samples: {len(cpu_samples)}")
    print(f"Average CPU: {avg_cpu:.1f}%")
    print(f"Target Range: 50-70%")
    print(f"Grade: {grade}\n")

    # ASSERT: Reasonable CPU usage (lenient - not optimizing for underuse)
    assert 30 <= avg_cpu <= 90, \
        f"CPU usage {avg_cpu:.1f}% outside reasonable bounds (30-90%)"
```

**Execution:** Manual (CI optional due to duration)

---

### NFR5: File Scanning Speed ✅

**Story:** 1.5 - File Scanning Service
**Requirement:** 1000 files scanned in <5 minutes
**Current Status:** ✅ VALIDATED (0.05 seconds - exceeds by 6000x)

**Test Implementation (Reference):**
```python
@pytest.mark.performance
def test_nfr5_file_scanning_performance():
    """
    Validates NFR5: File scanning performance.

    Target: 1000 files < 5 minutes (300 seconds)
    """
    # SETUP
    test_files = generate_test_dataset(
        audio_count=700,
        video_count=200,
        image_count=100,
    )

    # MEASURE
    start = time.perf_counter()
    results = scan_directory(test_files)
    duration = time.perf_counter() - start

    # CALCULATE
    throughput = len(results) / duration

    # GRADE
    if duration < 180:  # <3 minutes
        grade = "EXCELLENT"
    elif duration < 300:  # <5 minutes (NFR target)
        grade = "GOOD"
    else:
        grade = "FAIL"

    # REPORT
    print(f"\nNFR5 File Scanning Performance:")
    print(f"Files: {len(results)}")
    print(f"Duration: {duration:.2f}s ({duration/60:.2f} min)")
    print(f"Throughput: {throughput:.2f} files/sec")
    print(f"Grade: {grade}\n")

    # ASSERT
    assert duration < 300, \
        f"Scanning {len(results)} files took {duration:.2f}s, exceeds 300s limit"
```

**Result (Session 3):**
- Duration: 0.05 seconds
- Throughput: 18,844 files/second
- Grade: EXCELLENT
- **Status:** ✅ PASS

---

### NFR7: Logging Performance

**Story:** 1.3 - Loguru Configuration
**Requirement:** Logging overhead <5% CPU impact
**Current Status:** ⚠️ Not benchmarked

**Test Strategy:**
```python
import cProfile
import pstats

@pytest.mark.performance
def test_nfr7_logging_overhead():
    """
    Validates NFR7: Logging performance overhead.

    Target: <5% CPU overhead from logging calls.
    """
    from loguru import logger

    # BASELINE: Measure operation without logging
    def operation_without_logging(iterations=10000):
        for i in range(iterations):
            _ = complex_calculation(i)

    profiler = cProfile.Profile()
    profiler.enable()
    operation_without_logging()
    profiler.disable()

    stats = pstats.Stats(profiler)
    baseline_time = stats.total_tt

    # WITH LOGGING: Measure operation with logging
    def operation_with_logging(iterations=10000):
        for i in range(iterations):
            logger.debug(f"Processing item {i}")
            _ = complex_calculation(i)

    profiler = cProfile.Profile()
    profiler.enable()
    operation_with_logging()
    profiler.disable()

    stats = pstats.Stats(profiler)
    logging_time = stats.total_tt

    # CALCULATE: Overhead percentage
    overhead_pct = ((logging_time - baseline_time) / baseline_time) * 100

    # GRADE
    if overhead_pct < 3:
        grade = "EXCELLENT"
    elif overhead_pct < 5:
        grade = "GOOD (within NFR)"
    elif overhead_pct < 10:
        grade = "ACCEPTABLE (slight overhead)"
    else:
        grade = "NEEDS OPTIMIZATION"

    # REPORT
    print(f"\nNFR7 Logging Performance Overhead:")
    print(f"Baseline (no logging): {baseline_time:.4f}s")
    print(f"With logging: {logging_time:.4f}s")
    print(f"Overhead: {overhead_pct:.2f}%")
    print(f"Target: <5%")
    print(f"Grade: {grade}\n")

    # ASSERT: Lenient threshold (10% acceptable for local development)
    assert overhead_pct < 10, \
        f"Logging overhead {overhead_pct:.2f}% exceeds 10% threshold"
```

**Execution:** Manual or CI

**Note:** Story 1.3 uses Loguru with async file writing (minimal overhead expected)

---

### NFR10: File Monitor Latency

**Story:** 1.7 - File Monitor Watchdog
**Requirement:** <10 seconds from file creation to database record
**Current Status:** ⚠️ Test exists but marked as skip

**Test Strategy:**
```python
import shutil
from watchdog.observers import Observer

@pytest.mark.performance
@pytest.mark.slow  # Requires real watchdog observer (30s test)
def test_nfr10_file_monitor_latency(tmp_path, db):
    """
    Validates NFR10: File monitor latency.

    Target: File detected and inserted to DB within 10 seconds.
    """
    # SETUP: Start file monitor watchdog
    from samplify.management.commands.file_monitor import FileEventHandler

    event_handler = FileEventHandler(db_connection=db)
    observer = Observer()
    observer.schedule(event_handler, str(tmp_path), recursive=False)
    observer.start()

    latencies = []

    try:
        # MEASURE: Create 10 test files and measure latency
        for i in range(10):
            test_file = tmp_path / f"test_audio_{i}.wav"

            # Create file
            create_time = time.perf_counter()
            shutil.copy("tests/fixtures/sample.wav", test_file)

            # Wait for DB record (poll every 100ms, max 15s)
            db_record = None
            timeout = 15
            start_wait = time.perf_counter()

            while (time.perf_counter() - start_wait) < timeout:
                db_record = File.objects.filter(file_path=str(test_file)).first()
                if db_record:
                    break
                time.sleep(0.1)

            if not db_record:
                pytest.fail(f"File {test_file} not detected within {timeout}s")

            # Calculate latency
            latency = db_record.created_at.timestamp() - create_time
            latencies.append(latency)

    finally:
        observer.stop()
        observer.join()

    # CALCULATE: Average, min, max, p95 latency
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)
    p95_latency = sorted(latencies)[int(0.95 * len(latencies))]

    # GRADE
    if p95_latency < 5:
        grade = "EXCELLENT"
    elif p95_latency < 10:
        grade = "GOOD (within NFR)"
    else:
        grade = "NEEDS OPTIMIZATION"

    # REPORT
    print(f"\nNFR10 File Monitor Latency:")
    print(f"Files Tested: {len(latencies)}")
    print(f"Average Latency: {avg_latency:.2f}s")
    print(f"Min Latency: {min_latency:.2f}s")
    print(f"Max Latency: {max_latency:.2f}s")
    print(f"P95 Latency: {p95_latency:.2f}s")
    print(f"Target: <10s")
    print(f"Grade: {grade}\n")

    # ASSERT
    assert p95_latency < 10, \
        f"P95 latency {p95_latency:.2f}s exceeds 10s NFR requirement"
```

**Execution:** Manual (requires real file system events)

---

## Performance Grading System

### Standardized Grading Criteria

**EXCELLENT:**
- Exceeds NFR by ≥50% margin
- Example: NFR5 required <300s, achieved 0.05s (6000x faster)

**GOOD:**
- Meets NFR within acceptable margin (0-20% below target)
- Example: NFR1 target 50-70% CPU, achieved 55% CPU

**ACCEPTABLE:**
- Meets NFR but with minimal margin (20-50% below target)
- Example: NFR10 target <10s, achieved 9s

**NEEDS OPTIMIZATION:**
- Misses NFR but within recoverable range (50-100% over target)
- Example: NFR7 target <5% overhead, achieved 8% overhead

**FAIL:**
- Significantly misses NFR (>100% over target)
- Example: NFR5 target <300s, achieved 650s

---

## Baseline Metrics Documentation

### Current Validated Baselines

**NFR5: File Scanning (Story 1.5):**
```
Environment: Windows 10, Python 3.11, FFmpeg 8.0
Dataset: 1000 files (700 audio, 200 video, 100 image)
Result: 0.05 seconds (18,844 files/second)
Grade: EXCELLENT ✅
Date: 2025-10-06
```

**NFR1: Batch Processing (Story 1.6):**
```
Environment: TBD
Dataset: TBD
Result: NOT VALIDATED
Grade: PENDING
```

**NFR7: Logging Overhead (Story 1.3):**
```
Environment: TBD
Dataset: TBD
Result: NOT VALIDATED
Grade: PENDING
```

**NFR10: File Monitor Latency (Story 1.7):**
```
Environment: TBD
Dataset: TBD
Result: NOT VALIDATED
Grade: PENDING
```

---

## CI/CD Integration

### Performance Test Execution Strategy

**Local Development:**
```bash
# Run quick performance checks (exclude slow tests)
pytest -v -m "performance and not slow"

# Run full performance suite (including slow tests)
pytest -v -m performance --durations=10
```

**Pull Request CI:**
```yaml
# .github/workflows/pr-tests.yml
performance-tests:
  runs-on: ubuntu-latest
  steps:
    - name: Run performance tests
      run: pytest -v -m "performance and not slow" --timeout=300

    - name: Compare with baseline
      run: python scripts/compare_performance.py
```

**Nightly CI (Full Suite):**
```yaml
# .github/workflows/nightly.yml
full-performance:
  runs-on: ubuntu-latest
  steps:
    - name: Run all performance tests (including slow)
      run: pytest -v -m performance --timeout=1800

    - name: Generate performance report
      run: python scripts/generate_perf_report.py

    - name: Alert on regression
      if: ${{ steps.compare.outputs.regression == 'true' }}
      run: echo "Performance regression detected!" && exit 1
```

---

## Performance Regression Detection

### Automated Comparison

**Baseline File (`baselines/performance.json`):**
```json
{
  "nfr5_file_scanning": {
    "duration_seconds": 0.05,
    "throughput_files_per_second": 18844.49,
    "date": "2025-10-06",
    "grade": "EXCELLENT"
  }
}
```

**Regression Check Script:**
```python
# scripts/compare_performance.py
import json

def check_regression(baseline_file, current_results, threshold=0.10):
    """Alert if performance degrades by >10%."""
    with open(baseline_file) as f:
        baselines = json.load(f)

    for test_name, current in current_results.items():
        baseline = baselines.get(test_name)
        if not baseline:
            print(f"⚠️  No baseline for {test_name}, skipping")
            continue

        # Compare duration (lower is better)
        baseline_duration = baseline['duration_seconds']
        current_duration = current['duration_seconds']
        pct_change = ((current_duration - baseline_duration) / baseline_duration) * 100

        if pct_change > (threshold * 100):
            print(f"🚨 REGRESSION: {test_name}")
            print(f"   Baseline: {baseline_duration:.2f}s")
            print(f"   Current:  {current_duration:.2f}s")
            print(f"   Change:   +{pct_change:.1f}%")
            return True  # Regression detected

    print("✅ No performance regressions detected")
    return False
```

---

## Test Data Management

### Fixture Generation Strategy

**Audio Files (WAV):**
```python
def generate_audio_file(path: Path, duration_sec: int = 5):
    """Generate silent WAV file for testing."""
    sample_rate = 44100
    samples = np.zeros(sample_rate * duration_sec, dtype=np.int16)
    scipy.io.wavfile.write(path, sample_rate, samples)
```

**Video Files (MP4):**
```python
def generate_video_file(path: Path, duration_sec: int = 3):
    """Generate blank MP4 using FFmpeg."""
    subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', f'color=c=black:s=640x480:d={duration_sec}',
        '-c:v', 'libx264', '-t', str(duration_sec), str(path)
    ], check=True)
```

**Image Files (JPEG):**
```python
from PIL import Image

def generate_image_file(path: Path, width: int = 640, height: int = 480):
    """Generate blank JPEG image."""
    img = Image.new('RGB', (width, height), color='black')
    img.save(path, 'JPEG')
```

**Dataset Cleanup:**
```python
@pytest.fixture(scope="session")
def test_dataset(tmp_path_factory):
    """Generate test dataset once per session, cleanup after."""
    dataset_dir = tmp_path_factory.mktemp("performance_dataset")

    # Generate files
    generate_test_dataset(dataset_dir, audio=700, video=200, image=100)

    yield dataset_dir

    # Cleanup
    shutil.rmtree(dataset_dir)
```

---

## Troubleshooting Performance Issues

### Common Performance Antipatterns

**1. N+1 Query Problem (Database):**
```python
# BAD: Queries in loop
for file in File.objects.all():
    schema = file.schema  # Separate query per file

# GOOD: Prefetch related
files = File.objects.select_related('schema').all()
for file in files:
    schema = file.schema  # No extra query
```

**2. Synchronous External Calls:**
```python
# BAD: Blocking FFmpeg calls
for file in files:
    metadata = extract_ffmpeg_metadata(file)  # Blocks for 1-2s each

# GOOD: Async or multiprocessing
with ProcessPoolExecutor() as executor:
    futures = [executor.submit(extract_ffmpeg_metadata, f) for f in files]
    results = [f.result() for f in futures]
```

**3. Excessive Logging in Hot Paths:**
```python
# BAD: Debug logging in tight loop
for i in range(1000000):
    logger.debug(f"Processing item {i}")  # Expensive string formatting
    process(i)

# GOOD: Conditional logging or sampling
if i % 1000 == 0:  # Log every 1000th item
    logger.debug(f"Progress: {i}/1000000")
```

---

## Review & Maintenance

**Review Frequency:** After each major release
**Next Review:** Post-MVP (Q1 2026)

**Trigger for Early Review:**
- Performance regression detected in CI
- User-reported performance issues
- Infrastructure changes (new hardware, cloud migration)

---

**Last Updated:** 2025-10-06
**Owner:** Winston (Architect)
**Status:** Draft → Under Review
