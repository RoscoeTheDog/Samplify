# Technology Stack

**Version:** 1.0
**Last Updated:** 2025-10-04
**Status:** Specification Document

---

## Overview

This document defines the complete technology stack for Samplify Django Web UI, including required versions, dependencies, and tooling configurations.

---

## Core Framework

### Python
- **Version**: 3.10+ (minimum), 3.11 recommended
- **Rationale**:
  - Type hints improvements (PEP 604 union syntax `str | None`)
  - Performance enhancements
  - Django 4.2 LTS compatibility
- **Installation**:
  - Windows: python.org official installer
  - macOS: Homebrew (`brew install python@3.11`) or python.org
  - Linux: System package manager or pyenv

### Django
- **Version**: 4.2.7 LTS (Long-Term Support)
- **Rationale**:
  - LTS release (support until April 2026)
  - Stable, production-ready
  - Enhanced async support
  - Improved type hints
- **Documentation**: https://docs.djangoproject.com/en/4.2/

### Database
- **SQLite**: 3.35.0+ (minimum for enhanced WAL mode)
- **Rationale**:
  - Built into Python (no separate installation)
  - WAL mode support for concurrent access
  - Lightweight, zero-configuration
  - Sufficient for local desktop application
- **Configuration**: WAL mode enabled via Django settings (see NFR2)

---

## Media Processing

### FFmpeg
- **Version**: 5.0+ (5.1.2 recommended)
- **License**: GPL 3.0 (LGPL 2.1 if using shared libraries only)
- **Purpose**: Audio/video transcoding, format conversion, metadata extraction
- **Installation**:
  - Automatic via setup script (downloads platform-specific binary)
  - Manual: See `ffmpeg-sources.md` for trusted sources
- **Binary Location**: `bin/<platform>/ffmpeg` (not committed to git)
- **Verification**: SHA256 checksum validation on download

### Pillow (PIL Fork)
- **Version**: 10.1.0+
- **Purpose**: Image processing, format conversion, metadata extraction
- **Installation**: `pip install Pillow>=10.1.0`
- **Dependencies**: Automatic binary wheels on Windows/macOS/Linux

---

## Python Dependencies

### Core Application Dependencies

```txt
# Web Framework
Django==4.2.7                # LTS web framework
django-environ==0.11.2       # Environment variable management (.env files)

# Logging
git+https://github.com/RoscoeTheDog/loguru.git@master  # Custom loguru fork with hierarchical logging

# File System Monitoring
watchdog==3.0.0              # Cross-platform file system events

# Image Processing
Pillow==10.1.0               # Image manipulation and format conversion

# HTTP Requests
requests==2.31.0             # HTTP library for FFmpeg downloads
certifi==2023.11.17          # SSL certificate bundle (for HTTPS verification)

# Utilities
python-dateutil==2.8.2       # Date/time utilities
```

### Development Dependencies

```txt
# Code Quality
black==23.11.0               # Code formatter (line-length=120)
pylint==3.0.2                # Linter
pylint-django==2.5.5         # Django-specific linting rules
mypy==1.7.0                  # Static type checker
django-stubs==4.2.6          # Type stubs for Django
isort==5.12.0                # Import sorter

# Testing
pytest==7.4.3                # Test framework
pytest-django==4.7.0         # Django integration for pytest
pytest-cov==4.1.0            # Coverage reporting
factory-boy==3.3.0           # Test data generation
faker==20.1.0                # Fake data generator

# Pre-commit Hooks
pre-commit==3.5.0            # Pre-commit hook framework

# Documentation
mkdocs==1.5.3                # Documentation generator (optional)
mkdocs-material==9.4.14      # Material theme for MkDocs (optional)
```

### Production Dependencies (Future Deployment)

```txt
# WSGI Server
gunicorn==21.2.0             # Production WSGI server (Linux/macOS)
waitress==2.1.2              # Production WSGI server (Windows alternative)

# Static Files
whitenoise==6.6.0            # Static file serving without nginx

# Process Management
supervisor==4.2.5            # Process control system (Linux)
```

---

## Development Tools Configuration

