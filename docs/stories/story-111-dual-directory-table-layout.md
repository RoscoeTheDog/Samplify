# Story 1.11: Dual Directory Table Layout

## Status
**Approved**

---

## User Story
As a **user**,
I want **separate tables for input and output directories**,
So that **I can select folders and configure mappings visually**.

---

## Story Context
**Existing System Integration:**
- Integrates with: Story 1.10 (Schema UI), Story 1.2B (DirectoryMapping model)
- Technology: Django templates, JavaScript for folder selection
- Follows pattern: UI wireframe (Option 1 - Horizontal Split)
- Touch points: DirectoryMapping CRUD, folder browser integration

---

## Acceptance Criteria

**Functional Requirements:**
1. Input directory table displays all input paths from DirectoryMapping
2. Output directory table displays all output paths from DirectoryMapping
3. "Add Folder" button opens native file browser dialog (JavaScript)
4. Folder selection checkboxes allow enable/disable per directory
5. Selected folder highlights in table (active state)
6. Folder removal button (with confirmation)
7. Directory paths displayed with truncation (long paths)
8. Table responsive to window resize

**Integration Requirements:**
9. Integrates with DirectoryMapping model (Story 1.2B)
10. Uses schema from Story 1.10 (active schema context)
11. JavaScript uses local libraries (NFR3)
12. Works without JavaScript (degraded experience)

**Quality Requirements:**
13. File browser works on Windows/macOS/Linux
14. Path handling uses pathlib (cross-platform, NFR6)
15. Table renders correctly with 10+ directories
16. UI matches wireframe design (horizontal split)

---

## Tasks / Subtasks

- [ ] **Task 1: Create Django view structure for directory management** (AC: 1, 2, 9, 10)
  - [ ] Create `samplify/views/directory_views.py`
  - [ ] Implement DirectoryTableView (lists input/output directories)
  - [ ] Query DirectoryMapping model filtered by active schema
  - [ ] Pass input and output directories to template context

- [ ] **Task 2: Create HTML templates for dual tables** (AC: 1, 2, 7, 8, 16)
  - [ ] Create `templates/directories/directory_tables.html`
  - [ ] Implement horizontal split layout (input left, output right)
  - [ ] Add truncation for long paths (title attribute shows full path)
  - [ ] Make tables responsive with CSS media queries
  - [ ] Match UI wireframe Option 1 design

- [ ] **Task 3: Implement folder selection functionality** (AC: 3, 4, 11, 13)
  - [ ] Add "Add Folder" button with file browser integration
  - [ ] Use HTML5 `<input type="file" webkitdirectory>` for folder selection
  - [ ] Add checkbox per directory row (enable/disable monitoring)
  - [ ] Serve JavaScript locally (no CDN dependencies, NFR3)
  - [ ] Test on Windows/macOS/Linux platforms

- [ ] **Task 4: Add folder highlight and selection state** (AC: 5)
  - [ ] Add click handler to highlight selected directory row
  - [ ] Store selected directory in JavaScript state
  - [ ] Apply CSS class for active state (border/background change)
  - [ ] Clear selection when clicking outside table

- [ ] **Task 5: Implement folder removal with confirmation** (AC: 6)
  - [ ] Add "Remove" button per directory row
  - [ ] Show confirmation dialog (JavaScript confirm or modal)
  - [ ] Delete DirectoryMapping record via AJAX POST
  - [ ] Refresh table after successful deletion

- [ ] **Task 6: Implement cross-platform path handling** (AC: 14)
  - [ ] Use pathlib.Path for path operations in views
  - [ ] Display paths with forward slashes (normalized display)
  - [ ] Handle Windows UNC paths correctly
  - [ ] Test path truncation with long directory names

- [ ] **Task 7: Add progressive enhancement and fallback** (AC: 12)
  - [ ] Ensure table renders correctly without JavaScript
  - [ ] Provide text input fallback for adding directories (no JS)
  - [ ] Form submission works with full page refresh (non-AJAX)
  - [ ] Display appropriate messaging for non-JS browsers

- [ ] **Task 8: Testing** (AC: 13, 15, 16)
  - [ ] Test file browser on Windows/macOS/Linux
  - [ ] Test table rendering with 10+ directories
  - [ ] Test path truncation and display
  - [ ] Test checkbox state persistence
  - [ ] Validate UI matches wireframe

