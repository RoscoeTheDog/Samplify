# Database Schema Design

**Version:** 1.0
**Last Updated:** 2025-10-04
**Status:** Design Document

---

## Overview

This document specifies the Django ORM database schema for Samplify's Django migration. The design implements:
- **Single-table inheritance** (NFR12) for File model consolidation
- **SQLite WAL mode** (NFR2) for concurrent access
- **Schema-based processing** replacing XML templates

**Key Changes from Brownfield:**
- ❌ **Remove**: Redundant `FilesVideo`, `FilesAudio`, `FilesImage` tables
- ✅ **Add**: Single `File` model with `media_type` discriminator
- ✅ **Add**: Schema, Filter, ProcessingRule models for web UI configuration
- ✅ **Preserve**: All metadata fields from brownfield models

---

## Entity Relationship Diagram

```
┌─────────────┐
│   Schema    │
└──────┬──────┘
       │
       │ 1:N
       ├────────────────────────────────────┐
       │                                    │
       ▼                                    ▼
┌──────────────────┐              ┌─────────────────────┐
│ InputDirectory   │              │  OutputDirectory    │
└────────┬─────────┘              └──────────┬──────────┘
         │                                   │
         │ 1:N                               │ 1:N
         ▼                                   ├──────────┬─────────┐
    ┌────────┐                               │          │         │
    │  File  │◄──────────────────────────────┘          │         │
    └────────┘                                           ▼         ▼
       ▲                                          ┌────────┐ ┌──────────────┐
       │                                          │ Filter │ │ProcessingRule│
       │                                          └────────┘ └──────────────┘
       │ 1:N
       ▼
 ┌─────────────┐
 │ProcessingLog│
 └─────────────┘
```

---

## Core Models

### 1. Schema

**Purpose:** Replaces XML templates. Stores processing configuration for web UI.

**Django Model:**
```python
# apps/schemas/models.py
from django.db import models

class Schema(models.Model):
    """
    Processing schema configuration.
    Replaces XML templates from brownfield codebase.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Human-readable schema name"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of schema purpose"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Only active schemas are used for processing"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'schemas'
        verbose_name = 'Processing Schema'
        verbose_name_plural = 'Processing Schemas'
        ordering = ['name']

    def __str__(self):
        return self.name
```

**Fields:**
- `id`: Auto-increment primary key
- `name`: Unique schema identifier
- `description`: User-friendly description
- `is_active`: Only one schema can be active at a time (enforced in save())
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last modification

---

### 2. InputDirectory

**Purpose:** Defines directories to monitor and scan for input files.

**Django Model:**
```python
class InputDirectory(models.Model):
    """
    Input directory configuration for file scanning and monitoring.
    Maps to brownfield InputDirectories table.
    """
    schema = models.ForeignKey(
        Schema,
        on_delete=models.CASCADE,
        related_name='input_directories'
    )
    path = models.CharField(
        max_length=500,
        help_text="Absolute path to input directory"
    )
    monitor_enabled = models.BooleanField(
        default=True,
        help_text="Enable watchdog monitoring for this directory"
    )
    recursive = models.BooleanField(
        default=True,
        help_text="Scan subdirectories recursively"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'input_directories'
        unique_together = [['schema', 'path']]
        ordering = ['path']

    def __str__(self):
        return f"{self.schema.name}: {self.path}"
```

**Relationships:**
- N:1 with Schema (many input directories per schema)
- 1:N with File (one directory contains many files)

---

### 3. OutputDirectory

**Purpose:** Defines output destinations with associated filters and processing rules.

**Django Model:**
```python
class OutputDirectory(models.Model):
    """
    Output directory with filters and processing rules.
    Maps to brownfield OutputDirectories table.
    """
    schema = models.ForeignKey(
        Schema,
        on_delete=models.CASCADE,
        related_name='output_directories'
    )
    path = models.CharField(
        max_length=500,
        help_text="Absolute path to output directory"
    )
    logic_operator = models.CharField(
        max_length=3,
        choices=[
            ('AND', 'AND - All filters must match'),
            ('OR', 'OR - Any filter can match')
        ],
        default='AND',
        help_text="Logic for combining multiple filters"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'output_directories'
        unique_together = [['schema', 'path']]
        ordering = ['path']

    def __str__(self):
        return f"{self.schema.name}: {self.path}"
```

