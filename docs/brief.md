# Project Brief: Samplify

## Executive Summary

Samplify is a desktop application that automates media library organization and standardization for content creators working with audio, video, and image files. The tool addresses the persistent challenge of managing poorly labeled, inconsistent, and technically varied media assets from multiple sources by applying user-defined organizational schemas that filter, process, and normalize files according to specific criteria. Built initially as a Python-based script leveraging ffmpeg for media processing, Samplify is being revamped with a self-contained local web server architecture to modernize the stack, eliminate external dependencies through bundled portable binaries, and enable a more robust front-end user experience while serving as a practical test case for the BMAD development methodology.

## Problem Statement

Content creators—particularly music producers, video editors, and multimedia artists—face a persistent productivity drain from managing disorganized media libraries. Sample packs, stock assets, and production libraries arrive from multiple vendors with inconsistent naming conventions, varied audio levels, mixed file formats (MP3, WAV, FLAC, AIFF for audio; MP4, MOV, AVI for video), inconsistent bit depths and sample rates, and technical issues like leading/trailing silence or normalization problems.

The current state forces creators into manual, repetitive work: auditing files individually, renaming assets, converting formats, trimming silence, normalizing levels, and reorganizing into usable folder structures. For a music producer downloading dozens of sample packs annually, this can consume hours per pack. The cognitive overhead of remembering where specific sounds are located across hundreds of poorly organized folders disrupts creative flow and extends project timelines.

Existing solutions fall short in critical ways:
- **Generic file organizers** (like Hazel, DropIt) lack media-specific processing capabilities (format conversion, audio normalization, silence trimming)
- **DAW-integrated tools** (Ableton's browser, Logic's loop library) only organize within the DAW ecosystem and don't address the underlying file chaos
- **Batch converters** (XLD, FFmpeg GUI tools) handle format conversion but not intelligent organization or metadata-based filtering
- **Manual scripting** requires technical expertise and rebuilding solutions for each use case

The urgency of solving this now stems from the explosive growth of sample pack culture and stock media marketplaces—creators are drowning in assets. A typical producer might have 50-500GB of samples across thousands of files. Without systematic organization, this wealth of creative resources becomes a liability rather than an asset. Additionally, the rise of AI-assisted music production and content creation is increasing the volume of media assets creators need to manage, making automated organization not just convenient but essential.

## Proposed Solution

Samplify provides an intelligent, schema-driven media processing pipeline that combines rule-based organization with automated media optimization. Users define organizational schemas specifying how media should be categorized and processed—for example, "all files with 'kick' in the filename and .mp3 format should be converted to 24-bit WAV, have silence trimmed from beginning/end, be normalized to -6dB, and placed in /Drums/Kicks/". The system operates in two modes: batch processing for organizing existing libraries, and continuous watch mode where it monitors input directories and automatically processes new files in real-time as they arrive.

**Key differentiators from existing solutions:**

- **Unified media processing:** Combines file organization, format conversion, audio/video optimization, and metadata standardization in a single automated workflow—eliminating the need to chain multiple tools together
- **Schema-based intelligence:** Reusable, shareable organizational templates that encode best practices (e.g., "Ableton Sample Library Schema" or "Video Stock Asset Schema") instead of one-off manual organization
- **Background automation with watch mode:** Runs as a system tray service monitoring designated input folders—creators simply download new sample packs to the watched directory and Samplify automatically organizes them to the output location according to active schemas, enabling "download and forget" workflows
- **Self-contained architecture:** Leverages multiprocessing and bundled portable binaries (ffmpeg) to maximize throughput when processing thousands of files, with results cataloged in a database for auditability and rollback capability
- **Technical user empowerment:** Provides power users with fine-grained control over processing parameters while maintaining a structured configuration approach that's more maintainable than raw scripting

The solution succeeds where others haven't by recognizing that media library organization isn't just about moving files—it's about applying domain-specific transformations (silence trimming, normalization, format standardization) according to intelligent rules. By treating organization schemas as first-class configuration objects and coupling them with high-performance media processing, Samplify transforms library management from a manual chore into an automated, repeatable process.

**High-level vision:** A desktop application with dual interaction modes: (1) a browser-based UI (local web server) for configuring schemas, running batch operations with preview/progress monitoring, and reviewing results; and (2) a lightweight system tray service for background watch mode where users can quickly enable/disable monitoring, view processing activity, and access the full UI—creating a "set it and forget it" experience where new downloads are automatically organized without breaking creative flow.

