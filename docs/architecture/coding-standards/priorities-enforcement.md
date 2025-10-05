# Priorities & Enforcement

### Priority Ranking (1=most important, 10=least)

1. **Clear, descriptive naming** - Foundation of readable code
2. **Consistent patterns across codebase** - Reduces cognitive load
3. **Code readability over brevity** - Future-proof maintenance
4. **Error handling completeness** - Prevents silent failures
5. **Consistent formatting (automated)** - Zero mental effort with tools
6. **Test coverage** - Focus on critical paths
7. **Type safety (type hints)** - Helps with tooling
8. **Comprehensive documentation** - Good docstrings > extensive comments
9. **Git commit quality** - Important for collaboration
10. **Performance optimization** - Only optimize what's actually slow

### Enforcement Preferences

#### Enforcement Mechanism
**Pattern**: Lightweight pre-commit hooks + CI checks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort

  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
```

#### Standard Violations
**Pattern**: Graduated approach

- **Level 1 (Auto-fix)**: Formatting, imports - auto-fixes
- **Level 2 (Hard block)**: Security risks - must fix
- **Level 3 (Soft warning)**: Best practices - track as tech debt
- **Level 4 (Guidance)**: Nice-to-haves - warning only

#### Standard Updates
**Pattern**: Pragmatic solo process

- Track in version-controlled markdown
- Trial new standards on one module (1-2 weeks)
- Quarterly reviews
- Gradual adoption
- Document reasoning

---
