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
        ├─ feature/story-1.0 ← Story implementation branches
        ├─ feature/story-1.1
        └─ feature/story-X.X
```

**Workflow**:
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

**Key Principles**:
- Stories implemented sequentially in dependency order
- Each merge to `dev` creates explicit checkpoint (`--no-ff` flag)
- Feature branches follow naming: `feature/story-X.X` or `feature/story-X.Xa`
- Agent authorized to merge completed stories to `dev`
- Human oversight merges `dev` → `master` at epic completion

**Reference**: See PRD requirements.md Development Workflow Requirements (DW1-DW6) for complete specification

---

## Git Branch Guard for Story Development

**CRITICAL**: Before starting any story implementation, development agents **MUST** verify/create the correct feature branch.

### Pre-Implementation Checklist

Development agents must execute this guard **BEFORE** reading story tasks:

1. **Extract story number** from assigned story file
   - Example: `story-12a-file-model-single-table-inheritance.md` → `1.2a`
   - Example: `story-10-repository-environment-foundation.md` → `1.0`

2. **Determine expected feature branch**
   - Pattern: `feature/story-{number}`
   - Example: `feature/story-1.2a`
   - Example: `feature/story-1.0`

3. **Check current branch**
   ```bash
   git branch --show-current
   ```

4. **Branch verification logic**:
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

```bash
# Scenario: Agent assigned story-12a, currently on dev branch

# Step 1: Extract story number
story_number="1.2a"  # From story-12a-file-model-single-table-inheritance.md

# Step 2: Check current branch
current_branch=$(git branch --show-current)
# Output: dev

# Step 3: Wrong branch detected, check if feature branch exists
git branch --list feature/story-1.2a
# Output: (empty - doesn't exist)

# Step 4: Create feature branch from dev
git checkout -b feature/story-1.2a dev
# Output: Switched to a new branch 'feature/story-1.2a'

# Step 5: Inform user
echo "Created and switched to new feature/story-1.2a branch from dev"

# Step 6: Proceed with story implementation
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
