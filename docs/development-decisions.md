# Development Decisions - Samplify Django Migration

**Date:** 2025-10-05
**Product Owner/Developer:** User
**Documented By:** Scrum Master (Bob)

---

## Purpose

This document captures key technical decisions made by the Product Owner to guide development agents during implementation of Stories 1.5-1.17. These decisions resolve ambiguities and provide clear direction for critical requirements (CR1, CR2, CR4) and NFRs.

---

## Decision Summary

### 1. Brownfield Code Access ✓

**Decision:** Brownfield codebase is available in project root `.\handlers\` directory

**Key Files:**
- `.\handlers\rules.py` - Algorithm preservation source (CR1)
- `.\handlers\process_handler.py` - Multiprocessing patterns (CR2)
- Other handler files as needed

**Implication for Dev Agents:**
- Read brownfield code before implementing Stories 1.5 and 1.6
- Preserve exact algorithm behavior (100% identical output)
- Port multiprocessing patterns exactly (CR2 requirement)

---

### 2. Algorithm Preservation Strategy (CR1) ✓

**Decision:** Specific algorithms MUST work identically to brownfield

**Approach:**
- Extract algorithms from `.\handlers\rules.py`
- Create side-by-side test validation
- Require 100% identical output for test cases
- Test cases will be extracted from brownfield or provided by PO

**Functions Requiring Exact Preservation:**
1. `contains_expression()` - Keyword/regex matching
2. `contains_extensions()` - File extension filtering
3. `between_datetime()` - Date range filtering
4. `contains_audio()` - Audio file detection
5. `contains_video()` - Video file detection

**Verification Method:**
- Automated test suite with brownfield test cases
- Side-by-side comparison (brownfield vs Django implementation)
- Assert exact match for all test files

---

### 3. Performance Requirements ✓

**Decision:** Rough targets OK - use multiprocessing efficiently, informal measurement

**Targets:**
- CPU Utilization: 50-70% during batch processing (informal monitoring)
- Worker Scaling: One worker per CPU core (strict requirement)
- Processing Speed: Reasonable throughput, no formal benchmarking required
- Memory Usage: Monitor but no strict limits for v1

**Testing Approach:**
- Verify multiprocessing working (all cores utilized)
- Spot-check CPU usage with system monitor
- No formal performance benchmarking suite required for v1
- Can optimize based on real-world usage

---

### 4. Error Recovery & Service Behavior ✓

**Decision:** Robust - auto-restart, retry 3x, persist state

**Error Recovery Policy:**

**Queue Processor (Story 1.8):**
- On processing failure: Retry file 3 times before marking `failed`
- On crash mid-batch: Reset interrupted files to `pending` status
- Failed files: Log error, mark status `failed`, continue processing queue

**Watchdog Services (Story 1.13):**
- Service persistence: Store state in database (ServiceStatus model)
- Auto-restart: Services restart on Django server reboot
- Crash recovery: Auto-restart service immediately on crash
- Health monitoring: Check service status every 30 seconds

**Database Errors:**
- Connection errors: Retry with exponential backoff (max 5 retries)
- Lock timeouts: Skip locked files, retry next poll
- Transaction failures: Rollback, log error, continue

**FFmpeg Errors:**
- Processing errors: Mark file `failed`, log error details
- Binary not found: Block operation, alert user
- Timeout: 5 minutes per file, then mark failed

---

### 5. Testing & Validation Scope ✓

**Decision:** Comprehensive - 80% coverage, stability tests, multi-platform validation

**Test Coverage Requirements:**

**Overall Target:** 80% code coverage (critical paths 100%)

**Story-Specific Coverage:**
- Story 1.5 (CR1): 100% coverage for algorithm preservation
- Story 1.6 (CR2): 100% coverage for multiprocessing
- Stories 1.7-1.16: 80% minimum
- Story 1.17: Comprehensive integration test suite

**Test Categories Required:**

1. **Unit Tests**
   - All critical functions covered
   - Edge cases tested
   - Error handling validated

2. **Integration Tests**
   - End-to-end workflows
   - Database operations
   - Service coordination

3. **Performance Tests** (Story 1.17)
   - CPU utilization validation (informal)
   - Worker pool scaling
   - 1000+ file processing test

4. **Stability Tests**
   - 24-hour continuous operation test (Stories 1.8, 1.13)
   - Memory leak detection
   - Graceful shutdown validation

5. **Cross-Platform Tests**
   - Test on Windows, macOS, Linux
   - Path handling validation
   - Subprocess management per platform

**Test Framework:**
- pytest + pytest-django
- Coverage reporting with pytest-cov
- HTML coverage reports generated

---

## Implementation Guidance by Story

### Story 1.5 - File Scanning Service (CR1)

**Approach:**
1. Read `.\handlers\rules.py`
2. Extract 5 filter functions
3. Implement in `samplify/utils/search.py` (utility module pattern)
4. Create side-by-side test harness
5. Validate 100% identical output

**Test Cases:**
- Extract from brownfield or PO provides
- Minimum 100 test files per algorithm
- Cover all filter types and edge cases

---

### Story 1.6 - Batch Processing (CR2)

**Approach:**
1. Read `.\handlers\process_handler.py` lines 26-48
2. Preserve worker scheduling pattern exactly:
   - `multiprocessing.cpu_count()` for core detection
   - `collections.deque()` per worker (NOT queue.Queue)
   - `daemon=True` flag on processes
   - Round-robin job distribution
3. Integrate with Django File model
4. Informal CPU monitoring during testing

**Allowed Changes:**
- Replace structlog with loguru
- Add Django ORM queries
- Add Django cache for state management

**Not Allowed:**
- Change from deque to queue
- Modify worker pool size calculation
- Change daemon flag

---

### Story 1.8 - Queue Processor

**Implementation:**
- Use `select_for_update(skip_locked=True)` for race condition prevention
- Retry logic: 3 attempts with exponential backoff
- Database state: Track retry count per file
- Crash recovery: Reset `processing` → `pending` on startup

---

### Story 1.12 - Properties Panel (CR4)

**Implementation:**
- Support all 5 XML rule types (keyword, extension, media_type, attribute, date_range)
- Auto-save: 500ms debounce
- Form validation: Prevent invalid rules (e.g., sample rate > 192000)

---

### Story 1.13 - Watchdog Control Panel

**Implementation:**
- ServiceStatus model for persistence
- Auto-restart on Django boot (AppConfig.ready())
- Cross-platform subprocess:
  - Windows: `taskkill /PID /F`
  - Unix: `SIGTERM` → wait 5s → `SIGKILL`

---

### Story 1.17 - Integration Testing

**Implementation:**
- Create comprehensive test suite
- Side-by-side CR1 validation
- 24-hour stability test (can run async, not blocking release)
- Cross-platform testing on VMs
- 80% coverage enforced in CI (if configured)

---

## Critical Decisions Made (2025-10-05)

### CR1: Bug in `contains_extensions()` Line 33 ✅ **RESOLVED**
**Issue:** Brownfield code has `extension.translate()` with no assignment - unclear purpose
**Investigation:** Complete analysis at `docs/architecture/cr1-extension-bug-analysis.md`
**Test Results:** Isolated testing shows no functional impact when `extension` is a string
**Decision:** **PRESERVE EXACTLY AND TEST POST-MIGRATION** (Option A)
**Rationale:**
- Cannot determine full runtime behavior without testing actual brownfield system
- Possible that `extension` could be a list in certain runtime contexts (sorting feature?)
- CR1 requires exact preservation - safest approach until proven otherwise
- Line 33 may serve a purpose we haven't discovered yet
**Implementation:**
- Copy line 33 exactly with inline comment: `# CR1: Purpose unclear - preserved for post-migration validation`
- Add to Story 1.17 test suite: Runtime comparison test for extension filtering
- Validate behavior with actual brownfield data after migration complete

