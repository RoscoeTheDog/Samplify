# Story 1.12: Properties Panel with Filter/Rule CRUD

## Status
**Approved**

---

## User Story
As a **user**,
I want **a properties panel to configure filters and processing rules**,
So that **I can define how files are processed without editing code**.

---

## Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (SchemaRule, SchemaTransformation models), Story 1.11 (directory tables)
- Technology: Django forms, JavaScript for dynamic fields
- Follows pattern: UI wireframe (properties panel)
- Touch points: SchemaRule/SchemaTransformation CRUD

---

## Acceptance Criteria

**Functional Requirements:**
1. Properties panel displays for selected input directory
2. Filters section with "Add Filter" button:
   - Keyword filter (text input)
   - Extension filter (dropdown: .wav, .mp3, .flac, .aiff, etc.)
   - Media type filter (dropdown: audio, video, image)
   - Attribute filter (sample rate, bit depth ranges)
3. Processing rules section with "Add Rule" button:
   - Output format (dropdown: WAV, MP3, FLAC)
   - Sample rate (dropdown: 44100, 48000, 96000, 192000)
   - Bit depth (dropdown: 16, 24, 32)
   - Normalize (slider: -12dB to 0dB)
4. Logic operator selector (AND/OR toggle)
5. Filter/rule removal buttons (per item)
6. Rules saved to database on change (auto-save)

**Integration Requirements:**
7. Integrates with SchemaRule model (Story 1.2B)
8. Integrates with SchemaTransformation model (Story 1.2B)
9. Uses selected directory from Story 1.11
10. Supports all XML rule types (CR4)

**Quality Requirements:**
11. Auto-save works without page refresh (AJAX)
12. Form validation prevents invalid rules
13. UI matches wireframe design
14. Dynamic fields responsive and accessible

---

## Tasks / Subtasks

- [ ] **Task 1: Create Django forms for filters and rules** (AC: 2, 3, 7, 8, 12)
  - [ ] Create `samplify/forms/rule_forms.py`
  - [ ] Implement SchemaRuleForm (keyword, extension, media type, attribute filters)
  - [ ] Implement SchemaTransformationForm (format, sample rate, bit depth, normalize)
  - [ ] Add form validation for each rule type
  - [ ] Support all XML rule types (CR4 compliance)

- [ ] **Task 2: Create properties panel view** (AC: 1, 9)
  - [ ] Create `samplify/views/properties_panel.py`
  - [ ] Implement PropertiesPanelView (displays rules for selected directory)
  - [ ] Filter rules by selected InputDirectory (from Story 1.11)
  - [ ] Pass filter and transformation rules to template context

- [ ] **Task 3: Create HTML template for properties panel** (AC: 1, 2, 3, 4, 5, 13)
  - [ ] Create `templates/properties/properties_panel.html`
  - [ ] Add "Filters" section with dynamic filter list
  - [ ] Add "Processing Rules" section with dynamic rule list
  - [ ] Add "Add Filter" and "Add Rule" buttons
  - [ ] Add AND/OR logic operator toggle
  - [ ] Add remove buttons per filter/rule
  - [ ] Match UI wireframe design

- [ ] **Task 4: Implement dynamic field addition** (AC: 2, 3, 14)
  - [ ] Add JavaScript handlers for "Add Filter" button
  - [ ] Add JavaScript handlers for "Add Rule" button
  - [ ] Dynamically insert form fields based on filter/rule type
  - [ ] Populate dropdowns with appropriate values
  - [ ] Ensure accessibility (keyboard navigation, ARIA labels)

- [ ] **Task 5: Implement auto-save functionality** (AC: 6, 11)
  - [ ] Add AJAX handlers for form field changes (debounced)
  - [ ] Send rule data to Django view via POST
  - [ ] Save SchemaRule/SchemaTransformation to database
  - [ ] Display success/error feedback (toast notification)
  - [ ] Handle concurrent edits gracefully

- [ ] **Task 6: Implement filter/rule removal** (AC: 5)
  - [ ] Add click handlers for remove buttons
  - [ ] Send DELETE request via AJAX
  - [ ] Remove SchemaRule/SchemaTransformation from database
  - [ ] Remove DOM element from properties panel
  - [ ] Update UI to reflect removal

