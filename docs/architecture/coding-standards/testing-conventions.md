# Testing Conventions

### Test Organization

#### Test File Naming
**Pattern**: Mirror source structure with `tests/test_<module>.py`

```
apps/schemas/
├── models.py
├── views.py
├── services.py
└── tests/
    ├── test_models.py
    ├── test_views.py
    └── test_services.py
```

#### Test Class Naming
**Pattern**: `Test<ClassName>` (pytest/unittest standard)

```python
class TestSchema(TestCase):
    """Tests for Schema model."""

    def test_create_schema(self):
        schema = Schema.objects.create(name="Test")
        self.assertEqual(schema.name, "Test")
```

#### Test Method Naming
**Pattern**: `test_<what>_<condition>_<expected>` (BDD-style)

```python
class TestFileProcessor(TestCase):
    def test_process_file_valid_audio_returns_result(self):
        result = process_file('valid.wav')
        self.assertIsInstance(result, AudioResult)

    def test_process_file_invalid_format_raises_error(self):
        with self.assertRaises(AudioFormatError):
            process_file('invalid.txt')
```

#### Test Docstrings
**Pattern**: Only for complex tests (method name should be sufficient)

```python
# ✅ No docstring needed - name is clear
def test_process_file_valid_wav_returns_result(self):
    result = process_file('test.wav')
    self.assertIsNotNone(result)


# ✅ Docstring adds value - complex setup
def test_concurrent_processing_with_shared_cache(self):
    """Test that concurrent file processing doesn't corrupt shared cache.

    Setup: Create 10 audio files, process concurrently with ThreadPoolExecutor
    Validates: No cache corruption, all results correct
    """
    pass
```

#### Test Assertion Messages
**Pattern**: Only for non-obvious assertions

```python
# ✅ Message adds debugging context
def test_process_multiple_files_all_succeed(self):
    files = ['file1.wav', 'file2.wav', 'file3.wav']
    results = [process_file(f) for f in files]

    for i, result in enumerate(results):
        self.assertTrue(
            result.success,
            f"Processing failed for {files[i]}: {result.error}"
        )
```

---
