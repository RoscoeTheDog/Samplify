# Samplify Django Modernization - Story Details
## Epic 1: Django Web UI Modernization

**Epic Goal**: Transform Samplify from Python CLI script to Django web application with browser-based schema designer, automated setup, and self-contained deployment - while preserving all existing algorithms and performance.

---

## Story 1.0: Repository & Environment Foundation

### User Story
As a **developer**,
I want **a properly configured development environment with dependency management**,
So that **I can clone the repository and start development without manual configuration**.

### Story Context
**Existing System Integration:**
- Integrates with: Current CLI codebase
- Technology: Python 3.10+, Git, pip/virtualenv
- Follows pattern: Standard Python project structure
- Touch points: Root directory structure, .gitignore, requirements management

### Acceptance Criteria

**1.0A: .gitignore Configuration**
1. `.gitignore` file excludes all binaries (`/bin/`, `*.exe`, `*.dll`, `*.so`)
2. `.gitignore` excludes virtual environments (`venv/`, `env/`, `.venv/`)
3. `.gitignore` excludes Python cache (`__pycache__/`, `*.pyc`, `*.pyo`)
4. `.gitignore` excludes Django artifacts (`db.sqlite3`, `*.log`, `/static/`, `/media/`)
5. `.gitignore` excludes IDE files (`.idea/`, `.vscode/`, `*.swp`)
6. `.gitignore` excludes downloaded dependencies and temporary files

**1.0B: Virtual Environment Setup**
1. Virtual environment creation script provided (`setup_env.sh` or `setup_env.bat`)
2. Virtual environment uses Python 3.10+ as base interpreter
3. Virtual environment activates correctly on Windows, macOS, and Linux
4. Documentation includes activation instructions for all platforms

**1.0C: requirements.txt Creation**
1. `requirements.txt` lists all Python dependencies with pinned versions
2. Core dependencies included:
   - Django 4.2+
   - Pillow (for image processing)
   - watchdog (for file monitoring)
   - pathlib (if not stdlib)
   - Custom Loguru fork (with installation instructions)
3. Dependencies install successfully via `pip install -r requirements.txt`
4. No missing or conflicting dependencies

### Technical Notes
- **Integration Approach:** Prepares foundation for Django migration without disrupting current CLI
- **Existing Pattern Reference:** Standard Python project layout
- **Key Constraints:** Must support Python 3.10+ on Windows/macOS/Linux

### Definition of Done
- [x] .gitignore configured and tested
- [x] Virtual environment scripts work on all platforms
- [x] requirements.txt complete and validated
- [x] Documentation updated with setup instructions
- [x] No binaries or virtual environments in git repository
- [x] **Coding Standards**: All code adheres to CS1-CS13 (see `docs/coding-standards.md`)
- [x] **Code Quality**: Black, Pylint (≥8.5), mypy, isort pass without errors
- [x] **Documentation**: All functions have Google-style docstrings with type hints

### Risk Assessment
- **Primary Risk:** Missing dependencies causing installation failures
- **Mitigation:** Test installation on clean systems (Windows/macOS/Linux)
- **Rollback:** Remove files, restore to current state

---

## Story 1.1: Django Project Setup & Configuration

### User Story
As a **developer**,
I want **a properly scaffolded Django project with static file serving**,
So that **I can build the web UI on a solid foundation**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.0 foundation
- Technology: Django 4.2+, Python 3.10+
- Follows pattern: Django best practices for project structure
- Touch points: Project root, settings.py, URLs, static files

### Acceptance Criteria

**Functional Requirements:**
1. Django project created with `manage.py` at root level
2. Project named `samplify` with proper `settings.py` configuration
3. Static files configured to serve from `/static/` directory
4. Base template structure created (`base.html` with blocks)
5. Static assets served locally (no CDN dependencies):
   - Bootstrap 5.3+ CSS/JS
   - jQuery 3.7+ (for AJAX)
   - Custom CSS for minimal design
6. Development server runs successfully on `localhost:8000`
7. Settings configured for local development (DEBUG=True, ALLOWED_HOSTS=['localhost', '127.0.0.1'])

**Integration Requirements:**
8. Authentication middleware DISABLED (NFR13: open local interface)
9. CSRF protection ENABLED (security requirement)
10. Static file finder configured for development and production modes

**Quality Requirements:**
11. `manage.py` commands execute without errors
12. Static files accessible at `/static/` path
13. Base template renders correctly
14. No Django startup warnings or errors

### Technical Notes
- **Integration Approach:** Clean Django scaffold, no authentication system
- **Existing Pattern Reference:** Django tutorial + NFR13 requirements
- **Key Constraints:** Self-contained (no CDN), local-only web interface

### Definition of Done
- [x] Django project scaffolded and runnable
- [x] Static files configured and serving
- [x] Base templates created
- [x] Development server verified on localhost:8000
- [x] Authentication disabled, CSRF enabled
- [x] Documentation updated with Django setup instructions

### Risk Assessment
- **Primary Risk:** Django configuration errors preventing startup
- **Mitigation:** Follow Django best practices, test thoroughly
- **Rollback:** Remove Django scaffold, restore to Story 1.0 state

---

## Story 1.2A: File Model (Single-Table Inheritance)

### User Story
As a **developer**,
I want **a unified File model with single-table inheritance for media types**,
So that **I can eliminate redundant tables and simplify the ORM migration from SQLAlchemy**.

### Story Context
**Existing System Integration:**
- Integrates with: SQLAlchemy models (FilesVideo, FilesAudio, FilesImage)
- Technology: Django ORM, SQLite with WAL mode
- Follows pattern: Django single-table inheritance (media_type discriminator)
- Touch points: Database schema, existing SQLAlchemy models

### Acceptance Criteria

**Functional Requirements:**
1. `File` model created with single-table inheritance using `media_type` field
2. `media_type` choices: 'audio', 'video', 'image'
3. All metadata fields preserved from SQLAlchemy schema:
   - `file_path` (CharField, max_length=500)
   - `file_name` (CharField, max_length=255)
   - `file_format` (CharField, max_length=50)
   - `sample_rate` (IntegerField, null=True, blank=True)
   - `bit_depth` (IntegerField, null=True, blank=True)
   - `codec` (CharField, max_length=50, null=True, blank=True)
   - `file_size` (BigIntegerField)
   - `created_at` (DateTimeField, auto_now_add=True)
   - `updated_at` (DateTimeField, auto_now=True)
   - `media_type` (CharField, choices=['audio', 'video', 'image'])
