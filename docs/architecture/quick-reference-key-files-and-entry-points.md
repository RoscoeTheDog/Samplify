# Quick Reference - Key Files and Entry Points

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