- [ ] **Task 7: Implement logic operator toggle** (AC: 4)
  - [ ] Add AND/OR toggle button in filters section
  - [ ] Save logic operator preference to database (Schema model)
  - [ ] Apply logic operator to filter evaluation (Story 1.5 integration)
  - [ ] Display current logic operator state in UI

- [ ] **Task 8: Support all XML rule types (CR4)** (AC: 10)
  - [ ] Implement keyword filter (contains_expression from rules.py)
  - [ ] Implement extension filter (contains_extensions from rules.py)
  - [ ] Implement media type filter (contains_audio/contains_video from rules.py)
  - [ ] Implement attribute filter (sample_rate, bit_depth ranges)
  - [ ] Implement date range filter (between_datetime from rules.py)
  - [ ] Validate against XML template structure

- [ ] **Task 9: Testing** (AC: 11, 12, 14)
  - [ ] Test form validation for all rule types
  - [ ] Test auto-save functionality
  - [ ] Test dynamic field addition/removal
  - [ ] Test AND/OR logic operator
  - [ ] Test AJAX error handling
  - [ ] Test accessibility (keyboard, screen reader)

---

## Dev Notes

### Previous Story Insights
**From Story 1.11 (Dual Directory Table Layout):**
- Directory selection mechanism at `templates/directories/directory_tables.html` [Source: Story 1.11 Dev Agent Record]
- Selected directory stored in JavaScript state
- Click event triggers properties panel update

**From Story 1.2B (Schema Models):**
- SchemaRule model at `apps/catalog/models.py` [Source: Story 1.2B]
- SchemaTransformation model at `apps/catalog/models.py` [Source: Story 1.2B]
- ForeignKey relationships to InputDirectory and Schema

**From Story 1.5 (File Scanning Service):**
- Algorithm preservation for search/filter logic (handlers/rules.py) [Source: Story 1.5 Dev Notes]
- Filter functions: contains_expression(), contains_extensions(), contains_audio(), contains_video()

### File Locations (Source Tree)
**Form Location:** [Source: architecture/source-tree.md]
```
samplify/
└── forms/
    └── rule_forms.py            # Create this file
```

**View Location:**
```
samplify/
└── views/
    └── properties_panel.py      # Create this file
```

**Template Location:**
```
templates/
└── properties/
    └── properties_panel.html    # Create this file
```

**Static Assets Location:**
```
static/
└── js/
    └── properties_panel.js      # Create this file (local JavaScript)
```

**Test Location:**
```
tests/
└── test_properties_panel.py     # Create this file
```

### Data Models
**SchemaRule Model (Story 1.2B):** [Source: architecture/database-schema-design.md]
```python
class SchemaRule(models.Model):
    RULE_TYPE_CHOICES = [
        ('keyword', 'Keyword Filter'),
        ('extension', 'Extension Filter'),
        ('media_type', 'Media Type Filter'),
        ('attribute', 'Attribute Filter'),
        ('date_range', 'Date Range Filter'),
    ]

    input_directory = models.ForeignKey(InputDirectory, on_delete=models.CASCADE)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES)
    rule_value = models.JSONField()  # Stores filter parameters
    logic_operator = models.CharField(max_length=3, choices=[('AND', 'AND'), ('OR', 'OR')], default='AND')
    order = models.IntegerField(default=0)
```

**SchemaTransformation Model (Story 1.2B):** [Source: architecture/database-schema-design.md]
```python
class SchemaTransformation(models.Model):
    input_directory = models.ForeignKey(InputDirectory, on_delete=models.CASCADE)
    output_format = models.CharField(max_length=50)  # WAV, MP3, FLAC
    sample_rate = models.IntegerField(null=True, blank=True)  # 44100, 48000, 96000, 192000
    bit_depth = models.IntegerField(null=True, blank=True)  # 16, 24, 32
    normalize_db = models.FloatField(null=True, blank=True)  # -12.0 to 0.0
```

### Implementation Patterns