4. Model includes `__str__()` method returning filename
5. Model includes `get_absolute_path()` method using `pathlib.Path`

**Integration Requirements:**
6. Django migration created successfully
7. SQLite database created with WAL mode enabled (defer to Story 1.2C)
8. No redundant tables created (single `catalog_file` table)
9. ORM queries work correctly for filtering by media_type

**Quality Requirements:**
10. Migration applies without errors
11. Model admin interface works (for debugging)
12. Database queries execute efficiently
13. All fields nullable/required as per original schema

### Technical Notes
- **Integration Approach:** Consolidate FilesVideo/Audio/Image into single File model
- **Existing Pattern Reference:** NFR12 single-table inheritance requirement
- **Key Constraints:** Must preserve all metadata fields, eliminate redundant tables

### Definition of Done
- [x] File model implemented with media_type discriminator
- [x] All SQLAlchemy fields mapped to Django ORM
- [x] Migration created and applied successfully
- [x] Model registered in admin interface
- [x] Database schema validated (single table)
- [x] Documentation updated with model structure

### Risk Assessment
- **Primary Risk:** Data migration complexity from SQLAlchemy to Django ORM
- **Mitigation:** Create migration scripts, test with sample data
- **Rollback:** Drop Django migrations, restore SQLAlchemy models

---

## Story 1.2B: Schema Models

### User Story
As a **developer**,
I want **Django models for schema configuration storage**,
So that **I can replace XML templates with database-backed schemas**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2A (File model), existing XML template system
- Technology: Django ORM, SQLite
- Follows pattern: Django model relationships (ForeignKey, ManyToMany)
- Touch points: Schema storage, XML handler logic

### Acceptance Criteria

**Functional Requirements:**
1. `Schema` model created with fields:
   - `name` (CharField, max_length=255, unique=True)
   - `description` (TextField, null=True, blank=True)
   - `is_active` (BooleanField, default=False)
   - `created_at` (DateTimeField, auto_now_add=True)
   - `updated_at` (DateTimeField, auto_now=True)
2. `SchemaRule` model created with fields:
   - `schema` (ForeignKey to Schema, on_delete=CASCADE)
   - `rule_type` (CharField, choices=['keyword', 'extension', 'media_type', 'attribute'])
   - `rule_value` (CharField, max_length=500)
   - `logic_operator` (CharField, choices=['AND', 'OR'], default='AND')
   - `priority` (IntegerField, default=0)
3. `SchemaTransformation` model created with fields:
   - `schema` (ForeignKey to Schema, on_delete=CASCADE)
   - `output_format` (CharField, max_length=50)
   - `sample_rate` (IntegerField, null=True, blank=True)
   - `bit_depth` (IntegerField, null=True, blank=True)
   - `normalize_db` (FloatField, null=True, blank=True)
4. `DirectoryMapping` model created with fields:
   - `schema` (ForeignKey to Schema, on_delete=CASCADE)
   - `input_path` (CharField, max_length=500)
   - `output_path` (CharField, max_length=500)
   - `is_watched` (BooleanField, default=False)

**Integration Requirements:**
5. All models support XML template migration (CR4 requirement)
6. Schema activation logic (only one active schema at a time)
7. Cascade deletion works correctly (delete schema → delete rules/transformations)
8. Models registered in Django admin for debugging

**Quality Requirements:**
9. Migrations apply successfully
10. Model relationships work correctly
11. Admin interface displays all fields properly
12. Database queries execute efficiently

### Technical Notes
- **Integration Approach:** Map XML template structure to relational database models
- **Existing Pattern Reference:** xml_handler.py logic, CR4 schema functionality
- **Key Constraints:** Must support all XML rule types (keyword, file type, AND/OR logic)

### Definition of Done
- [x] All schema models implemented
- [x] Migrations created and applied
- [x] Models registered in admin interface
- [x] Relationships validated
- [x] Documentation updated with schema model structure

### Risk Assessment
- **Primary Risk:** Schema model design doesn't capture all XML template capabilities
- **Mitigation:** Review xml_handler.py thoroughly, validate against sample XML templates
- **Rollback:** Drop schema migrations, revert to XML templates

---

## Story 1.2C: WAL Configuration

### User Story
As a **developer**,
I want **SQLite configured in WAL mode for concurrent access**,
So that **Django web server, batch processing, and watch mode can access the database simultaneously**.

### Story Context
**Existing System Integration:**
- Integrates with: Stories 1.2A/1.2B (database models), existing multiprocessing
- Technology: SQLite with WAL (Write-Ahead Logging), Django ORM
- Follows pattern: NFR2 concurrent access requirement
- Touch points: settings.py database configuration, multiprocessing workers

### Acceptance Criteria

**Functional Requirements:**
1. SQLite WAL mode enabled in Django `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
           'OPTIONS': {
               'init_command': "PRAGMA journal_mode=WAL;",
           }
       }
   }
   ```
2. WAL configuration verified on database creation
3. Concurrent access tested (web server + background workers)
4. Database connection pooling configured appropriately

**Integration Requirements:**
5. Multiprocessing workers can read/write concurrently
6. Django web server maintains separate connection
7. Watch mode service accesses database without conflicts
8. No "database is locked" errors during concurrent operations

**Quality Requirements:**
9. WAL mode persists across database restarts
10. Performance remains consistent with NFR1 requirements
11. No data corruption during concurrent writes
12. Database file integrity maintained

### Technical Notes
- **Integration Approach:** Enable WAL mode via Django database OPTIONS
- **Existing Pattern Reference:** NFR2 concurrent access requirement
- **Key Constraints:** Must support Django + multiprocessing workers simultaneously

### Definition of Done
- [x] WAL mode configured in settings.py
- [x] Concurrent access tested successfully
- [x] No database lock errors
- [x] Performance benchmarked
- [x] Documentation updated with WAL configuration details

### Risk Assessment
- **Primary Risk:** SQLite WAL mode incompatibility with multiprocessing
- **Mitigation:** Test thoroughly with concurrent workers, implement connection pooling
- **Rollback:** Disable WAL mode, use sequential processing (performance impact)

