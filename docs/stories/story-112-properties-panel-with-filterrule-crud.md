# Story 1.12: Properties Panel with Filter/Rule CRUD

### User Story
As a **user**,
I want **a properties panel to configure filters and processing rules**,
So that **I can define how files are processed without editing code**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (SchemaRule, SchemaTransformation models), Story 1.11 (directory tables)
- Technology: Django forms, JavaScript for dynamic fields
- Follows pattern: UI wireframe (properties panel)
- Touch points: SchemaRule/SchemaTransformation CRUD

### Acceptance Criteria

**Functional Requirements:**
1. Properties panel displays for selected input directory
2. Filters section with "Add Filter" button:
   - Keyword filter (text input)
   - Extension filter (dropdown: .wav, .mp3, .flac, .aiff, etc.)
   - Media type filter (dropdown: audio, video, image)
   - Attribute filter (sample rate, bit depth ranges)
3. Processing rules section with "Add Rule" button:
   - Output format (dropdown: WAV, MP3, FLAC)
   - Sample rate (dropdown: 44100, 48000, 96000, 192000)
   - Bit depth (dropdown: 16, 24, 32)
   - Normalize (slider: -12dB to 0dB)
4. Logic operator selector (AND/OR toggle)
5. Filter/rule removal buttons (per item)
6. Rules saved to database on change (auto-save)

**Integration Requirements:**
7. Integrates with SchemaRule model (Story 1.2B)
8. Integrates with SchemaTransformation model (Story 1.2B)
9. Uses selected directory from Story 1.11
10. Supports all XML rule types (CR4)

**Quality Requirements:**
11. Auto-save works without page refresh (AJAX)
12. Form validation prevents invalid rules
13. UI matches wireframe design
14. Dynamic fields responsive and accessible

### Technical Notes
- **Integration Approach:** Django forms, JavaScript dynamic fields, AJAX auto-save
- **Existing Pattern Reference:** UI wireframe properties panel, CR4 rule types
- **Key Constraints:** Must support all XML rule types, auto-save

### Definition of Done
- [ ] Properties panel implemented
- [ ] Filter CRUD functional
- [ ] Processing rule CRUD functional
- [ ] AND/OR logic selector working
- [ ] Auto-save tested
- [ ] Documentation updated with filter/rule configuration instructions

### Risk Assessment
- **Primary Risk:** UI doesn't support all filter/rule types (CR4)
- **Mitigation:** Validate against XML templates, comprehensive testing
- **Rollback:** Revert to XML configuration

---
