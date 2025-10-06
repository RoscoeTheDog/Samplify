# Story 1.10: Schema Management UI (CRUD)

## Status
**Approved**

---

## User Story
As a **user**,
I want **a web interface to create, read, update, and delete schemas**,
So that **I can manage processing configurations without editing XML files**.

---

## Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (Schema models), Story 1.1 (Django templates)
- Technology: Django views/templates, forms, AJAX
- Follows pattern: Django CRUD pattern, progressive enhancement
- Touch points: Schema database, web UI

---

## Acceptance Criteria

**Functional Requirements:**
1. Schema list view displays all saved schemas
2. Schema create form includes:
   - Name (required, unique)
   - Description (optional)
   - Active status (checkbox)
3. Schema edit form allows modification of all fields
4. Schema delete confirms before removal (with cascade warning)
5. Only one schema can be active at a time (validation)
6. AJAX-based save/load operations (no page refresh)
7. Success/error messages displayed to user

**Integration Requirements:**
8. Integrates with Schema model (Story 1.2B)
9. Uses base template from Story 1.1
10. Static assets served locally (NFR3)
11. Progressive enhancement (works without JavaScript)

**Quality Requirements:**
12. Form validation prevents duplicate schema names
13. Active schema toggle works correctly (one active only)
14. Delete cascades to related rules/transformations
15. UI responsive and functional on modern browsers

---

## Tasks / Subtasks

- [ ] **Task 1: Create Django views for CRUD operations** (AC: 1, 3, 4, 8)
  - [ ] Create `samplify/views/schema_crud.py`
  - [ ] Implement SchemaListView (displays all schemas)
  - [ ] Implement SchemaCreateView (form for new schema)
  - [ ] Implement SchemaUpdateView (edit existing schema)
  - [ ] Implement SchemaDeleteView (confirm and delete)

- [ ] **Task 2: Create Django forms** (AC: 2, 12)
  - [ ] Create `samplify/forms/schema_forms.py`
  - [ ] Implement SchemaForm with fields: name, description, is_active
  - [ ] Add validation for unique schema name
  - [ ] Add custom validation for single active schema (model clean method)

- [ ] **Task 3: Create HTML templates** (AC: 1, 2, 3, 4, 9)
  - [ ] Create `templates/schemas/schema_list.html` (list view)
  - [ ] Create `templates/schemas/schema_form.html` (create/edit form)
  - [ ] Create `templates/schemas/schema_confirm_delete.html` (delete confirmation)
  - [ ] Extend base template from Story 1.1

- [ ] **Task 4: Add AJAX enhancements** (AC: 6, 7, 11)
  - [ ] Add JavaScript handlers for form submission (AJAX POST)
  - [ ] Add AJAX handlers for delete confirmation
  - [ ] Display success/error messages without page refresh
  - [ ] Ensure progressive enhancement (works without JS)

- [ ] **Task 5: Implement active schema toggle** (AC: 5, 13)
  - [ ] Add model validation: only one active schema allowed
  - [ ] Deactivate other schemas when one is activated
  - [ ] Add UI indicator for active schema (green checkmark icon)

- [ ] **Task 6: Add cascade delete handling** (AC: 4, 14)
  - [ ] Configure CASCADE on ForeignKey relationships (models.py)
  - [ ] Display warning message listing related objects to be deleted
  - [ ] Test cascade delete with rules, transformations, directories

- [ ] **Task 7: Add URL patterns and routing** (AC: all)
  - [ ] Add URL patterns in `samplify/urls.py`
  - [ ] Routes: /schemas/, /schemas/create/, /schemas/<id>/edit/, /schemas/<id>/delete/
  - [ ] Link schema list view to main navigation

- [ ] **Task 8: Testing** (AC: 12, 13, 14, 15)
  - [ ] Unit tests for schema form validation
  - [ ] Integration tests for CRUD views
  - [ ] Test active schema toggle (single active validation)
  - [ ] Test cascade delete
  - [ ] Test AJAX functionality
  - [ ] Cross-browser testing (Chrome, Firefox, Edge)

---

## Dev Notes