**Relationships:**
- N:1 with Schema
- 1:N with Filter (multiple filters per output directory)
- 1:N with ProcessingRule (multiple rules per output directory)

---

### 4. Filter

**Purpose:** Defines matching criteria for routing files to output directories.

**Django Model:**
```python
class Filter(models.Model):
    """
    File matching filter (keywords, extensions, media types).
    Maps to brownfield SearchTerms and rule conditions.
    """
    FILTER_TYPES = [
        ('keyword', 'Keyword Match'),
        ('extension', 'File Extension'),
        ('media_type', 'Media Type'),
        ('format', 'File Format'),
        ('sample_rate', 'Sample Rate'),
        ('bit_depth', 'Bit Depth'),
        ('date_range', 'Date Range'),
    ]

    output_directory = models.ForeignKey(
        OutputDirectory,
        on_delete=models.CASCADE,
        related_name='filters'
    )
    filter_type = models.CharField(
        max_length=20,
        choices=FILTER_TYPES
    )
    value = models.CharField(
        max_length=500,
        help_text="Filter value (e.g., 'kick', '.wav', '44100')"
    )
    case_sensitive = models.BooleanField(
        default=False,
        help_text="For keyword filters only"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'filters'
        ordering = ['filter_type', 'value']

    def __str__(self):
        return f"{self.filter_type}: {self.value}"

    def matches(self, file):
        """
        ALGORITHM PRESERVED FROM: handlers/rules.py lines 45-120
        Check if file matches this filter criteria.
        """
        if self.filter_type == 'keyword':
            search_str = file.filename if self.case_sensitive else file.filename.lower()
            value_str = self.value if self.case_sensitive else self.value.lower()
            return value_str in search_str

        elif self.filter_type == 'extension':
            return file.extension == self.value

        elif self.filter_type == 'media_type':
            return file.media_type == self.value

        elif self.filter_type == 'format':
            return file.format == self.value

        elif self.filter_type == 'sample_rate':
            return file.sample_rate == int(self.value) if file.sample_rate else False

        elif self.filter_type == 'bit_depth':
            return file.bit_depth == int(self.value) if file.bit_depth else False

        return False
```

**Relationships:**
- N:1 with OutputDirectory

---

### 5. ProcessingRule

**Purpose:** Defines media processing operations (conversion, normalization, etc.).

**Django Model:**
```python
class ProcessingRule(models.Model):
    """
    Processing operation configuration.
    Maps to brownfield OutputDirectories processing flags and settings.
    """
    output_directory = models.ForeignKey(
        OutputDirectory,
        on_delete=models.CASCADE,
        related_name='processing_rules'
    )

    # Output format settings
    output_format = models.CharField(
        max_length=10,
        blank=True,
        help_text="Target format (WAV, MP3, FLAC, etc.)"
    )
    sample_rate = models.IntegerField(
        null=True,
        blank=True,
        help_text="Target sample rate (e.g., 44100, 48000)"
    )
    bit_depth = models.IntegerField(
        null=True,
        blank=True,
        choices=[(16, '16-bit'), (24, '24-bit'), (32, '32-bit')],
        help_text="Target bit depth for audio"
    )
    channels = models.IntegerField(
        null=True,
        blank=True,
        choices=[(1, 'Mono'), (2, 'Stereo')],
        help_text="Target channel count"
    )

    # Processing flags
    normalize = models.BooleanField(
        default=False,
        help_text="Apply audio normalization"
    )
    normalize_level = models.FloatField(
        default=-6.0,
        help_text="Normalization target level in dB"
    )
    strip_silence = models.BooleanField(
        default=False,
        help_text="Remove silence from audio files"
    )

    # Media type filters
    audio_only = models.BooleanField(default=False)
    video_only = models.BooleanField(default=False)
    image_only = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processing_rules'
        ordering = ['id']

    def __str__(self):
        parts = []
        if self.output_format:
            parts.append(f"→{self.output_format}")
        if self.sample_rate:
            parts.append(f"{self.sample_rate}Hz")
        if self.bit_depth:
            parts.append(f"{self.bit_depth}bit")
        if self.normalize:
            parts.append(f"Norm{self.normalize_level}dB")
        return " ".join(parts) or "No processing"
```

