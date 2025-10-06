# Story 1.9: XML Template Import/Export Tool

## Status
**Approved**

---

## User Story
As a **user**,
I want **tools to import existing XML templates into the database and export schemas as XML templates**,
So that **I can migrate from XML configuration to the web-based schema designer and share templates across systems**.

---

## Story Context
**Existing System Integration:**
- Integrates with: Story 1.2B (Schema models), Story 1.10 (Schema Management UI), existing xml_handler.py logic
- Technology: Django management command + API endpoints, ElementTree for XML parsing/generation
- Follows pattern: CR4 schema functionality preservation, FR18/NFR14 template import/export
- Touch points: XML template parsing, schema database population, UI Import/Export buttons

---

## Acceptance Criteria

**Import Functionality (FR18):**
1. XML import tool created as Django management command (`manage.py import_xml_template`)
2. Import API endpoint created for UI integration (`POST /api/schemas/import-xml/`)
3. Tool accepts XML template file path as argument (CLI) or file upload (API)
4. Tool parses XML template using ElementTree
5. Tool maps XML elements to Schema models:
   - Template name → Schema.name
   - Rules → SchemaRule records
   - Transformations → SchemaTransformation records
   - Directory mappings → DirectoryMapping records
6. Tool supports ALL XML rule types (CR4):
   - Keyword filters
   - File type filters
   - Media attribute filters
   - AND/OR logic governors
7. Tool validates imported schema (rules match XML exactly)
8. Tool provides detailed import report

**Export Functionality (FR18):**
9. XML export tool created as Django management command (`manage.py export_xml_template`)
10. Export API endpoint created for UI integration (`GET /api/schemas/{id}/export-xml/`)
11. Tool accepts schema ID as argument
12. Tool generates XML template from Schema model data
13. Tool preserves XML structure compatible with existing xml_handler.py
14. Exported XML can be re-imported without data loss
15. Export includes all schema components (rules, transformations, mappings)

**UI Integration (FR18):**
16. [Import XML] button added to Input Files table header
17. [Export XML] button added to Input Files table header
18. [Import XML] button added to Output Destinations table header
19. [Export XML] button added to Output Destinations table header
20. Import button triggers file upload dialog and calls import API
21. Export button downloads generated XML file to browser
22. Import/Export operations provide user feedback (success/error messages)

**Database Storage (NFR14):**
23. Imported XML templates stored in database with original XML preserved
24. Schema table includes xml_source field (TextField) for XML storage
25. Database indexing enabled for efficient template querying
26. Templates retrievable by name, date, or source type (imported vs web-created)

**Integration Requirements:**
27. Integrates with Schema models (Story 1.2B)
28. Preserves all XML template functionality (CR4)
29. Validates against existing xml_handler.py logic
30. Creates database records atomically (transaction)
31. UI buttons integrate with Schema Management UI (Story 1.10)

**Quality Requirements:**
32. Import succeeds for all existing XML templates
33. Imported schemas function identically to XML originals
34. Export → Import round-trip preserves all data
35. Import/Export errors provide actionable messages
36. Rollback works correctly on import failure
37. UI Import/Export buttons are intuitive and responsive

---

## Tasks / Subtasks

- [ ] **Task 1: Create XML import management command** (AC: 1, 3, 4)
  - [ ] Create `samplify/management/commands/import_xml_template.py`
  - [ ] Implement BaseCommand with handle() method
  - [ ] Add command-line argument for XML file path
  - [ ] Parse XML using ElementTree library

- [ ] **Task 2: Implement XML to Django model mapping** (AC: 5, 6, 28)
  - [ ] Map template name to Schema.name
  - [ ] Map XML rules to SchemaRule records (keyword, file type, media attribute filters)
  - [ ] Map XML transformations to SchemaTransformation records
  - [ ] Map XML directory mappings to InputDirectory/OutputDirectory records
  - [ ] Support AND/OR logic operators from XML
  - [ ] **CRITICAL**: Preserve all XML rule types exactly (CR4)

