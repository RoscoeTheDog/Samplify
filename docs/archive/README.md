# Documentation Archive

**Purpose**: This directory contains archived **monolithic documentation** that has been **superseded by sharded versions**.

**Date Archived**: 2025-10-04
**Reason**: Documentation sharding completed - monolithic files replaced by modular structure

---

## Archived Files

### 1. `prd.md` (44KB, 797 lines)
**Superseded by**: `/docs/prd/` directory (9 files, 801 lines)

**Why archived**: The PRD was sharded into focused sections for better maintainability:
- `intro-project-analysis-and-context.md`
- `requirements.md`
- `user-interface-enhancement-goals.md`
- `technical-constraints-and-integration-requirements.md`
- `epic-and-story-structure.md`
- `next-steps.md`
- Plus: `index.md`, `table-of-contents.md`, `django-web-ui-modernization.md`

**Current reference**: See `/docs/prd/index.md` for navigation to active PRD sections

---

### 2. `architecture.md` (24KB, 509 lines)
**Superseded by**: `/docs/architecture/` directory (21 files, 8,455 lines)

**Why archived**: The architecture document was sharded and significantly expanded:
- Original brownfield analysis preserved
- Added comprehensive sections: tech-stack, testing-strategy, coding-standards
- Added detailed specs: database-schema-design, api-endpoints, frontend-components
- Added FFmpeg integration docs: ffmpeg-sources, ffmpeg-integration

**Current reference**: See `/docs/architecture/index.md` for navigation to active architecture docs

---

### 3. `stories.md` (54KB, 1,346 lines)
**Superseded by**: `/docs/stories/` directory (individual story files)

**Why archived**: Individual stories split into dedicated files for parallel development:
- `story-10-repository-environment-foundation.md`
- `story-11-django-project-setup-configuration.md`
- `story-12a-file-model-single-table-inheritance.md`
- `story-12b-schema-models.md`
- `story-12c-wal-configuration.md`
- ... (continues through Story 1.19)
- Plus: `epic-1-django-web-ui-modernization.md`, `index.md`

**Current reference**: See `/docs/stories/index.md` for navigation to active stories

---

## Archive Policy

These files are retained for:
- Historical comparison
- Rollback reference if needed
- Understanding documentation evolution

**If you need to reference archived content**:
1. Check the sharded version first (it's more current)
2. Only use archive for historical context
3. Never copy content from archive back to active docs without review

---

## Developer Guidance

**⚠️ DO NOT use archived files for development**

These files are preserved for historical reference only. All active development should reference the sharded versions in:
- `/docs/prd/`
- `/docs/architecture/`
- `/docs/stories/`

**Why sharding was done**:
1. **Modularity**: Developers can work on specific sections without merge conflicts
2. **Maintainability**: Smaller files are easier to review and update
3. **Navigation**: Focused files with clear purpose vs. monolithic scrolling
4. **Parallel work**: Multiple agents/developers can edit different sections simultaneously
5. **Version control**: Smaller diffs, clearer change history

---

**Last Updated**: 2025-10-04
**Maintained by**: PM Agent (John)