### Previous Story Insights
**From Story 1.2B (Schema Models):**
- Schema model structure defined [Source: Story 1.2B]
- Foreign key relationships established (CASCADE on delete)
- is_active field for single active schema enforcement

**From Story 1.1 (Django Project Setup):**
- Base template created at `templates/base.html` [Source: Story 1.1]
- Static files configuration ready
- Bootstrap/CSS framework available

### File Locations (Source Tree)
**Views:** [Source: architecture/source-tree.md]
```
samplify/
└── views/
    └── schema_crud.py              # Create this file
```

**Forms:**
```
samplify/
└── forms/
    └── schema_forms.py             # Create this file
```

**Templates:**
```
templates/
└── schemas/
    ├── schema_list.html           # Create this file
    ├── schema_form.html           # Create this file
    └── schema_confirm_delete.html # Create this file
```

**Test Location:**
```
tests/
└── test_schema_crud.py            # Create this file
```

### Data Models
**Schema Model (Story 1.2B):** [Source: architecture/database-schema-design.md]
```python
class Schema(models.Model):
    name = CharField(max_length=255, unique=True)
    description = TextField(blank=True, null=True)
    is_active = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        # Ensure only one active schema
        if self.is_active:
            Schema.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)

    def __str__(self):
        return self.name
```

### Django CRUD Pattern
**Class-Based Views (CBV):** [Source: Django 4.2 docs, architecture/tech-stack.md]

**ListView for Schema List:**
```python
from django.views.generic import ListView
from apps.schemas.models import Schema

class SchemaListView(ListView):
    model = Schema
    template_name = 'schemas/schema_list.html'
    context_object_name = 'schemas'
    paginate_by = 20

    def get_queryset(self):
        return Schema.objects.all().order_by('-created_at')
```

**CreateView for New Schema:**
```python
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from samplify.forms.schema_forms import SchemaForm

class SchemaCreateView(CreateView):
    model = Schema
    form_class = SchemaForm
    template_name = 'schemas/schema_form.html'
    success_url = reverse_lazy('schema_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Schema "{self.object.name}" created successfully')
        return response
```

**UpdateView for Edit Schema:**
```python
from django.views.generic.edit import UpdateView

class SchemaUpdateView(UpdateView):
    model = Schema
    form_class = SchemaForm
    template_name = 'schemas/schema_form.html'
    success_url = reverse_lazy('schema_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Schema "{self.object.name}" updated successfully')
        return response
```

**DeleteView for Delete Schema:**
```python
from django.views.generic.edit import DeleteView

class SchemaDeleteView(DeleteView):
    model = Schema
    template_name = 'schemas/schema_confirm_delete.html'
    success_url = reverse_lazy('schema_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related objects count for cascade warning
        context['related_rules_count'] = self.object.rules.count()
        context['related_transforms_count'] = self.object.transformations.count()
        context['related_dirs_count'] = self.object.input_directories.count() + self.object.output_directories.count()
        return context

    def delete(self, request, *args, **kwargs):
        schema_name = self.get_object().name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Schema "{schema_name}" deleted successfully')
        return response
```

### Django Forms Pattern
**SchemaForm:**
```python
from django import forms
from apps.schemas.models import Schema

class SchemaForm(forms.ModelForm):
    class Meta:
        model = Schema
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter schema name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        # Check for unique name (excluding current instance for updates)
        if Schema.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(f'Schema with name "{name}" already exists')
        return name

    def clean(self):
        cleaned_data = super().clean()
        is_active = cleaned_data.get('is_active')

        # Ensure only one active schema
        if is_active:
            active_schemas = Schema.objects.filter(is_active=True).exclude(pk=self.instance.pk)
            if active_schemas.exists():
                # Auto-deactivate others (handled in model.clean(), but confirm here)
                pass

        return cleaned_data
```

