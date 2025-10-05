# Error Handling & Validation

### Exception Handling Patterns

#### Exception Granularity
**Pattern**: Catch broad exceptions at top level, specific in functions

```python
# ✅ GOOD - Specific exceptions in business logic
def process_audio_file(path: str) -> AudioData:
    try:
        data = read_file(path)
    except FileNotFoundError:
        raise AudioFileError(f"Audio file not found: {path}")
    except PermissionError:
        raise AudioFileError(f"Cannot read file (permission denied): {path}")

    try:
        return parse_audio(data)
    except ValueError as e:
        raise AudioFormatError(f"Invalid audio format: {e}")


# ✅ GOOD - Broad exception at application boundary
def main():
    try:
        result = process_audio_file(args.input)
        save_result(result)
    except AudioFileError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        sys.exit(2)
```

#### Exception Chaining
**Pattern**: Only when adding context to exception

```python
# ✅ GOOD - Chain when adding domain context
def load_user_config(user_id: int) -> dict:
    try:
        data = fetch_from_database(user_id)
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ConfigurationError(
            f"Invalid configuration for user {user_id}"
        ) from e


# ✅ GOOD - Just re-raise when not adding context
def validate_data(data):
    try:
        check_format(data)
    except ValueError:
        raise  # Just re-raise, don't chain
```

#### Custom Exceptions
**Pattern**: Create exception hierarchy for domain

```python
# ✅ GOOD - Domain exception hierarchy
class SamplifyError(Exception):
    """Base exception for all Samplify errors."""
    pass


class AudioError(SamplifyError):
    """Audio processing errors."""
    pass


class AudioFileError(AudioError):
    """Audio file I/O errors."""
    pass


class SchemaError(SamplifyError):
    """Schema-related errors."""
    pass
```

#### Exception Messages
**Pattern**: Detailed with context

```python
# ✅ GOOD - Context + actual values + valid range
raise ValueError(
    f"Invalid sample rate: {sample_rate}. "
    f"Expected range: 8000-192000 Hz. "
    f"File: {file_path}"
)
```

#### Logging vs Raising
**Pattern**: Log only if handling exception, raise if propagating

```python
# ✅ GOOD - Log when handling (not re-raising)
def process_file(path):
    try:
        return parse_audio(path)
    except AudioFormatError as e:
        logger.warning(f"Skipping invalid file {path}: {e}")
        return None  # Handled


# ✅ GOOD - Don't log when propagating
def validate_schema(data):
    try:
        return parse_schema(data)
    except ValueError as e:
        raise SchemaValidationError(f"Invalid schema: {e}") from e
        # Let caller decide whether to log
```

---

### Input Validation

#### Validation Timing
**Pattern**: At function entry (fail fast)

```python
# ✅ GOOD - Validate at entry
def process_audio(file_path: str, sample_rate: int) -> AudioData:
    # Validate ALL inputs at the top
    if not file_path:
        raise ValueError("file_path is required")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not 8000 <= sample_rate <= 192000:
        raise ValueError(
            f"Invalid sample rate: {sample_rate}. Expected: 8000-192000 Hz"
        )

    # Now safe to proceed
    data = load_file(file_path)
    return resample(data, sample_rate)
```

#### Type Checking
**Pattern**: Type hints + mypy for development, isinstance() for runtime safety

```python
# ✅ GOOD - Type hints for static analysis
def create_schema(name: str, fields: list[dict[str, Any]]) -> Schema:
    # Runtime validation for critical types
    if not isinstance(name, str):
        raise TypeError(f"name must be str, got {type(name).__name__}")

    if not isinstance(fields, list):
        raise TypeError(f"fields must be list, got {type(fields).__name__}")

    # Business logic validation
    if not name.strip():
        raise ValueError("name cannot be empty")
```

#### Validation Helper Functions
**Pattern**: Raise for business logic, return bool for conditional checks

```python
# ✅ Pattern 1: Raise exceptions (business logic)
def validate_sample_rate(rate: int) -> None:
    """Validate sample rate or raise exception."""
    if not 8000 <= rate <= 192000:
        raise ValueError(f"Invalid sample rate: {rate}")


# ✅ Pattern 2: Return boolean (conditional logic)
def is_valid_sample_rate(rate: int) -> bool:
    """Check if sample rate is valid."""
    return isinstance(rate, int) and 8000 <= rate <= 192000
```

#### Assertion Statements
**Pattern**: Use for internal invariants only (never for user input)

```python
# ✅ GOOD - Assert for developer errors
def _internal_helper(data: list) -> None:
    """Internal function - caller must ensure data is not empty."""
    assert len(data) > 0, "Internal error: data should not be empty"
    process(data[0])


# ❌ NEVER - Assert for user input
def process_user_input(data: dict) -> None:
    assert 'name' in data  # Can be disabled with python -O!
    # Use explicit validation instead
```

---
