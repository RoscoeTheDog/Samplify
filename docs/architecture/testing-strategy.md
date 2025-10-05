# Testing Strategy

**Version:** 1.0
**Last Updated:** 2025-10-04
**Status:** Specification Document

---

## Overview

This document defines the comprehensive testing strategy for Samplify Django Web UI, including unit tests, integration tests, workflow validation tests, and algorithm preservation verification.

**Key Principle**: Test with real media files in `/media/` folder to validate end-to-end workflows WITHOUT modifying source media.

---

## Test Media Library (`/media/` Folder)

### Purpose

The `/media/` directory contains curated test media for validating Samplify's processing workflows across different media types and use cases.

**Critical Constraint**: Source media files are **READ-ONLY** - never modified during testing.

### Directory Structure

```
media/
├── audio/
│   ├── music/
│   │   ├── drums/
│   │   │   ├── kick_01_44k_24bit.wav
│   │   │   ├── kick_02_48k_16bit.wav
│   │   │   ├── snare_01_44k_24bit.wav
│   │   │   └── hihat_01_44k_16bit.wav
│   │   ├── bass/
│   │   │   ├── bass_c_01.wav
│   │   │   ├── bass_d_01.wav
│   │   │   └── synth_bass_01.wav
│   │   ├── synth/
│   │   │   ├── pad_a_01.wav
│   │   │   ├── lead_c_01.wav
│   │   │   └── chord_gmaj_01.wav
│   │   └── vocals/
│   │       ├── vocal_take_01.wav
│   │       └── vocal_harmony_01.wav
│   └── samples/
│       ├── fx/
│       │   ├── riser_01.wav
│       │   ├── impact_01.wav
│       │   └── sweep_01.wav
│       └── ambience/
│           ├── rain_loop.wav
│           └── city_ambience.wav
│
├── video/
│   ├── footage/
│   │   ├── interview_01_1080p.mp4
│   │   ├── broll_nature_01_4k.mp4
│   │   └── timelapse_city_01.mp4
│   ├── screencast/
│   │   ├── tutorial_01.mp4
│   │   └── demo_recording_01.mp4
│   └── animation/
│       ├── intro_logo_01.mp4
│       └── transition_01.mp4
│
├── image/
│   ├── photos/
│   │   ├── raw/
│   │   │   ├── portrait_01.cr2         (Canon RAW)
│   │   │   ├── landscape_01.nef        (Nikon RAW)
│   │   │   └── product_01.arw          (Sony RAW)
│   │   ├── jpeg/
│   │   │   ├── event_photo_01.jpg
│   │   │   ├── event_photo_02.jpg
│   │   │   └── event_photo_03.jpg
│   │   └── png/
│   │       ├── screenshot_01.png
│   │       └── screenshot_02.png
│   ├── graphics/
│   │   ├── logo_variations/
│   │   │   ├── logo_color.svg
│   │   │   ├── logo_black.svg
│   │   │   └── logo_white.svg
│   │   └── icons/
│   │       ├── icon_home.svg
│   │       ├── icon_settings.svg
│   │       └── icon_user.svg
│   └── textures/
│       ├── wood_grain_01.jpg
│       └── concrete_01.jpg
│
└── README.md  (describes each test file, purpose, metadata)
```

### Media File Specifications

**Audio Files**:
- **Formats**: WAV (primary), MP3, FLAC, OGG
- **Sample Rates**: 44.1kHz, 48kHz, 96kHz
- **Bit Depths**: 16-bit, 24-bit
- **Channels**: Mono, Stereo
- **Duration**: 1-10 seconds (short samples for fast testing)
- **Naming Convention**: `{type}_{note/variant}_{number}_{samplerate}_{bitdepth}.{ext}`

**Video Files**:
- **Formats**: MP4 (H.264), MOV, MKV
- **Resolutions**: 1080p, 4K
- **Frame Rates**: 24fps, 30fps, 60fps
- **Duration**: 5-30 seconds
- **Audio**: Embedded audio tracks

**Image Files**:
- **Formats**: JPEG, PNG, SVG, RAW (CR2, NEF, ARW)
- **Resolutions**: 1920x1080, 3840x2160, variable (RAW)
- **Color Spaces**: sRGB, Adobe RGB
- **DPI**: 72, 300

### Media Collection Guidelines

**Acquisition**:
1. **Royalty-Free Sources**:
   - Freesound.org (audio samples - Creative Commons)
   - Pexels.com (video footage, photos - free license)
   - Unsplash.com (photos - free license)
   - Generate synthetic audio (pure tones, noise) using FFmpeg

