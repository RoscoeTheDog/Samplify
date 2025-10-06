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

### Status
**Ready for Review**

### Definition of Done
- [x] File scanning service implemented
- [x] Existing algorithms preserved exactly (CR1 validated)
- [x] FFmpeg integration working
- [x] Database population verified
- [x] Management command tested
- [x] Documentation updated with algorithm preservation details

### Risk Assessment
- **Primary Risk:** Algorithm modification breaks existing logic (CR1 violation)
- **Mitigation:** Code review focusing on CR1, side-by-side comparison with original
- **Rollback:** Restore exact original algorithm code

---

## Dev Agent Record

### Agent Model Used
- Model: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- Story Implementation Date: 2025-10-06

### Debug Log References
- No debug log entries required for this story

### Completion Notes
**Implementation Summary:**
- Created Django management command `scan_input` at samplify/management/commands/scan_input.py
- Ported 6 CR1-preserved algorithms from handlers/rules.py with exact preservation:
  - contains_expression() - regex pattern matching (lines 10-23)
  - contains_extensions() - file extension filtering (lines 26-42, preserved mysterious line 33)
  - between_datetime() - date range filtering (lines 45-72)
  - contains_video() - video stream detection (lines 75-85)
  - contains_audio() - audio stream detection (lines 88-98)
  - contains_image() - image stream detection (lines 101-111)
- Integrated FFmpeg metadata extraction using Story 1.4 utility
- Implemented atomic File model CRUD operations with upsert pattern
- Added comprehensive error handling and logging with loguru
- Created pytest test suite with 22 tests covering:
  - CR1 algorithm preservation validation
  - FFmpeg integration testing
  - File model CRUD operations
  - Database atomicity verification
  - Management command functionality

**CR1 Compliance:**
- All algorithms preserved EXACTLY as specified
- Only adaptations: SQLAlchemy → Django ORM attribute mappings
- Line 33 bug from brownfield preserved with inline comment for post-migration validation
- All 22 tests pass, validating CR1 preservation

**Test Results:**
- 22/22 tests passing
- Coverage: Algorithm preservation, FFmpeg integration, CRUD operations, atomicity
- Performance: Directory scanning tested with recursive traversal

### File List
**Created Files:**
- `samplify/management/__init__.py` - Management package initialization
- `samplify/management/commands/__init__.py` - Commands package initialization
- `samplify/management/commands/scan_input.py` - Main file scanning service (648 lines)
- `tests/test_file_scanning.py` - Comprehensive test suite (545 lines, 22 tests)
- `pytest.ini` - Pytest configuration for Django integration

**Modified Files:**
- None (clean implementation)

---

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Story implemented - file scanning service with CR1 algorithm preservation | Dev Agent (James) |

---
