# Technical Constraints and Integration Requirements

### Existing Technology Stack

**Current Stack** (from brownfield analysis):
- **Runtime**: Python 3.x
- **Database**: SQLite via SQLAlchemy ORM
- **Logging**: Structlog with custom processors
- **Media Processing**: FFmpeg (subprocess), PIL (images)
- **File Watching**: Watchdog library
- **Multiprocessing**: Python stdlib
- **Critical Gap**: No requirements.txt exists

### Integration Approach

**Django Migration Strategy:**

1. **Database**: SQLAlchemy → Django ORM, SQLite WAL mode, single-table inheritance
2. **Services**: Management commands for watch/batch processing
3. **Frontend**: Django templates with AJAX polling
4. **FFmpeg**: Bundled portable binaries in `/bin/<platform>/`

### Django Project Structure

```
samplify/
├── manage.py
├── setup.py                 # Single-point installation
├── requirements.txt
├── .gitignore
├── samplify/
│   ├── settings.py         # All configs (Loguru, ffmpeg, DB)
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── schemas/            # Schema configuration
│   ├── processing/         # Media processing services
│   │   └── management/commands/
│   │       ├── watch.py
│   │       └── batch_process.py
│   └── catalog/            # File cataloging
├── static/                 # Locally served assets
└── bin/                    # Platform ffmpeg binaries
    ├── windows/
    ├── macos/
    └── linux/
```

### Risk Assessment

**Critical Risks:**
1. Algorithm preservation validation (CR1)
2. SQLite WAL multiprocessing compatibility
3. FFmpeg platform binary compatibility
4. Dual watchdog race conditions

**Mitigation**: See architecture.md for detailed risk analysis

### Coding Standards and Conventions

**Developer Experience Level**: Junior to Mid-level (5 years experience, CS Associates degree background)

**Core Philosophy**: Prioritize human readability and maintainability over syntactic brevity. Code should be self-documenting and easily understood by developers transitioning from the brownfield CLI codebase to the new Django architecture.

#### Code Style Standards

