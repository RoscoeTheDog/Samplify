# Samplify Media Test Library
## Comprehensive Testing Resources for MVP & Phase 2

---

## 📁 DIRECTORY STRUCTURE

```
media/
├── README.md                              # This file
├── download_chaos_packs.py                # Automated audio download script
├── generate_synthetic_chaos.py            # Programmatic edge case generator
├── curated_pack_urls.md                   # Manual audio source catalog
├── phase2_video_image_sources.md          # Video/image sources for Phase 2
├── EDGE_CASES_AND_FILTERING_CHALLENGES.md # Comprehensive testing taxonomy
│
├── samples/                               # Organized production samples (30+ files)
│   ├── SAMPLE_CATALOG.md                  # Metadata catalog
│   └── samples_metadata.json              # Rich metadata for testing
│
├── [existing test files]                  # MP3, WAV, FLAC, OGG, M4A, MP4, WebM, OGV
│
├── raw_downloads/                         # Downloaded sample packs (gitignored)
├── synthetic_chaos/                       # Generated edge case files (gitignored)
└── test_output/                           # Processing test outputs (gitignored)
```

---

## 🎯 QUICK START

### Existing Test Files (140MB)

The repository includes **baseline test files** covering:
- **Audio formats:** MP3, WAV, FLAC, OGG, M4A, AAC (lossy + lossless)
- **Video formats:** MP4 (H.264), WebM (VP8/VP9), OGV (Theora)
- **Channel configs:** Mono, stereo, 5.1 surround, 7.1 surround
- **File sizes:** Small (<100KB), medium (100KB-5MB), large (>5MB)
- **Content types:** Music, voice, sound effects, static/noise

**Organized Sample Library:** `/samples/` subdirectory with 30+ production-ready samples featuring:
- Drums (808/909 kicks, snares, hi-hats)
- Instruments (piano, guitar, trumpet, saxophone, violin)
- Effects (vocals, noise samples)
- Rich metadata (tags, categories, sources, notes)

See below for existing file inventory.

---

### NEW: Chaos Testing Resources

#### 1. Generate Synthetic Edge Cases

```bash
# Generate all categories (~200 files, <100MB)
python media/generate_synthetic_chaos.py

# Generate specific categories
python media/generate_synthetic_chaos.py --categories format naming technical

# Custom output location
python media/generate_synthetic_chaos.py --output /custom/path
```

**Output:** `media/synthetic_chaos/` with edge case files for:
- Format diversity (8-bit to 32-bit, 8kHz to 192kHz)
- Naming chaos (unicode, special chars, extreme lengths)
- Technical challenges (silence, duration extremes, corruption)
- Organizational chaos (deep nesting, flat dumps, mixed content)
- Keyword filtering tests (exact, partial, case-sensitive variations)

---

#### 2. Download Curated Audio Packs

```bash
# Create download manifest
python media/download_chaos_packs.py --manifest

# Auto-download available packs
python media/download_chaos_packs.py --auto

# Custom output directory
python media/download_chaos_packs.py --auto --output /custom/path
```

**Output:** `media/raw_downloads/` with real-world chaotic sample packs

**Manual Downloads:** See `curated_pack_urls.md` for sources requiring browsing/accounts:
- Freesound.org (user-uploaded chaos)
- Archive.org (legacy formats)
- Bedroom Producers Blog (aggregated sources)
- 99Sounds (format diversity)
- BBC Sound Effects (metadata chaos)
- Loopmasters (producer-grade realism)

**Total Estimated Downloads:** 4-8GB

---

#### 3. Review Edge Case Documentation

Open `EDGE_CASES_AND_FILTERING_CHALLENGES.md` for:
- **100+ documented edge cases** with expected behaviors
- **Testing checklist** (Priority 1/2/3 validation)
- **Performance benchmarks** (throughput targets)
- **Validation workflows** (automated + manual)
- **Expected failure modes** (acceptable vs. unacceptable)

---

## 📚 EXISTING TEST FILE INVENTORY

### Audio Files

#### MP3 Files (Lossy)
- `bloibb.mp3` (23KB) - Short sound effect
- `doorbell.mp3` (193KB) - Doorbell sound
- `hal-9000.mp3` (18KB) - Voice sample
- `kalimba.mp3` (8.1MB) - Music sample
- `mpthreetest.mp3` (195KB) - Test audio file
- `static.mp3` (36KB) - Static/noise sample