### HTML Templates Pattern
**schema_list.html:**
```html
{% extends 'base.html' %}

{% block title %}Schema Management{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Schema Management</h2>
        <a href="{% url 'schema_create' %}" class="btn btn-primary">Create New Schema</a>
    </div>

    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}

    <table class="table table-striped">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Active</th>
                <th>Created</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for schema in schemas %}
            <tr>
                <td>{{ schema.name }}</td>
                <td>{{ schema.description|truncatewords:10 }}</td>
                <td>
                    {% if schema.is_active %}
                        <span class="badge bg-success">Active</span>
                    {% else %}
                        <span class="badge bg-secondary">Inactive</span>
                    {% endif %}
                </td>
                <td>{{ schema.created_at|date:"Y-m-d" }}</td>
                <td>
                    <a href="{% url 'schema_update' schema.pk %}" class="btn btn-sm btn-warning">Edit</a>
                    <a href="{% url 'schema_delete' schema.pk %}" class="btn btn-sm btn-danger">Delete</a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5" class="text-center">No schemas found. Create one to get started.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% if is_paginated %}
        <nav>
            <ul class="pagination">
                {% if page_obj.has_previous %}
                    <li class="page-item"><a class="page-link" href="?page=1">First</a></li>
                    <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">Previous</a></li>
                {% endif %}
                <li class="page-item active"><span class="page-link">{{ page_obj.number }} / {{ page_obj.paginator.num_pages }}</span></li>
                {% if page_obj.has_next %}
                    <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">Next</a></li>
                    <li class="page-item"><a class="page-link" href="?page={{ page_obj.paginator.num_pages }}">Last</a></li>
                {% endif %}
            </ul>
        </nav>
    {% endif %}
</div>
{% endblock %}
```

**schema_form.html:**
```html
{% extends 'base.html' %}

{% block title %}{% if form.instance.pk %}Edit{% else %}Create{% endif %} Schema{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>{% if form.instance.pk %}Edit{% else %}Create{% endif %} Schema</h2>

    <form method="post" id="schema-form">
        {% csrf_token %}

        <div class="mb-3">
            {{ form.name.label_tag }}
            {{ form.name }}
            {% if form.name.errors %}
                <div class="text-danger">{{ form.name.errors }}</div>
            {% endif %}
        </div>

        <div class="mb-3">
            {{ form.description.label_tag }}
            {{ form.description }}
            {% if form.description.errors %}
                <div class="text-danger">{{ form.description.errors }}</div>
            {% endif %}
        </div>

        <div class="mb-3 form-check">
            {{ form.is_active }}
            {{ form.is_active.label_tag }}
            {% if form.is_active.errors %}
                <div class="text-danger">{{ form.is_active.errors }}</div>
            {% endif %}
            <small class="form-text text-muted">Only one schema can be active at a time</small>
        </div>

        <button type="submit" class="btn btn-primary">Save Schema</button>
        <a href="{% url 'schema_list' %}" class="btn btn-secondary">Cancel</a>
    </form>
</div>

<script>
// AJAX form submission (progressive enhancement)
document.getElementById('schema-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch(this.action || window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Schema saved successfully');
            window.location.href = '{% url "schema_list" %}';
        } else {
            alert('Error: ' + data.errors);
        }
    })
    .catch(error => {
        // Fallback: submit form normally
        this.submit();
    });
});
</script>
{% endblock %}
```

### URL Patterns
**samplify/urls.py:**
```python
from django.urls import path
from samplify.views.schema_crud import (
    SchemaListView, SchemaCreateView, SchemaUpdateView, SchemaDeleteView
)

urlpatterns = [
    # Schema CRUD
    path('schemas/', SchemaListView.as_view(), name='schema_list'),
    path('schemas/create/', SchemaCreateView.as_view(), name='schema_create'),
    path('schemas/<int:pk>/edit/', SchemaUpdateView.as_view(), name='schema_update'),
    path('schemas/<int:pk>/delete/', SchemaDeleteView.as_view(), name='schema_delete'),
]
```

---

## Dev Notes > Testing

### Test File Location
[Source: architecture/testing-strategy.md]
```
tests/
└── test_schema_crud.py
```

### Testing Standards
**Framework:** pytest + pytest-django [Source: architecture/tech-stack.md]

**Test Coverage Target:** 85%+ for CRUD views and forms