**CS1: PEP 8 Compliance with Extensions**
- Follow PEP 8 Python style guide rigorously
- Line length: 120 characters maximum (extended from PEP 8's 79)
- Use newline breakpoints for long wrapped code segments with logical grouping
- Indent wrapped lines for visual clarity and logical flow

**CS2: Type Hinting Requirements**
- Use type hints for ALL function signatures (parameters and return types)
- Use type hints for complex variables and class attributes
- Leverage `typing` module for complex types (List, Dict, Optional, Union, etc.)
- Enable type checking via mypy or similar linter

**CS3: Google-Style Docstrings (Required)**
- All public functions, classes, and methods MUST have Google-style docstrings
- Include: Description, Args, Returns, Raises, Examples (where helpful)
- Format:
  ```python
  def function_name(param1: str, param2: int) -> bool:
      """Brief one-line description of function.

      Detailed description if needed. Explain the purpose, behavior,
      and any important context.

      Args:
          param1: Description of first parameter and its purpose
          param2: Description of second parameter and expected range/format

      Returns:
          Description of return value and its meaning

      Raises:
          ValueError: When param2 is negative
          IOError: When file operations fail

      Example:
          >>> result = function_name("test", 42)
          >>> print(result)
          True
      """
      # Implementation here
  ```

**CS4: Commenting Philosophy - Verbose and Contextual**
- Comment the "why", not just the "what"
- Complex algorithms: Comment each logical block explaining purpose
- Business logic: Explain rationale for decisions (e.g., "Preserve existing algorithm per CR1")
- Branching logic: Explain conditions and expected flow
- Regular intervals: Every 5-10 lines for complex sections
- Group related code with section comments:
  ```python
  # ============================================================
  # Section: Database Query Preparation
  # ============================================================
  # Build the query to fetch unprocessed files matching schema
  # rules. Uses Django ORM with select_related() to minimize
  # database hits during multiprocessing.

  query = File.objects.filter(
      status='pending',
      media_type__in=schema.get_supported_types()
  ).select_related('schema')
  ```

**CS5: Human-Readable Code Over Shortcuts**
- Prefer explicit variable names over abbreviations
  - ✅ `input_file_path` over `in_fp`
  - ✅ `processing_queue` over `proc_q`
- Prefer readable constructs over compact one-liners
  - ✅ Multi-line if/else over ternary when logic is complex
  - ✅ Explicit loops over list comprehensions when readability suffers
- Use intermediate variables to break complex expressions:
  ```python
  # ❌ Avoid complex one-liners
  result = [transform(f) for f in files if validate(f) and check_format(f.fmt)]

  # ✅ Prefer readable breakdown
  validated_files = [f for f in files if validate(f)]
  format_checked_files = [f for f in validated_files if check_format(f.format)]
  result = [transform(f) for f in format_checked_files]
  ```

**CS6: Code Linting and Formatting**
- Use **Black** formatter with 120-character line length
- Use **Pylint** for code quality checks (target score: 8.5+)
- Use **mypy** for static type checking (strict mode)
- Use **isort** for import organization (Django style)
- Pre-commit hooks REQUIRED for all formatting/linting tools
- Configuration files:
  - `pyproject.toml`: Black, isort, mypy configuration
  - `.pylintrc`: Pylint rules and exceptions

**CS7: Import Organization (isort - Django profile)**
```python
# Standard library imports (alphabetical)
import os
import sys
from pathlib import Path
from typing import List, Optional

# Third-party imports (alphabetical)
import numpy as np
from watchdog.observers import Observer

# Django imports (alphabetical by module)
from django.conf import settings
from django.db import models
from django.http import JsonResponse

# Local application imports (relative, alphabetical)
from apps.catalog.models import File
from apps.processing.services import FFmpegService
from apps.schemas.models import Schema
```

**CS8: Function and Method Length**
- Maximum function length: 50 lines (excluding docstring)
- If function exceeds 50 lines: refactor into smaller helper functions
- Each function should have a single, clear responsibility

**CS9: Error Handling - Explicit and Verbose**
- Always use explicit exception types (never bare `except:`)
- Provide detailed error messages with context:
  ```python
  try:
      result = process_file(file_path)
  except FileNotFoundError as e:
      # Log the error with full context for debugging
      logger.error(
          f"Failed to process file: {file_path} does not exist. "
          f"Ensure input directory is correctly configured. Error: {e}"
      )
      raise
  except FFmpegError as e:
      # Provide actionable error message
      logger.error(
          f"FFmpeg processing failed for {file_path}. "
          f"Check FFmpeg installation and file format compatibility. Error: {e}"
      )
      raise ProcessingError(f"Media processing failed: {e}") from e
  ```

**CS10: Django-Specific Conventions**
- Use Django ORM query optimization (select_related, prefetch_related)
- Document ORM queries with expected result sets
- Use Django's built-in validators and form handling
- Follow Django's "fat models, thin views" philosophy
- Use Django management commands for all CLI operations

**CS11: Algorithm Preservation Documentation**
- When porting algorithms from brownfield codebase (CR1/CR2):
  - Add header comment: `# ALGORITHM PRESERVED FROM: handlers/rules.py lines 45-120`
  - Document any adaptations: `# ADAPTATION: Changed SQLAlchemy query to Django ORM`
  - Include side-by-side reference to original code location
  - Mark with `# CR1 REQUIREMENT` or `# CR2 REQUIREMENT` for traceability

**CS12: Visual Code Organization**
- Use blank lines to separate logical blocks (2 lines between functions/classes)
- Use section dividers for major code sections:
  ```python
  # ================================================================
  # DATABASE OPERATIONS
  # ================================================================

  def fetch_pending_files(schema_id: int) -> List[File]:
      """Fetch all pending files for processing."""
      pass


  # ================================================================
  # FFMPEG PROCESSING
  # ================================================================

  def execute_transformation(file: File, rules: List[SchemaRule]) -> bool:
      """Execute FFmpeg transformation based on schema rules."""
      pass
  ```

**CS13: Code Review Checklist (Pre-Merge)**
- [ ] All functions have Google-style docstrings
- [ ] Type hints present on all function signatures
- [ ] Complex logic has explanatory comments (every 5-10 lines)
- [ ] Black, Pylint, mypy, isort pass without errors
- [ ] No lines exceed 120 characters
- [ ] Variable names are explicit and readable
- [ ] Error handling is explicit with detailed messages
- [ ] Algorithm preservation documented (if applicable)
- [ ] Code is visually organized with section breaks

#### Development Tools Configuration

**Required Tools**:
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

**Configuration Example** (`pyproject.toml`):
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
disable = ["C0111"]  # Add specific rule exemptions as needed
```

**Pre-Commit Hook Setup** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=120]

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=django, --line-length=120]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        args: [--strict]

  - repo: https://github.com/PyCQA/pylint
    rev: v3.0.0
    hooks:
      - id: pylint
        args: [--max-line-length=120]
```

#### Code Quality Gates

**DQ1: Automated Quality Checks (CI/CD)**
- All code MUST pass Black formatting check
- All code MUST achieve Pylint score ≥ 8.5/10
- All code MUST pass mypy type checking (no errors)
- All imports MUST be sorted via isort
- Pre-commit hooks MUST be installed and passing

**DQ2: Manual Code Review Focus**
- Algorithm preservation validation (CR1/CR2 compliance)
- Comment quality and density (adequate explanations)
- Error handling completeness (all exception paths covered)
- Docstring completeness (all public functions documented)
- Readability assessment (can junior dev understand quickly?)

**DQ3: Documentation Requirements**
- All stories MUST include coding standards compliance in Definition of Done
- All pull requests MUST reference coding standards adherence
- Code review template MUST include CS1-CS13 checklist

---
