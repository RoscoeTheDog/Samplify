# Story 1.15: Dual Queue Visualization with UID Filtering

### User Story
As a **user**,
I want **dual queue tables with UID filtering**,
So that **I can preview input files and output destinations before batch processing**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.14 (AJAX endpoints), Story 1.5 (file scanning)
- Technology: Django templates, JavaScript/AJAX, DataTables (local)
- Follows pattern: UI wireframe (dual queue visualization)
- Touch points: File model, batch processing preview

### Acceptance Criteria

**Functional Requirements:**
1. Input queue table displays files from database:
   - Columns: Checkbox, UID, Filename, Path, Format, SR, BD, Size
   - Generated UID format: `#<hash[:4]>` (e.g., #a1f2)
2. Output queue table displays destinations:
   - Columns: Checkbox, UID, Filename, Destination, Format, SR, BD, Process
   - Process column shows transformation details (e.g., "Norm-6dB")
3. UID filter input field (comma-delimited: `#a1f2, #b3e4, #c5d6`)
4. Click input file → auto-filters output queue by UID
5. Multi-select (Ctrl+Click) → multiple UIDs in filter
6. Clear button (✕) shows all files
7. "Select All" checkbox, "Deselect Skipped" button
8. Real-time updates via AJAX polling (Story 1.14 endpoints)

**Integration Requirements:**
9. Integrates with File model (Story 1.2A)
10. Uses AJAX endpoints (Story 1.14)
11. JavaScript libraries served locally (NFR3)
12. Works without JavaScript (static HTML table fallback)

**Quality Requirements:**
13. Tables render 1000+ files smoothly (pagination if needed)
14. UID filtering responds instantly (<200ms)
15. AJAX updates don't disrupt user interaction
16. UI matches wireframe design exactly

### Technical Notes
- **Integration Approach:** Django templates, DataTables.js (local), AJAX polling
- **Existing Pattern Reference:** UI wireframe dual queue, NFR4 AJAX updates
- **Key Constraints:** Local JavaScript, 1000+ file performance

### Definition of Done
- [ ] Dual queue tables implemented
- [ ] UID filtering functional
- [ ] Click-to-filter working
- [ ] AJAX updates tested
- [ ] Performance validated (1000+ files)
- [ ] UI matches wireframe
- [ ] Documentation updated with queue visualization instructions

### Risk Assessment
- **Primary Risk:** Performance degrades with 1000+ files
- **Mitigation:** Pagination, virtual scrolling, efficient DOM updates
- **Rollback:** Simplify UI, remove real-time updates

---
