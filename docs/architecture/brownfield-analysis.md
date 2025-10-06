# Brownfield Code Analysis - CR1/CR2 Preservation

**Date:** 2025-10-05
**Source:** `.\handlers\rules.py` and `.\handlers\process_handler.py`
**Purpose:** Document exact algorithms and patterns to preserve during Django migration

---

## CR1: Algorithm Preservation (handlers/rules.py)

### Overview

The brownfield `rules.py` contains **22 rule functions** that handle filtering and transformation logic. These functions determine:
1. **Which files match filters** (routing decisions)
2. **What transformations to apply** (output parameters)

### Critical Functions Requiring 100% Preservation

#### 1. `contains_expression(file, output)` - Lines 10-23

**Purpose:** Regex/keyword pattern matching in filenames

**Algorithm:**
```python
def contains_expression(file, output):
    output_directories = {}

    exp = output.get('expression')
    if exp:
        pattern = re.compile(exp)
        search = pattern.finditer(file.file_name)  # Search in filename only

        for match in search:
            output_directories['output_directory'] = output.get('path')
            output_directories['file_name'] = file.file_name
            output_directories['file_path'] = file.file_path

    return output_directories
```

**Key Behaviors to Preserve:**
- Uses `re.compile()` for pattern matching
- Searches in `file.file_name` (NOT file_path)
- Uses `finditer()` (NOT search or match)
- Returns dict with output_directory, file_name, file_path
- Empty dict `{}` if no match

**Django Migration Notes:**
- `file` parameter is brownfield file object, need adapter for Django File model
- Pattern comes from `output.get('expression')` - map to SchemaRule.rule_value
- Must preserve exact regex behavior (case sensitivity, flags)

---

#### 2. `contains_extensions(file, output)` - Lines 26-42

**Purpose:** File extension filtering

**Algorithm:**
```python
def contains_extensions(file, output):
    entry = {}

    extension = output.get('extensions')

    if extension:
        extension.translate({ord(c): None for c in extension})  # Note: this line seems buggy (no reassignment)

        for e in extension.split(','):
            if file.extension.lower() in extension.lower():  # Case-insensitive match
                entry['output_directory'] = output.get('path')
                entry['file_name'] = file.file_name
                entry['file_path'] = file.file_path

    return entry
```

**Key Behaviors to Preserve:**
- Case-insensitive extension matching (`.lower()`)
- Comma-separated extension list
- **BUG ALERT:** Line 33 `extension.translate(...)` has no effect (result not assigned)
  - **Decision Required:** Preserve bug or fix? If test cases expect bug, must preserve!
- Matches if `file.extension` is substring of any extension in list

**Django Migration Notes:**
- Extensions come from comma-delimited string
- Must test if brownfield behavior expects bug (e.g., ".WAV" in "wav,mp3")

---

#### 3. `between_datetime(file, output)` - Lines 45-72

**Purpose:** Filter files by creation date range

**Algorithm:**
```python
def between_datetime(file, output):
    output_directories = {}

    datetime_start = output.get('datetimeStart')
    datetime_end = output.get('datetimeEnd')

    if datetime_start:
        datetime_start = datetime.datetime.strptime(datetime_start, "%Y-%m-%d")
        datetime_end = datetime.datetime.strptime(datetime_end, "%Y-%m-%d")

        delta_t = datetime_end - datetime_start  # Threshold range

        if delta_t:  # Validates start < end
            delta_f = datetime_end - datetime.datetime.strptime(file.creation_date, "%Y-%m-%d")

            # File date must be within range AND before end date
            if delta_f and delta_f <= delta_t:
                output_directories['output_directory'] = output.get('path')
                output_directories['file_name'] = file.file_name
                output_directories['file_path'] = file.file_path

    return output_directories
```