2. **Synthetic Generation** (preferred for tests):
   ```bash
   # Generate test audio samples
   ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -ar 44100 -ac 2 test_tone_440hz.wav
   ffmpeg -f lavfi -i "anoisesrc=duration=5" -ar 48000 -ac 1 test_noise.wav

   # Generate test video
   ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 test_pattern.mp4
   ```

3. **Licensing**:
   - Document source and license in `media/README.md`
   - Only use CC0, CC-BY, or self-generated content
   - Avoid copyrighted material

---

## Test Workflow Scenarios

### Workflow 1: Music Production Sample Organization

**Use Case**: Electronic music producer organizing drum samples

**Input Directory**: `media/audio/music/drums/`

**Schema Configuration**:
```python
{
    "name": "Drum Sample Sorter",
    "input_directories": [
        {"path": "media/audio/music/drums/", "monitor": False, "recursive": False}
    ],
    "output_directories": [
        {
            "path": "output/test/drums/kicks/",
            "filters": [
                {"type": "keyword", "value": "kick", "case_sensitive": False}
            ],
            "processing_rules": [
                {"output_format": "WAV", "sample_rate": 44100, "bit_depth": 24, "normalize": True, "normalize_level": -6.0}
            ],
            "logic_operator": "AND"
        },
        {
            "path": "output/test/drums/snares/",
            "filters": [
                {"type": "keyword", "value": "snare", "case_sensitive": False}
            ],
            "processing_rules": [
                {"output_format": "WAV", "sample_rate": 44100, "bit_depth": 24, "normalize": True, "normalize_level": -6.0}
            ],
            "logic_operator": "AND"
        },
        {
            "path": "output/test/drums/hihats/",
            "filters": [
                {"type": "keyword", "value": "hihat", "case_sensitive": False}
            ],
            "processing_rules": [
                {"output_format": "WAV", "sample_rate": 44100, "bit_depth": 24, "normalize": True, "normalize_level": -6.0}
            ],
            "logic_operator": "AND"
        }
    ]
}
```

**Expected Behavior**:
1. Scan `media/audio/music/drums/`
2. Route `kick_*.wav` → `output/test/drums/kicks/`
3. Route `snare_*.wav` → `output/test/drums/snares/`
4. Route `hihat_*.wav` → `output/test/drums/hihats/`
5. Convert all to 44.1kHz, 24-bit, normalize to -6dB
6. **Verify**: Original files in `media/` unchanged
7. **Verify**: Output files exist with correct format

**Test Assertions**:
- [ ] All 4 kick files routed to kicks/
- [ ] All snare files routed to snares/
- [ ] All hihat files routed to hihats/
- [ ] Output sample rate = 44100 Hz
- [ ] Output bit depth = 24-bit
- [ ] Peak level ≈ -6.0 dB (±0.5 dB tolerance)
- [ ] Original files unmodified (checksum verification)

---

### Workflow 2: Video Production Footage Organization

**Use Case**: Video editor organizing b-roll footage by resolution

**Input Directory**: `media/video/footage/`

**Schema Configuration**:
```python
{
    "name": "Video Resolution Sorter",
    "input_directories": [
        {"path": "media/video/footage/", "monitor": False, "recursive": False}
    ],
    "output_directories": [
        {
            "path": "output/test/video/4k/",
            "filters": [
                {"type": "metadata", "field": "resolution_width", "operator": ">=", "value": 3840}
            ],
            "processing_rules": [
                {"output_format": "MP4", "codec": "h264", "bitrate": "20M"}
            ],
            "logic_operator": "AND"
        },
        {
            "path": "output/test/video/1080p/",
            "filters": [
                {"type": "metadata", "field": "resolution_width", "operator": ">=", "value": 1920},
                {"type": "metadata", "field": "resolution_width", "operator": "<", "value": 3840}
            ],
            "processing_rules": [
                {"output_format": "MP4", "codec": "h264", "bitrate": "8M"}
            ],
            "logic_operator": "AND"
        }
    ]
}
```

**Expected Behavior**:
1. Scan `media/video/footage/`
2. Extract metadata (resolution, codec, duration)
3. Route 4K videos (3840x2160) → `output/test/video/4k/`
4. Route 1080p videos → `output/test/video/1080p/`
5. Re-encode with specified bitrates

**Test Assertions**:
- [ ] 4K video routed correctly
- [ ] 1080p videos routed correctly
- [ ] Output codec = H.264
- [ ] Bitrate within ±10% of specified
- [ ] Original files unmodified

---

### Workflow 3: Photography Workflow - RAW to JPEG Conversion

