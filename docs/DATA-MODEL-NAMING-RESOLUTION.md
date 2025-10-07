# Data Model Naming Resolution

**Date:** 2025-10-06
**Issue:** Inconsistent model naming between implementation and story documentation
**Resolution:** Use **`DirectoryMapping`** as official model name
**Status:** ✅ Resolved

---

## Problem Summary

During retrospective PO review of Stories 1.0-1.8, discovered naming inconsistency:

- **Actual Implementation:** `DirectoryMapping` (apps/catalog/models.py:350)
- **Story Documentation:** `InputDirectory` (referenced in Stories 1.5, 1.7, 1.8)

This created confusion about which model name is correct and risked future development errors.

---

## Investigation

### Code Analysis
```bash
$ grep -rn "class.*Directory.*models.Model" apps/
apps/catalog/models.py:350:class DirectoryMapping(models.Model):
```

**Result:** Implemented model is `DirectoryMapping`

### Documentation Analysis
Stories referencing the incorrect `InputDirectory` name:
- Story 1.5 (File Scanning Service) - Dev Notes section
- Story 1.7 (File Monitor Watchdog) - Dev Notes section
- Story 1.8 (Queue Processor Watchdog) - Dev Notes section

Architecture docs also inconsistent:
- `docs/architecture/database-schema-design.md` - references `InputDirectory`

---

## Official Decision

**OFFICIAL MODEL NAME:** `DirectoryMapping`

**Rationale:**
1. Actual implementation uses `DirectoryMapping`
2. Code is working and tested (Stories 1.5-1.8 passing tests)
3. Less disruptive to update docs than refactor code
4. Name `DirectoryMapping` is more descriptive (maps input → output directories)

---

## Model Definition (Official)

```python
class DirectoryMapping(models.Model):
    """
    Maps input directories to output directories for file processing.
    Part of Schema configuration for file routing.
    """
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)
    input_path = models.CharField(max_length=500)
    output_path = models.CharField(max_length=500)
    is_watched = models.BooleanField(default=False)  # File monitor flag
    recursive = models.BooleanField(default=True)    # Recursive directory scanning

    class Meta:
        db_table = 'catalog_directorymapping'
        verbose_name = 'Directory Mapping'
        verbose_name_plural = 'Directory Mappings'

    def __str__(self):
        return f"{self.input_path} → {self.output_path}"
```

**Location:** `apps/catalog/models.py:350`

---

## Required Documentation Updates

### Stories Requiring Updates

**Story 1.5: File Scanning Service**
- [ ] Update "Dev Notes > Data Models" section
- [ ] Change `InputDirectory` → `DirectoryMapping`
- [ ] Update field references (`monitor_enabled` → `is_watched`)

**Story 1.7: File Monitor Watchdog**
- [ ] Update "Dev Notes > Data Models" section
- [ ] Change `InputDirectory` → `DirectoryMapping`
- [ ] Update AC references (`monitor_enabled` → `is_watched`)

**Story 1.8: Queue Processor Watchdog**
- [ ] Update "Dev Notes > Data Models" section
- [ ] Change `InputDirectory` → `DirectoryMapping`
- [ ] Update code examples to use correct model name

### Architecture Documents Requiring Updates

**docs/architecture/database-schema-design.md**
- [ ] Update model definition to `DirectoryMapping`
- [ ] Update all references to use consistent naming

---

## Field Name Clarifications

| Story References | Actual Field Name | Notes |
|------------------|-------------------|-------|
| `monitor_enabled` | `is_watched` | Boolean flag for file monitor (Story 1.7) |
| `recursive` | `recursive` | ✅ Correct |
| `path` | `input_path` | Input directory path |
| N/A | `output_path` | Output directory path (missing from some docs) |

---

## Implementation Checklist

- [x] **Verify actual model name in code** → `DirectoryMapping` confirmed
- [ ] **Update Story 1.5 documentation**
- [ ] **Update Story 1.7 documentation**
- [ ] **Update Story 1.8 documentation**
- [ ] **Update database-schema-design.md**
- [ ] **Add glossary entry to architecture docs**
- [ ] **Verify no other stories reference InputDirectory**

---

## Architecture Glossary Entry (To Add)

**File:** `docs/architecture/glossary.md` (create if doesn't exist)

```markdown
## Data Models

### DirectoryMapping
**Model Name:** `DirectoryMapping`
**Database Table:** `catalog_directorymapping`
**Purpose:** Maps input directories to output directories for file processing schema

**Common Aliases (INCORRECT - DO NOT USE):**
- ~~InputDirectory~~ (incorrect, used in early story drafts)
- ~~OutputDirectory~~ (incorrect, this is a field not a model)

**Key Fields:**
- `schema`: ForeignKey to Schema model
- `input_path`: Source directory path for file scanning
- `output_path`: Destination directory for processed files
- `is_watched`: Boolean flag for file monitor watchdog (Story 1.7)
- `recursive`: Boolean flag for recursive directory scanning

**Related Stories:**
- Story 1.2B: Schema Models (initial definition)
- Story 1.5: File Scanning Service (uses input_path)
- Story 1.7: File Monitor Watchdog (uses is_watched flag)
- Story 1.8: Queue Processor Watchdog (queries for pending files)
```

---

## Communication Plan

**Notification to Dev Team:**
```
🔔 Data Model Naming Update

Official model name confirmed: **DirectoryMapping** (not InputDirectory)

Action Required:
- Update any local references to "InputDirectory" → "DirectoryMapping"
- Use field name "is_watched" (not "monitor_enabled")
- See docs/DATA-MODEL-NAMING-RESOLUTION.md for details

Stories affected: 1.5, 1.7, 1.8
```

---

## Lessons Learned

1. **Root Cause:** Story 1.2B defined model but didn't clearly establish naming convention
2. **Prevention:** Always verify implemented model names before referencing in dependent stories
3. **Best Practice:** Create architecture glossary early in project to establish canonical names
4. **Process Improvement:** PO review should include data model consistency check

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-06 | Resolution document created, official model name confirmed | PO (Sarah) |
| 2025-10-06 | Documentation update checklist created | PO (Sarah) |

---

## References

- **Model Implementation:** `apps/catalog/models.py:350`
- **Story 1.2B:** Schema Models (original definition)
- **Sprint Change Proposal:** Retroactive Quality Assurance (Section 3, Critical Issue #2)