---

## Dev Notes

### Previous Story Insights
**From Story 1.10 (Schema Management UI):**
- Django CRUD views pattern established at `samplify/views/schema_crud.py` [Source: Story 1.10 Dev Agent Record]
- Base template with navigation at `templates/base.html`
- AJAX form submission pattern with progressive enhancement
- Local static assets served from `static/` directory (NFR3)

**From Story 1.2B (Schema Models):**
- DirectoryMapping model at `apps/catalog/models.py` [Source: Story 1.2B]
- ForeignKey relationship to Schema model
- Boolean fields: `monitor` (enable/disable), `recursive` (subdirectory scanning)

### File Locations (Source Tree)
**View Location:** [Source: architecture/source-tree.md]
```
samplify/
└── views/
    └── directory_views.py       # Create this file
```

**Template Location:**
```
templates/
└── directories/
    └── directory_tables.html    # Create this file
```

**Static Assets Location:**
```
static/
└── js/
    └── directory_manager.js     # Create this file (local JavaScript)
```

**Test Location:**
```
tests/
└── test_directory_ui.py         # Create this file
```

### Data Models
**DirectoryMapping Model (Story 1.2B):** [Source: architecture/database-schema-design.md]
```python
class DirectoryMapping(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)
    path = models.CharField(max_length=500)
    is_input = models.BooleanField(default=True)  # True=input, False=output
    monitor = models.BooleanField(default=False)
    recursive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Schema Model (Story 1.2B):** [Source: architecture/database-schema-design.md]
```python
class Schema(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
```

### Implementation Patterns

**Django View Pattern:**
```python
from django.views.generic import TemplateView
from django.http import JsonResponse
from apps.catalog.models import DirectoryMapping, Schema
from pathlib import Path

class DirectoryTableView(TemplateView):
    template_name = 'directories/directory_tables.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_schema = Schema.objects.filter(is_active=True).first()

        if active_schema:
            context['input_directories'] = DirectoryMapping.objects.filter(
                schema=active_schema, is_input=True
            )
            context['output_directories'] = DirectoryMapping.objects.filter(
                schema=active_schema, is_input=False
            )
        else:
            context['input_directories'] = []
            context['output_directories'] = []

        context['active_schema'] = active_schema
        return context
```

**File Browser JavaScript Pattern (Local, NFR3):**
```javascript
// static/js/directory_manager.js
document.getElementById('add-folder-btn').addEventListener('click', function() {
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;  // Chrome/Edge
    input.directory = true;          // Firefox

    input.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const folderPath = e.target.files[0].webkitRelativePath.split('/')[0];
            // Send via AJAX to Django view
            addDirectory(folderPath);
        }
    });

    input.click();
});

function addDirectory(path) {
    fetch('/api/directories/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ path: path, is_input: true })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();  // Refresh table
        }
    });
}
```

**Path Handling Pattern (Cross-Platform, NFR6):**
```python
from pathlib import Path

def normalize_path_display(path_string):
    """Normalize path for cross-platform display."""
    path = Path(path_string)
    # Always display with forward slashes
    return str(path).replace('\\', '/')

def truncate_path(path_string, max_length=50):
    """Truncate long paths for display."""
    if len(path_string) <= max_length:
        return path_string

    parts = Path(path_string).parts
    if len(parts) <= 3:
        return path_string

    # Show first and last parts: "C:/Users/.../Documents/MyFolder"
    return f"{parts[0]}/.../{'/'.join(parts[-2:])}"
```

**HTML Template Pattern:**
```html
<!-- templates/directories/directory_tables.html -->
{% extends "base.html" %}

{% block content %}
<div class="directory-tables-container">
    <div class="input-directories">
        <h3>Input Directories</h3>
        <button id="add-input-folder-btn">Add Folder</button>
        <table>
            <thead>
                <tr>
                    <th><input type="checkbox" id="select-all-input"></th>
                    <th>Path</th>
                    <th>Monitor</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for dir in input_directories %}
                <tr class="directory-row" data-id="{{ dir.id }}">
                    <td><input type="checkbox" class="dir-checkbox"></td>
                    <td title="{{ dir.path }}">{{ dir.path|truncate_path }}</td>
                    <td><input type="checkbox" {% if dir.monitor %}checked{% endif %}></td>
                    <td><button class="remove-btn" data-id="{{ dir.id }}">Remove</button></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="output-directories">
        <h3>Output Directories</h3>
        <button id="add-output-folder-btn">Add Folder</button>
        <table>
            <!-- Similar structure -->
        </table>
    </div>
