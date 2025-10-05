# Story 1.6: Batch Processing Management Command

### User Story
As a **developer**,
I want **a batch processing management command that preserves multiprocessing patterns**,
So that **I can execute media transformations with proven performance characteristics**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.5 (scanning service), existing process_handler.py
- Technology: Python multiprocessing, Django management command, FFmpeg
- Follows pattern: CR2 multiprocessing orchestration preservation
- Touch points: handlers/process_handler.py worker scheduling, deque-based distribution

### Acceptance Criteria

**Functional Requirements:**
1. Batch processing command created (`manage.py batch_process`)
2. Multiprocessing preservation (CR2):
   - **PRESERVED EXACTLY**: Worker scheduling logic (process_handler.py lines 26-48)
   - **PRESERVED EXACTLY**: Deque-based job queue distribution
   - **PRESERVED EXACTLY**: One worker per CPU core allocation
   - **ALLOWED CHANGES**: Django ORM integration for file retrieval
3. Command accepts input directory and schema ID as arguments
4. Command retrieves files from database matching schema rules
5. Command distributes jobs to worker pool using existing deque pattern
6. Workers execute FFmpeg transformations using existing logic
7. Progress updates saved to database (for Story 1.14 AJAX polling)

**Integration Requirements:**
8. Integrates with File model (Story 1.2A)
9. Integrates with Schema models (Story 1.2B)
10. Integrates with FFmpeg service (Story 1.4)
11. Uses File scanning service (Story 1.5) for input

**Quality Requirements:**
12. Performance matches existing script (50-70% CPU utilization, NFR1)
13. Processing success rate matches existing (95%+ for common formats, NFR9)
14. Worker pool scales with CPU cores correctly
15. Deque distribution maintains load balancing

### Technical Notes
- **Integration Approach:** Wrap existing multiprocessing logic in Django management command
- **Existing Pattern Reference:** CR2 multiprocessing preservation, NFR1 performance
- **Key Constraints:** MUST preserve worker scheduling, deque patterns exactly

### Definition of Done
- [ ] Batch processing command implemented
- [ ] Multiprocessing patterns preserved exactly (CR2 validated)
- [ ] Performance benchmarked (matches NFR1)
- [ ] Worker pool verified (one per CPU core)
- [ ] Management command tested with sample files
- [ ] Documentation updated with multiprocessing details

### Risk Assessment
- **Primary Risk:** Multiprocessing modification degrades performance (CR2/NFR1 violation)
- **Mitigation:** Code review, performance benchmarking, side-by-side comparison
- **Rollback:** Restore exact original multiprocessing code

---
