# Epic and Story Structure

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
