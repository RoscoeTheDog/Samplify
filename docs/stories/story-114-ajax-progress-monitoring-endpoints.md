# Story 1.14: AJAX Progress Monitoring Endpoints

## Status
**Approved**

---

## User Story
As a **developer**,
I want **JSON endpoints for real-time progress updates**,
So that **the UI can display batch processing status without page refresh**.

---

## Story Context
**Existing System Integration:**
- Integrates with: Story 1.6 (batch processing), Story 1.15 (queue visualization)
- Technology: Django REST endpoints, AJAX polling
- Follows pattern: NFR4 progressive enhancement with AJAX
- Touch points: Batch processing status, queue updates

---

## Acceptance Criteria

**Functional Requirements:**
1. `/api/processing/status/` endpoint returns JSON:
   ```json
   {
     "status": "processing|idle|completed",
     "total_files": 245,
     "processed_files": 127,
     "failed_files": 3,
     "current_file": "kick_01.wav",
     "progress_percent": 51.8
   }
   ```
2. `/api/queue/files/` endpoint returns file list with metadata
3. `/api/queue/filter/<uid>/` endpoint returns filtered files by UID
4. Endpoints update every 1-2 seconds (NFR4 requirement)
5. Endpoints return 304 Not Modified when no changes (efficiency)

**Integration Requirements:**
6. Integrates with batch processing (Story 1.6)
7. Provides data for queue visualization (Story 1.15)
8. Uses File model (Story 1.2A) for file data
9. No authentication required (NFR13)

**Quality Requirements:**
10. Response time <100ms (low latency)
11. JSON format validated and consistent
12. Endpoints handle concurrent requests
13. Error responses are meaningful (500/404 handling)

---

## Tasks / Subtasks

- [ ] **Task 1: Create processing status endpoint** (AC: 1, 6, 10)
  - [ ] Create `samplify/views/api/processing_status.py`
  - [ ] Implement ProcessingStatusView (returns JSON status)
  - [ ] Query batch processing state from cache or database
  - [ ] Calculate progress percentage
  - [ ] Return current file being processed

- [ ] **Task 2: Create queue files endpoint** (AC: 2, 8, 10)
  - [ ] Implement QueueFilesView (returns file list)
  - [ ] Query File model with pending/processing status
  - [ ] Return file metadata (UID, name, path, format, SR, BD)
  - [ ] Paginate results (limit 100 files per request)

- [ ] **Task 3: Create UID filter endpoint** (AC: 3, 7, 10)
  - [ ] Implement FilterByUIDView (returns filtered files)
  - [ ] Parse comma-delimited UID list from URL parameter
  - [ ] Query files matching UIDs
  - [ ] Return filtered file list with metadata

- [ ] **Task 4: Implement 304 Not Modified optimization** (AC: 5, 10)
  - [ ] Track last modified timestamp for each endpoint
  - [ ] Check If-Modified-Since header in request
  - [ ] Return 304 if no changes since last request
  - [ ] Use Django cache for tracking modifications

- [ ] **Task 5: Add response caching** (AC: 4, 5, 10)
  - [ ] Cache endpoint responses (1-2 second TTL)
  - [ ] Invalidate cache on file status change
  - [ ] Use ETag headers for cache validation

- [ ] **Task 6: Optimize database queries** (AC: 10, 12)
  - [ ] Use select_related and prefetch_related for joins
  - [ ] Add database indexes on frequently queried fields
  - [ ] Limit query results (pagination)
  - [ ] Use only() and defer() to reduce data transfer

- [ ] **Task 7: Add error handling** (AC: 13)
  - [ ] Return 404 for invalid UID
  - [ ] Return 500 with error message on exceptions
  - [ ] Log errors with loguru
  - [ ] Validate JSON response format

- [ ] **Task 8: Testing** (AC: 10, 11, 12, 13)
  - [ ] Test response format for all endpoints
  - [ ] Test 304 Not Modified optimization
  - [ ] Load test with concurrent requests
  - [ ] Test error responses (404, 500)
  - [ ] Verify response time <100ms

---

## Dev Notes

### Previous Story Insights
**From Story 1.6 (Batch Processing Management Command):**
- Batch processing state stored in Django cache [Source: Story 1.6 Dev Agent Record]
- File status tracked in File model (pending/processing/completed/failed)
- Processing uses multiprocessing (CR2)

**From Story 1.2A (File Model):**
- File model at `apps/catalog/models.py` [Source: Story 1.2A]
- UID generated as hash of file path
- Status field tracks processing state

### File Locations (Source Tree)
**API View Location:** [Source: architecture/source-tree.md]
```
samplify/
└── views/
    └── api/
        ├── processing_status.py    # Create this file
        ├── queue_files.py          # Create this file
        └── filter_uid.py           # Create this file
```

