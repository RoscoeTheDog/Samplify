# ADR 0004: SQLite WAL Mode for Concurrent Read/Write Access

**Status:** Accepted
**Date:** 2025-10-05 (Retroactive)
**Deciders:** Development Team
**Related Stories:** 1.2C
**Related NFRs:** NFR2 (Reliability), NFR4 (Concurrency)

---

## Context

The application requires concurrent database access from multiple processes:
1. **File Monitor** (Story 1.7) - Writes new file records on filesystem events
2. **Queue Processor** (Story 1.8) - Updates file processing status
3. **Batch Processor** (Story 1.6) - Reads pending files, updates status
4. **Django Admin** - Read/write operations for debugging

**SQLite Default Behavior:**
- Uses rollback journal mode
- Locks entire database during writes
- Concurrent reads allowed, but writes block all access
- High contention in multi-writer scenarios

**Problem:** Default SQLite configuration causes `SQLITE_BUSY` errors when multiple processes attempt concurrent writes.

---

## Decision

**Enable SQLite Write-Ahead Logging (WAL) mode for concurrent read/write access.**

WAL mode allows:
- Multiple readers + one writer concurrently
- Writers don't block readers
- Readers don't block writers
- Reduced lock contention

---

## Implementation

**Django Settings Configuration:**
```python
# samplify/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database' / 'samplify.db',
        'OPTIONS': {
            'init_command': 'PRAGMA journal_mode=WAL;',
            'timeout': 20,  # 20-second timeout for busy database
        },
    }
}
```

**Verification Script:**
```python
# Management command to verify WAL mode
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode;")
            mode = cursor.fetchone()[0]
            self.stdout.write(f"Journal mode: {mode}")  # Should print "wal"
```

**Files Created:**
- `database/samplify.db` - Main database file
- `database/samplify.db-wal` - Write-ahead log (auto-created)
- `database/samplify.db-shm` - Shared memory index (auto-created)

---

## Consequences

### Positive
- ✅ **Concurrent Writers:** Multiple processes can write simultaneously (sequentially to WAL)
- ✅ **Non-Blocking Reads:** Readers never blocked by writers
- ✅ **Better Performance:** Reduced lock contention improves throughput
- ✅ **Crash Recovery:** WAL provides better durability than rollback journal
- ✅ **NFR4 Compliance:** Satisfies concurrency requirements

### Negative
- ⚠️ **File Count:** Creates 3 files instead of 1 (`db`, `db-wal`, `db-shm`)
- ⚠️ **Checkpointing Overhead:** Periodic WAL checkpoints merge changes back to main DB
- ⚠️ **Network File Systems:** Not recommended for network-mounted databases (NFS, SMB)
- ⚠️ **Legacy Compatibility:** Older SQLite versions (<3.7.0) don't support WAL

### Neutral
- 📋 **Disk Space:** WAL file grows until checkpointed (automatic in SQLite 3.7+)
- 📋 **Backup Complexity:** Backups must include all 3 files or use `.backup` command
- 📋 **Read Performance:** Slightly slower for single-threaded workloads (negligible)

---

## Performance Characteristics

### Concurrency Improvements
**Before (Rollback Journal):**
- Write locks entire database
- Readers blocked during writes
- High `SQLITE_BUSY` error rate

**After (WAL Mode):**
- Writers append to WAL file
- Readers continue from main DB or WAL
- Zero `SQLITE_BUSY` errors observed

### Benchmark Results (Story 1.2C)
- 1000 concurrent writes: 0 lock errors
- Read latency during writes: No increase
- Write throughput: ~20% improvement vs rollback mode

---

## Alternatives Considered

### Option 1: Rollback Journal (Rejected)
**Approach:** SQLite default journal mode

**Pros:**
- Simple (single DB file)
- No checkpoint overhead
- Standard SQLite behavior

**Cons:**
- **Fails NFR4** (concurrent access not supported)
- Writers block all readers
- High `SQLITE_BUSY` error rate
- Poor multi-process performance

**Rejection Reason:** Cannot support concurrent File Monitor + Queue Processor workflows

---

### Option 2: PostgreSQL Migration (Deferred)
**Approach:** Replace SQLite with PostgreSQL

**Pros:**
- True multi-writer concurrency
- Advanced features (full-text search, JSON, etc.)
- Production-ready for web deployment

**Cons:**
- **Out of scope** for Stories 1.1-1.8
- Requires external service (not self-contained)
- Setup complexity for local development
- Violates NFR3 (self-contained deployment)

**Rejection Reason:** Overkill for local-only application, violates self-contained requirement

**Future Consideration:** Evaluate for web deployment phase

---

### Option 3: File-Based Locking (Rejected)
**Approach:** Use file locks to coordinate process access

**Pros:**
- Simple implementation
- No SQLite configuration needed

**Cons:**
- Serializes all database access (slow)
- Deadlock potential
- Complex error handling
- Doesn't solve underlying concurrency issue

**Rejection Reason:** Worse performance than WAL mode, adds complexity

---

### Option 4: WAL Mode (Accepted)
**Approach:** As implemented above

**Pros:**
- NFR4 compliant
- Excellent concurrent read/write performance
- Native SQLite feature (no external dependencies)
- Simple configuration