**Relationships:**
- N:1 with OutputDirectory

---

### 6. File (Single-Table Inheritance)

**Purpose:** Unified file catalog with polymorphic media metadata.
**Implements:** NFR12 - Single-table inheritance to eliminate redundant tables.

**Django Model:**
```python
# apps/catalog/models.py
class File(models.Model):
    """
    Unified file catalog using single-table inheritance.

    CONSOLIDATES BROWNFIELD MODELS:
    - database/database_setup.py line 93 (Files)
    - database/database_setup.py line 124 (FilesVideo)
    - database/database_setup.py line 153 (FilesAudio)
    - database/database_setup.py line 172 (FilesImage)
    """
    MEDIA_TYPES = [
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('image', 'Image'),
        ('unknown', 'Unknown'),
    ]

    # Core fields (common to all media types)
    uid = models.CharField(
        max_length=10,
        unique=True,
        help_text="Short unique identifier for UI display (e.g., #a1f2)"
    )
    input_directory = models.ForeignKey(
        'schemas.InputDirectory',
        on_delete=models.CASCADE,
        related_name='files'
    )
    path = models.CharField(
        max_length=500,
        unique=True,
        help_text="Absolute path to file"
    )
    filename = models.CharField(max_length=255)
    extension = models.CharField(max_length=10)
    file_size = models.BigIntegerField(help_text="Size in bytes")

    # Media type discriminator (single-table inheritance key)
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPES,
        default='unknown'
    )

    # Timestamps
    file_created_at = models.DateTimeField(
        help_text="File system creation timestamp"
    )
    file_modified_at = models.DateTimeField(
        help_text="File system modification timestamp"
    )
    scanned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When file was cataloged in database"
    )

    # Processing status
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('skipped', 'Skipped'),
        ],
        default='pending'
    )

    # Common media metadata (nullable for non-applicable types)
    format = models.CharField(
        max_length=50,
        blank=True,
        help_text="Media format (e.g., WAV, MP4, PNG)"
    )
    duration = models.FloatField(
        null=True,
        blank=True,
        help_text="Duration in seconds (audio/video only)"
    )
    width = models.IntegerField(
        null=True,
        blank=True,
        help_text="Width in pixels (video/image only)"
    )
    height = models.IntegerField(
        null=True,
        blank=True,
        help_text="Height in pixels (video/image only)"
    )

    # Audio-specific metadata
    sample_rate = models.IntegerField(
        null=True,
        blank=True,
        help_text="Sample rate in Hz (audio only)"
    )
    bit_depth = models.IntegerField(
        null=True,
        blank=True,
        help_text="Bit depth (audio only)"
    )
    bit_rate = models.IntegerField(
        null=True,
        blank=True,
        help_text="Bit rate in bps (audio/video)"
    )
    channels = models.IntegerField(
        null=True,
        blank=True,
        help_text="Audio channel count"
    )
    channel_layout = models.CharField(
        max_length=50,
        blank=True,
        help_text="Channel layout (e.g., stereo, 5.1)"
    )
    codec = models.CharField(
        max_length=50,
        blank=True,
        help_text="Codec name (e.g., pcm_s16le, h264)"
    )

    # Video-specific metadata
    frame_rate = models.FloatField(
        null=True,
        blank=True,
        help_text="Frames per second (video only)"
    )
    pix_format = models.CharField(
        max_length=50,
        blank=True,
        help_text="Pixel format (video only)"
    )

    # Image-specific metadata
    alpha = models.BooleanField(
        default=False,
        help_text="Has alpha channel (image only)"
    )
    mode = models.CharField(
        max_length=20,
        blank=True,
        help_text="Color mode (e.g., RGB, RGBA, L)"
    )
    frames = models.IntegerField(
        default=1,
        help_text="Number of frames (animated images)"
    )

    class Meta:
        db_table = 'files'
        indexes = [
            models.Index(fields=['media_type']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['input_directory']),
            models.Index(fields=['scanned_at']),
        ]
        ordering = ['-scanned_at']

    def __str__(self):
        return f"{self.uid}: {self.filename}"

    def save(self, *args, **kwargs):
        """Generate UID if not set."""
        if not self.uid:
            import hashlib
            hash_str = hashlib.md5(self.path.encode()).hexdigest()[:4]
            self.uid = f"#{hash_str}"
        super().save(*args, **kwargs)
```

