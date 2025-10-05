# Samplify Brownfield Architecture Document

## Introduction

This document captures the **CURRENT STATE** of the Samplify codebase, including technical debt, workarounds, and real-world patterns. It serves as a reference for AI agents working on the planned Django web UI modernization enhancement.

### Document Scope

**Focused on areas relevant to:** Modernizing from Python script to Django-based web application with self-contained architecture, multiprocessing batch operations, and file watching capabilities.

### Change Log

| Date       | Version | Description                  | Author |
| ---------- | ------- | ---------------------------- | ------ |
| 2025-10-03 | 1.0     | Initial brownfield analysis  | PM     |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

- **Main Entry**: `__main__.py` (application bootstrap and orchestration)
- **Configuration**: `app/environment.py` (paths, database config), `app/settings.py` (runtime settings)
- **Database Models**: `database/database_setup.py` (SQLAlchemy ORM models)
- **Core Business Logic**: `handlers/` directory (all processing logic)
- **XML Template System**: `handlers/xml_handler.py` (schema configuration parser)
- **Media Processing**: `handlers/av_handler.py` (ffmpeg integration), `handlers/image_handler.py` (PIL integration)
- **File Watching**: `handlers/watch_handler.py` (watchdog library integration)
- **Multiprocessing**: `handlers/process_handler.py` (worker pool management)
- **Logging**: `app/logging/` (custom structlog configuration)

### Enhancement Impact Areas

**Files that will be affected by Django modernization:**

- `__main__.py` - Will be replaced by Django project structure (`manage.py`, settings, etc.)
- `app/environment.py` - Configuration will migrate to Django settings
- `database/database_setup.py` - SQLAlchemy models will migrate to Django ORM models
- `handlers/*_handler.py` - Business logic will be refactored into Django apps/services
- XML template system - Will be replaced by database-backed schema configuration with web UI

**New Django structure will need:**
- Django project scaffold (`samplify/` project, `apps/` for Django apps)
- Web UI for schema configuration (replaces XML templates)
- Django management commands for batch processing and watch mode
- Static files for frontend (minimal JavaScript, locally served)
- Database migration from SQLAlchemy to Django ORM

## High Level Architecture

### Technical Summary

Samplify is currently a **Python-based CLI script** that processes media files (audio, video, images) based on XML-defined templates. It uses:

- **Multiprocessing** for parallel media conversion
- **Watchdog** for file system monitoring
- **FFmpeg** (via subprocess) for audio/video processing
- **PIL** for image processing
- **SQLAlchemy** for database ORM
- **SQLite** for data persistence
- **Structlog** for structured logging

The architecture is **brownfield script-based** with manual orchestration in `__main__.py`. There is **no web interface** - all configuration is done via XML files stored in user documents folder.

### Actual Tech Stack

| Category           | Technology     | Version         | Notes                                           |
| ------------------ | -------------- | --------------- | ----------------------------------------------- |
| Runtime            | Python         | 3.x (inferred)  | No explicit version constraint found            |
| Database           | SQLite         | N/A             | Via SQLAlchemy, database file in `/database/`  |
| ORM                | SQLAlchemy     | Unknown version | Used for all database operations                |
| Logging            | Structlog      | Unknown version | Custom processors and console renderer          |
| Media Processing   | FFmpeg         | External binary | Via subprocess calls, not bundled               |
| Image Processing   | PIL            | Unknown version | For image format conversions                    |
| File Watching      | Watchdog       | Unknown version | For real-time input directory monitoring        |
| Multiprocessing    | Python stdlib  | Built-in        | Using `multiprocessing.Process` and `deque`     |
| XML Parsing        | ElementTree    | Built-in        | For template configuration parsing              |
| GPU Detection      | WMIC (Windows) | System tool     | Windows-specific GPU vendor detection           |
| **Missing**        | Requirements   | **NONE FOUND**  | ⚠️ No requirements.txt or dependency management |

### Repository Structure Reality Check

- **Type**: Single Python project (not Django, not web-based)
- **Package Manager**: None detected (no requirements.txt, setup.py, or pyproject.toml found)
- **Notable**: User data stored in `%USERPROFILE%\Documents\Samplify` (not in project directory)

## Source Tree and Module Organization

### Project Structure (Actual)

