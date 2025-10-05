# Git Workflow & Branching Strategy

**Version:** 1.0
**Last Updated:** 2025-10-04
**Purpose:** Git branching strategy, commit conventions, and merge procedures

---

## Overview

Samplify uses a hierarchical branching strategy to support parallel agent-based development while maintaining code quality and stability.

**Branch Hierarchy:**
```
master (production-ready releases)
  ↑
dev (integration workspace - all development happens here)
  ↑
feature/story-X.X-name (individual story branches)
```

**Key Principles:**
- `master` = production-ready code only
- `dev` = integration workspace for all stories
- Feature branches = isolated development per story
- All merges to `dev` must pass quality gates
- Only tested, complete work merges to `master`

---

## Branch Types

### Master Branch

**Purpose:** Production-ready releases only

**Rules:**
- ✅ Only merge from `dev` when release ready
- ✅ Must pass ALL tests (unit, integration, manual)
- ✅ Must meet ALL NFRs (performance, compatibility)
- ✅ Tagged with version numbers (v1.0.0, v1.1.0)
- ❌ Never commit directly to master
- ❌ Never merge incomplete features

**When to merge dev → master:**
- All Epic 1 stories complete (MVP ready)
- Integration testing passed (Story 1.17)
- Cross-platform validation complete
- Documentation complete

### Dev Branch

**Purpose:** Integration workspace for all development

**Rules:**
- ✅ Merge feature branches here
- ✅ All story work integrates here first
- ✅ Must maintain passing tests at all times
- ✅ Shared workspace for all developers/agents
- ❌ Never commit directly (use feature branches)
- ❌ Never break the build

**When to merge feature → dev:**
- Story acceptance criteria met
- All tests passing
- Code review checklist complete (CS1-CS13)
- Pre-merge checklist satisfied

### Feature Branches

**Purpose:** Isolated development for individual stories

**Naming Convention:**
```bash
feature/story-X.X-brief-name

Examples:
feature/story-1.0-repository-foundation
feature/story-1.1-django-setup
feature/story-1.2a-file-model
feature/story-1.4-ffmpeg-detection
```

**Rules:**
- ✅ One branch per story
- ✅ Branch from `dev` (not master)
- ✅ Keep branch focused on story scope
- ✅ Rebase on dev regularly
- ✅ Delete after merge to dev
- ❌ Don't mix multiple stories
- ❌ Don't let branches go stale (>1 week)

---

## Workflow: Starting a New Story

### 1. Ensure Dev is Up-to-Date

```bash
# Switch to dev branch
git checkout dev

# Pull latest changes
git pull origin dev

# Verify you're on dev and it's clean
git status
# Should show: "On branch dev, nothing to commit, working tree clean"
```

### 2. Create Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/story-X.X-name

# Example for Story 1.0:
git checkout -b feature/story-1.0-repository-foundation

# Verify branch created
git branch
# Should show: * feature/story-1.0-repository-foundation
```

### 3. Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Verify activation
which python
# Should show path in venv directory
```

### 4. Read Story Documentation

```bash
# Read story file
cat docs/stories/story-1X-....md

# Review related architecture docs
ls docs/architecture/
```

### 5. Begin Implementation

- Follow story acceptance criteria
- Use implementation checklist
- Commit frequently (see commit conventions below)
- Run tests regularly

---

## Workflow: During Development

### Making Changes

```bash
# Make code changes
# ... edit files ...

# Check what changed
git status
git diff

# Stage changes
git add path/to/file.py

# Or stage all changes (use carefully)
git add .
```

### Committing Changes

**Use Conventional Commits format:**

```bash
git commit -m "feat(module): add feature description

- Detailed explanation of change
- Why this change was needed
- Any important implementation notes

Refs: Story X.X"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring (no behavior change)
- `docs`: Documentation changes
- `test`: Adding/updating tests
- `chore`: Maintenance (dependencies, config)
- `style`: Formatting (black, isort)

**Examples:**

```bash
# Feature commit
git commit -m "feat(catalog): add File model with single-table inheritance

- Implement media_type discriminator
- Add UID auto-generation in save()
- Include all brownfield metadata fields

Refs: Story 1.2A"

# Fix commit
git commit -m "fix(processing): handle missing FFmpeg binary gracefully

- Add FileNotFoundError handling
- Provide clear error message with download instructions

Refs: Story 1.4"

# Documentation commit
git commit -m "docs(architecture): add FFmpeg integration design

- Platform detection patterns
- Auto-download workflow
- Subprocess execution examples

