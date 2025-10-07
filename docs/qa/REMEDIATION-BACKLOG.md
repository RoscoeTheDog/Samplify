# Remediation Backlog: Stories 1.1-1.9

**Created**: 2025-10-06
**Architect**: Winston
**Source**: Retroactive QA Review (Stories 1.1-1.9)
**Total Estimated Effort**: 10 hours (immediate) + ongoing monitoring
**Priority**: Complete Phase 1 before production deployment

---

## Overview

This backlog contains remediation work identified during the retroactive architectural review of Stories 1.1-1.9. Work is organized into three phases:

- **Phase 1**: Critical fixes (4 hours) - MUST complete before production
- **Phase 2**: Technical debt (6 hours) - SHOULD complete before MVP
- **Phase 3**: Optional enhancements - Nice-to-have improvements

---

## Phase 1: Critical Fixes (Pre-Production Required)

**Total Effort**: 4 hours
**Deadline**: Before production deployment
**Risk**: HIGH - Production blockers

### Story R1.1: Document NFR13 Admin Framework Decision

**Priority**: 🔴 HIGH
**Effort**: 1 hour
**Assigned To**: [Architect + PO]
**Related Stories**: 1.1, 1.2A, 1.2B

**Context**:
Story 1.1 AC#8 disabled authentication (NFR13: "open local interface"), but Stories 1.2A/1.2B required Django admin for AC compliance. QA retroactively re-enabled admin as "developer tooling" without PRD amendment. This creates architectural ambiguity.

**Tasks**:
- [ ] Review NFR13 original intent with Product Owner
- [ ] Choose architectural approach (see options below)
- [ ] Create ADR-001 documenting decision
- [ ] Update NFR13 in requirements.md if needed
- [ ] Update Story 1.1 with ADR reference
- [ ] Update settings.py with code comments explaining decision

**Architectural Options**:

**Option A: Admin as Developer Tooling (RECOMMENDED)**
```python
# settings.py
# ADR-001: Admin framework enabled for developer tooling only
# NFR13 "no end-user authentication" excludes Django admin (internal tooling)
# See docs/architecture/decisions/ADR-001-admin-framework.md
INSTALLED_APPS = [
    'django.contrib.admin',  # Developer tooling only
    'django.contrib.auth',   # Required by admin
    # ...
]
```
- **Pros**: Maintains admin interface for Stories 1.2A/1.2B compliance
- **Cons**: Requires NFR13 clarification in PRD
- **Action**: Update NFR13 to "No end-user authentication (admin is internal tooling)"

**Option B: Strict NFR13 - Remove Admin**
```python
# settings.py
# ADR-001: Strict NFR13 compliance - no authentication framework
INSTALLED_APPS = [
    # 'django.contrib.admin',  # Disabled per NFR13
    # 'django.contrib.auth',   # Disabled per NFR13
    # ...
]
```
- **Pros**: Pure NFR13 compliance
- **Cons**: Requires rework of Stories 1.2A/1.2B (remove admin AC)
- **Action**: Use Django shell or custom debug views instead

**Option C: Environment-Based Admin**
```python
# settings.py
# ADR-001: Environment-based admin (DEBUG mode only)
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
]

if DEBUG:  # Admin only in development
    INSTALLED_APPS += [
        'django.contrib.admin',
        'django.contrib.auth',
    ]
```
- **Pros**: Best of both worlds (dev tooling + production NFR13)
- **Cons**: Different behavior in DEBUG vs PROD
- **Action**: Document in deployment guide

**Deliverables**:
- ADR-001 in `docs/architecture/decisions/ADR-001-admin-framework.md`
- Updated `requirements.md` NFR13 (if Option A chosen)
- Updated `samplify/settings.py` with code comments
- Updated Story 1.1 changelog referencing ADR-001

**Acceptance Criteria**:
- [ ] Architectural decision documented in ADR format
- [ ] NFR13 clarified in PRD (if needed)
- [ ] Settings.py reflects chosen approach
- [ ] Story 1.1 updated with ADR reference

