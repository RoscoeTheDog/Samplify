# Implementation Checklists

**Version:** 1.0
**Last Updated:** 2025-10-04
**Purpose:** Per-story implementation and quality checklists

---

## How to Use This Document

Each story has three checklists:
1. **Pre-Implementation** - Before you start coding
2. **Implementation** - During development
3. **Pre-Merge** - Before merging to dev

**Usage:**
- Copy checklist for your story
- Track progress in your feature branch
- Complete all items before merging

---

## Universal Pre-Implementation Checklist

**Complete BEFORE starting any story:**

- [ ] Read story file (`docs/stories/story-XX-....md`)
- [ ] Review related architecture documents
- [ ] Understand acceptance criteria
- [ ] Check dependencies (which stories must complete first)
- [ ] Create feature branch (`git checkout -b feature/story-X.X-name`)
- [ ] Activate virtual environment (`source venv/bin/activate`)
- [ ] Pull latest from dev (`git pull origin dev`)
- [ ] Verify tests pass (if any exist)

---

## Universal Implementation Checklist

**Complete DURING implementation:**

### Code Quality (CS1-CS13)

- [ ] **CS1**: PEP 8 compliant (120 char line length)
- [ ] **CS2**: Type hints on all function signatures
- [ ] **CS3**: Google-style docstrings on all public functions/classes
- [ ] **CS4**: Comments every 5-10 lines for complex logic
- [ ] **CS5**: Human-readable variable names (no abbreviations)
- [ ] **CS6**: Black formatting applied
- [ ] **CS7**: Imports organized with isort (Django profile)
- [ ] **CS8**: Functions < 50 lines (refactor if longer)
- [ ] **CS9**: Explicit exception types with detailed error messages
- [ ] **CS10**: Django ORM optimization (select_related, prefetch_related)
- [ ] **CS11**: Algorithm preservation documented (if applicable)
- [ ] **CS12**: Visual code organization (section dividers, blank lines)
- [ ] **CS13**: Code review checklist items passed

### Testing

- [ ] Unit tests written for new functions
- [ ] Integration tests for API endpoints (if applicable)
- [ ] Edge cases tested
- [ ] Error handling tested
- [ ] All tests pass (`python manage.py test`)

### Documentation

- [ ] Inline code comments for complex logic
- [ ] Docstrings updated
- [ ] README updated (if setup changes)
- [ ] Architecture docs updated (if design changes)

---

## Universal Pre-Merge Checklist

**Complete BEFORE merging to dev:**

### Code Quality

- [ ] `black .` ran successfully
- [ ] `isort .` ran successfully
- [ ] `pylint apps/` score ≥ 8.5/10
- [ ] `mypy apps/` passes with no errors
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)

### Testing

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Manual testing completed per story acceptance criteria
- [ ] No regressions (existing functionality still works)

### Git

- [ ] Commits follow conventional commit format
- [ ] Commit messages are descriptive
- [ ] No merge conflicts with dev
- [ ] Feature branch up-to-date with dev

### Story Completion

- [ ] All acceptance criteria met
- [ ] All technical notes addressed
- [ ] Definition of Done satisfied
- [ ] Story file marked complete

### Merge Process

- [ ] Checkout dev: `git checkout dev`
- [ ] Pull latest: `git pull origin dev`
- [ ] Merge feature: `git merge feature/story-X.X-name`
- [ ] Run full test suite
- [ ] Push to remote: `git push origin dev`
- [ ] Delete feature branch: `git branch -d feature/story-X.X-name`

---

## Story-Specific Checklists

### Story 1.0: Repository & Environment Foundation

**Pre-Implementation:**
- [ ] Read brownfield analysis (`docs/architecture/technical-debt-and-known-issues.md`)
- [ ] Understand current Python dependencies (inferred from imports)
- [ ] Review coding standards (CS1-CS13)

