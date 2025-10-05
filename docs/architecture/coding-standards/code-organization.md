# Code Organization

### File Organization

#### Import Organization
**Pattern**: Alphabetical strictly (tool-enforced)

```python
# ================================================================
# IMPORTS
# ================================================================

# Standard library imports (alphabetical)
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports (alphabetical)
import pandas as pd
import requests
from celery import shared_task
from watchdog.observers import Observer

# Django imports (alphabetical by module)
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponse, JsonResponse

# Local application imports (alphabetical, relative)
from apps.catalog.models import File
from apps.processing.services import FFmpegService
from apps.schemas.models import Schema
from core.utils import parse_json
```

**Within each group**:
1. `import` statements first (alphabetical)
2. `from ... import` statements second (alphabetical by module, then by names)

**Rationale**:
- Deterministic (no ambiguity)
- Tool-friendly (isort, black, IDEs enforce this)
- Merge-friendly (reduces git conflicts)
- Easy to find (know exactly where import should be)
- No mental overhead

#### Constant Definitions
**Pattern**: settings.py for Django config, file-level for others

```python
# my_module.py
"""Module docstring."""

from django.conf import settings
import requests

# ============================================================
# MODULE-LEVEL CONSTANTS (after imports, before code)
# ============================================================
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_ENDPOINT = "https://api.example.com"

class MyClass:
    # Class-level constants
    DEFAULT_STATUS = "pending"
    MAX_FILE_SIZE = 1024 * 1024

    def my_function(self):
        pass
```

**Guidelines**:
- **Django configuration**: Always in `settings.py` or `settings/` module
- **Module-specific constants**: Top of file after imports
- **Class-specific constants**: As class variables
- **Separate constants.py**: Only when 20+ shared constants across modules

**Rationale**: Easy to find and modify, clear what's configurable, follows Python convention.

#### Class Organization
**Standard order (1-7)**:

```python
class FileProcessor:
    # 1. Class variables/constants
    DEFAULT_ENCODING = "utf-8"
    MAX_FILE_SIZE = 1024 * 1024

    # 2. Constructor
    def __init__(self, path: str):
        self.path = path
        self._cache: Dict[str, Any] = {}

    # 3. Properties
    @property
    def file_size(self) -> int:
        return os.path.getsize(self.path)

    @property
    def encoding(self) -> str:
        return self._encoding or self.DEFAULT_ENCODING

    # 4. Class methods
    @classmethod
    def from_url(cls, url: str) -> 'FileProcessor':
        path = download(url)
        return cls(path)

    # 5. Static methods
    @staticmethod
    def validate_path(path: str) -> bool:
        return os.path.exists(path)

    # 6. Public methods
    def process(self) -> dict:
        """Process file and return results."""
        data = self._read_file()
        return self._transform(data)

    def validate(self) -> bool:
        """Validate file format."""
        return self._check_format()

    # 7. Private methods
    def _read_file(self) -> bytes:
        """Read file contents."""
        pass

    def _transform(self, data: bytes) -> dict:
        """Transform raw data."""
        pass

    def _check_format(self) -> bool:
        """Check file format validity."""
        pass
```

