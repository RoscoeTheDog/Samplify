# /browse-profile-templates Task

When this command is used, execute the following task:

<!-- Powered by BMAD™ Core -->

# Browse Profile Templates

## Purpose

This task helps users explore and understand available project profile templates. It shows template hierarchies, inheritance relationships, and helps users select appropriate templates for their projects.

## Overview

Templates are organized in a three-tier hierarchy:

```
bmad-core/templates/project-profiles/
├── base/                  # Universal principles
├── languages/             # Language-specific
└── frameworks/            # Framework-specific
```

This task provides an interactive browser to navigate and understand these templates.

## Main Menu

When user invokes `/browse-profile-templates`:

```
📚 Project Profile Template Browser

Available template categories:
1. Base Templates (3) - Universal coding principles
2. Language Templates (3) - Python, C++, TypeScript
3. Framework Templates (2) - Django, React
4. View all templates (tree view)
5. Search templates
6. Show template inheritance diagram
7. Exit

Select 1-7:
```

## View 1: Base Templates

Show universal templates that apply to all projects:

```
📋 Base Templates

These templates provide universal coding principles that apply
across all languages and frameworks.

1. coding-style-base
   Purpose: Core code organization, naming, quality principles
   Sections: Code organization, naming conventions, code quality,
             error handling, critical rules, documentation
   Inheritance: None (root template)
   Output: .ai/profiles/coding-standards.md

2. comment-guidelines-base
   Purpose: When and how to write comments
   Sections: Comment philosophy, required comments, discouraged patterns,
             structure, TODO policy, examples
   Inheritance: None (root template)
   Output: .ai/profiles/comment-guidelines.md

3. experience-levels-base
   Purpose: Define developer experience and learning preferences
   Sections: Team composition, programming experience, language expertise,
             architecture experience, testing, learning preferences
   Inheritance: None (root template)
   Output: .ai/profiles/experience-levels.md

Select template (1-3) for details, or [B]ack:
```

## View 2: Language Templates

Show language-specific templates:

```
💻 Language Templates

These templates extend base templates with language-specific
conventions and best practices.

1. Python (coding-style-python)
   Inherits from: base/coding-style-base
   Adds: Python version, style tools (Ruff, Black), type hints,
         docstrings, import organization, class design, idioms
   Best for: Python 3.x projects

2. C++ (coding-style-cpp)
   Inherits from: base/coding-style-base
   Adds: C++ standard, compiler settings, header organization,
         memory management, modern C++ features, templates
   Best for: C++11/14/17/20/23 projects

3. TypeScript (coding-style-typescript)
   Inherits from: base/coding-style-base
   Adds: Type system usage, interfaces vs types, module organization,
         generics, async patterns, React/Node.js integration
   Best for: TypeScript projects (web or Node.js)

Select template (1-3) for details, or [B]ack:
```

## View 3: Framework Templates

Show framework-specific templates:

```
🎯 Framework Templates

These templates extend language templates with framework-specific
patterns and conventions.

1. Django (django-context)
   Inherits from: base/coding-style-base, languages/python/coding-style-python
   Adds: Django version, project structure, models, views, URLs,
         forms, templates, DRF, migrations, admin, signals
   Best for: Django web applications
   Requires: Python template

2. React (react-context)
   Inherits from: base/coding-style-base, languages/typescript/coding-style-typescript
   Adds: React version, component patterns, hooks, state management,
         styling, routing, forms, testing, accessibility
   Best for: React applications (with or without Next.js)
   Requires: TypeScript or JavaScript template

Select template (1-2) for details, or [B]ack:
```

## Detailed Template View

When user selects a specific template:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Template: coding-style-python
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID: coding-style-python
Name: Python Coding Style Context
Version: 1.0
Type: developer-context

Inheritance:
  Extends: base/coding-style-base
  ↳ Inherits all sections from base template
  ↳ Adds Python-specific sections
  ↳ Can be extended by framework templates (Django, etc.)

Output:
  Format: Markdown
  File: .ai/profiles/coding-standards.md
  Title: Python Coding Standards

