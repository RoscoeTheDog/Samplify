# Frontend Component Architecture

**Version:** 1.0
**Last Updated:** 2025-10-04
**Status:** Design Document

---

## Overview

Samplify's frontend uses Django templates with progressive JavaScript enhancement (NFR4). The architecture prioritizes:
- **Server-side rendering** for core functionality
- **Minimal JavaScript** for real-time updates (AJAX polling)
- **Local static files** - no CDN dependencies (NFR3)
- **Accessible design** - works without JavaScript

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Templates | Django Templates | Built-in | Server-side HTML rendering |
| JavaScript | Vanilla JS | ES6+ | AJAX polling, UI interactions |
| CSS | Custom CSS | N/A | Minimal styling (proof-of-concept) |
| Icons | Unicode/Emoji | N/A | Status indicators (●ON/●OFF) |

**No frameworks required** - keeping it simple per project brief.

---

## Component Hierarchy

```
┌─────────────────────────────────┐
│       Base Template             │
│  (base.html)                    │
│  - Header with navigation       │
│  - CSRF token                   │
│  - Static file loading          │
└────────┬────────────────────────┘
         │
         ├──► Schema Designer Page (index.html)
         │    └──► SchemaForm Component
         │    └──► DirectoryTables Component
         │    └──► PropertiesPanel Component
         │    └──► WatchdogControls Component
         │    └──► QueueVisualization Component
         │
         ├──► Batch Processing Page (batch.html)
         │    └──► ProgressMonitor Component
         │    └──► FileQueue Component
         │
         └──► Status Dashboard (dashboard.html)
              └──► SystemStatus Component
              └──► RecentActivity Component
```

---

## Core Templates

### 1. Base Template

**File:** `frontend/templates/base.html`