**Test Categories:**
1. **Unit Tests - Form Validation**
   - Test unique schema name validation
   - Test active schema toggle (single active)
   - Test required/optional fields

2. **Integration Tests - CRUD Views**
   - Test schema list view displays all schemas
   - Test schema create view creates new schema
   - Test schema update view modifies existing schema
   - Test schema delete view removes schema and cascades

3. **UI Tests - AJAX Functionality**
   - Test form submission via AJAX
   - Test success/error message display
   - Test progressive enhancement (works without JS)

4. **Cross-Browser Tests**
   - Test on Chrome, Firefox, Edge
   - Test responsive layout

**Example Test:**
```python
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from apps.schemas.models import Schema, SchemaRule

class SchemaCRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.schema = Schema.objects.create(name="Test Schema", is_active=True)

    def test_schema_list_view(self):
        """Test schema list view displays all schemas."""
        response = self.client.get(reverse('schema_list'))

        assert response.status_code == 200
        assert self.schema.name in str(response.content)

    def test_schema_create_view(self):
        """Test schema create view creates new schema."""
        response = self.client.post(reverse('schema_create'), {
            'name': 'New Schema',
            'description': 'Test description',
            'is_active': False
        })

        assert response.status_code == 302  # Redirect after success
        assert Schema.objects.filter(name='New Schema').exists()

    def test_schema_update_view(self):
        """Test schema update view modifies existing schema."""
        response = self.client.post(reverse('schema_update', args=[self.schema.pk]), {
            'name': 'Updated Schema',
            'description': 'Updated description',
            'is_active': True
        })

        self.schema.refresh_from_db()
        assert self.schema.name == 'Updated Schema'

    def test_schema_delete_view(self):
        """Test schema delete view removes schema."""
        response = self.client.post(reverse('schema_delete', args=[self.schema.pk]))

        assert response.status_code == 302
        assert not Schema.objects.filter(pk=self.schema.pk).exists()

    def test_single_active_schema_validation(self):
        """Test only one schema can be active at a time."""
        # Create second schema and activate it
        schema2 = Schema.objects.create(name="Schema 2", is_active=True)

        # First schema should be deactivated
        self.schema.refresh_from_db()
        assert not self.schema.is_active
        assert schema2.is_active

    def test_cascade_delete(self):
        """Test cascade delete removes related objects."""
        # Create related rules
        SchemaRule.objects.create(
            schema=self.schema,
            rule_type='keyword',
            field_name='filename',
            operator='contains',
            value='test'
        )

        # Delete schema
        self.client.post(reverse('schema_delete', args=[self.schema.pk]))

        # Verify cascade
        assert not Schema.objects.filter(pk=self.schema.pk).exists()
        assert not SchemaRule.objects.filter(schema=self.schema).exists()

    def test_duplicate_name_validation(self):
        """Test form validation prevents duplicate schema names."""
        from samplify.forms.schema_forms import SchemaForm

        form = SchemaForm(data={
            'name': 'Test Schema',  # Duplicate name
            'description': '',
            'is_active': False
        })

        assert not form.is_valid()
        assert 'name' in form.errors
```

**Running Tests:**
```bash
# Run all schema CRUD tests
pytest tests/test_schema_crud.py -v

# Run with coverage
pytest tests/test_schema_crud.py --cov=samplify.views.schema_crud --cov=samplify.forms.schema_forms --cov-report=html

# Test form validation
pytest tests/test_schema_crud.py::test_single_active_schema_validation -v

# Test cascade delete
pytest tests/test_schema_crud.py::test_cascade_delete -v
```

---

## Definition of Done
- [ ] Schema CRUD views implemented
- [ ] Forms validated and working
- [ ] AJAX save/load functional
- [ ] Delete cascade verified
- [ ] UI tested on Chrome/Firefox/Edge
- [ ] Documentation updated with schema management instructions

---

## Risk Assessment
- **Primary Risk:** UI doesn't support all schema features (CR4)
- **Mitigation:** Validate against imported XML templates, comprehensive testing
- **Rollback:** Revert to XML template editing

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