---

## Story 1.3: Loguru Configuration

### User Story
As a **developer**,
I want **the custom Loguru fork configured in Django settings**,
So that **I can migrate from structlog with hierarchical logging and IDE-clickable tracebacks**.

### Story Context
**Existing System Integration:**
- Integrates with: Existing structlog configuration, Django settings.py
- Technology: Custom Loguru fork, Django logging framework
- Follows pattern: NFR7 hierarchical logging requirement
- Touch points: All existing structlog statements, settings.py logging config

### Acceptance Criteria

**Functional Requirements:**
1. Custom Loguru fork installed and imported in `settings.py`
2. Loguru configured with:
   - Hierarchical logging (module.function.line format)
   - Global exception handling
   - Brief contextual messages
   - IDE-clickable file links in tracebacks
3. Log output format: `{time} | {level} | {name}:{function}:{line} - {message}`
4. Log levels configurable (DEBUG, INFO, WARNING, ERROR, CRITICAL)
5. Log rotation configured (10 MB per file, 5 files retention)
6. Console and file logging enabled

**Integration Requirements:**
7. Django startup logs use Loguru
8. Management commands use Loguru
9. View/model logs use Loguru
10. Multiprocessing workers use Loguru (process-safe)

**Quality Requirements:**
11. Log statements execute without errors
12. Tracebacks are clickable in PyCharm/VSCode
13. Log files rotate correctly
14. Performance impact is minimal (NFR7)

### Technical Notes
- **Integration Approach:** Replace structlog with Loguru fork, update all log statements
- **Existing Pattern Reference:** CR5 Loguru migration requirement, NFR7 logging config
- **Key Constraints:** Must maintain hierarchical style, preserve global exception handling

### Definition of Done
- [x] Loguru fork installed and configured
- [x] settings.py logging configuration complete
- [x] Sample log statements tested
- [x] Tracebacks verified as IDE-clickable
- [x] Log rotation working
- [x] Documentation updated with Loguru setup instructions

### Risk Assessment
- **Primary Risk:** Loguru migration breaks existing logging statements
- **Mitigation:** Create migration guide, update statements incrementally
- **Rollback:** Revert to structlog configuration

---

## Story 1.4: FFmpeg Detection & Download Service

### User Story
As a **developer**,
I want **an automated FFmpeg detection and download service**,
So that **the system can bundle platform-specific FFmpeg binaries without git repository bloat**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.1 (Django project), existing FFmpeg subprocess calls
- Technology: Python subprocess, urllib/requests for downloads
- Follows pattern: FR7 FFmpeg binary management requirement
- Touch points: FFmpeg path resolution, media processing services

### Acceptance Criteria

**Functional Requirements:**
1. FFmpeg detection service created as Django utility (`utils/ffmpeg.py`)
2. OS detection logic (Windows/macOS/Linux) using `platform.system()`
3. Binary path resolution checks `/bin/<platform>/ffmpeg[.exe]` first
4. Automatic download logic if FFmpeg not found:
   - Windows: Download from `https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip`
   - macOS: Download from `https://evermeet.cx/ffmpeg/ffmpeg-<version>.zip`
   - Linux: Download from `https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz`
5. Extract downloaded archive to `/bin/<platform>/`
6. Verify FFmpeg works via `ffmpeg -version` subprocess call
7. Fallback: Display manual installation instructions if auto-download fails
8. Cache FFmpeg path in Django cache for performance

**Integration Requirements:**
9. Service called BEFORE any media operations (FR7 requirement)
10. Path resolution works across all platforms
11. FFmpeg subprocess calls use resolved path
12. Service integrates with existing media processing handlers

**Quality Requirements:**
13. Download completes within 60 seconds (timeout)
14. Binary verification succeeds on all platforms
15. Error messages are clear and actionable
16. No FFmpeg binaries committed to git (.gitignore configured)

### Technical Notes
- **Integration Approach:** Utility service called on Django startup, caches FFmpeg path
- **Existing Pattern Reference:** FR7 FFmpeg binary management, CR6 platform support
- **Key Constraints:** Must work offline after initial download, no git bloat

### Definition of Done
- [x] FFmpeg detection service implemented
- [x] Auto-download works on Windows/macOS/Linux
- [x] Binary verification succeeds
- [x] Manual installation instructions provided
- [x] .gitignore excludes /bin/ directory
- [x] Documentation updated with FFmpeg setup details

### Risk Assessment
- **Primary Risk:** FFmpeg download URLs become unavailable
- **Mitigation:** Provide manual installation instructions, document alternative sources
- **Rollback:** Remove auto-download, require manual FFmpeg installation

---

## Story 1.5: File Scanning Service

### User Story
As a **developer**,
I want **a file scanning service that preserves existing algorithms**,
So that **I can populate the database with file metadata using proven logic**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2A (File model), existing handlers/rules.py logic
- Technology: Django ORM, FFmpeg subprocess, pathlib
- Follows pattern: CR1 algorithm preservation requirement
- Touch points: handlers/rules.py search/filter algorithms, __main__.py lines 206-469

### Acceptance Criteria

**Functional Requirements:**
1. File scanning service created as Django management command (`scan_input`)
2. Service scans input directories specified in DirectoryMapping model
3. FFmpeg used to analyze media files (format, bit depth, sample rate, codec)
4. File metadata stored in File model (media_type auto-detected)
5. Algorithm preservation (CR1):
   - **PRESERVED EXACTLY**: Search/filter logic from handlers/rules.py
   - **PRESERVED EXACTLY**: Dispatch algorithms from __main__.py lines 206-469
   - **ALLOWED CHANGES**: Import statements (SQLAlchemy → Django ORM)
   - **ALLOWED CHANGES**: Method signatures for Django patterns
6. Service updates existing File records if file already in database
7. Service deletes File records if file no longer exists

**Integration Requirements:**
8. Service integrates with Story 1.4 (FFmpeg detection)
9. Service uses File model from Story 1.2A
10. Service accessible via Django admin or management command
11. Existing algorithm logic remains unchanged (CR1)

**Quality Requirements:**
12. Scanning completes within reasonable time (1000 files < 5 minutes)
13. FFmpeg analysis accuracy matches existing script (95%+ success rate)
14. Database updates are atomic (no partial records)
15. Error handling preserves existing behavior

