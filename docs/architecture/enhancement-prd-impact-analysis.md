# Enhancement PRD Impact Analysis

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