## Target Users

### Primary User Segment: Technical Content Creators (Music Producers & Audio Engineers)

**Demographic Profile:**
- Music producers, beatmakers, sound designers, and audio engineers working in DAWs (Ableton, FL Studio, Logic Pro, Reaper)
- Age range: 18-45, predominantly freelance/independent creators or small studio operators
- Tech-savvy users comfortable with command-line tools, scripting, and technical configuration
- Active sample pack consumers (purchasing/downloading 10-50+ packs annually)

**Current Behaviors & Workflows:**
- Download sample packs from sites like Splice, Loopmasters, Producer Loops, or independent creators
- Manually audition samples, create custom folder hierarchies, and move files individually
- Often maintain personal "master libraries" organized by sound type (drums, bass, FX, vocals, etc.)
- Frequently work across multiple projects requiring quick access to specific sounds
- May use DAW-specific browsers but struggle with cross-DAW library access

**Specific Needs & Pain Points:**
- Spend 2-5 hours per week on library management instead of creative work
- Frustrated by inconsistent sample pack quality (poor naming, mixed formats, volume inconsistencies)
- Need reliable format standardization (24-bit WAV preferred for production)
- Want automated silence trimming and normalization to ensure samples are "production-ready"
- Desire "set it and forget it" automation for new downloads

**Goals:**
- Reduce library management time to near-zero
- Access any sample within seconds during creative sessions
- Maintain consistent, professional-grade audio standards across entire library
- Build a personal sample library that rivals commercial products in organization quality

### Secondary User Segment: Video Editors & Photographers

**Demographic Profile:**
- Video editors, motion graphics artists, and photographers managing stock footage and image libraries
- Similar tech-savvy profile to audio creators
- Active consumers of stock media from sites like Artlist, Envato, Adobe Stock, or independent creators

**Current Behaviors & Workflows:**
- Download video clips and image assets from multiple sources
- Manually organize by project, theme, or visual category
- Deal with mixed codecs, resolutions, and color profiles

**Specific Needs & Pain Points:**
- Similar organizational challenges to audio creators (poor naming, inconsistent formats)
- Need format/codec standardization for efficient editing workflows
- Longer processing times for video/image conversion compared to audio

## Goals & Success Metrics

### Business Objectives

- **Validate technical feasibility:** Successfully demonstrate that self-contained architecture with multiprocessing can achieve production-ready performance scalable to real-world libraries (100GB+)
- **BMAD methodology validation:** Complete brownfield modernization using BMAD method, documenting effectiveness for future projects
- **Create reusable foundation:** Build schema-driven processing framework that can extend to video/image media types in future iterations
- **User adoption proof-of-concept:** Achieve functional MVP that handles real-world audio production workflows without manual intervention

### User Success Metrics

- **Time savings:** Reduce library organization time from 2-5 hours/week to <15 minutes/week (setup + monitoring)
- **Processing reliability:** 95%+ successful processing rate for common audio formats (WAV, MP3, FLAC, AIFF)
- **Automation effectiveness:** Watch mode successfully processes 90%+ of new downloads without user intervention
- **Standardization quality:** 100% of processed files meet specified output criteria (format, bit depth, silence trimming, normalization)

### Key Performance Indicators (KPIs)

- **Processing throughput:** Efficient parallel processing demonstrated with 1GB test benchmark; architecture validated for scaling to real-world 100GB+ libraries
- **Concurrent processing efficiency:** Multiprocessing achieves 50-70% CPU utilization across available cores during batch operations
- **Schema accuracy:** <5% false positive rate in file filtering/categorization based on keywords and attributes
- **System responsiveness:** Watch mode file detection latency <10 seconds from file arrival to processing start
- **Error recovery:** Failed file processing logged to database with clear error reporting, <1% unrecoverable failures

## MVP Scope

### Core Features (Must Have)

- **Schema Configuration Engine:** Visual/form-based UI for defining processing schemas with:
  - Filename keyword filters (e.g., "kick", "snare", "bass")
  - File type filters (input format: .mp3, .wav, .flac, .aiff)
  - Output transformation rules (format conversion, bit depth, sample rate)
  - Audio processing parameters (silence trimming, normalization levels)
  - Target output directory mapping