- [ ] **Task 3: Add import validation and reporting** (AC: 7, 8, 32)
  - [ ] Validate XML schema against existing xml_handler.py logic
  - [ ] Compare imported rules with XML source (exact match)
  - [ ] Generate detailed import report (success/failure, rule count, warnings)
  - [ ] Test with all existing XML templates

- [ ] **Task 4: Create XML export management command** (AC: 9, 11, 12)
  - [ ] Create `samplify/management/commands/export_xml_template.py`
  - [ ] Accept schema ID as argument
  - [ ] Query Schema model and related records (rules, transformations, mappings)
  - [ ] Generate XML using ElementTree

- [ ] **Task 5: Implement Django model to XML mapping** (AC: 13, 14, 15)
  - [ ] Map Schema.name to template name element
  - [ ] Map SchemaRule records to XML rules (preserve all types)
  - [ ] Map SchemaTransformation records to XML transformations
  - [ ] Map InputDirectory/OutputDirectory to XML directory mappings
  - [ ] Preserve XML structure compatible with xml_handler.py
  - [ ] Test export → import round-trip (no data loss)

- [ ] **Task 6: Create import/export API endpoints** (AC: 2, 10, 20, 21)
  - [ ] Create `POST /api/schemas/import-xml/` endpoint (file upload)
  - [ ] Create `GET /api/schemas/{id}/export-xml/` endpoint (XML download)
  - [ ] Handle multipart/form-data for file uploads
  - [ ] Return XML as downloadable file (content-disposition header)
  - [ ] Add error handling and validation

- [ ] **Task 7: Add UI Import/Export buttons** (AC: 16-22, 31)
  - [ ] Add [Import XML] button to Input Files table header
  - [ ] Add [Export XML] button to Input Files table header
  - [ ] Add [Import XML] button to Output Destinations table header
  - [ ] Add [Export XML] button to Output Destinations table header
  - [ ] Implement JavaScript file upload handler (AJAX POST)
  - [ ] Implement JavaScript download handler (fetch and trigger browser download)
  - [ ] Add success/error message display

- [ ] **Task 8: Add database XML storage** (AC: 23, 24, 25, 26)
  - [ ] Add xml_source TextField to Schema model (migration)
  - [ ] Store original XML during import
  - [ ] Add database index on xml_source for querying
  - [ ] Add source_type field (choices: 'imported', 'web-created')
  - [ ] Query schemas by name, date, or source_type

- [ ] **Task 9: Testing** (AC: 32, 33, 34, 35, 36, 37)
  - [ ] Unit tests for XML parsing (import)
  - [ ] Unit tests for XML generation (export)
  - [ ] Integration test: Import all existing XML templates
  - [ ] Integration test: Export → Import round-trip (data preservation)
  - [ ] Test transaction rollback on import failure
  - [ ] UI test: Import/Export button functionality
  - [ ] Test error messages (invalid XML, missing fields)

---

## Dev Notes

### Previous Story Insights
**From Story 1.2B (Schema Models):**
- Schema model structure defined [Source: Story 1.2B]
- SchemaRule, SchemaTransformation, DirectoryMapping models ready
- Foreign key relationships established

### File Locations (Source Tree)
**Management Commands:** [Source: architecture/source-tree.md]
```
samplify/
└── management/
    └── commands/
        ├── import_xml_template.py    # Create this file
        └── export_xml_template.py    # Create this file
```

**API Endpoints:**
```
samplify/
└── api/
    └── views/
        └── schema_import_export.py   # Create this file
```

**Test Location:**
```
tests/
├── test_xml_import.py               # Create this file
└── test_xml_export.py               # Create this file
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
    # Add for Story 1.9:
    xml_source = TextField(blank=True, null=True)  # Store original XML
    source_type = CharField(
        max_length=20,
        choices=[('imported', 'Imported'), ('web', 'Web Created')],
        default='web'
    )
```

