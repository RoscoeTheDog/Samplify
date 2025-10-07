"""
API views for schema import/export operations.

Provides HTTP endpoints for:
- POST /api/schemas/import-xml/ - Import XML template
- GET /api/schemas/<id>/export-xml/ - Export schema as XML
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from typing import Any

from django.core.management import call_command
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.catalog.models import Schema


@csrf_exempt
@require_http_methods(["POST"])
def import_xml_api(request: HttpRequest) -> JsonResponse:
    """
    Import XML template via API.

    Accepts multipart/form-data file upload and imports XML template
    into database using import_xml_template management command.

    Args:
        request: HTTP request with uploaded XML file

    Returns:
        JSON response with success/error status

    Example:
        POST /api/schemas/import-xml/
        Content-Type: multipart/form-data
        Body: xml_file=<file>

        Response:
        {
            "success": true,
            "schema_id": 1,
            "schema_name": "My Template",
            "message": "Successfully imported template: My Template"
        }
    """
    try:
        # Validate file upload
        xml_file = request.FILES.get("xml_file")
        if not xml_file:
            return JsonResponse({"error": "No file provided. Use 'xml_file' field."}, status=400)

        # Validate file extension
        if not xml_file.name.endswith(".xml"):
            return JsonResponse({"error": "Invalid file type. Only .xml files accepted."}, status=400)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode="wb") as tmp:
            for chunk in xml_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Parse XML to get template name (for response)
            tree = ET.parse(tmp_path)
            root = tree.getroot()
            name_elem = root.find("name")
            template_name = name_elem.text if name_elem is not None and name_elem.text else "Unknown"

            # Import using management command
            call_command("import_xml_template", tmp_path)

            # Fetch created schema
            schema = Schema.objects.get(name=template_name)

            return JsonResponse(
                {
                    "success": True,
                    "schema_id": schema.id,
                    "schema_name": schema.name,
                    "rules_count": schema.rules.count(),
                    "mappings_count": schema.directory_mappings.count(),
                    "message": f"Successfully imported template: {schema.name}",
                }
            )

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except ET.ParseError as e:
        return JsonResponse({"error": f"Invalid XML file: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Import failed: {str(e)}"}, status=500)


@require_http_methods(["GET"])
def export_xml_api(request: HttpRequest, schema_id: int) -> HttpResponse:
    """
    Export schema as XML template via API.

    Generates brownfield XML template from schema and returns
    as downloadable file.

    Args:
        request: HTTP request
        schema_id: Schema ID to export

    Returns:
        HTTP response with XML file attachment

    Example:
        GET /api/schemas/1/export-xml/

        Response:
        Content-Type: application/xml
        Content-Disposition: attachment; filename="schema_1.xml"
        Body: <?xml version="1.0"?>...
    """
    try:
        # Validate schema exists
        try:
            schema = Schema.objects.get(id=schema_id)
        except Schema.DoesNotExist:
            return JsonResponse({"error": f"Schema with ID {schema_id} not found"}, status=404)

        # Generate XML using management command
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode="w") as tmp:
            tmp_path = tmp.name

        try:
            call_command("export_xml_template", str(schema_id), output=tmp_path)

            # Read generated XML
            with open(tmp_path, "r", encoding="utf-8") as f:
                xml_content = f.read()

            # Return as downloadable file
            response = HttpResponse(xml_content, content_type="application/xml")
            safe_filename = schema.name.replace(" ", "_").replace("/", "_")
            response["Content-Disposition"] = f'attachment; filename="{safe_filename}.xml"'
            return response

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        return JsonResponse({"error": f"Export failed: {str(e)}"}, status=500)