```django
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Samplify{% endblock %}</title>

    <!-- Local static files (NFR3) -->
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            <h1>Samplify - Django Web UI</h1>
            <ul>
                <li><a href="{% url 'schema_designer' %}">Schema Designer</a></li>
                <li><a href="{% url 'dashboard' %}">Dashboard</a></li>
            </ul>
        </nav>
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- JavaScript (loaded at end for performance) -->
    <script src="{% static 'js/utils.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

**Responsibilities:**
- Common layout structure
- Navigation
- Static file loading
- CSRF token inclusion

---

### 2. Schema Designer Page

**File:** `apps/schemas/templates/schemas/index.html`

**Layout Structure:**
```
┌─────────────────────────────────────────────────┐
│  Watchdog Controls                              │
│  [●ON File Monitor] [●ON Queue Processor]       │
├─────────────────────────────────────────────────┤
│  Schema Toolbar                                 │
│  Schema: [Dropdown] [Save] [Load] [Delete]     │
├──────────────────┬──────────────────────────────┤
│  Input Dirs      │  Output Dirs                 │
│  (DirectoryTable)│  (DirectoryTable)            │
├──────────────────┴──────────────────────────────┤
│  Properties Panel                               │
│  (Filters + Processing Rules)                   │
├─────────────────────────────────────────────────┤
│  Action Buttons                                 │
│  [Scan] [Preview] [Start Batch]                 │
├─────────────────────────────────────────────────┤
│  Queue Visualization                            │
│  (Dual tables: Input/Output files)              │
└─────────────────────────────────────────────────┘
```

**Template Code:**
```django
{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="schema-designer">
    <!-- Watchdog Controls -->
    <div class="watchdog-controls">
        <button id="file-monitor-toggle" class="watchdog-btn" data-status="{{ file_monitor_status }}">
            <span class="status-icon">●</span>
            <span class="status-text">File Monitor</span>
        </button>
        <button id="queue-processor-toggle" class="watchdog-btn" data-status="{{ queue_processor_status }}">
            <span class="status-icon">●</span>
            <span class="status-text">Queue Processor</span>
        </button>
    </div>

    <!-- Schema Toolbar -->
    <div class="schema-toolbar">
        <label for="schema-select">Schema:</label>
        <select id="schema-select" name="schema">
            {% for schema in schemas %}
            <option value="{{ schema.id }}" {% if schema.is_active %}selected{% endif %}>
                {{ schema.name }}
            </option>
            {% endfor %}
        </select>
        <button id="save-schema">Save</button>
        <button id="load-schema">Load</button>
        <button id="delete-schema">Delete</button>
    </div>

    <!-- Directory Tables -->
    <div class="directory-section">
        <div class="input-directories">
            <h2>Input Directories</h2>
            {% include 'schemas/components/directory_table.html' with directories=input_dirs type='input' %}
        </div>
        <div class="output-directories">
            <h2>Output Directories</h2>
            {% include 'schemas/components/directory_table.html' with directories=output_dirs type='output' %}
        </div>
    </div>

    <!-- Properties Panel -->
    <div class="properties-panel">
        {% include 'schemas/components/properties_panel.html' %}
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
        <button id="scan-input" class="btn-primary">Scan Input</button>
        <button id="preview-transformations" class="btn-secondary">Preview Transformations</button>
        <button id="start-batch" class="btn-primary">Start Batch Process</button>
    </div>

    <!-- Queue Visualization -->
    <div class="queue-visualization">
        {% include 'schemas/components/queue_visualization.html' %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/schema-designer.js' %}"></script>
{% endblock %}
```

---

## Component Templates

### 3. Directory Table Component

**File:** `apps/schemas/templates/schemas/components/directory_table.html`

```django
<div class="directory-table">
    <button class="add-directory">+ Add Folder</button>
    <table>
        <thead>
            <tr>
                <th><input type="checkbox" class="select-all"></th>
                <th>Path</th>
                {% if type == 'input' %}
                <th>Monitor</th>
                <th>Recursive</th>
                {% endif %}
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for dir in directories %}
            <tr>
                <td><input type="checkbox" class="dir-select" value="{{ dir.id }}"></td>
                <td>{{ dir.path }}</td>
                {% if type == 'input' %}
                <td><input type="checkbox" {% if dir.monitor_enabled %}checked{% endif %}></td>
                <td><input type="checkbox" {% if dir.recursive %}checked{% endif %}></td>
                {% endif %}
                <td>
                    <button class="btn-small edit-dir" data-id="{{ dir.id }}">Edit</button>
                    <button class="btn-small remove-dir" data-id="{{ dir.id }}">Remove</button>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5">No directories configured</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

---

### 4. Properties Panel Component

**File:** `apps/schemas/templates/schemas/components/properties_panel.html`

```django
<div class="properties-panel-content">
    <div class="selected-directory-info">
        <h3>Selected: <span id="selected-dir-path">None</span></h3>
    </div>

    <div class="panel-sections">
        <!-- Filters Section -->
        <div class="filters-section">
            <h4>Filters</h4>
            <button class="add-filter">+ Add Filter</button>
            <div id="filters-list">
                {% for filter in filters %}
                <div class="filter-item" data-id="{{ filter.id }}">
                    <select class="filter-type">
                        <option value="keyword" {% if filter.filter_type == 'keyword' %}selected{% endif %}>Keyword</option>
                        <option value="extension" {% if filter.filter_type == 'extension' %}selected{% endif %}>Extension</option>
                        <option value="media_type" {% if filter.filter_type == 'media_type' %}selected{% endif %}>Media Type</option>
                    </select>
                    <input type="text" class="filter-value" value="{{ filter.value }}" placeholder="Value">
                    <button class="remove-filter">×</button>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Processing Rules Section -->
        <div class="rules-section">
            <h4>Processing Rules</h4>
            <button class="add-rule">+ Add Rule</button>
            <div id="rules-list">
                {% for rule in processing_rules %}
                <div class="rule-item" data-id="{{ rule.id }}">
                    <label>Format: <input type="text" name="format" value="{{ rule.output_format }}"></label>
                    <label>Sample Rate: <input type="number" name="sample_rate" value="{{ rule.sample_rate }}"></label>
                    <label>Bit Depth:
                        <select name="bit_depth">
                            <option value="16" {% if rule.bit_depth == 16 %}selected{% endif %}>16-bit</option>
                            <option value="24" {% if rule.bit_depth == 24 %}selected{% endif %}>24-bit</option>
                        </select>
                    </label>
                    <label>Normalize:
                        <input type="checkbox" name="normalize" {% if rule.normalize %}checked{% endif %}>
                        <input type="number" name="normalize_level" value="{{ rule.normalize_level }}" step="0.1">dB
                    </label>
                    <button class="remove-rule">×</button>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Logic Operator -->
        <div class="logic-operator">
            <label>Logic:</label>
            <button class="logic-btn active" data-value="AND">AND</button>
            <button class="logic-btn" data-value="OR">OR</button>
        </div>
    </div>
</div>
```

---

### 5. Queue Visualization Component

**File:** `apps/schemas/templates/schemas/components/queue_visualization.html`

```django
<div class="queue-container">
    <h3>Processing Queue (<span id="queue-count">0</span> files)</h3>

    <!-- Input Files Table -->
    <div class="input-queue">
        <h4>Input Files</h4>
        <table class="file-table">
            <thead>
                <tr>
                    <th><input type="checkbox" class="select-all-files"></th>
                    <th>UID</th>
                    <th>Filename</th>
                    <th>Path</th>
                    <th>Format</th>
                    <th>SR</th>
                    <th>BD</th>
                    <th>Size</th>
                </tr>
            </thead>
            <tbody id="input-files-tbody">
                <!-- Populated via JavaScript AJAX -->
            </tbody>
        </table>
    </div>

    <!-- Output Destinations Table -->
    <div class="output-queue">
        <h4>Output Destinations
            <input type="text" id="uid-filter" placeholder="Filter by UID: #a1f2, #b3e4">
            <button id="clear-filter">✕</button>
        </h4>
        <table class="file-table">
            <thead>
                <tr>
                    <th><input type="checkbox" class="select-all-output"></th>
                    <th>UID</th>
                    <th>Filename</th>
                    <th>Destination</th>
                    <th>Format</th>
                    <th>SR</th>
                    <th>BD</th>
                    <th>Process</th>
                </tr>
            </thead>
            <tbody id="output-files-tbody">
                <!-- Populated via JavaScript AJAX -->
            </tbody>
        </table>
    </div>

    <!-- Actions -->
    <div class="queue-actions">
        <label><input type="checkbox" id="select-all-queue"> Select All</label>
        <button id="deselect-skipped">▲ Deselect Skipped</button>
        <button id="clear-queue">Clear Queue</button>
        <button id="export-preview">Export Preview</button>
    </div>
</div>
```

---

## JavaScript Modules

### 6. Schema Designer JS

**File:** `frontend/static/js/schema-designer.js`

```javascript
/**
 * Schema Designer - Main JavaScript Module
 * Handles AJAX interactions and UI state management
 */

// CSRF token helper (Django requirement)
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Watchdog control toggle
class WatchdogControl {
    constructor(buttonId, endpoint) {
        this.button = document.getElementById(buttonId);
        this.endpoint = endpoint;
        this.button.addEventListener('click', () => this.toggle());
    }

    async toggle() {
        const currentStatus = this.button.dataset.status;
        const newAction = currentStatus === 'running' ? 'stop' : 'start';

        try {
            const response = await fetch(`${this.endpoint}/${newAction}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.updateUI(newAction === 'start' ? 'running' : 'stopped');
            }
        } catch (error) {
            console.error('Watchdog toggle failed:', error);
        }
    }

    updateUI(status) {
        this.button.dataset.status = status;
        const icon = this.button.querySelector('.status-icon');
        const text = this.button.querySelector('.status-text');

        if (status === 'running') {
            icon.style.color = 'green';
            text.textContent = text.textContent.replace('OFF', 'ON');
        } else {
            icon.style.color = 'red';
            text.textContent = text.textContent.replace('ON', 'OFF');
        }
    }
}

