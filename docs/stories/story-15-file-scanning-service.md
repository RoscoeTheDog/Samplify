# Story 1.5: File Scanning Service

### User Story
As a **developer**,
I want **a file scanning service that preserves existing algorithms**,
So that **I can populate the database with file metadata using proven logic**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.2A (File model), existing handlers/rules.py logic
- Technology: Django ORM, FFmpeg subprocess, pathlib
- Follows pattern: CR1 algorithm preservation requirement
- Touch points: handlers/rules.py search/filter algorithms, __main__.py lines 206-469

### Acceptance Criteria

**Functional Requirements:**
1. File scanning service created as Django management command (`scan_input`)
2. Service scans input directories specified in DirectoryMapping model
3. FFmpeg used to analyze media files (format, bit depth, sample rate, codec)
4. File metadata stored in File model (media_type auto-detected)
5. Algorithm preservation (CR1):
   - **PRESERVED EXACTLY**: Search/filter logic from handlers/rules.py
   - **PRESERVED EXACTLY**: Dispatch algorithms from __main__.py lines 206-469
   - **ALLOWED CHANGES**: Import statements (SQLAlchemy → Django ORM)
   - **ALLOWED CHANGES**: Method signatures for Django patterns
6. Service updates existing File records if file already in database
7. Service deletes File records if file no longer exists

**Integration Requirements:**
8. Service integrates with Story 1.4 (FFmpeg detection)
9. Service uses File model from Story 1.2A
10. Service accessible via Django admin or management command
11. Existing algorithm logic remains unchanged (CR1)

**Quality Requirements:**
12. Scanning completes within reasonable time (1000 files < 5 minutes)
13. FFmpeg analysis accuracy matches existing script (95%+ success rate)
14. Database updates are atomic (no partial records)
15. Error handling preserves existing behavior

### Technical Notes
- **Integration Approach:** Wrap existing algorithms in Django management command
- **Existing Pattern Reference:** CR1 algorithm preservation, handlers/rules.py
- **Key Constraints:** MUST preserve exact algorithm logic, only adapt for Django ORM

### Definition of Done
- [ ] File scanning service implemented
- [ ] Existing algorithms preserved exactly (CR1 validated)
- [ ] FFmpeg integration working
- [ ] Database population verified
- [ ] Management command tested
- [ ] Documentation updated with algorithm preservation details

### Risk Assessment
- **Primary Risk:** Algorithm modification breaks existing logic (CR1 violation)
- **Mitigation:** Code review focusing on CR1, side-by-side comparison with original
- **Rollback:** Restore exact original algorithm code

---