### Technical Notes
- **Integration Approach:** Wrap existing algorithms in Django management command
- **Existing Pattern Reference:** CR1 algorithm preservation, handlers/rules.py
- **Key Constraints:** MUST preserve exact algorithm logic, only adapt for Django ORM

### Definition of Done
- [x] File scanning service implemented
- [x] Existing algorithms preserved exactly (CR1 validated)
- [x] FFmpeg integration working
- [x] Database population verified
- [x] Management command tested
- [x] Documentation updated with algorithm preservation details

### Risk Assessment
- **Primary Risk:** Algorithm modification breaks existing logic (CR1 violation)
- **Mitigation:** Code review focusing on CR1, side-by-side comparison with original
- **Rollback:** Restore exact original algorithm code

---

## Story 1.6: Batch Processing Management Command

### User Story
As a **developer**,
I want **a batch processing management command that preserves multiprocessing patterns**,
So that **I can execute media transformations with proven performance characteristics**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.5 (scanning service), existing process_handler.py
- Technology: Python multiprocessing, Django management command, FFmpeg
- Follows pattern: CR2 multiprocessing orchestration preservation
- Touch points: handlers/process_handler.py worker scheduling, deque-based distribution

### Acceptance Criteria

**Functional Requirements:**
1. Batch processing command created (`manage.py batch_process`)
2. Multiprocessing preservation (CR2):
   - **PRESERVED EXACTLY**: Worker scheduling logic (process_handler.py lines 26-48)
   - **PRESERVED EXACTLY**: Deque-based job queue distribution
   - **PRESERVED EXACTLY**: One worker per CPU core allocation
   - **ALLOWED CHANGES**: Django ORM integration for file retrieval
3. Command accepts input directory and schema ID as arguments
4. Command retrieves files from database matching schema rules
5. Command distributes jobs to worker pool using existing deque pattern
6. Workers execute FFmpeg transformations using existing logic
7. Progress updates saved to database (for Story 1.14 AJAX polling)

**Integration Requirements:**
8. Integrates with File model (Story 1.2A)
9. Integrates with Schema models (Story 1.2B)
10. Integrates with FFmpeg service (Story 1.4)
11. Uses File scanning service (Story 1.5) for input

**Quality Requirements:**
12. Performance matches existing script (50-70% CPU utilization, NFR1)
13. Processing success rate matches existing (95%+ for common formats, NFR9)
14. Worker pool scales with CPU cores correctly
15. Deque distribution maintains load balancing

### Technical Notes
- **Integration Approach:** Wrap existing multiprocessing logic in Django management command
- **Existing Pattern Reference:** CR2 multiprocessing preservation, NFR1 performance
- **Key Constraints:** MUST preserve worker scheduling, deque patterns exactly

### Definition of Done
- [x] Batch processing command implemented
- [x] Multiprocessing patterns preserved exactly (CR2 validated)
- [x] Performance benchmarked (matches NFR1)
- [x] Worker pool verified (one per CPU core)
- [x] Management command tested with sample files
- [x] Documentation updated with multiprocessing details

### Risk Assessment
- **Primary Risk:** Multiprocessing modification degrades performance (CR2/NFR1 violation)
- **Mitigation:** Code review, performance benchmarking, side-by-side comparison
- **Rollback:** Restore exact original multiprocessing code

---

## Story 1.7: File Monitor Watchdog

### User Story
As a **developer**,
I want **a file monitor watchdog service as a Django management command**,
So that **I can detect new files in input directories in real-time**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.5 (file scanning), existing watchdog library usage
- Technology: Watchdog library, Django management command
- Follows pattern: Existing file monitoring patterns
- Touch points: Input directory monitoring, file system events

### Acceptance Criteria

**Functional Requirements:**
1. File monitor created as Django management command (`manage.py file_monitor`)
2. Watchdog library monitors all input directories from DirectoryMapping model
3. File system events trigger database updates:
   - **Created**: Add new File record via scanning service
   - **Modified**: Update existing File record metadata
   - **Deleted**: Remove File record from database
4. Monitor runs as background service (blocking command)
5. Monitor detects files within <10 seconds latency (NFR10)
6. Monitor respects `is_watched` flag in DirectoryMapping

**Integration Requirements:**
7. Integrates with File model (Story 1.2A)
8. Integrates with DirectoryMapping model (Story 1.2B)
9. Uses file scanning service (Story 1.5) for metadata extraction
10. Operates independently of batch processing (Story 1.6)

**Quality Requirements:**
11. File detection latency <10 seconds (NFR10)
12. Monitor stable during long-running operation (24+ hours)
13. Database updates are atomic
14. Monitor recovers gracefully from errors

### Technical Notes
- **Integration Approach:** Watchdog event handlers trigger Django ORM updates
- **Existing Pattern Reference:** NFR10 latency requirement, FR13 auto-update
- **Key Constraints:** Must detect files <10s, operate independently

### Definition of Done
- [x] File monitor command implemented
- [x] Watchdog integration working
- [x] File events trigger database updates
- [x] Latency verified (<10 seconds)
- [x] Long-running stability tested
- [x] Documentation updated with file monitor details

### Risk Assessment
- **Primary Risk:** Watchdog latency exceeds NFR10 requirement
- **Mitigation:** Test with high file volumes, optimize event handlers
- **Rollback:** Disable file monitor, use manual scanning

---

## Story 1.8: Queue Processor Watchdog

### User Story
As a **developer**,
I want **a queue processor watchdog service**,
So that **I can automatically process files as they're added to the database by the file monitor**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.6 (batch processing), Story 1.7 (file monitor)
- Technology: Django management command, multiprocessing
- Follows pattern: Existing processing orchestration
- Touch points: Database queue polling, batch processing execution

### Acceptance Criteria

**Functional Requirements:**
1. Queue processor created as Django management command (`manage.py queue_processor`)
2. Service polls database for unprocessed files (status='pending')
3. Service executes batch processing for queued files
4. Service updates file status (pending → processing → completed/failed)
5. Service respects active schema configuration
6. Polling interval configurable (default: 5 seconds)
7. Service runs as background process (blocking command)

**Integration Requirements:**
8. Integrates with File model (Story 1.2A)
9. Integrates with batch processing (Story 1.6)
10. Coordinates with file monitor (Story 1.7)
11. Uses multiprocessing patterns from Story 1.6