Refs: Story 1.4"
```

### Syncing with Dev

**Important:** Regularly sync your feature branch with dev to avoid conflicts.

```bash
# While on feature branch
git fetch origin dev

# Rebase your changes on top of latest dev
git rebase origin/dev

# If conflicts occur:
# 1. Fix conflicts in files
# 2. git add <resolved-files>
# 3. git rebase --continue

# Push rebased branch (requires force push)
git push origin feature/story-X.X-name --force-with-lease
```

**When to sync:**
- Daily (if dev is active)
- Before opening PR/merge request
- When another story you depend on merges

---

## Workflow: Completing a Story

### 1. Pre-Merge Checklist

**Before merging, verify ALL items:**

- [ ] All acceptance criteria met
- [ ] Code follows CS1-CS13 standards
- [ ] All tests passing (`python manage.py test`)
- [ ] Black formatting applied (`black .`)
- [ ] Imports sorted (`isort .`)
- [ ] Pylint score ≥ 8.5 (`pylint apps/`)
- [ ] Mypy type checking passes (`mypy apps/`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] Documentation updated
- [ ] No TODO comments left
- [ ] No debug print statements

### 2. Final Sync with Dev

```bash
# Get latest dev changes
git checkout dev
git pull origin dev

# Switch back to feature branch
git checkout feature/story-X.X-name

# Rebase on latest dev
git rebase dev

# Run tests one final time
python manage.py test
```

### 3. Merge to Dev

**Option A: Fast-Forward Merge (Preferred)**

```bash
# Switch to dev
git checkout dev

# Merge feature branch (fast-forward)
git merge feature/story-X.X-name

# Verify tests still pass
python manage.py test

# Push to remote
git push origin dev
```

**Option B: Squash Merge (For messy history)**

```bash
# Switch to dev
git checkout dev

# Squash merge (combines all commits into one)
git merge --squash feature/story-X.X-name

# Create single commit with clean message
git commit -m "feat(story-1.X): implement story name

Complete implementation:
- Acceptance criteria 1
- Acceptance criteria 2
- Acceptance criteria 3

Refs: Story 1.X"

# Verify tests pass
python manage.py test

# Push to remote
git push origin dev
```

### 4. Clean Up Feature Branch

```bash
# Delete local feature branch
git branch -d feature/story-X.X-name

# Delete remote feature branch (if pushed)
git push origin --delete feature/story-X.X-name

# Verify deletion
git branch -a
# Should NOT show feature/story-X.X-name
```

### 5. Update Story Tracking

- [ ] Mark story as complete in tracking system
- [ ] Update `docs/stories/story-1X-....md` with completion notes
- [ ] Update `docs/architecture/` if design changed
- [ ] Update `README.md` if setup changed

---

## Workflow: Releasing to Master

**⚠️ Only after all Epic 1 stories complete!**

### 1. Verify Dev is Release-Ready

```bash
# Checkout dev
git checkout dev
git pull origin dev

# Run full test suite
python manage.py test

# Run integration tests (Story 1.17)
python manage.py test apps.integration_tests

# Verify all quality checks
black . --check
isort . --check
pylint apps/
mypy apps/
```

### 2. Create Release Branch (Optional)

```bash
# Create release branch for final testing
git checkout -b release/v1.0.0

# Perform final manual testing
# Update version numbers
# Update CHANGELOG.md

# Commit release prep
git commit -m "chore(release): prepare v1.0.0 release"
```

### 3. Merge to Master

```bash
# Switch to master
git checkout master
git pull origin master

# Merge dev (or release branch)
git merge dev

# Tag release
git tag -a v1.0.0 -m "Release v1.0.0 - Django UI Modernization MVP

Epic 1 Complete:
- Stories 1.0-1.17 implemented
- All acceptance criteria met
- Cross-platform testing passed
- Performance benchmarks met (NFR1: 50-70% CPU)"

# Push master and tags
git push origin master
git push origin --tags
```

### 4. Post-Release Cleanup

```bash
# Delete release branch if created
git branch -d release/v1.0.0

