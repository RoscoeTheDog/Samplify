# Story 1.8: Queue Processor Watchdog

## Status
**Approved**

---

## User Story
As a **developer**,
I want **a queue processor watchdog service**,
So that **I can automatically process files as they're added to the database by the file monitor**.

---

## Story Context
**Existing System Integration:**
- Integrates with: Story 1.6 (batch processing), Story 1.7 (file monitor)
- Technology: Django management command, multiprocessing patterns from process_handler.py
- Follows pattern: CR2 multiprocessing orchestration preservation
- Touch points: Database queue polling, batch processing execution, coordination with file monitor

---

## Acceptance Criteria

**Functional Requirements:**
1. Queue processor created as Django management command (`manage.py queue_processor`)
2. Service polls database for unprocessed files (status='pending')
3. Service executes batch processing for queued files
4. Service updates file status (pending → processing → completed/failed)
5. Service respects active schema configuration
6. Polling interval configurable (default: 5 seconds)
7. Service runs as background process (blocking command)

**Integration Requirements:**
8. Integrates with File model (Story 1.2A)
9. Integrates with batch processing (Story 1.6)
10. Coordinates with file monitor (Story 1.7) - no race conditions
11. Uses multiprocessing patterns from Story 1.6 (CR2 preservation)

**Quality Requirements:**
12. Processing starts within polling interval of file arrival
13. No race conditions with file monitor (atomic status updates)
14. Service stable during long-running operation (24+ hours)
15. Graceful shutdown on interrupt (SIGINT/SIGTERM)

---

## Tasks / Subtasks

- [ ] **Task 1: Create Django management command structure** (AC: 1, 7)
  - [ ] Create `samplify/management/commands/queue_processor.py`
  - [ ] Implement BaseCommand with blocking handle() method
  - [ ] Add command-line arguments (--poll-interval, --schema-id)
  - [ ] Add graceful shutdown handling (SIGINT/SIGTERM)

- [ ] **Task 2: Implement database polling logic** (AC: 2, 5, 6)
  - [ ] Query File model for status='pending' files
  - [ ] Filter by active schema
  - [ ] Configurable polling interval (default 5 seconds)
  - [ ] Use select_for_update() to prevent race conditions

- [ ] **Task 3: Integrate batch processing from Story 1.6** (AC: 3, 9, 11)
  - [ ] Import batch processing logic from Story 1.6
  - [ ] Preserve multiprocessing patterns (CR2)
  - [ ] Schedule workers using existing deque distribution
  - [ ] Call FFmpeg transformations per schema rules

- [ ] **Task 4: Implement status management** (AC: 4, 13)
  - [ ] Atomic status transitions: pending → processing → completed/failed
  - [ ] Use database transactions for status updates
  - [ ] Handle concurrent updates (select_for_update locking)
  - [ ] Log all status changes (loguru)

- [ ] **Task 5: Add coordination with file monitor** (AC: 10, 13)
  - [ ] No shared state with file monitor (Story 1.7)
  - [ ] Database as single source of truth
  - [ ] Atomic operations prevent race conditions
  - [ ] Test concurrent file monitor + queue processor

- [ ] **Task 6: Add stability and error handling** (AC: 14, 15)
  - [ ] Graceful shutdown on SIGINT/SIGTERM
  - [ ] Auto-restart on worker failures
  - [ ] Handle database connection errors (retry with backoff)
  - [ ] Log all processing events (success/failure)

- [ ] **Task 7: Testing** (AC: 12, 13, 14, 15)
  - [ ] Unit tests for polling logic
  - [ ] Integration test with batch processing
  - [ ] Race condition test (concurrent file monitor)
  - [ ] Stability test (24-hour continuous operation)
  - [ ] Graceful shutdown test

---

## Dev Notes

### Previous Story Insights
**From Story 1.6 (Batch Processing):**
- Batch processing preserves multiprocessing patterns (CR2) [Source: Story 1.6]
- Worker scheduling uses deque-based distribution
- One worker per CPU core
- FFmpeg transformations already implemented

**From Story 1.7 (File Monitor):**
- File monitor creates File records with status='pending'
- Monitor operates independently (no shared state)
- Database transactions ensure atomicity

### File Locations (Source Tree)
**Management Command Location:** [Source: architecture/source-tree.md]
```
samplify/
└── management/
    └── commands/
        └── queue_processor.py    # Create this file
```

**Test Location:**
```
tests/
└── test_queue_processor.py       # Create this file
```

### Data Models
**File Model (Story 1.2A):** [Source: architecture/database-schema-design.md]
```python
class File(models.Model):
    uid = CharField(max_length=10, unique=True)
    path = CharField(max_length=500, unique=True)
    processing_status = CharField(
        choices=[('pending', 'Pending'), ('processing', 'Processing'),
                 ('completed', 'Completed'), ('failed', 'Failed')]
    )
    # ... metadata fields
```

