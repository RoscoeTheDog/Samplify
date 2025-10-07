# Concurrency & Multiprocessing Patterns

**Status:** Draft
**Created:** 2025-10-06
**Owner:** Winston (Architect)
**Related ADRs:** ADR 0003 (Busy-Wait Pattern)
**Related Stories:** 1.6, 1.8
**Related NFRs:** NFR1 (Performance), CR2 (Legacy Pattern Preservation)

---

## Purpose

This document defines Samplify's **concurrency and multiprocessing patterns** to ensure consistent, safe, and performant parallel execution across all components.

**Motivation:** Stories 1.6 and 1.8 require multiprocessing for batch operations. CR2 mandates preserving legacy patterns while building new capabilities.

---

## Core Principles

### 1. Process vs Thread Selection

**Use Multiprocessing When:**
- CPU-bound work (FFmpeg encoding, file processing)
- Bypassing Python GIL (Global Interpreter Lock)
- Isolating failures (process crash doesn't kill main app)
- Legacy pattern preservation (CR2 requirement)

**Use Threading When:**
- I/O-bound work (network requests, file reads)
- Lightweight tasks with shared memory needs
- Monitoring/logging background tasks

**Use AsyncIO When:**
- Many concurrent I/O operations (future web deployment)
- Event-driven architecture
- WebSocket connections or streaming

**Current Choice:** Multiprocessing (per CR2 legacy pattern)

---

### 2. Safe Concurrency Patterns

**Avoid:**
- Shared mutable state without locks
- Busy-wait polling (see ADR 0003)
- Uncontrolled process spawning
- Silent failures in worker processes

**Prefer:**
- Message passing via queues
- Immutable data structures
- Event-based signaling
- Explicit error handling and logging

---

### 3. Graceful Shutdown

**All concurrent components MUST:**
- Handle SIGINT/SIGTERM signals
- Drain queues before exit
- Join worker processes/threads
- Log shutdown events

---

## Multiprocessing Architecture

### Worker Pool Pattern (Stories 1.6, 1.8)

**Pattern:** Fixed pool of worker processes consuming from a shared task queue.

**Components:**
1. **Manager Process:** Creates workers, distributes tasks
2. **Task Queue:** `multiprocessing.Queue()` for work distribution
3. **Worker Processes:** Consume tasks, execute work, report results
4. **Result Queue:** Optional for collecting worker outputs

**Diagram:**
```
┌─────────────────────────────────────────────────────────┐
│                    Manager Process                      │
│  - Scans for pending files                              │
│  - Enqueues tasks to task_queue                         │
│  - Monitors worker health                               │
└─────────────────┬───────────────────────────────────────┘
                  │
          ┌───────┴────────┐
          │   Task Queue   │  (multiprocessing.Queue)
          └───────┬────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
┌────▼────┐  ┌───▼─────┐  ┌──▼──────┐
│ Worker 1│  │ Worker 2│  │ Worker 3│  (Process pool)
│ FFmpeg  │  │ FFmpeg  │  │ FFmpeg  │
└────┬────┘  └───┬─────┘  └──┬──────┘
     │            │            │
     └────────────┼────────────┘
                  │
          ┌───────▼────────┐
          │  Result Queue  │  (Optional)
          └────────────────┘
```

**Reference Implementation (Story 1.6):**
```python
import multiprocessing
from multiprocessing import Queue, Process

class BatchProcessor:
    def __init__(self, worker_count=4):
        self.worker_count = worker_count
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.workers = []

    def start_workers(self):
        """Spawn worker processes."""
        for i in range(self.worker_count):
            worker = Process(
                target=self.worker_loop,
                args=(self.task_queue, self.result_queue, i)
            )
            worker.start()
            self.workers.append(worker)
            logger.info(f"Started worker {i} (PID: {worker.pid})")

    @staticmethod
    def worker_loop(task_queue, result_queue, worker_id):
        """Worker process main loop."""
        logger.info(f"Worker {worker_id} started")

        while True:
            try:
                # Get task (blocking with timeout)
                task = task_queue.get(timeout=1)

                # Sentinel value signals shutdown
                if task is None:
                    logger.info(f"Worker {worker_id} received shutdown signal")
                    break

                # Process task
                result = process_file(task)

                # Report result
                result_queue.put(result)

            except queue.Empty:
                # No tasks available, continue waiting
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                # Report error but continue processing
                result_queue.put({'error': str(e), 'task': task})

        logger.info(f"Worker {worker_id} exiting")

    def enqueue_tasks(self, tasks):
        """Add tasks to queue for workers."""
        for task in tasks:
            self.task_queue.put(task)

    def wait_for_completion(self):
        """Wait for all workers to finish."""
        # Signal workers to shutdown (sentinel values)
        for _ in self.workers:
            self.task_queue.put(None)

        # Wait for workers to exit
        for worker in self.workers:
            worker.join()

        logger.info("All workers completed")

    def shutdown(self):
        """Graceful shutdown of worker pool."""
        self.wait_for_completion()
```

**Usage:**
```python
processor = BatchProcessor(worker_count=4)
processor.start_workers()
processor.enqueue_tasks(pending_files)
processor.wait_for_completion()
```

---

### Queue Processor Pattern (Story 1.8)

**Pattern:** Polling-based processor that queries database for pending work.

**Differences from Worker Pool:**
- No explicit task queue (uses database as queue)
- Continuous polling loop
- Batch fetching for efficiency

**Reference Implementation:**
```python
class QueueProcessor:
    def __init__(self, batch_size=50, poll_interval=5):
        self.batch_size = batch_size
        self.poll_interval = poll_interval
        self.running = True

    def run(self):
        """Main polling loop."""
        logger.info("Queue processor started")

        while self.running:
            # Fetch batch of pending files
            pending_files = File.objects.filter(
                processing_status='pending'
            )[:self.batch_size]

            if pending_files:
                # Process batch with worker pool
                self.process_batch(pending_files)
            else:
                # No work, sleep before next poll
                time.sleep(self.poll_interval)

    def process_batch(self, files):
        """Process batch using worker pool."""
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_file, f) for f in files]

            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.handle_result(result)
                except Exception as e:
                    logger.error(f"Batch processing error: {e}")

    def shutdown(self):
        """Stop polling loop."""
        self.running = False
        logger.info("Queue processor shutting down")
```

**Signal Handling:**
```python
import signal

def signal_handler(signum, frame):
    """Handle SIGINT/SIGTERM for graceful shutdown."""
    logger.info(f"Received signal {signum}, shutting down...")
    processor.shutdown()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

---

## Process Synchronization Patterns

### Pattern 1: Event-Based Signaling (Future - ADR 0003 Refactoring)

**Use Case:** Notify main process when workers complete

**Implementation:**
```python
import multiprocessing

class EventBasedWorkerPool:
    def __init__(self, worker_count=4):
        self.completion_events = [multiprocessing.Event() for _ in range(worker_count)]
        self.workers = []

    @staticmethod
    def worker_with_event(task_queue, completion_event, worker_id):
        """Worker signals completion via event."""
        while True:
            task = task_queue.get()
            if task is None:
                break
            process_file(task)

        # Signal completion
        completion_event.set()
        logger.info(f"Worker {worker_id} signaled completion")

    def wait_for_completion(self):
        """Event-based wait (zero CPU overhead)."""
        for event in self.completion_events:
            event.wait()  # Blocks until worker signals
        logger.info("All workers completed (event-based)")
```

**Benefits vs Busy-Wait:**
- Zero CPU overhead (no polling)
- Instant completion detection
- Scales to many workers

**Status:** Deferred to post-MVP (ADR 0003 refactoring)

---

### Pattern 2: Semaphore for Resource Limiting

**Use Case:** Limit concurrent FFmpeg processes (memory/CPU constraints)

**Implementation:**
```python
from multiprocessing import Semaphore

# Global semaphore (max 4 concurrent FFmpeg instances)
ffmpeg_semaphore = Semaphore(4)

def process_video_file(file_path):
    """Process video with FFmpeg, limited by semaphore."""
    with ffmpeg_semaphore:  # Acquire/release automatically
        logger.info(f"Processing {file_path} (semaphore acquired)")
        subprocess.run(['ffmpeg', '-i', file_path, ...])
        logger.info(f"Processing {file_path} complete (semaphore released)")
```

**Benefits:**
- Prevents resource exhaustion
- Automatic cleanup (context manager)
- Fair scheduling (FIFO)

---

### Pattern 3: Manager for Shared State (Use Sparingly)

**Use Case:** Shared counters, progress tracking across workers

**Implementation:**
```python
from multiprocessing import Manager

class SharedProgressTracker:
    def __init__(self):
        manager = Manager()
        self.progress = manager.dict({
            'completed': 0,
            'failed': 0,
            'total': 0,
        })
        self.lock = manager.Lock()

    def increment_completed(self):
        with self.lock:
            self.progress['completed'] += 1

    def get_progress(self):
        with self.lock:
            return dict(self.progress)

# Usage in worker
tracker = SharedProgressTracker()

def worker_with_tracking(task_queue, tracker):
    while True:
        task = task_queue.get()
        if task is None:
            break

        try:
            process_file(task)
            tracker.increment_completed()
        except Exception as e:
            tracker.increment_failed()
```

**Warning:** Adds synchronization overhead. Prefer message passing (queues) when possible.

---

## Database Concurrency (SQLite WAL Mode)

### Safe Database Access from Workers

**Pattern: Per-Worker Connection**
```python
def worker_with_db(task_queue):
    """Each worker creates its own DB connection."""
    from django.db import connection

    while True:
        task = task_queue.get()
        if task is None:
            break

        # Django creates per-thread connection automatically
        with transaction.atomic():
            file_record = File.objects.get(id=task['file_id'])
            file_record.processing_status = 'processing'
            file_record.save()

            # Process file...

            file_record.processing_status = 'completed'
            file_record.save()

    # Close connection on worker exit
    connection.close()
```

**Key Points:**
- Each worker gets separate DB connection
- Use `transaction.atomic()` for consistency
- Close connections on worker exit
- WAL mode (ADR 0004) enables concurrent writes

**Retry on Lock Errors:**
```python
from django.db import OperationalError

def update_with_retry(file_record, max_retries=5):
    """Retry database updates on lock errors."""
    for attempt in range(max_retries):
        try:
            with transaction.atomic():
                file_record.save()
            return
        except OperationalError as e:
            if 'database is locked' in str(e) and attempt < max_retries - 1:
                delay = 2 ** attempt  # Exponential backoff
                logger.warning(f"DB locked, retrying in {delay}s")
                time.sleep(delay)
            else:
                raise
```

---

## Error Handling in Concurrent Contexts

### Worker Exception Handling

**Pattern: Catch-Log-Continue**
```python
def robust_worker(task_queue, result_queue):
    """Worker with comprehensive error handling."""
    while True:
        task = None
        try:
            task = task_queue.get(timeout=1)
            if task is None:
                break

            result = process_file(task)
            result_queue.put({'status': 'success', 'result': result})

        except queue.Empty:
            continue  # No work, keep waiting

        except FileNotFoundError as e:
            # Permanent error - log and skip
            logger.error(f"File not found: {task}, error: {e}")
            result_queue.put({'status': 'permanent_error', 'task': task, 'error': str(e)})

        except Exception as e:
            # Unexpected error - log with traceback
            logger.exception(f"Worker error processing {task}")
            result_queue.put({'status': 'unexpected_error', 'task': task, 'error': str(e)})

    logger.info("Worker exiting normally")
```

**Error Categories:**
- **Transient:** Retry in main process or next poll
- **Permanent:** Skip file, mark as failed in DB
- **Fatal:** Log and raise (will terminate worker, manager detects)

---

### Manager Monitoring Worker Health

**Pattern: Detect Dead Workers**
```python
class RobustBatchProcessor:
    def monitor_workers(self):
        """Check worker health and restart if needed."""
        for i, worker in enumerate(self.workers):
            if not worker.is_alive():
                logger.error(f"Worker {i} (PID {worker.pid}) died, restarting...")

                # Restart worker
                new_worker = Process(target=self.worker_loop, args=(self.task_queue, i))
                new_worker.start()
                self.workers[i] = new_worker
                logger.info(f"Restarted worker {i} (new PID: {new_worker.pid})")
```

---

## Performance Optimization Patterns

### Pattern 1: Batch Processing

**Inefficient (1-by-1):**
```python
for file in pending_files:
    task_queue.put(file)  # 1000 queue operations
```

**Efficient (Batching):**
```python
batch_size = 50
for i in range(0, len(pending_files), batch_size):
    batch = pending_files[i:i+batch_size]
    task_queue.put(batch)  # 20 queue operations
```

---

### Pattern 2: Worker Pool Size Tuning

**Formula:**
```python
import os

# CPU-bound work: N = CPU cores
cpu_bound_workers = os.cpu_count()

# I/O-bound work: N = 2 * CPU cores (or higher)
io_bound_workers = os.cpu_count() * 2

# Mixed workload (FFmpeg + file I/O): 1.5 * CPU cores
mixed_workers = int(os.cpu_count() * 1.5)
```

**Configuration (Story 1.6):**
```python
# Samplify default: 4 workers (configurable)
BATCH_PROCESSING_WORKERS = os.getenv('BATCH_WORKERS', 4)
```

---

### Pattern 3: Avoid Overspawning

**Bad:**
```python
# Spawns 1000 processes!
with ProcessPoolExecutor(max_workers=len(files)) as executor:
    futures = [executor.submit(process_file, f) for f in files]
```

**Good:**
```python
# Spawns optimal number of workers
with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_file, f) for f in files]
```

---

## Testing Concurrent Code

### Unit Testing with Mocking

**Pattern: Mock Queue for Isolation**
```python
from unittest.mock import Mock, patch