---

### Story R1.2: Update FFmpeg SHA256 Production Checksums

**Priority**: 🔴 HIGH (Security)
**Effort**: 1 hour
**Assigned To**: [Dev]
**Related Stories**: 1.4

**Context**:
Story 1.4 implemented SHA256 verification (SEC-001 fix) but uses placeholder checksums. Production deployment requires real checksums for Windows/macOS/Linux FFmpeg binaries to prevent supply-chain attacks.

**Tasks**:
- [ ] Download FFmpeg binaries for all platforms:
  - Windows: `https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip`
  - macOS: `https://evermeet.cx/ffmpeg/getrelease/zip`
  - Linux: `https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz`
- [ ] Calculate SHA256 for each binary:
  ```bash
  # Windows
  certutil -hashfile ffmpeg.exe SHA256

  # macOS/Linux
  shasum -a 256 ffmpeg
  ```
- [ ] Update `FFMPEG_SHA256` dictionary in `samplify/utils/ffmpeg.py`:
  ```python
  FFMPEG_SHA256 = {
      'windows': 'ACTUAL_CHECKSUM_HERE',  # Replace placeholder
      'darwin': 'ACTUAL_CHECKSUM_HERE',   # Replace placeholder
      'linux': 'ACTUAL_CHECKSUM_HERE',    # Replace placeholder
  }
  ```
- [ ] Test verification on all platforms (if possible) or document limitation
- [ ] Update Story 1.4 changelog with checksum update

**File to Modify**:
- `samplify/utils/ffmpeg.py` (lines with FFMPEG_SHA256 dictionary)

**Testing**:
```bash
# Run FFmpeg detection with real checksums
python manage.py shell
>>> from samplify.utils.ffmpeg import get_ffmpeg_binary_path
>>> get_ffmpeg_binary_path()  # Should verify checksum
```

**Deliverables**:
- Updated `FFMPEG_SHA256` with real checksums
- Test execution log showing successful verification
- Story 1.4 changelog entry

**Acceptance Criteria**:
- [ ] Real SHA256 checksums for Windows/macOS/Linux
- [ ] No "placeholder checksum" warnings in logs
- [ ] `verify_checksum()` function passes with real binaries
- [ ] Story 1.4 updated with completion note

---

### Story R1.3: Implement Schema Filtering in Queue Processor

**Priority**: 🔴 HIGH (Functional)
**Effort**: 2 hours
**Assigned To**: [Dev]
**Related Stories**: 1.8

**Context**:
Story 1.8 AC#5 requires "Service respects active schema configuration" but implementation queries all pending files without schema relationship filter. Queue processor may process files not associated with the active schema.

**Current Implementation** (INCORRECT):
```python
# samplify/management/commands/queue_processor.py:153-156
pending_files = File.objects.filter(
    processing_status="pending"
)[:batch_size]
```

**Required Implementation**:
```python
# Add schema relationship filter
pending_files = File.objects.filter(
    processing_status="pending",
    directory_mapping__schema=active_schema  # Missing filter
).select_for_update(skip_locked=True)[:batch_size]
```

**Tasks**:
- [ ] **Investigate data model relationships**:
  - Verify File → DirectoryMapping → Schema relationship exists
  - If not, determine correct filter path (e.g., File → InputDirectory → Schema)
  - Document actual model relationship in code comments
- [ ] **Update queue processor query** (`samplify/management/commands/queue_processor.py:153-156`):
  ```python
  def get_pending_files(self, active_schema, batch_size=10):
      """Query pending files associated with active schema."""
      return File.objects.select_for_update(
          skip_locked=True
      ).filter(
          processing_status="pending",
          # TODO: Verify correct relationship path
          directory_mapping__schema=active_schema
      ).order_by('created_at')[:batch_size]
  ```
- [ ] **Update tests** (`tests/test_queue_processor.py`):
  - Add test for schema filtering (verify files from other schemas ignored)
  - Update existing tests to create proper schema relationships
  - Verify `test_schema_id_argument` now fully validates filtering
