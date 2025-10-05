# Quick Reference

### Pre-Commit Checklist

- [ ] Run `black --line-length=120 .`
- [ ] Run `isort --profile=django --line-length=120 .`
- [ ] Run `mypy --strict .`
- [ ] Run `pylint --max-line-length=120 .` (score ≥ 8.5)
- [ ] All functions have Google-style docstrings
- [ ] All function signatures have type hints
- [ ] Complex logic has explanatory comments
- [ ] Algorithm preservation documented (if applicable)
- [ ] No lines exceed 120 characters
- [ ] Variable names are explicit and readable

### Naming Quick Reference

| Element | Pattern | Example |
|---------|---------|---------|
| Boolean var | is/has/can + description | `is_valid`, `has_permission`, `can_process` |
| Counter var | Descriptive name | `file_index`, `worker_count` |
| Collection var | Type suffix | `file_list`, `result_dict`, `error_set` |
| Constant | SCREAMING_SNAKE_CASE | `MAX_WORKERS`, `API_ENDPOINT` |
| Function (action) | Verb-Noun / Strong verb | `validate_input()`, `process_files()` |
| Function (query) | get/find/fetch | `get_user()`, `find_match()`, `fetch_data()` |
| Function (bool) | is/has/can | `is_valid()`, `has_errors()`, `can_delete()` |
| Private function | Single underscore | `_internal_helper()` |
| Class | PascalCase | `FileProcessor`, `UserFactory` |
| Module | snake_case | `file_processor.py`, `utils.py` |
| Django app | Plural | `users/`, `schemas/`, `files/` |

### Common Patterns

**Complex boolean**:
```python
if (
    condition_one
    and condition_two
    and not condition_three
):
    pass
```

**Guard clauses**:
```python
def process(data):
    if not data:
        return None
    if not validate(data):
        return None
    # Main logic
    return result
```

**Error handling**:
```python
try:
    result = operation()
except SpecificError as e:
    logger.error(f"Context: {e}")
    raise ProcessingError(f"Message") from e
```

**enumerate()**:
```python
for index, item in enumerate(items):
    process(item, position=index)
```

---

**Version History**:
- **3.1** (2025-10-03): Enhanced Loguru features - Advanced tracing, exception hooks, log analysis
  - Added: Advanced Function Tracing (pattern-based rules, performance tracers)
  - Added: Global Exception Hooks (beautiful formatting, thread support)
  - Added: Log Analysis and Monitoring (health checks, pattern search, reports)
- **3.0** (2025-10-03): Complete elicitation - All 13 sections with comprehensive preferences
  - Added: Error Handling & Validation
  - Added: Django-Specific Patterns
  - Added: Testing Conventions
  - Added: Performance & Optimization
  - Added: Logging & Debugging (Enhanced Loguru)
  - Added: Git & Version Control
  - Added: Custom Preferences
  - Added: Priorities & Enforcement
  - Added: AI Agent Requirements
- **2.0** (2025-10-03): Enhanced with elicited preferences (Sections 1-4)
- **1.0** (2025-10-03): Initial coding standards document
