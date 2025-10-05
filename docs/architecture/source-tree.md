# Source Tree and Module Organization

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
