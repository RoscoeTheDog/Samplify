# Development Artifact Lifecycle Management

### Core Principle (Industry Best Practice)

> **Heuristic**: *"Ignore what can be regenerated or is ephemeral vs. track what represents a source of truth"*
>
> — Git Repository Hygiene Standard (GitHub, Atlassian)

This section implements the **Twelve-Factor App** methodology (Factor #5: Build/Release/Run separation) and **Trunk-Based Development** practices for managing development artifacts throughout the feature branch lifecycle.

### Purpose and Scope

During development, agents create **ephemeral artifacts** for debugging, profiling, and iterative problem-solving. This section defines **what constitutes source of truth vs. ephemeral artifacts** and **when cleanup is required** to maintain a clean repository per **FR17** and **NFR15**.

---

### File Classification

#### Source of Truth (Track in Repository)

**1. Infrastructure as Code / Setup Automation**
- **Cannot be regenerated**: Setup logic is source of truth
- **Examples**: `setup_env.sh`, `setup_env.bat`, `manage.py`, installation scripts
- **Rule**: Track - these define project initialization

**2. Tracked Source Code**
- **Cannot be regenerated**: Core application logic
- **Examples**: All files in `samplify/`, `apps/`, `handlers/`, `database/`
- **Rule**: Always track with proper documentation

**3. Configuration Templates**
- **Cannot be regenerated**: Configuration structure and defaults
- **Examples**: `.gitignore`, `requirements.txt`, `settings.py`, `.env.template`
- **Rule**: Track templates, ignore runtime instances (`.env`)

**4. Permanent Test Fixtures**
- **Cannot be regenerated**: Canonical test data for repeatable tests
- **Location**: `tests/fixtures/`, documented in `tests/README.md`
- **Examples**: Sample audio files (<1MB), reference XML templates
- **Rule**: Track if <1MB and used across multiple tests

**5. Documentation**
- **Cannot be regenerated**: Architecture decisions, API contracts
- **Location**: `docs/`, `README.md`, inline docstrings
- **Rule**: Always track

**6. Build/Deployment Automation**
- **Cannot be regenerated**: CI/CD pipeline definitions, migrations
- **Examples**: Django migrations, GitHub Actions workflows, Docker configs
- **Rule**: Always track (these are Infrastructure as Code)

---

#### Ephemeral Artifacts (Ignore/Regenerate)

**1. Debug Scripts (Ephemeral Development Artifacts)**
- **Can be regenerated**: Created ad-hoc during feature development
- **Patterns**: `debug_*.py`, `test_*.py` (in root), `quick_test_*.py`, `scratch_*.py`
- **Examples**:
  - `debug_query.py` - Test database query during Story 1.2B
  - `test_ffmpeg_path.py` - Verify FFmpeg detection logic
  - `quick_profile.py` - Profile processing performance
- **Lifecycle**: Create in feature branch → Use during debugging → Delete before merge
- **Exception**: If broadly useful, refactor into source of truth (permanent test or utility)

**2. One-Off Migration/Setup Scripts (Usually Ephemeral)**
- **Can be regenerated**: Single-use data transformations
- **Examples**:
  - `migrate_old_db.py` - Migrate SQLAlchemy to Django ORM (Story 1.2A)
  - `fix_file_paths.py` - One-time path correction
  - `import_legacy_schemas.py` - Import old XML templates once
- **Lifecycle**: Create → Run once → Verify → Delete
- **Exception**: If repeatable across environments, promote to Infrastructure as Code

**3. Profiling Outputs (Derived Artifacts)**
- **Can be regenerated**: Re-run profiler on source code
- **Patterns**: `*.prof`, `profile_*.txt`, `benchmark_*.csv`
- **Examples**: `cProfile` output, line profiler results, memory snapshots
- **Lifecycle**: Generate → Analyze → Capture insights in docs/comments → Delete files

**4. Agent Execution Logs (Ephemeral)**
- **Can be regenerated**: Re-run agent on same task
- **Location**: `.ai/debug-log.md`, agent-specific trace files
- **Rule**: Keep during active development, clean before merge
- **Exception**: Keep `.ai/` directory structure, delete contents

**5. Test Media (Large, Generated)**
- **Can be regenerated**: Generate or download test files as needed
- **Location**: `media/test/`, `media/temp/`
- **Examples**: Large audio files (>1MB), video files for FFmpeg testing
- **Rule**: Use for local testing, never commit (see `.gitignore`)
- **Note**: Small canonical fixtures (<1MB) are source of truth → track in `tests/fixtures/`

**6. Prototype/Experiment Code (Ephemeral Exploration)**
- **Can be regenerated**: Ideas can be re-implemented if needed
- **Examples**: `prototype_batch_ui.py`, `experiment_async_processing.py`
- **Lifecycle**: Prototype → Decide (refactor into source OR delete)
- **Rule**: Either promote to source of truth or delete - no "maybe useful later" limbo

**7. Build Artifacts (Generated Outputs)**
- **Can be regenerated**: Re-run build from source code
- **Examples**: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `htmlcov/`
- **Rule**: `.gitignore` handles these - never manually commit

---

### Cleanup Timing and Workflow

#### During Feature Branch Development
**Allowed**: Keep all ephemeral artifacts during active development
- Debug scripts help iterative problem-solving
- Profiling outputs inform optimization decisions
- Test media files validate functionality

**Example**: Story 1.5 feature branch
```bash
feature/story-1.5/
├── samplify/processing/batch.py     # Source of truth ✅
├── tests/test_batch.py              # Source of truth ✅
├── debug_batch_queue.py             # Ephemeral artifact ❌ (delete before merge)
├── profile_workers.prof             # Derived artifact ❌ (delete before merge)
└── media/test/large_audio.wav       # Generated artifact ❌ (.gitignore handles)
```

#### Before Merging to `dev` (Trunk-Based Development Practice)
**Required**: Delete ALL ephemeral artifacts before creating merge commit

**Pre-Merge Cleanup Checklist**:
1. ✅ Delete debug scripts (`debug_*.py`, `test_*.py` in root)
2. ✅ Delete one-off migration scripts (unless promoting to Infrastructure as Code)
3. ✅ Delete profiling outputs (`*.prof`, benchmark files)
4. ✅ Clear agent execution logs (`.ai/debug-log.md` contents)
5. ✅ Remove generated test media from `media/test/`
6. ✅ Delete prototype code (or promote to source of truth)
7. ✅ Run `git status` - verify no untracked ephemeral artifacts
8. ✅ Review unstaged changes - ensure no WIP debug code
9. ✅ **Pre-commit hook will block** if ephemeral artifacts detected

**Command Sequence**:
```bash
# Review all files in feature branch
git status

# Delete ephemeral artifacts
rm debug_*.py test_*.py *.prof
rm -rf media/test/*
# Clear execution logs (keep directory structure)
echo "" > .ai/debug-log.md

# Verify cleanup
git status

# Commit cleanup (if needed)
git add -u
git commit -m "chore: Remove ephemeral development artifacts"

# Merge to dev (Trunk-Based Development practice)
git checkout dev
git merge --no-ff feature/story-X.X
```

#### On `dev` Branch (Integration Trunk)
**Rule**: No ephemeral artifacts allowed
- `dev` serves as trunk for integration/testing
- All merges must be clean per DW3 (Merge and Test Protocol)
- Human oversight reviews merge commits as quality checkpoints
- **Pre-commit hook enforces** artifact cleanup automatically

#### On `master` Branch (Release Trunk)
**Rule**: Absolutely no ephemeral artifacts
- `master` is stable production-ready code (source of truth)
- Only receives merges from `dev` when epic complete
- Release branches may be cut from `master` (Trunk-Based Development)

---

### Special Cases and Exceptions

#### Exception 1: Promoting Ephemeral → Source of Truth
**Scenario**: Debug script proves broadly useful across multiple stories

**Example**: `debug_schema_validation.py` used repeatedly

**Action** (Promotion Path):
1. Refactor into proper utility module
2. Add to appropriate location (`samplify/utils/`, `management/commands/`)
3. Add docstrings and type hints (CS3, CS2)
4. Add tests if non-trivial
5. Document in README or architecture docs
6. Commit as source of truth (can no longer be regenerated - contains business logic)

**Before** (Ephemeral):
```python
# debug_schema_validation.py (can be regenerated)
from apps.schemas.models import Schema
schema = Schema.objects.get(id=1)
print(schema.validate())
```

**After** (Source of Truth):
```python
# samplify/management/commands/validate_schema.py (cannot be regenerated)
class Command(BaseCommand):
    """Validate schema configuration for debugging."""
    def handle(self, *args, **options):
        # Proper implementation with error handling
        pass
```

#### Exception 2: Test Fixtures for CI/CD
**Scenario**: Need test media for automated tests

**Rule**: Keep small (<1MB), representative files in `tests/fixtures/`

**Example**:
```
tests/fixtures/
├── audio/
│   ├── sample_16bit_44100.wav    # 500KB, various formats
│   ├── sample_24bit_96000.flac   # 800KB
│   └── README.md                 # Documents fixtures
├── video/
│   └── sample_h264.mp4           # 900KB
└── images/
    └── sample.jpg                # 100KB
```

**Large files**: Never commit - use local `media/test/` (gitignored)

#### Exception 3: Agent Debug Logs for Critical Issues
**Scenario**: Complex bug requiring detailed trace across multiple sessions

**Action**:
1. Keep `.ai/debug-log.md` during investigation
2. Extract key insights into code comments or docs
3. Delete detailed log before merge
4. If issue remains unresolved, summarize in GitHub issue/ticket

---

### Agent-Specific Guidelines

#### Development Agent (Dev)
**Responsibilities**:
- Create ephemeral artifacts as needed during feature work
- Track which files are ephemeral (mental note or comment in file header)
- Run cleanup checklist before merging to `dev`
- Verify `git status` shows no ephemeral artifacts before merge commit
- Pre-commit hook will enforce cleanup automatically

**Common Ephemeral Artifacts**:
- `debug_*.py` - Quick database queries, API tests (can be regenerated)
- `test_*.py` (in root) - Fast iteration tests (not source of truth test suite)
- `*.prof` - Performance profiling outputs (derived from source code)
- `.ai/debug-log.md` - Agent execution traces (can be regenerated)

#### PM Agent (John)
**Responsibilities**:
- Not responsible for cleanup (read-only role)
- May reference ephemeral artifacts in story acceptance criteria during development
- Reviews merge commits to `dev` - should not see ephemeral artifacts

#### Architect Agent
**Responsibilities**:
- May create ephemeral architecture validation scripts
- Design prototypes should be promoted to source of truth OR deleted (no limbo state)
- Cleanup before merging architecture docs

---

### Integration with Existing Workflows

#### Story Definition of Done (DoD)
**Add to checklist** (references `.bmad-core/checklists/story-dod-checklist.md`):
- [ ] All ephemeral debug scripts deleted
- [ ] Agent execution logs cleared
- [ ] Profiling/benchmark outputs removed
- [ ] Only source of truth files remain in feature branch
- [ ] `git status` clean before merge to `dev`

#### Pre-Commit Checklist (CS Section)
**Add to existing checklist**:
- [ ] No ephemeral artifacts in commit (`debug_*.py`, `*.prof`, `test_*.py` in root)
- [ ] `.ai/debug-log.md` cleared (if exists)
- [ ] No one-off migration scripts (unless promoted to Infrastructure as Code)
- [ ] Pre-commit hook passes (automated enforcement)

#### Development Workflow Requirements (DW3)
**Reference**: PRD requirements.md DW3 - Merge and Test Protocol

**Enhancement**: Before merge to `dev` (Trunk-Based Development)
1. Run full test suite ✅ (existing)
2. **Cleanup ephemeral artifacts** ✅ (new requirement - NFR15)
3. Verify `git status` clean ✅ (new requirement)
4. Pre-commit hook enforcement ✅ (automated gate)
5. Create merge commit with `--no-ff` ✅ (existing)

---

### Common Patterns and Examples

#### Pattern 1: Ephemeral Debug Script
**Scenario**: Story 1.2B - File model queries slow

**Workflow**:
```python
# debug_slow_query.py (EPHEMERAL - feature/story-1.2b branch)
"""
Quick debug script to profile File.objects query performance.
Created: 2025-10-05 during Story 1.2B debugging
TODO: Delete before merge to dev (can be regenerated)
"""
from apps.catalog.models import File
import time

start = time.time()
files = File.objects.filter(media_type='audio').select_related('schema')
print(f"Query took {time.time() - start:.2f}s")
print(f"Found {files.count()} files")

# Result: Added select_related() to production code (batch.py:45)
# This file can be deleted now - insight captured in source of truth
```

**Resolution**:
- Insight captured in code comment: `# Query optimized with select_related() (see Story 1.2B debug)`
- Delete `debug_slow_query.py` before merge (ephemeral artifact)

#### Pattern 2: One-Off Migration Script
**Scenario**: Story 1.2A - Migrate SQLAlchemy to Django ORM

**Workflow**:
```python
# migrate_legacy_db.py (EVALUATE - ephemeral or source of truth?)
"""
Migrate data from old SQLAlchemy database to Django ORM.

DECISION POINT:
- If ONE-TIME migration: Delete (ephemeral - can be regenerated if needed)
- If REPEATABLE across environments: Promote to Infrastructure as Code (source of truth)
"""
from legacy_db import LegacySQLAlchemy
from apps.catalog.models import File

def migrate():
    # Migration logic
    pass

if __name__ == "__main__":
    migrate()
```

**Decision**:
- **Ephemeral**: Run on existing database → Delete after verification (one-time use)
- **Source of Truth**: Needed for fresh installations → Promote to Infrastructure as Code, add docs, commit

#### Pattern 3: Derived Profiling Artifacts
**Scenario**: Story 1.6 - Batch processing performance optimization

**Workflow**:
```bash
# Profile batch processing (generates ephemeral artifact)
python -m cProfile -o batch_profile.prof samplify/processing/batch.py

# Analyze (derived artifact - can be regenerated from source code)
python -m pstats batch_profile.prof
# (prints top time-consuming functions)

# RESULT: Identified bottleneck in File.save() - optimized with bulk_create()
# Capture insight in source of truth (code comment or architecture doc)
# DELETE batch_profile.prof before merge (ephemeral - can be regenerated)
```

**Resolution**:
- Optimization documented in source of truth: `# Uses bulk_create() for performance (50% faster, see Story 1.6 profiling)`
- Delete `batch_profile.prof` (derived artifact)

---

### Enforcement and Quality Gates

#### Automated Pre-Commit Hook (Implemented)
**Location**: `.git/hooks/pre-commit`

**Function**: Blocks commits containing ephemeral artifacts
- Checks for patterns: `debug_*.py`, `*.prof`, `test_*.py` (in root), etc.
- Validates `.ai/debug-log.md` is empty
- Provides remediation guidance
- Enforces "ignore what can be regenerated" principle

**Status**: ✅ Active - automated enforcement enabled

#### Manual Review Checkpoints
**Human oversight** (per DW6 - Agent Merge Responsibility):
- Review merge commits to `dev` for ephemeral artifacts (backup verification)
- Spot-check feature branches before epic completion
- Verify `.gitignore` patterns remain effective

#### Story Acceptance Criteria
**Every story DoD includes** (NFR15):
- No ephemeral debug scripts in final commit
- All insights from profiling/debugging captured in source of truth (code/docs)
- `git status` shows only intended changes
- Pre-commit hook passes

---

### Summary Quick Reference

| File Type | Keep in Feature Branch? | Track in Repo? | Rationale | Example |
|-----------|------------------------|----------------|-----------|---------|
| Debug scripts | ✅ Yes | ❌ Ignore | Can be regenerated | `debug_query.py` |
| One-off migrations | ✅ Yes | ⚠️ Evaluate | Ephemeral OR Infrastructure as Code | `migrate_old_db.py` |
| Profiling outputs | ✅ Yes | ❌ Ignore | Derived from source code | `*.prof`, `benchmark.csv` |
| Agent logs | ✅ Yes | ❌ Ignore | Can be regenerated | `.ai/debug-log.md` |
| Test media (large) | ✅ Yes (local) | ❌ Ignore | Can be generated/downloaded | `media/test/large.wav` |
| Setup automation | ✅ Yes | ✅ Track | Infrastructure as Code | `setup_env.sh` |
| Source code tests | ✅ Yes | ✅ Track | Cannot be regenerated | `tests/test_models.py` |
| Test fixtures (small) | ✅ Yes | ✅ Track | Canonical test data | `tests/fixtures/sample.wav` |
| Source code | ✅ Yes | ✅ Track | Cannot be regenerated | `samplify/batch.py` |

**Decision Rule (Twelve-Factor App / Git Hygiene)**:
*"Can this be regenerated from source code or external systems?"*
- **No** → Track as source of truth
- **Yes** → Ignore as ephemeral artifact

**Industry Reference**: GitHub `.gitignore` templates, Trunk-Based Development cleanup practices

---

**Version History**:
- **3.2** (2025-10-05): Added Temporary File Management section (NFR15 compliance)

---