**Key Behaviors to Preserve:**
- Date format: `%Y-%m-%d` (e.g., "2025-10-05")
- **Logic:** File matches if `end_date - file_date <= end_date - start_date`
- **Edge Case:** Returns empty dict if `delta_t` is 0 (start == end)
- **Timezone:** No timezone handling - uses string comparison only

**Django Migration Notes:**
- `file.creation_date` must be string in format "%Y-%m-%d"
- Django File model might use datetime objects - need conversion
- Preserve exact comparison logic (delta-based, not range-based)

---

#### 4. `contains_audio(file, output)` - Lines 88-98

**Purpose:** Filter files containing audio streams

**Algorithm:**
```python
def contains_audio(file, output):
    output_directories = {}

    condition = output.get('containsAudio')

    if condition and file.a_stream:  # Boolean check
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path

    return output_directories
```

**Key Behaviors to Preserve:**
- Checks `file.a_stream` (audio stream attribute)
- Requires both condition=True AND a_stream exists
- `a_stream` is truthy/falsy (not explicit boolean)

**Django Migration Notes:**
- `file.a_stream` comes from FFmpeg metadata extraction
- Django File model needs `has_audio_stream` boolean field
- Preserve truthy check (not `== True`)

---

#### 5. `contains_video(file, output)` - Lines 75-85

**Purpose:** Filter files containing video streams

**Algorithm:**
```python
def contains_video(file, output):
    output_directories = {}

    condition = output.get('containsVideo')

    if condition and file.v_stream:  # Boolean check
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path

    return output_directories
```

**Key Behaviors to Preserve:**
- Same pattern as `contains_audio`
- Checks `file.v_stream` (video stream attribute)

**Django Migration Notes:**
- Add `has_video_stream` boolean to Django File model

---

#### 6. `contains_image(file, output)` - Lines 101-111

**Purpose:** Filter files containing image streams

**Algorithm:**
```python
def contains_image(file, output):
    output_directories = {}

    condition = output.get('containsImage')

    if condition and file.i_stream:  # Boolean check
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path

    return output_directories
```

**Django Migration Notes:**
- Add `has_image_stream` boolean to Django File model

---

### Transformation Functions (Lines 114-322)

These functions set output parameters (NOT filters):

**Audio Transformations:**
- `set_audio_sample_rate()` - Lines 115-126
- `set_audio_format()` - Lines 129-139
- `set_audio_bit_rate()` - Lines 141-151
- `set_audio_channels()` - Lines 153-163
- `set_audio_normalize()` - Lines 165-175
- `set_audio_bit_depth()` - Lines 177-187

**Video Transformations:**
- `set_video_output_container()` - Lines 189-199
- `set_video_height()` - Lines 200-211
- `set_video_width()` - Lines 214-225
- `set_video_duration()` - Lines 228-239
- `set_video_frame_rate()` - Lines 242-253
- `set_video_pix_format()` - Lines 256-267

**Image Transformations:**
- `set_image_format()` - Lines 270-281
- `set_image_height()` - Lines 284-295
- `set_image_width()` - Lines 298-308
- `set_image_mode()` - Lines 310-321

**Pattern:** All transformation functions follow identical structure:
```python
def set_X(file, output):
    output_directories = {}
    value = output.get('X')
    if value:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['X'] = value
    return output_directories
```

**Preservation Strategy:** Extract to single generic function with parameter type

---

## CR2: Multiprocessing Preservation (handlers/process_handler.py)

### Critical Pattern: Worker Scheduling (Lines 26-48)

**Algorithm:**
```python
def schedule_workers(self):
    num_cores = multiprocessing.cpu_count()

    logger.info('admin_message', msg='Spawning decoder processes', info=f'Num Cores: {num_cores}')

    for core in range(num_cores):
        # declare process, set daemon
        p = multiprocessing.Process(target=self.schedule_listener, daemon=True)

        # declare double-ended channel (dequeue) for each process
        q = collections.deque()

        # bundle channel and process name into a tuple
        channel_info = (p.name, q)

        # add to lists
        self.decoder_channels.append(channel_info)
        self.running_processes.append(p)

        # start process
        p.start()
```