**Django Form Pattern:**
```python
from django import forms
from apps.catalog.models import SchemaRule, SchemaTransformation

class SchemaRuleForm(forms.ModelForm):
    class Meta:
        model = SchemaRule
        fields = ['rule_type', 'rule_value', 'logic_operator', 'order']

    def clean_rule_value(self):
        """Validate rule_value based on rule_type."""
        rule_type = self.cleaned_data.get('rule_type')
        rule_value = self.cleaned_data.get('rule_value')

        if rule_type == 'keyword':
            if not isinstance(rule_value, dict) or 'pattern' not in rule_value:
                raise forms.ValidationError("Keyword filter requires 'pattern' field")
        elif rule_type == 'extension':
            if not isinstance(rule_value, list):
                raise forms.ValidationError("Extension filter requires list of extensions")
        elif rule_type == 'attribute':
            if not all(k in rule_value for k in ['min', 'max', 'attribute']):
                raise forms.ValidationError("Attribute filter requires min/max/attribute fields")

        return rule_value

class SchemaTransformationForm(forms.ModelForm):
    class Meta:
        model = SchemaTransformation
        fields = ['output_format', 'sample_rate', 'bit_depth', 'normalize_db']
        widgets = {
            'normalize_db': forms.NumberInput(attrs={'type': 'range', 'min': -12, 'max': 0, 'step': 0.1})
        }

    def clean_sample_rate(self):
        """Validate sample rate is in allowed values."""
        sample_rate = self.cleaned_data.get('sample_rate')
        allowed_rates = [44100, 48000, 96000, 192000]
        if sample_rate and sample_rate not in allowed_rates:
            raise forms.ValidationError(f"Sample rate must be one of {allowed_rates}")
        return sample_rate
```

**Django View Pattern (Auto-save AJAX):**
```python
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.catalog.models import SchemaRule, InputDirectory
import json

class PropertiesPanelView(TemplateView):
    template_name = 'properties/properties_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        directory_id = self.request.GET.get('directory_id')

        if directory_id:
            directory = InputDirectory.objects.get(id=directory_id)
            context['selected_directory'] = directory
            context['filters'] = SchemaRule.objects.filter(input_directory=directory).order_by('order')
            context['transformations'] = SchemaTransformation.objects.filter(input_directory=directory)

        return context

@require_POST
def save_rule(request):
    """AJAX endpoint to save rule (auto-save)."""
    data = json.loads(request.body)
    directory_id = data.get('directory_id')
    rule_type = data.get('rule_type')
    rule_value = data.get('rule_value')

    try:
        directory = InputDirectory.objects.get(id=directory_id)
        rule = SchemaRule.objects.create(
            input_directory=directory,
            rule_type=rule_type,
            rule_value=rule_value,
            logic_operator=data.get('logic_operator', 'AND')
        )
        return JsonResponse({'success': True, 'rule_id': rule.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
```

**JavaScript Auto-save Pattern (Local, NFR3):**
```javascript
// static/js/properties_panel.js
let saveTimeout;

function autoSaveRule(ruleData) {
    // Debounce: wait 500ms after last change before saving
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        fetch('/api/rules/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(ruleData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Rule saved', 'success');
            } else {
                showToast('Error: ' + data.error, 'error');
            }
        });
    }, 500);
}

// Example: keyword filter input
document.getElementById('keyword-input').addEventListener('input', function(e) {
    const ruleData = {
        directory_id: getSelectedDirectoryId(),
        rule_type: 'keyword',
        rule_value: { pattern: e.target.value, case_sensitive: false }
    };
    autoSaveRule(ruleData);
});

// Dynamic field addition
document.getElementById('add-filter-btn').addEventListener('click', function() {
    const filterType = document.getElementById('filter-type-select').value;

    if (filterType === 'keyword') {
        addKeywordFilter();
    } else if (filterType === 'extension') {
        addExtensionFilter();
    }
});

function addKeywordFilter() {
    const filterHtml = `
        <div class="filter-item" data-type="keyword">
            <label>Keyword Pattern:</label>
            <input type="text" class="keyword-input" placeholder="Enter pattern...">
            <button class="remove-filter-btn">Remove</button>
        </div>
    `;
    document.getElementById('filters-container').insertAdjacentHTML('beforeend', filterHtml);
}
```

