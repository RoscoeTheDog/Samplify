# Story 1.15: Dual Queue Visualization with UID Filtering

## Status
**Approved**

---

## User Story
As a **user**,
I want **dual queue tables with UID filtering**,
So that **I can preview input files and output destinations before batch processing**.

---

## Story Context
**Existing System Integration:**
- Integrates with: Story 1.14 (AJAX endpoints), Story 1.5 (file scanning)
- Technology: Django templates, JavaScript/AJAX, DataTables (local)
- Follows pattern: UI wireframe (dual queue visualization)
- Touch points: File model, batch processing preview

---

## Acceptance Criteria

**Functional Requirements:**
1. Input queue table displays files from database:
   - Columns: Checkbox, UID, Filename, Path, Format, SR, BD, Size
   - Generated UID format: `#<hash[:4]>` (e.g., #a1f2)
2. Output queue table displays destinations:
   - Columns: Checkbox, UID, Filename, Destination, Format, SR, BD, Process
   - Process column shows transformation details (e.g., "Norm-6dB")
3. UID filter input field (comma-delimited: `#a1f2, #b3e4, #c5d6`)
4. Click input file → auto-filters output queue by UID
5. Multi-select (Ctrl+Click) → multiple UIDs in filter
6. Clear button (✕) shows all files
7. "Select All" checkbox, "Deselect Skipped" button
8. Real-time updates via AJAX polling (Story 1.14 endpoints)

**Integration Requirements:**
9. Integrates with File model (Story 1.2A)
10. Uses AJAX endpoints (Story 1.14)
11. JavaScript libraries served locally (NFR3)
12. Works without JavaScript (static HTML table fallback)

**Quality Requirements:**
13. Tables render 1000+ files smoothly (pagination if needed)
14. UID filtering responds instantly (<200ms)
15. AJAX updates don't disrupt user interaction
16. UI matches wireframe design exactly

---

## Tasks / Subtasks

- [ ] **Task 1: Create Django view for queue visualization** (AC: 1, 2, 9)
  - [ ] Create `samplify/views/queue_visualization.py`
  - [ ] Implement QueueVisualizationView (displays dual tables)
  - [ ] Query File model for input queue (pending status)
  - [ ] Query transformation mappings for output queue
  - [ ] Pass data to template context

- [ ] **Task 2: Create HTML templates for dual queue tables** (AC: 1, 2, 7, 16)
  - [ ] Create `templates/queue/queue_visualization.html`
  - [ ] Implement input queue table (checkbox, UID, filename, path, format, SR, BD, size)
  - [ ] Implement output queue table (checkbox, UID, filename, destination, format, SR, BD, process)
  - [ ] Add "Select All" checkbox and "Deselect Skipped" button
  - [ ] Match UI wireframe design

- [ ] **Task 3: Implement UID filtering functionality** (AC: 3, 4, 5, 6, 14)
  - [ ] Add UID filter input field (comma-delimited)
  - [ ] Add JavaScript handler for input file click (auto-populate filter)
  - [ ] Add Ctrl+Click handler for multi-select
  - [ ] Add clear button (✕) to reset filter
  - [ ] Filter output queue based on UID list (<200ms response)

- [ ] **Task 4: Integrate DataTables.js (local)** (AC: 11, 13)
  - [ ] Download and serve DataTables.js locally (no CDN, NFR3)
  - [ ] Initialize DataTables on queue tables
  - [ ] Configure pagination (100 rows per page)
  - [ ] Add search and sort functionality

- [ ] **Task 5: Implement AJAX real-time updates** (AC: 8, 10, 15)
  - [ ] Poll Story 1.14 endpoints every 2 seconds
  - [ ] Update table rows without full page refresh
  - [ ] Preserve user interaction state (scroll position, selections)
  - [ ] Handle new files and status changes

- [ ] **Task 6: Add UID generation and display** (AC: 1, 2)
  - [ ] Generate UID as hash of file path (first 4 chars)
  - [ ] Display UID with # prefix (#a1f2)
  - [ ] Make UID clickable for filtering

- [ ] **Task 7: Add progressive enhancement fallback** (AC: 12)
  - [ ] Render static HTML table without JavaScript
  - [ ] Form submission for filtering (non-AJAX)
  - [ ] Server-side pagination fallback

- [ ] **Task 8: Testing** (AC: 13, 14, 15, 16)
  - [ ] Test table rendering with 1000+ files
  - [ ] Test UID filtering performance (<200ms)
  - [ ] Test AJAX updates don't disrupt interaction
  - [ ] Test multi-select (Ctrl+Click)
  - [ ] Validate UI matches wireframe

---

## Dev Notes

### Previous Story Insights
**From Story 1.14 (AJAX Progress Monitoring Endpoints):**
- JSON endpoints at `/api/queue/files/` and `/api/queue/filter/<uid>/` [Source: Story 1.14 Dev Agent Record]
- Pagination support (100 files per page)
- 304 Not Modified optimization for efficiency

**From Story 1.2A (File Model):**
- File model tracks status (pending/processing/completed/failed) [Source: Story 1.2A]
- UID generated as hash of file_path

### File Locations (Source Tree)
**View Location:** [Source: architecture/source-tree.md]
```
samplify/
└── views/
    └── queue_visualization.py   # Create this file
```

**Template Location:**
```
templates/
└── queue/
    └── queue_visualization.html  # Create this file
```

**Static Assets Location (Local DataTables):**
```
static/
├── js/
│   ├── datatables.min.js        # Download locally (NFR3)
│   └── queue_visualization.js   # Create this file
└── css/
    └── datatables.min.css       # Download locally
```

**Test Location:**
```
tests/
└── test_queue_visualization.py  # Create this file
```

### Data Models
**File Model (Story 1.2A):** [Source: architecture/database-schema-design.md]
```python
class File(models.Model):
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)
    uid = models.CharField(max_length=8, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_format = models.CharField(max_length=50)
    sample_rate = models.IntegerField(null=True, blank=True)
    bit_depth = models.IntegerField(null=True, blank=True)
    file_size = models.BigIntegerField()
```

### Implementation Patterns

**Django View Pattern:**
```python
from django.views.generic import TemplateView
from apps.catalog.models import File
import hashlib

class QueueVisualizationView(TemplateView):
    template_name = 'queue/queue_visualization.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Input queue (pending files)
        input_files = File.objects.filter(status='pending')[:100]
        context['input_files'] = [
            {
                'uid': f.uid,
                'file_name': f.file_name,
                'file_path': f.file_path,
                'file_format': f.file_format,
                'sample_rate': f.sample_rate,
                'bit_depth': f.bit_depth,
                'file_size': f.file_size
            }
            for f in input_files
        ]

        # Output queue (with transformations)
        # TODO: Join with SchemaTransformation model
        context['output_files'] = []

        return context
```

**JavaScript UID Filtering (Local, NFR3):**
```javascript
// static/js/queue_visualization.js
let selectedUIDs = [];

// Click input file row to filter output queue
document.querySelectorAll('.input-row').forEach(row => {
    row.addEventListener('click', function(e) {
        const uid = this.dataset.uid;

        if (e.ctrlKey || e.metaKey) {
            // Multi-select with Ctrl/Cmd
            if (selectedUIDs.includes(uid)) {
                selectedUIDs = selectedUIDs.filter(u => u !== uid);
            } else {
                selectedUIDs.push(uid);
            }
        } else {
            // Single select
            selectedUIDs = [uid];
        }

        updateUIDFilter();
        filterOutputQueue();
    });
});

function updateUIDFilter() {
    const filterInput = document.getElementById('uid-filter');
    filterInput.value = selectedUIDs.map(uid => `#${uid}`).join(', ');
}