- **Input/Output Directory Schema Manager:** Interactive tree visualization for schema design:
  - **Input Directory Scanner:** User-triggered "Scan" button to populate database with file metadata and encoding information
  - **Input Tree Viewer:** Browse and visualize scanned directory structures with file counts and sizes
  - **Filter Assignment:** Click directories/files to assign filters (keywords, file types, attributes)
  - **Output Tree Designer:** Define and visualize target directory structure with mapping rules
  - **Schema Mapping Preview:** Visual representation showing how input files map to output locations based on applied rules
  - **Drag-and-drop interface** for assigning processing preferences to specific paths or file groups (minimal JavaScript, served locally)
  - Save/load schema configurations for reuse across different projects
  - **Database-backed metadata:** All parsed file metadata (format, bit depth, sample rate, codec) stored in database for fast access

- **Batch Processing System:** Process existing media libraries with:
  - Multi-folder input selection
  - Pre-processing preview showing planned transformations
  - Multiprocessing-based parallel execution
  - Real-time progress monitoring with file-by-file status
  - Completion summary with success/failure reporting

- **Watch Mode Automation:** Django management command service that:
  - Starts after Django initialization via CLI (`python manage.py watch`)
  - Monitors designated input directories using watchdog library
  - Automatically updates database entries (add/edit/remove) as files change in input directories
  - Applies active schema rules to incoming files
  - Runs in separate thread to avoid blocking main server
  - Logs file changes with brief contextual messages

- **Audio Processing Pipeline (ffmpeg-based):**
  - Broad format/codec support leveraging ffmpeg's extensive library (MP3, WAV, FLAC, AIFF, OGG, AAC, ADPCM, and other non-conventional formats)
  - Flexible bit depth/sample rate conversion (8/16/24/32-bit, 44.1/48/96/192kHz) supporting both professional standards and experimental/lo-fi formats
  - Creative codec conversion for hardware emulation (e.g., ADPCM for Game Boy Advance sound, μ-law for retro telephony effects)
  - Leading/trailing silence detection and trimming
  - Volume normalization to specified target levels
  - Metadata preservation where applicable
  - Support for reading and indexing obscure/legacy formats for cataloging purposes

- **Database Cataloging:** SQLite database tracking:
  - Processed file registry (input path, output path, timestamp)
  - Processing results (success/failure, error messages)
  - Schema application history
  - Rollback capability for batch operations

- **Self-Contained Deployment:**
  - Python virtual environment (venv) for all Python dependencies
  - Portable ffmpeg binary bundled within project directory
  - No system PATH dependencies or external installations required
  - Single-folder deployment for portability

### Out of Scope for MVP

- Schema sharing/marketplace (import/export locally only)
- Video and image processing (audio-only for MVP)
- Cloud storage integration (local filesystem only)
- Advanced audio analysis (BPM detection, key detection, spectral analysis)
- Machine learning-based categorization
- Multi-user/team collaboration features
- Mobile or web-remote access
- Undo/rollback UI (database supports it, but UI not implemented)

### MVP Success Criteria

The MVP is considered successful when:
- A user can define a schema, select input folders, and process a 1GB test library efficiently with the architecture demonstrating scalability to 100GB+ real-world libraries
- Watch mode successfully processes new downloads automatically with 90%+ success rate
- The system runs reliably as a background service without crashes or memory leaks
- Processing errors are logged clearly enough for troubleshooting without developer intervention
- The architecture demonstrates readiness for video/image expansion in Phase 2

## Post-MVP Vision

### Phase 2 Features

- **Video Processing Pipeline:** Extend schema engine to support video files with:
  - Codec conversion (H.264, H.265/HEVC, ProRes, AV1)
  - Resolution/framerate standardization
  - Video trimming and clip extraction
  - Thumbnail generation for cataloging

- **Image Processing Support:** Add image file handling with:
  - Format conversion (JPEG, PNG, TIFF, WebP, RAW formats)
  - Batch resizing and compression
  - Metadata extraction (EXIF, IPTC)
  - Duplicate detection based on visual similarity

- **Schema Marketplace/Sharing:** Community-driven schema library
  - Import/export schema templates
  - Schema versioning and compatibility tracking
  - Pre-built schemas for common workflows (e.g., "Ableton Producer Pack", "Stock Video Organizer")

- **Advanced Audio Analysis:** AI/ML-powered features
  - BPM and key detection for music samples
  - Audio similarity matching for finding duplicates
  - Automatic genre/instrument classification
  - Spectral analysis and visualization

### Long-term Vision (1-2 Years)

