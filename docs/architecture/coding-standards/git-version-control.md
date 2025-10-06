# Git & Version Control

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
# ✅ In feature branch (e.g., feature/story-1.5)
git commit -m "WIP: Implementing OAuth integration (login works, logout pending)"

# Before merging to dev - squash
git rebase -i dev
```

#### Branch Strategy
**Pattern**: Follow project-defined Development Workflow Requirements (DW1-DW6 in PRD)

**Branch Hierarchy**:
```
original ← Read-only archive (tagged v0.1-pre-bmad)
   │
master ← Stable production releases
   │
   └─ dev ← Integration branch (sequential story merges)
        ├─ feature/story-1.0 ← Individual story branches
        ├─ feature/story-1.1
        └─ feature/story-1.2 ← Parent branch for story series
             ├─ feature/story-1.2a → merge to parent
             ├─ feature/story-1.2b → merge to parent
             └─ feature/story-1.2c → merge to parent
                  └─ When complete: merge parent → dev
```

**Workflow for Individual Stories** (e.g., 1.0, 1.1, 1.3):
```bash
# Create feature branch for story
git checkout dev
git pull origin dev
git checkout -b feature/story-1.0

# Implement story with atomic commits
git commit -m "feat(env): Add .gitignore configuration"
git push -u origin feature/story-1.0

# When story complete, merge to dev with explicit merge commit
git checkout dev
git merge --no-ff feature/story-1.0  # Creates checkpoint
git push origin dev

# Next story branches from updated dev
git checkout -b feature/story-1.1
```

**Workflow for Story Series** (e.g., 1.2A, 1.2B, 1.2C) - **MANDATORY HIERARCHICAL BRANCHING**:

**Detection Rule**: Story series identified by **letter suffix** (e.g., `story-1.2a`, `story-1.2b`)

**Linear Dependency Pattern**: Sub-stories typically have linear dependencies (1.2C depends on 1.2B, which depends on 1.2A). The parent branch acts as an **integration point** that accumulates work from each completed sub-story:

```
feature/story-1.2 (parent - accumulates sub-story work incrementally)
  ├─ feature/story-1.2a → [implement → test → merge to parent → DELETE BRANCH]
  ├─ feature/story-1.2b (from UPDATED parent with 1.2A) → [test → merge → DELETE]
  └─ feature/story-1.2c (from UPDATED parent with 1.2A+B) → [test → merge → DELETE]
       └─ When complete: merge parent → dev (contains all sub-story work)
```

**CRITICAL**: Always branch sub-stories from **parent**, never from previous sub-story branch. The parent branch contains all previously merged sub-story work.

```bash
# Step 1: Create parent branch first (from dev)
git checkout dev
git pull origin dev
git checkout -b feature/story-1.2
git push -u origin feature/story-1.2

# Step 2: Implement 1.2A
git checkout feature/story-1.2
git pull origin feature/story-1.2  # Get latest parent (empty initially)
git checkout -b feature/story-1.2a

# Implement sub-story (code, tests, docs)

# Commit and merge to parent
git add .
git commit -m "feat(story-1.2a): Sub-story description

Detailed changes:
- Change 1
- Change 2

Tests: X/X passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git checkout feature/story-1.2
git merge --no-ff feature/story-1.2a  # Parent now contains 1.2A work
git push origin feature/story-1.2
git branch -d feature/story-1.2a  # Clean up merged branch

# Step 3: Implement 1.2B (branches from UPDATED parent with 1.2A)
git checkout feature/story-1.2
git pull origin feature/story-1.2  # ← Gets 1.2A's work from parent!
git checkout -b feature/story-1.2b  # 1.2B now has 1.2A as base

# Implement, test, commit, merge to parent, delete branch
# (repeat pattern from Step 2)

# Step 4: Implement 1.2C (branches from UPDATED parent with 1.2A+1.2B)
git checkout feature/story-1.2
git pull origin feature/story-1.2  # ← Gets 1.2A+1.2B work from parent!
git checkout -b feature/story-1.2c  # 1.2C now has 1.2A+1.2B as base