// Batch processing with AJAX polling
class BatchProcessor {
    constructor() {
        this.batchId = null;
        this.pollingInterval = null;
    }

    async start() {
        const response = await fetch('/api/batch/start/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                schema_id: document.getElementById('schema-select').value
            })
        });

        const data = await response.json();

        if (data.success) {
            this.batchId = data.data.batch_id;
            this.startPolling();
        }
    }

    startPolling() {
        // Poll every 2 seconds (NFR4)
        this.pollingInterval = setInterval(() => this.pollStatus(), 2000);
    }

    async pollStatus() {
        const response = await fetch(`/api/batch/${this.batchId}/status/`);
        const data = await response.json();

        if (data.success) {
            this.updateProgressUI(data.data);

            // Stop polling when complete
            if (data.data.status === 'completed' || data.data.status === 'failed') {
                clearInterval(this.pollingInterval);
                this.handleCompletion(data.data);
            }
        }
    }

    updateProgressUI(progressData) {
        const progressBar = document.getElementById('progress-bar');
        const statusText = document.getElementById('status-text');

        progressBar.style.width = `${progressData.progress.percent_complete}%`;
        statusText.textContent = `Processing: ${progressData.progress.files_processed}/${progressData.progress.total_files}`;
    }

    handleCompletion(finalData) {
        alert(`Batch processing ${finalData.status}. ${finalData.progress.files_processed} files processed.`);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Watchdog controls
    const fileMonitor = new WatchdogControl('file-monitor-toggle', '/api/watchdog/file-monitor');
    const queueProcessor = new WatchdogControl('queue-processor-toggle', '/api/watchdog/queue-processor');

    // Batch processor
    const batchProcessor = new BatchProcessor();
    document.getElementById('start-batch').addEventListener('click', () => {
        batchProcessor.start();
    });

    // Queue visualization (load files via AJAX)
    loadFileQueue();
});