**Rationale**: Shows interface first (what's public/accessible), implementation details (private methods) at bottom.

#### Function Organization Within Modules
**Pattern**: Public functions first, private functions last

```python
# ============================================================
# PUBLIC API FUNCTIONS (alphabetically within section)
# ============================================================

def process_file(path: str) -> dict:
    """Process file and return results."""
    data = _read_data(path)
    return _transform_data(data)


def validate_schema(schema: dict) -> bool:
    """Validate schema structure."""
    return _check_structure(schema)


# ============================================================
# PRIVATE HELPER FUNCTIONS (alphabetically within section)
# ============================================================

def _check_structure(schema: dict) -> bool:
    """Check schema structure validity."""
    pass


def _read_data(path: str) -> bytes:
    """Read data from file."""
    pass


def _transform_data(data: bytes) -> dict:
    """Transform raw data to dictionary."""
    pass
```

**Alternative for very large modules** - Group by functionality:

```python
# ============================================================
# FILE PROCESSING FUNCTIONS
# ============================================================

def process_file(path: str) -> dict:
    pass


def _read_file(path: str) -> bytes:
    pass


# ============================================================
# SCHEMA VALIDATION FUNCTIONS
# ============================================================

def validate_schema(schema: dict) -> bool:
    pass


def _validate_structure(schema: dict) -> bool:
    pass
```

**Rationale**: Shows module API immediately, matches class organization (public before private).

#### Maximum File Length
**Pattern**: Split based on responsibility, not line count

**Common thresholds**:
- **Single responsibility rule**: If file does more than one thing, split it
- **Class count**: More than 3-5 classes → consider splitting
- **Lines of code**: 300-500 lines is a review signal (not hard limit)
- **Cognitive load**: If you can't understand file purpose in 30 seconds, it's too complex

**Example of when to split**:

```python
# ❌ TOO MUCH - user_management.py (800 lines)
class UserCreator:
    pass

class UserUpdater:
    pass

class UserDeleter:
    pass

class UserValidator:
    pass

class UserNotifier:
    pass


# ✅ BETTER - Split by responsibility
# users/creators.py
class UserCreator:
    pass

# users/updaters.py
class UserUpdater:
    pass

# users/validators.py
class UserValidator:
    pass
```

**Rule of thumb**: If you're asking "should I split this?", the answer is probably yes.

---

### Code Block Organization

#### Blank Lines Between Sections
**Pattern**: 2 blank lines between major sections, 1 between minor blocks (PEP 8)

```python
import os
import sys


# 2 blank lines after imports


class MyClass:
    pass


# 2 blank lines between top-level classes/functions


class AnotherClass:
    pass


def top_level_function():
    result = calculate()

    # 1 blank line between logical blocks
    if result:
        process(result)

    return result


# 2 blank lines between top-level functions


def another_function():
    pass
```

**Within a class**:

```python
class FileProcessor:
    MAX_SIZE = 1024

    # 1 blank line after class variables

    def __init__(self):
        self.data = []

    # 1 blank line between methods

    def process(self):
        pass

    def validate(self):
        pass
```

**Standard rules**:
- **2 blank lines**: Between top-level functions and classes
- **1 blank line**: Between methods in class, between logical sections in function
- **0 blank lines**: Between tightly related statements

#### Related Statements Grouping
**Pattern**: Declare variables near first use (modern practice)

```python
# ✅ GOOD - Variables near first use
def process_user_data(user_id: int) -> Optional[dict]:
    # Fetch user when needed
    user = get_user(user_id)
    if not user:
        return None

    # Calculate score when needed
    base_score = calculate_base_score(user)
    bonus = get_bonus_points(user)
    final_score = base_score + bonus

    return {"user": user, "score": final_score}


# ❌ AVOID - All declarations at top (old C-style)
def process_user_data(user_id: int) -> Optional[dict]:
    user = None
    base_score = 0
    bonus = 0
    final_score = 0

    user = get_user(user_id)
    if not user:
        return None

    base_score = calculate_base_score(user)
    bonus = get_bonus_points(user)
    final_score = base_score + bonus

    return {"user": user, "score": final_score}
```

**Exception** - Configuration constants can be grouped at top:

```python
def process_file(path: str) -> dict:
    # Configuration constants together
    MAX_SIZE = 1024 * 1024
    ALLOWED_FORMATS = ['.txt', '.csv']
    TIMEOUT = 30

    # Then logic
    if not path.endswith(tuple(ALLOWED_FORMATS)):
        return None
```

**Rationale**: Easier to understand context, reduces cognitive load, supports early returns.

#### Error Handling Placement
**Pattern**: Validate early, handle errors where they occur

```python
def process_file(path: str, options: Optional[dict] = None) -> List[dict]:
    # 1. Input validation at top (guard clauses)
    if not path:
        raise ValueError("Path is required")

    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    # 2. Setup/initialization
    options = options or {}
    results: List[dict] = []

    # 3. Try-except for specific operations that can fail
    try:
        data = read_file(path)
    except IOError as e:
        logger.error(f"Failed to read {path}: {e}")
        raise

    # 4. Business logic with inline error handling
    for item in data:
        try:
            # Handle errors inline where they can occur
            processed = transform(item)
            results.append(processed)
        except ValueError as e:
            # Skip invalid items but continue
            logger.warning(f"Skipping invalid item: {e}")
            continue

    return results
```

**Pattern breakdown**:
1. Input validation first (guard clauses with early returns/raises)
2. Try-except around I/O operations (file, network, database)
3. Inline error handling for recoverable errors in loops
4. Let exceptions bubble for unexpected errors

**Don't wrap everything**:

```python
# ❌ AVOID - Overly broad try-except
def process_file(path: str):
    try:
        # 50 lines of code
        # Hides what can actually fail
        # Makes debugging harder
    except Exception as e:
        logger.error(f"Something went wrong: {e}")
        return None
```

#### Return Statements
**Pattern**: Guard clauses with early returns, then single return

```python
# ✅ GOOD - Guard clauses pattern
def process_user(user_id: int, options: dict) -> Optional[dict]:
    # Guard clauses - early returns for invalid cases
    if not user_id:
        return None

    if not options:
        return None

    user = get_user(user_id)
    if not user:
        return None

    if not user.is_active:
        return None

    # Main logic - single return at end
    result = calculate_score(user, options)
    formatted = format_result(result)
    return formatted


# ✅ Also acceptable for complex branching
def get_status(user: User) -> str:
    if user.is_banned:
        return "banned"

    if user.is_premium:
        return "premium"

    if user.trial_expired():
        return "expired"

    return "active"


# ❌ AVOID - Single-return dogma (forces unnecessary nesting)
def process_user(user_id: int) -> Optional[dict]:
    result = None
    if user_id:
        user = get_user(user_id)
        if user:
            if user.is_active:
                result = calculate_score(user)
    return result
```

**Rationale**: Reduces nesting, fail fast, clearer flow (validation → processing → return).

---