**URL Routing:**
```
samplify/
└── urls.py                         # Add API routes
```

**Test Location:**
```
tests/
└── test_api_endpoints.py           # Create this file
```

### Data Models
**File Model (Story 1.2A):** [Source: architecture/database-schema-design.md]
```python
class File(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)
    uid = models.CharField(max_length=8, unique=True)  # Generated hash
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_format = models.CharField(max_length=50)
    sample_rate = models.IntegerField(null=True, blank=True)
    bit_depth = models.IntegerField(null=True, blank=True)
```

### Implementation Patterns

**Processing Status Endpoint:**
```python
from django.http import JsonResponse
from django.views import View
from django.core.cache import cache
from apps.catalog.models import File

class ProcessingStatusView(View):
    def get(self, request):
        # Get batch processing state from cache
        processing_state = cache.get('batch_processing_state', {})

        total_files = File.objects.count()
        processed_files = File.objects.filter(status='completed').count()
        failed_files = File.objects.filter(status='failed').count()
        current_file = processing_state.get('current_file', None)

        progress_percent = (processed_files / total_files * 100) if total_files > 0 else 0

        status = 'idle'
        if processing_state.get('is_running'):
            status = 'processing'
        elif processed_files == total_files:
            status = 'completed'

        response_data = {
            'status': status,
            'total_files': total_files,
            'processed_files': processed_files,
            'failed_files': failed_files,
            'current_file': current_file,
            'progress_percent': round(progress_percent, 1)
        }

        return JsonResponse(response_data)
```

**Queue Files Endpoint:**
```python
from django.http import JsonResponse
from django.views import View
from apps.catalog.models import File

class QueueFilesView(View):
    def get(self, request):
        # Query files with pagination
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 100)), 100)  # Max 100
        offset = (page - 1) * limit

        files = File.objects.filter(
            status__in=['pending', 'processing']
        ).only(
            'uid', 'file_name', 'file_path', 'file_format', 'sample_rate', 'bit_depth', 'status'
        )[offset:offset + limit]

        files_data = [
            {
                'uid': f.uid,
                'file_name': f.file_name,
                'file_path': f.file_path,
                'file_format': f.file_format,
                'sample_rate': f.sample_rate,
                'bit_depth': f.bit_depth,
                'status': f.status
            }
            for f in files
        ]

        return JsonResponse({
            'files': files_data,
            'page': page,
            'total': File.objects.filter(status__in=['pending', 'processing']).count()
        })
```

**UID Filter Endpoint:**
```python
from django.http import JsonResponse
from django.views import View
from apps.catalog.models import File

class FilterByUIDView(View):
    def get(self, request, uids):
        # Parse comma-delimited UIDs: #a1f2,#b3e4,#c5d6
        uid_list = [uid.strip().lstrip('#') for uid in uids.split(',')]

        files = File.objects.filter(uid__in=uid_list).only(
            'uid', 'file_name', 'file_path', 'file_format', 'sample_rate', 'bit_depth', 'status'
        )

        if not files.exists():
            return JsonResponse({'error': 'No files found for given UIDs'}, status=404)

        files_data = [
            {
                'uid': f.uid,
                'file_name': f.file_name,
                'file_path': f.file_path,
                'file_format': f.file_format,
                'sample_rate': f.sample_rate,
                'bit_depth': f.bit_depth,
                'status': f.status
            }
            for f in files
        ]

        return JsonResponse({'files': files_data})
```

**304 Not Modified Optimization:**
```python
from django.views import View
from django.http import JsonResponse, HttpResponseNotModified
from django.core.cache import cache
from django.utils.http import http_date
import time

class OptimizedAPIView(View):
    cache_key = 'api_last_modified'
    cache_ttl = 2  # 2 seconds

    def get(self, request):
        # Get last modified timestamp
        last_modified = cache.get(self.cache_key, time.time())

        # Check If-Modified-Since header
        if_modified_since = request.META.get('HTTP_IF_MODIFIED_SINCE')
        if if_modified_since:
            if_modified_since_timestamp = time.mktime(time.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT'))
            if if_modified_since_timestamp >= last_modified:
                return HttpResponseNotModified()

        # Generate response
        response_data = self.get_response_data()
        response = JsonResponse(response_data)

        # Set Last-Modified header
        response['Last-Modified'] = http_date(last_modified)
        response['Cache-Control'] = f'max-age={self.cache_ttl}'

        return response

    def get_response_data(self):
        # Override in subclass
        raise NotImplementedError
```