- [ ] **Verify Story 1.8 AC#5 compliance**:
  - Files from Schema A not processed when Schema B is active
  - Schema argument correctly filters pending files
- [ ] **Update Story 1.8 changelog** with remediation completion

**File Modifications**:
- `samplify/management/commands/queue_processor.py` (query logic)
- `tests/test_queue_processor.py` (add schema filtering test)

**Testing**:
```python
# New test to add
def test_schema_filtering(self):
    """Verify queue processor only processes files from active schema."""
    schema_a = Schema.objects.create(name="Schema A", is_active=True)
    schema_b = Schema.objects.create(name="Schema B", is_active=False)

    # Create files for both schemas
    file_a = File.objects.create(..., schema=schema_a, status='pending')
    file_b = File.objects.create(..., schema=schema_b, status='pending')

    # Run queue processor with schema_a active
    cmd = Command()
    pending = cmd.get_pending_files(schema_a)

    # Verify only schema_a files returned
    assert file_a in pending
    assert file_b not in pending
```

**Deliverables**:
- Updated query with schema filter
- New test for schema filtering
- Story 1.8 AC#5 validation
- Story 1.8 changelog entry

**Acceptance Criteria**:
- [ ] Schema relationship filter implemented
- [ ] Test validates filtering works correctly
- [ ] No files processed from inactive schemas
- [ ] All existing tests still pass

---

### Story R1.4: Add Security Comments for CSRF/Auth Deferral

**Priority**: 🔴 HIGH (Documentation)
**Effort**: 30 minutes
**Assigned To**: [Dev]
**Related Stories**: 1.9, 1.10

**Context**:
Story 1.9 API endpoints use `@csrf_exempt` and lack authentication. This is acceptable for current CLI-only deployment but MUST be fixed before Story 1.10 UI integration. Add code comments to prevent accidental production deployment without security.

**Tasks**:
- [ ] **Add warning comments to import API** (`apps/catalog/api/views.py:22`):
  ```python
  # SECURITY WARNING: CSRF exemption is TEMPORARY for CLI-only usage
  # Story 1.10 MUST remove @csrf_exempt and add authentication
  # DO NOT deploy to production web UI without fixing
  # See: docs/qa/REMEDIATION-BACKLOG.md Story R1.4
  @csrf_exempt  # TODO(Story 1.10): Remove - CLI-only temporary exemption
  @require_http_methods(["POST"])
  def import_xml_api(request):
  ```
- [ ] **Add authentication TODO** (same file):
  ```python
  def import_xml_api(request):
      """
      API endpoint for XML template import.

      SECURITY TODO (Story 1.10):
      - Remove @csrf_exempt decorator
      - Add authentication (Django Rest Framework or similar)
      - Add authorization (user permissions for import)
      - Add rate limiting to prevent abuse
      """
  ```
- [ ] **Create Story 1.10 task** in backlog:
  - "Add authentication/CSRF to XML import/export APIs"
  - Link to this remediation story
  - Mark as blocking for web UI deployment
- [ ] **Update Story 1.9 QA Results** with comment additions
- [ ] **Add to deployment checklist**: "Verify Story 1.10 security fixes applied"

**File Modifications**:
- `apps/catalog/api/views.py` (add security comments)
- `docs/qa/gates/1.9-xml-template-importmigration-tool.yml` (update gate status)
- Story 1.10 backlog (create security task)

**Deliverables**:
- Security warning comments in code
- Story 1.10 task created
- Deployment checklist item
- Story 1.9 QA Results updated

**Acceptance Criteria**:
- [ ] Code comments clearly mark CSRF/auth as temporary
- [ ] Story 1.10 has explicit security task
- [ ] Deployment checklist prevents accidental production deployment
- [ ] QA gate updated with "conditional approval"

---

## Phase 2: Technical Debt (MVP Recommended)

**Total Effort**: 6 hours
**Deadline**: Before MVP release
**Risk**: MEDIUM - Code quality and maintainability

### Story R2.1: Move `processing_status` Field to Story 1.6

