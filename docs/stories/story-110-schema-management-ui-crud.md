# Story 1.10: Schema Management UI (CRUD)

### User Story
As a **user**,
I want **a web interface to create, read, update, and delete schemas**,
So that **I can manage processing configurations without editing XML files**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (Schema models), Story 1.1 (Django templates)
- Technology: Django views/templates, forms, AJAX
- Follows pattern: Django CRUD pattern, progressive enhancement
- Touch points: Schema database, web UI

### Acceptance Criteria

**Functional Requirements:**
1. Schema list view displays all saved schemas
2. Schema create form includes:
   - Name (required, unique)
   - Description (optional)
   - Active status (checkbox)
3. Schema edit form allows modification of all fields
4. Schema delete confirms before removal (with cascade warning)
5. Only one schema can be active at a time (validation)
6. AJAX-based save/load operations (no page refresh)
7. Success/error messages displayed to user

**Integration Requirements:**
8. Integrates with Schema model (Story 1.2B)
9. Uses base template from Story 1.1
10. Static assets served locally (NFR3)
11. Progressive enhancement (works without JavaScript)

**Quality Requirements:**
12. Form validation prevents duplicate schema names
13. Active schema toggle works correctly (one active only)
14. Delete cascades to related rules/transformations
15. UI responsive and functional on modern browsers

### Technical Notes
- **Integration Approach:** Django class-based views, forms, AJAX enhancements
- **Existing Pattern Reference:** Django CRUD tutorial, NFR4 progressive enhancement
- **Key Constraints:** Browser-based UI, no authentication (NFR13)

### Definition of Done
- [x] Schema CRUD views implemented
- [x] Forms validated and working
- [x] AJAX save/load functional
- [x] Delete cascade verified
- [x] UI tested on Chrome/Firefox/Edge
- [x] Documentation updated with schema management instructions

### Risk Assessment
- **Primary Risk:** UI doesn't support all schema features (CR4)
- **Mitigation:** Validate against imported XML templates, comprehensive testing
- **Rollback:** Revert to XML template editing

---