**Schema Model (Story 1.2B):**
```python
class Schema(models.Model):
    name = CharField(max_length=255, unique=True)
    is_active = BooleanField(default=False)  # Only one active schema
```

### Queue Processor Pattern
**Django Management Command Structure:**
```python
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.catalog.models import File
from apps.schemas.models import Schema
from loguru import logger
import time
import signal
import sys

class Command(BaseCommand):
    help = 'Process queued files from database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--poll-interval',
            type=int,
            default=5,
            help='Polling interval in seconds (default: 5)'
        )
        parser.add_argument(
            '--schema-id',
            type=int,
            help='Process only this schema (default: active schema)'
        )

    def handle(self, *args, **options):
        poll_interval = options['poll_interval']
        schema_id = options.get('schema_id')

        # Get active schema
        if schema_id:
            schema = Schema.objects.get(id=schema_id)
        else:
            schema = Schema.objects.get(is_active=True)

        logger.info(f"Queue processor started for schema: {schema.name}")

        # Graceful shutdown handling
        self.running = True

        def signal_handler(sig, frame):
            logger.info("Shutting down queue processor...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Main processing loop
        while self.running:
            try:
                # Query pending files (atomic operation)
                with transaction.atomic():
                    pending_files = File.objects.select_for_update(
                        skip_locked=True  # Skip files locked by other processors
                    ).filter(
                        processing_status='pending',
                        input_directory__schema=schema
                    )[:10]  # Batch size

                    if pending_files:
                        # Mark as processing
                        for file in pending_files:
                            file.processing_status = 'processing'
                            file.save()

                        # Execute batch processing
                        self.process_batch(list(pending_files))

                # Sleep before next poll
                time.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                time.sleep(poll_interval)

        logger.info("Queue processor stopped")

    def process_batch(self, files):
        """Execute batch processing for queued files."""
        from samplify.management.commands.batch_process import Command as BatchCommand

        batch_cmd = BatchCommand()
        batch_cmd.process_files(files)
```

**Usage:**
```bash
# Start queue processor (default: 5-second polling)
python manage.py queue_processor

# Custom polling interval
python manage.py queue_processor --poll-interval=10

# Process specific schema
python manage.py queue_processor --schema-id=1
```

### Coordination with File Monitor (Story 1.7)
**Race Condition Prevention:** [Source: Story 1.7]

**Pattern:**
1. **File Monitor (Story 1.7)**: Creates File with `status='pending'`
2. **Queue Processor (Story 1.8)**: Polls for `status='pending'`, updates to `'processing'`
3. **Atomicity**: Use `select_for_update(skip_locked=True)` to prevent conflicts

**Database Locking:**
```python
# Queue processor locks files before processing
pending_files = File.objects.select_for_update(
    skip_locked=True  # Skip files locked by other transactions
).filter(processing_status='pending')

# File monitor uses atomic transactions
with transaction.atomic():
    File.objects.get_or_create(
        path=event.src_path,
        defaults={'processing_status': 'pending'}
    )
```

**No shared state**: Each service queries database independently

### Multiprocessing Integration (CR2 Preservation)
**From Story 1.6 Batch Processing:** [Source: Story 1.6]

**Preserved Patterns:**
- Worker scheduling: `multiprocessing.cpu_count()` workers
- Deque distribution: `collections.deque()` per worker
- Process spawning: `daemon=True` flag
- Round-robin job distribution

**Integration in Queue Processor:**
```python
def process_batch(self, files):
    """Trigger batch processing with multiprocessing (CR2)."""
    from samplify.management.commands.batch_process import Command as BatchCommand

    # Batch command preserves multiprocessing patterns
    batch_cmd = BatchCommand()
    batch_cmd.schedule_workers()  # CR2: One worker per CPU core
    batch_cmd.distribute_jobs(files)  # CR2: Deque-based distribution
```

### Error Handling Requirements
**Database Errors:**
- Connection errors: Retry with exponential backoff
- Lock timeouts: Skip locked files, retry next poll
- Transaction failures: Rollback, log error, continue

**Processing Errors:**
- FFmpeg errors: Mark file as 'failed', log error
- Worker crashes: Auto-restart worker pool
- File not found: Mark as 'failed', log warning

---

## Dev Notes > Testing

### Test File Location
[Source: architecture/testing-strategy.md]
```
tests/
└── test_queue_processor.py
```

### Testing Standards
**Framework:** pytest + pytest-django [Source: architecture/tech-stack.md]

**Test Coverage Target:** 80%+ for queue processor service

**Test Categories:**
1. **Unit Tests - Polling Logic**
   - Test query for pending files
   - Test active schema filtering
   - Test batch size limit
   - Test polling interval

2. **Integration Tests - Batch Processing**
   - Test batch processing execution
   - Test status transitions (pending → processing → completed)
   - Test FFmpeg transformations
   - Test worker pool scaling

