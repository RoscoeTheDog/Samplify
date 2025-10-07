"""
Catalog models for Samplify file management.

This module implements models for:
- File: Single-table inheritance for audio/video/image files
- Schema: Configuration storage (replaces XML templates)
- SchemaRule: Filtering rules for schemas
- SchemaTransformation: Output format transformations
- DirectoryMapping: Input/output path mappings
"""

from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models


class File(models.Model):
    """
    Unified file model for audio, video, and image files.

    Uses single-table inheritance with media_type discriminator to consolidate
    the previous SQLAlchemy models (FilesVideo, FilesAudio, FilesImage) into
    a single Django model.

    Attributes:
        file_path: Full path to the file (max 500 chars)
        file_name: Name of the file including extension (max 255 chars)
        file_format: File extension/format (max 50 chars)
        sample_rate: Audio/video sample rate in Hz (optional)
        bit_depth: Audio bit depth or video bit depth (optional)
        codec: Codec used for encoding (optional, max 50 chars)
        file_size: File size in bytes
        media_type: Discriminator field - 'audio', 'video', or 'image'
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last modified
    """

    MEDIA_TYPE_CHOICES = [
        ("audio", "Audio"),
        ("video", "Video"),
        ("image", "Image"),
    ]

    PROCESSING_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    # Core file information
    file_path = models.CharField(max_length=500, help_text="Full path to the file")
    file_name = models.CharField(max_length=255, help_text="File name with extension")
    file_format = models.CharField(max_length=50, help_text="File extension/format")
    file_size = models.BigIntegerField(help_text="File size in bytes")

    # Media-specific metadata (nullable for non-applicable types)
    sample_rate = models.IntegerField(
        null=True,
        blank=True,
        help_text="Sample rate in Hz (audio/video)",
    )
    bit_depth = models.IntegerField(
        null=True,
        blank=True,
        help_text="Bit depth (audio/video)",
    )
    codec = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Codec used for encoding",
    )

    # Discriminator field for single-table inheritance
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        help_text="Type of media file",
    )

    # Batch processing status (Story 1.6)
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default="pending",
        help_text="Current processing status for batch operations",
    )

    # Schema association via directory mapping (Story R1.3 - Remediation)
    directory_mapping = models.ForeignKey(
        'DirectoryMapping',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files',
        help_text="Directory mapping (and thus schema) this file is associated with",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata."""

        db_table = "catalog_file"
        ordering = ["-created_at"]
        verbose_name = "File"
        verbose_name_plural = "Files"
        indexes = [
            models.Index(fields=["media_type"]),
            models.Index(fields=["file_format"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["directory_mapping"]),
        ]

    def __str__(self) -> str:
        """
        Return string representation of the file.

        Returns:
            File name as the string representation
        """
        return self.file_name

    def get_absolute_path(self) -> Path:
        """
        Return the absolute file path as a pathlib.Path object.

        Returns:
            Path object representing the absolute file path

        Example:
            >>> file = File(file_path="/media/audio/song.mp3")
            >>> file.get_absolute_path()
            PosixPath('/media/audio/song.mp3')
        """
        return Path(self.file_path)


class Schema(models.Model):
    """
    Schema configuration for file processing rules.

    Replaces XML templates with database-backed configuration storage.
    Supports both web-created schemas and imported XML templates.

    Attributes:
        name: Unique schema name
        description: Optional description of schema purpose
        is_active: Whether this schema is currently active (only one active at a time)
        xml_source: Original XML content for export/re-import (NFR14)
        source_type: Origin of schema ('web' or 'imported')
        created_at: Timestamp when schema was created
        updated_at: Timestamp when schema was last modified
    """

    SOURCE_TYPE_CHOICES = [
        ("web", "Web Created"),
        ("imported", "Imported from XML"),
    ]

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique schema name",
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description of schema purpose",
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Only one schema can be active at a time",
    )
    xml_source = models.TextField(
        null=True,
        blank=True,
        help_text="Original XML content for export (NFR14)",
    )
    source_type = models.CharField(
        max_length=10,
        choices=SOURCE_TYPE_CHOICES,
        default="web",
        help_text="Origin of schema (web-created or imported)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata."""

        db_table = "catalog_schema"
        ordering = ["-updated_at"]
        verbose_name = "Schema"
        verbose_name_plural = "Schemas"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["source_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        """
        Return string representation of the schema.

        Returns:
            Schema name with active status indicator
        """
        status = " (ACTIVE)" if self.is_active else ""
        return f"{self.name}{status}"

    def save(self, *args, **kwargs) -> None:
        """
        Save schema with validation.

        Ensures only one schema is active at a time by deactivating others
        when this schema is set to active.

        Raises:
            ValidationError: If validation fails
        """
        if self.is_active:
            # Deactivate all other schemas
            Schema.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class SchemaRule(models.Model):
    """
    Filtering rule for a schema.

    Defines conditions for matching files (keyword, extension, media type, etc.)
    with AND/OR logic support.

    Attributes:
        schema: Parent schema
        rule_type: Type of rule (keyword, extension, media_type, attribute)
        rule_value: Value to match against
        logic_operator: How to combine with other rules (AND/OR)
        priority: Rule execution priority (higher = earlier)
    """

    RULE_TYPE_CHOICES = [
        ("keyword", "Keyword Match"),
        ("extension", "File Extension"),
        ("media_type", "Media Type"),
        ("attribute", "File Attribute"),
    ]

    LOGIC_OPERATOR_CHOICES = [
        ("AND", "AND"),
        ("OR", "OR"),
    ]

    schema = models.ForeignKey(
        Schema,
        on_delete=models.CASCADE,
        related_name="rules",
        help_text="Parent schema",
    )
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPE_CHOICES,
        help_text="Type of filtering rule",
    )
    rule_value = models.CharField(
        max_length=500,
        help_text="Value to match against",
    )
    logic_operator = models.CharField(
        max_length=3,
        choices=LOGIC_OPERATOR_CHOICES,
        default="AND",
        help_text="Logic operator for combining rules",
    )
    priority = models.IntegerField(
        default=0,
        help_text="Rule execution priority (higher = earlier)",
    )

    class Meta:
        """Model metadata."""

        db_table = "catalog_schema_rule"
        ordering = ["-priority", "id"]
        verbose_name = "Schema Rule"
        verbose_name_plural = "Schema Rules"

    def __str__(self) -> str:
        """
        Return string representation of the rule.

        Returns:
            Rule description with type and value
        """
        return f"{self.get_rule_type_display()}: {self.rule_value}"


class SchemaTransformation(models.Model):
    """
    Output transformation configuration for a schema.

    Defines how files should be transformed (format, sample rate, bit depth, etc.)
    when processed by this schema.

    Attributes:
        schema: Parent schema
        output_format: Target output format
        sample_rate: Target sample rate (audio/video)
        bit_depth: Target bit depth (audio/video)
        normalize_db: Normalization level in dB
    """

    schema = models.ForeignKey(
        Schema,
        on_delete=models.CASCADE,
        related_name="transformations",
        help_text="Parent schema",
    )
    output_format = models.CharField(
        max_length=50,
        help_text="Target output format (e.g., mp3, wav, mp4)",
    )
    sample_rate = models.IntegerField(
        null=True,
        blank=True,
        help_text="Target sample rate in Hz (e.g., 44100, 48000)",
    )
    bit_depth = models.IntegerField(
        null=True,
        blank=True,
        help_text="Target bit depth (e.g., 16, 24)",
    )
    normalize_db = models.FloatField(
        null=True,
        blank=True,
        help_text="Normalization level in dB (e.g., -3.0, -6.0)",
    )

    class Meta:
        """Model metadata."""

        db_table = "catalog_schema_transformation"
        verbose_name = "Schema Transformation"
        verbose_name_plural = "Schema Transformations"

    def __str__(self) -> str:
        """
        Return string representation of the transformation.

        Returns:
            Transformation description with output format
        """
        return f"Transform to {self.output_format}"


class DirectoryMapping(models.Model):
    """
    Input/output directory mapping for a schema.

    Defines which input directories should be watched and where
    processed files should be output.

    Attributes:
        schema: Parent schema
        input_path: Path to input directory
        output_path: Path to output directory
        monitor_enabled: Whether this directory is actively monitored
    """

    schema = models.ForeignKey(
        Schema,
        on_delete=models.CASCADE,
        related_name="directory_mappings",
        help_text="Parent schema",
    )
    input_path = models.CharField(
        max_length=500,
        help_text="Input directory path",
    )
    output_path = models.CharField(
        max_length=500,
        help_text="Output directory path",
    )
    monitor_enabled = models.BooleanField(
        default=False,
        help_text="Whether this directory is actively monitored",
    )

    class Meta:
        """Model metadata."""

        db_table = "catalog_directory_mapping"
        verbose_name = "Directory Mapping"
        verbose_name_plural = "Directory Mappings"

    def __str__(self) -> str:
        """
        Return string representation of the mapping.

        Returns:
            Mapping description with input/output paths
        """
        watched = " [WATCHED]" if self.monitor_enabled else ""
        return f"{self.input_path} → {self.output_path}{watched}"