```text
Samplify/
├── __main__.py              # Entry point - orchestrates application initialization
├── app/                     # Application configuration and utilities
│   ├── environment.py       # Paths, database config, environment setup
│   ├── settings.py          # Runtime settings (minimal - 9 lines)
│   ├── gpu.py              # GPU vendor detection (NVIDIA/AMD/Intel)
│   ├── platform.py         # Platform detection utilities
│   ├── logging/            # Custom structlog configuration
│   │   ├── custom_console_renderer.py
│   │   └── custom_processors.py
├── database/                # Database layer
│   ├── database_setup.py   # SQLAlchemy models and engine config
│   └── database.db         # SQLite database file (recreated on each run - dev mode)
├── handlers/                # Business logic handlers
│   ├── av_handler.py       # Audio/video processing with ffmpeg
│   ├── database_handler.py # Database operations wrapper
│   ├── file_handler.py     # File scanning and validation
│   ├── image_handler.py    # Image processing with PIL
│   ├── process_handler.py  # Multiprocessing worker pool
│   ├── thread_handler.py   # Threading utilities
│   ├── watch_handler.py    # File watching with watchdog
│   ├── xml_handler.py      # XML template parsing
│   ├── rules.py            # Processing rule evaluation logic
│   └── date_handler.py     # Date/time utilities
├── gui/                     # (Empty - future GUI placeholder)
├── tests/                   # Test files
│   └── template.xml        # Example XML template for testing
└── docs/                    # Documentation
    └── brief.md            # Comprehensive project brief
```

**User Data Location** (created at runtime):
```text
%USERPROFILE%\Documents\Samplify/
├── Input/          # Watched input directories
├── Output/         # Processed file destinations
└── Templates/      # XML configuration templates
```

### Key Modules and Their Purpose

- **Application Bootstrap** (`__main__.py`):
  - Initializes logging with custom structlog config
  - Creates user environment directories
  - Detects GPU for hardware acceleration hints
  - **⚠️ Drops and recreates database on every run** (development mode)
  - Initializes handler chain: template → thread → process → database → watch → file managers
  - Validates output directories from XML template
  - Caches input/output tree structures for watchdog
  - Schedules multiprocessing workers
  - Runs one-time batch processing (no server/UI)

- **Environment Management** (`app/environment.py`):
  - Hardcoded install path: `C:\Program Files\Samplify` (not used)
  - Database path: `sqlite:///database/database.db`
  - User environment: `%USERPROFILE%\Documents\Samplify`
  - Creates directory structure on first run

- **Database Layer** (`database/database_setup.py`):
  - SQLAlchemy declarative base with multiple models
  - **⚠️ Case-sensitive LIKE pragma enabled** via SQLite event listener
  - Models: `Files`, `FilesVideo`, `FilesAudio`, `FilesImage`, `OutputDirectories`, `InputDirectories`, `SearchTerms`, `SupportedExtensions`, `UnsupportedExtensions`, `SearchByDate`, `InputMonitoringExclusions`
  - Single global session (not thread-safe)

- **Processing Handlers**:
  - **process_handler.py**: Spawns worker processes (one per CPU core), uses `collections.deque` for job queues
  - **watch_handler.py**: Watchdog-based file monitoring with manual directory tree caching
  - **xml_handler.py**: Parses XML templates into processing rules, creates default template if missing
  - **av_handler.py**: FFmpeg subprocess calls for audio/video conversion
  - **image_handler.py**: PIL-based image processing
  - **rules.py**: Complex rule evaluation (AND/OR logic for filters)

- **Logging System** (`app/logging/`):
  - Custom structlog processors with timestamping
  - Custom console renderer (replaces default structlog renderer)
  - JSON output to `samplify.log` file
  - Colored console output with structured fields

## Data Models and APIs

### Data Models

**Primary Models** (see `database/database_setup.py`):

- **Files** (line 93): Universal file registry with video/audio/image metadata
  - Stores: path, name, extension, creation date
  - Video fields: width, height, duration, frame_rate, pix_format
  - Audio fields: sample_rate, bit_depth, sample_fmt, bit_rate, channels, channel_layout
  - Image fields: format, frames, width, height, alpha, mode