**Use Case**: Photographer exporting RAW files to JPEG for client delivery

**Input Directory**: `media/image/photos/raw/`

**Schema Configuration**:
```python
{
    "name": "RAW to JPEG Exporter",
    "input_directories": [
        {"path": "media/image/photos/raw/", "monitor": False, "recursive": False}
    ],
    "output_directories": [
        {
            "path": "output/test/photos/client_delivery/",
            "filters": [
                {"type": "extension", "value": [".cr2", ".nef", ".arw"]}
            ],
            "processing_rules": [
                {
                    "output_format": "JPEG",
                    "quality": 90,
                    "resize": {"max_dimension": 2048, "maintain_aspect": True},
                    "color_space": "sRGB"
                }
            ],
            "logic_operator": "AND"
        }
    ]
}
```

**Expected Behavior**:
1. Scan for RAW files (.cr2, .nef, .arw)
2. Convert to JPEG with 90% quality
3. Resize to max 2048px (longest dimension)
4. Convert to sRGB color space

**Test Assertions**:
- [ ] All RAW files converted to JPEG
- [ ] JPEG quality ≈ 90%
- [ ] Max dimension ≤ 2048px
- [ ] Color space = sRGB
- [ ] Original RAW files unmodified

---

## Algorithm Preservation Validation (CR1/CR2)

### Objective

Verify that Django implementation produces **identical results** to brownfield Python CLI implementation.

### Comparison Methodology

**Approach**: Side-by-side execution with identical inputs

**Setup**:
1. **Brownfield (Baseline)**: Run original Python CLI with test schema
2. **Django (New)**: Run Django web UI with migrated schema
3. **Compare**: File routing decisions, output filenames, metadata

**Test Data**:
- Same input files from `/media/`
- Same schema configuration (migrated from XML template)

**Comparison Criteria**:
1. **File Routing**: Exact same files routed to exact same output directories
2. **Processing Decisions**: Same format conversions, sample rates, bit depths
3. **Output Filenames**: Identical naming (if brownfield had naming logic)
4. **Performance**: CPU utilization within ±10% (50-70% target per NFR5)

### Test Procedure

**Step 1: Baseline Capture (Brownfield)**
```bash
# Run brownfield version
cd brownfield/
python samplify_cli.py --template schemas/drum_template.xml --input media/audio/music/drums/

# Document results
ls -la output/drums/kicks/ > baseline_kicks.txt
ls -la output/drums/snares/ > baseline_snares.txt
```

**Step 2: Django Execution**
```bash
# Run Django version
python manage.py migrate_xml_template schemas/drum_template.xml
python manage.py scan_input --schema-id=1
python manage.py batch_process --schema-id=1

# Document results
ls -la output/test/drums/kicks/ > django_kicks.txt
ls -la output/test/drums/snares/ > django_snares.txt
```

**Step 3: Comparison**
```bash
# Compare file lists
diff baseline_kicks.txt django_kicks.txt
diff baseline_snares.txt django_snares.txt

# Verify file checksums (ensure identical processing)
md5sum output/drums/kicks/* > baseline_checksums.txt
md5sum output/test/drums/kicks/* > django_checksums.txt
diff baseline_checksums.txt django_checksums.txt
```

**Acceptance Criteria**:
- [ ] **100% routing match**: Same input files → same output directories
- [ ] **Identical processing**: Same format conversions applied
- [ ] **Performance**: CPU utilization 50-70% (±10% of brownfield)
- [ ] **No regressions**: All brownfield features preserved

**Failure Response**:
1. Document discrepancy in `docs/testing/algorithm-validation-report.md`
2. Investigate root cause (ORM query differences? Processing logic change?)
3. **Do not proceed** until discrepancy resolved (CR1 violation)

---

## Integration Testing

### Database Concurrency (WAL Mode Validation)

**Objective**: Verify SQLite WAL mode enables concurrent reads during writes

**Test Scenario**:
```python
import threading
import time
from django.test import TestCase
from apps.schemas.models import Schema

class WALConcurrencyTest(TestCase):
    def test_concurrent_read_write(self):
        """Verify concurrent reads work during write operations."""
        schema = Schema.objects.create(name="Test Schema")

        def write_operation():
            """Simulate long-running write."""
            for i in range(10):
                schema.description = f"Update {i}"
                schema.save()
                time.sleep(0.1)

        def read_operation():
            """Simulate concurrent read."""
            results = []
            for _ in range(10):
                s = Schema.objects.get(id=schema.id)
                results.append(s.description)
                time.sleep(0.1)
            return results

        # Start write thread
        write_thread = threading.Thread(target=write_operation)
        write_thread.start()

        # Concurrent reads should NOT block
        time.sleep(0.05)  # Ensure write started
        read_results = read_operation()

        write_thread.join()

        # Assertions
        self.assertEqual(len(read_results), 10)
        # Should have read some intermediate states (not blocked)
```

