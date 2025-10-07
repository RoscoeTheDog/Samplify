# Error Handling & Resilience Strategy

**Status:** Draft
**Created:** 2025-10-06
**Owner:** Winston (Architect)
**Related ADRs:** None yet (first cross-cutting strategy)
**Related Stories:** 1.4, 1.5, 1.6, 1.7, 1.8

---

## Purpose

This document defines Samplify's **centralized error handling and resilience strategy** to ensure consistent, predictable error management across all components.

**Motivation:** QA review (Stories 1.4-1.8) identified inconsistent error handling patterns requiring standardization:
- Story 1.4: Network retry logic needed
- Story 1.5: Error categorization needed
- Story 1.6: Database retry logic missing
- Story 1.7: FFmpeg retry logic missing
- Story 1.8: Exponential backoff missing

---

## Core Principles

### 1. Fail Gracefully
- Never crash silently - always log failures
- Degrade functionality rather than fail completely
- Provide actionable error messages to users/developers

### 2. Retry Transient Failures
- Network errors: Always retry with exponential backoff
- Database lock errors: Retry with backoff
- External process failures (FFmpeg): Retry with limits

### 3. Categorize Errors
- **Transient:** Temporary failures that may succeed on retry
- **Permanent:** Failures that will not succeed on retry
- **Fatal:** Unrecoverable errors requiring immediate attention

### 4. Observable Failures
- Log all errors with structured context
- Track error rates and patterns
- Alert on critical failures

---

## Error Classification Taxonomy

### Transient Errors (Retry Recommended)

**Network Errors:**
- `urllib.error.URLError` - Network connectivity issues
- `requests.exceptions.Timeout` - Request timeouts
- `requests.exceptions.ConnectionError` - Connection failures
- HTTP 429 (Too Many Requests), 503 (Service Unavailable), 504 (Gateway Timeout)

**Database Errors:**
- `sqlite3.OperationalError: database is locked` - Concurrent access conflict
- `django.db.utils.OperationalError` - Transient DB issues

**External Process Errors:**
- FFmpeg timeouts (process.wait() timeout)
- Temporary file access errors (`PermissionError` - file locked by antivirus)

**Action:** Retry with exponential backoff (see Retry Policies below)

---

### Permanent Errors (Do Not Retry)

**Validation Errors:**
- Invalid file formats (e.g., `.txt` passed as audio file)
- Corrupt file headers (cannot be decoded)
- Schema validation failures

**Authentication/Authorization:**
- HTTP 401 (Unauthorized), 403 (Forbidden)
- Invalid API keys or credentials

**Logic Errors:**
- `ValueError`, `TypeError` from invalid inputs
- Failed assertions (programming bugs)

**Resource Errors:**
- Disk full (`OSError: No space left on device`)
- File not found (after retries)

**Action:** Log error, fail gracefully, return error to caller

---

### Fatal Errors (Immediate Escalation)

**System Errors:**
- Out of memory (`MemoryError`)
- Segmentation faults (FFmpeg crashes)
- Critical infrastructure unavailable (database unrecoverable)

**Security Errors:**
- SHA256 checksum mismatch (Story 1.4 - potential malicious binary)
- Suspicious file operations (directory traversal attempts)

**Data Integrity Errors:**
- Database corruption detected
- Critical migration failures

**Action:** Log with CRITICAL level, alert operators, graceful shutdown

---

## Retry Policies

### Standard Exponential Backoff

**Configuration:**
```python
# Standard retry policy for all components
MAX_RETRIES = 3
RETRY_DELAYS = [2, 4, 8]  # seconds between retries
TOTAL_MAX_TIME = 14  # seconds (2+4+8)
```

**Algorithm:**
```python
def retry_with_backoff(max_retries=3, delays=[2, 4, 8]):
    """Decorator for automatic retry with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except TRANSIENT_ERRORS as e:
                    if attempt < max_retries - 1:
                        delay = delays[attempt]
                        logger.warning(f"Attempt {attempt+1} failed, retrying in {delay}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")
                        raise
        return wrapper
    return decorator
```

**Usage:**
```python
@retry_with_backoff(max_retries=3, delays=[2, 4, 8])
def download_file(url):
    response = urllib.request.urlopen(url, timeout=60)
    return response.read()
```

---

### Policy Variations by Component

**Network Operations (FFmpeg Downloads, External APIs):**
- Retries: 3
- Delays: [2, 4, 8] seconds
- Total timeout: 60 seconds per attempt
- Example: `download_ffmpeg()` in Story 1.4

**Database Operations (SQLite WAL):**
- Retries: 5 (more retries for lock contention)
- Delays: [0.5, 1, 2, 4, 8] seconds
- Total timeout: 15.5 seconds
- Example: File scanning in Story 1.5

**FFmpeg Metadata Extraction:**
- Retries: 2 (fewer retries for external process)
- Delays: [1, 2] seconds
- Subprocess timeout: 30 seconds per attempt
- Example: File monitor in Story 1.7

**Long-Running Batch Operations:**
- Retries: 0 (manual retry recommended)
- Logging: Comprehensive error context
- User notification: Required
- Example: Batch processing in Story 1.6

---

## Circuit Breaker Pattern (Future Enhancement)

For repeated failures (e.g., FFmpeg consistently crashing), implement circuit breaker:

**States:**
1. **Closed:** Normal operation, allow all requests
2. **Open:** Too many failures, reject requests immediately (fail fast)
3. **Half-Open:** Test if service recovered, allow limited requests

**Thresholds:**
- Failure rate: 50% failures in 10 attempts
- Open duration: 60 seconds
- Half-open test: 3 requests

