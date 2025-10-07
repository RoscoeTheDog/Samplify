# Story Definition of Done (DoD) - Standardized Template

**Version:** 1.0
**Effective Date:** 2025-10-06
**Applies To:** All stories from Epic 1.0 onwards

---

## Purpose

This template defines the **required Definition of Done elements** for all user stories in the Samplify project. Every story must include these checkpoints to ensure consistent quality, maintainability, and adherence to project standards.

---

## Standard DoD Checklist

Copy this checklist into the **Definition of Done** section of every story:

```markdown
## Definition of Done

### Implementation Complete
- [ ] All tasks/subtasks completed
- [ ] All acceptance criteria met
- [ ] All file changes committed to version control

### Code Quality Standards
- [ ] **Coding Standards**: All code adheres to CS1-CS13 (see `docs/architecture/coding-standards/index.md`)
- [ ] **Black**: Code formatted with Black (line length 100)
- [ ] **Pylint**: Pylint score ≥ 8.5/10 with no critical errors
- [ ] **mypy**: Type checking passes without errors
- [ ] **isort**: Imports sorted and organized correctly

### Documentation Standards
- [ ] **Docstrings**: All functions/classes have Google-style docstrings
- [ ] **Type Hints**: All function signatures include type hints
- [ ] **Inline Comments**: Complex logic documented with clear comments
- [ ] **README Updates**: Project documentation updated if needed

### Testing Standards
- [ ] **Unit Tests**: All new code covered by unit tests
- [ ] **Integration Tests**: Integration points tested
- [ ] **Test Coverage**: ≥80% coverage for critical path code
- [ ] **All Tests Pass**: pytest runs without failures or errors

### Performance Validation (if applicable)
- [ ] **NFR Compliance**: Non-functional requirements validated
- [ ] **Performance Benchmarks**: Performance metrics meet acceptance criteria
- [ ] **Load Testing**: Tested under expected load conditions (if applicable)

### Security Review (if applicable)
- [ ] **Security Standards**: No known security vulnerabilities introduced
- [ ] **Input Validation**: All user inputs validated
- [ ] **External Dependencies**: Third-party dependencies verified (checksums, licenses)

### Dev Agent Record Complete
- [ ] Agent model/version documented
- [ ] Debug log references added (if any)
- [ ] Completion notes documented
- [ ] File list updated (created/modified files)

### QA Validation
- [ ] **QA Agent Review**: Story validated by QA agent
- [ ] **QA Results Section**: Populated with validation results
- [ ] **Known Issues**: Any known limitations documented
```

---

## DoD Element Descriptions

### 1. Implementation Complete
**What:** All development work finished
**How to Verify:**
- All checkboxes in Tasks/Subtasks section marked complete
- All Acceptance Criteria validated and met
- All code changes committed to git

**Example:**
```markdown
- [x] Task 1: Create Django model (AC: 1, 2, 3)
- [x] Task 2: Implement API endpoint (AC: 4, 5)
- [x] Task 3: Add unit tests (AC: 6)
```

---

### 2. Code Quality Standards

#### CS1-CS13 Coding Standards
**What:** Project-specific coding standards from architecture docs
**Location:** `docs/architecture/coding-standards/index.md`
**How to Verify:**
- Read coding standards document
- Ensure code follows all 13 standards
- Document any approved exceptions

**Key Standards:**
- CS1: PEP 8 compliance
- CS2: Google-style docstrings
- CS3: Type hints for all functions
- CS4: Error handling patterns
- CS5-CS13: See coding standards doc

#### Black Formatting
**What:** Consistent code formatting
**How to Verify:**
```bash
black . --check --line-length 100
```
**Action if Fails:** Run `black . --line-length 100` to auto-format

#### Pylint Score ≥ 8.5
**What:** Static code analysis quality check
**How to Verify:**
```bash
pylint apps/ samplify/ --fail-under=8.5
```
**Action if Fails:** Fix critical/error issues, document any disabled warnings

#### mypy Type Checking
**What:** Static type checking for type hints
**How to Verify:**
```bash
mypy apps/ samplify/ --ignore-missing-imports
```
**Action if Fails:** Add missing type hints, fix type errors

#### isort Import Organization
**What:** Consistent import ordering
**How to Verify:**
```bash
isort . --check-only
```
**Action if Fails:** Run `isort .` to auto-sort imports

---

### 3. Documentation Standards

#### Google-Style Docstrings
**What:** Comprehensive function/class documentation
**How to Verify:** All public functions/classes have docstrings with:
- Summary line
- Args section (with types)
- Returns section (with type)
- Raises section (if applicable)
- Example section (for complex functions)

**Example:**
```python
def extract_metadata(file_path: Path) -> dict:
    """
    Extract media file metadata using FFmpeg.

    Args:
        file_path: Absolute path to media file

    Returns:
        Dictionary containing:
            - format: File format (e.g., 'WAV', 'MP4')
            - sample_rate: Sample rate in Hz (audio only)
            - bit_depth: Bit depth (audio only)
            - codec: Codec name

    Raises:
        FileNotFoundError: If file does not exist
        FFmpegError: If FFmpeg extraction fails

    Example:
        >>> metadata = extract_metadata(Path("/media/audio.wav"))
        >>> metadata['sample_rate']
        44100
    """
```

#### Type Hints
**What:** Type annotations for all function parameters and return values
**How to Verify:** All function signatures include types
```python
# Good
def process_file(path: Path, schema_id: int) -> bool:

# Bad
def process_file(path, schema_id):
```

---

### 4. Testing Standards