#### WAV Files (Uncompressed PCM)
- `drip2.wav` (36KB) - Water drip sound effect
- `hal-9000.wav` (242KB) - Voice sample (uncompressed)
- `kalimba.wav` (30MB) - Music sample (high quality uncompressed)

#### FLAC Files (Lossless)
- `drippy.flac` (25KB) - Water drip sound effect
- `sample.flac` (67MB) - Large lossless audio sample
- `stereo.flac` (95KB) - Stereo channel test
- `surround51.flac` (311KB) - 5.1 surround sound test
- `surround71.flac` (418KB) - 7.1 surround sound test

#### OGG Files (Ogg Vorbis)
- `drips2.ogg` (66KB) - Water drip sound effect
- `mpthreetest.ogg` (111KB) - Test audio file

#### M4A/AAC Files
- `sample.m4a` (46KB) - AAC encoded audio
- `sample2.m4a` (3.2MB) - AAC encoded audio (larger)
- `sample.aac` (1.1MB) - Raw AAC stream

---

### Video Files

#### MP4 Files
- `big_buck_bunny.mp4` (5.3MB) - H.264 video sample
- `lion.mp4` (11MB) - Video test sample

#### WebM Files
- `echo-hereweare.webm` (3.3MB) - VP8/VP9 video sample
- `lion.webm` (3.4MB) - WebM video test sample

#### OGV Files (Ogg Video)
- `lion.ogv` (5.0MB) - Theora video test sample

---

### Organized Sample Library (`/samples/`)

**30+ production samples** with rich metadata for testing advanced features:

#### Drums
- 808/909 kicks, snares, hi-hats with descriptive labels

#### Instruments
- Piano, guitar, trumpet, saxophone, violin (note-labeled)

#### Effects
- Sound effects, vocals, noise samples

**See:** `samples/SAMPLE_CATALOG.md` and `samples/samples_metadata.json` for:
- Keyword search testing (tags, categories, sources)
- Multi-filter combinations (format + type + note)
- Dependency-driven UI filters (category → type → variant)
- Metadata-based operations

---

## 🧪 COMPREHENSIVE TEST COVERAGE

### Baseline Coverage (Existing Files)

| Category | Coverage |
|----------|----------|
| **Lossy Audio** | MP3, AAC, Ogg Vorbis |
| **Lossless Audio** | FLAC, WAV (PCM) |
| **Video** | MP4 (H.264), WebM (VP8/VP9), OGV (Theora) |
| **File Sizes** | Small (<100KB), Medium (100KB-5MB), Large (>5MB) |
| **Channels** | Mono, Stereo, 5.1 Surround, 7.1 Surround |
| **Content Types** | Music, Voice/Speech, Sound Effects, Static/Noise, Video |

---

### NEW: Chaos Testing Coverage

#### Synthetic Edge Cases (`synthetic_chaos/`)

| Category | Files | Edge Cases |
|----------|-------|------------|
| **1. Format Chaos** | 7+ | 8-bit to 32-bit, 8kHz to 192kHz, mono/stereo |
| **2. Naming Chaos** | 30+ | Unicode, special chars, whitespace, case sensitivity, extreme lengths |
| **3. Technical Chaos** | 8+ | Leading/trailing silence, duration extremes, corruption, mismatched extensions |
| **4. Organizational Chaos** | 100+ | Deep nesting, flat dumps, mixed audio/non-audio |
| **5. Keyword Filters** | 25+ | Exact/partial matches, case variations, misspellings, multiple keywords |

**Total:** ~200 files, <100MB

---

#### Curated Downloads (`raw_downloads/`)

| Source | File Count | Size | Edge Cases |
|--------|-----------|------|------------|
| **Freesound** | 10-15 packs | 1-2GB | User chaos, mixed formats |
| **Archive.org** | 2-3 collections | 500MB-1GB | Legacy codecs, μ-law, ADPCM |
| **BPB** | 3-5 packs | 500MB-1GB | Zero consistency, aggregated sources |
| **99Sounds** | 5 packs | 200-500MB | Format diversity, lo-fi character |
| **BBC SFX** | 50-100 samples | 500MB-1GB | Metadata chaos, long filenames |
| **Loopmasters** | Varies | 500MB-1GB | Generic naming, duplicate names |

**Total:** 4-8GB for comprehensive real-world testing

---

### Phase 2: Video/Image Coverage

See `phase2_video_image_sources.md` for:

#### Video Sources (5-10GB estimated)
- **Kodi Samples:** H.264, HEVC, VP9, AV1, legacy (AVI, WMV, FLV)
- **Jellyfin:** SDR/HDR, 4K/8K, multiple codecs
- **Stock footage:** Pixabay, Pexels, Videvo (organizational chaos)

#### Image Sources (3-5GB estimated)
- **Modern formats:** JPEG, PNG, WebP, AVIF, HEIC
- **RAW formats:** CR2, NEF, ARW, DNG
- **Stock photos:** Openverse, Unsplash, Pixabay (metadata chaos)

---

## 🛠️ TESTING WORKFLOWS

### 1. Baseline Functionality Testing (Existing Files)

```bash
# Test basic format conversion
python manage.py process_batch \
  --input media/ \
  --schema baseline_test \
  --output media/test_output/baseline

# Test multichannel audio
python manage.py process_file media/surround71.flac --output test_output

# Test video audio extraction (Phase 2)
python manage.py process_file media/big_buck_bunny.mp4 --extract-audio
```

**Expected:** All existing files process successfully, basic format conversion works

---

### 2. Edge Case Validation (Synthetic Chaos)

```bash
# Generate synthetic edge cases
python media/generate_synthetic_chaos.py

# Process all categories
python manage.py process_batch \
  --input media/synthetic_chaos \
  --schema edge_case_test \
  --output media/test_output/synthetic

# Validate results
python manage.py validate_database
cat .ai/debug-log.md | grep -E "ERROR|WARNING"
```

**Expected:** Priority 1 edge cases pass (see `EDGE_CASES_AND_FILTERING_CHALLENGES.md`)

---

### 3. Real-World Chaos Testing (Downloaded Packs)

```bash
# Download curated packs
python media/download_chaos_packs.py --auto

# Process downloaded chaos
python manage.py process_batch \
  --input media/raw_downloads \
  --schema real_world_test \
  --output media/test_output/real_world

# Watch mode testing
python manage.py watch \
  --input media/raw_downloads/watch_test \
  --schema watch_mode_test
```

**Expected:** 90%+ success rate, graceful handling of corrupt/unsupported files

---

### 4. Performance Benchmarking

```bash
# 1GB test set throughput
python media/benchmark_processing.py \
  --files 1000 \
  --format wav \
  --cores 4

# Expected metrics:
# - 60+ files/minute for 1MB WAVs
# - 50-70% CPU utilization (4-core)
# - <500MB memory usage for 1000-file queue
```

---

## 📊 USE CASES FOR TESTING

### Existing Files

1. **Codec Conversion:** Test conversion between MP3, WAV, FLAC, OGG, AAC
2. **Quality Testing:** Compare lossy vs. lossless compression
3. **Volume Normalization:** Various volume levels for normalization testing
4. **Multichannel Audio:** Surround sound processing (5.1, 7.1)
5. **Format Compatibility:** Verify support for different containers
6. **Noise Detection:** Static samples for noise gate testing
7. **Video Processing:** Audio extraction from video files (Phase 2)

---

### Chaos Testing

1. **Silence Detection/Trimming:** Leading/trailing silence edge cases
2. **Filename Sanitization:** Unicode, special chars, extreme lengths
3. **Format Auto-Detection:** Mismatched extensions, magic byte parsing
4. **Keyword Filtering:** Case-insensitive substring matching
5. **Corrupt File Handling:** Zero-byte, malformed headers
6. **Organizational Intelligence:** Flat dumps, deep nesting, mixed content
7. **Multiprocessing Stability:** Large batches, database concurrency
8. **Watch Mode Reliability:** Rapid file creation, file locking

---

## 📋 VALIDATION CHECKLIST

### Priority 1: Critical Edge Cases (Must Pass)

- [ ] **Silence Trimming:** Leading, trailing, both, only-silence
- [ ] **Format Conversion:** 8-bit to 24-bit, MP3 to WAV, FLAC to WAV
- [ ] **Unicode Filenames:** Japanese, Arabic, Cyrillic, emoji
- [ ] **Keyword Filtering:** Exact, partial, case-insensitive, multiple matches
- [ ] **Multiprocessing:** 100+ files, no crashes, no database locks
- [ ] **Watch Mode:** File creation, modification, deletion detection
- [ ] **Corrupt Files:** Zero-byte, malformed headers, mismatched extensions
- [ ] **Path Length:** Windows MAX_PATH (260 chars), long filenames

### Priority 2: Important Edge Cases (Should Pass)