**Priority**: 🟡 MEDIUM
**Effort**: 2 hours
**Assigned To**: [Dev + SM]
**Related Stories**: 1.2A, 1.6

**Context**:
Story 1.2A added `processing_status` field (pending/processing/completed/failed) without AC or PRD authorization. This is "forward-looking for Story 1.6" which violates story boundaries. Field was properly used in Story 1.6 with migration `0003_file_processing_status.py`.

**Options**:

**Option A: Create Story 1.2A.1 Addendum** (RECOMMENDED)
- Create mini-story documenting field addition
- Backdated AC to match implementation
- Document as approved scope change
- Update Story 1.2A changelog referencing addendum
- **Effort**: 30 minutes (documentation only)

**Option B: Move to Story 1.6**
- Delete migration `0003_file_processing_status.py`
- Move field addition to Story 1.6 implementation
- Update Story 1.6 to include model change
- Regenerate migration in Story 1.6 context
- **Effort**: 2 hours (requires code/migration rework)

**Tasks** (Option A - Recommended):
- [ ] Create `docs/stories/story-12a-addendum-processing-status.md`:
  ```markdown
  # Story 1.2A Addendum: Processing Status Field

  ## Scope Change Approval
  **Date**: 2025-10-06 (Retroactive)
  **Approved By**: [PO Name]
  **Reason**: Forward-looking field for Story 1.6 batch processing

  ## Additional AC
  AC#12: File model includes processing_status field (CharField)
  AC#13: Status choices: pending, processing, completed, failed
  AC#14: Default status is 'pending'

  ## Migration
  - Migration 0003_file_processing_status.py created
  - Field added: processing_status (max_length=20, default='pending')
  ```
- [ ] Update Story 1.2A changelog:
  ```markdown
  | 2025-10-06 | 1.1 | **ADDENDUM**: Added processing_status field (forward-looking for Story 1.6) - See story-12a-addendum-processing-status.md | SM (Bob) |
  ```
- [ ] Update PRD with retroactive scope change note
- [ ] Document lesson learned: "No forward-looking fields without PO approval"

**Deliverables**:
- Story 1.2A Addendum document (Option A)
- Updated Story 1.2A changelog
- PRD scope change note
- Process improvement: "No forward-looking additions" policy

**Acceptance Criteria**:
- [ ] Scope change formally documented
- [ ] Story 1.2A updated with addendum reference
- [ ] Migration ownership clarified (1.2A or 1.6)
- [ ] Process policy created to prevent recurrence

---

### Story R2.2: Execute Performance Benchmarks (Story 1.6)

**Priority**: 🟡 MEDIUM
**Effort**: 30 minutes
**Assigned To**: [QA]
**Related Stories**: 1.6

**Context**:
Story 1.6 AC#12 requires 50-70% CPU utilization (NFR1) but performance tests are marked `@pytest.mark.skip`. Manual validation required before production deployment.

**Tasks**:
- [ ] **Prepare test environment**:
  - 100 test files (media samples from `media/` directory)
  - CPU monitoring tool ready (Task Manager, htop, or similar)
  - Baseline measurement (CPU idle before test)
- [ ] **Execute benchmark test** (`tests/test_batch_processing.py:390-476`):
  ```bash
  # Remove @pytest.mark.skip decorator temporarily
  pytest tests/test_batch_processing.py::test_cpu_utilization_50_70_percent -v -s
  ```
- [ ] **Monitor CPU during test**:
  - Record average CPU utilization over test duration
  - Verify 50-70% target met
  - Note any anomalies (spikes, drops, worker crashes)
- [ ] **Execute load balancing test**:
  ```bash
  pytest tests/test_batch_processing.py::test_load_balancing_across_workers -v -s
  ```