### CR2: Task Distribution Algorithm
**Issue:** Brownfield uses greedy assignment (first empty queue) with TODO noting inefficiency
**Decision:** **IMPROVE TO ROUND-ROBIN** (Option B approved by PO)
**Rationale:** Better load balancing, TODO suggests improvement was intended
**Implementation:** Cycle through workers instead of using first available

### Testing Strategy
**Decision:**
- No brownfield unit tests exist, only runtime tests performed previously
- Use sample media from `\media\` folder in project directory
- **CRITICAL:** Do NOT destructively edit original sample media
- Output test results to NEW directory in project (e.g., `test_output/`)
- Add output folder to `.gitignore`

**Test Infrastructure Setup Required:**
1. Create `test_output/` directory for processed files
2. Update `.gitignore` with test output paths
3. Use `\media\` samples as read-only test fixtures
4. Create side-by-side validation harness

---

## Deferred Decisions (Can Be Made During Implementation)

The following minor decisions can be made by dev agents using reasonable defaults:

**Story 1.9 - XML Import/Export:**
- XML schema validation: Validate against structure, allow with warning on minor errors
- Conflict resolution: Prompt user (merge/replace)
- Export format: Human-readable with indentation

**Story 1.11 - Directory Tables:**
- File browser fallback: Text input if `webkitdirectory` not supported
- Path truncation: Max 50 chars, show first and last segments

**Story 1.14 - AJAX Endpoints:**
- Polling frequency: 2 seconds default, configurable later if needed
- Caching: 304 Not Modified with 2-second TTL

**Story 1.16 - Setup Script:**
- Offline installation: Not supported in v1
- FFmpeg cache: Download to project `cache/` directory

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-05 | Initial decisions documented | SM (Bob) |

---

## Notes

- This document is the **single source of truth** for development decisions
- Dev agents MUST reference this before implementing high-risk stories
- Update this document if decisions change during implementation
- PO can override any decision at any time (document in Change Log)
