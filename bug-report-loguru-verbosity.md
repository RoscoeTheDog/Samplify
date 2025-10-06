# Bug Report: KeyError "'verbosity'" in Hierarchical Exception Formatting

## Summary
When using `logger.exception()` with hierarchical formatting enabled, loguru raises `KeyError: "'verbosity'"` when trying to format the exception message. This prevents hierarchical exception output to console, though JSON file logging works correctly.

## Environment
- **Loguru Version**: 0.7.3 (RoscoeTheDog/loguru fork)
- **Python Version**: 3.10+
- **OS**: Windows 11 / Linux
- **Feature**: Hierarchical logging with `create_hierarchical_format_function()`

## Reproduction

### Minimal Example
```python
import sys
from loguru import logger
from loguru._template_formatters import create_hierarchical_format_function

# Remove default handler
logger.remove()

# Add hierarchical console handler
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

# Test exception logging (this fails)
try:
    data = {"name": "test"}
    missing = data["missing_key"]
except KeyError as e:
    logger.exception("Exception test", error=str(e))
```

### Expected Behavior
Should display hierarchical formatted exception with box-drawing characters:
```
┌─ 20:00:00 │ ❌ ERROR │ __main__
├─ Exception test
├─ Context:
│  └─ error: missing_key
├─ Exception:
│  └─ KeyError: 'missing_key'
│     File "test.py", line X, in <module>
│       missing = data["missing_key"]
└──────────────────────────────────────────────
```

### Actual Behavior
```
--- Logging error in Loguru Handler #1 ---
Record was: {...}
Traceback (most recent call last):
  File "...\loguru\_handler.py", line 165, in emit
    formatted = precomputed_format.format_map(formatter_record)
KeyError: "'verbosity'"
--- End of logging error ---
```

Note: Exception **IS** logged successfully to JSON file handler, only hierarchical console output fails.

## Root Cause Analysis

### Issue Location
The error occurs in `loguru/_handler.py` at line 165:
```python
formatted = precomputed_format.format_map(formatter_record)
```

### Root Cause
When a custom format **function** (not string) is passed to `logger.add()`, loguru's handler code path incorrectly attempts to process it as a format **string**:

1. **Handler receives format function** (from `create_hierarchical_format_function()`)
2. **prepare_colored_format()** is called with the function object
3. **Colorizer.prepare_format()** treats the function as a string
4. **_parse_without_formatting()** parses the function's `repr()` or `str()` representation
5. This generates malformed format tokens like `{'verbosity'}` (with literal quotes)
6. Later, `format_map()` fails trying to find a key named `'verbosity'` (with quotes)

### Key Code Paths

**loguru/_handler.py (line 13-14)**:
```python
def prepare_colored_format(format_, ansi_level):
    colored = Colorizer.prepare_format(format_)  # <- format_ is a FUNCTION, not string!
    return colored, colored.colorize(ansi_level)
```

**loguru/_colorizer.py (line 388-390)**:
```python
def prepare_format(string):
    tokens, messages_color_tokens = Colorizer._parse_without_formatting(string)
    return ColoredFormat(tokens, messages_color_tokens)
```

The `Colorizer.prepare_format()` method expects a format **string** but receives a format **function**, causing it to parse the function object's string representation incorrectly.

## Why This Happens with Exceptions Only

Regular logging works because:
- The custom format function is called directly by the handler
- It returns a pre-formatted string (already processed by hierarchical formatter)
- No colorization parsing is needed

Exception logging fails because:
- Loguru's exception handling code path uses a different flow
- It tries to colorize/process the format specification BEFORE calling the function
- This triggers `Colorizer.prepare_format()` on the function object
- Parsing a function object as a format string generates malformed tokens

## Suggested Solutions

### Solution 1: Check for Callable Format in prepare_colored_format (Recommended)
Modify `_handler.py` to detect callable formats and handle them differently:

```python
def prepare_colored_format(format_, ansi_level):
    # Check if format_ is a callable (custom format function)
    if callable(format_):
        # Return a wrapper that preserves the function behavior
        # The function itself handles all formatting and colorization
        class CallableFormat:
            def __init__(self, func):
                self.func = func

            def format_map(self, record):
                # Call the format function directly with the record
                return self.func(record)

            def colorize(self, ansi_level):
                # Return self since function handles its own colorization
                return self

            def strip(self):
                # Return self for consistency
                return self

        wrapper = CallableFormat(format_)
        return wrapper, wrapper
    else:
        # Original behavior for format strings
        colored = Colorizer.prepare_format(format_)
        return colored, colored.colorize(ansi_level)
```

### Solution 2: Add Type Guard in Colorizer.prepare_format
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

            # ... other methods
        return PassThroughFormat(string)

    # Original behavior
    tokens, messages_color_tokens = Colorizer._parse_without_formatting(string)
    return ColoredFormat(tokens, messages_color_tokens)
```

### Solution 3: Separate Code Path for Function Formats in Handler
Modify the handler's emit() method to detect callable formats early and bypass colorization logic entirely:

```python
# In _handler.py emit() method
if callable(self._format):
    # Custom format function - call it directly
    formatted = self._format(record)
else:
    # Standard format string - use existing colorization logic
    # ... existing code ...
```

## Recommendation

**Solution 1 is recommended** because:
- ✅ Minimal changes to existing code
- ✅ Centralizes the fix in one location
- ✅ Preserves backward compatibility
- ✅ Follows separation of concerns (handler decides how to use format)
- ✅ Easy to test and verify

## Workaround

Until fixed, exception logging works correctly in JSON file output:

```python
# Add JSON file handler - exceptions work here
logger.add(
    "app.log",
    format="{message}",
    serialize=True,
    backtrace=True,
    diagnose=True,
)

# Console hierarchical handler - exceptions fail here
logger.add(
    sys.stderr,
    format=create_hierarchical_format_function(),
    colorize=True,
)

# Exception will fail on console but succeed in JSON file
try:
    raise ValueError("test")
except Exception:
    logger.exception("Error occurred")  # Logs to app.log successfully
```

## Impact

- **Severity**: High - Breaks exception logging for hierarchical template
- **Scope**: Affects all custom format functions with exception logging
- **Data Loss**: No - Exceptions are logged to JSON file correctly
- **User Experience**: Poor - Console exception output fails silently

## Additional Notes

- This bug only affects hierarchical template console output
- Regular log messages (INFO, WARNING, SUCCESS, ERROR) work perfectly
- JSON file logging works for all message types including exceptions
- The bug was discovered while implementing Story 1.3 (Loguru Configuration) in the Samplify project
- Related to Issue #1 (recursion depth bug) but separate root cause

---

**Filed by**: Claude Code Agent
**Date**: 2025-10-05
**Related Issues**: #1 (recursion depth)
