# GitHub Issue #2 - Draft Content for RoscoeTheDog/loguru

**Copy and paste this content when creating the issue on GitHub**

---

## Title

`KeyError when using logger.exception() with callable format functions`

---

## Labels

`bug`, `hierarchical-logging`, `needs-investigation`

---

## Description

### Summary

When using `logger.exception()` with a custom format function (callable), loguru raises `KeyError: "'name'"` (or `"'verbosity'"`) when attempting to format the exception message. This prevents exception output from callable formatters, specifically affecting hierarchical logging.

**Critical Note**: Exception logging **works correctly** with JSON file handlers - only callable format functions fail.

---

### Environment

- **Loguru Version**: 0.7.3 (RoscoeTheDog/loguru fork - commit `1cf3410`)
- **Python Version**: 3.10+
- **OS**: Windows 11 / Linux / macOS
- **Feature**: Hierarchical logging with `create_hierarchical_format_function()`

---

### Minimal Reproduction

```python
import sys
from loguru import logger
from loguru._template_formatters import create_hierarchical_format_function

# Remove default handler
logger.remove()

# Add hierarchical console handler with callable format
console_format_func = create_hierarchical_format_function(
    format_string="{time:HH:mm:ss} | {level} | {name} | {message}",
    template="hierarchical"
)

logger.add(
    sys.stderr,
    format=console_format_func,
    colorize=True,
    level="INFO",
    backtrace=True,
    diagnose=True,
)

# Regular logging works perfectly ✅
logger.info("This works fine", context="regular_log")

# Exception logging fails ❌
try:
    data = {"name": "test"}
    missing = data["missing_key"]
except KeyError as e:
    logger.exception("This fails", error=str(e))
```

---

### Expected Behavior

Should display hierarchical formatted exception with box-drawing characters:

```
┌─ 20:00:00 │ ❌ ERROR │ __main__
├─ This fails
├─ Context:
│  └─ error: missing_key
├─ Exception:
│  └─ KeyError: 'missing_key'
│     File "test.py", line X, in <module>
│       missing = data["missing_key"]
└──────────────────────────────────────────────
```

---

### Actual Behavior

```
--- Logging error in Loguru Handler #1 ---
Record was: {'elapsed': datetime.timedelta(...), 'exception': (...), ...}
Traceback (most recent call last):
  File "...\loguru\_handler.py", line 232, in emit
    formatted = precomputed_format.format_map(formatter_record)
KeyError: "'name'"
--- End of logging error ---
```

**Note**: The exception **IS** logged successfully to JSON file handlers, only callable format functions fail.

---

### Root Cause Analysis

When a custom format **function** (not string) is passed to `logger.add()`, loguru's handler incorrectly processes it as a format **string** in certain code paths.

#### Call Chain

1. User calls `logger.add(sys.stderr, format=callable_func, ...)`
2. Loguru detects `format` is callable, sets `is_formatter_dynamic=True`
3. On exception logging, handler calls `prepare_colored_format(callable_func, ansi_level)`
4. **BUG**: `prepare_colored_format()` calls `Colorizer.prepare_format(callable_func)`
5. `Colorizer.prepare_format()` expects a **string**, receives a **function**
6. Parses function's `repr()` as a format string → generates malformed tokens
7. Later, `format_map()` fails on malformed tokens like `{'name'}` (with literal quotes)

#### Key Code Locations

**`loguru/_handler.py` (line 13-14)** - Current code:
```python
def prepare_colored_format(format_, ansi_level):
    colored = Colorizer.prepare_format(format_)  # <- BUG: format_ is a FUNCTION!
    return colored, colored.colorize(ansi_level)
```

**`loguru/_colorizer.py` (line 388-390)**:
```python
def prepare_format(string):  # <- Expects string, gets function
    tokens, messages_color_tokens = Colorizer._parse_without_formatting(string)
    return ColoredFormat(tokens, messages_color_tokens)
```

The `Colorizer.prepare_format()` method expects a format **string** but receives a format **function**, causing it to parse the function object's string representation incorrectly.

---

### Why Regular Logging Works But Exceptions Fail

**Regular logging (INFO, WARNING, etc.)** - ✅ Works:
- Custom format function called directly by handler
- Returns pre-formatted string (already processed)
- No colorization parsing needed

**Exception logging** - ❌ Fails:
- Loguru's exception handling uses different code path
- Tries to colorize/process format BEFORE calling function
- Triggers `Colorizer.prepare_format()` on function object
- Parsing function object as string generates malformed tokens

---

### Suggested Solutions

#### Solution 1: Check for Callable in `prepare_colored_format` (Recommended)

Modify `_handler.py` to detect callable formats and handle them differently:

```python
def prepare_colored_format(format_, ansi_level):
    """
    Prepare a format for colorization.

    Handles both format strings and custom format functions (callables).
    """
    # Check if format_ is a callable (custom format function)
    if callable(format_):
        # Return a wrapper that preserves the function behavior
        class CallableFormatWrapper:
            """Wrapper for custom format functions."""
            def __init__(self, func):
                self.func = func
                self.tokens = []
                self.messages_color_tokens = []

            def format_map(self, record):
                """Call the format function directly with the record."""
                return self.func(record)

            def colorize(self, ansi_level):
                """Return self since function handles its own colorization."""
                return self

            def strip(self):
                """Return stripped version (returns self for functions)."""
                return self

        wrapper = CallableFormatWrapper(format_)
        return wrapper, wrapper
    else:
        # Original behavior for format strings
        colored = Colorizer.prepare_format(format_)
        return colored, colored.colorize(ansi_level)
```

Apply same pattern to `prepare_stripped_format()`.

