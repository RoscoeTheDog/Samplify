# Development and Deployment

### Local Development Setup

**Current State** (no formal setup):
1. Clone repository
2. ⚠️ **Unknown dependencies** - no requirements file
3. Ensure ffmpeg installed and in system PATH
4. Run `python __main__.py` (creates user directories and database automatically)

**Known Issues**:
- Database drops on every run (development mode still active)
- No virtual environment configuration
- Windows-only (hardcoded paths, WMIC dependency)

### Build and Deployment Process

**No build process exists** - this is a Python script

- **Deployment**: Manual copy (not packaged)
- **Environments**: Only local development
- **Configuration**: XML templates in `%USERPROFILE%\Documents\Samplify\Templates\`

---

### Ephemeral Artifact Cleanup Guidelines

**Purpose**: Maintain clean repository per FR17 and NFR15 (Twelve-Factor App / Trunk-Based Development)

**Core Principle**: *"Ignore what can be regenerated from source of truth"*

#### Cleanup Timing

**Before Merging to `dev`** (Required - Trunk-Based Development Practice):
1. Delete all agent-generated debug scripts (`debug_*.py`, `test_*.py` in root)
2. Remove derived profiling artifacts (`*.prof`, `benchmark_*.csv`, `profile_*.txt`)
3. Clear agent execution logs (`.ai/debug-log.md` contents - keep directory structure)
4. Delete one-off migration scripts (unless promoting to Infrastructure as Code)
5. Remove prototype/experiment code (or promote to source of truth)
6. Verify no generated test media committed (`media/test/` is gitignored)
7. **Pre-commit hook will automatically block** ephemeral artifacts

**Command Sequence**:
```bash
# Review status
git status

# Delete ephemeral artifacts (adjust patterns as needed)
rm debug_*.py test_*.py *.prof profile_*.txt benchmark_*.csv 2>/dev/null
rm -rf media/test/* media/temp/* 2>/dev/null
echo "" > .ai/debug-log.md 2>/dev/null

# Verify cleanup
git status

# Attempt commit (pre-commit hook will block if artifacts remain)
git add -u
git commit -m "chore: Remove ephemeral development artifacts"
```

#### Source of Truth vs. Ephemeral Artifacts

**Track in Repository (Source of Truth)**:
- Infrastructure as Code / Setup automation (`setup_env.sh`, `manage.py`)
- Tracked source code (`samplify/`, `apps/`, `handlers/`)
- Source code tests (`tests/test_*.py`)
- Canonical test fixtures (<1MB in `tests/fixtures/`)
- Documentation (`docs/`, `README.md`)
- Configuration templates (`.env.template`, `requirements.txt`)

**Ignore (Ephemeral - Can Be Regenerated)**:
- Debug scripts created during feature development
- Derived profiling artifacts and performance analysis files
- Agent execution logs and traces
- One-off migration scripts (unless promoted to Infrastructure as Code)
- Prototype/experiment code (unless promoted to source of truth)
- Generated test media files (>1MB - use gitignored `media/test/`)

**Decision Rule (Twelve-Factor App / Git Hygiene)**:
*"Can this be regenerated from source code or external systems?"*
- **No** → Track as source of truth
- **Yes** → Ignore as ephemeral artifact

#### Reference
See **docs/architecture/coding-standards.md - Development Artifact Lifecycle Management** for comprehensive guidelines and examples.