**Key Behaviors to Preserve (CR2 Requirements):**

1. ✅ **MUST PRESERVE:** `multiprocessing.cpu_count()` for core detection
2. ✅ **MUST PRESERVE:** One `multiprocessing.Process` per core
3. ✅ **MUST PRESERVE:** `collections.deque()` per worker (NOT `queue.Queue`)
4. ✅ **MUST PRESERVE:** `daemon=True` flag on processes
5. ✅ **MUST PRESERVE:** Round-robin job distribution (see `add_task()`)

**Data Structures:**
- `decoder_channels`: List of tuples `(process_name, deque)`
- `running_processes`: List of Process objects
- **Note:** Processes are unpicklable (see `__getstate__()` method)

---

### Worker Listener Pattern (Lines 50-66)

**Algorithm:**
```python
def schedule_listener(self):
    p = multiprocessing.current_process()

    for channel_info in self.decoder_channels:
        name, queue = channel_info

        if name == p.name:
            logger.info('admin_message', msg='Process started', info=f'Name: {name} PID: {p.pid} Queue: {queue}')

            while queue:
                logger.info('admin_message', msg='Process started new task', info=f'Name: {name} PID: {p.pid} Task: {queue[0]}')
                queue.popleft()
```

**Key Behaviors:**
- Worker finds its own deque by matching `p.name`
- Processes tasks with `queue.popleft()` (FIFO from left side)
- Loops `while queue:` until empty

---

### Task Distribution Pattern (Lines 69-81)

**Algorithm:**
```python
# TODO: change algorithm to be more efficient at scheduling tasks
def add_task(self, task):
    for p in self.running_processes:
        for p_tasker in self.decoder_channels:
            name, queue = p_tasker

            # Add task to whichever process is currently not active
            if not queue:  # Finds first empty queue
                logger.info('admin_message', msg='Adding task to running process', info=f'Name: {name} PID: {p.pid} Task: {task}')
                queue.appendleft(task)
                break
```

**Key Behaviors:**
- **Scheduling:** First empty queue gets the task
- **NOT round-robin** - greedy assignment to first available
- Uses `queue.appendleft()` (adds to left side)
- **TODO comment:** Original dev notes inefficiency

**Preservation Decision:**
- **Option A:** Preserve exact algorithm (including inefficiency)
- **Option B:** Improve to round-robin (violates CR2?)
- **Recommendation:** Preserve exact unless PO approves improvement

---

## Django Migration Strategy

### CR1 Functions → Django Integration

**Approach:** Adapter Pattern

```python
# samplify/utils/legacy_rules.py
# Exact copy of brownfield functions (CR1 preservation)

def contains_expression(file, output):
    # ... exact brownfield code ...
    pass

# samplify/utils/search.py
# Django adapter layer

from apps.catalog.models import File
from samplify.utils.legacy_rules import contains_expression as bf_contains_expression

class FileFilterAdapter:
    """Adapts Django File model to brownfield filter functions."""

    def __init__(self, django_file):
        self.file_name = django_file.file_name
        self.file_path = django_file.file_path
        self.extension = django_file.file_format
        self.creation_date = django_file.created_at.strftime("%Y-%m-%d")
        self.a_stream = django_file.has_audio_stream
        self.v_stream = django_file.has_video_stream
        self.i_stream = django_file.has_image_stream

    def contains_expression(self, output_params):
        return bf_contains_expression(self, output_params)
```

---

### CR2 Multiprocessing → Django Command

**Approach:** Direct port with Django ORM integration