**SchemaRule Model:**
```python
class SchemaRule(models.Model):
    schema = ForeignKey(Schema, on_delete=CASCADE, related_name='rules')
    rule_type = CharField(choices=['keyword', 'extension', 'media_type', 'attribute'])
    field_name = CharField(max_length=100)  # e.g., 'filename', 'extension', 'sample_rate'
    operator = CharField(choices=['contains', 'equals', 'between', 'gt', 'lt'])
    value = CharField(max_length=500)
    logic_operator = CharField(choices=['AND', 'OR'], default='AND')
    order = IntegerField(default=0)
```

### XML Template Structure (Brownfield)
**Brownfield XML Source:** `templates/` directory [Source: architecture/source-tree.md]

**Example XML Template:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<template name="Audio Normalization">
    <description>Normalize audio files to -6dB</description>
    <rules logic="AND">
        <rule type="keyword" field="filename" operator="contains">drum</rule>
        <rule type="extension" field="extension" operator="equals">.wav</rule>
        <rule type="attribute" field="sample_rate" operator="between">44100,48000</rule>
    </rules>
    <transformations>
        <transform type="normalize" value="-6"/>
        <transform type="format" value="WAV"/>
        <transform type="sample_rate" value="48000"/>
    </transformations>
    <directories>
        <input path="/media/audio/drums/" recursive="true"/>
        <output path="/media/output/normalized/" create="true"/>
    </directories>
</template>
```

### XML Import Pattern
**ElementTree Parsing:**
```python
import xml.etree.ElementTree as ET
from django.db import transaction
from apps.schemas.models import Schema, SchemaRule, SchemaTransformation, InputDirectory, OutputDirectory

def import_xml_template(xml_file_path):
    """Import XML template into database."""
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Read original XML for storage
    with open(xml_file_path, 'r') as f:
        xml_source = f.read()

    with transaction.atomic():
        # Create Schema
        schema = Schema.objects.create(
            name=root.attrib['name'],
            description=root.find('description').text,
            xml_source=xml_source,
            source_type='imported'
        )

        # Import Rules
        rules_elem = root.find('rules')
        logic_operator = rules_elem.attrib.get('logic', 'AND')

        for idx, rule_elem in enumerate(rules_elem.findall('rule')):
            SchemaRule.objects.create(
                schema=schema,
                rule_type=rule_elem.attrib['type'],
                field_name=rule_elem.attrib['field'],
                operator=rule_elem.attrib['operator'],
                value=rule_elem.text,
                logic_operator=logic_operator,
                order=idx
            )

        # Import Transformations
        transforms_elem = root.find('transformations')
        for transform_elem in transforms_elem.findall('transform'):
            SchemaTransformation.objects.create(
                schema=schema,
                transform_type=transform_elem.attrib['type'],
                value=transform_elem.attrib['value']
            )

        # Import Directories
        dirs_elem = root.find('directories')
        for input_elem in dirs_elem.findall('input'):
            InputDirectory.objects.create(
                schema=schema,
                path=input_elem.attrib['path'],
                recursive=input_elem.attrib.get('recursive', 'true') == 'true'
            )

        for output_elem in dirs_elem.findall('output'):
            OutputDirectory.objects.create(
                schema=schema,
                path=output_elem.attrib['path'],
                create_if_missing=output_elem.attrib.get('create', 'false') == 'true'
            )

    return schema
```

### XML Export Pattern
**ElementTree Generation:**
```python
import xml.etree.ElementTree as ET
from xml.dom import minidom