Samplify evolves into a comprehensive media asset management platform for technical creators, becoming the go-to tool for anyone working with large media libraries. The platform supports not just organization and conversion, but intelligent cataloging with searchable metadata, visual browsers for audio (waveforms), video (thumbnails/timelines), and images (galleries). Advanced users can create complex multi-stage processing workflows with conditional logic, while the schema marketplace enables knowledge sharing across the creator community.

Cross-platform expansion (Windows, macOS, Linux) ensures accessibility, and optional cloud sync enables multi-device workflows without sacrificing the local-first architecture. The tool becomes invaluable for game developers managing audio assets, video editors organizing stock footage, and music producers maintaining massive sample libraries—all through a unified, automation-first interface.

### Expansion Opportunities

- **DAW Integration:** Plugins or extensions for direct integration with Ableton, FL Studio, Logic Pro, and other DAWs
- **Cloud Storage Support:** Optional integration with Dropbox, Google Drive, OneDrive for distributed workflows
- **Team Collaboration:** Multi-user support with shared schemas, conflict resolution, and processing queue management
- **Content Creator Ecosystem:** Integration with sample pack marketplaces (Splice, Loopmasters) for automatic download-to-organized-library workflows
- **Mobile Companion App:** iOS/Android apps for remote monitoring, schema management, and triggering batch operations
- **API/CLI Interface:** Programmatic access for power users and workflow automation tools

## Technical Considerations

### Platform Requirements

- **Target Platforms:** Windows (primary), with architecture designed for future macOS/Linux compatibility
- **Browser/OS Support:** Modern browsers (Chrome, Firefox, Edge) for local web UI; Windows 10/11 for system tray service
- **Performance Requirements:**
  - Multi-core CPU (4+ cores recommended for optimal parallel processing)
  - 8GB+ RAM for handling large batch operations
  - SSD storage recommended for I/O-intensive operations
  - Network: None required (fully local operation)

### Technology Preferences

- **Frontend:**
  - Django templates for server-rendered HTML with dynamic updates
  - AJAX polling (vanilla JS/minimal libraries) for real-time status updates without complex WebSocket infrastructure
  - Django JSON endpoints for fetching processing status, progress metrics, and completion states
  - All JavaScript libraries served locally from Django static files (no CDN dependencies)
  - Progressive enhancement: static fallback with JavaScript-enhanced dynamic updates