def test_worker_processes_task():
    """Test worker logic without spawning processes."""
    task_queue = Mock()
    result_queue = Mock()

    # Mock queue.get() to return test task then None (shutdown)
    task_queue.get.side_effect = [
        {'file_id': 123, 'action': 'process'},
        None,  # Shutdown signal
    ]

    # Run worker (single-threaded for test)
    worker_loop(task_queue, result_queue, worker_id=0)

    # Verify result reported
    assert result_queue.put.called
    result = result_queue.put.call_args[0][0]
    assert result['status'] == 'success'
```

---

### Integration Testing with Real Processes

**Pattern: Small Worker Pool**
```python
@pytest.mark.slow
def test_batch_processor_integration():
    """Integration test with real multiprocessing."""
    processor = BatchProcessor(worker_count=2)  # Small pool
    processor.start_workers()

    # Enqueue test tasks
    test_files = [{'id': i, 'path': f'/tmp/test_{i}.wav'} for i in range(10)]
    processor.enqueue_tasks(test_files)

    # Wait for completion
    processor.wait_for_completion()

    # Verify all tasks processed
    assert processor.result_queue.qsize() == 10
```

---

### Concurrency Testing (Race Conditions)

**Pattern: Stress Test with Many Iterations**
```python
def test_concurrent_database_writes():
    """Stress test for race conditions in DB writes."""
    import threading

    results = []
    errors = []

    def concurrent_writer(file_id):
        try:
            with transaction.atomic():
                file_record = File.objects.get(id=file_id)
                file_record.processing_status = 'completed'
                file_record.save()
            results.append(file_id)
        except Exception as e:
            errors.append(e)

    # Spawn 50 threads writing concurrently
    threads = [threading.Thread(target=concurrent_writer, args=(i,)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify no errors (WAL mode handles contention)
    assert len(errors) == 0
    assert len(results) == 50
```

---

## Checklist for New Concurrent Components

### Design Phase
- [ ] Choose concurrency model (multiprocessing/threading/asyncio)
- [ ] Justify choice (CPU-bound vs I/O-bound)
- [ ] Define task distribution mechanism (queue/polling)
- [ ] Plan error handling strategy

### Implementation Phase
- [ ] Implement graceful shutdown (SIGINT/SIGTERM handlers)
- [ ] Add worker health monitoring (restart dead workers)
- [ ] Use event-based signaling (avoid busy-wait)
- [ ] Implement per-worker DB connections (if needed)
- [ ] Add comprehensive logging (worker ID, task context)

### Testing Phase
- [ ] Unit tests with mocked queues
- [ ] Integration tests with real processes (small pool)
- [ ] Stress tests for race conditions
- [ ] Performance validation (worker pool size tuning)

### Documentation Phase
- [ ] Document concurrency model in code comments
- [ ] Add usage examples
- [ ] Explain signal handling
- [ ] Document configuration (worker count, timeouts)

---

## Related Documentation

**ADRs:**
- ADR 0003: Busy-Wait Pattern (tech debt, future refactoring to events)

**Stories:**
- Story 1.6: Batch Processing (worker pool pattern)
- Story 1.8: Queue Processor (polling pattern)

**NFRs:**
- NFR1: CPU utilization (50-70% during batch processing)
- CR2: Legacy pattern preservation

**Code References:**
- `samplify/management/commands/batch_process.py` - Worker pool implementation
- `samplify/management/commands/queue_processor.py` - Polling processor

---

## Future Enhancements

### Phase 2 (Post-MVP)
- [ ] Refactor busy-wait to event-based (ADR 0003)
- [ ] Implement circuit breaker for FFmpeg failures
- [ ] Add worker pool auto-scaling (based on queue depth)
- [ ] Centralize concurrency utilities (`samplify/utils/concurrency.py`)

### Phase 3 (Web Deployment)
- [ ] Evaluate Celery for distributed task queue
- [ ] AsyncIO for web request handling
- [ ] Redis/RabbitMQ for persistent queue

---

**Last Updated:** 2025-10-06
**Owner:** Winston (Architect)
**Status:** Draft → Under Review
