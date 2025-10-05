# Story 1.16: Complete Setup Script

### User Story
As a **user**,
I want **a single setup script that configures everything**,
So that **I can clone the repository and run the application without manual steps**.

### Story Context
**Existing System Integration:**
- Integrates with: All previous stories (foundation, Django, FFmpeg, database)
- Technology: Python setup script, shell scripts, pip
- Follows pattern: FR15/FR16 clone-to-run deployment
- Touch points: Installation, configuration, validation

### Acceptance Criteria

**Functional Requirements:**
1. `setup.py` script checks prerequisites:
   - Python 3.10+ installed
   - Git installed
   - Disk space (500 MB minimum for FFmpeg)
2. Script creates virtual environment (if not exists)
3. Script installs requirements from `requirements.txt`
4. Script runs FFmpeg detection/download (Story 1.4)
5. Script runs Django migrations (`manage.py migrate`)
6. Script runs health check:
   - Database accessible (WAL mode verified)
   - FFmpeg binary works
   - Static files collectible
   - Loguru configured correctly
7. Script reports success/failure with actionable messages
8. Script creates `.env` file from `.env.template` (if exists)

**Integration Requirements:**
9. Integrates with all infrastructure stories (1.0-1.4)
10. Uses FFmpeg service (Story 1.4)
11. Runs Django migrations (Story 1.2)
12. Validates all configurations (NFR5)

**Quality Requirements:**
13. Setup completes in <5 minutes on fresh system
14. Error messages are clear and actionable (FR16)
15. Script is idempotent (safe to run multiple times)
16. Cross-platform support (Windows/macOS/Linux)

### Technical Notes
- **Integration Approach:** Orchestrate all setup tasks in single script
- **Existing Pattern Reference:** FR15/FR16 clone-to-run, NFR11 prerequisites
- **Key Constraints:** Python 3.10+ and git only prerequisites

### Definition of Done
- [x] Setup script implemented
- [x] All checks and tasks functional
- [x] Health check validated
- [x] Error messages tested
- [x] Cross-platform tested (Windows/macOS/Linux)
- [x] Documentation updated with setup instructions

### Risk Assessment
- **Primary Risk:** Setup script fails on specific platforms
- **Mitigation:** Test on clean VMs (Windows/macOS/Linux), provide manual fallback
- **Rollback:** Manual installation instructions

---
