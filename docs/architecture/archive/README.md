# Architecture Archive

This directory contains superseded architecture documentation files that have been replaced by sharded versions.

## Archived Files

### coding-standards.md
- **Archived**: 2025-10-05
- **Reason**: File exceeded token limits (28KB / 3,554 lines) preventing developer agents from loading it
- **Replaced by**: `docs/architecture/coding-standards/` (19 sharded files)
- **Status**: ⚠️ DO NOT USE - Reference sharded version in `coding-standards/index.md`

## Why Archive Instead of Delete?

Archived files are kept for:
- Historical reference
- Comparison with sharded versions
- Recovery if needed during transition period

## Using Sharded Documents

**For coding standards**, use:
- **Index**: `docs/architecture/coding-standards/index.md` - Navigation hub
- **Load contextually**: Load specific shards as needed (e.g., `django-specific-patterns.md` when working on Django code)
- **Git workflow**: See `git-version-control.md` for branch guard requirements

---

**Status**: ✅ Archive maintained for historical reference only