**Implementation:**
- [ ] Create `requirements.txt` with all dependencies
- [ ] Update `.gitignore` with patterns (venv/, *.pyc, __pycache__, etc.)
- [ ] Create `.env.example` template
- [ ] Create `pyproject.toml` with Black/isort/mypy config
- [ ] Create `.pylintrc` with custom rules
- [ ] Create `.pre-commit-config.yaml`
- [ ] Test venv creation: `python -m venv venv`
- [ ] Test dependency install: `pip install -r requirements.txt`
- [ ] Verify all imports work

**Pre-Merge:**
- [ ] `requirements.txt` installs cleanly on fresh venv
- [ ] `.gitignore` excludes all temporary files
- [ ] Pre-commit hooks install successfully
- [ ] Documentation in DEVELOPMENT_SETUP.md tested

---

### Story 1.1: Django Project Setup & Configuration

**Pre-Implementation:**
- [ ] Story 1.0 completed and merged
- [ ] Review Django project structure (`docs/architecture/source-tree.md`)
- [ ] Read NFR5 (centralized configuration in settings.py)

**Implementation:**
- [ ] Run `django-admin startproject samplify .`
- [ ] Create `apps/` directory structure
- [ ] Configure `settings.py` (DATABASES, STATIC_FILES, etc.)
- [ ] Create base templates in `frontend/templates/`
- [ ] Set up static files directory (`frontend/static/`)
- [ ] Configure logging (Loguru integration)
- [ ] Create `manage.py` wrapper if needed
- [ ] Test server starts: `python manage.py runserver`
- [ ] Test static files serve correctly

**Pre-Merge:**
- [ ] Django dev server runs without errors
- [ ] Static files accessible at `/static/`
- [ ] Base template renders
- [ ] No security warnings in console
- [ ] `python manage.py check` passes

---

### Story 1.2A: File Model (Single-Table Inheritance)

**Pre-Implementation:**
- [ ] Story 1.1 completed
- [ ] Review database schema design (`docs/architecture/database-schema-design.md`)
- [ ] Read NFR12 (single-table inheritance requirement)
- [ ] Review brownfield models (`docs/architecture/data-models-and-apis.md`)

**Implementation:**
- [ ] Create `apps/catalog/models.py`
- [ ] Implement `File` model with media_type discriminator
- [ ] Add all metadata fields (audio/video/image)
- [ ] Implement UID auto-generation in save()
- [ ] Create indexes for performance
- [ ] Add model Meta configuration
- [ ] Write __str__ method
- [ ] Create initial migration: `python manage.py makemigrations`
- [ ] Apply migration: `python manage.py migrate`
- [ ] Test model in Django shell

**Pre-Merge:**
- [ ] Migration applies cleanly
- [ ] All brownfield metadata fields present
- [ ] UID generation works
- [ ] Indexes created
- [ ] Model admin registered (if applicable)
- [ ] Unit tests pass

---

### Story 1.4: FFmpeg Detection & Download Service

**Pre-Implementation:**
- [ ] Review FFmpeg integration design (`docs/architecture/ffmpeg-integration.md`)
- [ ] Read FR7 (auto-download requirement)
- [ ] Read CR6 (cross-platform requirement)

**Implementation:**
- [ ] Create `apps/processing/services/ffmpeg_service.py`
- [ ] Implement `detect_platform()` method
- [ ] Implement `get_binary_path()` with pathlib.Path
- [ ] Implement `verify_ffmpeg()` with subprocess test
- [ ] Implement `download_ffmpeg()` with urllib
- [ ] Implement `_organize_extracted_files()` helper
- [ ] Create Django management command `setup.py`
- [ ] Create `bin/` directory structure
- [ ] Test on Windows (if applicable)
- [ ] Test on macOS (if applicable)
- [ ] Test on Linux (if applicable)

**Pre-Merge:**
- [ ] FFmpeg auto-download works
- [ ] Platform detection correct
- [ ] Binary path resolution cross-platform
- [ ] `python manage.py setup` runs successfully
- [ ] FFmpeg version command executes
- [ ] Error messages clear and actionable

---

### Story 1.6: Batch Processing Management Command

