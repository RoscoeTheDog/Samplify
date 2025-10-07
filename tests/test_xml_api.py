"""
Tests for XML import/export API endpoints.

Covers:
- POST /api/schemas/import-xml/
- GET /api/schemas/<id>/export-xml/
"""

import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from apps.catalog.models import Schema, SchemaRule


class XMLAPITest(TestCase):
    """Test XML import/export API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_import_api_endpoint(self):
        """Test POST /api/schemas/import-xml/ endpoint."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <samplify>
            <name>API Import Test</name>
            <libraries>
                <directory path="/test/input"/>
            </libraries>
            <outputDirectories>
                <directory path="/test/output">
                    <rules>
                        <containsVideo>true</containsVideo>
                    </rules>
                    <governor><comparison>AND</comparison></governor>
                </directory>
            </outputDirectories>
        </samplify>"""

        xml_file = SimpleUploadedFile("test.xml", xml_content, content_type="application/xml")

        response = self.client.post("/api/schemas/import-xml/", {"xml_file": xml_file})

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "schema_id" in data
        assert data["schema_name"] == "API Import Test"

        # Verify schema created
        schema = Schema.objects.get(id=data["schema_id"])
        assert schema.name == "API Import Test"
        assert schema.source_type == "imported"

    def test_import_api_no_file(self):
        """Test import API with missing file."""
        response = self.client.post("/api/schemas/import-xml/", {})

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "No file provided" in data["error"]

    def test_import_api_invalid_xml(self):
        """Test import API with malformed XML."""
        xml_content = b"""<?xml version="1.0"?>
        <samplify>
            <name>Invalid</name>
            <!-- Missing closing tag -->
        """

        xml_file = SimpleUploadedFile("invalid.xml", xml_content, content_type="application/xml")

        response = self.client.post("/api/schemas/import-xml/", {"xml_file": xml_file})

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_import_api_wrong_file_type(self):
        """Test import API with non-XML file."""
        txt_file = SimpleUploadedFile("test.txt", b"Not an XML file", content_type="text/plain")

        response = self.client.post("/api/schemas/import-xml/", {"xml_file": txt_file})

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Invalid file type" in data["error"]

    def test_export_api_endpoint(self):
        """Test GET /api/schemas/<id>/export-xml/ endpoint."""
        # Create test schema
        schema = Schema.objects.create(name="API Export Test", source_type="web")
        SchemaRule.objects.create(
            schema=schema,
            rule_type="media_type",
            rule_value="video",
            logic_operator="AND",
            priority=0,
        )

        response = self.client.get(f"/api/schemas/{schema.id}/export-xml/")

        # Verify response
        assert response.status_code == 200
        assert response["Content-Type"] == "application/xml"
        assert "attachment" in response["Content-Disposition"]
        assert "API_Export_Test.xml" in response["Content-Disposition"]

        # Verify XML content
        content = response.content.decode("utf-8")
        assert "<?xml version" in content
        assert "<samplify>" in content
        assert "API Export Test" in content

    def test_export_api_nonexistent_schema(self):
        """Test export API with invalid schema ID."""
        response = self.client.get("/api/schemas/99999/export-xml/")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"]


class XMLAPIIntegrationTest(TestCase):
    """Integration tests for import → export via API."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_api_import_export_roundtrip(self):
        """Test API import → export preserves data."""
        # Import via API
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <samplify>
            <name>API Roundtrip Test</name>
            <libraries>
                <directory path="/api/input"/>
            </libraries>
            <outputDirectories>
                <directory path="/api/output">
                    <rules>
                        <containsAudio>true</containsAudio>
                        <expression>TestKeyword</expression>
                    </rules>
                    <governor><comparison>OR</comparison></governor>
                </directory>
            </outputDirectories>
        </samplify>"""

        xml_file = SimpleUploadedFile("roundtrip.xml", xml_content, content_type="application/xml")
        import_response = self.client.post("/api/schemas/import-xml/", {"xml_file": xml_file})

        assert import_response.status_code == 200
        import_data = import_response.json()
        schema_id = import_data["schema_id"]

        # Export via API
        export_response = self.client.get(f"/api/schemas/{schema_id}/export-xml/")

        assert export_response.status_code == 200

        # Verify exported XML structure
        exported_xml = export_response.content.decode("utf-8")
        assert "API Roundtrip Test" in exported_xml
        assert "<samplify>" in exported_xml
        assert "libraries" in exported_xml
        assert "outputDirectories" in exported_xml
