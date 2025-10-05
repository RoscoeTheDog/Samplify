# Story 1.14: AJAX Progress Monitoring Endpoints

### User Story
As a **developer**,
I want **JSON endpoints for real-time progress updates**,
So that **the UI can display batch processing status without page refresh**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.6 (batch processing), Story 1.15 (queue visualization)
- Technology: Django REST endpoints, AJAX polling
- Follows pattern: NFR4 progressive enhancement with AJAX
- Touch points: Batch processing status, queue updates

### Acceptance Criteria

**Functional Requirements:**
1. `/api/processing/status/` endpoint returns JSON:
   ```json
   {
     "status": "processing|idle|completed",
     "total_files": 245,
     "processed_files": 127,
     "failed_files": 3,
     "current_file": "kick_01.wav",
     "progress_percent": 51.8
   }
   ```
2. `/api/queue/files/` endpoint returns file list with metadata
3. `/api/queue/filter/<uid>/` endpoint returns filtered files by UID
4. Endpoints update every 1-2 seconds (NFR4 requirement)
5. Endpoints return 304 Not Modified when no changes (efficiency)

**Integration Requirements:**
6. Integrates with batch processing (Story 1.6)
7. Provides data for queue visualization (Story 1.15)
8. Uses File model (Story 1.2A) for file data
9. No authentication required (NFR13)

**Quality Requirements:**
10. Response time <100ms (low latency)
11. JSON format validated and consistent
12. Endpoints handle concurrent requests
13. Error responses are meaningful (500/404 handling)

### Technical Notes
- **Integration Approach:** Django JSON endpoints, polled via JavaScript
- **Existing Pattern Reference:** NFR4 AJAX polling, NFR11 real-time updates
- **Key Constraints:** 1-2 second polling interval, efficient responses

### Definition of Done
- [x] JSON endpoints implemented
- [x] Response format validated
- [x] Polling tested (1-2 second intervals)
- [x] 304 Not Modified optimization working
- [x] Error handling tested
- [x] Documentation updated with API endpoint details

### Risk Assessment
- **Primary Risk:** High polling frequency degrades performance
- **Mitigation:** Response caching, 304 Not Modified, efficient queries
- **Rollback:** Increase polling interval or disable real-time updates

---