#### Unit Tests
**What:** Tests for individual functions/classes in isolation
**Location:** `tests/test_<module_name>.py`
**Framework:** pytest + pytest-django
**How to Verify:**
```bash
pytest tests/ -v
```

#### Integration Tests
**What:** Tests for interactions between components
**Coverage:** Database operations, API calls, external services
**How to Verify:** Integration tests pass in test suite

#### Test Coverage ≥80%
**What:** Percentage of code covered by tests
**How to Verify:**
```bash
pytest --cov=apps --cov=samplify --cov-report=html --cov-fail-under=80
```
**Action if Fails:** Add tests for uncovered code paths

---

### 5. Performance Validation (when applicable)

#### NFR Compliance
**What:** Non-functional requirements from PRD validated
**Examples:**
- NFR1: CPU utilization 50-70%
- NFR10: File detection latency <10 seconds
- NFR9: Processing success rate ≥95%

**How to Verify:** Run performance benchmarks specified in AC

#### Performance Benchmarks
**What:** Specific performance metrics from acceptance criteria
**How to Verify:** pytest performance tests pass
```bash
pytest tests/test_performance.py -v
```

---

### 6. Security Review (when applicable)

#### Security Standards
**What:** No security vulnerabilities introduced
**Common Checks:**
- No hardcoded secrets/credentials
- Input validation for user inputs
- SQL injection prevention (use ORM)
- XSS prevention (template escaping)
- CSRF protection enabled

**How to Verify:**
- Code review focused on security
- Run security scanner (if available)
- Document any security-sensitive decisions

#### External Dependencies
**What:** Third-party code/binaries verified
**How to Verify:**
- Checksum verification for binaries
- License compatibility checked
- Dependency vulnerabilities scanned

---

### 7. Dev Agent Record Complete

**What:** Implementation documentation for future reference
**Required Sections:**
```markdown
## Dev Agent Record

### Agent Model Used
- Model: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- Implementation Date: 2025-10-06

### Debug Log References
- <Link to debug logs or "None">

### Completion Notes
- <Summary of implementation>
- <Design decisions made>
- <Known limitations>
- <Test results>

### File List
**Created Files:**
- <list of new files>

**Modified Files:**
- <list of changed files>
```

---

### 8. QA Validation

**What:** Independent validation by QA agent
**Required:**
```markdown
## QA Results

**QA Agent:** <Agent name/version>
**QA Date:** 2025-10-06

**Validation Summary:**
- [ ] All acceptance criteria validated
- [ ] Functional testing complete
- [ ] Performance testing complete (if applicable)
- [ ] Security review complete (if applicable)

**Test Results:**
- <Summary of QA tests run>
- <Pass/fail status>
- <Any issues found>

**Known Issues:**
- <List any limitations or bugs>

**Recommendation:**
- [ ] Ready for Production
- [ ] Needs Revision (see issues above)
```

---

## Story Status Transitions

Stories progress through these statuses as DoD elements are completed:

```
Draft
  └─> PO Review Required (AC validated, tasks defined)
      └─> Ready for Development (PO approved)
          └─> In Progress (Dev working)
              └─> Ready for Review (Dev complete, tests passing)
                  └─> QA Validation (QA testing)
                      └─> Ready for Production (All DoD complete)
```

**DoD Requirements by Status:**

| Status | DoD Requirements |
|--------|------------------|
| **Draft** | None (story being written) |
| **PO Review Required** | AC clear, tasks defined |
| **Ready for Development** | PO approved, SM scheduled |
| **In Progress** | Dev working, partial DoD |
| **Ready for Review** | Implementation complete, code quality pass, tests pass |
| **QA Validation** | Dev Agent Record complete |
| **Ready for Production** | **ALL DoD elements complete** |

---

## Exceptions and Waivers

**When DoD elements don't apply:**
- Mark as `[N/A]` with brief explanation
- Example: `[N/A - No Python code in this story]` for Story 1.0 (repository setup)

**PO-Approved Exceptions:**
- Document in story with `[PO APPROVED]` tag
- Example: `[PO APPROVED - Accept 95% functionality, see Story 1.3 notes]`

**Post-MVP Deferrals:**
- Mark as `[POST-MVP]` with backlog item reference
- Example: `[POST-MVP - Issue #2 fix deferred, see BACKLOG.md item #47]`

---

## Validation Commands Quick Reference

```bash
# Code Quality
black . --check --line-length 100
pylint apps/ samplify/ --fail-under=8.5
mypy apps/ samplify/ --ignore-missing-imports
isort . --check-only

# Testing
pytest tests/ -v
pytest --cov=apps --cov=samplify --cov-report=html --cov-fail-under=80

# Django Checks
python manage.py check
python manage.py makemigrations --check --dry-run

# Full Validation (run all checks)
./scripts/validate-story.sh <story_number>
```

---

## Template Usage

### For New Stories
1. Copy the Standard DoD Checklist section into your story
2. Add story-specific items if needed (e.g., "NFR10 latency <10s validated")
3. Mark `[N/A]` for inapplicable items

### For Existing Stories (Retroactive Application)
1. Add Standard DoD Checklist to existing stories
2. Validate all implemented code against checklist
3. Document any violations with action plan
4. Update story status based on DoD completion

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-10-06 | 1.0 | Initial DoD template created from Sprint Change Proposal | PO (Sarah) |

---

## References

- **Coding Standards:** `docs/architecture/coding-standards/index.md`
- **Testing Strategy:** `docs/architecture/testing-strategy.md`
- **Story Template:** `.bmad-core/templates/story-tmpl.yaml`
- **Sprint Change Proposal:** (This retrospective review document)