# Merge master back to dev (in case of hotfixes)
git checkout dev
git merge master
git push origin dev
```

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- **feat**: New feature
- **fix**: Bug fix
- **refactor**: Code change (no new behavior)
- **docs**: Documentation only
- **test**: Adding/updating tests
- **chore**: Maintenance (dependencies, build)
- **style**: Formatting (no code change)
- **perf**: Performance improvement

### Scope

Module or component affected:

- `catalog` - File/Schema models
- `processing` - Batch processing, FFmpeg
- `schemas` - Schema management
- `frontend` - Templates, JavaScript
- `api` - API endpoints
- `db` - Database migrations
- `config` - Settings, configuration
- `docs` - Documentation

### Subject

- Use imperative mood ("add" not "added")
- No period at end
- Max 72 characters
- Describe WHAT changed

### Body

- Explain WHY change was needed
- Describe HOW it was implemented
- Reference related issues/stories
- Use bullet points for multiple items
- Wrap at 80 characters

### Footer

- Reference story: `Refs: Story 1.X`
- Breaking changes: `BREAKING CHANGE: description`
- Closes issues: `Closes #123`

### Examples

**Good Commits:**

```bash
# Feature with context
git commit -m "feat(processing): add multiprocessing worker pool

- Implement deque-based job distribution (CR2 pattern)
- Spawn one worker per CPU core
- Preserve brownfield allocation logic

Refs: Story 1.6"

# Bug fix with explanation
git commit -m "fix(catalog): prevent duplicate UID generation

UIDs were occasionally duplicating under high concurrency.
Added database constraint and retry logic.

Refs: Story 1.2A
Closes #45"

# Documentation update
git commit -m "docs(api): add batch processing endpoint examples

- JSON request/response schemas
- Error handling patterns
- Polling interval recommendations

Refs: Story 1.14"
```

**Bad Commits:**

```bash
# Too vague
git commit -m "fix stuff"

# Missing context
git commit -m "update file model"

# Wrong tense
git commit -m "added new feature"

# Too long subject
git commit -m "feat(catalog): add comprehensive file model with single-table inheritance and metadata fields for audio, video, and images"
```

---

## Handling Merge Conflicts

### When Conflicts Occur

```bash
# During merge or rebase
git merge dev
# Auto-merging apps/catalog/models.py
# CONFLICT (content): Merge conflict in apps/catalog/models.py
```

### Resolving Conflicts

**1. Identify conflicted files:**
```bash
git status
# Unmerged paths:
#   both modified:   apps/catalog/models.py
```

**2. Open file and find conflict markers:**
```python
class File(models.Model):
<<<<<<< HEAD
    # Your changes
    media_type = models.CharField(max_length=10)
=======
    # Incoming changes from dev
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
>>>>>>> dev
```

**3. Resolve conflict (choose one or combine):**
```python
class File(models.Model):
    # Combined: keep both improvements
    media_type = models.CharField(
        max_length=20,  # From dev (increased length)
        choices=MEDIA_TYPES,  # From dev (validation)
        default='unknown'  # Your change
    )
```

**4. Mark as resolved:**
```bash
git add apps/catalog/models.py
```

**5. Continue merge/rebase:**
```bash
# If merging:
git commit -m "merge: resolve conflict in File model"

# If rebasing:
git rebase --continue
```

### Preventing Conflicts

- Sync with dev daily
- Keep feature branches short-lived
- Communicate with team about overlapping work
- Use modular code (less overlap)

---

## Best Practices

### DO:

✅ **Commit often** - Small, focused commits are easier to review and revert
✅ **Write descriptive messages** - Future you will thank you
✅ **Test before committing** - Ensure your code works
✅ **Sync with dev regularly** - Avoid large merge conflicts
✅ **Use feature branches** - Keep dev stable
✅ **Delete merged branches** - Keep repo clean
✅ **Follow coding standards** - Use pre-commit hooks
✅ **Reference stories in commits** - Traceability

### DON'T:

❌ **Commit directly to master** - Always use dev → master flow
❌ **Commit broken code** - Run tests first
❌ **Mix unrelated changes** - One commit = one logical change
❌ **Leave branches stale** - Merge or abandon within a week
❌ **Force push to dev/master** - Only force push feature branches
❌ **Commit secrets** - Use .env files (gitignored)
❌ **Skip pre-commit hooks** - They enforce standards
❌ **Use generic messages** - "fix bug" tells nothing

---

## Common Git Commands

### Branch Management

```bash
# List all branches
git branch -a

# Create branch
git checkout -b feature/name

# Switch branches
git checkout branch-name

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name

# Rename current branch
git branch -m new-name
```

### Viewing History

```bash
# View commit log
git log --oneline -10

# View log with graph
git log --oneline --graph --all

# View changes in commit
git show <commit-hash>

# View file history
git log --follow path/to/file.py

# Search commits
git log --grep="search term"
```

