# API Endpoint Specification

**Version:** 1.0
**Last Updated:** 2025-10-04
**Status:** Design Document

---

## Overview

This document specifies all Django REST API endpoints for the Samplify web UI. The API supports:
- Schema CRUD operations
- File scanning and metadata retrieval
- Batch processing orchestration
- Real-time progress monitoring via AJAX polling
- Watchdog status management

**Design Principles:**
- RESTful resource-oriented design
- JSON request/response format
- Progressive enhancement (works without JavaScript)
- 1-2 second AJAX polling for real-time updates (NFR4)
- No authentication required (NFR13 - local-only application)

---

## Base Configuration

### URL Routing

```python
# samplify/urls.py
from django.urls import path, include

urlpatterns = [
    path('', include('apps.schemas.urls')),           # Schema management
    path('api/', include('apps.processing.urls')),    # Processing operations
    path('api/', include('apps.catalog.urls')),       # File catalog
]
```

### Response Format Standards

**Success Response:**
```json
{
  "success": true,
  "data": { /* resource data */ },
  "message": "Operation completed successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* additional context */ }
  }
}
```

**Pagination Envelope:**
```json
{
  "success": true,
  "data": [ /* items */ ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 245,
    "total_pages": 5
  }
}
```

---

## Schema Management Endpoints

### 1. List Schemas

**GET** `/schemas/`

Lists all saved processing schemas.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Audio Processing Template",
      "description": "Processes WAV files for drums and bass",
      "created_at": "2025-10-04T10:30:00Z",
      "updated_at": "2025-10-04T12:15:00Z",
      "is_active": true,
      "input_directory_count": 3,
      "output_directory_count": 5
    }
  ]
}
```

### 2. Get Schema Detail

**GET** `/schemas/<id>/`

Retrieves complete schema configuration including rules.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Audio Processing Template",
    "description": "Processes WAV files",
    "is_active": true,
    "input_directories": [
      {
        "id": 1,
        "path": "C:\\Input\\Samples",
        "monitor_enabled": true,
        "recursive": true
      }
    ],
    "output_directories": [
      {
        "id": 1,
        "path": "C:\\Output\\Drums",
        "filters": [
          {
            "id": 1,
            "type": "keyword",
            "value": "kick",
            "case_sensitive": false
          },
          {
            "id": 2,
            "type": "extension",
            "value": ".wav"
          }
        ],
        "processing_rules": [
          {
            "id": 1,
            "output_format": "WAV",
            "sample_rate": 44100,
            "bit_depth": 24,
            "normalize": true,
            "normalize_level": -6.0
          }
        ],
        "logic_operator": "AND"
      }
    ]
  }
}
```

### 3. Create Schema

**POST** `/schemas/`

Creates a new processing schema.

**Request:**
```json
{
  "name": "New Audio Template",
  "description": "Description here",
  "is_active": false,
  "input_directories": [
    {
      "path": "C:\\Input\\NewFolder",
      "monitor_enabled": true,
      "recursive": true
    }
  ],
  "output_directories": [
    {
      "path": "C:\\Output\\Processed",
      "filters": [
        {"type": "keyword", "value": "sample"}
      ],
      "processing_rules": [
        {"output_format": "WAV", "sample_rate": 48000}
      ],
      "logic_operator": "AND"
    }
  ]
}
```

**Response:** Same as Get Schema Detail

### 4. Update Schema

**PUT** `/schemas/<id>/`
**PATCH** `/schemas/<id>/` (partial update)

Updates existing schema configuration.

**Request:** Same structure as Create Schema
**Response:** Same as Get Schema Detail

### 5. Delete Schema

**DELETE** `/schemas/<id>/`

Deletes a schema (soft delete - marks as inactive).

**Response:**
```json
{
  "success": true,
  "message": "Schema deleted successfully"
}
```

### 6. Import XML Template

**POST** `/api/schemas/import-xml/`

Imports an XML template and creates corresponding schema in database (FR18).

**Request:**
```
Content-Type: multipart/form-data

file: <XML file upload>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "schema_id": 5,
    "name": "Imported Audio Template",
    "source_type": "imported",
    "import_report": {
      "rules_imported": 12,
      "transformations_imported": 5,
      "directory_mappings_imported": 3
    }
  },
  "message": "XML template imported successfully"
}
```

**Error Response (Invalid XML):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_XML_FORMAT",
    "message": "XML template is malformed or incompatible",
    "details": {
      "line": 15,
      "error": "Missing closing tag for 'rule'"
    }
  }
}
```

### 7. Export XML Template

**GET** `/api/schemas/<id>/export-xml/`

Exports a schema as XML template file for sharing or backup (FR18).

**Response:**
```
Content-Type: application/xml
Content-Disposition: attachment; filename="schema_audio_processing_template.xml"

