# Story 1.8: Queue Processor Watchdog

### User Story
As a **developer**,
I want **a queue processor watchdog service**,
So that **I can automatically process files as they're added to the database by the file monitor**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.6 (batch processing), Story 1.7 (file monitor)
- Technology: Django management command, multiprocessing
- Follows pattern: Existing processing orchestration
- Touch points: Database queue polling, batch processing execution

### Acceptance Criteria

**Functional Requirements:**
1. Queue processor created as Django management command (`manage.py queue_processor`)
2. Service polls database for unprocessed files (status='pending')
3. Service executes batch processing for queued files
4. Service updates file status (pending → processing → completed/failed)
5. Service respects active schema configuration
6. Polling interval configurable (default: 5 seconds)
7. Service runs as background process (blocking command)

**Integration Requirements:**
8. Integrates with File model (Story 1.2A)
9. Integrates with batch processing (Story 1.6)
10. Coordinates with file monitor (Story 1.7)
11. Uses multiprocessing patterns from Story 1.6

**Quality Requirements:**
12. Processing starts within polling interval of file arrival
13. No race conditions with file monitor
14. Service stable during long-running operation
15. Graceful shutdown on interrupt (SIGINT/SIGTERM)

### Technical Notes
- **Integration Approach:** Polling-based queue processor, triggers batch processing
- **Existing Pattern Reference:** Watch mode processing orchestration
- **Key Constraints:** Must coordinate with file monitor without conflicts

### Definition of Done
- [ ] Queue processor command implemented
- [ ] Database polling working
- [ ] Batch processing integration verified
- [ ] Race conditions tested and resolved
- [ ] Long-running stability tested
- [ ] Documentation updated with queue processor details

### Risk Assessment
- **Primary Risk:** Race conditions between file monitor and queue processor
- **Mitigation:** Database locking, status field management, thorough testing
- **Rollback:** Disable queue processor, use manual batch processing

---
