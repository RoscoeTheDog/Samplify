# Developer Handoff - Stories 1.5-1.17

**Date:** 2025-10-05
**Scrum Master:** Bob
**Status:** ✅ All stories APPROVED and ready for implementation

---

## Executive Summary

All stories (1.5-1.17) have been reviewed and are **ready for developer agent implementation**.

**Critical Decisions Documented:**
- CR1 Algorithm Preservation: Line 33 in `contains_extensions()` preserved exactly (see `docs/development-decisions.md`)
- CR2 Multiprocessing: Round-robin improvement approved for task distribution
- Testing Infrastructure: Use `\media\` samples, output to `test_output/` directory

---

## Story Compliance Status

### ✅ All Stories Approved

| Story | Title | Status | Compliance |
|-------|-------|--------|------------|
| 1.5 | File Scanning Service (CR1) | Approved | ✅ Ready |
| 1.6 | Batch Processing Command (CR2) | Approved | ✅ Ready |
| 1.7 | File Monitor Watchdog | Approved | ✅ Ready |
| 1.8 | Queue Processor Watchdog | Approved | ✅ Ready |
| 1.9 | XML Template Import/Migration | Approved | ✅ Ready |
| 1.10 | Schema Management UI (CRUD) | Approved | ✅ Ready |
| 1.11 | Dual Directory Table Layout | Approved | ✅ Ready |
| 1.12 | Properties Panel (Filter/Rule CRUD) | Approved | ✅ Ready |
| 1.13 | Watchdog Control Panel UI | Approved | ✅ Ready |
| 1.14 | AJAX Progress Monitoring | Approved | ✅ Ready |
| 1.15 | Dual Queue Visualization (UID Filtering) | Approved | ✅ Ready |
| 1.16 | Complete Setup Script | Approved | ✅ Ready |
| 1.17 | Integration Testing & Validation | Approved | ✅ Ready |

---

## Required Reading for Developer

### Critical Documents (MUST READ)

1. **`docs/development-decisions.md`** - All PO/Developer decisions
   - CR1: Line 33 preservation strategy
   - CR2: Round-robin improvement
   - Testing infrastructure setup

2. **`docs/architecture/brownfield-analysis.md`** - CR1/CR2 preservation requirements
   - 5 filter functions requiring exact preservation
   - Multiprocessing patterns from process_handler.py
   - Known bugs and decisions

3. **`docs/architecture/cr1-extension-bug-analysis.md`** - Line 33 investigation
   - Why line 33 must be preserved
   - Post-migration validation required

### High-Risk Stories (Implement with Extra Care)

**Story 1.5 (CR1):**
- Preserve 5 filter functions EXACTLY from `handlers/rules.py`
- Line 33 in `contains_extensions()` MUST be copied exactly
- Add inline comment: `# CR1: Purpose unclear - preserved for post-migration validation`
- See brownfield-analysis.md lines 19-214

**Story 1.6 (CR2):**
- Preserve multiprocessing pattern from `handlers/process_handler.py` lines 26-48
- Use `collections.deque()` NOT `queue.Queue`
- **APPROVED CHANGE:** Implement round-robin (not greedy assignment)
- See brownfield-analysis.md lines 260-356

---

## Recommended Implementation Order

### Phase 1: Low-Risk Foundation (Stories 1.7, 1.10, 1.15, 1.16)
**Why first:** No brownfield preservation requirements, well-defined patterns

1. Story 1.7 - File Monitor Watchdog
2. Story 1.10 - Schema Management UI
3. Story 1.15 - Dual Queue Visualization
4. Story 1.16 - Complete Setup Script

### Phase 2: High-Risk Core (Stories 1.5, 1.6)
**Why second:** Requires CR1/CR2 decisions, brownfield preservation

5. Story 1.5 - File Scanning Service (CR1 - use brownfield-analysis.md)
6. Story 1.6 - Batch Processing (CR2 - use brownfield-analysis.md)

### Phase 3: Robust Features (Stories 1.8, 1.12, 1.13)
**Why third:** Depends on Stories 1.5/1.6 integration

7. Story 1.8 - Queue Processor Watchdog
8. Story 1.12 - Properties Panel
9. Story 1.13 - Watchdog Control Panel

### Phase 4: Integration & Polish (Stories 1.9, 1.11, 1.14)
**Why fourth:** Medium complexity, integrates multiple stories

10. Story 1.9 - XML Template Import
11. Story 1.11 - Dual Directory Table
12. Story 1.14 - AJAX Progress Monitoring

