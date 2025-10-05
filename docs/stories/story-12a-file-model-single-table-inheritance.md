# Story 1.2A: File Model (Single-Table Inheritance)

### User Story
As a **developer**,
I want **a unified File model with single-table inheritance for media types**,
So that **I can eliminate redundant tables and simplify the ORM migration from SQLAlchemy**.

### Story Context
**Existing System Integration:**
- Integrates with: SQLAlchemy models (FilesVideo, FilesAudio, FilesImage)
- Technology: Django ORM, SQLite with WAL mode
- Follows pattern: Django single-table inheritance (media_type discriminator)
- Touch points: Database schema, existing SQLAlchemy models

### Acceptance Criteria

**Functional Requirements:**
1. `File` model created with single-table inheritance using `media_type` field
2. `media_type` choices: 'audio', 'video', 'image'
3. All metadata fields preserved from SQLAlchemy schema:
   - `file_path` (CharField, max_length=500)
   - `file_name` (CharField, max_length=255)
   - `file_format` (CharField, max_length=50)
   - `sample_rate` (IntegerField, null=True, blank=True)
   - `bit_depth` (IntegerField, null=True, blank=True)
   - `codec` (CharField, max_length=50, null=True, blank=True)
   - `file_size` (BigIntegerField)
   - `created_at` (DateTimeField, auto_now_add=True)
   - `updated_at` (DateTimeField, auto_now=True)
   - `media_type` (CharField, choices=['audio', 'video', 'image'])
4. Model includes `__str__()` method returning filename
5. Model includes `get_absolute_path()` method using `pathlib.Path`

**Integration Requirements:**
6. Django migration created successfully
7. SQLite database created with WAL mode enabled (defer to Story 1.2C)
8. No redundant tables created (single `catalog_file` table)
9. ORM queries work correctly for filtering by media_type

**Quality Requirements:**
10. Migration applies without errors
11. Model admin interface works (for debugging)
12. Database queries execute efficiently
13. All fields nullable/required as per original schema

### Technical Notes
- **Integration Approach:** Consolidate FilesVideo/Audio/Image into single File model
- **Existing Pattern Reference:** NFR12 single-table inheritance requirement
- **Key Constraints:** Must preserve all metadata fields, eliminate redundant tables

### Definition of Done
- [ ] File model implemented with media_type discriminator
- [ ] All SQLAlchemy fields mapped to Django ORM
- [ ] Migration created and applied successfully
- [ ] Model registered in admin interface
- [ ] Database schema validated (single table)
- [ ] Documentation updated with model structure

### Risk Assessment
- **Primary Risk:** Data migration complexity from SQLAlchemy to Django ORM
- **Mitigation:** Create migration scripts, test with sample data
- **Rollback:** Drop Django migrations, restore SQLAlchemy models

---