# Implement, test, commit, merge to parent

# Step 5: When ALL sub-stories complete, merge parent to dev
git checkout dev
git pull origin dev
git merge --no-ff feature/story-1.2  # Contains all sub-story work
git push origin dev
```

**Why Hierarchical Branching for Series**:
- ✅ Maintains isolation of incomplete work (sub-stories don't affect dev)
- ✅ Enables incremental testing (each sub-story tested before merging)
- ✅ Provides clear audit trail (parent shows all sub-story merges)
- ✅ Allows pause/resume workflow (work on 1.2B while 1.2C pending)
- ✅ Prevents dev branch pollution (dev only gets complete feature sets)

**Key Principles**:
- Stories implemented sequentially in dependency order (DW2)
- Each merge to `dev` creates explicit checkpoint (`--no-ff` flag)
- Feature branches follow naming: `feature/story-X.X` or `feature/story-X.Xa`
- Agent authorized to merge completed stories to `dev` (DW6)
- Human oversight merges `dev` → `master` at epic completion

**Historical Exception**: Stories 1.2A and 1.2B were committed directly to `dev` during workflow learning phase (before hierarchical branching enforcement). No further exceptions granted.

**Reference**: See PRD requirements.md Development Workflow Requirements (DW1-DW6) for complete specification

---

## Git Branch Guard for Story Development

**CRITICAL**: Before starting any story implementation, development agents **MUST** verify/create the correct feature branch, including parent branches for story series.

### Pre-Implementation Checklist

Development agents must execute this guard **BEFORE** reading story tasks:

1. **Extract story number** from assigned story file
   - Example: `story-12a-file-model-single-table-inheritance.md` → `1.2a`
   - Example: `story-10-repository-environment-foundation.md` → `1.0`

2. **Detect if story is part of a series** (has letter suffix)
   - Pattern: `{number}{letter}` (e.g., `1.2a`, `1.2b`, `1.2c`)
   - Extract base number: `1.2a` → `1.2` (parent)
   - Extract full number: `1.2a` (sub-story)

3. **Determine expected feature branch(es)**:
   - **IF story has letter suffix** (series detected):
     - Parent branch: `feature/story-{base}` (e.g., `feature/story-1.2`)
     - Sub-story branch: `feature/story-{full}` (e.g., `feature/story-1.2a`)
   - **ELSE** (individual story):
     - Feature branch: `feature/story-{number}` (e.g., `feature/story-1.0`)

4. **Check current branch**
   ```bash
   git branch --show-current
   ```

5. **Branch verification logic**:

   **A. For Story Series (letter suffix detected)**:

   1. **Check if parent branch exists**:
      ```bash
      git branch --list feature/story-{base}
      ```

   2. **IF parent branch does NOT exist**:
      ```bash
      git checkout dev
      git pull origin dev
      git checkout -b feature/story-{base}
      ```
      - Inform user: "Created parent branch feature/story-{base} from dev"

   3. **Check if sub-story branch exists**:
      ```bash
      git branch --list feature/story-{full}
      ```

   4. **IF sub-story branch does NOT exist**:
      ```bash
      git checkout feature/story-{base}
      git pull origin feature/story-{base}  # CRITICAL: Get previous sub-story work!
      git checkout -b feature/story-{full}
      ```
      - Inform user: "Created sub-story branch feature/story-{full} from parent (includes previous sub-story work)"

   5. **IF on wrong branch**:
      ```bash
      git checkout feature/story-{full}
      ```
      - Inform user: "Switched to feature/story-{full} branch"

   **CRITICAL - Linear Dependencies**: Always branch sub-stories from **parent**, never from previous sub-story branch. Parent branch accumulates all merged sub-story work, ensuring linear dependencies (1.2C gets 1.2A+1.2B work by branching from updated parent).

   **B. For Individual Stories (no letter suffix)**:

   - **IF on correct feature branch**: Continue silently to story implementation
   - **IF on wrong branch**:
     - Check if feature branch exists:
       ```bash
       git branch --list feature/story-{number}
       ```
     - **IF feature branch exists**:
       ```bash
       git checkout feature/story-{number}
       ```
       - Inform user: "Switched to existing feature/story-{number} branch"
     - **IF feature branch does NOT exist**:
       ```bash
       git checkout -b feature/story-{number} dev
       ```
       - Inform user: "Created and switched to new feature/story-{number} branch from dev"
   - **IF unable to create/switch branches**: **HALT** and report error to user

### Workflow Integration

This branch guard enables:
- **Pause/Resume**: Work can be paused, dev branch checked out for other work, then resumed automatically
- **Multi-Session Safety**: Agent resumes work on correct branch even after restarts
- **DW1-DW6 Compliance**: Ensures feature isolation per git workflow requirements
- **Audit Trail**: Clear branch history per story

### Example Execution

**Scenario A: Individual Story (No Series)**
```bash
# Agent assigned story-10, currently on dev branch

