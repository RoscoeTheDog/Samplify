# Requirements

### Functional Requirements

**FR1**: The system shall provide a browser-based UI for creating and managing processing schemas, replacing the current XML template configuration system, with no login or authentication required

**FR2**: The system shall scan input directories on user request via "Scan" button and populate the database with file metadata (format, bit depth, sample rate, codec) using ffmpeg analysis

**FR3**: The system shall display input directory structures in an interactive tree viewer, pulling data from the database with file counts and technical attributes

**FR4**: The system shall allow users to define output directory mappings with filters based on keywords, file types, and media attributes through the web UI

**FR5**: The system shall support batch processing mode where users can select input folders, preview planned transformations, and execute processing with real-time progress monitoring

**FR6**: The system shall run watch mode as a Django management command (`python manage.py watch`) that monitors input directories and automatically processes new files according to active schemas

**FR7**: The system shall verify ffmpeg availability BEFORE any media operations, automatically detecting OS type and checking for ffmpeg binary in project directory (`/bin/<platform>/`), downloading and installing platform-specific ffmpeg from specified trusted sources if not present, with clear error messages and manual installation instructions if automatic download fails

**FR8**: The system shall preserve ALL existing search, filtering, and dispatch algorithms from `handlers/rules.py` and `__main__.py` (lines 206-469) with minimal modifications only for Django architecture remapping

**FR9**: The system shall maintain existing multiprocessing orchestration patterns from `handlers/process_handler.py` including worker scheduling, deque-based job distribution, and core allocation logic

**FR10**: The system shall catalog all processed files in SQLite database using Django ORM with single-table inheritance (one File model with media_type discriminator field) to eliminate redundant table creation

**FR11**: The system shall provide AJAX-based real-time status updates during batch processing, polling Django JSON endpoints for progress metrics without requiring page refresh

**FR12**: The system shall save and load schema configurations from the database, allowing users to create reusable processing templates

**FR13**: The system shall automatically update database entries (add/edit/remove) as files change in watched input directories during watch mode operation

**FR14**: The system shall migrate all existing structlog statements to the custom Loguru fork syntax, preserving hierarchical logging style, global exception handling, and brief contextual messages

**FR15**: The system shall provide a single-point-of-entry setup script (`setup.py` or similar) that executes all installation and configuration tasks, enabling clone-to-run deployment on fresh systems

**FR16**: The setup script shall check and install all requirements from `requirements.txt`, detect/download platform-specific ffmpeg binaries, verify all configuration prerequisites, and report any issues with actionable error messages

**FR17**: The system shall maintain a clean git repository with `.gitignore` configured to exclude all binaries, downloaded files, virtual environments, and temporary artifacts generated during installation or runtime

### Non-Functional Requirements

**NFR1**: The system shall utilize the existing optimized multiprocessing worker pool pattern (one worker per CPU core, deque-based distribution) to achieve 50-70% CPU utilization during batch operations, preserving proven performance characteristics

**NFR2**: The system shall configure SQLite in WAL (Write-Ahead Logging) mode to support concurrent database access from Django web server, batch processing workers, and watch mode service

**NFR3**: The system shall serve all JavaScript libraries and CSS from Django static files (no CDN dependencies), ensuring fully local operation without internet connectivity

**NFR4**: The system shall use Django templates with progressive enhancement for batch processing UI - static HTML fallback with JavaScript-enhanced AJAX polling (1-2 second intervals) for real-time progress updates

**NFR5**: The system shall define all service configurations (Loguru logging, ffmpeg paths, database settings) in Django `settings.py` module for centralized configuration management

**NFR6**: The system shall implement cross-platform path handling using `pathlib.Path` throughout the codebase, supporting Windows, macOS, and Linux deployments

**NFR7**: The system shall configure the custom Loguru fork in `settings.py` with hierarchical logging, global exception handling, brief contextual messages, and IDE-clickable file links in tracebacks

**NFR8**: The system shall maintain existing GPU acceleration hints (NVIDIA/AMD detection) for future hardware-accelerated encoding support

**NFR9**: The system shall process files with 95%+ success rate for common audio formats (WAV, MP3, FLAC, AIFF), matching existing script reliability

**NFR10**: The watch mode file detection (via watchdog library) shall detect new files with <10 seconds latency from file arrival to processing start, independent of UI update frequency

**NFR11**: The setup script shall enable true clone-to-run deployment requiring only Python 3.10+ and git as prerequisites, with all other dependencies installed automatically

**NFR12**: The system shall use single-table inheritance (one File model with media_type discriminator) to eliminate redundant table creation and improve ORM maintainability

**NFR13**: The system shall disable Django's authentication middleware and user management entirely, operating as an open local web interface without login features, while maintaining CSRF protection

### Compatibility Requirements

**CR1: Processing Algorithm Preservation**: The Django implementation MUST retain ALL search, filtering, and dispatch algorithms from the brownfield codebase (`handlers/rules.py`, `__main__.py` lines 206-469) exactly as-is for the first prototype. **Allowed modifications**: import statement changes (SQLAlchemy → Django ORM), method signature adaptations for Django patterns, variable renaming for Django conventions. **Prohibited modifications**: algorithm logic changes, flow control changes, performance optimizations, code restructuring

**CR2: Multiprocessing Orchestration**: The system MUST preserve the existing multiprocessing orchestration patterns including worker scheduling logic (`process_handler.py` lines 26-48), deque-based job queues, and performance characteristics that have been extensively optimized

**CR3: ORM Migration with Single-Table Inheritance**: The system must migrate from SQLAlchemy to Django ORM using single-table inheritance (one File model with media_type field) to consolidate redundant models (FilesVideo/Audio/Image), while preserving all metadata fields from the brownfield schema

**CR4: Schema Functionality**: The new web-based schema configuration must support all rule types from the existing XML template system (keyword filters, file type filters, output transformations, AND/OR logic governors from `xml_handler.py`)

**CR5: Loguru Migration**: The system must provide a complete migration strategy from structlog to the custom Loguru fork, including syntax conversion for all existing log statements in handlers, maintaining log output format and functionality

**CR6: FFmpeg Binary Management**: The system must support platform-specific ffmpeg binary detection (Windows/macOS/Linux), automatic download from trusted online sources, installation to project `/bin` directory, and programmatic path resolution - all without git repository bloat

### Development Workflow Requirements

**DW1: Branch Strategy**
- **master branch**: Stable production-ready code (current brownfield baseline)
- **dev branch**: Integration branch where all completed features merge
- **feature branches**: Individual feature branches (e.g., `feature/django-models`, `feature/web-ui`, `feature/batch-processing`) isolated for agent work

**DW2: Feature Sequencing and Dependency Management**
- Features must be sequenced to avoid circular dependencies (backend before frontend)
- Each feature branch should declare its backend/frontend dependencies in branch description

**DW3: Merge and Test Protocol**
- Feature branches merge to `dev` only when feature-complete
- `dev` branch runs full test suite on each merge
- If tests fail due to missing dependencies: document failure, prioritize dependent feature next
- Only merge `dev` → `master` when all features stable and tests pass

**DW4: Controlled Development Propagation**
- Feature isolation prevents breaking changes from affecting other work
- `dev` serves as integration testing environment
- `master` remains stable baseline for new feature branches

**DW5: Dependency-Aware Sequencing**
- Backend architecture changes must merge before frontend features that depend on them
- Shared utilities/services merge before features that consume them
- Database migrations must be backward-compatible or sequenced correctly

---