def export_xml_template(schema_id):
    """Export schema to XML template."""
    schema = Schema.objects.get(id=schema_id)

    # Create root element
    root = ET.Element('template', name=schema.name)

    # Add description
    desc_elem = ET.SubElement(root, 'description')
    desc_elem.text = schema.description or ''

    # Add rules
    rules = schema.rules.order_by('order')
    logic_op = rules.first().logic_operator if rules.exists() else 'AND'
    rules_elem = ET.SubElement(root, 'rules', logic=logic_op)

    for rule in rules:
        rule_elem = ET.SubElement(
            rules_elem, 'rule',
            type=rule.rule_type,
            field=rule.field_name,
            operator=rule.operator
        )
        rule_elem.text = rule.value

    # Add transformations
    transforms_elem = ET.SubElement(root, 'transformations')
    for transform in schema.transformations.all():
        ET.SubElement(
            transforms_elem, 'transform',
            type=transform.transform_type,
            value=transform.value
        )

    # Add directories
    dirs_elem = ET.SubElement(root, 'directories')
    for input_dir in schema.input_directories.all():
        ET.SubElement(
            dirs_elem, 'input',
            path=input_dir.path,
            recursive='true' if input_dir.recursive else 'false'
        )

    for output_dir in schema.output_directories.all():
        ET.SubElement(
            dirs_elem, 'output',
            path=output_dir.path,
            create='true' if output_dir.create_if_missing else 'false'
        )

    # Pretty print XML
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    return xml_str
```

### API Endpoints Pattern
**Import Endpoint (POST /api/schemas/import-xml/):**
```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def import_xml_api(request):
    """API endpoint for XML import."""
    try:
        xml_file = request.FILES.get('xml_file')
        if not xml_file:
            return JsonResponse({'error': 'No file provided'}, status=400)

        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
            tmp.write(xml_file.read())
            tmp_path = tmp.name

        # Import XML
        schema = import_xml_template(tmp_path)

        # Clean up temp file
        import os
        os.unlink(tmp_path)

        return JsonResponse({
            'success': True,
            'schema_id': schema.id,
            'schema_name': schema.name,
            'message': f'Successfully imported template: {schema.name}'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

**Export Endpoint (GET /api/schemas/{id}/export-xml/):**
```python
from django.http import HttpResponse

@require_http_methods(["GET"])
def export_xml_api(request, schema_id):
    """API endpoint for XML export."""
    try:
        xml_str = export_xml_template(schema_id)

        # Return as downloadable file
        response = HttpResponse(xml_str, content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="schema_{schema_id}.xml"'
        return response

    except Schema.DoesNotExist:
        return JsonResponse({'error': 'Schema not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

### UI Integration Pattern
**JavaScript Import Handler:**
```javascript
// Import XML button handler
document.getElementById('import-xml-btn').addEventListener('click', function() {
    // Trigger file input
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.xml';

    fileInput.onchange = function(e) {
        const file = e.target.files[0];
        const formData = new FormData();
        formData.append('xml_file', file);

        // Upload file via AJAX
        fetch('/api/schemas/import-xml/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Success: ${data.message}`);
                location.reload();  // Refresh to show new schema
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            alert(`Error: ${error}`);
        });
    };

    fileInput.click();
});
```

**JavaScript Export Handler:**
```javascript
// Export XML button handler
document.getElementById('export-xml-btn').addEventListener('click', function() {
    const schemaId = this.dataset.schemaId;

    // Fetch XML file
    fetch(`/api/schemas/${schemaId}/export-xml/`)
        .then(response => response.blob())
        .then(blob => {
            // Trigger browser download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `schema_${schemaId}.xml`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            alert(`Error: ${error}`);
        });
});
```

### CR4 Validation Requirements
**All XML Rule Types Must Be Supported:** [Source: requirements.md CR4]
1. ✅ Keyword filters (filename contains)
2. ✅ File type filters (extension equals)
3. ✅ Media attribute filters (sample_rate between, bit_depth gt/lt)
4. ✅ AND/OR logic governors
5. ✅ Nested rule groups (if XML supports)

**Validation Pattern:**
```python
def validate_imported_schema(schema, xml_file_path):
    """Validate imported schema matches XML exactly."""
    # Re-parse XML
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Validate rule count
    xml_rules = root.find('rules').findall('rule')
    db_rules = schema.rules.all()
    assert len(xml_rules) == db_rules.count(), "Rule count mismatch"

    # Validate each rule
    for xml_rule, db_rule in zip(xml_rules, db_rules):
        assert xml_rule.attrib['type'] == db_rule.rule_type
        assert xml_rule.attrib['field'] == db_rule.field_name
        assert xml_rule.attrib['operator'] == db_rule.operator
        assert xml_rule.text == db_rule.value

    # Validate transformations
    xml_transforms = root.find('transformations').findall('transform')
    db_transforms = schema.transformations.all()
    assert len(xml_transforms) == db_transforms.count(), "Transform count mismatch"

    # Validate directories
    xml_inputs = root.find('directories').findall('input')
    db_inputs = schema.input_directories.all()
    assert len(xml_inputs) == db_inputs.count(), "Input directory count mismatch"

    return True  # Validation passed
```

---

## Dev Notes > Testing

### Test File Location
[Source: architecture/testing-strategy.md]
```
tests/
├── test_xml_import.py
└── test_xml_export.py
```

### Testing Standards
**Framework:** pytest + pytest-django [Source: architecture/tech-stack.md]

**Test Coverage Target:** 90%+ for XML import/export (critical for CR4 compliance)

**Test Categories:**
1. **Unit Tests - XML Parsing**
   - Test XML parsing with ElementTree
   - Test all rule types (keyword, extension, attribute)
   - Test AND/OR logic operators
   - Test malformed XML handling

2. **Integration Tests - Import Functionality**
   - Import all existing XML templates (from templates/ directory)
   - Validate database records created correctly
   - Test transaction rollback on import failure
   - Test duplicate template name handling

3. **Integration Tests - Export Functionality**
   - Export schema to XML
   - Validate XML structure (well-formed, valid)
   - Test export → import round-trip (data preservation)
   - Test all schema components included (rules, transforms, directories)

4. **API Tests - Import/Export Endpoints**
   - Test POST /api/schemas/import-xml/ with file upload
   - Test GET /api/schemas/{id}/export-xml/ download
   - Test error handling (invalid file, missing schema)
   - Test CSRF protection (if enabled)

5. **UI Tests - Import/Export Buttons**
   - Test button click triggers file dialog
   - Test file upload and success message
   - Test export download to browser
   - Test error message display

6. **CR4 Validation Tests**
   - Test all XML rule types preserved
   - Side-by-side comparison: XML vs imported schema
   - Test schema functionality identical to XML original

**Example Test:**
```python
import pytest
from django.test import TestCase, TransactionTestCase
from apps.schemas.models import Schema, SchemaRule, SchemaTransformation
from samplify.management.commands.import_xml_template import import_xml_template
from samplify.management.commands.export_xml_template import export_xml_template
import xml.etree.ElementTree as ET
import os

class XMLImportTest(TestCase):
    def test_import_all_existing_templates(self):
        """Import all existing XML templates from templates/ directory."""
        templates_dir = 'templates/'
        xml_files = [f for f in os.listdir(templates_dir) if f.endswith('.xml')]

        for xml_file in xml_files:
            xml_path = os.path.join(templates_dir, xml_file)

            # Import XML
            schema = import_xml_template(xml_path)

            # Validate import
            assert schema is not None
            assert schema.name is not None
            assert schema.rules.count() > 0

    def test_import_all_rule_types(self):
        """Test import supports all XML rule types (CR4)."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <template name="All Rule Types Test">
            <rules logic="AND">
                <rule type="keyword" field="filename" operator="contains">drum</rule>
                <rule type="extension" field="extension" operator="equals">.wav</rule>
                <rule type="attribute" field="sample_rate" operator="between">44100,48000</rule>
            </rules>
            <transformations>
                <transform type="normalize" value="-6"/>
            </transformations>
            <directories>
                <input path="/test/" recursive="true"/>
                <output path="/output/" create="true"/>
            </directories>
        </template>'''

        # Write to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = tmp.name

        # Import
        schema = import_xml_template(tmp_path)

        # Validate all rule types
        rules = schema.rules.all()
        assert rules.count() == 3
        assert rules[0].rule_type == 'keyword'
        assert rules[1].rule_type == 'extension'
        assert rules[2].rule_type == 'attribute'

        # Cleanup
        os.unlink(tmp_path)

class XMLExportTest(TestCase):
    def test_export_import_roundtrip(self):
        """Test export → import preserves all data."""
        # Create schema
        schema = Schema.objects.create(name="Roundtrip Test")
        SchemaRule.objects.create(
            schema=schema,
            rule_type='keyword',
            field_name='filename',
            operator='contains',
            value='test'
        )

        # Export to XML
        xml_str = export_xml_template(schema.id)

        # Write to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            tmp.write(xml_str)
            tmp_path = tmp.name

        # Re-import
        schema2 = import_xml_template(tmp_path)

        # Validate data preserved
        assert schema2.name == schema.name
        assert schema2.rules.count() == schema.rules.count()
        assert schema2.rules.first().rule_type == schema.rules.first().rule_type

        # Cleanup
        os.unlink(tmp_path)

    def test_export_xml_structure(self):
        """Validate exported XML structure."""
        schema = Schema.objects.create(name="Structure Test")
        SchemaRule.objects.create(
            schema=schema,
            rule_type='keyword',
            field_name='filename',
            operator='contains',
            value='test'
        )

        xml_str = export_xml_template(schema.id)

        # Parse and validate
        root = ET.fromstring(xml_str)
        assert root.tag == 'template'
        assert root.attrib['name'] == 'Structure Test'
        assert root.find('rules') is not None
        assert root.find('transformations') is not None
        assert root.find('directories') is not None

class XMLAPITest(TransactionTestCase):
    def test_import_api_endpoint(self):
        """Test POST /api/schemas/import-xml/ endpoint."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        xml_content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <template name="API Test">
            <rules logic="AND">
                <rule type="keyword" field="filename" operator="contains">test</rule>
            </rules>
            <transformations/>
            <directories>
                <input path="/test/" recursive="true"/>
            </directories>
        </template>'''

        xml_file = SimpleUploadedFile("test.xml", xml_content, content_type="application/xml")

        response = self.client.post('/api/schemas/import-xml/', {'xml_file': xml_file})

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'schema_id' in data

    def test_export_api_endpoint(self):
        """Test GET /api/schemas/{id}/export-xml/ endpoint."""
        schema = Schema.objects.create(name="Export API Test")

        response = self.client.get(f'/api/schemas/{schema.id}/export-xml/')

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/xml'
        assert 'attachment' in response['Content-Disposition']
```

**Running Tests:**
```bash
# Run all XML import/export tests
pytest tests/test_xml_import.py tests/test_xml_export.py -v

# Run with coverage
pytest tests/test_xml_import.py tests/test_xml_export.py --cov=samplify.management.commands --cov-report=html

# Test import with all existing templates
pytest tests/test_xml_import.py::test_import_all_existing_templates -v

# Test export → import round-trip
pytest tests/test_xml_export.py::test_export_import_roundtrip -v
```

---

## Definition of Done
- [ ] XML import command implemented
- [ ] XML export command implemented
- [ ] Import API endpoint implemented (`POST /api/schemas/import-xml/`)
- [ ] Export API endpoint implemented (`GET /api/schemas/{id}/export-xml/`)
- [ ] All XML rule types supported (import and export)
- [ ] Import validated against sample templates
- [ ] Export → Import round-trip tested
- [ ] Import/Export report generated
- [ ] Transaction rollback tested
- [ ] UI Import/Export buttons added to Input Files table
- [ ] UI Import/Export buttons added to Output Destinations table
- [ ] JavaScript file upload/download handlers implemented
- [ ] Schema model updated with xml_source field (NFR14)
- [ ] Database migrations created and tested
- [ ] User feedback messages implemented (success/error)
- [ ] Documentation updated with XML import/export guide
- [ ] Template sharing workflow documented

---

## Risk Assessment
- **Primary Risk:** XML import doesn't capture all template functionality (CR4 violation)
- **Mitigation:** Validate against xml_handler.py, test with all sample templates, comprehensive CR4 testing
- **Secondary Risk:** Export → Import round-trip loses data or introduces errors
- **Mitigation:** Comprehensive round-trip testing, XML schema validation, side-by-side comparison
- **UI Risk:** Import/Export buttons confuse users about which templates to use
- **Mitigation:** Clear button labels, tooltips, success/error messages, user documentation
- **Rollback:** Delete imported schema, restore XML template, revert database changes

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