</div>
{% endblock %}
```

### Preservation Rules
**CR4 Compliance:** Schema functionality preserved [Source: requirements.md CR4]
- DirectoryMapping CRUD maintains relationship to Schema
- Input/output directory separation preserved from XML structure

**NFR3 Compliance:** No CDN dependencies [Source: requirements.md NFR3]
- All JavaScript served from `static/js/` directory
- No external library dependencies for file browser

**NFR6 Compliance:** Cross-platform paths [Source: requirements.md NFR6]
- Use pathlib.Path for all path operations
- Test on Windows (backslash), macOS/Linux (forward slash)
- Handle UNC paths on Windows (`\\server\share`)

---

## Dev Notes > Testing

### Test File Location
[Source: architecture/testing-strategy.md]
```
tests/
└── test_directory_ui.py
```

### Testing Standards
**Framework:** pytest + pytest-django [Source: architecture/tech-stack.md]

**Test Coverage Target:** 80%+ for directory management views [Source: architecture/testing-strategy.md]

**Test Categories:**
1. **Unit Tests - View Logic**
   - Test DirectoryTableView context data
   - Test path normalization and truncation functions
   - Test AJAX endpoint responses

2. **Integration Tests - DirectoryMapping CRUD**
   - Test add directory via AJAX
   - Test remove directory with confirmation
   - Test checkbox state persistence
   - Test schema filtering (only active schema directories shown)

3. **UI Tests - Template Rendering**
   - Test table rendering with 0, 1, 10+ directories
   - Test path truncation display
   - Test progressive enhancement (no JS fallback)

4. **Cross-Platform Tests**
   - Test file browser on Windows/macOS/Linux
   - Test path display with backslashes (Windows) and forward slashes (Unix)
   - Test UNC path handling on Windows

**Example Test:**
```python
import pytest
from django.test import TestCase, Client
from apps.catalog.models import DirectoryMapping, Schema

class DirectoryUITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)

    def test_directory_table_view_displays_input_directories(self):
        """Test input directories displayed in table."""
        DirectoryMapping.objects.create(
            schema=self.schema,
            path="/media/audio/music",
            is_input=True,
            monitor=True
        )

        response = self.client.get('/directories/')

        assert response.status_code == 200
        assert '/media/audio/music' in response.content.decode()

    def test_add_directory_via_ajax(self):
        """Test adding directory via AJAX POST."""
        response = self.client.post(
            '/api/directories/add/',
            data={'path': '/media/samples', 'is_input': True},
            content_type='application/json'
        )

        assert response.status_code == 200
        assert DirectoryMapping.objects.filter(path='/media/samples').exists()

    def test_path_truncation(self):
        """Test long path truncation for display."""
        from samplify.views.directory_views import truncate_path

        long_path = '/Users/username/Documents/Projects/Audio/Samples/Drums/Kicks'
        truncated = truncate_path(long_path, max_length=50)

        assert len(truncated) <= 50
        assert '...' in truncated
```

**Running Tests:**
```bash
# Run directory UI tests
pytest tests/test_directory_ui.py -v

# Run with coverage
pytest tests/test_directory_ui.py --cov=samplify.views.directory_views --cov-report=html

# Cross-platform test (run on each OS)
pytest tests/test_directory_ui.py::test_file_browser_platform -v
```

---

## Definition of Done
- [ ] Input/output directory tables implemented
- [ ] Add/remove folder functionality working
- [ ] File browser dialog tested on all platforms
- [ ] Checkbox selection functional
- [ ] UI matches wireframe design
- [ ] Documentation updated with directory management instructions

---

## Risk Assessment
- **Primary Risk:** File browser API inconsistent across platforms
- **Mitigation:** Test on Windows/macOS/Linux, provide fallback text input
- **Rollback:** Use text input for directory paths

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