### Undoing Changes

```bash
# Discard uncommitted changes in file
git checkout -- path/to/file.py

# Unstage file (keep changes)
git reset HEAD path/to/file.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) ⚠️ DANGEROUS
git reset --hard HEAD~1

# Revert commit (creates new commit)
git revert <commit-hash>
```

### Stashing Changes

```bash
# Save uncommitted changes temporarily
git stash

# List stashes
git stash list

# Apply most recent stash
git stash apply

# Apply and remove stash
git stash pop

# Discard stash
git stash drop
```

### Remote Operations

```bash
# View remotes
git remote -v

# Fetch changes (don't merge)
git fetch origin

# Pull changes (fetch + merge)
git pull origin dev

# Push branch
git push origin branch-name

# Force push (feature branches only!)
git push origin branch-name --force-with-lease
```

---

## Git Configuration

### One-Time Setup

```bash
# Set user info
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default editor
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "vim"          # Vim

# Enable color output
git config --global color.ui auto

# Set default branch name
git config --global init.defaultBranch master

# Enable auto-prune on fetch
git config --global fetch.prune true
```

### Useful Aliases

Add to `~/.gitconfig`:

```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    lg = log --oneline --graph --all --decorate
    amend = commit --amend --no-edit
    undo = reset --soft HEAD~1
```

Usage:
```bash
git st              # git status
git co dev          # git checkout dev
git lg              # pretty log
git amend           # amend last commit
```

---

## Troubleshooting

### Problem: "Your branch has diverged"

**Cause:** Local and remote branches have different histories

**Solution:**
```bash
# Option 1: Rebase local on remote (recommended)
git pull --rebase origin branch-name

# Option 2: Force push local (feature branches only!)
git push origin branch-name --force-with-lease

# Option 3: Reset to remote
git reset --hard origin/branch-name
```

### Problem: Accidentally committed to wrong branch

**Solution:**
```bash
# 1. Create branch from current state
git branch feature/correct-branch

# 2. Reset current branch to before commit
git reset --hard HEAD~1

# 3. Switch to correct branch
git checkout feature/correct-branch
```

### Problem: Need to undo a merge

**Solution:**
```bash
# If merge not pushed yet
git reset --hard HEAD~1

# If merge already pushed
git revert -m 1 <merge-commit-hash>
```

### Problem: Committed sensitive data

**⚠️ URGENT FIX:**
```bash
# 1. Remove from repository
git rm --cached path/to/sensitive-file

# 2. Add to .gitignore
echo "path/to/sensitive-file" >> .gitignore

# 3. Commit removal
git commit -m "chore: remove sensitive data"

# 4. Push
git push origin branch-name

# 5. Rotate credentials immediately!
```

**Prevention:** Use `.env` files (already in `.gitignore`)

---

## GitHub/GitLab Integration (Optional)

### Pull Request Workflow

**If using GitHub/GitLab:**

1. **Push feature branch to remote:**
   ```bash
   git push origin feature/story-X.X-name
   ```

2. **Create Pull Request (PR):**
   - Go to GitHub/GitLab repository
   - Click "New Pull Request"
   - Base: `dev`, Compare: `feature/story-X.X-name`
   - Fill in PR template (if exists)

3. **PR Description Template:**
   ```markdown
   ## Story
   Story X.X: Brief Description

   ## Changes
   - Change 1
   - Change 2
   - Change 3

   ## Testing
   - [ ] Unit tests passing
   - [ ] Integration tests passing
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows CS1-CS13
   - [ ] Documentation updated
   - [ ] Pre-commit hooks pass
   - [ ] No breaking changes
   ```

4. **Review and Merge:**
   - Request review (if applicable)
   - Address feedback
   - Merge when approved

---

## Quick Reference

### Starting Story
```bash
git checkout dev
git pull origin dev
git checkout -b feature/story-X.X-name
source venv/bin/activate  # or venv\Scripts\activate
```

### During Development
```bash
# Check status
git status
git diff

# Commit
git add .
git commit -m "type(scope): description"

# Sync with dev
git fetch origin dev
git rebase origin/dev
```

### Completing Story
```bash
# Final checks
python manage.py test
black .
isort .
pylint apps/
mypy apps/

# Merge to dev
git checkout dev
git pull origin dev
git merge feature/story-X.X-name
python manage.py test
git push origin dev

# Cleanup
git branch -d feature/story-X.X-name
```

---

**Follow this workflow for consistent, high-quality development!** 🚀