- **Backend:**
  - Python 3.10+
  - Django 4.2+ as web framework (aligns with existing project experience)
  - Django ORM for database operations
  - Threading for non-blocking operations (prevent main server thread stalls)
  - Multiprocessing library for parallel batch processing orchestration
  - ffmpeg via subprocess calls (leverage existing optimized integration patterns from brownfield codebase)
  - Python pathlib.Path for cross-platform file path handling
  - Custom Loguru fork (https://github.com/RoscoeTheDog/loguru) for logging with brief contextual messages

- **Database:**
  - SQLite for MVP (Django default, zero-config, portable)
  - **Critical:** SQLite WAL (Write-Ahead Logging) mode must be configured for multiprocessing compatibility
  - PostgreSQL migration path for future multi-user features
  - Django ORM handles database abstraction

- **Logging & Observability:**
  - Hierarchical logging style with global exception handling (from Loguru fork)
  - Tracing enabled at high-level functions for performance bottleneck identification
  - Custom format function with contextual metadata (module, version, timestamps)
  - IDE-clickable file links in exception tracebacks

- **Deployment/Infrastructure:**
  - Python virtual environment (venv) for dependency isolation
  - Portable ffmpeg binary (downloaded and bundled in `/bin` or `/vendor` directory)
  - ffmpeg path configured programmatically, not relying on system PATH
  - Self-hosted local deployment (no cloud infrastructure required)

### Architecture Considerations

- **Repository Structure:**
  - Django project structure: `/samplify` (main project), `/apps` (Django apps: schemas, processing, catalog)
  - `/frontend` for static assets and templates
  - `/bin` or `/vendor` for portable ffmpeg binary
  - `/venv` for Python virtual environment (gitignored)

- **Service Architecture:**
  - Django web service (serves UI, API endpoints, admin interface)
  - Threading model for non-blocking operations (prevents main server thread stalls)
  - Background worker service (Django management commands with multiprocessing for batch processing)
  - File watcher service (Django management command using watchdog library, runs in separate thread)
  - SQLite database file (within project directory, WAL mode enabled for concurrent access)

- **Integration Requirements:**
  - Portable ffmpeg binary bundled in project directory with programmatic path resolution using pathlib.Path
  - **Leverage existing brownfield ffmpeg integration:** Review and adapt optimized patterns from legacy codebase
  - File system access for user-specified input/output directories (cross-platform path handling via pathlib)
  - Loguru hierarchical logging configured at application startup with brief contextual messages
  - Global exception hook installed for comprehensive error tracking
  - Virtual environment activation as part of startup/deployment process
  - SQLite WAL mode configuration in Django settings for multiprocessing support

- **Security/Compliance:**
  - Local-only operation (no network exposure by default)
  - File permission handling for cross-platform compatibility
  - Input validation via Django forms for schema configurations
  - Security considerations deprioritized for MVP (local filesystem use case)

## Constraints & Assumptions

### Constraints

- **Budget:** Personal/portfolio project - no budget for commercial tools or services; open-source/free solutions only
- **Timeline:** Flexible development timeline driven by BMAD methodology validation; no hard deadlines but targeting functional MVP within reasonable timeframe for testing
- **Resources:** Solo developer effort; existing Python/Django experience leveraged; limited time for learning new technologies
- **Technical:**
  - Windows-first development environment; cross-platform support deferred to post-MVP
  - Existing Python codebase provides foundation but may require significant refactoring for Django web architecture
  - ffmpeg portable binary must be sourced and bundled (platform-specific builds for Windows/macOS/Linux)
  - Performance bound by available hardware (multi-core CPU, SSD storage)

### Key Assumptions

- Users have basic technical literacy (comfortable with file paths, directory structures, configuration files)
- 1GB test library sufficient for performance validation while demonstrating scalability to 100GB+ real-world usage patterns
- ffmpeg supports all required audio codecs and transformations out-of-box
- Multiprocessing will achieve adequate parallelization without hitting I/O bottlenecks on SSD storage
- Django's built-in development server adequate for local-only deployment (no production WSGI server needed for MVP)
- SQLite performance sufficient for cataloging thousands of files without significant query degradation
- File watching (watchdog library) performs reliably on Windows without excessive CPU/memory overhead
- Portable ffmpeg binaries available and functionally equivalent to system-installed versions
- Virtual environment provides sufficient isolation for deployment without containerization
- AJAX polling (1-2 second intervals) provides acceptable "real-time" user experience without excessive server load
- Users will primarily process common audio formats (MP3, WAV, FLAC); exotic formats are edge cases
- BMAD methodology will surface architectural improvements organically during development

## Risks & Open Questions

### Key Risks

- **Performance bottleneck risk:** Multiprocessing may not scale efficiently to large libraries if I/O becomes bottleneck; mitigation requires early benchmarking with 1GB test set and potentially implementing queue-based processing with priority scheduling
- **ffmpeg integration complexity:** Subprocess-based ffmpeg calls may introduce edge cases with exotic formats or special characters in filenames; risk of command injection if not properly sanitized
- **Portable ffmpeg sourcing:** Finding reliable, up-to-date portable ffmpeg builds for Windows; ensuring codec support (especially ADPCM and exotic formats) matches system-installed versions; managing platform-specific binary distributions
- **Virtual environment portability:** venv may have path dependencies making it non-portable across machines; may need to document reinstall process or investigate alternatives like PyInstaller for true bundling
- **File watcher reliability:** Watchdog library may miss rapid file changes or consume excessive resources on large directories; needs stress testing with realistic download patterns
- **UI complexity creep:** Interactive tree visualization with drag-and-drop could become complex to implement in Django templates; may require more JavaScript than anticipated
- **Database scaling:** SQLite may struggle with concurrent writes from multiprocessing workers; potential locking issues require testing at scale
- **Existing codebase integration:** Legacy Python code may have architectural assumptions incompatible with Django web approach; refactoring effort could be significant

### Open Questions

- How should schema versioning work to ensure backwards compatibility as the system evolves?
- What's the optimal polling interval for AJAX status updates to balance responsiveness vs. server load?
- Should the input tree viewer scan directories on-demand or pre-index them? (performance vs. real-time accuracy trade-off)
- How to handle partial failures in batch processing? (continue processing remaining files, retry failed, or halt?)
- What's the rollback strategy if a batch operation needs to be undone? (database-only or actual file restoration?)
- Should schemas support conditional logic (e.g., "if BPM > 140, put in /drums/fast/")? MVP scope or Phase 2?
- How to handle duplicate filenames when mapping multiple inputs to same output directory structure?
- What's the user experience for updating schemas that are actively being used by watch mode?
- Should processing preserve original files by default, or allow destructive operations with warnings?
- Where to source portable ffmpeg binaries? (ffmpeg.org official builds, zeranoe builds, or build from source?)

### Areas Needing Further Research

- **Portable ffmpeg distribution:** Identify reliable sources for Windows portable ffmpeg builds with full codec support; validate ADPCM and exotic format availability
- **JavaScript tree visualization libraries:** Evaluate lightweight options (jsTree, Fancytree) compatible with Django templates without heavy framework dependencies
- **Django multiprocessing patterns:** Research best practices for Django management commands spawning multiprocessing workers with proper database connection handling and SQLite locking management
- **Virtual environment bundling:** Investigate PyInstaller, cx_Freeze, or similar tools for creating truly portable standalone executables if venv proves insufficient
- **Loguru integration patterns:** Determine best practices for integrating custom Loguru fork with Django's logging framework without conflicts
- **File attribute extraction:** Research libraries for reading audio metadata (sample rate, bit depth, codec) without full ffmpeg analysis for tree viewer performance
- **Schema export formats:** Decide on JSON vs. YAML vs. custom format for schema import/export and sharing
- **ffmpeg path resolution:** Establish pattern for programmatically locating bundled ffmpeg binary across different deployment scenarios

## Next Steps

### Immediate Actions

1. **Source portable ffmpeg binary** - Download Windows-compatible portable ffmpeg build with full codec support; validate ADPCM and exotic format availability; place in `/bin` or `/vendor` directory
2. **Set up development environment** - Create Python virtual environment, install Django 4.2+, integrate custom Loguru fork, configure hierarchical logging with global exception handling and brief contextual messages
3. **Configure Django project with SQLite WAL mode** - Initialize Django project with apps for schemas, processing, and cataloging; **CRITICAL: Configure SQLite WAL (Write-Ahead Logging) mode in Django settings for multiprocessing compatibility**; create basic project skeleton
4. **Review existing brownfield codebase** - Examine legacy ffmpeg integration patterns and optimization techniques; identify reusable components and adapt for Django architecture
5. **Implement cross-platform path utilities** - Create pathlib.Path-based utility functions for ffmpeg binary location and file path handling; ensure Windows/macOS/Linux compatibility
6. **Create database models with metadata fields** - Define Django models for schemas, processed files (with parsed metadata: format, bit depth, sample rate, codec), processing jobs, and results; run migrations
7. **Implement input directory scanner** - Create "Scan" button UI and threaded backend logic to parse input directories and populate database with file metadata using ffmpeg analysis
8. **Build database-backed tree viewer** - Research minimal JavaScript tree library (to be served locally from Django static files); create Django view for tree visualization pulling from database
9. **Implement schema configuration UI** - Create Django forms and templates for defining filters, transformations, and output mappings (minimal locally-served JavaScript only)
10. **Develop threaded processing engine** - Build Django management command with threading/multiprocessing for batch processing; leverage existing brownfield ffmpeg integration patterns
11. **Implement file watcher management command** - Create `python manage.py watch` command using watchdog library in separate thread; auto-update database entries (add/edit/remove) as input directory files change
12. **Set up performance benchmarking** - Create test harness with 1GB sample library for efficient testing; measure processing throughput and identify bottlenecks using Loguru tracing at high-level functions; validate architecture scales to 100GB+ real-world libraries

### PM Handoff

This Project Brief provides the full context for **Samplify**. The next phase involves translating this brief into a detailed Product Requirements Document (PRD) that specifies user stories, acceptance criteria, and technical implementation details.

**Recommended next step:** Transition to PRD development using the BMAD methodology. The PRD should break down the MVP scope into discrete user stories and engineering tasks, with particular attention to:
- Input Directory Scanner workflow (user triggers scan → database population → tree visualization)
- Database-backed tree viewer with minimal JavaScript (locally served, no CDN dependencies)
- SQLite WAL mode configuration and multiprocessing/threading patterns for Django
- File watcher service as Django management command running in separate thread
- Reuse of existing brownfield ffmpeg integration optimizations
- Cross-platform path handling using pathlib.Path throughout

Review this brief thoroughly, ask for any necessary clarification, and use it as the foundation for creating a comprehensive PRD that guides development.
