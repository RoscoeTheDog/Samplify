# Summary for Django Migration

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