<?xml version="1.0" encoding="UTF-8"?>
<template name="Audio Processing Template">
  <description>Processes WAV files for drums and bass</description>
  <rules>
    <rule type="keyword" value="kick" operator="AND"/>
    <rule type="extension" value=".wav" operator="AND"/>
  </rules>
  <transformations>
    <transformation format="WAV" sample_rate="44100" bit_depth="24" normalize="-6.0"/>
  </transformations>
  <directory_mappings>
    <mapping input="C:\Input\Samples" output="C:\Output\Drums" watched="true"/>
  </directory_mappings>
</template>
```

**Error Response (Schema Not Found):**
```json
{
  "success": false,
  "error": {
    "code": "SCHEMA_NOT_FOUND",
    "message": "Schema with ID 999 does not exist"
  }
}
```

---

## File Scanning Endpoints

### 8. Scan Input Directories

**POST** `/api/scan/`

Triggers file scanning for specified input directories and populates database with metadata.

**Request:**
```json
{
  "schema_id": 1,
  "input_directory_ids": [1, 2, 3],
  "force_rescan": false  // Re-scan already cataloged files
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "scan_id": "scan_abc123",
    "status": "running",
    "directories_scanned": 0,
    "files_found": 0,
    "files_processed": 0,
    "started_at": "2025-10-04T14:20:00Z"
  }
}
```

### 9. Get Scan Status

**GET** `/api/scan/<scan_id>/status/`

Polls scan progress (AJAX endpoint for real-time updates).

**Response:**
```json
{
  "success": true,
  "data": {
    "scan_id": "scan_abc123",
    "status": "running",  // "pending", "running", "completed", "failed"
    "progress": {
      "directories_scanned": 2,
      "files_found": 245,
      "files_processed": 180,
      "current_file": "C:\\Input\\Samples\\kick_03.wav",
      "percent_complete": 73
    },
    "started_at": "2025-10-04T14:20:00Z",
    "completed_at": null,
    "errors": []
  }
}
```

---

## File Catalog Endpoints

### 10. List Files

**GET** `/api/files/`

Retrieves paginated file catalog with filtering.

**Query Parameters:**
- `schema_id` (int): Filter by schema
- `input_directory_id` (int): Filter by input directory
- `media_type` (string): "audio", "video", "image"
- `format` (string): File format (e.g., "WAV", "MP3")
- `page` (int): Page number (default: 1)
- `per_page` (int): Results per page (default: 50, max: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "uid": "#a1f2",
      "filename": "kick_01.wav",
      "path": "C:\\Input\\Samples\\kick_01.wav",
      "media_type": "audio",
      "format": "WAV",
      "file_size": 1258291,  // bytes
      "created_at": "2025-09-15T08:30:00Z",
      "metadata": {
        "sample_rate": 44100,
        "bit_depth": 16,
        "channels": 2,
        "duration": 2.5  // seconds
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 245,
    "total_pages": 5
  }
}
```

### 11. Get File Detail

**GET** `/api/files/<id>/`

Retrieves detailed file metadata.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "uid": "#a1f2",
    "filename": "kick_01.wav",
    "path": "C:\\Input\\Samples\\kick_01.wav",
    "media_type": "audio",
    "format": "WAV",
    "file_size": 1258291,
    "created_at": "2025-09-15T08:30:00Z",
    "modified_at": "2025-09-15T08:30:00Z",
    "scanned_at": "2025-10-04T14:22:15Z",
    "metadata": {
      "sample_rate": 44100,
      "bit_depth": 16,
      "channels": 2,
      "channel_layout": "stereo",
      "duration": 2.5,
      "codec": "pcm_s16le",
      "bit_rate": 1411200
    },
    "processing_status": "pending",  // "pending", "processing", "completed", "failed"
    "output_mappings": [
      {
        "output_directory": "C:\\Output\\Drums",
        "processing_rule": {
          "output_format": "WAV",
          "sample_rate": 44100,
          "bit_depth": 24,
          "normalize": true
        }
      }
    ]
  }
}
```

---

## Batch Processing Endpoints

### 12. Preview Transformations

**POST** `/api/batch/preview/`

Generates preview of planned transformations without executing.

**Request:**
```json
{
  "schema_id": 1,
  "file_ids": [1, 2, 3]  // Optional: preview specific files
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_files": 245,
    "transformations": [
      {
        "file_id": 1,
        "uid": "#a1f2",
        "input_file": "C:\\Input\\Samples\\kick_01.wav",
        "output_file": "C:\\Output\\Drums\\kick_01.wav",
        "operations": [
          "Convert to 24-bit",
          "Normalize to -6dB"
        ],
        "estimated_size": 2516582  // bytes
      }
    ],
    "total_estimated_size": 615454220,  // bytes
    "estimated_duration": 180  // seconds
  }
}
```

### 13. Start Batch Processing

**POST** `/api/batch/start/`

Initiates batch processing operation.

**Request:**
```json
{
  "schema_id": 1,
  "file_ids": [1, 2, 3],  // Optional: process specific files only
  "overwrite_existing": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_xyz789",
    "status": "running",
    "total_files": 245,
    "started_at": "2025-10-04T15:00:00Z"
  }
}
```

### 14. Get Batch Processing Status

**GET** `/api/batch/<batch_id>/status/`

Polls batch processing progress (AJAX endpoint - poll every 1-2 seconds per NFR4).

**Response:**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_xyz789",
    "status": "running",  // "pending", "running", "completed", "failed", "paused"
    "progress": {
      "total_files": 245,
      "files_processed": 180,
      "files_failed": 2,
      "current_file": {
        "uid": "#c5d6",
        "filename": "snare_01.wav",
        "operation": "Normalizing audio"
      },
      "percent_complete": 73,
      "cpu_utilization": 65.2,  // percentage
      "workers_active": 8
    },
    "started_at": "2025-10-04T15:00:00Z",
    "estimated_completion": "2025-10-04T15:03:00Z",
    "completed_at": null,
    "errors": [
      {
        "file_id": 45,
        "filename": "corrupted.wav",
        "error": "Invalid WAV header"
      }
    ]
  }
}
```