- **FilesVideo/FilesAudio/FilesImage** (lines 124, 153, 172): Type-specific file tables (redundant with Files)

- **OutputDirectories** (line 44): Processing rules per output folder
  - Conversion settings: extensions, sample rates, bit depths, channels
  - Processing flags: normalize, strip_silence, video_only, audio_only, image_only

- **InputDirectories** (line 195): Watched directories with monitoring flag

- **SearchTerms** (line 85): Keyword filters linked to folders

**⚠️ Technical Debt**: Denormalized schema with redundant tables (Files vs. FilesVideo/Audio/Image)

### API Specifications

**No API exists** - this is a CLI script. XML templates act as configuration:

**XML Template Structure**:
```xml
<samplify>
    <name>templateName</name>
    <libraries>
        <directory path="C:\input\path"/>
    </libraries>
    <outputDirectories>
        <directory path="C:\output\kick">
            <rules>
                <expression>Kick</expression>
                <extensions>.wav</extensions>
                <containsAudio>true</containsAudio>
                <audioFormat>default</audioFormat>
                <audioSampleRate>44100</audioSampleRate>
                <audioNormalize>True</audioNormalize>
            </rules>
            <governor>
                <comparison>AND</comparison>  <!-- or OR -->
            </governor>
        </directory>
    </outputDirectories>
</samplify>
```

## Technical Debt and Known Issues

### Critical Technical Debt

1. **No Dependency Management**: No `requirements.txt`, `setup.py`, or `pyproject.toml` found
   - Cannot reproduce environment
   - Unknown package versions
   - **Impact**: Must reverse-engineer dependencies from imports

2. **Database Recreation on Every Run**: `__main__.py` line 37-38 drops and recreates all tables
   - **Development anti-pattern still in production code**
   - All data is lost on restart
   - **Impact**: Django migration will need to remove this behavior

3. **Denormalized Database Schema**: Separate tables for FilesVideo, FilesAudio, FilesImage duplicate Files table
   - Redundant data storage
   - Query complexity
   - **Impact**: Django models should consolidate into single polymorphic File model

4. **Hardcoded Paths**: `environment.py` line 13 has hardcoded `C:\Program Files\Samplify` (unused)
   - Windows-specific paths throughout
   - **Impact**: Django settings must be platform-agnostic

5. **XML Template System**: Configuration via XML files in user documents folder
   - No validation
   - No versioning
   - Manual editing required
   - **Impact**: Replace with database-backed schemas + web UI

6. **FFmpeg Not Bundled**: External dependency on system-installed ffmpeg
   - No path configuration
   - Relies on system PATH
   - **Impact**: Django version must bundle portable ffmpeg binary

7. **Single Global Database Session**: `database_setup.py` line 30-33 creates one session
   - Not thread-safe
   - Not process-safe
   - **Impact**: Django ORM handles this correctly, but need to verify multiprocessing compatibility with SQLite WAL mode

8. **GPU Detection Bug**: `gpu.py` line 39 - logic error in conditional
   - `if environment.gpu_vendor.lower() == 'nvidia' or 'amd':` always True (should be `in ['nvidia', 'amd']`)

### Workarounds and Gotchas

- **Manual Directory Caching**: `watch_handler.py` line 23-26 - Watchdog doesn't track folders recursively, so manual cache lists `input_cache` and `output_cache` are used
- **Unpicklable Objects**: `process_handler.py` and `watch_handler.py` have custom `__getstate__` methods to exclude session/process objects from pickling (for multiprocessing)
- **Case-Sensitive LIKE**: `database_setup.py` line 37-41 - SQLite LIKE made case-sensitive via pragma (non-standard)
- **Deque for Queues**: `process_handler.py` line 38 uses `collections.deque` instead of `multiprocessing.Queue` (may have been for pickling reasons)

## Integration Points and External Dependencies

### External Services/Tools

| Service/Tool | Purpose                  | Integration Type | Key Files                |
| ------------ | ------------------------ | ---------------- | ------------------------ |
| FFmpeg       | Audio/video conversion   | subprocess calls | `handlers/av_handler.py` |
| PIL          | Image processing         | Python library   | `handlers/image_handler.py` |
| Watchdog     | File system monitoring   | Python library   | `handlers/watch_handler.py` |
| WMIC         | GPU detection (Windows)  | subprocess call  | `app/gpu.py` line 20     |

