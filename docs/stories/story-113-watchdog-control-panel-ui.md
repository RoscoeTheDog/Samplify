# Story 1.13: Watchdog Control Panel UI

## Status
**Approved**

---

## User Story
As a **user**,
I want **toggle controls for file monitor and queue processor**,
So that **I can start/stop watchdog services from the web interface**.

---

## Story Context
**Existing System Integration:**
- Integrates with: Story 1.7 (file monitor), Story 1.8 (queue processor)
- Technology: Django views/templates, AJAX for service control
- Follows pattern: UI wireframe (dual watchdog controls)
- Touch points: Management command lifecycle, service status

---

## Acceptance Criteria

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

---

## Tasks / Subtasks

- [ ] **Task 1: Create Django views for service control** (AC: 4, 7, 8, 9)
  - [ ] Create `samplify/views/watchdog_control.py`
  - [ ] Implement WatchdogControlView (displays control panel)
  - [ ] Implement start_service view (starts management command subprocess)
  - [ ] Implement stop_service view (stops subprocess gracefully)
  - [ ] Implement service_status view (returns JSON status)

- [ ] **Task 2: Implement subprocess management** (AC: 4, 10, 11, 14)
  - [ ] Use subprocess.Popen to start management commands
  - [ ] Store process PIDs in Django cache or database
  - [ ] Implement graceful shutdown (send SIGTERM, wait, then SIGKILL)
  - [ ] Handle process cleanup (prevent zombie processes)
  - [ ] Cross-platform signal handling (Windows/Unix)

- [ ] **Task 3: Create HTML template for control panel** (AC: 1, 2, 3)
  - [ ] Create `templates/watchdog/control_panel.html`
  - [ ] Add File Monitor toggle button with ON/OFF states
  - [ ] Add Queue Processor toggle button with ON/OFF states
  - [ ] Add status indicators (green/red dots)
  - [ ] Add loading state during service start/stop

- [ ] **Task 4: Implement AJAX toggle functionality** (AC: 1, 2, 6, 9)
  - [ ] Add JavaScript handlers for toggle buttons
  - [ ] Send AJAX POST to start/stop endpoints
  - [ ] Disable toggle during operation (loading state)
  - [ ] Update UI based on response (success/error)

- [ ] **Task 5: Implement real-time status polling** (AC: 3, 12)
  - [ ] Add AJAX polling (every 2 seconds) to check service status
  - [ ] Update status indicators (green/red dots) based on response
  - [ ] Display service uptime or last activity
  - [ ] Handle polling errors gracefully

- [ ] **Task 6: Implement service persistence** (AC: 5, 13)
  - [ ] Store service enabled/disabled state in database (ServiceStatus model)
  - [ ] On Django startup, check if services should be running
  - [ ] Auto-restart services if enabled (via startup signal)
  - [ ] Handle Django restart gracefully

- [ ] **Task 7: Add error handling and logging** (AC: 11, 14)
  - [ ] Log service start/stop events (loguru)
  - [ ] Handle subprocess errors (command not found, permission denied)
  - [ ] Display user-friendly error messages
  - [ ] Log PID and process status for debugging

- [ ] **Task 8: Testing** (AC: 11, 12, 13, 14)
  - [ ] Test start/stop functionality
  - [ ] Test graceful shutdown (SIGTERM handling)
  - [ ] Test service persistence across Django restarts
  - [ ] Test AJAX polling and status updates
  - [ ] Test error handling (process crashes, permissions)
  - [ ] Test on Windows (no SIGTERM, use taskkill)

---

## Dev Notes

### Previous Story Insights
**From Story 1.7 (File Monitor Watchdog):**
- Management command at `samplify/management/commands/file_monitor.py` [Source: Story 1.7 Dev Agent Record]
- Uses watchdog library to monitor directories
- Runs indefinitely until stopped (infinite loop with signal handling)

**From Story 1.8 (Queue Processor Watchdog):**
- Management command at `samplify/management/commands/queue_processor.py` [Source: Story 1.8 Dev Agent Record]
- Processes files from queue using multiprocessing
- Runs indefinitely until stopped (infinite loop with signal handling)

### File Locations (Source Tree)
**View Location:** [Source: architecture/source-tree.md]
```
samplify/
└── views/
    └── watchdog_control.py      # Create this file
```

**Template Location:**
```
templates/
└── watchdog/
    └── control_panel.html       # Create this file
```

**Static Assets Location:**
```
static/
└── js/
    └── watchdog_control.js      # Create this file (local JavaScript)
```