async function loadFileQueue() {
    const response = await fetch('/api/files/?schema_id=' + document.getElementById('schema-select').value);
    const data = await response.json();

    if (data.success) {
        renderInputQueue(data.data);
    }
}

function renderInputQueue(files) {
    const tbody = document.getElementById('input-files-tbody');
    tbody.innerHTML = '';

    files.forEach(file => {
        const row = `
            <tr>
                <td><input type="checkbox" class="file-select" value="${file.id}"></td>
                <td>${file.uid}</td>
                <td>${file.filename}</td>
                <td>${file.path}</td>
                <td>${file.format}</td>
                <td>${file.metadata.sample_rate || '-'}</td>
                <td>${file.metadata.bit_depth || '-'}</td>
                <td>${formatFileSize(file.file_size)}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}
```

---

## Static Assets Structure

```
frontend/static/
├── css/
│   ├── main.css                 # Global styles
│   ├── schema-designer.css      # Schema page styles
│   └── components.css           # Reusable component styles
├── js/
│   ├── utils.js                 # Utility functions (CSRF, formatting)
│   ├── schema-designer.js       # Main schema page logic
│   ├── batch-processor.js       # Batch processing + polling
│   └── queue-visualization.js   # Queue table management
└── icons/
    └── (none - using Unicode/emoji)
```

---

## Progressive Enhancement Strategy

### Without JavaScript (Baseline)

1. **Schema Designer**: Form submission → server renders updated page
2. **Batch Processing**: Form submit → redirect to status page with auto-refresh meta tag
3. **Watchdog Controls**: POST forms with redirect

### With JavaScript (Enhanced)

1. **Schema Designer**: AJAX updates, no page reload
2. **Batch Processing**: Real-time progress via 2-second polling
3. **Watchdog Controls**: Toggle buttons with instant feedback

---

## Accessibility

- **Keyboard navigation**: All controls accessible via Tab
- **Screen readers**: Semantic HTML, ARIA labels where needed
- **No-JS fallback**: Full functionality without JavaScript
- **Color contrast**: Meets WCAG AA standards

---

## Related Documents

- **[API Endpoints](./api-endpoints.md)** - Backend APIs consumed by frontend
- **[User Interface Goals](../prd/user-interface-enhancement-goals.md)** - UI requirements
- **[Technical Constraints](../prd/technical-constraints-and-integration-requirements.md)** - NFR3, NFR4