### Phase 5: Validation (Story 1.17)
**Why last:** Tests all previous stories

13. Story 1.17 - Integration Testing & Validation
    - **CRITICAL:** Add runtime validation test for contains_extensions() line 33
    - Side-by-side comparison with brownfield
    - 24-hour stability tests

---

## Test Infrastructure Setup

### Already Complete ✅

1. `test_output/` directory created
2. `.gitignore` updated to exclude test output
3. Sample media available in `\media\` folder (READ-ONLY)

### Developer Responsibilities

- Use `\media\` samples for testing (DO NOT modify originals)
- Output test results to `test_output/`
- Create side-by-side validation harness for CR1 functions
- 80% code coverage minimum (100% for CR1/CR2 critical paths)

---

## Critical Implementation Notes

### CR1: Algorithm Preservation

**MUST PRESERVE EXACTLY:**
1. `contains_expression()` - handlers/rules.py lines 10-23
2. `contains_extensions()` - handlers/rules.py lines 26-42 (INCLUDING LINE 33!)
3. `between_datetime()` - handlers/rules.py lines 45-72
4. `contains_audio()` - handlers/rules.py lines 88-98
5. `contains_video()` - handlers/rules.py lines 75-85
6. `contains_image()` - handlers/rules.py lines 101-111

**ALLOWED CHANGES:**
- Django ORM instead of SQLAlchemy
- File object attribute mapping (e.g., `file.extension` → `file.file_format`)
- Import statements

**NOT ALLOWED:**
- Changing regex patterns, logic operators, case sensitivity
- Removing or modifying line 33 in contains_extensions()
- Changing delta-based date logic in between_datetime()

### CR2: Multiprocessing Preservation

**MUST PRESERVE:**
- `multiprocessing.cpu_count()` for core detection
- `collections.deque()` per worker (NOT queue.Queue)
- `daemon=True` flag on processes
- Channel tuple pattern: `(process.name, deque)`

**APPROVED IMPROVEMENT:**
- Change task distribution from greedy (first available) to round-robin
- See development-decisions.md for rationale

---

## Success Criteria

### Definition of Done (All Stories)

- [ ] All acceptance criteria met
- [ ] Code follows Django patterns and coding standards
- [ ] 80% test coverage (100% for CR1/CR2)
- [ ] Documentation updated (inline comments, docstrings)
- [ ] No regressions in existing functionality
- [ ] Scrum Master approval

### Story-Specific DoD

**Story 1.5 (CR1):**
- [ ] Side-by-side test validates 100% identical output to brownfield
- [ ] Line 33 preserved with inline comment
- [ ] All 5 filter functions tested

**Story 1.6 (CR2):**
- [ ] Worker scaling test: One process per CPU core
- [ ] Deque validation: NOT using queue.Queue
- [ ] Round-robin distribution verified

**Story 1.17 (Integration):**
- [ ] Runtime validation of line 33 with actual brownfield data
- [ ] 24-hour stability test passed
- [ ] Cross-platform tests (Windows/macOS/Linux)

---

## Developer Agent Instructions

1. **Read all critical documents first** (development-decisions.md, brownfield-analysis.md)
2. **Follow recommended implementation order** (Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5)
3. **For Stories 1.5 and 1.6:** Reference brownfield-analysis.md for exact line numbers
4. **Mark todos as completed after each story**
5. **Run compliance checks before marking story complete**
6. **For Story 1.17:** Add line 33 runtime validation test

---

## Questions or Issues?

**For CR1/CR2 decisions:** See docs/development-decisions.md
**For brownfield patterns:** See docs/architecture/brownfield-analysis.md
**For line 33 investigation:** See docs/architecture/cr1-extension-bug-analysis.md
**For testing strategy:** See test_output/ directory and \media\ samples

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-05 | Initial handoff document created | SM (Bob) |
| 2025-10-05 | All stories 1.7-1.17 compliance verified | SM (Bob) |
| 2025-10-05 | CR1/CR2 decisions documented | PO/Dev |

---

## Scrum Master Sign-Off

**Status:** ✅ APPROVED FOR IMPLEMENTATION

All stories meet BMad methodology requirements:
- ✅ Status: Approved
- ✅ User Story: Present and well-formed
- ✅ Acceptance Criteria: Complete
- ✅ Tasks/Subtasks: Detailed
- ✅ Dev Notes: Comprehensive
- ✅ Definition of Done: Present
- ✅ Risk Assessment: Present

**Scrum Master:** Bob
**Date:** 2025-10-05