Sections (11):
  1. Python Version and Runtime
     - Python version requirements
     - Virtual environment approach

  2. Style and Linting Tools
     - Formatter: Black, Ruff, autopep8, YAPF
     - Linter: Pylint, Flake8, Ruff
     - Type checker: mypy, pyright
     - Line length configuration

  3. Python Naming Conventions
     - Module/package naming
     - Class, function, constant naming
     - Private member conventions

  4. Type Hints Policy
     - Type hints requirement level
     - Type hint style preferences
     - Generic types usage

  5. Docstring Standards
     - Docstring format: Google, NumPy, Sphinx
     - Required sections
     - Examples

  [... 6 more sections ...]

Elicitation:
  Mode: interactive
  Method: advanced-elicitation
  All sections marked elicit: true for user review

Use Cases:
  ✓ Python web applications (Django, Flask, FastAPI)
  ✓ Python data science projects
  ✓ Python CLI tools
  ✓ Python libraries and packages

Template File:
  Location: bmad-core/templates/developer-context/languages/python/coding-style-python.yaml
  Size: 8.4 KB

Options:
1. View full template YAML
2. Show example output
3. Show inheritance chain
4. Use this template
5. Return to browser

Select 1-5:
```

## View 4: Tree View

Show all templates in a hierarchical tree:

```
📁 All Project Profile Templates

bmad-core/templates/project-profiles/
│
├── 📂 base/
│   ├── 📄 coding-style-base.yaml
│   │   • Universal coding principles
│   │   • Output: coding-standards.md
│   │
│   ├── 📄 comment-guidelines-base.yaml
│   │   • Comment standards
│   │   • Output: comment-guidelines.md
│   │
│   └── 📄 experience-levels-base.yaml
│       • Developer experience and preferences
│       • Output: experience-levels.md
│
├── 📂 languages/
│   ├── 📂 python/
│   │   └── 📄 coding-style-python.yaml
│   │       • Extends: base/coding-style-base
│   │       • Python-specific conventions
│   │
│   ├── 📂 cpp/
│   │   └── 📄 coding-style-cpp.yaml
│   │       • Extends: base/coding-style-base
│   │       • C++ specific conventions
│   │
│   └── 📂 typescript/
│       └── 📄 coding-style-typescript.yaml
│           • Extends: base/coding-style-base
│           • TypeScript-specific conventions
│
└── 📂 frameworks/
    ├── 📂 django/
    │   └── 📄 django-context.yaml
    │       • Extends: base/coding-style-base
    │       •          languages/python/coding-style-python
    │       • Django-specific patterns
    │
    └── 📂 react/
        └── 📄 react-context.yaml
            • Extends: base/coding-style-base
            •          languages/typescript/coding-style-typescript
            • React-specific patterns

Total: 8 templates (3 base, 3 language, 2 framework)

Select path to explore, or [B]ack:
```

## View 5: Search Templates

Allow keyword search across templates:

```
🔍 Search Templates

Enter search term (template name, section, or keyword):
> type hints

Found 3 matches for "type hints":

1. coding-style-python (languages/python)
   Section: "Type Hints Policy"
   - Type hints requirement level
   - Type hint style preferences

2. coding-style-typescript (languages/typescript)
   Section: "Type System Usage"
   - Type inference vs explicit typing
   - any usage policy

3. django-context (frameworks/django)
   Section: "Models Patterns"
   - Mentions type hints for Django ORM

Select result (1-3) for details, or [B]ack:
```

## View 6: Inheritance Diagram

Show template inheritance relationships:

```
🌳 Template Inheritance Diagram

Base Layer (Universal):
┌──────────────────────────┐
│ coding-style-base        │
│ comment-guidelines-base  │
│ experience-levels-base   │
└──────────────────────────┘
           ▲
           │ inherits
           │
Language Layer:
┌──────────┴────────┬──────────────┬──────────────┐
│                   │              │              │
▼                   ▼              ▼              ▼
coding-style-    coding-style-  coding-style-  (others)
python           cpp            typescript
│                │              │
│                │              │ inherits
│                │              │
Framework Layer:
▼                                 ▼
django-context                react-context


