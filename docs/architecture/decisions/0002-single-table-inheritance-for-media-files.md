# ADR 0002: Single-Table Inheritance for Media File Types

**Status:** Accepted
**Date:** 2025-10-05 (Retroactive)
**Deciders:** Development Team
**Related Stories:** 1.2A, 1.2B
**Related NFRs:** NFR12

---

## Context

The legacy SQLAlchemy codebase used three separate tables for media files:
- `FilesVideo` - Video file metadata
- `FilesAudio` - Audio file metadata
- `FilesImage` - Image file metadata

During Django migration (Story 1.2A), we needed to choose an inheritance strategy:
1. **Single-table inheritance** - One table with `media_type` discriminator
2. **Multi-table inheritance** - Django's native model inheritance with JOIN queries
3. **Abstract base class** - Separate concrete tables for each type
4. **No inheritance** - Duplicate code across three models

NFR12 explicitly requires: *"Use single-table inheritance with `media_type` discriminator to eliminate redundant tables."*

---

## Decision

**Implement single-table inheritance using a `media_type` CharField as discriminator.**

All media file types (audio, video, image) share a unified `File` model stored in a single `catalog_file` table.

---

## Implementation

**Model Structure:**
```python
class File(models.Model):
    """Unified file model with single-table inheritance."""

    MEDIA_TYPE_CHOICES = [
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('image', 'Image'),
    ]

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        db_index=True,  # Optimize filtering by type
    )

    # Common fields across all media types
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)
    file_format = models.CharField(max_length=50, db_index=True)
    file_size = models.BigIntegerField()

    # Type-specific fields (nullable for non-applicable types)
    sample_rate = models.IntegerField(null=True, blank=True)  # Audio/Video
    bit_depth = models.IntegerField(null=True, blank=True)    # Audio
    codec = models.CharField(max_length=50, null=True, blank=True)  # Audio/Video

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Database Schema:**
- Single table: `catalog_file`
- No redundant tables
- Indexes on `media_type`, `file_format`, `created_at` for query optimization

---

## Consequences

### Positive
- ✅ **Simplified schema:** Single table eliminates JOIN complexity
- ✅ **Query performance:** No multi-table JOINs required
- ✅ **ORM simplicity:** Single model for all media types
- ✅ **NFR12 compliance:** Explicit requirement satisfied
- ✅ **Migration ease:** Direct mapping from SQLAlchemy models
- ✅ **Index optimization:** Strategic indexes on discriminator and high-cardinality fields
- ✅ **Code reuse:** Shared methods (`__str__`, `get_absolute_path`) work across all types

### Negative
- ⚠️ **Nullable fields required:** Type-specific fields must be `null=True, blank=True`
- ⚠️ **Schema bloat potential:** Adding video-specific fields affects all rows
- ⚠️ **No compile-time type safety:** All media types use same model class
- ⚠️ **Data validation complexity:** Must validate field applicability by `media_type`

### Neutral
- 📋 **Storage overhead:** Nullable columns have minimal overhead in SQLite/PostgreSQL
- 📋 **Field explosion risk:** Adding many type-specific fields could complicate schema
- 📋 **Alternative approach:** Could use JSON fields for type-specific metadata if needed

---

## Alternatives Considered

### Option 1: Django Multi-Table Inheritance (Rejected)
**Approach:**
```python
class File(models.Model):  # Base table
    file_path = models.CharField(max_length=500)
    # Common fields

class AudioFile(File):  # Separate table with FK to File
    sample_rate = models.IntegerField()

class VideoFile(File):
    codec = models.CharField(max_length=50)
```

**Pros:**
- Type-safe subclasses
- No nullable fields
- Django native pattern

**Cons:**
- **Violates NFR12** (multiple tables)
- JOIN overhead on every query
- More complex migrations
- Harder to query across all media types

**Rejection Reason:** Explicit NFR12 requirement for single-table inheritance

---

### Option 2: Abstract Base Class (Rejected)
**Approach:**
```python
class AbstractFile(models.Model):
    class Meta:
        abstract = True
    file_path = models.CharField(max_length=500)

class AudioFile(AbstractFile):  # Separate table
    sample_rate = models.IntegerField()
```

**Pros:**
- No nullable fields
- Type-safe models
- Clean separation

**Cons:**
- **Violates NFR12** (creates 3 separate tables: `catalog_audiofile`, `catalog_videofile`, `catalog_imagefile`)
- Cannot query across all media types easily
- Duplicates common columns
- More migrations complexity

**Rejection Reason:** Creates redundant tables, violates NFR12

---

### Option 3: Single Model with JSON Field (Rejected)
**Approach:**
```python
class File(models.Model):
    media_type = models.CharField(max_length=10)
    file_path = models.CharField(max_length=500)
    metadata = models.JSONField()  # Type-specific fields
