# Development Environment Setup

**Version:** 1.0
**Last Updated:** 2025-10-04
**Target:** Django Web UI Modernization

---

## Prerequisites

Before setting up the Samplify development environment, ensure you have:

- **Python 3.10+** (required for Django 4.2+ and type hints)
- **Git** (for version control)
- **Node.js 20+** and **npm** (for BMAD tools and md-tree)
- **Text editor/IDE** (VS Code, PyCharm, or similar)

**Operating Systems Supported:**
- ✅ Windows 10/11
- ✅ macOS 12+
- ✅ Linux (Ubuntu 20.04+, Fedora, etc.)

---

## Quick Start (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/Samplify.git
cd Samplify

# 2. Checkout dev branch
git checkout dev

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 5. Install dependencies (once requirements.txt exists)
pip install -r requirements.txt

# 6. Verify setup
python --version  # Should show Python 3.10+

# You're ready to start Story 1.0!
```

---

## Detailed Setup Instructions

### Step 1: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/yourusername/Samplify.git
cd Samplify

# Verify you're in the right place
ls -la
# Should see: .bmad-core/, docs/, handlers/, app/, etc.
```

### Step 2: Checkout Dev Branch

```bash
# Checkout development workspace
git checkout dev

# Verify branch
git branch
# Should show: * dev

# Check documentation is present
ls docs/architecture/
# Should show: api-endpoints.md, database-schema-design.md, etc.
```

### Step 3: Create Python Virtual Environment

**Why virtual environments?**
- Isolate project dependencies
- Avoid conflicts with system Python
- Enable reproducible builds

**Windows:**
```bash
# Create venv
python -m venv venv

# Activate
venv\Scripts\activate

# Verify activation (should show (venv) prefix)
which python
# Should show: .../Samplify/venv/Scripts/python
```

**macOS/Linux:**
```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify activation
which python
# Should show: .../Samplify/venv/bin/python
```

**Deactivating:**
```bash
deactivate  # Exit virtual environment
```

### Step 4: Install Python Dependencies

**⚠️ Note:** `requirements.txt` will be created in Story 1.0. For now, this is the planned content:

**Expected `requirements.txt`:**
```txt
# Django framework
Django>=4.2,<5.0

# Database
# (SQLite is built-in, no extra package needed)

# Logging
loguru>=0.7.0

# Media processing (PIL)
Pillow>=10.0.0

# File watching
watchdog>=3.0.0

# Development tools
black>=23.0.0
pylint>=3.0.0
mypy>=1.0.0
isort>=5.12.0
pre-commit>=3.0.0

# Django type stubs for mypy
django-stubs>=4.2.0
```

**Install (once file exists):**
```bash
pip install -r requirements.txt

# Verify Django installation
python -m django --version
# Should show: 4.2.x or higher
```

### Step 5: Install Development Tools

**Install BMAD and md-tree (if not already installed):**
```bash
# Navigate to BMAD fork
cd /c/Users/Admin/Documents/GitHub/BMAD-METHOD

# Install BMAD globally
npm run install:global

# Verify md-tree is available
md-tree version
# Should show: md-tree v1.6.1

# Return to Samplify
cd /c/Users/Admin/Documents/GitHub/Samplify
```

### Step 6: Configure Pre-Commit Hooks

**Once Story 1.0 creates `.pre-commit-config.yaml`:**

```bash
# Install pre-commit hooks
pre-commit install

# Test hooks
pre-commit run --all-files

# Should run: black, isort, pylint, mypy
```

### Step 7: Verify FFmpeg (After Story 1.4)

**FFmpeg will be auto-downloaded by Django management command:**

```bash
# Run setup command (Story 1.4+)
python manage.py setup

# Should output:
# ✓ FFmpeg is available
# ffmpeg version 6.x.x
```

---

## IDE Configuration

### Visual Studio Code

**Recommended Extensions:**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.pylint",
    "batisteo.vscode-django",
    "bradlc.vscode-tailwindcss"
  ]
}
```

**Settings (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "120"],
  "editor.formatOnSave": true,
  "editor.rulers": [120],
  "[python]": {
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm

**Configuration:**
1. **Open Project** → Select `Samplify` directory
2. **Python Interpreter** → Add Local Interpreter → Select `venv/bin/python`
3. **Code Style** → Python → Set line length to 120
4. **Tools** → Black → Enable "On code reformat"
5. **Tools** → Python Integrated Tools → Set Docstring format to "Google"

---

## Project Structure After Setup

```
Samplify/
├── venv/                        # Virtual environment (gitignored)
├── .bmad-core/                  # BMAD configuration
├── docs/                        # All documentation
│   ├── architecture/            # Technical design docs
│   ├── prd/                     # PRD sections
│   └── stories/                 # Story files
├── app/                         # Brownfield Python app (legacy)
├── handlers/                    # Brownfield handlers (legacy)
├── database/                    # Brownfield database (legacy)
├── .gitignore                   # Git ignore rules
└── README.md                    # Project overview

# After Django setup (Story 1.1+):
├── manage.py                    # Django management script
├── samplify/                    # Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                        # Django applications
│   ├── schemas/
│   ├── processing/
│   └── catalog/
├── frontend/                    # Frontend assets
│   ├── static/
│   └── templates/
├── bin/                         # FFmpeg binaries (auto-downloaded)
└── requirements.txt             # Python dependencies
```

---

## Common Setup Issues

### Issue 1: Python Version Too Old

**Error:** `Python 3.9 or older detected`

**Solution:**
```bash
# Install Python 3.10+ from python.org
# Then create venv with explicit version
python3.10 -m venv venv
```

### Issue 2: Virtual Environment Not Activating

**Windows - "Execution Policy" Error:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry activation
venv\Scripts\activate
```

