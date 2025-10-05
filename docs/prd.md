# Samplify Brownfield Enhancement PRD
## Django Web UI Modernization

**Version**: 1.1
**Date**: 2025-10-03
**Author**: PM Agent (John)

---

## Table of Contents
1. [Intro Project Analysis and Context](#intro-project-analysis-and-context)
2. [Requirements](#requirements)
3. [User Interface Enhancement Goals](#user-interface-enhancement-goals)
4. [Technical Constraints and Integration Requirements](#technical-constraints-and-integration-requirements)
5. [Epic and Story Structure](#epic-and-story-structure)

---

## Intro Project Analysis and Context

### Analysis Source
- ✅ Document-project analysis completed
- ✅ Brownfield architecture document available at: `docs/architecture.md`
- ✅ Project brief available at: `docs/brief.md`

### Current Project State

**Samplify** is a Python-based CLI application for automated media library organization and processing. Current capabilities:

**Core Functionality:**
- Processes audio (ffmpeg), video (ffmpeg), and image files (PIL)
- XML template-driven processing rules with keyword/regex pattern matching
- Multiprocessing-based parallel conversion (one worker per CPU core)
- Watchdog-based file system monitoring for real-time processing
- SQLite database (SQLAlchemy ORM) for file cataloging and metadata storage
- Structured logging via custom structlog configuration

**Current Architecture:**
- **Entry Point**: `__main__.py` orchestrates all initialization
- **Business Logic**: Handler classes in `handlers/` directory
- **Data Layer**: SQLAlchemy models with SQLite backend
- **Configuration**: XML templates stored in `%USERPROFILE%\Documents\Samplify\Templates\`
- **User Data**: Input/Output directories in user documents folder

### Available Documentation

**✓ Available:**
- ✅ **Project Brief**: `docs/brief.md` (comprehensive enhancement plan)
- ✅ **Brownfield Architecture**: `docs/architecture.md` (complete technical analysis)
- ✅ **README**: Basic project overview

**⚠️ Gaps Identified:**
- ❌ No `requirements.txt` (dependency management missing)
- ❌ No coding standards documentation
- ❌ No API documentation (CLI-only, no API exists)
- ❌ No test documentation (no test suite exists)

### Enhancement Scope Definition

**Enhancement Type:**
- ☑️ **Major Feature Modification** - Modernizing from CLI script to web application
- ☑️ **Technology Stack Upgrade** - Python script → Django framework
- ☑️ **UI/UX Overhaul** - Adding browser-based interface (currently none exists)
- ☑️ **Integration with New Systems** - Self-contained architecture with bundled ffmpeg

**Enhancement Description:**

Transform Samplify from a Python CLI script into a Django-based web application with self-contained architecture. The modernization will replace XML-based configuration with a browser UI, implement database-backed schema management, bundle portable ffmpeg binaries, and provide batch processing with real-time progress monitoring—all while preserving proven multiprocessing and media conversion patterns from the existing codebase.

**Impact Assessment:**
- ☑️ **Major Impact (architectural changes required)**

### Goals and Background Context

**Goals:**
- Modernize architecture from CLI script to Django web application
- Replace XML template configuration with intuitive browser-based schema designer
- Implement self-contained deployment with bundled portable ffmpeg binaries
- Provide real-time batch processing progress monitoring via web UI
- Enable watch mode as a Django management command service
- Eliminate external dependencies by bundling all required binaries
- Maintain and enhance existing multiprocessing performance patterns
- Create foundation for future video/image processing expansion

**Background Context:**

Samplify currently exists as a functional Python script that successfully processes media files using proven ffmpeg integration and multiprocessing patterns. However, the CLI-only interface and XML-based configuration create barriers to usability and limit adoption.

The planned Django modernization addresses three critical needs: (1) **Accessibility** - replacing XML editing with a visual web interface makes the tool approachable for non-technical users, (2) **Self-Contained Deployment** - bundling ffmpeg and using virtual environments eliminates installation complexity and system dependencies, and (3) **Scalability** - the Django architecture provides a foundation for adding video/image processing, advanced features, and future enhancements outlined in the project brief.

This enhancement also serves as a validation of the BMAD methodology for brownfield modernization.

### Change Log

| Change                               | Date       | Version | Description                                    | Author |
| ------------------------------------ | ---------- | ------- | ---------------------------------------------- | ------ |
| Initial PRD Creation                 | 2025-10-03 | 1.0     | Brownfield enhancement PRD for Django migration | PM     |
| Architecture Documentation Completed | 2025-10-03 | 1.0     | Added comprehensive brownfield analysis        | PM     |
| Story Details Completed              | 2025-10-03 | 1.0     | Added detailed acceptance criteria for 17 stories | PM     |
| Developer Analysis Completed         | 2025-10-03 | 1.0     | Implementation practicality assessment complete | PM     |
| Coding Standards Added               | 2025-10-03 | 1.1     | Added CS1-CS13 coding standards and conventions | PM     |
| PRD Finalized                        | 2025-10-03 | 1.1     | Ready for developer handoff with coding standards | PM     |

---

## Requirements

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

## User Interface Enhancement Goals

### Integration with Existing UI

**Current State**: Samplify has NO existing UI - it's a CLI-only application with XML-based configuration.

**New UI Integration Approach**:
- Django-based web interface served on `localhost` (default port 8000)
- Browser-accessible UI replacing all XML template editing
- Self-contained local web server (no remote access, no cloud integration)
- Progressive enhancement: functional HTML with JavaScript enhancements
- Minimal design aesthetic (proof-of-concept focus)

### Single-Page Schema Designer (Final Design)

**Layout: Option 1 - Horizontal Split with Dual Queue Visualization**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  [🔄 File Monitor: ●ON ] [⚙️ Queue Processor: ●ON ]                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Schema: "Audio Processing Template" [Save] [Load] [Delete]                                         │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                       │
│  INPUT DIRECTORIES                              OUTPUT DIRECTORIES                                   │
│  ┌───────────────────────────┐                 ┌───────────────────────────┐                       │
│  │ [+ Add Folder]            │                 │ [+ Add Folder]            │                       │
│  ├───────────────────────────┤                 ├───────────────────────────┤                       │
│  │ ☑ C:\Input\Samples        │                 │ ☑ C:\Output\Drums         │                       │
│  │ ☐ C:\Input\Loops          │                 │ ☐ C:\Output\Bass          │                       │
│  │ ☐ C:\Input\FX             │                 │ ☐ C:\Output\Vocals        │                       │
│  └───────────────────────────┘                 └───────────────────────────┘                       │
│                                                                                                       │
│  SELECTED FOLDER PROPERTIES                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ Input: C:\Input\Samples                                                                       │   │
│  │ ┌──────────────────────────┐  ┌─────────────────────────────────────────────────────────────┐│   │
│  │ │ FILTERS                  │  │ PROCESSING RULES                                            ││   │
│  │ │ [+ Add Filter]           │  │ [+ Add Rule]                                                ││   │
│  │ │ • Keywords: kick         │  │ • Format: WAV                                               ││   │
│  │ │ • Extension: .wav        │  │ • Sample Rate: 44100                                        ││   │
│  │ │ • Contains: Audio        │  │ • Bit Depth: 24                                             ││   │
│  │ │                          │  │ • Normalize: -6dB                                           ││   │
│  │ └──────────────────────────┘  └─────────────────────────────────────────────────────────────┘│   │
│  │ Logic: [AND ▼] [OR]                                                                           │   │
│  └──────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                       │
│  [Scan Input] [Preview Transformations] [Start Batch Process]                                       │
│                                                                                                       │
│  PROCESSING QUEUE (245 files)                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ INPUT FILES                                                                                   │   │
│  ├───┬────────┬─────────────────────────┬──────────────────┬────────┬────────┬───────┬─────────┤   │
│  │ ☑ │ UID    │ Filename                │ Path             │ Format │ SR     │ BD    │ Size    │   │
│  ├───┼────────┼─────────────────────────┼──────────────────┼────────┼────────┼───────┼─────────┤   │
│  │ ☑ │ #a1f2  │ kick_01.wav             │ C:\Input\Samples │ WAV    │ 44100  │ 16    │ 1.2 MB  │   │
│  │ ☑ │ #b3e4  │ kick_02.wav             │ C:\Input\Samples │ WAV    │ 44100  │ 24    │ 2.1 MB  │   │
│  │ ☑ │ #c5d6  │ snare_01.wav            │ C:\Input\Samples │ WAV    │ 48000  │ 16    │ 890 KB  │   │
│  └───┴────────┴─────────────────────────┴──────────────────┴────────┴────────┴───────┴─────────┘   │
│                                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ OUTPUT DESTINATIONS        Filter by UID: [#a1f2, #b3e4, #c5d6                           ✕]  │   │
│  ├───┬────────┬─────────────────────────┬──────────────────┬────────┬────────┬───────┬─────────┤   │
│  │ ☑ │ UID    │ Filename                │ Destination      │ Format │ SR     │ BD    │ Process │   │
│  ├───┼────────┼─────────────────────────┼──────────────────┼────────┼────────┼───────┼─────────┤   │
│  │ ☑ │ #a1f2  │ kick_01.wav             │ C:\Output\Drums  │ WAV    │ 44100  │ 24    │ Norm-6dB│   │
│  │ ☑ │ #b3e4  │ kick_02.wav             │ C:\Output\Drums  │ WAV    │ 44100  │ 24    │ Norm-6dB│   │
│  │ ☑ │ #c5d6  │ snare_01.wav            │ C:\Output\Drums  │ WAV    │ 44100  │ 24    │ Resample│   │
│  └───┴────────┴─────────────────────────┴──────────────────┴────────┴────────┴───────┴─────────┘   │
│                                                                                                       │
│  ☑ Select All  [▲ Deselect Skipped]              [Clear Queue] [Export Preview]                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Key UI Features:**

1. **Dual Watchdog Controls** (top bar):
   - File Monitor toggle (filesystem watchdog)
   - Queue Processor toggle (processing watchdog)
   - Status indicators: ●ON (green) / ●OFF (red)

2. **Input/Output Directory Tables**:
   - Folder selection with checkboxes
   - Add/remove directories via file browser dialog

3. **Properties Panel**:
   - Filters (keywords, extensions, media type)
   - Processing rules (format, sample rate, bit depth, normalize)
   - AND/OR logic selector

4. **Dual Queue Visualization**:
   - **Input Queue**: Shows files with UID, metadata columns
   - **Output Queue**: Shows destinations with processing details
   - **UID Filtering**: Comma-delimited search (#a1f2, #b3e4)
   - Click input file → auto-filters output queue
   - Clear button (✕) shows all files

5. **Interaction Flow**:
   - Scan Input → Populates queue
   - Click input file → Filters output by UID
   - Multi-select (Ctrl+Click) → Multiple UIDs in filter
   - Preview Transformations → Shows queue
   - Start Batch Process → Executes checked items

---

## Technical Constraints and Integration Requirements

### Existing Technology Stack

**Current Stack** (from brownfield analysis):
- **Runtime**: Python 3.x
- **Database**: SQLite via SQLAlchemy ORM
- **Logging**: Structlog with custom processors
- **Media Processing**: FFmpeg (subprocess), PIL (images)
- **File Watching**: Watchdog library
- **Multiprocessing**: Python stdlib
- **Critical Gap**: No requirements.txt exists

### Integration Approach

**Django Migration Strategy:**

1. **Database**: SQLAlchemy → Django ORM, SQLite WAL mode, single-table inheritance
2. **Services**: Management commands for watch/batch processing
3. **Frontend**: Django templates with AJAX polling
4. **FFmpeg**: Bundled portable binaries in `/bin/<platform>/`

### Django Project Structure

```
samplify/
├── manage.py
├── setup.py                 # Single-point installation
├── requirements.txt
├── .gitignore
├── samplify/
│   ├── settings.py         # All configs (Loguru, ffmpeg, DB)
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── schemas/            # Schema configuration
│   ├── processing/         # Media processing services
│   │   └── management/commands/
│   │       ├── watch.py
│   │       └── batch_process.py
│   └── catalog/            # File cataloging
├── static/                 # Locally served assets
└── bin/                    # Platform ffmpeg binaries
    ├── windows/
    ├── macos/
    └── linux/
```

### Risk Assessment

**Critical Risks:**
1. Algorithm preservation validation (CR1)
2. SQLite WAL multiprocessing compatibility
3. FFmpeg platform binary compatibility
4. Dual watchdog race conditions

**Mitigation**: See architecture.md for detailed risk analysis

### Coding Standards and Conventions

**Developer Experience Level**: Junior to Mid-level (5 years experience, CS Associates degree background)

**Core Philosophy**: Prioritize human readability and maintainability over syntactic brevity. Code should be self-documenting and easily understood by developers transitioning from the brownfield CLI codebase to the new Django architecture.

#### Code Style Standards

**CS1: PEP 8 Compliance with Extensions**
- Follow PEP 8 Python style guide rigorously
- Line length: 120 characters maximum (extended from PEP 8's 79)
- Use newline breakpoints for long wrapped code segments with logical grouping
- Indent wrapped lines for visual clarity and logical flow

**CS2: Type Hinting Requirements**
- Use type hints for ALL function signatures (parameters and return types)
- Use type hints for complex variables and class attributes
- Leverage `typing` module for complex types (List, Dict, Optional, Union, etc.)
- Enable type checking via mypy or similar linter

**CS3: Google-Style Docstrings (Required)**
- All public functions, classes, and methods MUST have Google-style docstrings
- Include: Description, Args, Returns, Raises, Examples (where helpful)
- Format:
  ```python
  def function_name(param1: str, param2: int) -> bool:
      """Brief one-line description of function.

      Detailed description if needed. Explain the purpose, behavior,
      and any important context.

      Args:
          param1: Description of first parameter and its purpose
          param2: Description of second parameter and expected range/format

      Returns:
          Description of return value and its meaning

      Raises:
          ValueError: When param2 is negative
          IOError: When file operations fail

      Example:
          >>> result = function_name("test", 42)
          >>> print(result)
          True
      """
      # Implementation here
  ```

**CS4: Commenting Philosophy - Verbose and Contextual**
- Comment the "why", not just the "what"
- Complex algorithms: Comment each logical block explaining purpose
- Business logic: Explain rationale for decisions (e.g., "Preserve existing algorithm per CR1")
- Branching logic: Explain conditions and expected flow
- Regular intervals: Every 5-10 lines for complex sections
- Group related code with section comments:
  ```python
  # ============================================================
  # Section: Database Query Preparation
  # ============================================================
  # Build the query to fetch unprocessed files matching schema
  # rules. Uses Django ORM with select_related() to minimize
  # database hits during multiprocessing.

  query = File.objects.filter(
      status='pending',
      media_type__in=schema.get_supported_types()
  ).select_related('schema')
  ```

**CS5: Human-Readable Code Over Shortcuts**
- Prefer explicit variable names over abbreviations
  - ✅ `input_file_path` over `in_fp`
  - ✅ `processing_queue` over `proc_q`
- Prefer readable constructs over compact one-liners
  - ✅ Multi-line if/else over ternary when logic is complex
  - ✅ Explicit loops over list comprehensions when readability suffers
- Use intermediate variables to break complex expressions:
  ```python
  # ❌ Avoid complex one-liners
  result = [transform(f) for f in files if validate(f) and check_format(f.fmt)]

  # ✅ Prefer readable breakdown
  validated_files = [f for f in files if validate(f)]
  format_checked_files = [f for f in validated_files if check_format(f.format)]
  result = [transform(f) for f in format_checked_files]
  ```

**CS6: Code Linting and Formatting**
- Use **Black** formatter with 120-character line length
- Use **Pylint** for code quality checks (target score: 8.5+)
- Use **mypy** for static type checking (strict mode)
- Use **isort** for import organization (Django style)
- Pre-commit hooks REQUIRED for all formatting/linting tools
- Configuration files:
  - `pyproject.toml`: Black, isort, mypy configuration
  - `.pylintrc`: Pylint rules and exceptions

**CS7: Import Organization (isort - Django profile)**
```python
# Standard library imports (alphabetical)
import os
import sys
from pathlib import Path
from typing import List, Optional

# Third-party imports (alphabetical)
import numpy as np
from watchdog.observers import Observer

# Django imports (alphabetical by module)
from django.conf import settings
from django.db import models
from django.http import JsonResponse

# Local application imports (relative, alphabetical)
from apps.catalog.models import File
from apps.processing.services import FFmpegService
from apps.schemas.models import Schema
```

**CS8: Function and Method Length**
- Maximum function length: 50 lines (excluding docstring)
- If function exceeds 50 lines: refactor into smaller helper functions
- Each function should have a single, clear responsibility

**CS9: Error Handling - Explicit and Verbose**
- Always use explicit exception types (never bare `except:`)
- Provide detailed error messages with context:
  ```python
  try:
      result = process_file(file_path)
  except FileNotFoundError as e:
      # Log the error with full context for debugging
      logger.error(
          f"Failed to process file: {file_path} does not exist. "
          f"Ensure input directory is correctly configured. Error: {e}"
      )
      raise
  except FFmpegError as e:
      # Provide actionable error message
      logger.error(
          f"FFmpeg processing failed for {file_path}. "
          f"Check FFmpeg installation and file format compatibility. Error: {e}"
      )
      raise ProcessingError(f"Media processing failed: {e}") from e
  ```

**CS10: Django-Specific Conventions**
- Use Django ORM query optimization (select_related, prefetch_related)
- Document ORM queries with expected result sets
- Use Django's built-in validators and form handling
- Follow Django's "fat models, thin views" philosophy
- Use Django management commands for all CLI operations

**CS11: Algorithm Preservation Documentation**
- When porting algorithms from brownfield codebase (CR1/CR2):
  - Add header comment: `# ALGORITHM PRESERVED FROM: handlers/rules.py lines 45-120`
  - Document any adaptations: `# ADAPTATION: Changed SQLAlchemy query to Django ORM`
  - Include side-by-side reference to original code location
  - Mark with `# CR1 REQUIREMENT` or `# CR2 REQUIREMENT` for traceability

**CS12: Visual Code Organization**
- Use blank lines to separate logical blocks (2 lines between functions/classes)
- Use section dividers for major code sections:
  ```python
  # ================================================================
  # DATABASE OPERATIONS
  # ================================================================

  def fetch_pending_files(schema_id: int) -> List[File]:
      """Fetch all pending files for processing."""
      pass


  # ================================================================
  # FFMPEG PROCESSING
  # ================================================================

  def execute_transformation(file: File, rules: List[SchemaRule]) -> bool:
      """Execute FFmpeg transformation based on schema rules."""
      pass
  ```

**CS13: Code Review Checklist (Pre-Merge)**
- [ ] All functions have Google-style docstrings
- [ ] Type hints present on all function signatures
- [ ] Complex logic has explanatory comments (every 5-10 lines)
- [ ] Black, Pylint, mypy, isort pass without errors
- [ ] No lines exceed 120 characters
- [ ] Variable names are explicit and readable
- [ ] Error handling is explicit with detailed messages
- [ ] Algorithm preservation documented (if applicable)
- [ ] Code is visually organized with section breaks

#### Development Tools Configuration

**Required Tools**:
1. **Black** (code formatter)
   - Line length: 120
   - Target Python version: 3.10+

2. **Pylint** (linter)
   - Score threshold: 8.5/10
   - Django plugin enabled

3. **mypy** (type checker)
   - Strict mode enabled
   - Django stubs installed

4. **isort** (import sorter)
   - Profile: django
   - Line length: 120

**Configuration Example** (`pyproject.toml`):
```toml
[tool.black]
line-length = 120
target-version = ['py310']

[tool.isort]
profile = "django"
line_length = 120
multi_line_output = 3
include_trailing_comma = true

[tool.mypy]
python_version = "3.10"
strict = true
plugins = ["mypy_django_plugin.main"]

[tool.pylint.messages_control]
max-line-length = 120
disable = ["C0111"]  # Add specific rule exemptions as needed
```

**Pre-Commit Hook Setup** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=120]

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=django, --line-length=120]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        args: [--strict]

  - repo: https://github.com/PyCQA/pylint
    rev: v3.0.0
    hooks:
      - id: pylint
        args: [--max-line-length=120]
```

#### Code Quality Gates

**DQ1: Automated Quality Checks (CI/CD)**
- All code MUST pass Black formatting check
- All code MUST achieve Pylint score ≥ 8.5/10
- All code MUST pass mypy type checking (no errors)
- All imports MUST be sorted via isort
- Pre-commit hooks MUST be installed and passing

**DQ2: Manual Code Review Focus**
- Algorithm preservation validation (CR1/CR2 compliance)
- Comment quality and density (adequate explanations)
- Error handling completeness (all exception paths covered)
- Docstring completeness (all public functions documented)
- Readability assessment (can junior dev understand quickly?)

**DQ3: Documentation Requirements**
- All stories MUST include coding standards compliance in Definition of Done
- All pull requests MUST reference coding standards adherence
- Code review template MUST include CS1-CS13 checklist

---

## Epic and Story Structure

### Epic Approach

**Single Epic**: "Django Web UI Modernization"

**Rationale**: Highly interconnected work toward one unified goal (CLI → Web UI). Backend models, services, and frontend all depend on each other.

### Epic 1: Django Web UI Modernization

**Epic Goal**: Transform Samplify from Python CLI script to Django web application with browser-based schema designer, automated setup, and self-contained deployment - while preserving all existing algorithms and performance.

### Story Structure (17 Stories - Optimized)

**Story 1.0**: Repository & Environment Foundation
- 1.0A: .gitignore configuration
- 1.0B: Virtual environment setup
- 1.0C: requirements.txt creation

**Story 1.1**: Django Project Setup & Configuration
- Django scaffold, static files, base templates

**Story 1.2**: Database Models (SPLIT INTO SUB-TASKS)
- 1.2A: File Model (single-table inheritance)
- 1.2B: Schema Models
- 1.2C: WAL Configuration

**Story 1.3**: Loguru Configuration
- Settings.py setup, custom formatters

**Story 1.4**: FFmpeg Detection & Download Service
- OS detection, download logic, path resolution

**Story 1.5**: File Scanning Service
- Preserve existing algorithms, integrate Django

**Story 1.6**: Batch Processing Management Command
- Multiprocessing worker pool preservation

**Story 1.7**: File Monitor Watchdog
- Django management command

**Story 1.8**: Queue Processor Watchdog
- Processing orchestration

**Story 1.9**: XML Template Import/Migration Tool
- Parse existing XML → Django models

**Story 1.10**: Schema Management UI (CRUD)
- Save/load/delete operations

**Story 1.11**: Dual Directory Table Layout
- Input/output tables with folder selection

**Story 1.12**: Properties Panel with Filter/Rule CRUD
- Filter and rule configuration UI

**Story 1.13**: Watchdog Control Panel UI
- Toggle buttons and status indicators

**Story 1.14**: AJAX Progress Monitoring Endpoints
- JSON endpoints for real-time status

**Story 1.15**: Dual Queue Visualization with UID Filtering
- Input/output queue tables, UID filtering

**Story 1.16**: Complete Setup Script
- FFmpeg install, migrations, health check

**Story 1.17**: Integration Testing & Validation
- Algorithm validation, performance benchmarking

### Dependency Graph (Optimized)

**Critical Path** (24 days with 3 parallel agents):
```
1.0 → 1.1 → 1.2A → 1.5 → 1.6 → 1.8 → 1.15 → 1.17
```

**Parallel Work Streams**:
- Backend: 1.0 → 1.1 → 1.2A → 1.5 → 1.6 → 1.8
- Frontend: 1.2B → 1.9 → 1.10 → 1.11 → 1.12 → 1.13
- Infrastructure: 1.3, 1.4, 1.14, 1.16 (parallel)

**Merge Strategy** (per DW requirements):
- Each story = feature branch
- Merge to `dev` when feature-complete
- `dev` → `master` only when all stories pass tests

---

## Next Steps

**PRD Status**: ✅ **COMPLETE** - All sections finalized, ready for developer handoff

**Deliverables**:
1. ✅ PRD document (this file) - Sections 1-5 complete
2. ✅ Story details document (`docs/stories.md`) - All 17 stories with acceptance criteria
3. ✅ Developer analysis - Implementation practicality assessment included
4. ✅ Risk mitigation - Story-level risk assessments complete
5. ✅ Testing requirements - Defined per story with validation criteria
6. ✅ Coding standards - CS1-CS13 requirements for junior-to-mid developer experience

**Developer Handoff**:
- **PRD Document**: `docs/prd.md` (architecture, requirements, epic structure, coding standards)
- **Story Details**: `docs/stories.md` (detailed acceptance criteria, technical notes, risk assessments)
- **Coding Standards**: `docs/coding-standards.md` (CS1-CS13 requirements, tools, examples)
- **Architecture Reference**: `docs/architecture.md` (brownfield analysis)
- **Project Brief**: `docs/brief.md` (enhancement plan)

**Implementation Recommendation**: ✅ **GO** - All 17 stories are practical and implementable. See `docs/stories.md` for detailed developer analysis and execution strategy.

---

*PRD complete. Ready for development. Refer to `docs/stories.md` for detailed story specifications.*
