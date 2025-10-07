"""
URL configuration for catalog app.

Defines URL patterns for schema management API endpoints.
"""

from django.urls import path

from apps.catalog.api import views as api_views

app_name = "catalog"

urlpatterns = [
    # API endpoints for XML import/export
    path("api/schemas/import-xml/", api_views.import_xml_api, name="import_xml"),
    path("api/schemas/<int:schema_id>/export-xml/", api_views.export_xml_api, name="export_xml"),
]
