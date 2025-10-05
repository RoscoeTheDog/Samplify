# Technical Debt and Known Issues

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