**Model Location (for persistence):**
```
apps/catalog/
└── models.py                    # Add ServiceStatus model
```

**Test Location:**
```
tests/
└── test_watchdog_control.py     # Create this file
```

### Data Models
**ServiceStatus Model (New):** [Source: this story requirements]
```python
class ServiceStatus(models.Model):
    SERVICE_CHOICES = [
        ('file_monitor', 'File Monitor'),
        ('queue_processor', 'Queue Processor'),
    ]

    service_name = models.CharField(max_length=50, choices=SERVICE_CHOICES, unique=True)
    is_enabled = models.BooleanField(default=False)
    is_running = models.BooleanField(default=False)
    process_pid = models.IntegerField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
```

### Implementation Patterns

**Subprocess Management Pattern (Cross-Platform):**
```python
import subprocess
import signal
import os
import sys
from django.core.cache import cache
from loguru import logger

def start_service(service_name):
    """Start Django management command as subprocess."""
    # Build command
    python_exe = sys.executable
    manage_py = os.path.join(os.getcwd(), 'manage.py')
    cmd = [python_exe, manage_py, service_name]

    # Start subprocess
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        )

        # Store PID for later control
        cache.set(f'{service_name}_pid', process.pid, timeout=None)
        logger.info(f"Started {service_name} with PID {process.pid}")

        return {'success': True, 'pid': process.pid}
    except Exception as e:
        logger.error(f"Failed to start {service_name}: {e}")
        return {'success': False, 'error': str(e)}

def stop_service(service_name):
    """Stop service gracefully using SIGTERM."""
    pid = cache.get(f'{service_name}_pid')

    if not pid:
        return {'success': False, 'error': 'Service not running'}

    try:
        if sys.platform == 'win32':
            # Windows: use taskkill
            subprocess.run(['taskkill', '/PID', str(pid), '/F'], check=True)
        else:
            # Unix: send SIGTERM, wait, then SIGKILL if needed
            os.kill(pid, signal.SIGTERM)
            # Wait up to 5 seconds for graceful shutdown
            import time
            for _ in range(50):
                try:
                    os.kill(pid, 0)  # Check if process exists
                    time.sleep(0.1)
                except OSError:
                    break  # Process terminated
            else:
                # Force kill if still running
                os.kill(pid, signal.SIGKILL)

        cache.delete(f'{service_name}_pid')
        logger.info(f"Stopped {service_name} (PID {pid})")
        return {'success': True}
    except Exception as e:
        logger.error(f"Failed to stop {service_name}: {e}")
        return {'success': False, 'error': str(e)}

def get_service_status(service_name):
    """Check if service is running."""
    pid = cache.get(f'{service_name}_pid')

    if not pid:
        return {'running': False}

    try:
        # Check if process exists
        if sys.platform == 'win32':
            result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], capture_output=True, text=True)
            running = str(pid) in result.stdout
        else:
            os.kill(pid, 0)  # Raises OSError if process doesn't exist
            running = True
    except (OSError, subprocess.CalledProcessError):
        running = False
        cache.delete(f'{service_name}_pid')

    return {'running': running, 'pid': pid if running else None}
```

**Django View Pattern (AJAX Endpoints):**
```python
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.catalog.models import ServiceStatus

class WatchdogControlView(TemplateView):
    template_name = 'watchdog/control_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file_monitor_status'] = get_service_status('file_monitor')
        context['queue_processor_status'] = get_service_status('queue_processor')
        return context

@require_POST
def start_service_view(request):
    """AJAX endpoint to start service."""
    service_name = request.POST.get('service_name')

    if service_name not in ['file_monitor', 'queue_processor']:
        return JsonResponse({'success': False, 'error': 'Invalid service name'}, status=400)

    result = start_service(service_name)

    # Update database
    if result['success']:
        ServiceStatus.objects.update_or_create(
            service_name=service_name,
            defaults={'is_enabled': True, 'is_running': True, 'process_pid': result['pid']}
        )

    return JsonResponse(result)

@require_POST
def stop_service_view(request):
    """AJAX endpoint to stop service."""
    service_name = request.POST.get('service_name')

    if service_name not in ['file_monitor', 'queue_processor']:
        return JsonResponse({'success': False, 'error': 'Invalid service name'}, status=400)

    result = stop_service(service_name)

    # Update database
    if result['success']:
        ServiceStatus.objects.update_or_create(
            service_name=service_name,
            defaults={'is_enabled': False, 'is_running': False, 'process_pid': None}
        )

    return JsonResponse(result)

def service_status_view(request):
    """AJAX endpoint to check service status."""
    file_monitor = get_service_status('file_monitor')
    queue_processor = get_service_status('queue_processor')

    return JsonResponse({
        'file_monitor': file_monitor,
        'queue_processor': queue_processor
    })
```