- [ ] **Document results** in Story 1.6:
  ```markdown
  ## Performance Validation (Manual Test - 2025-10-06)

  **Test Environment**:
  - CPU: [Processor model, core count]
  - Test Files: 100 WAV files (44.1kHz, 24-bit)
  - OS: [Windows/macOS/Linux version]

  **Results**:
  - Average CPU Utilization: [X]% (Target: 50-70%)
  - Peak CPU: [Y]%
  - Worker Count: [N cores]
  - Processing Time: [Z] seconds
  - Files Processed: 100/100 (100% success rate)

  **Verdict**: ✅ PASS - NFR1 compliant
  ```
- [ ] **Update test file**: Remove `@pytest.mark.skip` if tests can run in CI/CD
- [ ] **Create baseline metrics**: Document for regression testing

**File Modifications**:
- `tests/test_batch_processing.py` (remove skip decorators if possible)
- `docs/stories/story-16-batch-processing-management-command.md` (add results)

**Deliverables**:
- Performance test execution log
- Story 1.6 performance validation section
- Baseline metrics documented

**Acceptance Criteria**:
- [ ] CPU utilization measured (50-70% target)
- [ ] Load balancing verified across workers
- [ ] Results documented in Story 1.6
- [ ] NFR1 compliance confirmed or violations documented

---

### Story R2.3: Refactor Busy-Wait to Event-Based Signaling (Story 1.6)

**Priority**: 🟡 MEDIUM
**Effort**: 3 hours
**Assigned To**: [Dev]
**Related Stories**: 1.6

**Context**:
Story 1.6 `wait_for_completion()` uses busy-wait pattern (polls every 0.5s) which consumes unnecessary CPU cycles. Event-based signaling improves efficiency and responsiveness.

**Current Implementation** (INEFFICIENT):
```python
# samplify/management/commands/batch_process.py:394-414
def wait_for_completion(self):
    """Wait for all workers to complete (busy-wait)."""
    while True:
        time.sleep(0.5)  # Polls every 500ms - inefficient

        all_done = all(
            deque.empty() for _, deque in self.decoder_channels
        )

        if all_done:
            break
```

**Improved Implementation** (EVENT-BASED):
```python
# Use multiprocessing.Event for worker completion signaling
import multiprocessing

def __init__(self):
    self.completion_event = multiprocessing.Event()
    self.active_tasks = multiprocessing.Value('i', 0)  # Atomic counter

def wait_for_completion(self):
    """Wait for all workers to complete (event-based)."""
    self.completion_event.wait()  # Blocks until signaled (no polling)

def process_task(self, task):
    """Worker processes task and signals completion."""
    try:
        # ... existing processing logic ...
        pass
    finally:
        with self.active_tasks.get_lock():
            self.active_tasks.value -= 1

            if self.active_tasks.value == 0:
                self.completion_event.set()  # Signal all tasks done
```

**Tasks**:
- [ ] **Add multiprocessing.Event** to batch processor initialization
- [ ] **Add atomic task counter** (multiprocessing.Value)
- [ ] **Update distribute_jobs()** to increment counter when adding tasks
- [ ] **Update process_task()** to decrement counter and signal when done
- [ ] **Replace busy-wait loop** with `completion_event.wait()`
- [ ] **Add timeout** to event wait (prevent infinite blocking):
  ```python
  if not self.completion_event.wait(timeout=3600):  # 1 hour max
      logger.error("Workers did not complete within timeout")
  ```
- [ ] **Test with multiple files** (verify no race conditions)
- [ ] **Measure CPU improvement** (before/after comparison)
- [ ] **Update tests** (`tests/test_batch_processing.py`) if needed

**File Modifications**:
- `samplify/management/commands/batch_process.py` (wait logic)
- `tests/test_batch_processing.py` (update if mocking affected)

**Testing**:
```python
# Verify event-based signaling works
def test_event_based_completion(self):
    """Test completion event triggers when all tasks done."""
    cmd = Command()
    cmd.schedule_workers()

    # Add tasks
    files = [File.objects.create(...) for _ in range(10)]
    cmd.distribute_jobs(files)

    # Wait for completion (should not busy-wait)
    import time
    start = time.time()
    cmd.wait_for_completion()
    duration = time.time() - start

    # Verify completion event was used (no 0.5s polling delay artifacts)
    assert cmd.completion_event.is_set()
```