### Black (Code Formatter)

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 120
target-version = ['py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | migrations
)/
```

**Usage**:
```bash
black --line-length=120 .
```

---

### isort (Import Sorter)

**Configuration** (`pyproject.toml`):
```toml
[tool.isort]
profile = "django"
line_length = 120
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*"]
known_django = ["django"]
known_first_party = ["samplify", "apps"]
sections = ["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

**Usage**:
```bash
isort --profile=django --line-length=120 .
```

---

### mypy (Type Checker)

**Configuration** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
plugins = ["mypy_django_plugin.main"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.django-stubs]
django_settings_module = "samplify.settings"
```

**Usage**:
```bash
mypy --strict .
```

---

### Pylint (Linter)

**Configuration** (`.pylintrc`):
```ini
[MASTER]
load-plugins=pylint_django
django-settings-module=samplify.settings

[FORMAT]
max-line-length=120

[MESSAGES CONTROL]
disable=
    C0111,  # missing-docstring (handled by other tools)
    R0903,  # too-few-public-methods (common in Django models)
    R0801   # duplicate-code (common in Django views)

[DESIGN]
max-attributes=10
max-args=8
```

**Usage**:
```bash
pylint --max-line-length=120 apps/
```

---

### Pre-commit Hooks

**Configuration** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        args: [--line-length=120]
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=django, --line-length=120]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        args: [--strict]
        additional_dependencies: [django-stubs==4.2.6]

  - repo: https://github.com/pycqa/pylint
    rev: v3.0.2
    hooks:
      - id: pylint
        args: [--max-line-length=120]
        additional_dependencies: [pylint-django==2.5.5, Django==4.2.7]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
```

**Installation**:
```bash
pip install pre-commit
pre-commit install
```

---

## Browser Compatibility (Web UI)

### Target Browsers
- **Modern Browsers** (Evergreen, auto-updating):
  - Chrome/Edge 90+ (Chromium-based)
  - Firefox 88+
  - Safari 14+
  - Opera 76+

### JavaScript
- **Standard**: ES6+ (ECMAScript 2015+)
- **No transpilation** required (modern browsers support ES6 natively)
- **No frameworks**: Vanilla JavaScript only (per NFR3 - no CDN dependencies)

### CSS
- **Standard**: CSS3
- **No preprocessors**: Plain CSS only
- **No frameworks**: No Bootstrap, Tailwind, etc. (custom minimal CSS)

---

## Operating System Requirements

### Supported Platforms

| OS | Version | Python Source | FFmpeg Source |
|----|---------|---------------|---------------|
| **Windows** | 10, 11 (64-bit) | python.org | gyan.dev static builds |
| **macOS** | 12+ (Monterey+) | Homebrew or python.org | Homebrew or static builds |
| **Linux** | Ubuntu 20.04+, Debian 11+, Fedora 35+ | System package manager or pyenv | Static builds (johnvansickle) |

### Prerequisites (User Must Install)
1. **Python 3.10+** installed and in system PATH
2. **Git** (for cloning repository)
3. **Internet connection** (for pip installs, FFmpeg download during setup)

### Automated by Setup Script
- Virtual environment creation (`venv`)
- Python dependency installation
- FFmpeg binary download and verification
- Database initialization (migrations)
- Settings file generation

---

## Version Constraints Philosophy

### Dependency Versioning Strategy

1. **Pinned Major.Minor** (e.g., `Django==4.2.7`):
   - Core framework (Django)
   - Critical libraries (Pillow, watchdog)
   - **Rationale**: Prevent breaking changes

2. **Minimum Version** (e.g., `requests>=2.31.0`):
   - Utilities with stable APIs
   - **Rationale**: Allow security patches

3. **Development Tools**: Exact versions in pre-commit config
   - **Rationale**: Consistent formatting across environments

### Updating Dependencies

**Frequency**: Quarterly security review + urgent patches as needed

**Process**:
1. Check for security advisories (GitHub Dependabot, PyUp)
2. Test updates in isolated environment
3. Update `requirements.txt` or `requirements-dev.txt`
4. Run full test suite
5. Update `tech-stack.md` version numbers

---

## Installation Quick Reference

### Fresh Setup (Clone-to-Run)

```bash
# 1. Clone repository
git clone <repository-url>
cd Samplify

# 2. Run automated setup
python setup.py

# 3. Verify installation
python manage.py check
python manage.py test

# 4. Run development server
python manage.py runserver
```

### Manual Setup (Alternative)

```bash
# 1. Create virtual environment
python3.10 -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# 4. Download FFmpeg (if setup.py not used)
python manage.py download_ffmpeg

# 5. Initialize database
python manage.py migrate

# 6. Create superuser (optional)
python manage.py createsuperuser

# 7. Run server
python manage.py runserver
```

---

## Environment Variables

**Configuration**: Use `.env` file (loaded via `django-environ`)

**Required Variables**:
```env
# Django Core
SECRET_KEY=<random-50-char-string>
DEBUG=True  # False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional override)
DATABASE_NAME=database/samplify.db

# FFmpeg (optional override)
FFMPEG_PATH=bin/windows/ffmpeg.exe  # Auto-detected by default

# Logging
LOG_LEVEL=DEBUG  # INFO in production
LOG_FILE=logs/samplify.log
```

**Security Note**: `.env` file is gitignored. Use `.env.example` template.

---

## Dependency Rationale

### Why SQLite (not PostgreSQL/MySQL)?
- **Use case**: Local desktop application, single-user
- **Advantages**: Zero configuration, bundled with Python, sufficient performance
- **WAL mode**: Enables concurrent reads during writes
- **Future**: Could migrate to PostgreSQL for multi-user server deployment

### Why Custom Loguru Fork (not stdlib logging)?
- **Developer experience**: Simpler API, hierarchical formatting
- **Hierarchical logging**: Tree-based visual output with Unicode box-drawing
- **Dual output**: Hierarchical console + structured JSON file logging
- **Features**: Automatic rotation, structured logging, global exception hooks
- **Performance**: Minimal overhead with intelligent caching
- **Fork source**: https://github.com/RoscoeTheDog/loguru

### Why Django 4.2 LTS (not 5.x)?
- **Stability**: LTS release with extended support (until April 2026)
- **Compatibility**: Mature ecosystem, stable third-party packages
- **Migration path**: Can upgrade to Django 5.x LTS when available

### Why Vanilla JavaScript (not React/Vue)?
- **NFR3**: No CDN dependencies requirement
- **Simplicity**: AJAX polling is straightforward with vanilla JS
- **Proof-of-concept**: Can add framework later if needed
- **Bundle size**: Zero external dependencies

---

## Related Documents

- **[FFmpeg Integration](./ffmpeg-sources.md)** - Binary sources, checksums, licensing
- **[Database Schema](./database-schema-design.md)** - SQLite configuration
- **[Coding Standards](./coding-standards.md)** - Development practices
- **[Testing Strategy](./testing-strategy.md)** - Test dependencies and approach

---

## Version History

- **1.1** (2025-10-05): Updated logging dependency to custom Loguru fork
  - Changed from standard Loguru 0.7.2 to RoscoeTheDog/loguru fork
  - Added hierarchical logging with tree-based visual output
  - Added dual output: hierarchical console + structured JSON file
- **1.0** (2025-10-04): Initial tech stack specification
  - Python 3.10+, Django 4.2.7 LTS
  - Development tooling configurations
  - Complete dependency list with rationale