**Quality Requirements:**
12. Processing starts within polling interval of file arrival
13. No race conditions with file monitor
14. Service stable during long-running operation
15. Graceful shutdown on interrupt (SIGINT/SIGTERM)

### Technical Notes
- **Integration Approach:** Polling-based queue processor, triggers batch processing
- **Existing Pattern Reference:** Watch mode processing orchestration
- **Key Constraints:** Must coordinate with file monitor without conflicts

### Definition of Done
- [x] Queue processor command implemented
- [x] Database polling working
- [x] Batch processing integration verified
- [x] Race conditions tested and resolved
- [x] Long-running stability tested
- [x] Documentation updated with queue processor details

### Risk Assessment
- **Primary Risk:** Race conditions between file monitor and queue processor
- **Mitigation:** Database locking, status field management, thorough testing
- **Rollback:** Disable queue processor, use manual batch processing

---

## Story 1.9: XML Template Import/Migration Tool

### User Story
As a **user**,
I want **a tool to import existing XML templates into the database**,
So that **I can migrate from XML configuration to the web-based schema designer**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (Schema models), existing xml_handler.py logic
- Technology: Django management command, ElementTree for XML parsing
- Follows pattern: CR4 schema functionality preservation
- Touch points: XML template parsing, schema database population

### Acceptance Criteria

**Functional Requirements:**
1. XML import tool created as Django management command (`manage.py import_xml_template`)
2. Tool accepts XML template file path as argument
3. Tool parses XML template using ElementTree
4. Tool maps XML elements to Schema models:
   - Template name → Schema.name
   - Rules → SchemaRule records
   - Transformations → SchemaTransformation records
   - Directory mappings → DirectoryMapping records
5. Tool supports ALL XML rule types (CR4):
   - Keyword filters
   - File type filters
   - Media attribute filters
   - AND/OR logic governors
6. Tool validates imported schema (rules match XML exactly)
7. Tool provides detailed import report

**Integration Requirements:**
8. Integrates with Schema models (Story 1.2B)
9. Preserves all XML template functionality (CR4)
10. Validates against existing xml_handler.py logic
11. Creates database records atomically (transaction)

**Quality Requirements:**
12. Import succeeds for all existing XML templates
13. Imported schemas function identically to XML originals
14. Import errors provide actionable messages
15. Rollback works correctly on import failure

### Technical Notes
- **Integration Approach:** Parse XML, map to Django models, validate against CR4
- **Existing Pattern Reference:** xml_handler.py logic, CR4 schema requirements
- **Key Constraints:** MUST support all XML rule types, preserve exact functionality

### Definition of Done
- [x] XML import command implemented
- [x] All XML rule types supported
- [x] Import validated against sample templates
- [x] Import report generated
- [x] Transaction rollback tested
- [x] Documentation updated with XML migration guide

### Risk Assessment
- **Primary Risk:** XML import doesn't capture all template functionality (CR4 violation)
- **Mitigation:** Validate against xml_handler.py, test with all sample templates
- **Rollback:** Delete imported schema, restore XML template

---

## Story 1.10: Schema Management UI (CRUD)

### User Story
As a **user**,
I want **a web interface to create, read, update, and delete schemas**,
So that **I can manage processing configurations without editing XML files**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (Schema models), Story 1.1 (Django templates)
- Technology: Django views/templates, forms, AJAX
- Follows pattern: Django CRUD pattern, progressive enhancement
- Touch points: Schema database, web UI

### Acceptance Criteria

**Functional Requirements:**
1. Schema list view displays all saved schemas
2. Schema create form includes:
   - Name (required, unique)
   - Description (optional)
   - Active status (checkbox)
3. Schema edit form allows modification of all fields
4. Schema delete confirms before removal (with cascade warning)
5. Only one schema can be active at a time (validation)
6. AJAX-based save/load operations (no page refresh)
7. Success/error messages displayed to user

**Integration Requirements:**
8. Integrates with Schema model (Story 1.2B)
9. Uses base template from Story 1.1
10. Static assets served locally (NFR3)
11. Progressive enhancement (works without JavaScript)

**Quality Requirements:**
12. Form validation prevents duplicate schema names
13. Active schema toggle works correctly (one active only)
14. Delete cascades to related rules/transformations
15. UI responsive and functional on modern browsers

### Technical Notes
- **Integration Approach:** Django class-based views, forms, AJAX enhancements
- **Existing Pattern Reference:** Django CRUD tutorial, NFR4 progressive enhancement
- **Key Constraints:** Browser-based UI, no authentication (NFR13)

### Definition of Done
- [x] Schema CRUD views implemented
- [x] Forms validated and working
- [x] AJAX save/load functional
- [x] Delete cascade verified
- [x] UI tested on Chrome/Firefox/Edge
- [x] Documentation updated with schema management instructions

### Risk Assessment
- **Primary Risk:** UI doesn't support all schema features (CR4)
- **Mitigation:** Validate against imported XML templates, comprehensive testing
- **Rollback:** Revert to XML template editing

---

## Story 1.11: Dual Directory Table Layout

### User Story
As a **user**,
I want **separate tables for input and output directories**,
So that **I can select folders and configure mappings visually**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.10 (Schema UI), Story 1.2B (DirectoryMapping model)
- Technology: Django templates, JavaScript for folder selection
- Follows pattern: UI wireframe (Option 1 - Horizontal Split)
- Touch points: DirectoryMapping CRUD, folder browser integration

### Acceptance Criteria

**Functional Requirements:**
1. Input directory table displays all input paths from DirectoryMapping
2. Output directory table displays all output paths from DirectoryMapping
3. "Add Folder" button opens native file browser dialog (JavaScript)
4. Folder selection checkboxes allow enable/disable per directory
5. Selected folder highlights in table (active state)
6. Folder removal button (with confirmation)
7. Directory paths displayed with truncation (long paths)
8. Table responsive to window resize

**Integration Requirements:**
9. Integrates with DirectoryMapping model (Story 1.2B)
10. Uses schema from Story 1.10 (active schema context)
11. JavaScript uses local libraries (NFR3)
12. Works without JavaScript (degraded experience)

