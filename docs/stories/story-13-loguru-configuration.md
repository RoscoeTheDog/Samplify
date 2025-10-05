# Story 1.3: Loguru Configuration

### User Story
As a **developer**,
I want **the custom Loguru fork configured in Django settings**,
So that **I can migrate from structlog with hierarchical logging and IDE-clickable tracebacks**.

### Story Context
**Existing System Integration:**
- Integrates with: Existing structlog configuration, Django settings.py
- Technology: Custom Loguru fork, Django logging framework
- Follows pattern: NFR7 hierarchical logging requirement
- Touch points: All existing structlog statements, settings.py logging config

### Acceptance Criteria

**Functional Requirements:**
1. Custom Loguru fork installed and imported in `settings.py`
2. Loguru configured with:
   - Hierarchical logging (module.function.line format)
   - Global exception handling
   - Brief contextual messages
   - IDE-clickable file links in tracebacks
3. Log output format: `{time} | {level} | {name}:{function}:{line} - {message}`
4. Log levels configurable (DEBUG, INFO, WARNING, ERROR, CRITICAL)
5. Log rotation configured (10 MB per file, 5 files retention)
6. Console and file logging enabled

**Integration Requirements:**
7. Django startup logs use Loguru
8. Management commands use Loguru
9. View/model logs use Loguru
10. Multiprocessing workers use Loguru (process-safe)

**Quality Requirements:**
11. Log statements execute without errors
12. Tracebacks are clickable in PyCharm/VSCode
13. Log files rotate correctly
14. Performance impact is minimal (NFR7)

### Technical Notes
- **Integration Approach:** Replace structlog with Loguru fork, update all log statements
- **Existing Pattern Reference:** CR5 Loguru migration requirement, NFR7 logging config
- **Key Constraints:** Must maintain hierarchical style, preserve global exception handling

### Definition of Done
- [ ] Loguru fork installed and configured
- [ ] settings.py logging configuration complete
- [ ] Sample log statements tested
- [ ] Tracebacks verified as IDE-clickable
- [ ] Log rotation working
- [ ] Documentation updated with Loguru setup instructions

### Risk Assessment
- **Primary Risk:** Loguru migration breaks existing logging statements
- **Mitigation:** Create migration guide, update statements incrementally
- **Rollback:** Revert to structlog configuration

---
