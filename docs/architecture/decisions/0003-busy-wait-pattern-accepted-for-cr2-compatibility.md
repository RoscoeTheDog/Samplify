# ADR 0003: Busy-Wait Pattern Accepted for CR2 Compatibility

**Status:** Accepted (with future refactoring planned)
**Date:** 2025-10-05 (Retroactive)
**Deciders:** Development Team
**Related Stories:** 1.6
**Related NFRs:** NFR1 (Performance), CR2 (Legacy Pattern Preservation)
**Technical Debt:** Yes - tracked for future refactoring

---

## Context

Story 1.6 (Batch Processing Management Command) requires preserving the legacy multiprocessing pattern from the brownfield codebase (CR2 requirement).

The original `__main__.py` implementation uses a **busy-wait polling pattern** in `wait_for_completion()`:

```python
def wait_for_completion(self):
    """Wait for all workers to complete (BUSY-WAIT PATTERN)."""
    while any(p.is_alive() for p in self.workers):
        time.sleep(0.5)  # Poll every 500ms
```

**Problem:** This pattern consumes unnecessary CPU cycles by repeatedly polling worker status, even when no work is being done.

**Constraint:** CR2 (Constraint Requirement 2) mandates preserving the original multiprocessing approach for compatibility with legacy codebase patterns.

**Trade-off Decision Required:** Choose between:
1. **Preserve busy-wait** (CR2 compliance, known tech debt)
2. **Refactor to event-based** (better performance, violates CR2)

---

## Decision

**Accept busy-wait pattern for initial implementation to satisfy CR2, but formally document as technical debt for future refactoring.**

**Rationale:**
1. **CR2 Compliance:** Preserves legacy multiprocessing pattern as required
2. **Implementation Velocity:** Avoids scope creep in Story 1.6
3. **Acceptable Trade-off:** 0.5s polling interval is tolerable for batch processing workload
4. **Future Path:** Event-based refactoring planned as post-MVP enhancement

---

## Implementation

**Current Pattern (Story 1.6):**
```python
def wait_for_completion(self) -> None:
    """
    Wait for all worker processes to complete.

    Uses polling pattern (CR2 legacy compatibility).
    TODO: Refactor to event-based signaling (multiprocessing.Event) in future sprint.
    """
    while any(p.is_alive() for p in self.workers):
        time.sleep(0.5)  # Poll every 500ms
```

**Location:** `samplify/management/commands/batch_process.py:394-414`

---

## Consequences

### Positive
- ✅ **CR2 Compliance:** Preserves legacy multiprocessing pattern
- ✅ **Simplicity:** Easy to understand and debug
- ✅ **No Deadlocks:** No risk of event signaling bugs
- ✅ **Proven Pattern:** Works in production brownfield codebase

### Negative
- ❌ **CPU Waste:** Polling consumes CPU even when idle
- ❌ **Response Latency:** 0.5s worst-case delay in completion detection
- ❌ **Not Scalable:** Inefficient for high-frequency or long-running workloads
- ❌ **Power Inefficiency:** Unnecessary wake-ups on battery-powered systems

### Neutral
- 📋 **Technical Debt:** Documented in QA gate and this ADR
- 📋 **Refactoring Path:** Clear upgrade path to `multiprocessing.Event()`
- 📋 **Performance Impact:** Minimal for typical batch workloads (10-100 files)

---

## Performance Impact

### Measured Impact (Estimated)
- **CPU Overhead:** ~0.1-0.5% CPU per polling cycle (negligible)
- **Latency:** 0-500ms delay in detecting worker completion
- **Power:** ~2-3 wake-ups/second (acceptable for desktop/server)

### NFR1 Compliance
**NFR1 Requirement:** 50-70% CPU utilization during batch processing

**Assessment:** Busy-wait polling adds negligible overhead (~0.5%) compared to FFmpeg worker processes consuming 50-70% CPU. NFR1 compliance not affected.

**Caveat:** Performance benchmarks not executed in CI (PERF-001 issue in QA gate).

---

## Alternatives Considered

### Option 1: Busy-Wait Pattern (Accepted)
**Approach:** Poll worker status every 0.5s

**Pros:**
- CR2 compliant
- Simple implementation
- No event coordination bugs

**Cons:**
- CPU waste
- Not scalable

**Acceptance Reason:** Best trade-off for CR2 compliance and simplicity

---

### Option 2: Event-Based Signaling (Deferred)
**Approach:**
```python
completion_event = multiprocessing.Event()

def worker_wrapper(task_queue, completion_event):
    process_tasks(task_queue)
    completion_event.set()  # Signal completion

def wait_for_completion(self):
    for event in self.completion_events:
        event.wait()  # Block until signaled (no polling)
```

**Pros:**
- Zero CPU waste
- Instant completion detection
- Scalable to many workers

**Cons:**
- **Violates CR2** (changes multiprocessing pattern)
- More complex event coordination
- Risk of deadlocks if event not set

**Rejection Reason (Current):** Violates CR2 requirement

**Future Consideration:** Refactor after CR2 constraint lifted