```

**Pros:**
- No nullable fields in schema
- Flexible metadata structure
- Single table

**Cons:**
- Loss of type safety
- Cannot index JSON fields efficiently
- Complex validation logic
- Poor query performance for type-specific fields

**Rejection Reason:** Sacrifices query performance and type safety

---

### Option 4: Single-Table Inheritance (Accepted)
**Approach:** As implemented above

**Pros:**
- NFR12 compliant
- Excellent query performance
- Simple ORM usage
- Strategic indexes

**Cons:**
- Nullable fields required
- Field applicability validation needed

**Acceptance Reason:** Best balance of NFR compliance, performance, and maintainability

---

## Design Patterns

### Query Filtering by Type
```python
# Efficient filtering with indexed media_type
audio_files = File.objects.filter(media_type='audio')
video_files = File.objects.filter(media_type='video')

# Query across all types
all_media = File.objects.all()
```

### Field Validation Pattern
```python
def clean(self):
    """Validate field applicability by media_type."""
    if self.media_type == 'image':
        if self.sample_rate or self.bit_depth or self.codec:
            raise ValidationError("Images cannot have audio/video metadata")
```

### Manager Pattern (Future Enhancement)
```python
class AudioFileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(media_type='audio')

class File(models.Model):
    objects = models.Manager()
    audio = AudioFileManager()  # File.audio.all()
```

---

## Performance Characteristics

### Storage Efficiency
- **Nullable columns:** Minimal overhead (1 bit per NULL in most databases)
- **Index overhead:** 3 indexes (media_type, file_format, created_at) acceptable
- **Row size:** Estimated ~200 bytes per row (within single page for most DBs)

### Query Performance
```python
# Single table scan (FAST)
File.objects.filter(media_type='audio', file_format='mp3')

# vs Multi-table inheritance (SLOW)
AudioFile.objects.filter(file_format='mp3')  # Requires JOIN with File table
```

**Benchmark (Future):** Add to Story 1.5 performance validation

---

## Validation

### QA Approval
- **Reviewer:** Quinn (Test Architect)
- **Date:** 2025-10-06
- **Assessment:** "Perfect single-table inheritance with `media_type` discriminator"
- **Code Quality:** "Exemplary - type hints, docstrings, strategic indexes"
- **Quality Gate:** Story 1.2A - CONCERNS (due to admin conflict, not inheritance design)

### Database Verification
```bash
# Verified single table created
$ python manage.py migrate
$ sqlite3 database/samplify.db ".schema catalog_file"

# Result: Single table, no FilesVideo/Audio/Image tables ✅
```

### Field Mapping from Legacy
| SQLAlchemy Model | Django Field | Notes |
|------------------|--------------|-------|
| `FilesVideo.file_path` | `File.file_path` | ✅ Preserved |
| `FilesAudio.sample_rate` | `File.sample_rate` | ✅ Nullable |
| `FilesImage.file_format` | `File.file_format` | ✅ Preserved |
| Discriminator | `media_type` | ✅ New field |

---

## Migration Strategy

### From SQLAlchemy to Django
1. Create Django model with all fields from FilesVideo/Audio/Image
2. Make type-specific fields nullable (`null=True, blank=True`)
3. Add `media_type` discriminator field
4. Generate Django migration
5. (Future) Data migration script to populate `media_type` from legacy tables

### Migration File
- `apps/catalog/migrations/0001_initial.py` - Creates `catalog_file` table

---

## References

- **NFR12:** Single-table inheritance requirement
- **Story 1.2A:** File Model (Single-Table Inheritance)
- **Legacy Schema:** SQLAlchemy models (FilesVideo, FilesAudio, FilesImage)
- **Implementation:** `apps/catalog/models.py:18-130`
- **QA Report:** `docs/qa/RETROACTIVE-QA-REPORT-1.1-1.2C.md`

---

## Notes

**Implementation Observations:**
- Type hints (PEP 484) used throughout model
- Strategic indexes improve query performance
- `__str__()` and `get_absolute_path()` methods clean and functional

**Future Enhancements:**
- Consider custom managers for type-specific queries (`File.audio.all()`)
- Add field applicability validation in `clean()` method
- Monitor schema bloat if many type-specific fields added

**Scope Creep Identified:**
- `processing_status` field added but not in Story 1.2A AC
- Appears to be forward-looking addition from Story 1.6
- Documented as technical debt, acceptable given forward compatibility

---

**Last Updated:** 2025-10-06 (ADR formalized retroactively)