**Example Use Case:**
- FFmpeg binary corruption detected
- Circuit breaker trips to OPEN
- Skip FFmpeg operations for 60 seconds
- Half-open: Test 3 files
- If successful, return to CLOSED

**Status:** Deferred to Phase 2 (post-MVP)

---

## Error Logging Standards

### Log Levels

**CRITICAL:**
- Fatal errors requiring immediate attention
- Security violations (SHA256 mismatch)
- Data corruption detected

**ERROR:**
- Permanent failures after all retries exhausted
- Unexpected exceptions requiring investigation

**WARNING:**
- Transient failures before retry
- Degraded functionality
- Resource constraints (disk space low)

**INFO:**
- Successful operations after retry
- Major workflow milestones

**DEBUG:**
- Retry attempt details
- Detailed error context for troubleshooting

---

### Structured Logging Context

**All error logs MUST include:**
```python
logger.error(
    "File scanning failed",
    extra={
        'file_path': file_path,
        'error_type': type(e).__name__,
        'error_message': str(e),
        'retry_count': attempt,
        'duration_ms': duration,
        'correlation_id': request_id,  # For tracing across components
    }
)
```

**Example (Story 1.5 - File Scanning):**
```python
try:
    file_record = scan_file(file_path)
except PermissionError as e:
    logger.warning(
        "File access denied, will retry",
        extra={
            'file_path': file_path,
            'error_type': 'PermissionError',
            'error_message': str(e),
            'retry_count': attempt,
            'action': 'retry_after_delay',
        }
    )
except ValueError as e:
    logger.error(
        "Invalid file format, permanent failure",
        extra={
            'file_path': file_path,
            'error_type': 'ValueError',
            'error_message': str(e),
            'action': 'skip_file',
        }
    )
```

---

## Error Propagation Strategy

### 1. Catch Specific Exceptions
```python
# Good
try:
    result = risky_operation()
except FileNotFoundError:
    logger.warning("File not found, skipping")
    return None
except PermissionError:
    logger.error("Permission denied")
    raise

# Bad - overly broad
try:
    result = risky_operation()
except Exception:  # Catches too much
    pass
```

### 2. Re-raise After Logging
```python
try:
    critical_operation()
except DatabaseError as e:
    logger.error(f"Database operation failed: {e}")
    raise  # Re-raise for caller to handle
```

### 3. Wrap External Exceptions
```python
try:
    subprocess.run(['ffmpeg', '-version'], check=True)
except subprocess.CalledProcessError as e:
    raise FFmpegNotFoundError(
        "FFmpeg binary not available",
        original_error=e
    )
```

---

## Implementation Checklist

### Phase 1: Immediate (Stories 1.4-1.8)
- [x] **Story 1.4:** Network retry logic (GUIDE 3) - COMPLETE
- [ ] **Story 1.5:** Error categorization (GUIDE 8) - IN PROGRESS
- [ ] **Story 1.6:** Database retry logic - PENDING
- [ ] **Story 1.7:** FFmpeg retry logic - PENDING
- [ ] **Story 1.8:** Exponential backoff - PENDING

### Phase 2: Standardization (Post-MVP)
- [ ] Create `samplify/utils/retry.py` module
  - [ ] `retry_with_backoff()` decorator
  - [ ] `CircuitBreaker` class (future)
  - [ ] Error classification utilities
- [ ] Update all components to use centralized retry module
- [ ] Add retry metrics to logging

### Phase 3: Monitoring (Production)
- [ ] Track error rates by category (transient/permanent/fatal)
- [ ] Alert on repeated failures (circuit breaker trigger)
- [ ] Dashboard: Error trends over time

---

## Testing Requirements

### Unit Tests
- [ ] Test retry behavior with mocked failures
- [ ] Verify exponential backoff delays
- [ ] Validate error classification logic

### Integration Tests
- [ ] Test real network retry scenarios
- [ ] Simulate database lock contention
- [ ] FFmpeg crash recovery

### Chaos Engineering (Future)
- [ ] Randomly inject transient failures
- [ ] Validate graceful degradation
- [ ] Measure recovery time

---

## Related Documentation

**ADRs:**
- ADR 0003: Busy-Wait Pattern (future refactoring to event-based with error handling)

**Stories:**
- Story 1.4: FFmpeg Detection & Download (network retry)
- Story 1.5: File Scanning Service (error categorization)
- Story 1.6: Batch Processing (database retry)
- Story 1.7: File Monitor (FFmpeg retry)
- Story 1.8: Queue Processor (exponential backoff)

**QA Reports:**
- `docs/qa/REMEDIATION-TRACKING.md` - GUIDES 3, 8 (retry implementations)

**Code References:**
- `samplify/utils/ffmpeg.py:retry_with_backoff()` - Reference implementation

---

## Exceptions to This Strategy

**When NOT to retry:**
1. User-initiated cancellation (KeyboardInterrupt)
2. Programming errors (TypeError, AttributeError) - fix code, don't retry
3. Validation failures (bad input data)
4. Security violations (checksum mismatch)

**When to fail fast:**
1. Critical infrastructure missing (database file deleted)
2. Irrecoverable errors (corrupt database schema)
3. Security threats detected

---

## Review & Maintenance

**Review Frequency:** Quarterly
**Next Review:** 2026-01-06

**Trigger for Early Review:**
- New error patterns discovered in production
- External dependency behavior changes (e.g., FFmpeg)
- Performance issues from excessive retries

---

**Last Updated:** 2025-10-06
**Owner:** Winston (Architect)
**Status:** Draft → Under Review