### 15. Pause Batch Processing

**POST** `/api/batch/<batch_id>/pause/`

Pauses ongoing batch processing.

**Response:**
```json
{
  "success": true,
  "message": "Batch processing paused"
}
```

### 16. Resume Batch Processing

**POST** `/api/batch/<batch_id>/resume/`

Resumes paused batch processing.

**Response:**
```json
{
  "success": true,
  "message": "Batch processing resumed"
}
```

### 17. Cancel Batch Processing

**POST** `/api/batch/<batch_id>/cancel/`

Cancels batch processing (stops workers gracefully).

**Response:**
```json
{
  "success": true,
  "message": "Batch processing cancelled",
  "data": {
    "files_processed": 120,
    "files_remaining": 125
  }
}
```

---

## Watchdog Management Endpoints

### 18. Get Watchdog Status

**GET** `/api/watchdog/status/`

Retrieves current status of both file monitor and queue processor watchdogs.

**Response:**
```json
{
  "success": true,
  "data": {
    "file_monitor": {
      "status": "running",  // "stopped", "running", "error"
      "monitored_directories": 3,
      "events_detected": 45,
      "last_event_at": "2025-10-04T15:10:22Z",
      "uptime_seconds": 3600
    },
    "queue_processor": {
      "status": "running",
      "queue_size": 12,
      "files_processed": 230,
      "workers_active": 8,
      "cpu_utilization": 58.3,
      "uptime_seconds": 3600
    }
  }
}
```

### 19. Start File Monitor

**POST** `/api/watchdog/file-monitor/start/`

Starts file monitoring watchdog.

**Request:**
```json
{
  "schema_id": 1  // Optional: monitor specific schema's directories
}
```

**Response:**
```json
{
  "success": true,
  "message": "File monitor started",
  "data": {
    "status": "running",
    "monitored_directories": 3
  }
}
```

### 20. Stop File Monitor

**POST** `/api/watchdog/file-monitor/stop/`

Stops file monitoring watchdog.

**Response:**
```json
{
  "success": true,
  "message": "File monitor stopped"
}
```

### 21. Start Queue Processor

**POST** `/api/watchdog/queue-processor/start/`

Starts queue processing watchdog.

**Response:**
```json
{
  "success": true,
  "message": "Queue processor started",
  "data": {
    "status": "running",
    "workers_spawned": 8
  }
}
```

### 22. Stop Queue Processor

**POST** `/api/watchdog/queue-processor/stop/`

Stops queue processing watchdog (graceful shutdown).

**Response:**
```json
{
  "success": true,
  "message": "Queue processor stopped",
  "data": {
    "files_remaining_in_queue": 5
  }
}
```

---

## Error Codes

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `SCHEMA_NOT_FOUND` | 404 | Schema ID does not exist |
| `FILE_NOT_FOUND` | 404 | File ID does not exist |
| `BATCH_NOT_FOUND` | 404 | Batch ID does not exist |
| `INVALID_PARAMETER` | 400 | Request parameter validation failed |
| `FFMPEG_NOT_AVAILABLE` | 503 | FFmpeg binary not found or not working |
| `DIRECTORY_NOT_ACCESSIBLE` | 403 | Cannot access specified directory |
| `OPERATION_IN_PROGRESS` | 409 | Cannot modify resource during active operation |
| `INVALID_XML_FORMAT` | 400 | XML template is malformed or incompatible |
| `XML_EXPORT_FAILED` | 500 | Failed to generate XML from schema |
| `DATABASE_ERROR` | 500 | SQLite database operation failed |
| `WORKER_POOL_ERROR` | 500 | Multiprocessing worker pool error |