**Pre-Implementation:**
- [ ] Stories 1.2A, 1.2B, 1.4, 1.5 completed
- [ ] Review multiprocessing patterns (`docs/architecture/integration-points.md`)
- [ ] Read CR2 (preserve multiprocessing orchestration)
- [ ] Review brownfield `handlers/process_handler.py`

**Implementation:**
- [ ] Create `apps/processing/management/commands/batch_process.py`
- [ ] Implement worker pool spawning (one per CPU core)
- [ ] Implement deque-based job distribution (CR2 pattern)
- [ ] Preserve core allocation logic
- [ ] Integrate with File model queries
- [ ] Implement progress tracking
- [ ] Add command line arguments (--schema-id, --dry-run, etc.)
- [ ] Test with small file set
- [ ] Test with large file set (100+ files)
- [ ] Verify 50-70% CPU utilization (NFR1)

**Pre-Merge:**
- [ ] Command executes without errors
- [ ] Multiprocessing workers spawn correctly
- [ ] Files process successfully
- [ ] Progress tracking accurate
- [ ] CPU utilization meets NFR1
- [ ] No database locking issues (WAL mode working)

---

### Story 1.10: Schema Management UI (CRUD)

**Pre-Implementation:**
- [ ] Stories 1.1, 1.2B completed
- [ ] Review frontend components (`docs/architecture/frontend-components.md`)
- [ ] Review API endpoints (`docs/architecture/api-endpoints.md`)

**Implementation:**
- [ ] Create `apps/schemas/views.py` with CRUD views
- [ ] Create `apps/schemas/forms.py` for schema forms
- [ ] Create templates in `apps/schemas/templates/schemas/`
- [ ] Implement list view (GET /schemas/)
- [ ] Implement detail view (GET /schemas/<id>/)
- [ ] Implement create view (POST /schemas/)
- [ ] Implement update view (PUT /schemas/<id>/)
- [ ] Implement delete view (DELETE /schemas/<id>/)
- [ ] Add CSRF protection
- [ ] Add form validation
- [ ] Test CRUD operations manually

**Pre-Merge:**
- [ ] All CRUD operations work
- [ ] Forms validate correctly
- [ ] CSRF protection active
- [ ] Templates render properly
- [ ] Error messages display
- [ ] Success messages display

---

### Story 1.14: AJAX Progress Monitoring Endpoints

**Pre-Implementation:**
- [ ] Story 1.6 (batch processing) completed
- [ ] Review API endpoints (`docs/architecture/api-endpoints.md`)
- [ ] Read NFR4 (1-2 second polling requirement)

**Implementation:**
- [ ] Create `apps/processing/views/batch.py`
- [ ] Implement `/api/batch/<batch_id>/status/` endpoint
- [ ] Return JSON with progress data
- [ ] Include percent_complete, files_processed, current_file
- [ ] Add CPU utilization to response
- [ ] Implement error handling
- [ ] Test polling with AJAX
- [ ] Verify 2-second poll interval works
- [ ] Test with multiple concurrent batches

**Pre-Merge:**
- [ ] Endpoint returns valid JSON
- [ ] Progress data accurate
- [ ] Polling works smoothly (no lag)
- [ ] Handles concurrent requests
- [ ] CORS configured if needed

---

### Story 1.17: Integration Testing & Validation

**Pre-Implementation:**
- [ ] ALL previous stories (1.0-1.16) completed
- [ ] Review coding standards (CS1-CS13)
- [ ] Review compatibility requirements (CR1-CR6)

**Implementation:**
- [ ] Create integration test suite
- [ ] Test full workflow: scan → preview → batch process
- [ ] Validate algorithm preservation (CR1)
- [ ] Benchmark multiprocessing performance (CR2, NFR1)
- [ ] Test SQLite WAL concurrent access (NFR2)
- [ ] Verify local static files (NFR3)
- [ ] Test AJAX polling (NFR4)
- [ ] Cross-platform testing (Windows/macOS/Linux)
- [ ] Load testing (1000+ files)
- [ ] Regression testing (brownfield comparison)