Template Combinations:

Python Project:
  base/coding-style-base
  ↓
  languages/python/coding-style-python

Python + Django Project:
  base/coding-style-base
  ↓
  languages/python/coding-style-python
  ↓
  frameworks/django/django-context

TypeScript + React Project:
  base/coding-style-base
  ↓
  languages/typescript/coding-style-typescript
  ↓
  frameworks/react/react-context

C++ Project:
  base/coding-style-base
  ↓
  languages/cpp/coding-style-cpp

[B]ack to menu
```

## Template Recommendations

Based on project detection:

```
💡 Template Recommendations

Based on your current project:
  Detected: Python 3.12, Django 5.0

Recommended template combination:
  1. base/coding-style-base ⭐
  2. base/comment-guidelines-base ⭐
  3. base/experience-levels-base ⭐
  4. languages/python/coding-style-python ⭐
  5. frameworks/django/django-context ⭐

Optional additions:
  6. API documentation template (if building APIs)
  7. Data science template (if using pandas/numpy)

Options:
1. Use recommended templates
2. Customize selection
3. View each template first
4. Cancel

Select 1-4:
```

## Example Output Preview

When user wants to see example output:

```
📄 Example Output: coding-style-python

This is what will be generated in .ai/profiles/coding-standards.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Python Coding Standards

## Python Version and Runtime

- **Python Version:** 3.12+
- **Virtual Environment:** poetry

## Style and Linting Tools

- **Formatter:** Ruff
- **Linter:** Ruff
- **Type Checker:** mypy
- **Import Sorter:** Ruff
- **Line Length:** 100
- **Config Files:** pyproject.toml

## Type Hints Policy

**Type Hints Requirement:** Required-All
**Type Hints Style:** Modern-Style-3.9+

All functions and methods must have type hints for
parameters and return values...

[... continued ...]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is a preview with example values.
Actual output will be customized during setup.

[V]iew more | [B]ack
```

## Integration with Setup

Quick path to setup from browser:

```
Found a template you want to use?

Options:
1. Setup project profile with this template
2. Add to template selection list
3. Continue browsing
4. Exit

Select 1-4:
> 1

Starting project profile setup with selected template...
[Launches /init-profile with pre-selected template]
```

## Template Metadata

Show additional information about templates:

```
📊 Template Statistics

Total templates: 8
  Base: 3 (37.5%)
  Language: 3 (37.5%)
  Framework: 2 (25%)

Coverage:
  Languages: Python, C++, TypeScript
  Frameworks: Django, React

Average sections per template: 8.5
Average template size: 6.2 KB

Most commonly used:
  1. coding-style-python (used in 45% of profiles)
  2. coding-style-typescript (used in 30% of profiles)
  3. django-context (used in 25% of profiles)

[B]ack to menu
```

## Error Handling

### Template Not Found

```
❌ Template file not found

Searched for: bmad-core/templates/developer-context/languages/rust/coding-style-rust.yaml

This template doesn't exist yet.

Would you like to:
1. Create custom template
2. Request template (open GitHub issue)
3. Use closest available template (Python)
4. Cancel

Select 1-4:
```

### Corrupted Template

```
❌ Error: Could not parse template

Template: coding-style-python
Error: Invalid YAML syntax at line 45

This template file appears to be corrupted.

Options:
1. View error details
2. Attempt to repair
3. Report issue
4. Skip this template

Select 1-4:
```

## Integration Points

This task uses:

- `bmad-core/templates/project-profiles/` - Template library
- File system scanning for template discovery
- YAML parsing for template metadata
- Optional: profile manager to show usage statistics

## Notes for AI Agents

- **Be informative**: Help users understand template purpose
- **Show relationships**: Explain inheritance clearly
- **Provide examples**: Show what output looks like
- **Guide selection**: Help users choose appropriate templates
- **Enable exploration**: Make browsing intuitive
- **Link to setup**: Easy path from browsing to using templates
