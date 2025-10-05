# Integration Points and External Dependencies

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