**Deliverables**:
- Event-based completion signaling
- Atomic task counter
- Updated tests
- CPU improvement measurement
- Story 1.6 QA update

**Acceptance Criteria**:
- [ ] No busy-wait polling (CPU usage reduced)
- [ ] Completion event triggers when tasks done
- [ ] Atomic counter prevents race conditions
- [ ] Timeout prevents infinite blocking
- [ ] All tests pass with new implementation

---

## Phase 3: Optional Enhancements

**Total Effort**: Variable
**Deadline**: Post-MVP
**Risk**: LOW - Nice-to-have improvements

### Story R3.1: Execute NFR10 Latency Test (Story 1.7)

**Priority**: 🟢 LOW
**Effort**: 30 minutes
**Assigned To**: [QA]
**Related Stories**: 1.7

**Context**:
Story 1.7 AC#5/AC#11 require <10 second file detection latency (NFR10) but test is marked `@pytest.mark.skip`. Manual validation recommended to confirm compliance.

**Tasks**:
- [ ] Remove `@pytest.mark.skip` from `tests/test_file_monitor.py::test_file_detection_latency_under_10_seconds`
- [ ] Execute test with real watchdog observer (not mocked)
- [ ] Document results in Story 1.7
- [ ] If test fails, investigate latency sources and optimize

**Deliverables**:
- Test execution log
- NFR10 compliance confirmation
- Story 1.7 update

**Acceptance Criteria**:
- [ ] Latency measured (target: <10 seconds)
- [ ] Results documented
- [ ] NFR10 compliance confirmed or violations noted

---

### Story R3.2: Document 24-Hour Stability Plan (Story 1.8)

**Priority**: 🟢 LOW
**Effort**: 1 hour (documentation) + 24 hours (execution)
**Assigned To**: [QA + Ops]
**Related Stories**: 1.8

**Context**:
Story 1.8 AC#14 requires "Service stable during long-running operation (24+ hours)" but no long-running stability test exists. Create manual validation plan for production readiness.

**Tasks**:
- [ ] Create stability test plan document
- [ ] Define monitoring metrics (CPU, memory, file processing rate)
- [ ] Create test script for 24-hour run
- [ ] Execute stability test in staging environment
- [ ] Document results and any issues found

**Deliverables**:
- Stability test plan
- 24-hour execution results
- Story 1.8 AC#14 validation

**Acceptance Criteria**:
- [ ] Test plan documented
- [ ] 24-hour run completed without crashes
- [ ] Memory leaks checked
- [ ] Results documented in Story 1.8

---

### Story R3.3: Monitor Loguru Fork Issue #2 (Story 1.3)

**Priority**: 🟢 LOW (Ongoing)
**Effort**: Ongoing monitoring
**Assigned To**: [Architect]
**Related Stories**: 1.3

