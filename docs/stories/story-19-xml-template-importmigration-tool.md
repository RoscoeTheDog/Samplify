# Story 1.9: XML Template Import/Migration Tool

### User Story
As a **user**,
I want **a tool to import existing XML templates into the database**,
So that **I can migrate from XML configuration to the web-based schema designer**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (Schema models), existing xml_handler.py logic
- Technology: Django management command, ElementTree for XML parsing
- Follows pattern: CR4 schema functionality preservation
- Touch points: XML template parsing, schema database population

### Acceptance Criteria

**Functional Requirements:**
1. XML import tool created as Django management command (`manage.py import_xml_template`)
2. Tool accepts XML template file path as argument
3. Tool parses XML template using ElementTree
4. Tool maps XML elements to Schema models:
   - Template name → Schema.name
   - Rules → SchemaRule records
   - Transformations → SchemaTransformation records
   - Directory mappings → DirectoryMapping records
5. Tool supports ALL XML rule types (CR4):
   - Keyword filters
   - File type filters
   - Media attribute filters
   - AND/OR logic governors
6. Tool validates imported schema (rules match XML exactly)
7. Tool provides detailed import report

**Integration Requirements:**
8. Integrates with Schema models (Story 1.2B)
9. Preserves all XML template functionality (CR4)
10. Validates against existing xml_handler.py logic
11. Creates database records atomically (transaction)

**Quality Requirements:**
12. Import succeeds for all existing XML templates
13. Imported schemas function identically to XML originals
14. Import errors provide actionable messages
15. Rollback works correctly on import failure

### Technical Notes
- **Integration Approach:** Parse XML, map to Django models, validate against CR4
- **Existing Pattern Reference:** xml_handler.py logic, CR4 schema requirements
- **Key Constraints:** MUST support all XML rule types, preserve exact functionality

### Definition of Done
- [x] XML import command implemented
- [x] All XML rule types supported
- [x] Import validated against sample templates
- [x] Import report generated
- [x] Transaction rollback tested
- [x] Documentation updated with XML migration guide

### Risk Assessment
- **Primary Risk:** XML import doesn't capture all template functionality (CR4 violation)
- **Mitigation:** Validate against xml_handler.py, test with all sample templates
- **Rollback:** Delete imported schema, restore XML template

---
