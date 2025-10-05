# Custom Preferences

### Additional Requirements

#### String Formatting
**Pattern**: f-strings exclusively (except SQL parameters, i18n)

```python
# ✅ f-strings
logger.info(f"Processing {file_path} with schema {schema_id}")
error_msg = f"Invalid rate: {rate}. Expected: {MIN_RATE}-{MAX_RATE}"
```

#### Path Handling
**Pattern**: pathlib.Path exclusively

```python
from pathlib import Path

# ✅ pathlib.Path
file_path = Path("uploads") / "audio" / "file.wav"
file_path.exists()
file_path.read_text()
```

#### Configuration Management
**Pattern**: Layered approach (12-factor app methodology)

1. **Environment variables** (.env files)
2. **Django settings** (base/production/development)
3. **Application constants** (constants.py)
4. **Feature flags** (database-backed)
5. **Secrets management** (AWS Secrets Manager for production)

#### Dependency Injection
**Pattern**: No formal DI framework - pass as needed (Django's pragmatic approach)

```python
class AudioService:
    def __init__(self, storage=None, logger=None):
        from django.core.files.storage import default_storage
        self.storage = storage or default_storage
        self.logger = logger or logger
```

---
