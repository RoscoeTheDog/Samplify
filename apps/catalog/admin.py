"""Admin interface configuration for catalog app."""

from django.contrib import admin

from apps.catalog.models import DirectoryMapping, File, Schema, SchemaRule, SchemaTransformation


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """
    Admin interface for File model.

    Provides filtering, search, and display customization for debugging
    and data inspection during development.
    """

    list_display = (
        "file_name",
        "media_type",
        "file_format",
        "file_size",
        "created_at",
    )
    list_filter = ("media_type", "file_format", "created_at")
    search_fields = ("file_name", "file_path", "codec")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "File Information",
            {
                "fields": (
                    "file_path",
                    "file_name",
                    "file_format",
                    "file_size",
                    "media_type",
                )
            },
        ),
        (
            "Media Metadata",
            {
                "fields": ("sample_rate", "bit_depth", "codec"),
                "description": "Optional metadata for audio/video files",
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


class SchemaRuleInline(admin.TabularInline):
    """Inline admin for SchemaRule."""

    model = SchemaRule
    extra = 1
    fields = ("rule_type", "rule_value", "logic_operator", "priority")


class SchemaTransformationInline(admin.StackedInline):
    """Inline admin for SchemaTransformation."""

    model = SchemaTransformation
    extra = 0
    fields = ("output_format", "sample_rate", "bit_depth", "normalize_db")


class DirectoryMappingInline(admin.TabularInline):
    """Inline admin for DirectoryMapping."""

    model = DirectoryMapping
    extra = 1
    fields = ("input_path", "output_path", "monitor_enabled")


@admin.register(Schema)
class SchemaAdmin(admin.ModelAdmin):
    """
    Admin interface for Schema model.

    Provides inline editing of rules, transformations, and directory mappings.
    """

    list_display = ("name", "source_type", "is_active", "created_at", "updated_at")
    list_filter = ("source_type", "is_active", "created_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)
    inlines = [SchemaRuleInline, SchemaTransformationInline, DirectoryMappingInline]

    fieldsets = (
        (
            "Schema Information",
            {
                "fields": ("name", "description", "is_active", "source_type"),
            },
        ),
        (
            "XML Source (NFR14)",
            {
                "fields": ("xml_source",),
                "description": "Original XML content for export/re-import",
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(SchemaRule)
class SchemaRuleAdmin(admin.ModelAdmin):
    """Admin interface for SchemaRule model."""

    list_display = ("schema", "rule_type", "rule_value", "logic_operator", "priority")
    list_filter = ("rule_type", "logic_operator", "schema")
    search_fields = ("rule_value",)
    ordering = ("schema", "-priority", "id")


@admin.register(SchemaTransformation)
class SchemaTransformationAdmin(admin.ModelAdmin):
    """Admin interface for SchemaTransformation model."""

    list_display = ("schema", "output_format", "sample_rate", "bit_depth", "normalize_db")
    list_filter = ("output_format", "schema")
    search_fields = ("output_format",)


@admin.register(DirectoryMapping)
class DirectoryMappingAdmin(admin.ModelAdmin):
    """Admin interface for DirectoryMapping model."""

    list_display = ("schema", "input_path", "output_path", "monitor_enabled")
    list_filter = ("monitor_enabled", "schema")
    search_fields = ("input_path", "output_path")