**Status**: Partially implemented in branch `fix/issue-2-callable-format-exception`
- ✅ Works for simple callable functions
- ❌ Still fails for `create_hierarchical_format_function()` (needs investigation)

#### Solution 2: Add Type Guard in `Colorizer.prepare_format`

Add a check in `_colorizer.py`:

```python
@staticmethod
def prepare_format(string):
    # If it's a callable, return a pass-through wrapper
    if callable(string):
        class PassThroughFormat:
            def __init__(self, func):
                self.func = func
                self.tokens = []
                self.messages_color_tokens = []

            def format_map(self, record):
                return self.func(record)

            def colorize(self, ansi_level):
                return self

            def strip(self):
                return self

        return PassThroughFormat(string)

    # Original behavior for strings
    tokens, messages_color_tokens = Colorizer._parse_without_formatting(string)
    return ColoredFormat(tokens, messages_color_tokens)
```

#### Solution 3: Separate Code Path for Callables in Handler

Modify handler's `emit()` method to detect callable formats early:

```python
# In _handler.py emit() method
if callable(self._format):
    # Custom format function - call it directly
    formatted = self._format(record)
else:
    # Standard format string - use existing colorization logic
    # ... existing code ...
```

---

### Current Workaround

Until fixed, use separate handlers for exceptions and regular logs:

```python
from loguru import logger
import sys

# Remove default
logger.remove()

# JSON file handler - works for ALL messages including exceptions ✅
logger.add(
    "app.log",
    format="{message}",
    serialize=True,
    backtrace=True,
    diagnose=True,
)

# Hierarchical console handler - works for regular logs, fails for exceptions
logger.add(
    sys.stderr,
    format=create_hierarchical_format_function(),
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Regular logs work on both handlers ✅
logger.info("Processing file", filename="test.mp3")
logger.warning("Rate limit approaching", requests=850)

# Exceptions work on JSON handler ✅, fail on console handler ❌
try:
    raise ValueError("test error")
except Exception:
    logger.exception("Error occurred")  # Logs to app.log successfully
```

The exception is captured in the JSON log file with full traceback, just not displayed in hierarchical console format.

---

### Investigation Areas

The partial fix (Solution 1) works for simple callables but fails for `create_hierarchical_format_function()`. Investigation needed:

1. **Memoization Interaction**
   - How does `_memoize_dynamic_format` interact with the wrapper?
   - Is LRU cache interfering?
   - Does wrapper need to be cache-aware?

2. **Record vs. Formatter Record**
   - What's the difference between `record` and `formatter_record`?
   - Does `formatter_record` need transformation before passing to function?
   - Is the wrapper receiving the correct data structure?

3. **Hierarchical Formatter Specifics**
   - Why does simple callable work but hierarchical fails?
   - Is `HierarchicalFormatter.format_record()` returning wrong type?
   - Does it need modification to be wrapper-compatible?

4. **Alternative Code Paths**
   - Should we bypass `prepare_colored_format` entirely for callables?
   - Can we detect `is_formatter_dynamic=True` earlier?
   - Is there a cleaner separation point in handler pipeline?

---

### Testing

**Test case provided** in `test_exception_fix.py`:

```python
"""Test that exception logging works with hierarchical formatting"""
import sys
from loguru import logger
from loguru._template_formatters import create_hierarchical_format_function

logger.remove()
console_format_func = create_hierarchical_format_function(
    format_string="{time:HH:mm:ss} | {level} | {name} | {message}",
    template="hierarchical"
)

logger.add(sys.stderr, format=console_format_func, colorize=True,
           level="INFO", backtrace=True, diagnose=True)

logger.info("Testing basic logging")  # ✅ Works

try:
    data = {"name": "test"}
    missing = data["missing_key"]
except KeyError as e:
    logger.exception("Testing exception logging", error=str(e))  # ❌ Fails
```

**Expected**: Exception displayed with hierarchical formatting
**Actual**: `KeyError: "'name'"` in handler

---

### Impact

- **Severity**: High - Breaks exception logging for callable formats
- **Scope**: Affects all custom format functions with exception logging
- **Data Loss**: None - Exceptions logged to JSON file handlers correctly
- **User Experience**: Poor - Console exception output fails, requires workaround

---

### Related Issues

- **Issue #1**: Max string recursion exceeded (✅ RESOLVED)
  - Fixed recursion depth from 2 → 200
  - Made configurable via `LOGURU_FORMAT_RECURSION_DEPTH`
  - Merged to master

---

### Additional Context

- Discovered while implementing hierarchical logging for Samplify Django Web UI project
- Regular log messages (INFO, WARNING, SUCCESS, ERROR) work perfectly with callable formats
- JSON file logging works for all message types including exceptions
- The bug specifically affects console/stream handlers with callable format functions
- Partial fix implemented in branch `fix/issue-2-callable-format-exception` (not yet merged)

---

### Files

**Bug Report**: `bug-report-loguru-verbosity.md` (available in related project)
**Comprehensive Analysis**: `loguru-fork-comprehensive-report.md`
**Test Scripts**:
- `test_exception_fix.py` - Reproduction test
- `test_wrapper_debug.py` - Debug test showing simple callables work

---

### Recommendation

**Suggested approach**:
1. Implement Solution 1 for simple callables (✅ already done)
2. Investigate hierarchical formatter interaction with memoization
3. Add comprehensive test suite for all format types:
   - String formats (baseline)
   - Simple callable functions
   - Complex callable functions (like hierarchical)
   - With/without colorization
   - With/without exceptions
4. Consider architectural separation of callable format pipeline

**Priority**: High - Affects primary feature (hierarchical logging) but has working workaround

---

**Filed by**: Claude Code Agent (via user RoscoeTheDog)
**Date**: 2025-10-05
**Related to**: Samplify Project Story 1.3 - Loguru Configuration