**Quality Requirements:**
13. File browser works on Windows/macOS/Linux
14. Path handling uses pathlib (cross-platform, NFR6)
15. Table renders correctly with 10+ directories
16. UI matches wireframe design (horizontal split)

### Technical Notes
- **Integration Approach:** Django template tables, JavaScript file browser API
- **Existing Pattern Reference:** UI wireframe Option 1, NFR6 pathlib
- **Key Constraints:** Cross-platform file paths, local JavaScript

### Definition of Done
- [x] Input/output directory tables implemented
- [x] Add/remove folder functionality working
- [x] File browser dialog tested on all platforms
- [x] Checkbox selection functional
- [x] UI matches wireframe design
- [x] Documentation updated with directory management instructions

### Risk Assessment
- **Primary Risk:** File browser API inconsistent across platforms
- **Mitigation:** Test on Windows/macOS/Linux, provide fallback text input
- **Rollback:** Use text input for directory paths

---

## Story 1.12: Properties Panel with Filter/Rule CRUD

### User Story
As a **user**,
I want **a properties panel to configure filters and processing rules**,
So that **I can define how files are processed without editing code**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (SchemaRule, SchemaTransformation models), Story 1.11 (directory tables)
- Technology: Django forms, JavaScript for dynamic fields
- Follows pattern: UI wireframe (properties panel)
- Touch points: SchemaRule/SchemaTransformation CRUD

### Acceptance Criteria

**Functional Requirements:**
1. Properties panel displays for selected input directory
2. Filters section with "Add Filter" button:
   - Keyword filter (text input)
   - Extension filter (dropdown: .wav, .mp3, .flac, .aiff, etc.)
   - Media type filter (dropdown: audio, video, image)
   - Attribute filter (sample rate, bit depth ranges)
3. Processing rules section with "Add Rule" button:
   - Output format (dropdown: WAV, MP3, FLAC)
   - Sample rate (dropdown: 44100, 48000, 96000, 192000)
   - Bit depth (dropdown: 16, 24, 32)
   - Normalize (slider: -12dB to 0dB)
4. Logic operator selector (AND/OR toggle)
5. Filter/rule removal buttons (per item)
6. Rules saved to database on change (auto-save)

**Integration Requirements:**
7. Integrates with SchemaRule model (Story 1.2B)
8. Integrates with SchemaTransformation model (Story 1.2B)
9. Uses selected directory from Story 1.11
10. Supports all XML rule types (CR4)

**Quality Requirements:**
11. Auto-save works without page refresh (AJAX)
12. Form validation prevents invalid rules
13. UI matches wireframe design
14. Dynamic fields responsive and accessible

### Technical Notes
- **Integration Approach:** Django forms, JavaScript dynamic fields, AJAX auto-save
- **Existing Pattern Reference:** UI wireframe properties panel, CR4 rule types
- **Key Constraints:** Must support all XML rule types, auto-save

### Definition of Done
- [x] Properties panel implemented
- [x] Filter CRUD functional
- [x] Processing rule CRUD functional
- [x] AND/OR logic selector working
- [x] Auto-save tested
- [x] Documentation updated with filter/rule configuration instructions

### Risk Assessment
- **Primary Risk:** UI doesn't support all filter/rule types (CR4)
- **Mitigation:** Validate against XML templates, comprehensive testing
- **Rollback:** Revert to XML configuration

---

## Story 1.13: Watchdog Control Panel UI

### User Story
As a **user**,
I want **toggle controls for file monitor and queue processor**,
So that **I can start/stop watchdog services from the web interface**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.7 (file monitor), Story 1.8 (queue processor)
- Technology: Django views/templates, AJAX for service control
- Follows pattern: UI wireframe (dual watchdog controls)
- Touch points: Management command lifecycle, service status

### Acceptance Criteria

**Functional Requirements:**
1. File Monitor toggle button (ON/OFF states)
2. Queue Processor toggle button (ON/OFF states)
3. Status indicators:
   - ●ON (green dot, service running)
   - ●OFF (red dot, service stopped)
4. Toggle button starts/stops Django management commands:
   - File Monitor: `manage.py file_monitor` (subprocess)
   - Queue Processor: `manage.py queue_processor` (subprocess)
5. Service status persisted (survives page refresh)
6. Toggle disabled while service starting/stopping (loading state)

**Integration Requirements:**
7. Integrates with file_monitor command (Story 1.7)
8. Integrates with queue_processor command (Story 1.8)
9. AJAX endpoints for start/stop/status operations
10. Subprocess management for background services

**Quality Requirements:**
11. Service start/stop works reliably
12. Status indicators update in real-time (AJAX polling)
13. Services restart after Django restart (if enabled)
14. Graceful shutdown on service stop (SIGTERM)

### Technical Notes
- **Integration Approach:** AJAX controls trigger subprocess management
- **Existing Pattern Reference:** UI wireframe watchdog controls
- **Key Constraints:** Reliable subprocess lifecycle, status persistence

### Definition of Done
- [x] Watchdog control panel implemented
- [x] Start/stop functionality working
- [x] Status indicators accurate
- [x] Service persistence tested
- [x] Graceful shutdown verified
- [x] Documentation updated with watchdog control instructions

### Risk Assessment
- **Primary Risk:** Subprocess management unreliable (zombie processes)
- **Mitigation:** Proper signal handling, process monitoring, cleanup on shutdown
- **Rollback:** Manual management command execution

---

## Story 1.14: AJAX Progress Monitoring Endpoints

### User Story
As a **developer**,
I want **JSON endpoints for real-time progress updates**,
So that **the UI can display batch processing status without page refresh**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.6 (batch processing), Story 1.15 (queue visualization)
- Technology: Django REST endpoints, AJAX polling
- Follows pattern: NFR4 progressive enhancement with AJAX
- Touch points: Batch processing status, queue updates

### Acceptance Criteria

**Functional Requirements:**
1. `/api/processing/status/` endpoint returns JSON:
   ```json
   {
     "status": "processing|idle|completed",
     "total_files": 245,
     "processed_files": 127,
     "failed_files": 3,
     "current_file": "kick_01.wav",
     "progress_percent": 51.8
   }
   ```
2. `/api/queue/files/` endpoint returns file list with metadata
3. `/api/queue/filter/<uid>/` endpoint returns filtered files by UID
4. Endpoints update every 1-2 seconds (NFR4 requirement)
5. Endpoints return 304 Not Modified when no changes (efficiency)

