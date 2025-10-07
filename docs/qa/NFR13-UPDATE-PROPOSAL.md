# NFR13 Update Proposal

**Date**: 2025-10-06
**Author**: Winston (Architect)
**Status**: Awaiting PO Approval
**Related**: ADR-001 (Django Admin Framework Enablement)
**Tracking**: Remediation Story R1.1

---

## Current NFR13 Text (Line 67)

**Location**: `docs/prd/requirements.md:67`

```markdown
**NFR13**: The system shall disable Django's authentication middleware and user
management entirely, operating as an open local web interface without login
features, while maintaining CSRF protection
```

---

## Problem with Current Text

**Interpretation Ambiguity**:
- "Disable Django's authentication middleware entirely" conflicts with Stories 1.2A/1.2B AC requirements
- Story 1.2A AC#11: "Admin interface functional for File model CRUD operations"
- Story 1.2B AC#16: "Admin interface functional for Schema model operations"
- Django admin **requires** `django.contrib.auth` to function

**Real-World Impact**:
- Story 1.1 initially disabled admin (per NFR13)
- Stories 1.2A/1.2B could not meet AC without admin
- QA retroactively re-enabled admin as "developer tooling"
- No architectural documentation of decision (ADR-001 created to fix)

**Root Cause**:
NFR13 doesn't distinguish between:
- **End-user authentication**: Login required for users to process files (not wanted)
- **Developer tooling**: Django admin for database inspection (needed for development)

---

## Proposed NFR13 Text (Updated)

**Location**: `docs/prd/requirements.md:67`

```markdown
**NFR13: Open Local Interface**

The system shall provide an open local interface for **end-user media file
processing operations** (CLI commands, batch processing, file monitoring)
requiring no authentication or login.

**Scope**:
- ✅ **No end-user authentication**: Users process files via CLI without login
- ✅ **CSRF protection maintained**: Web UI protected against cross-site attacks
- ❌ **Django admin excluded from scope**: Admin framework is developer tooling,
  not end-user functionality (see ADR-001)

**Rationale**: End users interact via CLI commands or future desktop UI (Story
1.10+), never through Django admin. Admin serves as developer tooling for
database inspection, testing, and debugging—not as end-user authentication.

**Architectural Decision**: See ADR-001 (Django Admin Framework Enablement) for
detailed analysis of admin framework enablement decision.
```

---

## Change Summary

### What Changes:
1. **Title**: "NFR13" → "NFR13: Open Local Interface" (clearer heading)
2. **Scope Clarification**: Explicitly states what IS and ISN'T in scope
3. **Developer Tooling Exception**: Django admin excluded from "authentication" ban
4. **Rationale Added**: Explains intent behind requirement
5. **ADR Reference**: Links to architectural decision record

### What Stays the Same:
- ✅ No end-user authentication required
- ✅ CSRF protection maintained
- ✅ Open local interface for file processing
- ✅ CLI-based interaction model

### Key Additions:
- **"End-user media file processing operations"** - Scopes restriction to user-facing features
- **"Django admin excluded from scope"** - Resolves Story 1.2A/1.2B conflict
- **"Developer tooling"** - Clarifies admin is for developers, not end users
- **ADR-001 reference** - Points to detailed architectural analysis

---

## Impact Analysis

### Stories Affected:
- ✅ **Story 1.1**: NFR13 compliance now clear (admin allowed as dev tooling)
- ✅ **Story 1.2A**: AC#11 (admin functional) no longer conflicts with NFR13
- ✅ **Story 1.2B**: AC#16 (admin functional) no longer conflicts with NFR13
- ✅ **Future Stories**: Clear guidance on authentication scope

### Code Impact:
- ✅ **No code changes required** - Current implementation already correct
- ✅ **settings.py comments updated** - Reference ADR-001 (see below)
- ✅ **Story changelogs updated** - Document NFR13 clarification

### Process Impact:
- ✅ **Prevents future confusion** - Clear scope for "authentication"
- ✅ **Aligns with Django best practices** - Admin as developer tooling is standard
- ✅ **Documents decision** - ADR-001 provides full context

---

## Implementation Steps

### Step 1: PO Approval (30 minutes)
- [ ] Review this proposal with Product Owner
- [ ] Discuss alternatives (see ADR-001 Section "Alternatives Considered")
- [ ] Confirm NFR13 intent: "no end-user auth" vs "no Django framework"
- [ ] Approve updated text

### Step 2: Update requirements.md (5 minutes)
```bash
# Edit file
nano docs/prd/requirements.md

# Replace line 67 with proposed text above

# Commit
git add docs/prd/requirements.md
git commit -m "docs: Update NFR13 to clarify developer tooling scope (ADR-001)"
```

### Step 3: Update settings.py Comments (10 minutes)
**File**: `samplify/settings.py`