**HTML Template Pattern:**
```html
<!-- templates/properties/properties_panel.html -->
{% extends "base.html" %}

{% block content %}
<div class="properties-panel">
    <h3>Properties: {{ selected_directory.path }}</h3>

    <!-- Filters Section -->
    <div class="filters-section">
        <h4>Filters</h4>
        <div class="logic-operator-toggle">
            <button class="logic-btn active" data-logic="AND">AND</button>
            <button class="logic-btn" data-logic="OR">OR</button>
        </div>

        <div id="filters-container">
            {% for filter in filters %}
            <div class="filter-item" data-id="{{ filter.id }}" data-type="{{ filter.rule_type }}">
                {% if filter.rule_type == 'keyword' %}
                    <label>Keyword:</label>
                    <input type="text" value="{{ filter.rule_value.pattern }}" class="keyword-input">
                {% elif filter.rule_type == 'extension' %}
                    <label>Extensions:</label>
                    <select multiple class="extension-select">
                        <option value=".wav" {% if '.wav' in filter.rule_value %}selected{% endif %}>.wav</option>
                        <option value=".mp3" {% if '.mp3' in filter.rule_value %}selected{% endif %}>.mp3</option>
                        <option value=".flac" {% if '.flac' in filter.rule_value %}selected{% endif %}>.flac</option>
                    </select>
                {% endif %}
                <button class="remove-filter-btn" data-id="{{ filter.id }}">Remove</button>
            </div>
            {% endfor %}
        </div>

        <button id="add-filter-btn">Add Filter</button>
    </div>

    <!-- Processing Rules Section -->
    <div class="rules-section">
        <h4>Processing Rules</h4>

        <div id="transformations-container">
            {% for transform in transformations %}
            <div class="transformation-item" data-id="{{ transform.id }}">
                <label>Output Format:</label>
                <select class="format-select">
                    <option value="WAV" {% if transform.output_format == 'WAV' %}selected{% endif %}>WAV</option>
                    <option value="MP3" {% if transform.output_format == 'MP3' %}selected{% endif %}>MP3</option>
                    <option value="FLAC" {% if transform.output_format == 'FLAC' %}selected{% endif %}>FLAC</option>
                </select>

                <label>Sample Rate:</label>
                <select class="sample-rate-select">
                    <option value="44100" {% if transform.sample_rate == 44100 %}selected{% endif %}>44.1 kHz</option>
                    <option value="48000" {% if transform.sample_rate == 48000 %}selected{% endif %}>48 kHz</option>
                    <option value="96000" {% if transform.sample_rate == 96000 %}selected{% endif %}>96 kHz</option>
                    <option value="192000" {% if transform.sample_rate == 192000 %}selected{% endif %}>192 kHz</option>
                </select>

                <label>Normalize: <span class="normalize-value">{{ transform.normalize_db }} dB</span></label>
                <input type="range" min="-12" max="0" step="0.1" value="{{ transform.normalize_db }}" class="normalize-slider">

                <button class="remove-rule-btn" data-id="{{ transform.id }}">Remove</button>
            </div>
            {% endfor %}
        </div>

        <button id="add-rule-btn">Add Processing Rule</button>
    </div>
</div>
{% endblock %}
```

### XML Rule Type Mapping (CR4 Compliance)
**All XML rule types must be supported:** [Source: requirements.md CR4]

1. **Keyword Filter** → `contains_expression()` from handlers/rules.py
   - UI: Text input
   - Storage: `{"pattern": "kick", "case_sensitive": false}`

2. **Extension Filter** → `contains_extensions()` from handlers/rules.py
   - UI: Multi-select dropdown
   - Storage: `[".wav", ".mp3", ".flac"]`

3. **Media Type Filter** → `contains_audio()/contains_video()` from handlers/rules.py
   - UI: Dropdown (audio/video/image)
   - Storage: `{"media_type": "audio"}`

4. **Attribute Filter** → Sample rate/bit depth range
   - UI: Min/max inputs
   - Storage: `{"attribute": "sample_rate", "min": 44100, "max": 48000}`

5. **Date Range Filter** → `between_datetime()` from handlers/rules.py
   - UI: Date pickers
   - Storage: `{"start_date": "2025-01-01", "end_date": "2025-12-31"}`

### Preservation Rules
**CR4 Compliance:** All XML rule types supported [Source: requirements.md CR4]
- UI must map to existing filter functions (handlers/rules.py)
- No new filter logic introduced (preserve algorithms)

**NFR3 Compliance:** No CDN dependencies [Source: requirements.md NFR3]
- All JavaScript served from `static/js/` directory
- No external form libraries (use vanilla JS)

**NFR4 Compliance:** Progressive enhancement with AJAX [Source: requirements.md NFR4]
- Auto-save works with JavaScript enabled
- Form submission works without JavaScript (fallback to POST)

---

## Dev Notes > Testing

### Test File Location
[Source: architecture/testing-strategy.md]
```
tests/
└── test_properties_panel.py
```