- [ ] **Sample Rate Conversion:** 8kHz to 192kHz range
- [ ] **Bit Depth Conversion:** 8/16/24/32-bit with dithering
- [ ] **Exotic Codecs:** ADPCM, μ-law, AIFF-C, OGG Vorbis
- [ ] **Special Characters:** `&!@#$%` in filenames
- [ ] **Deep Nesting:** 10+ directory levels
- [ ] **Flat Dumps:** 1000+ files in one folder
- [ ] **Duplicate Names:** Same filename in different folders
- [ ] **Duration Extremes:** <50ms, 30+ seconds
- [ ] **Normalization:** Quiet, loud, already-normalized audio

See `EDGE_CASES_AND_FILTERING_CHALLENGES.md` for complete checklist.

---

## 🔧 TROUBLESHOOTING

### Issue: "Unsupported format" errors for WAV files

**Cause:** Corrupt headers or exotic WAV variants
**Solution:** Validate with `ffprobe`, regenerate test file if needed

---

### Issue: SQLite database locks during multiprocessing

**Cause:** WAL mode not enabled
**Solution:** Check Django settings for `DATABASES['default']['OPTIONS']`

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'init_command': 'PRAGMA journal_mode=WAL;',
        }
    }
}
```

---

### Issue: Unicode filenames corrupted on Windows

**Cause:** Non-UTF-8 filesystem encoding
**Solution:** Use `pathlib.Path` throughout, ensure UTF-8 encoding

---

### Issue: Memory usage spikes during large batch

**Cause:** Loading entire files into memory
**Solution:** Stream processing with ffmpeg, don't read entire file contents

---

## 📝 SOURCES & LICENSING

### Existing Test Files

Files collected from public domain and creative commons sources:
- Internet Archive (archive.org)
- GitHub test repositories
- Public domain audio samples
- Creative Commons licensed content

**License:** Public domain / CC0 where applicable

---

### Chaos Testing Resources

- **Synthetic files:** Generated programmatically, public domain (CC0)
- **Downloaded packs:** Check individual source licenses in `curated_pack_urls.md`
  - Freesound.org: CC0, CC-BY (varies by pack)
  - Archive.org: Public domain, CC licenses
  - 99Sounds: Free for personal/commercial use
  - BBC SFX: BBC license (free for research/development)
  - Loopmasters: Free tier with restrictions
- **Scripts (`.py` files):** Same license as Samplify project

**Important:** Verify individual licenses before commercial use

---

## 🔗 RELATED DOCUMENTATION

- **Project Brief:** `docs/brief.md`
- **PRD:** `docs/prd.md`
- **Architecture:** `docs/architecture.md`
- **Coding Standards:** `docs/architecture/coding-standards.md`
- **Curated Audio URLs:** `media/curated_pack_urls.md`
- **Phase 2 Video/Image:** `media/phase2_video_image_sources.md`
- **Edge Cases:** `media/EDGE_CASES_AND_FILTERING_CHALLENGES.md`

---

## 📧 CONTRIBUTION GUIDELINES

### Adding New Test Sources

1. Research source for edge case coverage
2. Add to `curated_pack_urls.md` or `phase2_video_image_sources.md`
3. Update download scripts if direct-link available
4. Document edge cases in `EDGE_CASES_AND_FILTERING_CHALLENGES.md`
5. Update this README with new source

---

### Creating New Synthetic Edge Cases

1. Identify edge case not covered by existing tests
2. Add generation code to `generate_synthetic_chaos.py`
3. Document expected behavior in `EDGE_CASES_AND_FILTERING_CHALLENGES.md`
4. Update test matrix checklist

---

## 📜 SUMMARY

| Test Resource | Files | Size | Purpose |
|---------------|-------|------|---------|
| **Existing baseline** | 30+ | 140MB | Format compatibility, basic functionality |
| **Organized samples** | 30+ | Included | Metadata testing, keyword filtering |
| **Synthetic chaos** | ~200 | <100MB | Edge case validation |
| **Curated downloads** | Varies | 4-8GB | Real-world chaos, diverse formats |
| **Phase 2 (future)** | TBD | 8-15GB | Video/image expansion testing |

**Total Current:** ~8-9GB (baseline + synthetic + downloads)
**Total Phase 2:** 16-24GB (includes video/image)

---

*Last Updated: 2025-10-04*
*Media Library Version: 2.0*
*Status: MVP Audio Testing Complete, Phase 2 Video/Image Documented*
