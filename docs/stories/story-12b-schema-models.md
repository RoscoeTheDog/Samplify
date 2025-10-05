# Story 1.2B: Schema Models

### User Story
As a **developer**,
I want **Django models for schema configuration storage**,
So that **I can replace XML templates with database-backed schemas**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2A (File model), existing XML template system
- Technology: Django ORM, SQLite
- Follows pattern: Django model relationships (ForeignKey, ManyToMany)
- Touch points: Schema storage, XML handler logic

### Acceptance Criteria

**Functional Requirements:**
1. `Schema` model created with fields:
   - `name` (CharField, max_length=255, unique=True)
   - `description` (TextField, null=True, blank=True)
   - `is_active` (BooleanField, default=False)
   - `xml_source` (TextField, null=True, blank=True) - Stores original XML for export (NFR14)
   - `source_type` (CharField, choices=['web', 'imported'], default='web') - Tracks origin
   - `created_at` (DateTimeField, auto_now_add=True)
   - `updated_at` (DateTimeField, auto_now=True)
2. `SchemaRule` model created with fields:
   - `schema` (ForeignKey to Schema, on_delete=CASCADE)
   - `rule_type` (CharField, choices=['keyword', 'extension', 'media_type', 'attribute'])
   - `rule_value` (CharField, max_length=500)
   - `logic_operator` (CharField, choices=['AND', 'OR'], default='AND')
   - `priority` (IntegerField, default=0)
3. `SchemaTransformation` model created with fields:
   - `schema` (ForeignKey to Schema, on_delete=CASCADE)
   - `output_format` (CharField, max_length=50)
   - `sample_rate` (IntegerField, null=True, blank=True)
   - `bit_depth` (IntegerField, null=True, blank=True)
   - `normalize_db` (FloatField, null=True, blank=True)
4. `DirectoryMapping` model created with fields:
   - `schema` (ForeignKey to Schema, on_delete=CASCADE)
   - `input_path` (CharField, max_length=500)
   - `output_path` (CharField, max_length=500)
   - `is_watched` (BooleanField, default=False)

**Integration Requirements:**
5. All models support XML template migration (CR4 requirement)
6. Schema activation logic (only one active schema at a time)
7. Cascade deletion works correctly (delete schema → delete rules/transformations)
8. Models registered in Django admin for debugging
9. `xml_source` field stores complete XML for re-export (NFR14, FR18)
10. `source_type` field enables filtering by origin (web-created vs imported)
11. Database indexing on `name` and `source_type` for efficient querying

**Quality Requirements:**
12. Migrations apply successfully
13. Model relationships work correctly
14. Admin interface displays all fields properly (including xml_source and source_type)
15. Database queries execute efficiently
16. XML storage in `xml_source` field preserves formatting and special characters

### Technical Notes
- **Integration Approach:** Map XML template structure to relational database models
- **Existing Pattern Reference:** xml_handler.py logic, CR4 schema functionality
- **Key Constraints:** Must support all XML rule types (keyword, file type, AND/OR logic)
- **XML Storage Strategy:** Store complete XML in `xml_source` field for export/re-import (NFR14)
- **Database Indexing:** Index on `name`, `source_type`, `is_active` for efficient filtering

### Definition of Done
- [x] All schema models implemented
- [x] `xml_source` and `source_type` fields added to Schema model
- [x] Migrations created and applied
- [x] Database indexing configured
- [x] Models registered in admin interface
- [x] Relationships validated
- [x] XML storage tested (import → store → export round-trip)
- [x] Documentation updated with schema model structure including new fields

### Risk Assessment
- **Primary Risk:** Schema model design doesn't capture all XML template capabilities
- **Mitigation:** Review xml_handler.py thoroughly, validate against sample XML templates
- **Rollback:** Drop schema migrations, revert to XML templates

---