### Testing Standards
**Framework:** pytest + pytest-django [Source: architecture/tech-stack.md]

**Test Coverage Target:** 80%+ for properties panel and rule forms [Source: architecture/testing-strategy.md]

**Test Categories:**
1. **Unit Tests - Form Validation**
   - Test SchemaRuleForm validation for each rule type
   - Test SchemaTransformationForm validation
   - Test invalid rule_value structures

2. **Integration Tests - AJAX Auto-save**
   - Test auto-save endpoint with valid data
   - Test auto-save with invalid data (error handling)
   - Test debouncing (rapid changes)

3. **UI Tests - Dynamic Fields**
   - Test adding keyword filter
   - Test adding extension filter
   - Test adding transformation rule
   - Test removing filters/rules
   - Test AND/OR logic operator toggle

4. **CR4 Compliance Tests - All XML Rule Types**
   - Test keyword filter UI → contains_expression() mapping
   - Test extension filter UI → contains_extensions() mapping
   - Test media type filter UI → contains_audio/video() mapping
   - Test attribute filter UI → sample_rate/bit_depth range
   - Test date range filter UI → between_datetime() mapping

**Example Test:**
```python
import pytest
from django.test import TestCase, Client
from apps.catalog.models import SchemaRule, InputDirectory, Schema

class PropertiesPanelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)
        self.directory = InputDirectory.objects.create(
            schema=self.schema,
            path="/media/audio",
            is_input=True
        )

    def test_auto_save_keyword_filter(self):
        """Test auto-save creates keyword filter in database."""
        response = self.client.post(
            '/api/rules/save/',
            data={
                'directory_id': self.directory.id,
                'rule_type': 'keyword',
                'rule_value': {'pattern': 'kick', 'case_sensitive': False}
            },
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json()['success'] == True

        rule = SchemaRule.objects.get(input_directory=self.directory)
        assert rule.rule_type == 'keyword'
        assert rule.rule_value['pattern'] == 'kick'

    def test_form_validation_invalid_sample_rate(self):
        """Test SchemaTransformationForm rejects invalid sample rate."""
        from samplify.forms.rule_forms import SchemaTransformationForm

        form = SchemaTransformationForm(data={
            'output_format': 'WAV',
            'sample_rate': 99999,  # Invalid
            'bit_depth': 24
        })

        assert not form.is_valid()
        assert 'sample_rate' in form.errors

    def test_all_xml_rule_types_supported(self):
        """Test UI supports all XML rule types (CR4)."""
        rule_types = ['keyword', 'extension', 'media_type', 'attribute', 'date_range']

        for rule_type in rule_types:
            # Verify form accepts each rule type
            response = self.client.post(
                '/api/rules/save/',
                data={
                    'directory_id': self.directory.id,
                    'rule_type': rule_type,
                    'rule_value': self._get_sample_rule_value(rule_type)
                },
                content_type='application/json'
            )
            assert response.status_code == 200

    def _get_sample_rule_value(self, rule_type):
        """Helper to generate sample rule_value for testing."""
        if rule_type == 'keyword':
            return {'pattern': 'test'}
        elif rule_type == 'extension':
            return ['.wav', '.mp3']
        elif rule_type == 'media_type':
            return {'media_type': 'audio'}
        elif rule_type == 'attribute':
            return {'attribute': 'sample_rate', 'min': 44100, 'max': 48000}
        elif rule_type == 'date_range':
            return {'start_date': '2025-01-01', 'end_date': '2025-12-31'}
```

**Running Tests:**
```bash
# Run properties panel tests
pytest tests/test_properties_panel.py -v

# Run with coverage
pytest tests/test_properties_panel.py --cov=samplify.views.properties_panel --cov=samplify.forms.rule_forms --cov-report=html

# Test CR4 compliance
pytest tests/test_properties_panel.py::test_all_xml_rule_types_supported -v
```

---

## Definition of Done
- [ ] Properties panel implemented
- [ ] Filter CRUD functional
- [ ] Processing rule CRUD functional
- [ ] AND/OR logic selector working
- [ ] Auto-save tested
- [ ] Documentation updated with filter/rule configuration instructions

---

## Risk Assessment
- **Primary Risk:** UI doesn't support all filter/rule types (CR4)
- **Mitigation:** Validate against XML templates, comprehensive testing
- **Rollback:** Revert to XML configuration

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