**macOS/Linux - Permission Denied:**
```bash
# Make activate script executable
chmod +x venv/bin/activate

# Then retry
source venv/bin/activate
```

### Issue 3: pip Install Fails

**Error:** `Could not find a version that satisfies the requirement...`

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Retry installation
pip install -r requirements.txt
```

### Issue 4: md-tree Command Not Found

**Solution:**
```bash
# Reinstall BMAD globally
cd /path/to/BMAD-METHOD
npm run install:global

# Verify installation
md-tree version
```

### Issue 5: Git Branch Issues

**Error:** `Cannot checkout dev - branch does not exist`

**Solution:**
```bash
# Fetch all branches
git fetch origin

# Checkout dev (creates local tracking branch)
git checkout -b dev origin/dev

# Or if dev is local-only:
git branch
# Should show: dev
```

---

## Development Workflow Checklist

### Daily Development Routine

- [ ] Activate virtual environment (`source venv/bin/activate`)
- [ ] Pull latest changes (`git pull origin dev`)
- [ ] Check branch (`git branch` - should show feature branch)
- [ ] Run tests if applicable (`python manage.py test`)
- [ ] Make changes
- [ ] Run linters (`black .`, `isort .`, `pylint apps/`)
- [ ] Commit changes (`git commit -m "..."`)
- [ ] Push to remote (`git push origin feature/story-X.X`)

### Before Starting New Story

- [ ] Ensure on `dev` branch (`git checkout dev`)
- [ ] Pull latest (`git pull origin dev`)
- [ ] Create feature branch (`git checkout -b feature/story-X.X`)
- [ ] Read story file (`docs/stories/story-XX-....md`)
- [ ] Review related architecture docs
- [ ] Implement story
- [ ] Run tests
- [ ] Merge to `dev`

---

## Environment Variables

**Django will use environment variables (Story 1.1+):**

Create `.env` file (gitignored):
```bash
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite - no config needed)

# FFmpeg paths (auto-detected, override if needed)
# FFMPEG_BINARY_PATH=/custom/path/to/ffmpeg
```

**Load with python-decouple or django-environ (Story 1.1).**

---

## Testing Your Setup

### Verify Python Environment

```bash
# Activate venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Check Python version
python --version
# Expected: Python 3.10.x or higher

# Check pip
pip --version
# Should show venv path

# List installed packages
pip list
# Should show Django, Pillow, watchdog, etc. (after requirements installed)
```

### Verify Git Configuration

```bash
# Check current branch
git branch
# Should show: * dev or * feature/story-X.X

# Check remote
git remote -v
# Should show origin pointing to GitHub

# Check commit history
git log --oneline -5
# Should show recent commits including documentation sharding
```

### Verify BMAD Tools

```bash
# Check md-tree
md-tree version
# Expected: md-tree v1.6.1

# Check bmad
bmad --version
# Expected: 4.43.0 (or your fork version)
```

### Verify Documentation

```bash
# Check architecture docs exist
ls docs/architecture/
# Should show: api-endpoints.md, database-schema-design.md, etc.

# Check stories exist
ls docs/stories/
# Should show: story-10-..., story-11-..., etc.
```

---

## Next Steps After Setup

1. **Read Story 1.0** (`docs/stories/story-10-repository-environment-foundation.md`)
2. **Create feature branch** (`git checkout -b feature/story-1.0-repository-foundation`)
3. **Implement Story 1.0** (create `requirements.txt`, `.gitignore`, etc.)
4. **Run tests** (verify setup works)
5. **Commit and merge** to `dev` branch

---

## Additional Resources

### Documentation References

- **[Architecture Overview](./architecture/index.md)** - System design
- **[PRD](./prd/index.md)** - Requirements
- **[Stories](./stories/index.md)** - Implementation tasks
- **[Coding Standards](./architecture/coding-standards.md)** - CS1-CS13 rules
- **[Git Workflow](./GIT_WORKFLOW.md)** - Branching strategy

### External Resources

- **Django Documentation**: https://docs.djangoproject.com/en/4.2/
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html
- **Black Formatter**: https://black.readthedocs.io/
- **BMAD Methodology**: https://github.com/bmad-code-org/BMAD-METHOD

---

## Troubleshooting & Support

### Getting Help

1. **Check documentation** - Most questions answered in docs/
2. **Review story files** - Detailed acceptance criteria per story
3. **Check architecture docs** - Technical specifications
4. **Git issues** - See GIT_WORKFLOW.md
5. **Python issues** - Verify venv activation, pip version

### Common Commands Reference

```bash
# Virtual environment
python -m venv venv                  # Create
source venv/bin/activate             # Activate (Unix)
venv\Scripts\activate                # Activate (Windows)
deactivate                           # Deactivate

# Git
git checkout dev                     # Switch to dev
git checkout -b feature/name         # Create feature branch
git status                           # Check status
git add .                            # Stage changes
git commit -m "message"              # Commit
git push origin branch-name          # Push

# Django (after Story 1.1)
python manage.py runserver           # Start dev server
python manage.py migrate             # Run migrations
python manage.py test                # Run tests
python manage.py setup               # Setup (FFmpeg, etc.)

# Formatting/Linting
black .                              # Format code
isort .                              # Sort imports
pylint apps/                         # Lint code
mypy apps/                           # Type check
pre-commit run --all-files           # Run all hooks
```

---

**Setup complete? You're ready to start development!** 🚀

Read `docs/stories/story-10-repository-environment-foundation.md` to begin Story 1.0.