3. **Race Condition Tests - Coordination with File Monitor**
   - Test concurrent file monitor + queue processor
   - Test atomic status updates (no double-processing)
   - Test database locking (select_for_update)
   - Test no data loss during concurrent operations

4. **Stability Tests**
   - 24-hour continuous operation test
   - Test graceful shutdown (SIGINT)
   - Test auto-recovery from errors

**Test Data:**
Use media library from `/media/` folder [Source: architecture/testing-strategy.md]

**Example Test:**
```python
import pytest
from django.test import TransactionTestCase
from apps.catalog.models import File
from apps.schemas.models import Schema, InputDirectory
from samplify.management.commands.queue_processor import Command
import threading
import time

class QueueProcessorTest(TransactionTestCase):
    def test_pending_file_processing(self):
        """Test queue processor processes pending files."""
        # Create schema and file
        schema = Schema.objects.create(name="Test Schema", is_active=True)
        input_dir = InputDirectory.objects.create(schema=schema, path="/test/")
        file = File.objects.create(
            path="/test/file.wav",
            filename="file.wav",
            input_directory=input_dir,
            processing_status='pending'
        )

        # Run queue processor (one iteration)
        cmd = Command()
        cmd.handle(poll_interval=1, schema_id=schema.id)

        # Verify file processed
        file.refresh_from_db()
        assert file.processing_status in ['processing', 'completed']

    def test_race_condition_prevention(self):
        """Test no race conditions with file monitor."""
        from samplify.management.commands.file_monitor import Command as MonitorCommand

        schema = Schema.objects.create(name="Test Schema", is_active=True)
        input_dir = InputDirectory.objects.create(schema=schema, path="/test/")

        # Start queue processor in thread
        queue_cmd = Command()
        queue_thread = threading.Thread(
            target=queue_cmd.handle,
            kwargs={'poll_interval': 1, 'schema_id': schema.id}
        )
        queue_thread.daemon = True
        queue_thread.start()

        # Simulate file monitor creating files
        for i in range(10):
            File.objects.create(
                path=f"/test/file_{i}.wav",
                filename=f"file_{i}.wav",
                input_directory=input_dir,
                processing_status='pending'
            )
            time.sleep(0.1)

        # Wait for processing
        time.sleep(5)

        # Verify all files processed exactly once (no duplicates)
        files = File.objects.all()
        assert files.count() == 10
        for file in files:
            assert file.processing_status in ['completed', 'failed']

    def test_select_for_update_locking(self):
        """Test database locking prevents concurrent processing."""
        schema = Schema.objects.create(name="Test Schema", is_active=True)
        input_dir = InputDirectory.objects.create(schema=schema, path="/test/")
        file = File.objects.create(
            path="/test/file.wav",
            filename="file.wav",
            input_directory=input_dir,
            processing_status='pending'
        )

        # Simulate two queue processors
        from django.db import transaction

        def processor_1():
            with transaction.atomic():
                locked_files = File.objects.select_for_update().filter(id=file.id)
                for f in locked_files:
                    f.processing_status = 'processing'
                    f.save()
                time.sleep(2)  # Hold lock

        def processor_2():
            with transaction.atomic():
                # Should skip locked files
                locked_files = File.objects.select_for_update(
                    skip_locked=True
                ).filter(id=file.id)
                assert locked_files.count() == 0  # File locked by processor_1

        thread1 = threading.Thread(target=processor_1)
        thread2 = threading.Thread(target=processor_2)

        thread1.start()
        time.sleep(0.5)  # Let processor_1 acquire lock
        thread2.start()

        thread1.join()
        thread2.join()
```

**Running Tests:**
```bash
# Run all queue processor tests
pytest tests/test_queue_processor.py -v

# Run with coverage
pytest tests/test_queue_processor.py --cov=samplify.management.commands.queue_processor --cov-report=html

# Run race condition test
pytest tests/test_queue_processor.py::test_race_condition_prevention -v

# Run stability test (24 hours)
pytest tests/test_queue_processor.py::test_24_hour_stability -v --timeout=86400
```

---

## Definition of Done
- [ ] Queue processor command implemented
- [ ] Database polling working
- [ ] Batch processing integration verified
- [ ] Race conditions tested and resolved
- [ ] Long-running stability tested
- [ ] Documentation updated with queue processor details

---

## Risk Assessment
- **Primary Risk:** Race conditions between file monitor and queue processor
- **Mitigation:** Database locking (select_for_update), atomic status updates, comprehensive concurrency testing
- **Rollback:** Disable queue processor, use manual batch processing (Story 1.6)

---

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-05 | 1.0 | Story completed by Scrum Master - added Status, Tasks, Dev Notes, Testing sections | SM (Bob) |

---

## Dev Agent Record

### Agent Model Used
(To be populated by dev agent during implementation)

### Debug Log References
(To be populated by dev agent during implementation)

### Completion Notes
(To be populated by dev agent during implementation)

### File List
(To be populated by dev agent during implementation)

---

## QA Results
(To be populated by QA agent after implementation)