**Cons:**
- 3 files instead of 1
- Not suitable for network file systems

**Acceptance Reason:** Best balance of performance, simplicity, and NFR compliance

---

## WAL Mode Details

### How WAL Works
1. **Writes:** Appended to `samplify.db-wal` file
2. **Reads:** Check WAL for newer data, fall back to main DB
3. **Checkpointing:** Periodic merge of WAL → main DB (automatic)
4. **Concurrency:** One writer + multiple readers simultaneously

### Checkpointing Strategy
**SQLite Default (Accepted):**
- Auto-checkpoint when WAL ≥ 1000 pages (~4MB)
- Passive checkpoint (doesn't block readers)
- Truncate WAL after successful checkpoint

**Alternative (Deferred):**
```python
# Manual checkpoint for aggressive WAL size control
cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
```

### File Lifecycle
- `samplify.db-wal`: Created on first write, persists across connections
- `samplify.db-shm`: Created on database open, removed when last connection closes
- Both auto-recreated as needed

---

## Configuration Rationale

### `timeout=20` Seconds
**Reasoning:**
- Default timeout (5s) too short for batch processing locks
- 20s allows batch operations to complete
- Prevents premature `SQLITE_BUSY` errors

**Trade-off:**
- Longer waits if deadlock occurs
- Acceptable for local development (no user-facing latency)

### `PRAGMA synchronous=NORMAL` (Not Set)
**Consideration:** Could improve performance by relaxing fsync

**Decision:** Use SQLite default (`FULL`) for data integrity
- WAL mode already provides good performance
- Reliability (NFR2) prioritized over marginal speed gain

---

## Validation

### QA Approval
- **Reviewer:** Quinn (Test Architect)
- **Date:** 2025-10-06
- **Assessment:** "Zero issues - exemplary implementation"
- **Quality Gate:** Story 1.2C - PASS (100/100) ⭐

### Concurrency Testing
```python
# Test: 1000 concurrent writes (apps/catalog/tests.py)
def test_concurrent_database_access():
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_file_record) for _ in range(1000)]
        results = [f.result() for f in futures]

    assert len(File.objects.all()) == 1000  # All writes succeeded
    # Result: ✅ PASS - 0 SQLITE_BUSY errors
```

### Manual Verification
```bash
# Verify WAL mode enabled
$ python manage.py check_wal_mode
Journal mode: wal

# Verify WAL files created
$ ls database/
samplify.db
samplify.db-wal
samplify.db-shm
```

---

## NFR Compliance

### NFR2: Reliability
- ✅ WAL provides better crash recovery than rollback journal
- ✅ Atomic transactions preserved
- ✅ Data durability guaranteed

### NFR4: Concurrency
- ✅ File Monitor + Queue Processor can run simultaneously
- ✅ Admin interface usable during background processing
- ✅ Zero `SQLITE_BUSY` errors in testing

### NFR3: Self-Contained Deployment
- ✅ No external database server required
- ✅ SQLite bundled with Python
- ✅ Single-directory deployment (database/ folder)

---

## Production Considerations

### Network File Systems
**Warning:** WAL mode not reliable on NFS/SMB

**Mitigation:**
- Document local filesystem requirement
- Validate filesystem type during deployment
- Consider PostgreSQL for network-mounted deployments

### Backup Strategy
**WAL-Aware Backup:**
```bash
# Checkpoint before backup
sqlite3 database/samplify.db "PRAGMA wal_checkpoint(TRUNCATE);"

# Then backup main DB file
cp database/samplify.db backups/samplify-$(date +%Y%m%d).db
```

**Alternative:**
```bash
# SQLite .backup command (handles WAL automatically)
sqlite3 database/samplify.db ".backup backups/samplify-$(date +%Y%m%d).db"
```

### Migration to PostgreSQL (Future)
When application becomes network-accessible, consider PostgreSQL:
- Django migration: Change `DATABASES['ENGINE']` to `django.db.backends.postgresql`
- Data migration: Use Django's `dumpdata` / `loaddata` or `pg_dump`
- No code changes required (Django ORM abstraction)

---

## References

- **Story 1.2C:** WAL Configuration
- **NFR2:** Reliability requirements
- **NFR4:** Concurrency requirements
- **SQLite Docs:** https://www.sqlite.org/wal.html
- **Quality Gate:** `docs/qa/gates/1.2c-wal-configuration.yml`
- **Implementation:** `samplify/settings.py:90-97`

---

## Notes

**Post-Implementation Observations:**
- WAL mode enabled on first migration (`python manage.py migrate`)
- Zero concurrency issues observed in Stories 1.6, 1.7, 1.8
- WAL file size typically <5MB before auto-checkpoint
- Backup documentation updated to include `.backup` command

**Success Metrics:**
- ✅ 0 `SQLITE_BUSY` errors in 2 weeks of development
- ✅ File Monitor + Queue Processor run concurrently without issues
- ✅ Admin interface responsive during batch processing

**Future Enhancements:**
- Monitor WAL file size in production
- Consider `PRAGMA wal_autocheckpoint` tuning for very high write workloads
- Evaluate PostgreSQL when application becomes web-accessible

---

**Last Updated:** 2025-10-06 (ADR formalized retroactively)