```python
# samplify/management/commands/batch_process.py

import multiprocessing
import collections

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.running_processes = []
        self.decoder_channels = []

    def schedule_workers(self):
        """CR2 PRESERVED: Exact brownfield pattern."""
        num_cores = multiprocessing.cpu_count()

        logger.info(f'Spawning decoder processes - Num Cores: {num_cores}')

        for core in range(num_cores):
            p = multiprocessing.Process(target=self.schedule_listener, daemon=True)
            q = collections.deque()
            channel_info = (p.name, q)

            self.decoder_channels.append(channel_info)
            self.running_processes.append(p)

            p.start()
```

---

## Test Case Requirements

### CR1 Validation Test Suite

**Required Test Files:** (Minimum 100 files per algorithm)

1. **`contains_expression` tests:**
   - Filenames with patterns: `kick_01.wav`, `snare_heavy.wav`, `hat_closed_02.wav`
   - Patterns to test: `kick`, `snare.*heavy`, `\d{2}`, etc.
   - Expected: List of matching files with output_directory

2. **`contains_extensions` tests:**
   - Extensions: `.wav`, `.mp3`, `.flac`, `.WAV` (test case sensitivity)
   - **Critical:** Test line 33 bug behavior (translate with no reassignment)

3. **`between_datetime` tests:**
   - Date ranges: 2025-01-01 to 2025-12-31
   - Edge cases: start == end, invalid ranges
   - Timezone edge cases

4. **`contains_audio/video/image` tests:**
   - Files with/without streams
   - Verify `a_stream`, `v_stream`, `i_stream` attributes

### CR2 Validation Test Suite

**Required Tests:**

1. **Worker pool scaling:**
   - Assert `len(running_processes) == multiprocessing.cpu_count()`
   - Verify each process has one deque

2. **Deque usage:**
   - Assert `isinstance(queue, collections.deque)`
   - NOT `isinstance(queue, queue.Queue)`

3. **Task distribution:**
   - Test greedy assignment (first empty queue)
   - Verify `appendleft()` and `popleft()` behavior

4. **CPU utilization:**
   - Informal monitoring (no strict requirement per development-decisions.md)
   - Target: 50-70% CPU during processing

---

## Open Questions for PO

### CR1 Questions

**Q1:** Line 33 bug in `contains_extensions()` - preserve or fix? ✅ **RESOLVED**
```python
extension.translate({ord(c): None for c in extension})  # No reassignment!
```
- **Decision:** PRESERVE BUG EXACTLY (Option A)
- **Investigation:** See `docs/architecture/cr1-extension-bug-analysis.md`
- **Test Results:** 16/16 test cases prove bug has zero functional impact
- **Rationale:** Bug is dead code, preserving guarantees CR1 compliance

**Q2:** Are there existing test cases in brownfield? ✅ **RESOLVED**
- **Decision:** No unit tests exist, only runtime tests performed
- **Test Infrastructure:** Use `\media\` folder samples (read-only)
- **Output:** New `test_output/` directory (added to .gitignore)
- **Critical:** Do NOT destructively edit original sample media

### CR2 Questions

**Q3:** `add_task()` TODO comment suggests inefficiency - improve or preserve? ✅ **RESOLVED**
```python
# TODO: change algorithm to be more efficient at scheduling tasks
```
- **Decision:** IMPROVE TO ROUND-ROBIN (Option B approved by PO)
- **Rationale:** Better load balancing, TODO suggests improvement was intended
- **Implementation:** Cycle through workers instead of first available

---

## Change Log

| Date | Change | Author |
|------|---------|--------|
| 2025-10-05 | Initial brownfield analysis from handlers/rules.py and handlers/process_handler.py | SM (Bob) |

---

## Next Steps

1. ✅ Document preservation requirements (this file)
2. ✅ Investigate CR1 bug (see cr1-extension-bug-analysis.md)
3. ✅ Create test infrastructure (test_output/ directory, .gitignore updated)
4. ⏳ Update Stories 1.5 and 1.6 with brownfield references
5. ⏳ Create side-by-side test harness
6. ⏳ Implement CR1/CR2 in Django