**Acceptance Criteria**:
- [ ] Reads complete successfully during writes
- [ ] No database lock errors
- [ ] WAL mode confirmed in settings

---

### Dual Watchdog Coordination

**Objective**: Verify file monitor and queue processor coordinate without race conditions

**Test Scenario**:
```python
from django.test import TransactionTestCase
from apps.processing.services import FileMonitorWatchdog, QueueProcessorWatchdog
import time

class DualWatchdogTest(TransactionTestCase):
    def test_no_race_condition(self):
        """Verify file monitor and queue processor coordinate properly."""
        # Start both watchdogs
        file_monitor = FileMonitorWatchdog()
        queue_processor = QueueProcessorWatchdog()

        file_monitor.start()
        queue_processor.start()

        # Simulate file creation
        test_file = Path("media/audio/music/drums/test_kick.wav")
        test_file.touch()

        # Wait for processing
        time.sleep(2)

        # Verify file processed exactly once
        from apps.catalog.models import File
        file_records = File.objects.filter(path=str(test_file))

        self.assertEqual(file_records.count(), 1)
        self.assertEqual(file_records.first().processing_status, 'completed')

        # Cleanup
        file_monitor.stop()
        queue_processor.stop()
        test_file.unlink()
```

**Acceptance Criteria**:
- [ ] File discovered by monitor
- [ ] File processed by queue processor
- [ ] No duplicate processing
- [ ] Status transitions: discovered → queued → processing → completed

---

## Unit Testing

### Target Coverage

**Overall Target**: 60%+ (aspirational for MVP)
**Critical Path Target**: 80%+

**Critical Paths**:
1. File scanning service
2. Batch processing orchestration
3. FFmpeg integration
4. Database models (CRUD)
5. API endpoints (schema management)

### Test Organization

```
apps/
├── schemas/
│   └── tests/
│       ├── test_models.py         # Schema, InputDir, OutputDir models
│       ├── test_views.py          # Schema CRUD views
│       └── test_serializers.py    # API serializers
├── catalog/
│   └── tests/
│       ├── test_models.py         # File model
│       └── test_services.py       # File scanning service
├── processing/
│   └── tests/
│       ├── test_ffmpeg.py         # FFmpeg detection, download
│       ├── test_batch.py          # Batch processing
│       ├── test_watchdogs.py      # Watchdog services
│       └── test_transformations.py # Media transformations
```

### Example Unit Tests

**File Model Test** (`apps/catalog/tests/test_models.py`):
```python
from django.test import TestCase
from apps.catalog.models import File

class FileModelTest(TestCase):
    def test_create_audio_file(self):
        """Test creating audio file with metadata."""
        audio_file = File.objects.create(
            path="media/audio/test.wav",
            filename="test.wav",
            media_type="audio",
            format="WAV",
            file_size=1024000,
            metadata={
                "sample_rate": 44100,
                "bit_depth": 16,
                "channels": 2,
                "duration": 5.5
            }
        )

        self.assertEqual(audio_file.media_type, "audio")
        self.assertEqual(audio_file.metadata['sample_rate'], 44100)
        self.assertTrue(audio_file.uid.startswith('#'))  # UID auto-generated

    def test_file_size_display(self):
        """Test human-readable file size formatting."""
        file = File.objects.create(
            path="test.wav",
            filename="test.wav",
            media_type="audio",
            file_size=1258291  # ~1.2 MB
        )

        self.assertEqual(file.file_size_display, "1.2 MB")
```

**FFmpeg Integration Test** (`apps/processing/tests/test_ffmpeg.py`):
```python
from django.test import TestCase
from apps.processing.services.ffmpeg_service import (
    detect_platform,
    get_ffmpeg_binary_path,
    verify_ffmpeg_installation
)

class FFmpegServiceTest(TestCase):
    def test_platform_detection(self):
        """Test OS platform detection."""
        platform = detect_platform()
        self.assertIn(platform, ['windows', 'macos', 'linux'])

    def test_ffmpeg_binary_path(self):
        """Test FFmpeg binary path resolution."""
        binary_path = get_ffmpeg_binary_path()
        self.assertTrue(binary_path.exists(), f"FFmpeg not found at {binary_path}")

    def test_ffmpeg_execution(self):
        """Test FFmpeg can execute."""
        self.assertTrue(verify_ffmpeg_installation())
```