**URL Routing:**
```python
# samplify/urls.py
from django.urls import path
from samplify.views.api.processing_status import ProcessingStatusView
from samplify.views.api.queue_files import QueueFilesView
from samplify.views.api.filter_uid import FilterByUIDView

urlpatterns = [
    path('api/processing/status/', ProcessingStatusView.as_view(), name='processing_status'),
    path('api/queue/files/', QueueFilesView.as_view(), name='queue_files'),
    path('api/queue/filter/<str:uids>/', FilterByUIDView.as_view(), name='filter_by_uid'),
]
```

### Database Optimization
**Indexes for fast queries:** [Source: architecture/database-schema-design.md]
```python
class File(models.Model):
    # ... fields ...

    class Meta:
        indexes = [
            models.Index(fields=['status']),  # Fast status filtering
            models.Index(fields=['uid']),     # Fast UID lookup
            models.Index(fields=['created_at']),  # Fast sorting
        ]
```

### Preservation Rules
**NFR4 Compliance:** Progressive enhancement with AJAX [Source: requirements.md NFR4]
- Endpoints support 1-2 second polling
- 304 Not Modified optimization reduces bandwidth

**NFR13 Compliance:** No authentication required [Source: requirements.md NFR13]
- Endpoints accessible without login (local application)

---

## Dev Notes > Testing

### Test File Location
[Source: architecture/testing-strategy.md]
```
tests/
└── test_api_endpoints.py
```

### Testing Standards
**Framework:** pytest + pytest-django [Source: architecture/tech-stack.md]

**Test Coverage Target:** 80%+ for API endpoints [Source: architecture/testing-strategy.md]

**Test Categories:**
1. **Unit Tests - Response Format**
   - Test processing status JSON structure
   - Test queue files JSON structure
   - Test UID filter JSON structure
   - Test error responses (404, 500)

2. **Integration Tests - Database Queries**
   - Test endpoint with 1000+ files
   - Test pagination
   - Test UID filtering with comma-delimited list

3. **Performance Tests - Response Time**
   - Test response time <100ms
   - Load test with concurrent requests (10+ simultaneous)
   - Test 304 Not Modified reduces load

4. **Caching Tests**
   - Test cache invalidation on file status change
   - Test If-Modified-Since header
   - Test ETag validation

**Example Test:**
```python
import pytest
from django.test import TestCase, Client
from apps.catalog.models import File
import time

class APIEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test files
        for i in range(10):
            File.objects.create(
                file_path=f'/media/test_{i}.wav',
                file_name=f'test_{i}.wav',
                uid=f'uid{i:03d}',
                status='pending' if i < 5 else 'completed'
            )

    def test_processing_status_response_format(self):
        """Test processing status endpoint returns correct JSON."""
        response = self.client.get('/api/processing/status/')

        assert response.status_code == 200
        data = response.json()

        assert 'status' in data
        assert 'total_files' in data
        assert 'processed_files' in data
        assert 'progress_percent' in data
        assert data['total_files'] == 10
        assert data['processed_files'] == 5

    def test_queue_files_pagination(self):
        """Test queue files endpoint pagination."""
        response = self.client.get('/api/queue/files/?page=1&limit=3')

        assert response.status_code == 200
        data = response.json()

        assert 'files' in data
        assert len(data['files']) == 3
        assert data['page'] == 1

    def test_uid_filter_endpoint(self):
        """Test UID filter endpoint."""
        response = self.client.get('/api/queue/filter/uid001,uid002/')

        assert response.status_code == 200
        data = response.json()

        assert 'files' in data
        assert len(data['files']) == 2
        assert data['files'][0]['uid'] in ['uid001', 'uid002']

    def test_304_not_modified(self):
        """Test 304 Not Modified optimization."""
        # First request
        response1 = self.client.get('/api/processing/status/')
        last_modified = response1['Last-Modified']

        # Second request with If-Modified-Since
        response2 = self.client.get(
            '/api/processing/status/',
            HTTP_IF_MODIFIED_SINCE=last_modified
        )

        assert response2.status_code == 304

    def test_response_time_under_100ms(self):
        """Test endpoint response time <100ms."""
        start = time.time()
        response = self.client.get('/api/processing/status/')
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        assert elapsed < 100
```

**Running Tests:**
```bash
# Run API endpoint tests
pytest tests/test_api_endpoints.py -v

# Run with coverage
pytest tests/test_api_endpoints.py --cov=samplify.views.api --cov-report=html

# Performance test
pytest tests/test_api_endpoints.py::test_response_time_under_100ms -v
```

---

## Definition of Done
- [ ] JSON endpoints implemented
- [ ] Response format validated
- [ ] Polling tested (1-2 second intervals)
- [ ] 304 Not Modified optimization working
- [ ] Error handling tested
- [ ] Documentation updated with API endpoint details

---

## Risk Assessment
- **Primary Risk:** High polling frequency degrades performance
- **Mitigation:** Response caching, 304 Not Modified, efficient queries
- **Rollback:** Increase polling interval or disable real-time updates

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