### Error Response Examples

**Schema not found:**
```json
{
  "success": false,
  "error": {
    "code": "SCHEMA_NOT_FOUND",
    "message": "Schema with ID 999 does not exist",
    "details": {
      "schema_id": 999
    }
  }
}
```

**FFmpeg not available:**
```json
{
  "success": false,
  "error": {
    "code": "FFMPEG_NOT_AVAILABLE",
    "message": "FFmpeg binary not found. Run setup script or install manually.",
    "details": {
      "expected_path": "bin/windows/ffmpeg.exe",
      "install_command": "python manage.py setup"
    }
  }
}
```

---

## AJAX Polling Patterns

### Recommended Polling Implementation

**Frontend JavaScript example:**
```javascript
function pollBatchStatus(batchId) {
  const intervalId = setInterval(async () => {
    const response = await fetch(`/api/batch/${batchId}/status/`);
    const data = await response.json();

    // Update UI with progress
    updateProgressBar(data.data.progress.percent_complete);

    // Stop polling when complete
    if (data.data.status === 'completed' || data.data.status === 'failed') {
      clearInterval(intervalId);
      handleCompletion(data);
    }
  }, 2000);  // Poll every 2 seconds (NFR4)
}
```

### Progressive Enhancement

All endpoints return proper HTTP status codes and can work without JavaScript:
- Form submissions → redirect to status page
- Status page → auto-refresh with `<meta http-equiv="refresh">`
- JavaScript enhances with AJAX polling for smoother UX

---

## Implementation Notes

### Django URL Configuration Example

```python
# apps/schemas/urls.py
from django.urls import path
from .views import schemas

urlpatterns = [
    # Schema CRUD
    path('schemas/', schemas.list_schemas, name='schema_list'),
    path('schemas/<int:id>/', schemas.get_schema, name='schema_detail'),
    path('schemas/create/', schemas.create_schema, name='schema_create'),
    path('schemas/<int:id>/update/', schemas.update_schema, name='schema_update'),
    path('schemas/<int:id>/delete/', schemas.delete_schema, name='schema_delete'),

    # XML Import/Export (FR18)
    path('api/schemas/import-xml/', schemas.import_xml_template, name='schema_import_xml'),
    path('api/schemas/<int:id>/export-xml/', schemas.export_xml_template, name='schema_export_xml'),
]

# apps/processing/urls.py
from django.urls import path
from .views import batch, scan, watchdog

urlpatterns = [
    # Scanning
    path('scan/', scan.scan_input_directories, name='scan_start'),
    path('scan/<str:scan_id>/status/', scan.get_scan_status, name='scan_status'),

    # Batch Processing
    path('batch/preview/', batch.preview_transformations, name='batch_preview'),
    path('batch/start/', batch.start_batch_processing, name='batch_start'),
    path('batch/<str:batch_id>/status/', batch.get_batch_status, name='batch_status'),
    path('batch/<str:batch_id>/pause/', batch.pause_batch, name='batch_pause'),
    path('batch/<str:batch_id>/resume/', batch.resume_batch, name='batch_resume'),
    path('batch/<str:batch_id>/cancel/', batch.cancel_batch, name='batch_cancel'),

    # Watchdog
    path('watchdog/status/', watchdog.get_status, name='watchdog_status'),
    path('watchdog/file-monitor/start/', watchdog.start_file_monitor, name='file_monitor_start'),
    path('watchdog/file-monitor/stop/', watchdog.stop_file_monitor, name='file_monitor_stop'),
    path('watchdog/queue-processor/start/', watchdog.start_queue_processor, name='queue_processor_start'),
    path('watchdog/queue-processor/stop/', watchdog.stop_queue_processor, name='queue_processor_stop'),
]
```

### CSRF Protection

Django CSRF protection enabled for all POST/PUT/PATCH/DELETE requests:
- Include `{% csrf_token %}` in forms
- Add `X-CSRFToken` header to AJAX requests
- Use Django's `ensure_csrf_cookie` decorator where needed

---

## Related Documents

- **[Frontend Component Architecture](./frontend-components.md)** - UI components consuming these APIs
- **[Database Schema Design](./database-schema-design.md)** - ORM models supporting these endpoints
- **[Technical Constraints](../prd/technical-constraints-and-integration-requirements.md)** - NFR requirements
