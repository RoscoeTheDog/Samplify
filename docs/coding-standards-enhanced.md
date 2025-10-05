# Samplify Coding Standards & Conventions - Enhanced

**Version**: 3.1 (Enhanced Loguru Features)
**Last Updated**: 2025-10-03
**Target Audience**: Solo Developer (Junior to Mid-level, 5+ years experience)

---

## Table of Contents
1. [Philosophy](#philosophy)
2. [Naming Conventions](#naming-conventions)
3. [Code Organization](#code-organization)
4. [Comments & Documentation](#comments--documentation)
5. [Control Flow & Logic](#control-flow--logic)
6. [Error Handling & Validation](#error-handling--validation)
7. [Django-Specific Patterns](#django-specific-patterns)
8. [Testing Conventions](#testing-conventions)
9. [Performance & Optimization](#performance--optimization)
10. [Logging & Debugging](#logging--debugging)
11. [Git & Version Control](#git--version-control)
12. [Custom Preferences](#custom-preferences)
13. [Priorities & Enforcement](#priorities--enforcement)
14. [AI Agent Requirements](#ai-agent-requirements)
15. [Development Tools](#development-tools)
16. [Quick Reference](#quick-reference)

---

## Philosophy

**Core Principle**: Prioritize human readability and maintainability over syntactic brevity.

Code must be:
- **Self-documenting**: Clear variable names, explicit logic flow
- **Extensively commented**: Explain "why" not just "what"
- **Type-safe**: Full type hints for IDE support and static analysis
- **Linted and formatted**: Automated quality enforcement
- **Easy to understand**: Glanceable code that reveals purpose immediately

**Developer Experience Target**: Junior to mid-level developer with CS fundamentals transitioning between unfamiliar codebases.

---

## Naming Conventions (Detailed)

### Variable Naming

#### Boolean Variables
**Pattern**: Use prefix that reads like a natural question

```python
# ✅ State checks - is_ prefix
is_valid = check_validation(data)
is_active = user.status == "active"
is_empty = len(items) == 0

# ✅ Possession/existence - has_ prefix
has_permission = user.check_permission("edit")
has_errors = len(error_list) > 0
has_children = len(node.children) > 0

# ✅ Ability/capability - can_ prefix
can_process = is_valid and has_permission
can_delete = user.is_admin or user.is_owner
can_access = check_access_rights()

# ❌ AVOID - check_ prefix (too vague, doesn't indicate boolean)
check_valid = validate(data)  # Unclear if boolean or function call
```

**Rule**: The prefix should make it read like a natural question: "Is it valid?", "Has permission?", "Can process?"

#### Counter/Index Variables
**Pattern**: Always use descriptive names

```python
# ✅ GOOD - Descriptive names
for file_index in range(len(files)):
    process_file(files[file_index], position=file_index)

worker_count = multiprocessing.cpu_count()
iteration_number = 0

# ❌ AVOID - Single letter variables
for i in range(len(files)):  # What does i represent?
    process_file(files[i], position=i)
```

**Exception**: Single letters acceptable in mathematics/algorithms where conventional (i, j, k for loops in academic contexts).

#### Collection Variables
**Pattern**: Suffix with type for clarity

```python
# ✅ GOOD - Type-suffixed collections
file_list: List[File] = []
transformation_queue: Deque[Transform] = deque()
result_dict: Dict[str, Any] = {}
error_set: Set[str] = set()

# ❌ AVOID - Plural without type (ambiguous)
files = []  # List? Set? Tuple?
transformations = deque()  # Not clear it's a queue
```

**Rationale**: Type suffix makes collection type explicit, especially important when type isn't obvious from context.

#### Temporary Variables
**Pattern**: Use short names in small scopes, make outer scope specific if shadowing

```python
# ✅ GOOD - Short names in small scopes
def process_data(input_data):
    result = transform(input_data)
    output = format_result(result)
    return output

# ✅ GOOD - Contextual prefixes when shadowing
def process_files(file_list):
    total_size = 0
    for file_item in file_list:  # Avoid shadowing "file" builtin
        file_size = file_item.stat().st_size
        total_size += file_size

# ✅ GOOD - Outer scope more specific if inner scope shadows
def batch_process(input_file_list):
    for input_file in input_file_list:
        # Inner scope uses simple "file"
        with open(input_file) as file:
            data = file.read()
```

#### Constants
**Pattern**: SCREAMING_SNAKE_CASE for all constants

```python
# ✅ GOOD - All constants
MAX_WORKERS = 8
DEFAULT_TIMEOUT_SECONDS = 30
API_ENDPOINT = "https://api.example.com"
ALLOWED_EXTENSIONS = [".wav", ".mp3", ".flac"]

# Configuration constants
RETRY_ATTEMPTS = 3
BATCH_SIZE = 100
```

---

### Function Naming

#### Action Functions
**Pattern**: Mixed approach based on action type

```python
# ✅ Verb-Noun for transformations
def validate_input(data):
    pass

def parse_template(xml_string):
    pass

def transform_audio(input_path, output_format):
    pass

# ✅ Strong verbs for processes
def process_files(file_list):
    pass

def execute_query(sql):
    pass

# ✅ Get/Set for simple property access
def get_status():
    return self._status

def set_timeout(seconds):
    self._timeout = seconds
```

#### Query/Lookup Functions
**Pattern**: Context-dependent with clear semantics

```python
# ✅ get_ - Direct access, expected to exist (raises if not found)
def get_user_by_id(user_id: int) -> User:
    """Get user by ID. Raises UserNotFoundError if not found."""
    user = User.objects.get(id=user_id)
    return user

def get_config(key: str) -> str:
    """Get configuration value. Raises KeyError if not found."""
    return settings.CONFIG[key]

# ✅ find_ - Search operation, may not exist (returns None)
def find_user_by_email(email: str) -> Optional[User]:
    """Find user by email. Returns None if not found."""
    return User.objects.filter(email=email).first()

def find_first_match(pattern: str, items: List[str]) -> Optional[str]:
    """Find first item matching pattern. Returns None if no match."""
    for item in items:
        if re.match(pattern, item):
            return item
    return None

# ✅ fetch_ - Remote/database retrieval, implies I/O operation
def fetch_from_api(endpoint: str) -> dict:
    """Fetch data from API endpoint."""
    response = requests.get(endpoint)
    return response.json()

def fetch_from_database(query: str) -> List[dict]:
    """Fetch records from database."""
    return db.execute(query).fetchall()

# ✅ retrieve_ - Less common, formal variant of fetch
def retrieve_archived_data(archive_id: str) -> bytes:
    """Retrieve data from archive storage."""
    pass
```

**Semantic Distinctions**:
- **get_**: Expected to exist, raises exception if not found
- **find_**: Search that may fail, returns None/empty
- **fetch_**: I/O operation (network, database, file)
- **retrieve_**: Formal/archive retrieval operation

#### Boolean-Returning Functions
**Pattern**: Match the question (is/has/can)

```python
# ✅ is_ - State/property check
def is_valid(data: dict) -> bool:
    return all(key in data for key in REQUIRED_KEYS)

def is_active(user: User) -> bool:
    return user.status == "active"

def is_empty(collection: List) -> bool:
    return len(collection) == 0

# ✅ has_ - Possession/existence
def has_permission(user: User, permission: str) -> bool:
    return permission in user.permissions

def has_errors(result: dict) -> bool:
    return "errors" in result and len(result["errors"]) > 0

def has_children(node: TreeNode) -> bool:
    return len(node.children) > 0

# ✅ can_ - Ability/permission
def can_process(file: File) -> bool:
    return file.is_valid and file.has_permissions

def can_delete(user: User, resource: Resource) -> bool:
    return user.is_admin or resource.owner_id == user.id

def can_access(user: User, resource: Resource) -> bool:
    return user.has_role("viewer") or user.has_role("editor")

# ❌ AVOID - check_ prefix (too vague, doesn't indicate boolean return)
def check_valid(data):  # Returns bool? Raises exception? Returns errors?
    pass
```

**Rule**: Prefix should make it read like a natural question.

#### Private/Internal Functions
**Pattern**: Single underscore prefix (Python standard)

```python
# ✅ Private/internal functions
def _internal_helper():
    """Private helper function."""
    pass

def _calculate_hash(data: bytes) -> str:
    """Internal hash calculation."""
    pass

# ✅ Name mangling for very private (rare, special cases)
def __very_private():
    """Name-mangled private method."""
    pass

# ✅ Public API
def public_function():
    """Public interface function."""
    result = _internal_helper()
    return result
```

**Rationale**:
- PEP 8 language convention
- IDE/tooling support
- Import behavior (`from module import *` excludes `_` prefixed)
- Clear visual indicator

#### Helper/Utility Functions
**Pattern**: Good descriptive names, no special prefix

```python
# ✅ GOOD - Descriptive names, private if internal
def process_batch():
    data = _parse_xml(xml_string)  # Private helper
    return _transform_data(data)   # Private helper

def _parse_xml(xml_string: str) -> dict:
    """Parse XML string to dictionary."""
    pass

def _transform_data(data: dict) -> list:
    """Transform data structure."""
    pass

# ✅ GOOD - Utils module organization
from utils.xml import parse_xml  # Module organization, not naming
from utils.validation import validate_schema

# ❌ AVOID - Redundant prefixes
def _helper_parse_xml():  # "helper" adds no information
    pass

def util_parse_xml():  # "util" prefix is noise
    pass
```

**Better organization**:
- Make them private with `_` if internal to module
- Group in dedicated modules (`utils/`, `helpers/`) by functionality
- Use clear descriptive names that explain what they do

---

### Class and Module Naming

#### Class Names
**Pattern**: PascalCase, no type suffixes (except design patterns)

```python
# ✅ GOOD - Clean PascalCase
class FileProcessor:
    pass

class SchemaManager:
    pass

class UserRepository:
    pass

class AudioConverter:
    pass

# ❌ AVOID - Redundant type suffixes
class FileProcessorService:  # "Service" is redundant
    pass

class SchemaManagerHandler:  # "Handler" is redundant
    pass

class UserRepositoryClass:  # "Class" is redundant
    pass

# ✅ EXCEPTION - Design pattern names add clarity
class UserFactory:  # Factory pattern
    pass

class CommandBuilder:  # Builder pattern
    pass

class ObserverAdapter:  # Adapter pattern
    pass
```

**Rationale**: Code structure already shows it's a class, avoid redundancy.

#### Module Names
**Pattern**: Context-dependent (primarily snake_case singular)

```python
# ✅ Singular when module contains one main class/concept
file_processor.py      # Contains FileProcessor class
schema_manager.py      # Contains SchemaManager class
audio_converter.py     # Contains AudioConverter class

# ✅ Plural when module contains collections/utilities
utils.py              # Various utility functions
constants.py          # Multiple constants
exceptions.py         # Multiple exception classes
models.py             # Multiple model classes
handlers.py           # Multiple handler classes
```

**Standard Python convention (PEP 8)**:
- Always `snake_case` (never PascalCase for modules)
- Short, all-lowercase
- Singular for single-purpose modules
- Plural for collections

#### Django App Names
**Pattern**: Plural nouns (Django community standard)

```python
# ✅ GOOD - Plural (matches Django's own apps)
apps/
├── users/           # Not user/
├── schemas/         # Not schema/
├── files/           # Not file/
├── payments/        # Not payment/
└── notifications/   # Not notification/

# ✅ EXCEPTION - Singular for services/features
apps/
├── authentication/  # A service, not a collection
├── billing/         # A service
├── search/          # A feature/service
```

**Rationale**:
- Matches Django's own apps (admin, auth, contenttypes, sessions)
- Apps typically handle multiple instances
- Reads naturally: "the users app", "the payments app"
- Overwhelming community convention

---

## Code Organization

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

## Comments & Documentation

### Comment Density and Style

#### TODO Comments
**Format**: `# TODO(author): Description` with owner

```python
# ✅ GOOD - Include owner for accountability
# TODO(jsmith): Add error handling for network timeouts
# TODO(alee): Optimize this query - currently O(n²)
# TODO(bob): Remove this after migration to v2 API

# Easy to search
# git grep "TODO(jsmith)"
```

**Rationale**: Clear accountability, searchable, standard in Google/major projects.

**Avoid dates inline** - they become stale. Use issue trackers for time-tracking.

#### FIXME/HACK Comments
**Pattern**: Prefer issue tracker, minimal inline comments

```python
# ✅ For production code - create tickets, minimal inline markers
# FIXME: Memory leak in batch processing - see issue #1234
# HACK: Workaround for Django bug #32123 - remove after Django 5.0

# ✅ Better - Use issue tracker and link
# See issue #1234 for memory leak details

# ✅ Inline OK for temporary workarounds
# HACK: API returns invalid JSON on empty results
# Workaround until v2 API is deployed
if response == "":
    response = "[]"
```

**Standard tags**:
- **FIXME**: Known bugs that need fixing
- **HACK**: Workarounds for external issues (library bugs, API limitations)
- **XXX**: Less common, some teams use for warnings

**Rationale**: TODOs/FIXMEs proliferate and become noise, no tracking/visibility, get outdated.

**Keep it minimal** - if explanation is >2 lines, create a ticket and link it.

#### Algorithm Complexity Comments
**Pattern**: Only for complex algorithms (O(n²) or worse)

```python
# ✅ Include for non-obvious complexity
def find_duplicates(items: List[str]) -> List[str]:
    """Find duplicate items in list.

    Note: O(n²) complexity - consider optimization for large lists.
    """
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items[i+1:]):
            if item == other:
                duplicates.append(item)
    return duplicates


# ✅ Include for optimized solutions
def find_duplicates_fast(items: List[str]) -> List[str]:
    """Find duplicate items using set lookup.

    Complexity: O(n) time, O(n) space
    """
    seen = set()
    duplicates = []
    for item in items:
        if item in seen:
            duplicates.append(item)
        seen.add(item)
    return duplicates


# ❌ Don't include for obvious cases
def sum_list(numbers: List[int]) -> int:
    """Sum all numbers in list."""
    # No need to say "O(n)" - it's obvious
    return sum(numbers)
```

**When to include**:
- Non-obvious complexity (quadratic, exponential)
- Performance-critical code
- Explicit trade-offs (space vs time)
- Counterintuitive complexity

**Where to put it**:
- Docstring for overall function complexity
- Inline comment for specific section if needed

#### Magic Number Explanations
**Pattern**: Named constant with comment explaining origin

```python
# ✅ GOOD - Named constant with context
# Based on RFC 2616 - standard HTTP timeout recommendation
HTTP_TIMEOUT_SECONDS = 30

# Determined from production metrics (95th percentile response time)
API_TIMEOUT_SECONDS = 45

# Maximum file size for free tier (product requirement)
MAX_FILE_SIZE_MB = 10


def fetch_data(url: str) -> dict:
    response = requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)
    return response.json()


# ✅ Explains WHY the value
RETRY_ATTEMPTS = 3  # Balances reliability vs latency - tested in prod

# ❌ Redundant comment
RETRY_ATTEMPTS = 3  # Number of retry attempts (obvious!)

# ✅ Self-documenting, no comment needed
MAX_LOGIN_ATTEMPTS = 3
```

**Comment should explain**:
- Origin (where the number comes from)
- Rationale (why this specific value)
- Constraints (business rules, external requirements)
- Trade-offs (why not higher/lower)

#### Commented-Out Code
**Pattern**: Never commit commented-out code

```python
# ❌ NEVER DO THIS
def process_data(data: dict) -> dict:
    # Old implementation - keeping just in case
    # result = old_process(data)
    # if result:
    #     return transform(result)

    # New implementation
    return new_process(data)


# ✅ DO THIS - Just delete it
def process_data(data: dict) -> dict:
    return new_process(data)

# If you need the old code: git log, git blame, git show
```

**Why never commit commented code**:
- Creates confusion ("should I uncomment this?")
- Makes code harder to read
- Git history exists for this purpose
- Rots quickly (becomes outdated)
- False sense of safety (usually never used again)

**Extremely rare exception** - Educational context:

```python
# ✅ Acceptable: Showing what NOT to do
def secure_query(user_id: int) -> dict:
    # DON'T DO THIS - security vulnerability
    # query = f"SELECT * FROM users WHERE id = {user_id}"

    # DO THIS - use parameterized queries
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,)).fetchone()
```

---

### Docstring Standards

#### Type Hints in Docstrings
**Pattern**: No duplication - types in signature, descriptions in docstring

```python
# ✅ GOOD - Type hints in signature, descriptions in docstring
def process_file(path: str, max_size: int = 1024) -> Dict[str, Any]:
    """Process a file and return parsed data.

    Args:
        path: Path to the file to process
        max_size: Maximum file size in bytes

    Returns:
        Dictionary containing parsed file data with 'content' and 'metadata' keys
    """
    pass


# ❌ REDUNDANT - Don't duplicate types
def process_file(path: str, max_size: int = 1024) -> Dict[str, Any]:
    """Process a file and return parsed data.

    Args:
        path (str): Path to the file to process  # Redundant!
        max_size (int): Maximum file size in bytes  # Redundant!

    Returns:
        dict[str, Any]: Dictionary containing...  # Redundant!
    """
    pass
```

**Exception** - Complex types that need explanation:

```python
# ✅ OK - Explanation adds value
def transform_data(
    data: Dict[str, List[Tuple[int, str]]]
) -> List[ProcessedItem]:
    """Transform nested data structure.

    Args:
        data: Mapping of category names to lists of (id, value) tuples.
              Example: {"users": [(1, "alice"), (2, "bob")]}

    Returns:
        List of ProcessedItem objects, one per tuple in input
    """
    pass
```

**Rationale**: DRY principle, type hints are tool-checked, docstrings get out of sync.

#### Default Values in Docstrings
**Pattern**: Include only when default behavior is complex

```python
# ✅ No need to mention simple defaults
def fetch_data(url: str, timeout: int = 30) -> dict:
    """Fetch data from URL.

    Args:
        url: URL to fetch from
        timeout: Request timeout in seconds
    """
    pass


# ✅ Explain complex/non-obvious defaults
def process_batch(
    items: List,
    batch_size: Optional[int] = None,
    retry_failed: bool = True
) -> List:
    """Process items in batches.

    Args:
        items: Items to process
        batch_size: Items per batch. Defaults to CPU count * 2 if not specified
        retry_failed: Whether to retry failed items. Defaults to True for
                     production; automatically set to False in test environments
    """
    pass


# ✅ Explain when None has special meaning
def save_file(path: str, data: bytes, mode: Optional[str] = None) -> None:
    """Save data to file.

    Args:
        path: Destination path
        data: Data to write
        mode: File mode. If None (default), automatically determined from
              file extension ('.gz' uses gzip compression, etc.)
    """
    pass
```

**When to include defaults**:
- Default value has special meaning beyond the literal value
- Default behavior is computed/dynamic
- Understanding the default is important for correct usage

#### Side Effects Documentation
**Pattern**: Only if side effects are non-obvious

```python
# ✅ Document non-obvious side effects
def update_user(user_id: int, data: dict) -> User:
    """Update user information.

    Args:
        user_id: ID of user to update
        data: Fields to update

    Returns:
        Updated user object

    Note:
        Sends email notification to user and logs audit trail to database.
        Invalidates all active sessions for this user.
    """
    pass


# ❌ Don't document obvious side effects
def save_to_database(obj: Model) -> None:
    """Save object to database.

    Side effects:  # REDUNDANT - obvious from function name!
        Writes to database
    """
    pass


# ✅ Good - side effects are clear from description
def delete_user(user_id: int) -> None:
    """Delete user and all associated data.

    Permanently removes user account, posts, comments, and uploaded files.
    This operation cannot be undone.

    Warning:
        This cascades to related records. Use with caution.
    """
    pass
```

**Document side effects when**:
- External systems affected (emails, APIs, queues)
- Database modifications beyond the obvious
- File system changes
- Global state mutations
- Cache invalidations
- Async operations triggered

**Use appropriate sections**:
- **Note**: for important side effects
- **Warning**: for dangerous side effects
- Main description if side effects are the primary purpose

#### Performance Characteristics
**Pattern**: In "Note:" section when relevant

```python
# ✅ Include for performance-critical or non-obvious complexity
def find_shortest_path(graph: Graph, start: Node, end: Node) -> List[Node]:
    """Find shortest path between nodes using Dijkstra's algorithm.

    Args:
        graph: Graph to search
        start: Starting node
        end: Destination node

    Returns:
        List of nodes representing shortest path

    Note:
        Time complexity: O(E + V log V) where E is edges, V is vertices.
        Space complexity: O(V) for priority queue.
        For graphs with >10k nodes, consider using A* algorithm instead.
    """
    pass


# ❌ Don't include for obvious operations
def get_user_by_id(user_id: int) -> User:
    """Retrieve user by ID.

    Note:
        O(1) lookup using primary key  # OBVIOUS - don't include
    """
    pass


# ✅ Include performance warnings
def calculate_similarity(items: List[str]) -> dict:
    """Calculate pairwise similarity between all items.

    Warning:
        O(n²) complexity. Not suitable for >1000 items.
        Use approximate_similarity() for large datasets.
    """
    pass
```

**When to document performance**:
- Non-obvious complexity (O(n²) or worse)
- Performance-critical code paths
- Operations that don't scale well
- When there's a better alternative for large inputs
- Memory usage concerns

**Where to put it**:
- **Note**: for informational complexity
- **Warning**: for performance pitfalls
- Docstring description if performance is key characteristic

#### Related Functions/Classes Cross-Reference
**Pattern**: In description only when directly related

```python
# ✅ Natural mentions in description
def encode_message(message: str, key: str) -> bytes:
    """Encode message with encryption key.

    Use decode_message() to reverse this operation.
    For bulk operations, see encode_messages_batch().
    """
    pass


# ✅ See Also for genuine alternatives/related functionality
def quicksort(items: List) -> List:
    """Sort items using quicksort algorithm.

    Args:
        items: List to sort

    Returns:
        Sorted list

    See Also:
        mergesort: More stable but slower for small lists
        heapsort: Better worst-case complexity O(n log n)
        timsort: Python's built-in sort (usually fastest)
    """
    pass


# ❌ Don't over-document relationships
def save_user(user: User) -> None:
    """Save user to database.

    See Also:  # TOO MUCH - becomes noise
        get_user: Retrieve user
        delete_user: Delete user
        update_user: Update user
        User: User model class
        UserSerializer: User serialization
    """
    pass


# ✅ Minimal - only when helpful
def calculate_tax(amount: Decimal, rate: Decimal) -> Decimal:
    """Calculate tax on amount.

    For tax-inclusive calculations, use calculate_tax_inclusive() instead.
    """
    pass
```

**When to cross-reference**:
- Direct alternatives (different algorithms for same task)
- Inverse operations (encode/decode, serialize/deserialize)
- Related operations users might need next
- Common confusions ("use X instead of Y for Z")

**When NOT to cross-reference**:
- Standard CRUD operations on same model (too obvious)
- Every function that touches same data
- Parent/child class relationships (use inheritance docs)
- Anything the IDE "find usages" shows easily

---

## Control Flow & Logic

### Conditional Logic

#### Complex Boolean Expressions
**Pattern**: Multi-line with parentheses (Black/PEP 8 standard)

```python
# ✅ BEST - Multi-line with parentheses
if (
    user.is_active
    and user.has_permission('edit')
    and not user.is_locked
):
    process_edit()

# ✅ Also good for longer expressions
if (
    user.is_active
    and user.has_permission('edit')
    and not user.is_locked
    and user.email_verified
    and user.account_age_days > 30
):
    grant_advanced_access()

# ❌ AVOID - Inline (hard to read when long)
if (user.is_active and user.has_permission('edit') and not user.is_locked):
    pass

# ❌ AVOID - Backslash (fragile, easy to break)
if user.is_active and \
   user.has_permission('edit') and \
   not user.is_locked:
    pass
```

**When to use intermediate variables** - For complex/reusable logic:

```python
# ✅ Use variables for reusable logic
can_edit = (
    user.is_active
    and user.has_permission('edit')
    and not user.is_locked
)
can_delete = (
    user.is_active
    and user.has_permission('delete')
    and not user.is_locked
)

if can_edit:
    edit_item()

if can_delete:
    delete_item()

# ✅ When condition needs explanation
# User can proceed if they're active and verified, or if they're an admin
can_proceed = (
    (user.is_active and user.is_verified)
    or user.is_admin
)
if can_proceed:
    grant_access()
```

**Benefits**:
- No backslashes needed (cleaner)
- Easy to add/remove conditions
- Git diffs are cleaner (one condition per line)
- Each condition stands out clearly
- Black/autopep8 formats this way automatically

#### Guard Clauses vs Nested Ifs
**Pattern**: Guard clauses (early returns) - overwhelming preference

```python
# ✅ BEST - Guard clauses
def process_file(file_path: Path) -> Optional[dict]:
    if not file_path.exists():
        return None

    if not is_valid_format(file_path):
        return None

    if file_path.stat().st_size > MAX_SIZE:
        return None

    # Main logic is not nested - easy to read
    data = read_file(file_path)
    result = transform(data)
    return result


# ❌ AVOID - Arrow anti-pattern (nested ifs)
def process_file(file_path: Path) -> Optional[dict]:
    if file_path.exists():
        if is_valid_format(file_path):
            if file_path.stat().st_size <= MAX_SIZE:
                # Main logic buried 3 levels deep
                data = read_file(file_path)
                result = transform(data)
                return result
    return None
```

**Standard pattern**:

```python
def process_request(request: Request) -> dict:
    # All validation/guard clauses first
    if not request:
        raise ValueError("Request required")

    if not request.user:
        raise AuthenticationError("User not authenticated")

    if not request.user.has_permission('access'):
        raise PermissionError("Access denied")

    # Main logic - completely unnested
    data = fetch_data(request)
    result = process_data(data)
    return result
```

**Benefits**:
- Reduces nesting (main logic at top level)
- Fail fast (invalid cases exit immediately)
- Easier to read (validation separate from logic)
- Easier to modify (add/remove guards without restructuring)
- Clearer intent ("these are prerequisites")

#### Ternary Operators
**Pattern**: OK when it improves readability

```python
# ✅ GOOD - Simple, clear assignments
status = "active" if user.is_active else "inactive"
color = "green" if score > 80 else "red"
value = x if x is not None else default

# ✅ GOOD - Simple return values
def get_label(count: int) -> str:
    return "item" if count == 1 else "items"

# ✅ GOOD - Short conditional argument
logger.log(message, level="DEBUG" if settings.DEBUG else "INFO")


# ❌ AVOID - Nested ternaries (confusing)
value = "high" if x > 100 else "medium" if x > 50 else "low"  # Hard to read

# ✅ BETTER - Explicit if/elif/else
if x > 100:
    value = "high"
elif x > 50:
    value = "medium"
else:
    value = "low"


# ❌ AVOID - Complex expressions
result = (
    process_data(x) if validate(x) and check_permission() else fallback_process(x)
)  # Too complex

# ✅ BETTER - Explicit if/else
if validate(x) and check_permission():
    result = process_data(x)
else:
    result = fallback_process(x)
```

**Guidelines**:
- **Use ternary for**: Simple variable assignment or return values
- **Must fit comfortably on one line** (< 79 characters)
- **Avoid**: Nested ternaries, complex expressions, side effects
- **Ask**: "Is this easier to read than if/else?" If no, use if/else

#### Short-Circuit Evaluation
**Pattern**: Rely on it (it's a feature, not a bug)

```python
# ✅ GOOD - Idiomatic Python (short-circuit)
if user and user.is_active:
    process(user)

if items and len(items) > 0:
    process_items(items)

if config.get('enabled') and config['timeout'] > 0:
    start_service()


# ❌ VERBOSE - Unnecessarily explicit
if user is not None:
    if user.is_active:
        process(user)

# ❌ VERBOSE
if items is not None:
    if len(items) > 0:
        process_items(items)
```

**More examples**:

```python
# ✅ Common patterns
value = user.name if user else "Anonymous"
result = cache.get(key) or compute_expensive_value()
output = data or []  # Ensure list even if None

# ✅ Safe attribute access
email = user and user.email  # None if user is None, else user.email

# ✅ Validation chains
if request and request.user and request.user.is_authenticated:
    grant_access()
```

**Why rely on short-circuit**:
- **Idiomatic Python** - expected by Python developers
- **Concise and readable** - less nesting
- **Prevents errors** - `user and user.is_active` won't raise AttributeError
- **Well-defined behavior** - Python guarantees left-to-right evaluation
- **Standard in all modern languages** (JavaScript, Java, Go, Rust, etc.)

**When to be explicit**:

```python
# ✅ When None is a valid value distinct from False
if value is not None:  # Not just "if value"
    process(value)  # 0, False, "" are valid

# ✅ When checking type explicitly
if isinstance(data, list):
    process_list(data)
```

---

### Loop and Iteration

#### For Loops vs Comprehensions
**Pattern**: Comprehensions for simple transforms, loops for complex logic

```python
# ✅ GOOD - Comprehensions for simple transforms
squares = [x**2 for x in numbers]
active_users = [u for u in users if u.is_active]
names = [user.name.upper() for user in users]

# ✅ GOOD - Loops for complex logic
results = []
for user in users:
    # Multiple statements, complex logic
    if not user.is_active:
        continue

    profile = fetch_profile(user.id)
    if profile and profile.is_verified:
        result = process_user(user, profile)
        results.append(result)
        logger.info(f"Processed {user.name}")

# ❌ AVOID - Complex comprehension (hard to read)
results = [
    process_user(user, profile)
    for user in users
    if user.is_active
    for profile in [fetch_profile(user.id)]
    if profile and profile.is_verified
]  # Too complex!

# ✅ GOOD - Dict/set comprehensions for simple transforms
user_map = {user.id: user.name for user in users}
unique_emails = {user.email.lower() for user in users}
```

**Rule of thumb**:
- **Use comprehension if**: Single expression, fits comfortably on 1-3 lines
- **Use loop if**: Multiple statements, complex conditions, side effects (logging, I/O)
- **If unsure**: Use a loop (easier to debug and modify later)

#### Nested Comprehensions
**Pattern**: Max 2 levels, only if clear and simple

```python
# ✅ OK - Simple 2-level nesting, clear intent
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [x for row in matrix for x in row]
# Result: [1, 2, 3, 4, 5, 6, 7, 8, 9]

doubled = [[x * 2 for x in row] for row in matrix]
# Result: [[2, 4, 6], [8, 10, 12], [14, 16, 18]]


# ✅ OK - 2D transformation that's easy to understand
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]


# ❌ AVOID - Too complex (3+ levels or complex conditions)
result = [
    [
        [z * 2 for z in y if z > 0]
        for y in x if len(y) > 2
    ]
    for x in data if x
]  # What does this even do?

# ✅ BETTER - Explicit loops
result = []
for x in data:
    if not x:
        continue
    x_result = []
    for y in x:
        if len(y) <= 2:
            continue
        y_result = [z * 2 for z in y if z > 0]
        x_result.append(y_result)
    result.append(x_result)
```

**Guidelines**:
- **Max 2 levels** of nesting in comprehensions
- **Must be immediately clear** what it's doing
- **No complex filters** in nested comprehensions
- **When in doubt, use explicit loops**

**Common acceptable patterns**:

```python
# ✅ Flatten 2D list
flat = [item for sublist in nested_list for item in sublist]

# ✅ Cartesian product
pairs = [(x, y) for x in list1 for y in list2]

# ✅ 2D transformation
processed = [[func(x) for x in row] for row in matrix]
```

#### Generator Expressions vs List Comprehensions
**Pattern**: Lists for small/reusable, generators for large/single-pass

```python
# ✅ List comprehension - Small, need multiple passes
user_ids = [u.id for u in users]  # ~100s of users
if user_ids:
    print(f"Found {len(user_ids)} users")  # Need length
    process_batch(user_ids)  # Use multiple times

# ✅ Generator - Large data or single pass
# Reading large file
lines = (line.strip() for line in open('huge_file.txt'))
for line in lines:
    process(line)  # Use once, don't load all into memory

# ✅ Generator - Potentially infinite
fibonacci = (fib(n) for n in itertools.count())

# ✅ Generator - Chain of transformations
numbers = (int(x) for x in file)
squares = (x**2 for x in numbers)
evens = (x for x in squares if x % 2 == 0)
result = sum(evens)  # Memory efficient pipeline


# ✅ List - Need to use multiple times or check length
results = [expensive_operation(x) for x in items]
print(f"Got {len(results)} results")  # Need length
for r in results:
    process(r)
for r in results:  # Reuse
    validate(r)

# ❌ WASTEFUL - List when only used once
total = sum([x**2 for x in range(1000000)])  # Creates huge list!

# ✅ BETTER - Generator
total = sum(x**2 for x in range(1000000))  # Memory efficient
```

**Decision tree**:
1. **Multiple passes or need `len()`?** → List comprehension
2. **Large data (>10k items)?** → Generator
3. **Single iteration?** → Generator
4. **Small data (<100 items)?** → List is fine (negligible difference)
5. **Passed to function expecting iterable?** → Check if function consumes once (generator) or multiple times (list)

**Note**: `sum()`, `max()`, `min()`, `any()`, `all()` work with generators - use them!

#### enumerate() vs Manual Counter
**Pattern**: Always use enumerate()

```python
# ✅ ALWAYS USE enumerate()
for index, item in enumerate(items):
    print(f"{index}: {item}")

# Start at 1 instead of 0
for number, item in enumerate(items, start=1):
    print(f"{number}. {item}")

# With both index and value
for i, user in enumerate(users):
    if i == 0:
        print(f"First user: {user.name}")
    process(user, position=i)


# ❌ NEVER DO THIS - Manual counter (error-prone, not Pythonic)
index = 0
for item in items:
    print(f"{index}: {item}")
    index += 1  # Easy to forget, can cause bugs


# ❌ ALSO AVOID - Range indexing when you need the value
for i in range(len(items)):
    print(f"{i}: {items[i]}")  # Unnecessary indexing

# ✅ BETTER
for i, item in enumerate(items):
    print(f"{i}: {item}")
```

**Why enumerate() is better**:
- **More Pythonic** - idiomatic Python
- **Less error-prone** - no forgetting to increment
- **More readable** - clear intent
- **Works with any iterable** - not just lists
- **Can't forget to increment** - eliminates whole class of bugs

#### Loop Else Clause
**Pattern**: Avoid; if used, require clear comment

```python
# ✅ ACCEPTABLE - With clear comment explaining else
for item in items:
    if item.matches(criteria):
        result = item
        break
else:
    # No break occurred - no matching item found
    result = None

# ✅ BETTER - More explicit (preferred by most teams)
result = None
for item in items:
    if item.matches(criteria):
        result = item
        break

if result is None:
    handle_no_match()


# ✅ BEST - Use built-in function when available
result = next((item for item in items if item.matches(criteria)), None)
if result is None:
    handle_no_match()
```

**Why it's controversial**:
- **Confusing**: "else" implies "if didn't execute", but it means "if didn't break"
- **Non-obvious**: Most developers don't expect it
- **Rare**: Not commonly used in production code
- **Alternatives are clearer**: Setting flag or using early return

**Community opinion**: Most Python style guides **discourage loop-else** or require comments.

---

## Error Handling & Validation

### Exception Handling Patterns

#### Exception Granularity
**Pattern**: Catch broad exceptions at top level, specific in functions

```python
# ✅ GOOD - Specific exceptions in business logic
def process_audio_file(path: str) -> AudioData:
    try:
        data = read_file(path)
    except FileNotFoundError:
        raise AudioFileError(f"Audio file not found: {path}")
    except PermissionError:
        raise AudioFileError(f"Cannot read file (permission denied): {path}")

    try:
        return parse_audio(data)
    except ValueError as e:
        raise AudioFormatError(f"Invalid audio format: {e}")


# ✅ GOOD - Broad exception at application boundary
def main():
    try:
        result = process_audio_file(args.input)
        save_result(result)
    except AudioFileError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        sys.exit(2)
```

#### Exception Chaining
**Pattern**: Only when adding context to exception

```python
# ✅ GOOD - Chain when adding domain context
def load_user_config(user_id: int) -> dict:
    try:
        data = fetch_from_database(user_id)
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ConfigurationError(
            f"Invalid configuration for user {user_id}"
        ) from e


# ✅ GOOD - Just re-raise when not adding context
def validate_data(data):
    try:
        check_format(data)
    except ValueError:
        raise  # Just re-raise, don't chain
```

#### Custom Exceptions
**Pattern**: Create exception hierarchy for domain

```python
# ✅ GOOD - Domain exception hierarchy
class SamplifyError(Exception):
    """Base exception for all Samplify errors."""
    pass


class AudioError(SamplifyError):
    """Audio processing errors."""
    pass


class AudioFileError(AudioError):
    """Audio file I/O errors."""
    pass


class SchemaError(SamplifyError):
    """Schema-related errors."""
    pass
```

#### Exception Messages
**Pattern**: Detailed with context

```python
# ✅ GOOD - Context + actual values + valid range
raise ValueError(
    f"Invalid sample rate: {sample_rate}. "
    f"Expected range: 8000-192000 Hz. "
    f"File: {file_path}"
)
```

#### Logging vs Raising
**Pattern**: Log only if handling exception, raise if propagating

```python
# ✅ GOOD - Log when handling (not re-raising)
def process_file(path):
    try:
        return parse_audio(path)
    except AudioFormatError as e:
        logger.warning(f"Skipping invalid file {path}: {e}")
        return None  # Handled


# ✅ GOOD - Don't log when propagating
def validate_schema(data):
    try:
        return parse_schema(data)
    except ValueError as e:
        raise SchemaValidationError(f"Invalid schema: {e}") from e
        # Let caller decide whether to log
```

---

### Input Validation

#### Validation Timing
**Pattern**: At function entry (fail fast)

```python
# ✅ GOOD - Validate at entry
def process_audio(file_path: str, sample_rate: int) -> AudioData:
    # Validate ALL inputs at the top
    if not file_path:
        raise ValueError("file_path is required")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not 8000 <= sample_rate <= 192000:
        raise ValueError(
            f"Invalid sample rate: {sample_rate}. Expected: 8000-192000 Hz"
        )

    # Now safe to proceed
    data = load_file(file_path)
    return resample(data, sample_rate)
```

#### Type Checking
**Pattern**: Type hints + mypy for development, isinstance() for runtime safety

```python
# ✅ GOOD - Type hints for static analysis
def create_schema(name: str, fields: list[dict[str, Any]]) -> Schema:
    # Runtime validation for critical types
    if not isinstance(name, str):
        raise TypeError(f"name must be str, got {type(name).__name__}")

    if not isinstance(fields, list):
        raise TypeError(f"fields must be list, got {type(fields).__name__}")

    # Business logic validation
    if not name.strip():
        raise ValueError("name cannot be empty")
```

#### Validation Helper Functions
**Pattern**: Raise for business logic, return bool for conditional checks

```python
# ✅ Pattern 1: Raise exceptions (business logic)
def validate_sample_rate(rate: int) -> None:
    """Validate sample rate or raise exception."""
    if not 8000 <= rate <= 192000:
        raise ValueError(f"Invalid sample rate: {rate}")


# ✅ Pattern 2: Return boolean (conditional logic)
def is_valid_sample_rate(rate: int) -> bool:
    """Check if sample rate is valid."""
    return isinstance(rate, int) and 8000 <= rate <= 192000
```

#### Assertion Statements
**Pattern**: Use for internal invariants only (never for user input)

```python
# ✅ GOOD - Assert for developer errors
def _internal_helper(data: list) -> None:
    """Internal function - caller must ensure data is not empty."""
    assert len(data) > 0, "Internal error: data should not be empty"
    process(data[0])


# ❌ NEVER - Assert for user input
def process_user_input(data: dict) -> None:
    assert 'name' in data  # Can be disabled with python -O!
    # Use explicit validation instead
```

---

## Django-Specific Patterns

### Model Preferences

#### Model Method Organization
**Standard Django order (1-6)**:

```python
class Schema(models.Model):
    # 1. Field definitions
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # 2. Meta class
    class Meta:
        ordering = ['-created_at']

    # 3. __str__() method
    def __str__(self):
        return self.name

    # 4. Class methods and managers
    @classmethod
    def create_default(cls, owner):
        return cls.objects.create(name=f"{owner.username}'s Schema", owner=owner)

    # 5. Properties
    @property
    def rule_count(self):
        return self.rules.count()

    # 6. Instance methods
    def activate(self):
        self.is_active = True
        self.save(update_fields=['is_active'])
```

#### Model Validation
**Pattern**: Mix all three - field validators, clean(), save()

```python
class Schema(models.Model):
    # Field-level validators (simple, reusable)
    name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3)]
    )

    # Model-level validation (cross-field, complex logic)
    def clean(self):
        super().clean()
        if self.is_active and not self.owner.is_active:
            raise ValidationError('Cannot activate schema when owner is inactive')

    # Override save for auto-computation (not validation)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not kwargs.pop('skip_validation', False):
            self.full_clean()
        super().save(*args, **kwargs)
```

#### QuerySet Methods
**Pattern**: QuerySet with as_manager() for chainable methods

```python
class SchemaQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def for_user(self, user):
        return self.filter(owner=user)


class Schema(models.Model):
    objects = SchemaQuerySet.as_manager()


# Usage - methods are chainable
Schema.objects.active().for_user(request.user)
```

#### Related Name Conventions
**Pattern**: Plural of source model (add prefix for collisions)

```python
# ✅ Standard - Plural
class Rule(models.Model):
    schema = models.ForeignKey(Schema, related_name='rules')


# Usage
schema.rules.all()


# ✅ Prefix when multiple relations to same model
class Article(models.Model):
    author = models.ForeignKey(User, related_name='authored_articles')
    editor = models.ForeignKey(User, related_name='edited_articles')
```

---

### View Preferences

#### View Organization
**Pattern**: CBV for CRUD, FBV for custom logic

```python
# ✅ CBV for standard CRUD
class SchemaListView(ListView):
    model = Schema

    def get_queryset(self):
        return Schema.objects.filter(owner=self.request.user).active()


# ✅ FBV for custom/complex business logic
@login_required
def process_audio_upload(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # Complex multi-step logic
    # ...
```

#### View Docstrings
**Pattern**: URL pattern, HTTP methods, parameters

```python
@api_view(['POST'])
def create_schema(request):
    """Create a new schema for the authenticated user.

    URL: POST /api/schemas/

    Request Body:
        {
            "name": str (required) - Schema name
            "fields": list[dict] (required) - Field definitions
        }

    Returns:
        201: Schema created
        400: Validation error
    """
    pass
```

#### Business Logic in Views
**Pattern**: Simple logic OK in views, complex in services

```python
# ✅ Simple logic in view
@login_required
def toggle_schema(request, schema_id):
    schema = get_object_or_404(Schema, id=schema_id, owner=request.user)
    schema.is_active = not schema.is_active
    schema.save(update_fields=['is_active'])
    return redirect('schema-detail', pk=schema_id)


# ✅ Complex logic in service layer
def process_audio(request):
    result = audio_service.process_file(
        file=request.FILES['file'],
        schema_id=request.data['schema_id'],
        user=request.user
    )
    return Response({'result_id': result.id}, status=202)
```

#### Response Formatting
**Pattern**: Named variable for complex responses

```python
# ✅ Named variable for complex responses
@api_view(['POST'])
def create_schema(request):
    serializer = SchemaSerializer(data=request.data)

    if not serializer.is_valid():
        error_response = {
            'status': 'error',
            'errors': serializer.errors
        }
        return Response(error_response, status=400)

    schema = serializer.save(owner=request.user)
    success_response = {
        'status': 'success',
        'data': {'id': schema.id, 'name': schema.name}
    }
    return Response(success_response, status=201)
```

---

## Testing Conventions

### Test Organization

#### Test File Naming
**Pattern**: Mirror source structure with `tests/test_<module>.py`

```
apps/schemas/
├── models.py
├── views.py
├── services.py
└── tests/
    ├── test_models.py
    ├── test_views.py
    └── test_services.py
```

#### Test Class Naming
**Pattern**: `Test<ClassName>` (pytest/unittest standard)

```python
class TestSchema(TestCase):
    """Tests for Schema model."""

    def test_create_schema(self):
        schema = Schema.objects.create(name="Test")
        self.assertEqual(schema.name, "Test")
```

#### Test Method Naming
**Pattern**: `test_<what>_<condition>_<expected>` (BDD-style)

```python
class TestFileProcessor(TestCase):
    def test_process_file_valid_audio_returns_result(self):
        result = process_file('valid.wav')
        self.assertIsInstance(result, AudioResult)

    def test_process_file_invalid_format_raises_error(self):
        with self.assertRaises(AudioFormatError):
            process_file('invalid.txt')
```

#### Test Docstrings
**Pattern**: Only for complex tests (method name should be sufficient)

```python
# ✅ No docstring needed - name is clear
def test_process_file_valid_wav_returns_result(self):
    result = process_file('test.wav')
    self.assertIsNotNone(result)


# ✅ Docstring adds value - complex setup
def test_concurrent_processing_with_shared_cache(self):
    """Test that concurrent file processing doesn't corrupt shared cache.

    Setup: Create 10 audio files, process concurrently with ThreadPoolExecutor
    Validates: No cache corruption, all results correct
    """
    pass
```

#### Test Assertion Messages
**Pattern**: Only for non-obvious assertions

```python
# ✅ Message adds debugging context
def test_process_multiple_files_all_succeed(self):
    files = ['file1.wav', 'file2.wav', 'file3.wav']
    results = [process_file(f) for f in files]

    for i, result in enumerate(results):
        self.assertTrue(
            result.success,
            f"Processing failed for {files[i]}: {result.error}"
        )
```

---

## Performance & Optimization

### Code Optimization Preferences

#### Premature Optimization
**Pattern**: Profile first, then optimize (Donald Knuth's wisdom)

```python
# ✅ Write clear code first
def process_schemas(user):
    schemas = Schema.objects.filter(owner=user, is_active=True)
    results = []
    for schema in schemas:
        if schema.has_valid_fields():
            results.append(validate_and_process(schema))
    return results


# Then if profiling shows slow, optimize specifically
def process_schemas(user):
    # Profile showed N+1 query problem
    schemas = Schema.objects.filter(
        owner=user, is_active=True
    ).select_related('owner').prefetch_related('fields')
    # ... rest of logic
```

#### List vs Generator
**Pattern**: Context-dependent (lists for small/reusable, generators for large/single-pass)

```python
# ✅ List - small collection, need multiple passes
schemas = list(Schema.objects.filter(owner=user))
print(f"Found {len(schemas)} schemas")


# ✅ Generator - large data, single pass
def process_large_file(filepath):
    with open(filepath) as f:
        for line in f:  # Generator
            yield process_line(line)
```

#### Database Query Optimization
**Pattern**: Add select_related/prefetch_related when N+1 detected

```python
# ✅ Add optimization when N+1 detected
class SchemaListView(ListView):
    def get_queryset(self):
        return Schema.objects.filter(
            owner=self.request.user
        ).select_related('owner').prefetch_related('rules')
```

#### Caching Strategy
**Pattern**: Cache based on profiling data

```python
# ✅ Add caching after profiling shows it's needed
from django.core.cache import cache

def get_user_statistics(user):
    cache_key = f'user_stats_{user.id}'
    stats = cache.get(cache_key)

    if stats is None:
        stats = calculate_expensive_stats(user)
        cache.set(cache_key, stats, 300)  # 5 minutes

    return stats
```

#### Readability vs Performance
**Pattern**: Readability wins by default; performance-critical code can be optimized with documentation

```python
# ✅ Performance-critical - document why optimized
def process_audio_samples(samples):
    """Process audio samples using vectorized operations.

    Note: Uses NumPy for performance (10x faster than pure Python).
    """
    import numpy as np
    samples_array = np.array(samples, dtype=np.float32)
    # Optimized vectorized operations
```

---

## Logging & Debugging

### Logging Preferences (Enhanced Loguru)

#### Log Levels
**Extended Loguru levels**:

- **TRACE**: Fine-grained debugging (loop iterations, variable states)
- **DEBUG**: Diagnostic info; automatic with function tracing
- **INFO**: General messages; smart context styling auto-highlights
- **SUCCESS**: Operation completion (Loguru-specific)
- **WARNING**: Potential issues
- **ERROR**: Operation failures; exception hooks provide beautiful tracebacks
- **CRITICAL**: System failures; triggers comprehensive diagnostics

#### Log Message Format
**Pattern**: Structured with bind() + template system

```python
from loguru import logger

# ✅ Structured with bind() + smart context styling
logger.bind(
    file_path=file_path,
    schema_id=schema_id,
    user_id=user.id
).info("File processing started")


# ✅ Configure dual streams
logger.configure_streams(
    console=dict(template="beautiful", level="INFO"),
    file=dict(sink="app.log", template="minimal", level="DEBUG"),
    json=dict(sink="data.jsonl", serialize=True)
)
```

#### Exception Logging
**Pattern**: Use exception hooks + context-aware logging

```python
from loguru import logger
from loguru._exception_hook import install_exception_hook

# ✅ Install global exception hook
install_exception_hook(logger, template="beautiful")


# ✅ Use @logger.catch for automatic exception handling
@logger.catch
def process_file(file_path):
    # Any exception automatically logged with beautiful formatting
    data = parse_audio(file_path)
    return transform(data)
```

#### Sensitive Data in Logs
**Pattern**: Smart masking with custom patterns

```python
def mask_email(email):
    username, domain = email.split('@')
    return f"{username[0]}***@{domain}"

logger.bind(
    user_email=mask_email(user.email),
    user_id=user.id
).info("User action performed")
```

#### Log Statement Density
**Pattern**: Use function tracing instead of manual entry/exit logs

```python
from loguru._tracing import FunctionTracer

tracer = FunctionTracer(logger, "beautiful")

@tracer.trace
def process_audio_pipeline(file_path, schema_id):
    # Entry/exit automatically logged!
    audio_data = load_audio(file_path)
    return apply_transformations(audio_data, schema_id)
```

#### Advanced Function Tracing
**Pattern**: Use performance and development tracers with rule-based configuration

```python
from loguru._tracing import FunctionTracer, PerformanceTracer

# ✅ Configure tracing rules by pattern
tracer = FunctionTracer(logger, "beautiful")

tracer.add_rule(
    pattern=r"^process_.*",  # All process_* functions
    log_args=True,
    log_result=True,
    log_duration=True,
    level="DEBUG"
)

tracer.add_rule(
    pattern=r"^_.*",  # Private functions
    enabled=False  # Don't trace
)

# ✅ Performance monitoring with thresholds
perf_tracer = PerformanceTracer(logger)

@perf_tracer.trace_performance(threshold_ms=500)
def slow_operation():
    # Automatic alert if > 500ms
    time.sleep(0.6)
    return "result"

# Get performance statistics
stats = perf_tracer.get_performance_stats("slow_operation")

# ✅ Development vs Production tracers
from loguru._tracing import create_development_tracer, create_production_tracer

if settings.DEBUG:
    tracer = create_development_tracer(logger)  # Verbose
else:
    tracer = create_production_tracer(logger)  # Minimal
```

#### Global Exception Hooks
**Pattern**: Beautiful exception formatting for all unhandled exceptions

```python
from loguru._exception_hook import install_exception_hook, ExceptionContext

# ✅ Install global exception hook
hook = install_exception_hook(logger, template="beautiful")

# Now all unhandled exceptions are beautifully formatted
def risky_function():
    return 1 / 0  # Caught and styled automatically

# ✅ Temporary exception hooks for code blocks
with ExceptionContext(logger, "beautiful") as ctx:
    risky_operation()
    another_risky_operation()
# Hook automatically removed when exiting

# ✅ Development hook with enhanced context
from loguru._exception_hook import create_development_hook

dev_hook = create_development_hook(logger)
dev_hook.install()
# Captures local variables, provides rich debugging context

# ✅ Thread exception handling
# Exception hooks automatically capture exceptions from all threads
import threading

def background_task():
    raise ValueError("Background error")  # Automatically caught and logged

thread = threading.Thread(target=background_task)
thread.start()
```

#### Log Analysis and Monitoring
**Pattern**: Use built-in analysis tools for health checks and debugging

```python
from loguru import (
    analyze_log_file,
    check_health,
    quick_stats,
    get_error_summary,
    find_log_patterns
)

# ✅ Daily health checks
def daily_log_health_check():
    """Automated log health monitoring."""
    health = check_health("production.log")

    if health['status'] == 'critical':
        logger.critical("Critical log issues detected", extra=health['issues'])
        send_alert(health)

# ✅ Quick stats for debugging
stats = quick_stats("app.log")
print(stats)  # One-line summary

# ✅ Error investigation
errors = get_error_summary("app.log")
logger.info("Error summary", extra={'error_count': errors['error_count']})

# ✅ Pattern-based debugging
database_errors = find_log_patterns("app.log", r"database.*error")

# ✅ Comprehensive analysis
full_analysis = analyze_log_file("app.log")
# Returns: error counts, performance metrics, health status, patterns

# ✅ Generate formatted reports
from loguru import generate_report

report = generate_report("app.log", format="markdown")
with open("logs/daily_report.md", "w") as f:
    f.write(report)
```

**Available analysis functions**:
- `analyze_log_file()` - Comprehensive analysis
- `check_health()` - Health assessment with scoring
- `quick_stats()` - One-line summary
- `get_error_summary()` - Error-focused analysis
- `get_performance_summary()` - Performance metrics
- `find_log_patterns()` - Regex pattern search
- `generate_report()` - Formatted reports (markdown, JSON, HTML)

---

### Debug Code

#### Print Statements
**Pattern**: Never - use Loguru (just as easy!)

```python
# ❌ NEVER
print(f"Processing {file_path}")


# ✅ ALWAYS
logger.debug(f"Processing {file_path}")


# ✅ Even easier with function tracing
@tracer.trace
def process_file(file_path):
    # Automatic logging!
    pass
```

#### Debugger Breakpoints
**Pattern**: Conditional via env vars + Loguru's dynamic debugging

```python
import os

DEBUG_BREAKPOINTS = os.getenv('DEBUG_BREAKPOINTS', 'False') == 'True'

def process_data(data):
    if DEBUG_BREAKPOINTS:
        breakpoint()
    return transform(data)
```

#### Debug Modes
**Pattern**: Layered approach (env vars → Django settings → feature flags)

```python
# settings.py
import os

DEBUG = os.getenv('DEBUG', 'False') == 'True'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG_SQL = os.getenv('DEBUG_SQL', str(DEBUG)) == 'True'

def configure_logging():
    if ENVIRONMENT == 'development':
        logger.configure_style("beautiful")
        logger.level("TRACE" if DEBUG else "DEBUG")
    else:
        logger.configure_streams(
            console=dict(template="minimal", level="WARNING"),
            file=dict(sink="logs/production.log", serialize=True)
        )
```

---

## Git & Version Control

### Commit Preferences

#### Commit Message Format
**Pattern**: Conventional Commits (industry standard)

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

# Examples:
feat(audio): Add FFmpeg binary detection service
fix(queue): Resolve race condition in batch processor
docs(api): Update REST API authentication documentation
```

**Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

#### Commit Frequency
**Pattern**: Commit after each logical change (atomic commits)

```bash
# ✅ Atomic commits
git commit -m "feat(schemas): Add is_active field to Schema model"
git commit -m "feat(schemas): Add migration for is_active field"
git commit -m "feat(api): Expose is_active field in Schema API"
```

#### WIP Commits
**Pattern**: OK in feature branches only, must be squashed before merging

```bash
# ✅ In feature branch
git commit -m "WIP: Implementing OAuth integration (login works, logout pending)"

# Before merging - squash
git rebase -i main
```

---

## Custom Preferences

### Additional Requirements

#### String Formatting
**Pattern**: f-strings exclusively (except SQL parameters, i18n)

```python
# ✅ f-strings
logger.info(f"Processing {file_path} with schema {schema_id}")
error_msg = f"Invalid rate: {rate}. Expected: {MIN_RATE}-{MAX_RATE}"
```

#### Path Handling
**Pattern**: pathlib.Path exclusively

```python
from pathlib import Path

# ✅ pathlib.Path
file_path = Path("uploads") / "audio" / "file.wav"
file_path.exists()
file_path.read_text()
```

#### Configuration Management
**Pattern**: Layered approach (12-factor app methodology)

1. **Environment variables** (.env files)
2. **Django settings** (base/production/development)
3. **Application constants** (constants.py)
4. **Feature flags** (database-backed)
5. **Secrets management** (AWS Secrets Manager for production)

#### Dependency Injection
**Pattern**: No formal DI framework - pass as needed (Django's pragmatic approach)

```python
class AudioService:
    def __init__(self, storage=None, logger=None):
        from django.core.files.storage import default_storage
        self.storage = storage or default_storage
        self.logger = logger or logger
```

---

## Priorities & Enforcement

### Priority Ranking (1=most important, 10=least)

1. **Clear, descriptive naming** - Foundation of readable code
2. **Consistent patterns across codebase** - Reduces cognitive load
3. **Code readability over brevity** - Future-proof maintenance
4. **Error handling completeness** - Prevents silent failures
5. **Consistent formatting (automated)** - Zero mental effort with tools
6. **Test coverage** - Focus on critical paths
7. **Type safety (type hints)** - Helps with tooling
8. **Comprehensive documentation** - Good docstrings > extensive comments
9. **Git commit quality** - Important for collaboration
10. **Performance optimization** - Only optimize what's actually slow

### Enforcement Preferences

#### Enforcement Mechanism
**Pattern**: Lightweight pre-commit hooks + CI checks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort

  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
```

#### Standard Violations
**Pattern**: Graduated approach

- **Level 1 (Auto-fix)**: Formatting, imports - auto-fixes
- **Level 2 (Hard block)**: Security risks - must fix
- **Level 3 (Soft warning)**: Best practices - track as tech debt
- **Level 4 (Guidance)**: Nice-to-haves - warning only

#### Standard Updates
**Pattern**: Pragmatic solo process

- Track in version-controlled markdown
- Trial new standards on one module (1-2 weeks)
- Quarterly reviews
- Gradual adoption
- Document reasoning

---

## AI Agent Requirements

### AI-Generated Code

#### AI Code Markers
**Pattern**: Mark complex/non-obvious AI code with context in docstrings

```python
def process_audio_batch(files: list[Path]) -> list[AudioResult]:
    """Process multiple audio files concurrently.

    AI-assisted implementation using ThreadPoolExecutor pattern.
    Reviewed for thread safety and error handling.

    Note: Concurrency logic generated by Claude, tested manually with 100+ files.
    """
    pass
```

#### AI Code Review
**Pattern**: Focus on specific risk areas

- **Edge cases** (empty, null, missing, invalid)
- **Error handling** (specific exceptions, not generic)
- **Security** (path traversal, injection, XSS)
- **Resource management** (cleanup, context managers)
- **Type correctness** (None checks, type mismatches)

#### AI Agent Instructions
**Pattern**: Detailed for security/complexity, high-level for standard patterns

```
# Detailed for security
"Implement user authentication for API endpoints. Requirements:
- Use Django's IsAuthenticated permission class
- Add rate limiting (100 requests/hour)
- Never log passwords or tokens"

# High-level for standard patterns
"Add CRUD API for Template model following existing patterns"
```

#### Cross-Agent Consistency
**Pattern**: Multi-layer approach

1. Standards document (this file)
2. Reference examples (pattern library)
3. Project patterns (Samplify-specific)
4. Pre-commit checks (automated enforcement)
5. Code review (human validation)

---

## Development Tools

### Required Tools

1. **Black** (code formatter)
   - Line length: 120
   - Target Python version: 3.10+

2. **Pylint** (linter)
   - Score threshold: 8.5/10
   - Django plugin enabled

3. **mypy** (type checker)
   - Strict mode enabled
   - Django stubs installed

4. **isort** (import sorter)
   - Profile: django
   - Line length: 120

### Configuration Files

**pyproject.toml**:
```toml
[tool.black]
line-length = 120
target-version = ['py310']

[tool.isort]
profile = "django"
line_length = 120
multi_line_output = 3
include_trailing_comma = true

[tool.mypy]
python_version = "3.10"
strict = true
plugins = ["mypy_django_plugin.main"]

[tool.pylint.messages_control]
max-line-length = 120
disable = ["C0111"]
```

**Pre-commit hooks** (.pre-commit-config.yaml):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        args: [--line-length=120]

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=django, --line-length=120]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        args: [--strict]

  - repo: https://github.com/PyCQA/pylint
    rev: v3.0.2
    hooks:
      - id: pylint
        args: [--max-line-length=120]
```

---

## Quick Reference

### Pre-Commit Checklist

- [ ] Run `black --line-length=120 .`
- [ ] Run `isort --profile=django --line-length=120 .`
- [ ] Run `mypy --strict .`
- [ ] Run `pylint --max-line-length=120 .` (score ≥ 8.5)
- [ ] All functions have Google-style docstrings
- [ ] All function signatures have type hints
- [ ] Complex logic has explanatory comments
- [ ] Algorithm preservation documented (if applicable)
- [ ] No lines exceed 120 characters
- [ ] Variable names are explicit and readable

### Naming Quick Reference

| Element | Pattern | Example |
|---------|---------|---------|
| Boolean var | is/has/can + description | `is_valid`, `has_permission`, `can_process` |
| Counter var | Descriptive name | `file_index`, `worker_count` |
| Collection var | Type suffix | `file_list`, `result_dict`, `error_set` |
| Constant | SCREAMING_SNAKE_CASE | `MAX_WORKERS`, `API_ENDPOINT` |
| Function (action) | Verb-Noun / Strong verb | `validate_input()`, `process_files()` |
| Function (query) | get/find/fetch | `get_user()`, `find_match()`, `fetch_data()` |
| Function (bool) | is/has/can | `is_valid()`, `has_errors()`, `can_delete()` |
| Private function | Single underscore | `_internal_helper()` |
| Class | PascalCase | `FileProcessor`, `UserFactory` |
| Module | snake_case | `file_processor.py`, `utils.py` |
| Django app | Plural | `users/`, `schemas/`, `files/` |

### Common Patterns

**Complex boolean**:
```python
if (
    condition_one
    and condition_two
    and not condition_three
):
    pass
```

**Guard clauses**:
```python
def process(data):
    if not data:
        return None
    if not validate(data):
        return None
    # Main logic
    return result
```

**Error handling**:
```python
try:
    result = operation()
except SpecificError as e:
    logger.error(f"Context: {e}")
    raise ProcessingError(f"Message") from e
```

**enumerate()**:
```python
for index, item in enumerate(items):
    process(item, position=index)
```

---

**Version History**:
- **3.1** (2025-10-03): Enhanced Loguru features - Advanced tracing, exception hooks, log analysis
  - Added: Advanced Function Tracing (pattern-based rules, performance tracers)
  - Added: Global Exception Hooks (beautiful formatting, thread support)
  - Added: Log Analysis and Monitoring (health checks, pattern search, reports)
- **3.0** (2025-10-03): Complete elicitation - All 13 sections with comprehensive preferences
  - Added: Error Handling & Validation
  - Added: Django-Specific Patterns
  - Added: Testing Conventions
  - Added: Performance & Optimization
  - Added: Logging & Debugging (Enhanced Loguru)
  - Added: Git & Version Control
  - Added: Custom Preferences
  - Added: Priorities & Enforcement
  - Added: AI Agent Requirements
- **2.0** (2025-10-03): Enhanced with elicited preferences (Sections 1-4)
- **1.0** (2025-10-03): Initial coding standards document