**Add before INSTALLED_APPS**:
```python
# ============================================================================
# Django Admin Framework Configuration
# ============================================================================
# ADR-001: Admin enabled as developer tooling (not end-user authentication)
#
# NFR13 "no authentication" applies to end-user workflows (CLI commands,
# batch processing, file monitoring), NOT to Django admin framework used by
# developers for database inspection and debugging.
#
# Rationale:
# - Stories 1.2A/1.2B require admin for AC compliance (AC#11, AC#16)
# - End users interact via CLI, not admin interface
# - Admin is standard Django developer tooling
# - No end-user authentication or login required for file processing
#
# See: docs/architecture/decisions/ADR-001-admin-framework.md
# See: docs/prd/requirements.md (NFR13: Open Local Interface)
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',      # Developer tooling (ADR-001)
    'django.contrib.auth',       # Required by admin
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.catalog',
    'samplify',
]
```

### Step 4: Update Story Changelogs (10 minutes)

**Story 1.1** (`docs/stories/story-11-django-project-setup-configuration.md`):
```markdown
| 2025-10-06 | 1.2 | **NFR13 CLARIFICATION**: Admin framework re-enabled per ADR-001 (developer tooling exception). See docs/architecture/decisions/ADR-001-admin-framework.md | Architect (Winston) |
```

**Story 1.2A** (`docs/stories/story-12a-file-model-single-table-inheritance.md`):
```markdown
| 2025-10-06 | 1.1 | **NFR13 CLARIFICATION**: AC#11 admin requirement no longer conflicts with NFR13 per ADR-001. See docs/prd/requirements.md NFR13 update. | Architect (Winston) |
```

**Story 1.2B** (`docs/stories/story-12b-schema-models.md`):
```markdown
| 2025-10-06 | 1.1 | **NFR13 CLARIFICATION**: AC#16 admin requirement no longer conflicts with NFR13 per ADR-001. See docs/prd/requirements.md NFR13 update. | Architect (Winston) |
```

### Step 5: Update ADR-001 Status (2 minutes)
**File**: `docs/architecture/decisions/ADR-001-admin-framework.md`

```markdown
**Status**: Accepted  # Change from "Proposed"
**Date**: 2025-10-06
**Approved By**: [Product Owner Name]
```

Update Changelog:
```markdown
| 2025-10-06 | 1.1 | Accepted by PO - NFR13 updated in requirements.md | Winston (Architect) |
```

---

## Validation Checklist

**After Implementation, Verify**:
- [ ] NFR13 in requirements.md updated with new text
- [ ] settings.py has ADR-001 reference comments
- [ ] Story 1.1 changelog references NFR13 clarification
- [ ] Story 1.2A changelog references NFR13 clarification
- [ ] Story 1.2B changelog references NFR13 clarification
- [ ] ADR-001 status changed to "Accepted"
- [ ] ADR index (README.md) updated
- [ ] All changes committed with clear messages
- [ ] Team notified in stand-up/Slack

---

## Alternative Proposals (If PO Prefers Different Approach)

### Alternative 1: Minimal Change (Quick Fix)

**If PO wants minimal disruption**:
```markdown
**NFR13**: The system shall disable Django's authentication middleware and user
management entirely for end-user operations, operating as an open local web
interface without login features, while maintaining CSRF protection.
(Django admin framework is excluded as developer tooling - see ADR-001)
```

**Pros**: Small change, preserves most original text
**Cons**: Less clear scope definition

---

### Alternative 2: Strict NFR13 (Disable Admin)

**If PO wants strict interpretation**:
- Update NFR13: Keep original text (no changes)
- Rework Stories 1.2A/1.2B: Remove admin AC requirements
- Use Django shell for database inspection
- **Impact**: Requires story rework, removes developer tooling

---

### Alternative 3: Environment-Based (Dev vs Prod)

**If PO wants admin only in development**:
```markdown
**NFR13**: The system shall disable Django's authentication middleware in
production deployments, enabling it only in DEBUG mode for developer tooling.
End-user operations require no login or authentication.
```

**Pros**: Clear dev/prod separation
**Cons**: Environment-specific behavior, migration complexity

---

## Approval Section

**Product Owner Decision**:
- [ ] **Option A**: Approve proposed NFR13 text (recommended)
- [ ] **Option B**: Choose Alternative 1 (minimal change)
- [ ] **Option C**: Choose Alternative 2 (strict NFR13, rework stories)
- [ ] **Option D**: Choose Alternative 3 (environment-based)
- [ ] **Option E**: Propose different text (specify below)

**PO Signature**: _________________________ Date: _____________

**Notes/Changes Requested**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## References

- **ADR-001**: `docs/architecture/decisions/ADR-001-admin-framework.md`
- **Remediation Story**: `docs/qa/REMEDIATION-BACKLOG.md` (R1.1)
- **QA Report**: `docs/qa/RETROACTIVE-QA-REPORT-1.1-1.2C.md`
- **Story 1.1**: `docs/stories/story-11-django-project-setup-configuration.md`
- **Story 1.2A**: `docs/stories/story-12a-file-model-single-table-inheritance.md`
- **Story 1.2B**: `docs/stories/story-12b-schema-models.md`

---

**Document Status**: Ready for PO Review
**Next Step**: Schedule 30-minute PO approval meeting
**After Approval**: Execute Steps 2-5 (30 minutes total)