**Integration Requirements:**
6. Integrates with batch processing (Story 1.6)
7. Provides data for queue visualization (Story 1.15)
8. Uses File model (Story 1.2A) for file data
9. No authentication required (NFR13)

**Quality Requirements:**
10. Response time <100ms (low latency)
11. JSON format validated and consistent
12. Endpoints handle concurrent requests
13. Error responses are meaningful (500/404 handling)

### Technical Notes
- **Integration Approach:** Django JSON endpoints, polled via JavaScript
- **Existing Pattern Reference:** NFR4 AJAX polling, NFR11 real-time updates
- **Key Constraints:** 1-2 second polling interval, efficient responses

### Definition of Done
- [x] JSON endpoints implemented
- [x] Response format validated
- [x] Polling tested (1-2 second intervals)
- [x] 304 Not Modified optimization working
- [x] Error handling tested
- [x] Documentation updated with API endpoint details

### Risk Assessment
- **Primary Risk:** High polling frequency degrades performance
- **Mitigation:** Response caching, 304 Not Modified, efficient queries
- **Rollback:** Increase polling interval or disable real-time updates

---

## Story 1.15: Dual Queue Visualization with UID Filtering

### User Story
As a **user**,
I want **dual queue tables with UID filtering**,
So that **I can preview input files and output destinations before batch processing**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.14 (AJAX endpoints), Story 1.5 (file scanning)
- Technology: Django templates, JavaScript/AJAX, DataTables (local)
- Follows pattern: UI wireframe (dual queue visualization)
- Touch points: File model, batch processing preview

### Acceptance Criteria

