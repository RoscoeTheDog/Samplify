# Story 1.9: XML Template Import/Export Tool

### User Story
As a **user**,
I want **tools to import existing XML templates into the database and export schemas as XML templates**,
So that **I can migrate from XML configuration to the web-based schema designer and share templates across systems**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (Schema models), Story 1.10 (Schema Management UI), existing xml_handler.py logic
- Technology: Django management command + API endpoints, ElementTree for XML parsing/generation
- Follows pattern: CR4 schema functionality preservation, FR18/NFR14 template import/export
- Touch points: XML template parsing, schema database population, UI Import/Export buttons

### Acceptance Criteria

**Import Functionality (FR18):**
1. XML import tool created as Django management command (`manage.py import_xml_template`)
2. Import API endpoint created for UI integration (`POST /api/schemas/import-xml/`)
3. Tool accepts XML template file path as argument (CLI) or file upload (API)
4. Tool parses XML template using ElementTree
5. Tool maps XML elements to Schema models:
   - Template name → Schema.name
   - Rules → SchemaRule records
   - Transformations → SchemaTransformation records
   - Directory mappings → DirectoryMapping records
6. Tool supports ALL XML rule types (CR4):
   - Keyword filters
   - File type filters
   - Media attribute filters
   - AND/OR logic governors
7. Tool validates imported schema (rules match XML exactly)
8. Tool provides detailed import report

**Export Functionality (FR18):**
9. XML export tool created as Django management command (`manage.py export_xml_template`)
10. Export API endpoint created for UI integration (`GET /api/schemas/{id}/export-xml/`)
11. Tool accepts schema ID as argument
12. Tool generates XML template from Schema model data
13. Tool preserves XML structure compatible with existing xml_handler.py
14. Exported XML can be re-imported without data loss
15. Export includes all schema components (rules, transformations, mappings)

**UI Integration (FR18):**
16. [Import XML] button added to Input Files table header
17. [Export XML] button added to Input Files table header
18. [Import XML] button added to Output Destinations table header
19. [Export XML] button added to Output Destinations table header
20. Import button triggers file upload dialog and calls import API
21. Export button downloads generated XML file to browser
22. Import/Export operations provide user feedback (success/error messages)

**Database Storage (NFR14):**
23. Imported XML templates stored in database with original XML preserved
24. Schema table includes xml_source field (TextField) for XML storage
25. Database indexing enabled for efficient template querying
26. Templates retrievable by name, date, or source type (imported vs web-created)

**Integration Requirements:**
27. Integrates with Schema models (Story 1.2B)
28. Preserves all XML template functionality (CR4)
29. Validates against existing xml_handler.py logic
30. Creates database records atomically (transaction)
31. UI buttons integrate with Schema Management UI (Story 1.10)

**Quality Requirements:**
32. Import succeeds for all existing XML templates
33. Imported schemas function identically to XML originals
34. Export → Import round-trip preserves all data
35. Import/Export errors provide actionable messages
36. Rollback works correctly on import failure
37. UI Import/Export buttons are intuitive and responsive

### Technical Notes
- **Integration Approach:** Parse XML (import), generate XML (export), map to/from Django models, validate against CR4
- **Existing Pattern Reference:** xml_handler.py logic, CR4 schema requirements
- **Key Constraints:** MUST support all XML rule types, preserve exact functionality, enable template sharing (FR18)
- **Database Design:** Add xml_source field to Schema model (NFR14) for XML preservation
- **API Design:** RESTful endpoints for import (POST with file upload) and export (GET with XML download)
- **UI Integration:** JavaScript handlers for Import/Export buttons, AJAX file upload, browser download

### Definition of Done
- [ ] XML import command implemented (CLI)
- [ ] XML export command implemented (CLI)
- [ ] Import API endpoint implemented (`POST /api/schemas/import-xml/`)
- [ ] Export API endpoint implemented (`GET /api/schemas/{id}/export-xml/`)
- [ ] All XML rule types supported (import and export)
- [ ] Import validated against sample templates
- [ ] Export → Import round-trip tested
- [ ] Import/Export report generated
- [ ] Transaction rollback tested
- [ ] UI Import/Export buttons added to Input Files table
- [ ] UI Import/Export buttons added to Output Destinations table
- [ ] JavaScript file upload/download handlers implemented
- [ ] Schema model updated with xml_source field (NFR14)
- [ ] Database migrations created and tested
- [ ] User feedback messages implemented (success/error)
- [ ] Documentation updated with XML import/export guide
- [ ] Template sharing workflow documented

### Risk Assessment
- **Primary Risk:** XML import doesn't capture all template functionality (CR4 violation)
- **Mitigation:** Validate against xml_handler.py, test with all sample templates
- **Secondary Risk:** Export → Import round-trip loses data or introduces errors
- **Mitigation:** Comprehensive round-trip testing, XML schema validation
- **UI Risk:** Import/Export buttons confuse users about which templates to use
- **Mitigation:** Clear button labels, tooltips, success/error messages
- **Rollback:** Delete imported schema, restore XML template, revert database changes

---