**Key Design Decisions:**
1. **Single table** instead of separate Audio/Video/Image tables (NFR12)
2. **media_type discriminator** for polymorphism
3. **Nullable fields** for type-specific metadata
4. **Auto-generated UID** for UI display
5. **Indexes** on commonly queried fields

---

### 7. ProcessingLog

**Purpose:** Audit trail for file processing operations.

**Django Model:**
```python
class ProcessingLog(models.Model):
    """
    Audit log for file processing operations.
    Tracks success/failure and error details.
    """
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name='processing_logs'
    )
    output_directory = models.ForeignKey(
        'schemas.OutputDirectory',
        on_delete=models.SET_NULL,
        null=True
    )
    batch_id = models.CharField(
        max_length=50,
        help_text="Batch operation identifier"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('skipped', 'Skipped'),
        ]
    )
    output_file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to generated output file"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error details if failed"
    )
    worker_id = models.IntegerField(
        help_text="Multiprocessing worker that handled this file"
    )

    class Meta:
        db_table = 'processing_logs'
        indexes = [
            models.Index(fields=['batch_id']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.file.uid}: {self.status}"
```

---

## Database Configuration

### SQLite WAL Mode (NFR2)

**Django Settings:**
```python
# samplify/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database' / 'samplify.db',
        'OPTIONS': {
            # Enable WAL mode for concurrent access
            'init_command': 'PRAGMA journal_mode=WAL;',
        }
    }
}
```

**Benefits:**
- Concurrent reads during writes
- Web server + batch workers + watch mode can access DB simultaneously
- Automatic checkpoint management

---

## Migration Strategy

### From Brownfield SQLAlchemy to Django ORM

**Phase 1: Schema Migration**
```bash
# Create initial migrations
python manage.py makemigrations schemas catalog

# Apply migrations
python manage.py migrate
```

**Phase 2: Data Migration**
```python
# apps/catalog/management/commands/migrate_brownfield_data.py
from django.core.management.base import BaseCommand
import sqlite3
from apps.catalog.models import File

class Command(BaseCommand):
    help = 'Migrate data from brownfield SQLite database'

    def handle(self, *args, **options):
        # Connect to old database
        old_db = sqlite3.connect('database/database.db')
        cursor = old_db.cursor()

        # Migrate Files table
        cursor.execute("SELECT * FROM Files")
        for row in cursor.fetchall():
            File.objects.create(
                path=row[1],
                filename=row[2],
                # ... map all fields
            )

        # Migrate FilesAudio → File (media_type='audio')
        # Migrate FilesVideo → File (media_type='video')
        # Migrate FilesImage → File (media_type='image')

        self.stdout.write(self.style.SUCCESS('Migration complete'))
```

---

## Indexes and Performance

### Recommended Indexes

```python
# Composite indexes for common queries
class File(models.Model):
    class Meta:
        indexes = [
            # For filtering by type and status
            models.Index(fields=['media_type', 'processing_status']),

            # For batch processing queries
            models.Index(fields=['input_directory', 'processing_status']),

            # For recent file lookups
            models.Index(fields=['-scanned_at']),
        ]
```

### Query Optimization

```python
# Use select_related for foreign key traversal
files = File.objects.select_related('input_directory__schema').all()

# Use prefetch_related for reverse relationships
output_dirs = OutputDirectory.objects.prefetch_related(
    'filters',
    'processing_rules'
).all()
```

---

## Related Documents

- **[API Endpoints](./api-endpoints.md)** - REST API using these models
- **[Technical Debt](./technical-debt-and-known-issues.md)** - Brownfield schema issues
- **[Data Models and APIs](./data-models-and-apis.md)** - Brownfield current state