---

## Test Execution

### Running Tests

**All Tests**:
```bash
pytest
```

**Specific App**:
```bash
pytest apps/schemas/tests/
```

**With Coverage**:
```bash
pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

**Parallel Execution** (faster):
```bash
pytest -n auto  # Auto-detect CPU cores
```

### Continuous Integration (Future)

**GitHub Actions Workflow** (`.github/workflows/tests.yml`):
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        run: pytest --cov=apps --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Test Data Management

### Factory Pattern (factory-boy)

**File Factory** (`apps/catalog/tests/factories.py`):
```python
import factory
from factory.django import DjangoModelFactory
from apps.catalog.models import File

class FileFactory(DjangoModelFactory):
    class Meta:
        model = File

    path = factory.Faker('file_path', extension='wav')
    filename = factory.LazyAttribute(lambda obj: obj.path.split('/')[-1])
    media_type = "audio"
    format = "WAV"
    file_size = factory.Faker('random_int', min=100000, max=10000000)
    metadata = {
        "sample_rate": 44100,
        "bit_depth": 16,
        "channels": 2,
        "duration": 5.0
    }

# Usage in tests
def test_something():
    audio_file = FileFactory(media_type='audio')
    video_file = FileFactory(media_type='video', format='MP4')
```

---

## Workflow Validation Report Template

### Template: `docs/testing/workflow-validation-report.md`

```markdown
# Workflow Validation Report

**Date**: YYYY-MM-DD
**Tester**: Name
**Workflow**: [Music Production / Video Organization / Photo Export]

## Test Configuration

**Schema Name**: [Name]
**Input Directory**: [Path]
**Output Directories**: [List paths]

## Test Results

### File Routing

| Input File | Expected Output | Actual Output | Status |
|------------|-----------------|---------------|--------|
| kick_01.wav | output/kicks/ | output/kicks/ | ✅ PASS |
| snare_01.wav | output/snares/ | output/snares/ | ✅ PASS |

### Processing Verification

| File | Expected Format | Actual Format | Expected SR | Actual SR | Status |
|------|-----------------|---------------|-------------|-----------|--------|
| kick_01.wav | WAV 44.1kHz 24bit | WAV 44.1kHz 24bit | 44100 | 44100 | ✅ PASS |

### Source Media Integrity

- [ ] All source files unchanged (checksum verified)
- [ ] No files deleted from /media/
- [ ] No files modified in /media/

## Performance

- **CPU Utilization**: [X]% (target: 50-70%)
- **Processing Time**: [X] seconds for [Y] files
- **Memory Usage**: [X] MB

## Issues / Ambiguities

### Issue 1: [Description]
**Expected**: [What you expected]
**Actual**: [What happened]
**Questions for Project Director**:
1. [Question 1]
2. [Question 2]

**Recommendation**: [Suggested resolution]

## Conclusion

- [ ] Workflow performs as expected
- [ ] Issues require clarification (see above)
- [ ] Spec updates required
```

---

## Elicitation Process (Ambiguity Resolution)

### When to Elicit

Elicit the project director when:
1. **Unexpected behavior** that doesn't match PRD/architecture docs
2. **Ambiguous specifications** discovered during testing
3. **Edge cases** not covered in documentation
4. **Performance deviations** beyond acceptable ranges

### Elicitation Template

**Subject**: Clarification Needed - [Workflow/Feature]

**Context**: Testing [specific workflow] with [test files]

**Observation**: [What you observed]

**Expected Behavior (per docs)**: [Reference PRD/architecture section]

**Actual Behavior**: [What happened]

**Question**:
1. Is this the intended behavior?
2. If not, what should the correct behavior be?
3. Should we update the specification?

**Impact**: [High/Medium/Low] - blocks [X stories/features]

**Proposed Solution** (if applicable): [Your recommendation]

---

## Related Documents

- **[Tech Stack](./tech-stack.md)** - Testing dependencies (pytest, factory-boy)
- **[Coding Standards](./coding-standards.md)** - Test naming conventions
- **[Database Schema](./database-schema-design.md)** - Model validation
- **[Documentation Assessment](../documentation-assessment.md)** - Known gaps

---

## Version History

- **1.0** (2025-10-04): Initial testing strategy
  - Test media library structure (`/media/` folder)
  - Workflow validation scenarios (music, video, photo)
  - Algorithm preservation methodology (CR1/CR2)
  - Unit and integration test approach
  - Elicitation process for ambiguity resolution