**Pre-Merge:**
- [ ] All integration tests pass
- [ ] Performance meets NFR1 (50-70% CPU)
- [ ] No regressions from brownfield
- [ ] Cross-platform validation complete
- [ ] Load testing passed
- [ ] Documentation complete

---

## Testing Checklists

### Unit Testing Checklist

- [ ] Test file created (`tests/test_<module>.py`)
- [ ] All public functions have test coverage
- [ ] Edge cases tested (empty input, None, invalid types)
- [ ] Error conditions tested (exceptions raised correctly)
- [ ] Mock external dependencies (FFmpeg, filesystem, etc.)
- [ ] Assertions clear and specific
- [ ] Test names descriptive (`test_function_name_condition_expected_result`)

### Integration Testing Checklist

- [ ] End-to-end workflow tested
- [ ] Database interactions tested
- [ ] API endpoints tested with requests
- [ ] Form submissions tested
- [ ] File uploads/downloads tested
- [ ] Multiprocessing tested
- [ ] Watchdog services tested

### Manual Testing Checklist

- [ ] Happy path tested (normal workflow)
- [ ] Error paths tested (invalid input, missing files, etc.)
- [ ] UI interactions tested (buttons, forms, tables)
- [ ] AJAX polling tested (real-time updates)
- [ ] Cross-browser tested (Chrome, Firefox, Safari)
- [ ] Responsive design tested (if applicable)

---

## Code Review Checklist

### Reviewer Checklist

**Before approving merge, verify:**

- [ ] Code follows CS1-CS13 coding standards
- [ ] All functions have type hints and docstrings
- [ ] Comments explain "why" not just "what"
- [ ] Variable names are explicit and readable
- [ ] No code duplication (DRY principle)
- [ ] Error handling comprehensive
- [ ] Tests cover new functionality
- [ ] No security vulnerabilities (SQL injection, XSS, etc.)
- [ ] Performance acceptable (no N+1 queries, etc.)
- [ ] Documentation updated
- [ ] Commit messages clear

### Algorithm Preservation Review (CR1/CR2)

**For stories involving brownfield algorithm ports:**

- [ ] Original algorithm identified in brownfield code
- [ ] Header comment references original location
- [ ] Logic flow preserved exactly
- [ ] Only allowed adaptations made:
  - [ ] Import statement changes (SQLAlchemy → Django ORM)
  - [ ] Method signature adaptations
  - [ ] Variable renaming for Django conventions
- [ ] No performance optimizations added
- [ ] No code restructuring
- [ ] Test validates output matches brownfield

---

## Definition of Done (DoD)

**A story is DONE when:**

### Code Complete
- [ ] All acceptance criteria met
- [ ] All technical notes addressed
- [ ] Code follows coding standards (CS1-CS13)
- [ ] No TODO comments left in code
- [ ] No debug print statements

### Testing Complete
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Manual testing completed
- [ ] Edge cases tested
- [ ] Performance validated

### Documentation Complete
- [ ] Code documented (docstrings, comments)
- [ ] Architecture docs updated if design changed
- [ ] README updated if setup changed
- [ ] API docs updated if endpoints added

### Quality Checks Pass
- [ ] Black formatting applied
- [ ] isort imports organized
- [ ] Pylint score ≥ 8.5/10
- [ ] Mypy type checking passes
- [ ] Pre-commit hooks pass

### Merged to Dev
- [ ] Feature branch merged to dev
- [ ] No merge conflicts
- [ ] All tests pass on dev
- [ ] Feature branch deleted

---

## Quick Reference Commands

```bash
# Before starting
git checkout dev
git pull origin dev
git checkout -b feature/story-X.X-name
source venv/bin/activate

# During implementation
python manage.py test                    # Run tests
black .                                  # Format code
isort .                                  # Sort imports
pylint apps/                             # Lint
mypy apps/                               # Type check
pre-commit run --all-files               # Run all hooks

# Before merge
git checkout dev
git pull origin dev
git merge feature/story-X.X-name
python manage.py test                    # Verify
git push origin dev
git branch -d feature/story-X.X-name
```

---

**Use these checklists to ensure high-quality, consistent implementation across all stories!** ✅
