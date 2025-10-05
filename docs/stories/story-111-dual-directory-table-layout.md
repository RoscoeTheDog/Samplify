# Story 1.11: Dual Directory Table Layout

### User Story
As a **user**,
I want **separate tables for input and output directories**,
So that **I can select folders and configure mappings visually**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.10 (Schema UI), Story 1.2B (DirectoryMapping model)
- Technology: Django templates, JavaScript for folder selection
- Follows pattern: UI wireframe (Option 1 - Horizontal Split)
- Touch points: DirectoryMapping CRUD, folder browser integration

### Acceptance Criteria

**Functional Requirements:**
1. Input directory table displays all input paths from DirectoryMapping
2. Output directory table displays all output paths from DirectoryMapping
3. "Add Folder" button opens native file browser dialog (JavaScript)
4. Folder selection checkboxes allow enable/disable per directory
5. Selected folder highlights in table (active state)
6. Folder removal button (with confirmation)
7. Directory paths displayed with truncation (long paths)
8. Table responsive to window resize

**Integration Requirements:**
9. Integrates with DirectoryMapping model (Story 1.2B)
10. Uses schema from Story 1.10 (active schema context)
11. JavaScript uses local libraries (NFR3)
12. Works without JavaScript (degraded experience)

**Quality Requirements:**
13. File browser works on Windows/macOS/Linux
14. Path handling uses pathlib (cross-platform, NFR6)
15. Table renders correctly with 10+ directories
16. UI matches wireframe design (horizontal split)

### Technical Notes
- **Integration Approach:** Django template tables, JavaScript file browser API
- **Existing Pattern Reference:** UI wireframe Option 1, NFR6 pathlib
- **Key Constraints:** Cross-platform file paths, local JavaScript

### Definition of Done
- [x] Input/output directory tables implemented
- [x] Add/remove folder functionality working
- [x] File browser dialog tested on all platforms
- [x] Checkbox selection functional
- [x] UI matches wireframe design
- [x] Documentation updated with directory management instructions

### Risk Assessment
- **Primary Risk:** File browser API inconsistent across platforms
- **Mitigation:** Test on Windows/macOS/Linux, provide fallback text input
- **Rollback:** Use text input for directory paths

---
