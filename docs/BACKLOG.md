# Product Backlog - Post-MVP Items

**Project:** Samplify - Django Web UI Modernization
**Product Owner:** Sarah (PO Agent)
**Last Updated:** 2025-10-06

---

## Purpose

This backlog tracks features, enhancements, and technical debt items **deferred from MVP** for future development. Items are prioritized but not scheduled for immediate implementation.

---

## Priority Levels

- **P1 - High:** Should address in next sprint after MVP
- **P2 - Medium:** Address within 2-3 sprints post-MVP
- **P3 - Low:** Nice-to-have, address when capacity permits
- **P4 - Deferred:** May revisit if user feedback indicates need

---

## Post-MVP Backlog Items

### P2 - Story 1.3.1: Resolve Loguru Exception Console Formatting (Issue #2)

**Status:** Deferred Post-MVP (PO Approved: 2025-10-06)
**Priority:** P2 - Medium
**Epic:** Epic 1 - Django Web UI Modernization
**Related Story:** Story 1.3 (Loguru Configuration)

**Description:**
Fix hierarchical console exception formatting in custom Loguru fork (Issue #2). Currently, `logger.exception()` shows "Logging error" on console instead of proper hierarchical traceback format. Exceptions ARE successfully logged to JSON file handler.

**Current Limitation:**
- **Impact:** 5% of logging use cases (exception tracebacks in console)
- **Workaround:** Review exception logs in JSON file (`logs/samplify.log`)
- **User Impact:** Low (developers can access exception details via JSON logs)

**Acceptance Criteria:**
1. `logger.exception()` displays hierarchical tree format in console (matching regular log messages)
2. Exception tracebacks render with proper formatting and colors
3. Console exception output matches JSON exception output
4. No "Logging error" messages in console
5. All 8 existing Loguru tests still pass
6. New test added for console exception formatting

**Technical Notes:**
- **Root Cause:** Loguru fork treats callable format functions as strings in exception code path
- **Existing Analysis:** See `loguru-fork-comprehensive-report.md` in Story 1.3 dev notes
- **Partial Fix:** WIP branch `fix/issue-2-callable-format-exception` exists in fork repo
- **Fork Repo:** https://github.com/RoscoeTheDog/loguru

**Effort Estimate:** 2-3 days (requires fork investigation and testing)

**Dependencies:**
- Access to Loguru fork repository
- Understanding of fork's hierarchical formatting implementation

**Acceptance Decision:**
- MVP can proceed without this fix (95% functionality acceptable)
- Post-MVP enhancement to improve developer experience
- Re-evaluate priority based on user feedback during MVP testing

**Created:** 2025-10-06 by PO (Sarah) during Story 1.3 retrospective review

---

## Backlog Management Process

### Adding New Items
1. Create entry with priority, description, AC
2. Link to related story/epic
3. Document reason for deferral
4. Add effort estimate if known

### Prioritization Criteria
- **P1:** Blocks key workflows or has significant user impact
- **P2:** Improves user experience or resolves known limitations
- **P3:** Minor enhancements or optimizations
- **P4:** Speculative features or low-value improvements

### Review Cadence
- **After MVP Launch:** Re-prioritize backlog based on user feedback
- **Monthly:** Review P1/P2 items for sprint planning
- **Quarterly:** Review P3/P4 items for potential removal

---

## Completed Post-MVP Items

(None yet - MVP not launched)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-06 | Backlog created, Story 1.3.1 added as first post-MVP item | PO (Sarah) |

---

## References

- **Story 1.3:** Loguru Configuration (95% functionality accepted)
- **Sprint Change Proposal:** Retroactive Quality Assurance (PO decisions)
- **Loguru Fork:** https://github.com/RoscoeTheDog/loguru
