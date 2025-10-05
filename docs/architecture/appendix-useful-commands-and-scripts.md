# Appendix - Useful Commands and Scripts

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