function filterOutputQueue() {
    const outputTable = $('#output-queue-table').DataTable();

    if (selectedUIDs.length === 0) {
        outputTable.search('').draw();
    } else {
        // Filter by UID (supports DataTables search)
        const searchPattern = selectedUIDs.map(uid => `#${uid}`).join('|');
        outputTable.column(1).search(searchPattern, true, false).draw();
    }
}

// Clear filter button
document.getElementById('clear-filter-btn').addEventListener('click', function() {
    selectedUIDs = [];
    updateUIDFilter();
    filterOutputQueue();
});

// AJAX polling for real-time updates (every 2 seconds)
setInterval(updateQueueTables, 2000);

function updateQueueTables() {
    fetch('/api/queue/files/')
        .then(response => response.json())
        .then(data => {
            const inputTable = $('#input-queue-table').DataTable();
            // Update rows without full redraw (preserve state)
            // ... implementation
        });
}
```

**HTML Template Pattern:**
```html
<!-- templates/queue/queue_visualization.html -->
{% extends "base.html" %}

{% block content %}
<div class="queue-visualization">
    <h3>Queue Visualization</h3>

    <!-- UID Filter -->
    <div class="uid-filter">
        <label>UID Filter:</label>
        <input type="text" id="uid-filter" placeholder="#a1f2, #b3e4, #c5d6">
        <button id="clear-filter-btn">✕ Clear</button>
    </div>

    <!-- Input Queue Table -->
    <div class="input-queue">
        <h4>Input Queue</h4>
        <table id="input-queue-table" class="queue-table">
            <thead>
                <tr>
                    <th><input type="checkbox" id="select-all-input"></th>
                    <th>UID</th>
                    <th>Filename</th>
                    <th>Path</th>
                    <th>Format</th>
                    <th>SR</th>
                    <th>BD</th>
                    <th>Size</th>
                </tr>
            </thead>
            <tbody>
                {% for file in input_files %}
                <tr class="input-row" data-uid="{{ file.uid }}">
                    <td><input type="checkbox"></td>
                    <td>#{{ file.uid }}</td>
                    <td>{{ file.file_name }}</td>
                    <td>{{ file.file_path }}</td>
                    <td>{{ file.file_format }}</td>
                    <td>{{ file.sample_rate }}</td>
                    <td>{{ file.bit_depth }}</td>
                    <td>{{ file.file_size|filesizeformat }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Output Queue Table -->
    <div class="output-queue">
        <h4>Output Queue</h4>
        <table id="output-queue-table" class="queue-table">
            <thead>
                <tr>
                    <th><input type="checkbox" id="select-all-output"></th>
                    <th>UID</th>
                    <th>Filename</th>
                    <th>Destination</th>
                    <th>Format</th>
                    <th>SR</th>
                    <th>BD</th>
                    <th>Process</th>
                </tr>
            </thead>
            <tbody>
                <!-- Populated via AJAX or server-side -->
            </tbody>
        </table>
    </div>
</div>

<link rel="stylesheet" href="{% static 'css/datatables.min.css' %}">
<script src="{% static 'js/datatables.min.js' %}"></script>
<script src="{% static 'js/queue_visualization.js' %}"></script>

<script>
// Initialize DataTables
$(document).ready(function() {
    $('#input-queue-table').DataTable({
        pageLength: 100,
        order: [[1, 'asc']]  // Sort by UID
    });

    $('#output-queue-table').DataTable({
        pageLength: 100,
        order: [[1, 'asc']]
    });
});
</script>
{% endblock %}
```

### Performance Optimization
**1000+ files rendering:** [Source: requirements AC 13]
- Use DataTables pagination (100 rows per page)
- Virtual scrolling for smooth performance
- Debounce AJAX updates (2-second interval)
- Only update changed rows (not full redraw)

**UID filtering <200ms:** [Source: requirements AC 14]
- Client-side filtering with DataTables search
- Index UID column in database
- Cache filtered results

### Preservation Rules
**NFR3 Compliance:** No CDN dependencies [Source: requirements.md NFR3]
- DataTables.js downloaded and served locally
- All JavaScript/CSS from `static/` directory

**NFR4 Compliance:** Progressive enhancement [Source: requirements.md NFR4]
- Works without JavaScript (static table)
- AJAX enhances experience but not required

---

## Dev Notes > Testing

### Test File Location
```
tests/
└── test_queue_visualization.py
```

### Testing Standards
**Framework:** pytest + pytest-django

**Test Coverage Target:** 80%+

**Test Categories:**
1. **Unit Tests - View Logic**
   - Test QueueVisualizationView context data
   - Test UID generation
   - Test filtering logic

2. **Integration Tests - AJAX Polling**
   - Test real-time updates every 2 seconds
   - Test preserving user state during updates
   - Test new file additions

3. **Performance Tests - 1000+ Files**
   - Load test with 1000+ files
   - Test UID filtering response time (<200ms)
   - Test table rendering performance

4. **UI Tests - UID Filtering**
   - Test click-to-filter
   - Test multi-select (Ctrl+Click)
   - Test clear button

**Example Test:**
```python
import pytest
from django.test import TestCase, Client
from apps.catalog.models import File

class QueueVisualizationTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create 1000 test files
        for i in range(1000):
            File.objects.create(
                file_path=f'/media/test_{i}.wav',
                file_name=f'test_{i}.wav',
                uid=f'uid{i:04d}',
                status='pending',
                file_size=1024000
            )

    def test_table_renders_1000_files(self):
        """Test table renders 1000+ files smoothly."""
        response = self.client.get('/queue/')

        assert response.status_code == 200
        # With pagination, only 100 visible at once
        assert response.content.decode().count('<tr class="input-row"') <= 100

    def test_uid_filtering_performance(self):
        """Test UID filtering responds <200ms."""
        import time
        start = time.time()

        response = self.client.get('/api/queue/filter/uid0001,uid0002/')
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed < 200

    def test_ajax_updates_dont_disrupt_interaction(self):
        """Test AJAX updates preserve user state."""
        # Simulate user selecting rows
        # Trigger AJAX update
        # Verify selections preserved
        pass
```

**Running Tests:**
```bash
pytest tests/test_queue_visualization.py -v
pytest tests/test_queue_visualization.py --cov=samplify.views.queue_visualization --cov-report=html
```

---

## Definition of Done
- [ ] Dual queue tables implemented
- [ ] UID filtering functional
- [ ] Click-to-filter working
- [ ] AJAX updates tested
- [ ] Performance validated (1000+ files)
- [ ] UI matches wireframe
- [ ] Documentation updated with queue visualization instructions

---

## Risk Assessment
- **Primary Risk:** Performance degrades with 1000+ files
- **Mitigation:** Pagination, virtual scrolling, efficient DOM updates
- **Rollback:** Simplify UI, remove real-time updates

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