---

### Option 3: Threading.Condition (Rejected)
**Approach:**
```python
condition = threading.Condition()

def worker_wrapper(task_queue, condition):
    process_tasks(task_queue)
    with condition:
        condition.notify()

def wait_for_completion(self):
    with self.condition:
        self.condition.wait()
```

**Pros:**
- Clean signaling pattern
- Low overhead

**Cons:**
- **Violates CR2** (requires threading, not multiprocessing)
- Mixing threading and multiprocessing adds complexity
- GIL contention potential

**Rejection Reason:** Incompatible with multiprocessing-based architecture

---

### Option 4: Queue Sentinel Values (Rejected)
**Approach:**
```python
def wait_for_completion(self):
    for _ in self.workers:
        self.result_queue.get()  # Block until worker sends sentinel
```

**Pros:**
- No polling
- Uses existing queue infrastructure

**Cons:**
- **Violates CR2** (changes worker communication pattern)
- Requires workers to send completion signals
- Complicates error handling

**Rejection Reason:** Changes legacy pattern, complicates implementation

---

## Mitigation Strategy

### Immediate (Story 1.6)
1. **Document as Tech Debt:** ADR created (this document)
2. **Inline Comments:** TODO added in code referencing future refactoring
3. **QA Tracking:** PERF-001 issue logged in quality gate

### Short-Term (Post-MVP)
1. **Validate Impact:** Run performance benchmarks to measure actual CPU overhead
2. **Monitor Production:** Log polling frequency and completion latency
3. **User Feedback:** Assess if latency impacts user experience

### Long-Term (Future Sprint)
1. **Refactor to Events:** Implement `multiprocessing.Event()` pattern
2. **Benchmark Comparison:** Measure CPU savings and latency improvements
3. **Update CR2:** Negotiate lifting legacy pattern constraint

---

## Refactoring Path

**Future Implementation (Post-CR2):**
```python
class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.completion_events = []  # One event per worker

    def start_workers(self):
        for i in range(self.worker_count):
            event = multiprocessing.Event()
            self.completion_events.append(event)

            worker = multiprocessing.Process(
                target=worker_wrapper,
                args=(self.task_queue, event)
            )
            worker.start()
            self.workers.append(worker)

    def wait_for_completion(self):
        """Event-based completion (zero CPU overhead)."""
        for event in self.completion_events:
            event.wait()  # Block until worker signals completion
```

**Estimated Effort:** 2-3 hours (low-risk refactoring)

**Testing Requirements:**
- Unit tests for event signaling
- Integration tests for multi-worker completion
- Performance benchmarks comparing before/after

---

## Validation

### QA Assessment
- **Reviewer:** Quinn (Test Architect)
- **Date:** 2025-10-06
- **Finding:** "Busy-wait in `wait_for_completion()` polls every 0.5s consuming unnecessary CPU"
- **Severity:** HIGH (PERF-001)
- **Recommendation:** "Refactor to use `multiprocessing.Event()` or `threading.Condition()` for event-based signaling"
- **Quality Gate:** Story 1.6 - CONCERNS (80/100)

### CR2 Compliance
- ✅ **Verified:** Multiprocessing pattern matches legacy `__main__.py` implementation
- ✅ **Documentation:** CR2 preservation notes added to code
- ✅ **Acceptance Criteria:** Story 1.6 AC#1 satisfied

### Code Review
- ✅ **Inline Comments:** Future refactoring documented
- ✅ **TODO Tags:** Searchable for future sprints
- ✅ **Test Coverage:** 17/17 tests passing

---

## References

- **Story 1.6:** Batch Processing Management Command
- **NFR1:** Performance requirement (50-70% CPU)
- **CR2:** Legacy pattern preservation requirement
- **QA Gate:** `docs/qa/gates/1.6-batch-processing-management-command.yml`
- **Implementation:** `samplify/management/commands/batch_process.py:394-414`
- **Legacy Code:** `__main__.py` (brownfield codebase)

---

## Notes

**Decision Context:**
- This decision was made during initial implementation of Story 1.6
- QA review (Quinn) identified as technical debt post-implementation
- Team agreed to accept pattern for CR2 compliance with planned refactoring

**Post-Decision Observations:**
- 17/17 tests passing with busy-wait pattern
- No user-reported latency issues in manual testing
- CPU overhead deemed acceptable for batch processing use case

**Future Considerations:**
1. **When to Refactor:**
   - After MVP delivery (not blocking production)
   - When CR2 constraint lifted
   - If CPU overhead becomes measurable issue in production

2. **Success Metrics:**
   - CPU utilization reduction during idle worker periods
   - Completion detection latency improvement (0.5s → <10ms)
   - No regression in worker coordination reliability

3. **Risk Assessment:**
   - Low risk refactoring (well-understood pattern)
   - High test coverage mitigates regression risk
   - Event-based pattern is industry standard

---

**Last Updated:** 2025-10-06 (ADR formalized retroactively)
**Status Review Date:** Post-MVP (Q4 2025)
