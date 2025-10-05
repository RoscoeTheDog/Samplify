# Development Tools

### Required Tools

1. **Black** (code formatter)
   - Line length: 120
   - Target Python version: 3.10+

2. **Pylint** (linter)
   - Score threshold: 8.5/10
   - Django plugin enabled

3. **mypy** (type checker)
   - Strict mode enabled
   - Django stubs installed

4. **isort** (import sorter)
   - Profile: django
   - Line length: 120

### Configuration Files

**pyproject.toml**:
```toml
[tool.black]
line-length = 120
target-version = ['py310']

[tool.isort]
profile = "django"
line_length = 120
multi_line_output = 3
include_trailing_comma = true

[tool.mypy]
python_version = "3.10"
strict = true
plugins = ["mypy_django_plugin.main"]

[tool.pylint.messages_control]
max-line-length = 120
disable = ["C0111"]
```

**Pre-commit hooks** (.pre-commit-config.yaml):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        args: [--line-length=120]

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=django, --line-length=120]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        args: [--strict]

  - repo: https://github.com/PyCQA/pylint
    rev: v3.0.2
    hooks:
      - id: pylint
        args: [--max-line-length=120]
```

---