# Step 1: Extract story number
story_number="1.0"  # From story-10-repository-environment-foundation.md

# Step 2: Detect series? No letter suffix → Individual story

# Step 3: Check current branch
current_branch=$(git branch --show-current)
# Output: dev

# Step 4: Check if feature branch exists
git branch --list feature/story-1.0
# Output: (empty - doesn't exist)

# Step 5: Create feature branch from dev
git checkout -b feature/story-1.0 dev
# Output: Switched to a new branch 'feature/story-1.0'

# Step 6: Inform user
echo "Created and switched to new feature/story-1.0 branch from dev"

# Step 7: Proceed with story implementation
```

**Scenario B: Story Series (Hierarchical Branching Required)**
```bash
# Agent assigned story-12a, currently on dev branch

# Step 1: Extract story number
story_number="1.2a"  # From story-12a-file-model-single-table-inheritance.md

# Step 2: Detect series? Letter suffix detected → Story series
base_number="1.2"  # Parent branch
full_number="1.2a"  # Sub-story branch

# Step 3: Check current branch
current_branch=$(git branch --show-current)
# Output: dev

# Step 4: Check if parent branch exists
git branch --list feature/story-1.2
# Output: (empty - doesn't exist)

# Step 5: Create parent branch from dev
git checkout dev
git pull origin dev
git checkout -b feature/story-1.2
# Output: Switched to a new branch 'feature/story-1.2'
echo "Created parent branch feature/story-1.2 from dev"

# Step 6: Check if sub-story branch exists
git branch --list feature/story-1.2a
# Output: (empty - doesn't exist)

# Step 7: Create sub-story branch from parent
git checkout feature/story-1.2
git pull origin feature/story-1.2  # Get any previous sub-story work (empty for 1.2a)
git checkout -b feature/story-1.2a
# Output: Switched to a new branch 'feature/story-1.2a'
echo "Created sub-story branch feature/story-1.2a from parent (includes previous sub-story work)"

# Step 8: Proceed with story implementation

# NOTE: For 1.2B, the parent will contain 1.2A's merged work
# NOTE: For 1.2C, the parent will contain 1.2A+1.2B's merged work
# This ensures linear dependencies are maintained
```

### Guard Placement

**Execute this guard**:
- ✅ **Before** reading story tasks
- ✅ At the start of `develop-story` command execution
- ✅ On agent activation when assigned a story
- ❌ **Not** during story validation (validation can happen on dev)
- ❌ **Not** during documentation/infrastructure changes (those stay on dev)

### Error Handling

**HALT execution if**:
- Git is not installed
- Repository is in detached HEAD state
- Merge conflicts prevent branch switch
- User lacks write permissions

**Inform user with clear error message**:
```
ERROR: Unable to switch to feature/story-1.2a branch
Current state: {git status output}
Action required: {specific fix needed}
```

---