**JavaScript Control Panel (Local, NFR3):**
```javascript
// static/js/watchdog_control.js

// Poll service status every 2 seconds
setInterval(updateServiceStatus, 2000);

function updateServiceStatus() {
    fetch('/api/watchdog/status/')
        .then(response => response.json())
        .then(data => {
            updateIndicator('file-monitor', data.file_monitor.running);
            updateIndicator('queue-processor', data.queue_processor.running);
        });
}

function updateIndicator(serviceId, isRunning) {
    const indicator = document.getElementById(`${serviceId}-indicator`);
    const statusText = document.getElementById(`${serviceId}-status`);

    if (isRunning) {
        indicator.className = 'status-indicator running';
        statusText.textContent = 'ON';
    } else {
        indicator.className = 'status-indicator stopped';
        statusText.textContent = 'OFF';
    }
}

document.getElementById('file-monitor-toggle').addEventListener('click', function() {
    toggleService('file_monitor', this);
});

document.getElementById('queue-processor-toggle').addEventListener('click', function() {
    toggleService('queue_processor', this);
});

function toggleService(serviceName, button) {
    const isRunning = button.dataset.running === 'true';
    const action = isRunning ? 'stop' : 'start';

    // Disable button during operation
    button.disabled = true;
    button.textContent = 'Loading...';

    fetch(`/api/watchdog/${action}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCsrfToken()
        },
        body: `service_name=${serviceName}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.dataset.running = !isRunning;
            button.textContent = !isRunning ? 'Stop' : 'Start';
        } else {
            alert('Error: ' + data.error);
        }
    })
    .finally(() => {
        button.disabled = false;
        updateServiceStatus();  // Immediate status check
    });
}
```

**HTML Template Pattern:**
```html
<!-- templates/watchdog/control_panel.html -->
{% extends "base.html" %}

{% block content %}
<div class="watchdog-control-panel">
    <h3>Watchdog Services</h3>

    <!-- File Monitor Control -->
    <div class="service-control">
        <div class="service-header">
            <h4>File Monitor</h4>
            <span id="file-monitor-indicator" class="status-indicator {% if file_monitor_status.running %}running{% else %}stopped{% endif %}"></span>
            <span id="file-monitor-status">{% if file_monitor_status.running %}ON{% else %}OFF{% endif %}</span>
        </div>
        <button id="file-monitor-toggle" class="toggle-btn" data-running="{{ file_monitor_status.running|lower }}">
            {% if file_monitor_status.running %}Stop{% else %}Start{% endif %}
        </button>
    </div>

    <!-- Queue Processor Control -->
    <div class="service-control">
        <div class="service-header">
            <h4>Queue Processor</h4>
            <span id="queue-processor-indicator" class="status-indicator {% if queue_processor_status.running %}running{% else %}stopped{% endif %}"></span>
            <span id="queue-processor-status">{% if queue_processor_status.running %}ON{% else %}OFF{% endif %}</span>
        </div>
        <button id="queue-processor-toggle" class="toggle-btn" data-running="{{ queue_processor_status.running|lower }}">
            {% if queue_processor_status.running %}Stop{% else %}Start{% endif %}
        </button>
    </div>
</div>

<style>
.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 5px;
}
.status-indicator.running { background-color: #00ff00; }
.status-indicator.stopped { background-color: #ff0000; }
</style>

<script src="{% static 'js/watchdog_control.js' %}"></script>
{% endblock %}
```

### Service Persistence (Auto-restart)
**Django startup signal to restart services:** [Source: requirements AC 13]
```python
# apps/catalog/apps.py
from django.apps import AppConfig

class CatalogConfig(AppConfig):
    name = 'apps.catalog'

    def ready(self):
        # Import here to avoid circular imports
        from apps.catalog.models import ServiceStatus
        from samplify.views.watchdog_control import start_service

        # Check which services should be running
        for service in ServiceStatus.objects.filter(is_enabled=True):
            start_service(service.service_name)
```

### Preservation Rules
**NFR3 Compliance:** No CDN dependencies [Source: requirements.md NFR3]
- All JavaScript served from `static/js/` directory
- No external libraries for AJAX or UI

