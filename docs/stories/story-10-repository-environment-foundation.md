# Story 1.0: Repository & Environment Foundation

### User Story
As a **developer**,
I want **a properly configured development environment with dependency management**,
So that **I can clone the repository and start development without manual configuration**.

### Story Context
**Existing System Integration:**
- Integrates with: Current CLI codebase
- Technology: Python 3.10+, Git, pip/virtualenv
- Follows pattern: Standard Python project structure
- Touch points: Root directory structure, .gitignore, requirements management

### Acceptance Criteria

**1.0A: .gitignore Configuration**
1. `.gitignore` file excludes all binaries (`/bin/`, `*.exe`, `*.dll`, `*.so`)
2. `.gitignore` excludes virtual environments (`venv/`, `env/`, `.venv/`)
3. `.gitignore` excludes Python cache (`__pycache__/`, `*.pyc`, `*.pyo`)
4. `.gitignore` excludes Django artifacts (`db.sqlite3`, `*.log`, `/static/`, `/media/`)
5. `.gitignore` excludes IDE files (`.idea/`, `.vscode/`, `*.swp`)
6. `.gitignore` excludes downloaded dependencies and temporary files

**1.0B: Virtual Environment Setup**
1. Virtual environment creation script provided (`setup_env.sh` or `setup_env.bat`)
2. Virtual environment uses Python 3.10+ as base interpreter
3. Virtual environment activates correctly on Windows, macOS, and Linux
4. Documentation includes activation instructions for all platforms

**1.0C: requirements.txt Creation**
1. `requirements.txt` lists all Python dependencies with pinned versions
2. Core dependencies included:
   - Django 4.2+
   - Pillow (for image processing)
   - watchdog (for file monitoring)
   - pathlib (if not stdlib)
   - Custom Loguru fork (with installation instructions)
3. Dependencies install successfully via `pip install -r requirements.txt`
4. No missing or conflicting dependencies

### Technical Notes
- **Integration Approach:** Prepares foundation for Django migration without disrupting current CLI
- **Existing Pattern Reference:** Standard Python project layout
- **Key Constraints:** Must support Python 3.10+ on Windows/macOS/Linux

### Definition of Done
- [ ] .gitignore configured and tested
- [ ] Virtual environment scripts work on all platforms
- [ ] requirements.txt complete and validated
- [ ] Documentation updated with setup instructions
- [ ] No binaries or virtual environments in git repository
- [ ] **Coding Standards**: All code adheres to CS1-CS13 (see `docs/coding-standards.md`)
- [ ] **Code Quality**: Black, Pylint (≥8.5), mypy, isort pass without errors
- [ ] **Documentation**: All functions have Google-style docstrings with type hints

### Risk Assessment
- **Primary Risk:** Missing dependencies causing installation failures
- **Mitigation:** Test installation on clean systems (Windows/macOS/Linux)
- **Rollback:** Remove files, restore to current state

---
