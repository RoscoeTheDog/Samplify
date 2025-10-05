# Story 1.13: Watchdog Control Panel UI

### User Story
As a **user**,
I want **toggle controls for file monitor and queue processor**,
So that **I can start/stop watchdog services from the web interface**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.7 (file monitor), Story 1.8 (queue processor)
- Technology: Django views/templates, AJAX for service control
- Follows pattern: UI wireframe (dual watchdog controls)
- Touch points: Management command lifecycle, service status

### Acceptance Criteria

**Functional Requirements:**
1. File Monitor toggle button (ON/OFF states)
2. Queue Processor toggle button (ON/OFF states)
3. Status indicators:
   - ●ON (green dot, service running)
   - ●OFF (red dot, service stopped)
4. Toggle button starts/stops Django management commands:
   - File Monitor: `manage.py file_monitor` (subprocess)
   - Queue Processor: `manage.py queue_processor` (subprocess)
5. Service status persisted (survives page refresh)
6. Toggle disabled while service starting/stopping (loading state)

**Integration Requirements:**
7. Integrates with file_monitor command (Story 1.7)
8. Integrates with queue_processor command (Story 1.8)
9. AJAX endpoints for start/stop/status operations
10. Subprocess management for background services

**Quality Requirements:**
11. Service start/stop works reliably
12. Status indicators update in real-time (AJAX polling)
13. Services restart after Django restart (if enabled)
14. Graceful shutdown on service stop (SIGTERM)

### Technical Notes
- **Integration Approach:** AJAX controls trigger subprocess management
- **Existing Pattern Reference:** UI wireframe watchdog controls
- **Key Constraints:** Reliable subprocess lifecycle, status persistence

### Definition of Done
- [x] Watchdog control panel implemented
- [x] Start/stop functionality working
- [x] Status indicators accurate
- [x] Service persistence tested
- [x] Graceful shutdown verified
- [x] Documentation updated with watchdog control instructions

### Risk Assessment
- **Primary Risk:** Subprocess management unreliable (zombie processes)
- **Mitigation:** Proper signal handling, process monitoring, cleanup on shutdown
- **Rollback:** Manual management command execution

---