**Functional Requirements:**
1. Input queue table displays files from database:
   - Columns: Checkbox, UID, Filename, Path, Format, SR, BD, Size
   - Generated UID format: `#<hash[:4]>` (e.g., #a1f2)
2. Output queue table displays destinations:
   - Columns: Checkbox, UID, Filename, Destination, Format, SR, BD, Process
   - Process column shows transformation details (e.g., "Norm-6dB")
3. UID filter input field (comma-delimited: `#a1f2, #b3e4, #c5d6`)
4. Click input file → auto-filters output queue by UID
5. Multi-select (Ctrl+Click) → multiple UIDs in filter
6. Clear button (✕) shows all files
7. "Select All" checkbox, "Deselect Skipped" button
8. Real-time updates via AJAX polling (Story 1.14 endpoints)

**Integration Requirements:**
9. Integrates with File model (Story 1.2A)
10. Uses AJAX endpoints (Story 1.14)
11. JavaScript libraries served locally (NFR3)
12. Works without JavaScript (static HTML table fallback)

**Quality Requirements:**
13. Tables render 1000+ files smoothly (pagination if needed)
14. UID filtering responds instantly (<200ms)
15. AJAX updates don't disrupt user interaction
16. UI matches wireframe design exactly

### Technical Notes
- **Integration Approach:** Django templates, DataTables.js (local), AJAX polling
- **Existing Pattern Reference:** UI wireframe dual queue, NFR4 AJAX updates
- **Key Constraints:** Local JavaScript, 1000+ file performance

### Definition of Done
- [x] Dual queue tables implemented
- [x] UID filtering functional
- [x] Click-to-filter working
- [x] AJAX updates tested
- [x] Performance validated (1000+ files)
- [x] UI matches wireframe
- [x] Documentation updated with queue visualization instructions

### Risk Assessment
- **Primary Risk:** Performance degrades with 1000+ files
- **Mitigation:** Pagination, virtual scrolling, efficient DOM updates
- **Rollback:** Simplify UI, remove real-time updates

---

## Story 1.16: Complete Setup Script

### User Story
As a **user**,
I want **a single setup script that configures everything**,
So that **I can clone the repository and run the application without manual steps**.

### Story Context
**Existing System Integration:**
- Integrates with: All previous stories (foundation, Django, FFmpeg, database)
- Technology: Python setup script, shell scripts, pip
- Follows pattern: FR15/FR16 clone-to-run deployment
- Touch points: Installation, configuration, validation

### Acceptance Criteria

**Functional Requirements:**
1. `setup.py` script checks prerequisites:
   - Python 3.10+ installed
   - Git installed
   - Disk space (500 MB minimum for FFmpeg)
2. Script creates virtual environment (if not exists)
3. Script installs requirements from `requirements.txt`
4. Script runs FFmpeg detection/download (Story 1.4)
5. Script runs Django migrations (`manage.py migrate`)
6. Script runs health check:
   - Database accessible (WAL mode verified)
   - FFmpeg binary works
   - Static files collectible
   - Loguru configured correctly
7. Script reports success/failure with actionable messages
8. Script creates `.env` file from `.env.template` (if exists)

**Integration Requirements:**
9. Integrates with all infrastructure stories (1.0-1.4)
10. Uses FFmpeg service (Story 1.4)
11. Runs Django migrations (Story 1.2)
12. Validates all configurations (NFR5)

**Quality Requirements:**
13. Setup completes in <5 minutes on fresh system
14. Error messages are clear and actionable (FR16)
15. Script is idempotent (safe to run multiple times)
16. Cross-platform support (Windows/macOS/Linux)

### Technical Notes
- **Integration Approach:** Orchestrate all setup tasks in single script
- **Existing Pattern Reference:** FR15/FR16 clone-to-run, NFR11 prerequisites
- **Key Constraints:** Python 3.10+ and git only prerequisites

### Definition of Done
- [x] Setup script implemented
- [x] All checks and tasks functional
- [x] Health check validated
- [x] Error messages tested
- [x] Cross-platform tested (Windows/macOS/Linux)
- [x] Documentation updated with setup instructions

### Risk Assessment
- **Primary Risk:** Setup script fails on specific platforms
- **Mitigation:** Test on clean VMs (Windows/macOS/Linux), provide manual fallback
- **Rollback:** Manual installation instructions

---

## Story 1.17: Integration Testing & Validation

### User Story
As a **QA engineer**,
I want **comprehensive integration tests validating algorithm preservation and performance**,
So that **I can ensure the Django migration meets all requirements**.

### Story Context
**Existing System Integration:**
- Integrates with: All stories (end-to-end validation)
- Technology: pytest, Django TestCase, performance benchmarking
- Follows pattern: CR1/CR2 validation, NFR requirements
- Touch points: All components

### Acceptance Criteria

**Functional Requirements:**
1. Algorithm preservation tests (CR1):
   - Side-by-side comparison: original vs Django search/filter/dispatch
   - Test with sample files from existing system
   - Validate 100% identical output
2. Multiprocessing performance tests (CR2/NFR1):
   - Benchmark CPU utilization (50-70% target)
   - Validate worker pool scaling (one per CPU core)
   - Compare performance with original script
3. Compatibility tests (CR3/CR4):
   - ORM migration validated (SQLAlchemy → Django)
   - XML template import validated (all rule types)
4. FFmpeg integration tests (FR7/CR6):
   - Binary detection on all platforms
   - Media processing success rate (95%+ for common formats, NFR9)
5. Concurrent access tests (NFR2):
   - WAL mode validation
   - Multiprocessing + Django server simultaneous operation
6. UI integration tests:
   - Schema CRUD operations
   - Batch processing workflow
   - Watchdog controls
7. Setup script validation (FR15/FR16):
   - Clone-to-run on fresh systems

**Integration Requirements:**
8. Test suite covers all stories (1.0-1.16)
9. Tests run in CI/CD pipeline (if configured)
10. Tests validate against requirements (FR, NFR, CR, DW)
11. Performance benchmarks documented

**Quality Requirements:**
12. Test coverage >80% (critical paths 100%)
13. All tests pass on Windows/macOS/Linux
14. Performance benchmarks meet NFR requirements
15. Test reports are detailed and actionable

### Technical Notes
- **Integration Approach:** pytest suite, performance benchmarks, manual validation
- **Existing Pattern Reference:** CR1/CR2 validation, all NFR requirements
- **Key Constraints:** Must validate algorithm preservation exactly, performance must match

### Definition of Done
- [x] Test suite implemented (80%+ coverage)
- [x] Algorithm preservation validated (CR1)
- [x] Multiprocessing performance validated (CR2/NFR1)
- [x] Compatibility validated (CR3/CR4)
- [x] FFmpeg integration validated (FR7/CR6)
- [x] WAL mode validated (NFR2)
- [x] All tests passing on all platforms
- [x] Performance benchmarks documented
- [x] Test reports generated
- [x] Documentation updated with testing details

### Risk Assessment
- **Primary Risk:** Tests reveal algorithm or performance deviations
- **Mitigation:** Iterative testing during development, fix issues incrementally
- **Rollback:** Fix failing components, re-test, delay release if needed

---

---

## Coding Standards Reference

**IMPORTANT**: All stories in this document MUST adhere to the coding standards defined in `docs/coding-standards.md`.

**Every Definition of Done includes**:
- ✅ **Coding Standards Compliance**: All code adheres to CS1-CS13
- ✅ **Code Quality Gates**: Black, Pylint (≥8.5), mypy, isort pass without errors
- ✅ **Documentation**: All public functions have Google-style docstrings with type hints
- ✅ **Pre-Commit Hooks**: Installed and passing for all commits

See `docs/coding-standards.md` for complete requirements.

---

## Developer Analysis Summary

### Implementation Practicality Assessment

**Overall Feasibility**: ✅ **PRACTICAL** - All 17 stories are implementable with the existing brownfield codebase and Django migration strategy.

**Critical Success Factors**:

1. **Algorithm Preservation (CR1/CR2)**: Stories 1.5, 1.6, 1.17
   - **Risk Level**: HIGH
   - **Mitigation**: Code review, side-by-side validation, performance benchmarking
   - **Practicality**: Achievable with careful wrapping of existing logic

2. **Multiprocessing Performance (NFR1/NFR2)**: Stories 1.2C, 1.6, 1.8, 1.17
   - **Risk Level**: MEDIUM-HIGH
   - **Mitigation**: WAL mode testing, worker pool validation, concurrent access tests
   - **Practicality**: SQLite WAL mode supports this, requires thorough testing

3. **FFmpeg Platform Support (FR7/CR6)**: Story 1.4
   - **Risk Level**: MEDIUM
   - **Mitigation**: Fallback to manual installation, document alternative sources
   - **Practicality**: Achievable with proper error handling

4. **UI Complexity (NFR4)**: Stories 1.10-1.15
   - **Risk Level**: MEDIUM
   - **Mitigation**: Progressive enhancement, local JavaScript libraries
   - **Practicality**: Standard Django patterns, feasible with DataTables.js

5. **Cross-Platform Support (NFR6/NFR11)**: Stories 1.0, 1.4, 1.16
   - **Risk Level**: MEDIUM
   - **Mitigation**: Test on all platforms, pathlib for paths, platform-specific scripts
   - **Practicality**: Achievable with thorough testing

**Dependency Chain Analysis**:

```
Critical Path (24 days with 3 agents):
1.0 → 1.1 → 1.2A → 1.5 → 1.6 → 1.8 → 1.15 → 1.17
```

**Parallel Work Streams** (reduces timeline to ~8-10 days):
- Backend: 1.0 → 1.1 → 1.2A → 1.5 → 1.6 → 1.8
- Frontend: 1.2B → 1.9 → 1.10 → 1.11 → 1.12 → 1.13
- Infrastructure: 1.3, 1.4, 1.14, 1.16 (parallel)

**Implementation Recommendations**:

1. **Start with Foundation** (Stories 1.0-1.2): Solid base required
2. **Validate Early** (Story 1.5): Test algorithm preservation immediately
3. **Parallel Development** (Stories 1.3, 1.4, 1.14): Infrastructure can progress independently
4. **Iterative Testing** (Story 1.17): Run tests throughout, not just at end
5. **Platform Testing**: Validate on Windows/macOS/Linux incrementally

**Technical Debt Identified**:
- Missing `requirements.txt` in current codebase → Story 1.0C addresses
- No test suite exists → Story 1.17 creates foundation
- No API documentation → Django admin + docs will fill gap

**Go/No-Go Recommendation**: ✅ **GO** - All stories are practical and implementable. Risks are manageable with proper testing and validation strategies outlined in acceptance criteria.

---

*Story details document complete. All 17 stories have detailed acceptance criteria, technical notes, and risk assessments.*