**Context**:
Story 1.3 uses custom loguru fork (https://github.com/RoscoeTheDog/loguru) with unresolved Issue #2 (exception console formatting). Create monitoring plan for upstream merge strategy.

**Tasks**:
- [ ] Subscribe to fork repository for updates
- [ ] Check Issue #2 status monthly
- [ ] Evaluate upstream loguru releases for alternatives
- [ ] Document migration plan if fork becomes unmaintainable
- [ ] Consider contributing fix to upstream loguru

**Deliverables**:
- Fork monitoring schedule
- Migration plan (if needed)
- Quarterly review of fork status

**Acceptance Criteria**:
- [ ] Monthly check of Issue #2 status
- [ ] Migration plan documented
- [ ] Fork viability reviewed quarterly

---

## Sprint Plan Recommendation

### Sprint 1: Critical Fixes (1 week)
**Goal**: Production blockers resolved

**Day 1-2**:
- R1.1: NFR13 ADR (1 hour) → Architect + PO
- R1.2: SHA256 checksums (1 hour) → Dev

**Day 3-4**:
- R1.3: Schema filtering (2 hours) → Dev
- R1.4: Security comments (30 min) → Dev

**Day 5**:
- Testing and validation
- Sprint review

**Sprint Deliverables**:
- ✅ All Phase 1 stories complete
- ✅ Production deployment unblocked
- ✅ Security gaps documented

---

### Sprint 2: Technical Debt (1 week)
**Goal**: Code quality and maintainability

**Day 1-2**:
- R2.1: Processing status addendum (2 hours) → Dev + SM
- R2.2: Performance benchmarks (30 min) → QA

**Day 3-5**:
- R2.3: Event-based signaling (3 hours) → Dev
- Testing and documentation

**Sprint Deliverables**:
- ✅ Scope creep documented
- ✅ Performance validated
- ✅ Busy-wait eliminated

---

### Sprint 3: Optional (As needed)
**Goal**: Nice-to-have improvements

**Tasks**:
- R3.1: NFR10 latency test
- R3.2: 24-hour stability plan
- R3.3: Fork monitoring setup

**Sprint Deliverables**:
- ✅ NFR compliance validated
- ✅ Long-term monitoring established

---

## Success Metrics

**Phase 1 Complete When**:
- [ ] All 🔴 HIGH priority stories Done
- [ ] Production deployment approved by Architect + QA
- [ ] No security warnings in code
- [ ] All critical issues in QA gate resolved

**Phase 2 Complete When**:
- [ ] All 🟡 MEDIUM priority stories Done
- [ ] Performance benchmarks executed and documented
- [ ] Technical debt tracked in backlog
- [ ] Code quality metrics improved

**Phase 3 Complete When**:
- [ ] Optional enhancements implemented or deferred
- [ ] Monitoring plans in place
- [ ] Long-term maintenance strategy documented

---

## Lessons Learned

**Process Improvements to Prevent Recurrence**:

1. **Quality Gates**: Enforce PO → SM → Dev → QA workflow (no skipping)
2. **Story Handoff**: Checklist validates AC, dependencies, test strategy
3. **ADR Template**: Architectural decisions documented proactively
4. **Performance Benchmarks**: All NFR claims must have tests (not skipped)
5. **Scope Change Approval**: No "forward-looking" additions without PO approval

**BMad Method Compliance**:
- Stories not marked "Ready" until PO/SM review complete
- Development not started until story approved
- QA review required before "Done" status
- Retrospective QA is expensive - prevent issues upstream

---

## Status Tracking

| Story | Priority | Effort | Status | Assigned | Deadline | Blocked By |
|-------|----------|--------|--------|----------|----------|------------|
| R1.1  | 🔴 HIGH  | 1h     | 📋 TODO | Architect | TBD | - |
| R1.2  | 🔴 HIGH  | 1h     | ✅ DONE | Dev (James) | 2025-10-07 | - |
| R1.3  | 🔴 HIGH  | 2h     | ✅ DONE | Dev (James) | 2025-10-07 | - |
| R1.4  | 🔴 HIGH  | 30m    | ✅ DONE | Dev (James) | 2025-10-07 | - |
| R2.1  | 🟡 MED   | 2h     | 📋 TODO | Dev+SM | TBD | R1.1 |
| R2.2  | 🟡 MED   | 30m    | 📋 TODO | QA | TBD | - |
| R2.3  | 🟡 MED   | 3h     | 📋 TODO | Dev | TBD | R2.2 |
| R3.1  | 🟢 LOW   | 30m    | 📋 TODO | QA | Post-MVP | - |
| R3.2  | 🟢 LOW   | 25h    | 📋 TODO | QA+Ops | Post-MVP | - |
| R3.3  | 🟢 LOW   | Ongoing| 📋 TODO | Architect | Ongoing | - |

**Legend**:
- 📋 TODO - Not started
- 🚧 IN PROGRESS - Active work
- ✅ DONE - Completed
- ⏸️ BLOCKED - Waiting on dependency

---

**Document Owner**: Winston (Architect)
**Last Updated**: 2025-10-06
**Next Review**: After Phase 1 completion