### Internal Integration Points

- **Handler Chain**: `__main__.py` lines 41-46 creates dependent handler chain:
  1. `template_manager` (xml_handler)
  2. `thread_manager` (thread_handler) - depends on template_manager
  3. `process_manager` (process_handler)
  4. `db_manager` (database_handler) - depends on process_manager
  5. `watch_manager` (watch_handler) - depends on db_manager
  6. `file_manager` (file_handler) - depends on template_manager, process_manager, db_manager

- **Multiprocessing Communication**: Deque-based job queues (one per CPU core)

## Development and Deployment

### Local Development Setup

**Current State** (no formal setup):
1. Clone repository
2. ⚠️ **Unknown dependencies** - no requirements file
3. Ensure ffmpeg installed and in system PATH
4. Run `python __main__.py` (creates user directories and database automatically)

**Known Issues**:
- Database drops on every run (development mode still active)
- No virtual environment configuration
- Windows-only (hardcoded paths, WMIC dependency)

### Build and Deployment Process

**No build process exists** - this is a Python script

- **Deployment**: Manual copy (not packaged)
- **Environments**: Only local development
- **Configuration**: XML templates in `%USERPROFILE%\Documents\Samplify\Templates\`

## Testing Reality

### Current Test Coverage

- **Unit Tests**: None found
- **Integration Tests**: None found
- **Test Files**: Only `tests/template.xml` (sample XML, not automated test)
- **QA Method**: Manual execution

### Running Tests

No test framework configured. Only manual testing via:
```bash
python __main__.py
```

## Enhancement PRD Impact Analysis

### What Needs to Change for Django Modernization

**Core Architecture Changes:**

1. **Replace `__main__.py` with Django Project Structure**:
   - Create `manage.py`, `samplify/settings.py`, `samplify/urls.py`
   - Move initialization logic to Django app ready() hooks
   - Remove database drop behavior

2. **Migrate SQLAlchemy → Django ORM**:
   - Convert `database/database_setup.py` models to Django models
   - Consolidate FilesVideo/Audio/Image into single polymorphic File model
   - Configure SQLite WAL mode in Django settings for multiprocessing
   - Create initial migrations

3. **Refactor Handlers → Django Apps/Services**:
   - `handlers/xml_handler.py` → Django model-based schema configuration
   - `handlers/process_handler.py` → Django management command with multiprocessing
   - `handlers/watch_handler.py` → Django management command with threading
   - `handlers/av_handler.py` → Service layer (keep ffmpeg integration patterns)
   - `handlers/file_handler.py` → Service layer for file operations
   - `handlers/database_handler.py` → Replace with Django ORM queries

4. **Create Web UI**:
   - Django templates for schema configuration (replace XML)
   - AJAX polling for batch processing status
   - Database-backed tree viewer for input/output directories
   - Static files served locally (no CDN dependencies)

5. **Bundle Portable FFmpeg**:
   - Download platform-specific ffmpeg binaries
   - Store in `/bin` or `/vendor` directory
   - Programmatic path resolution using `pathlib.Path` (already partially used)
   - Update `av_handler.py` to use bundled binary instead of system PATH

6. **Virtual Environment & Dependencies**:
   - Create `requirements.txt` from current imports:
     - Django 4.2+
     - watchdog
     - Pillow (PIL)
     - structlog
     - Any others discovered during testing
   - Create venv setup documentation

### Files That Will Need Modification

**Direct Modifications** (existing files to adapt):
- `app/gpu.py` - Fix line 39 logic bug, make cross-platform
- `app/platform.py` - Ensure cross-platform compatibility
- `handlers/av_handler.py` - Update for bundled ffmpeg, preserve existing patterns
- `handlers/image_handler.py` - Minimal changes, integrate with Django
- `handlers/rules.py` - Refactor for Django model-based rules
- Custom logging (`app/logging/*`) - Integrate with Django logging framework

**To Be Replaced/Removed**:
- `__main__.py` → Delete (replaced by Django project)
- `app/environment.py` → Migrate to Django settings
- `app/settings.py` → Delete (too minimal)
- `database/database_setup.py` → Rewrite as Django models
- `handlers/xml_handler.py` → Delete (replaced by web UI)
- `handlers/database_handler.py` → Delete (use Django ORM directly)
- `handlers/thread_handler.py` → Evaluate if needed in Django context

### New Files/Modules Needed

**Django Project Structure**:
```
samplify/              # Django project
├── manage.py
├── samplify/
│   ├── settings.py    # Django settings (SQLite WAL mode, static files)
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── schemas/       # Schema configuration app
│   │   ├── models.py  # OutputDirectory, ProcessingRule, etc.
│   │   ├── views.py   # Schema CRUD, tree viewer
│   │   ├── forms.py   # Schema configuration forms
│   │   └── templates/ # Web UI templates
│   ├── processing/    # Batch processing app
│   │   ├── services/  # av_service, file_service (refactored handlers)
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── batch_process.py  # Multiprocessing command
│   │   │       └── watch.py          # File watching command
│   └── catalog/       # File cataloging app
│       ├── models.py  # File, FileMetadata
│       └── views.py   # API endpoints for status/progress
├── frontend/
│   ├── static/        # Locally served JS/CSS
│   └── templates/     # Base templates
├── bin/               # Portable ffmpeg binaries
│   ├── ffmpeg.exe     # Windows
│   ├── ffmpeg         # Linux
│   └── ffmpeg-mac     # macOS
└── requirements.txt   # Python dependencies
```

### Integration Considerations

**Preserving Existing Patterns**:
- ✅ Keep multiprocessing approach from `process_handler.py` (proven to work)
- ✅ Preserve ffmpeg subprocess patterns from `av_handler.py` (well-tested)
- ✅ Maintain structlog custom logging (integrate with Django logging)
- ✅ Keep watchdog file monitoring approach (move to Django management command)

**New Integration Requirements**:
- Must work with Django ORM (replace SQLAlchemy session management)
- Must handle concurrent database access (SQLite WAL mode)
- Must serve static files locally (no CDN)
- Must provide web-based schema configuration (replace XML)
- Must run background processes via Django management commands

**Critical Constraints**:
- Maintain backward compatibility with existing file processing logic
- Ensure multiprocessing works with SQLite (WAL mode required)
- Bundle all dependencies (portable ffmpeg, local static files)
- Support cross-platform deployment (pathlib.Path, not hardcoded Windows paths)

## Appendix - Useful Commands and Scripts

### Frequently Used Commands

**Current State** (pre-Django):
```bash
python __main__.py     # Run application (drops DB, processes files once)
```

**Post-Django Enhancement**:
```bash
python manage.py migrate              # Run database migrations
python manage.py runserver            # Start web UI
python manage.py batch_process        # Run batch processing
python manage.py watch                # Start file watching service
python manage.py scan_input           # Scan and populate database with input files
```

### Debugging and Troubleshooting

- **Logs**: `samplify.log` in project root (JSON format)
- **Console Output**: Colored structlog output with custom renderer
- **Database**: `database/database.db` (recreated on each run in current version)

**Common Issues**:
1. **FFmpeg not found**: Ensure ffmpeg in system PATH (pre-Django) or bundled in `/bin` (post-Django)
2. **Database locked**: Current version has no locking issues (single-threaded DB access), Django version must use WAL mode
3. **GPU detection fails**: Windows-only WMIC dependency, gracefully degrades if not available
4. **XML template errors**: No validation, manually check XML syntax

---

## Summary for Django Migration

**What Exists and Works Well**:
- FFmpeg integration patterns (preserve)
- Multiprocessing architecture (adapt to Django management commands)
- File watching with watchdog (move to Django command)
- Custom structured logging (integrate with Django)
- Database models capture all needed metadata (migrate to Django ORM)

**What Must Change**:
- CLI script → Django web application
- XML templates → Database-backed schemas with web UI
- SQLAlchemy → Django ORM
- Hardcoded paths → Platform-agnostic configuration
- External ffmpeg → Bundled portable binary
- No dependency management → requirements.txt + venv

**Critical Success Factors**:
1. Preserve proven ffmpeg and multiprocessing patterns
2. Ensure SQLite WAL mode for concurrent access
3. Bundle all dependencies (ffmpeg, static files)
4. Maintain cross-platform compatibility
5. Provide clear migration path from XML templates to web-based schemas