**NFR6 Compliance:** Cross-platform subprocess [Source: requirements.md NFR6]
- Use subprocess.Popen with platform-specific flags
- Windows: CREATE_NEW_PROCESS_GROUP, taskkill
- Unix: SIGTERM/SIGKILL signals

---

## Dev Notes > Testing

### Test File Location
[Source: architecture/testing-strategy.md]
```
tests/
└── test_watchdog_control.py
```

### Testing Standards
**Framework:** pytest + pytest-django [Source: architecture/tech-stack.md]

**Test Coverage Target:** 80%+ for watchdog control views [Source: architecture/testing-strategy.md]

**Test Categories:**
1. **Unit Tests - Subprocess Management**
   - Test start_service creates subprocess
   - Test stop_service sends SIGTERM (graceful)
   - Test stop_service sends SIGKILL (force)
   - Test get_service_status checks PID

2. **Integration Tests - AJAX Endpoints**
   - Test start_service_view returns success
   - Test stop_service_view returns success
   - Test service_status_view returns correct status
   - Test error handling (invalid service name)

3. **UI Tests - Toggle Controls**
   - Test toggle button changes state
   - Test status indicator updates
   - Test loading state during operation
   - Test AJAX polling updates UI

4. **Cross-Platform Tests**
   - Test subprocess on Windows (CREATE_NEW_PROCESS_GROUP, taskkill)
   - Test subprocess on Unix (SIGTERM, SIGKILL)
   - Test graceful shutdown on both platforms

**Example Test:**
```python
import pytest
from django.test import TestCase, Client
from apps.catalog.models import ServiceStatus
from samplify.views.watchdog_control import start_service, stop_service, get_service_status

class WatchdogControlTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_start_service_creates_subprocess(self):
        """Test starting service creates subprocess."""
        result = start_service('file_monitor')

        assert result['success'] == True
        assert result['pid'] is not None

        # Clean up
        stop_service('file_monitor')

    def test_stop_service_graceful_shutdown(self):
        """Test stopping service sends SIGTERM."""
        # Start service first
        start_service('file_monitor')

        # Stop service
        result = stop_service('file_monitor')

        assert result['success'] == True

        # Verify service stopped
        status = get_service_status('file_monitor')
        assert status['running'] == False

    def test_ajax_start_endpoint(self):
        """Test AJAX endpoint to start service."""
        response = self.client.post(
            '/api/watchdog/start/',
            data={'service_name': 'file_monitor'}
        )

        assert response.status_code == 200
        assert response.json()['success'] == True

        # Clean up
        stop_service('file_monitor')

    def test_service_persistence_across_restart(self):
        """Test service restarts if enabled."""
        # Enable service in database
        ServiceStatus.objects.create(
            service_name='file_monitor',
            is_enabled=True
        )

        # Simulate Django restart (call ready() method)
        from apps.catalog.apps import CatalogConfig
        app_config = CatalogConfig('apps.catalog', None)
        app_config.ready()

        # Verify service started
        status = get_service_status('file_monitor')
        assert status['running'] == True

        # Clean up
        stop_service('file_monitor')
```

**Running Tests:**
```bash
# Run watchdog control tests
pytest tests/test_watchdog_control.py -v

# Run with coverage
pytest tests/test_watchdog_control.py --cov=samplify.views.watchdog_control --cov-report=html

# Test graceful shutdown
pytest tests/test_watchdog_control.py::test_stop_service_graceful_shutdown -v
```

---

## Definition of Done
- [ ] Watchdog control panel implemented
- [ ] Start/stop functionality working
- [ ] Status indicators accurate
- [ ] Service persistence tested
- [ ] Graceful shutdown verified
- [ ] Documentation updated with watchdog control instructions

---

## Risk Assessment
- **Primary Risk:** Subprocess management unreliable (zombie processes)
- **Mitigation:** Proper signal handling, process monitoring, cleanup on shutdown
- **Rollback:** Manual management command execution

---

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-05 | 1.0 | Story completed by Scrum Master - added Status, Tasks, Dev Notes, Testing sections | SM (Bob) |

---

## Dev Agent Record

### Agent Model Used
(To be populated by dev agent during implementation)

### Debug Log References
(To be populated by dev agent during implementation)

### Completion Notes
(To be populated by dev agent during implementation)

### File List
(To be populated by dev agent during implementation)

---

## QA Results
(To be populated by QA agent after implementation)
