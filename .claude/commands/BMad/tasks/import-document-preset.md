# /import-document-preset Task

When this command is used, execute the following task:

<!-- Powered by BMAD™ Core -->

# Import Document Preset

## Purpose

Load saved preset or extract from another BMAD project to use during PRD and Architecture creation.

## When to Use

- Before creating PRD in a new project
- When you want to reuse standards from another project
- To apply team standards to current project
- To speed up document creation with pre-filled values

---

## Step 1: Show All Available Presets

Scan multiple locations and present unified list:

```
╔════════════════════════════════════════╗
║       Import Document Preset           ║
╚════════════════════════════════════════╝

Global Presets (in ~/.bmad-document-presets/):

1. 📦 my-api-standard (v1.0)
   FastAPI Microservices Standard
   Created: 2025-10-02

2. 📦 django-rest-standard (v1.0)
   Django REST API patterns
   Created: 2025-09-28

Project Local Presets (in ./.ai/document-presets/):

3. 📦 this-project-variant (v1.0)
   Variation of current project setup
   Created: 2025-10-01

──────────────────────────────────────

Other Import Options:

4. 📁 Import from custom file path
5. 🔍 Import from another BMAD project (auto-detect)

0. Cancel

Choose (0-5): _
```

**Scanning Logic:**

1. Scan `~/.bmad-document-presets/` for global presets
2. Scan `./.ai/document-presets/` for local presets
3. Read `preset-config.yaml` from each to get metadata
4. Number sequentially across all sources
5. Show options 4 and 5 at bottom

**If No Presets Found:**

```
╔════════════════════════════════════════╗
║       Import Document Preset           ║
╚════════════════════════════════════════╝

No saved presets found.

You can still:

4. 📁 Import from custom file path
5. 🔍 Import from another BMAD project (auto-detect)

0. Cancel

Choose (0, 4-5): _
```

---

## Option 4: Import from Custom Path

Allow user to specify any valid preset location:

```
Enter full path to preset directory:

> /Users/team/shared-presets/my-api-standard

Validating preset...
✓ Directory exists
✓ preset-config.yaml found
✓ prd-preset.yaml found
✓ architecture-preset.yaml found

Found preset:
  Name: FastAPI Microservices Standard
  Version: 1.0
  Created: 2025-10-02

Continue with import? (y/n): _
```

**Validation:**

- Check directory exists
- Verify all 3 YAML files present:
  - `preset-config.yaml`
  - `prd-preset.yaml`
  - `architecture-preset.yaml`
- Parse `preset-config.yaml` for metadata
- Show error if invalid

**Error Handling:**

```
❌ Invalid preset directory

Reason: Missing required files
  ✗ preset-config.yaml - NOT FOUND
  ✓ prd-preset.yaml - found
  ✓ architecture-preset.yaml - found

A valid preset must contain all 3 files.

Try again? (y/n): _
```

---

## Option 5: Import from BMAD Project

Detect and extract from another BMAD-enabled project:

```
Enter full path to BMAD-enabled project:

> /Users/me/projects/acme-api

Scanning project...
✓ .bmad-core/ directory found (BMAD-enabled)
✓ docs/prd.md found
✓ docs/architecture.md found

Found BMAD project: ACME API
  • PRD: docs/prd.md (last modified: 2025-09-15)
  • Architecture: docs/architecture.md (last modified: 2025-09-15)

This will:
  1. Extract documents from ACME API project
  2. Load as temporary preset for this session
  3. Allow you to use in PM/Architect agents

Continue? (y/n): y

Extracting documents... ✓

[Internally runs export-document-preset extraction logic,
 saves to temp location: .ai/temp-preset-import/,
 then proceeds to preview step]
```

**Detection Logic:**

1. Check for `.bmad-core/` directory (confirms BMAD project)
2. Check for `docs/prd.md`
3. Check for `docs/architecture.md`
4. If valid, extract sections (same as export task)
5. Save to `.ai/temp-preset-import/` temporarily
6. Continue to preview step

**Error Handling:**

```
❌ Not a valid BMAD project

Path: /Users/me/projects/some-project

Issues found:
  ✗ .bmad-core/ directory - NOT FOUND
  ✗ docs/prd.md - NOT FOUND
  ✗ docs/architecture.md - NOT FOUND

This does not appear to be a BMAD-enabled project.

Options:
  1. Try different path
  2. Use custom preset path instead (Option 4)
  3. Cancel

Choose (1-3): _
```

---

## Step 2: Preview Preset Details

Show **full itemized preview** of what will be imported:

```
═══ Preset Preview: my-api-standard ═══

Technical Assumptions (will pre-fill PRD):
  Languages:
    • Python 3.11+
    • TypeScript 5.0+
  Frameworks:
    • FastAPI 0.104+
    • React 18
  Database:
    • PostgreSQL 15+
  Repository: Monorepo
  Architecture: Microservices
  Testing: Full pyramid

Functional Requirements (12 will be added):
  • FR1: User authentication with JWT
  • FR2: CRUD operations for resources
  • FR3: Real-time notifications
  • FR4: File upload with virus scanning
  • FR5: Role-based access control
  ... and 7 more

[Show all/expand? (y/n): _ ]

Non-Functional Requirements (8 will be added):
  • NFR1: Response time < 200ms for API
  • NFR2: 99.9% uptime SLA
  • NFR3: GDPR compliance required
  ... and 5 more

[Show all/expand? (y/n): _ ]

Epics (4 will be added):
  • Epic 1: Foundation & Core Infrastructure
  • Epic 2: User Management & Auth
  • Epic 3: Core Business Logic
  • Epic 4: Reporting & Analytics

───────────────────────────────────

Tech Stack (8 components for Architecture):
  • Backend: FastAPI + Python 3.11+
  • Frontend: React 18 + TypeScript
  • Database: PostgreSQL 15
  • Caching: Redis 7
  • Message Queue: RabbitMQ
  ... and 3 more

[Show all/expand? (y/n): _ ]

Coding Standards:
  Python:
    • Formatter: Black, 100 chars
    • Type hints: Required (mypy strict)
    • Docstring: Google style
  TypeScript:
    • Linter: ESLint + Prettier, 80 chars
    • Strict mode: Enabled
  Critical Rules:
    • All API responses use ApiResponse wrapper
    • Database access through repository pattern only
    • No console.log in production code

Security Policies (5 defined):
  • Authentication: JWT with refresh tokens
  • Encryption at rest: AES-256 for sensitive data
  • Encryption in transit: TLS 1.3 required
  • Input validation: Pydantic models mandatory
  • Rate limiting: 100 req/min per user

Test Strategy:
  • Approach: TDD with 90% coverage minimum
  • Unit: pytest + mocking all external deps
  • Integration: Testcontainers for DB/queue
  • E2E: Playwright for critical paths

───────────────────────────────────

Import this preset? (y/n): _
```

**Allow expansion of truncated lists:**

When user types 'y' to "Show all/expand":

```
Functional Requirements (all 12):
  • FR1: User authentication with JWT
  • FR2: CRUD operations for resources
  • FR3: Real-time notifications
  • FR4: File upload with virus scanning
  • FR5: Role-based access control
  • FR6: Audit logging for all operations
  • FR7: Multi-tenant data isolation
  • FR8: RESTful API with OpenAPI docs
  • FR9: Webhook support for integrations
  • FR10: Bulk data import/export
  • FR11: Advanced search and filtering
  • FR12: Email notification system

[Press Enter to return to preview]
```

---

## Step 3: Configure Import Mode

Let user choose how agents use the preset:

```
How should PM and Architect agents use this preset?

1. Auto-fill (use all values, skip questions)
   → Agents will use preset values directly
   → Fastest option, minimal user input needed
   → Best for: Standardized projects, team templates

2. Suggest (show as defaults, allow changes)
   → Agents will suggest preset values
   → User can accept or modify each value
   → Best for: Similar but not identical projects

3. Reference (available for review/copy)
   → Load as reference material only
   → Agents ask questions normally
   → User can manually copy values as needed
   → Best for: Inspiration, partial reuse

Choose (1-3): _
```

**Store choice for use in Step 4:**

- Mode 1 → `import_mode: auto`
- Mode 2 → `import_mode: suggest`
- Mode 3 → `import_mode: reference`

---

## Step 4: Activate Preset

Write preset data to `.ai/document-preset-active.yaml`:

```yaml
preset:
  source_type: global # or 'local', 'custom', 'project'
  source_path: ~/.bmad-document-presets/my-api-standard/
  import_mode: suggest # or 'auto' or 'reference'
  loaded_at: 2025-10-02T10:30:00Z

prd_data:
  technical_assumptions:
    languages:
      - name: Python
        version: '>=3.11'
      - name: TypeScript
        version: '^5.0'
    frameworks:
      - name: FastAPI
        version: '^0.104.0'
      - name: React
        version: '^18.0'
    databases:
      - name: PostgreSQL
        version: '15+'
    repository: Monorepo
    architecture: Microservices
    testing: Full pyramid

  functional_requirements:
    - id: FR1
      text: 'User authentication with JWT'
    - id: FR2
      text: 'CRUD operations for resources'
    # ... all FRs

  non_functional_requirements:
    - id: NFR1
      text: 'Response time < 200ms for API'
    - id: NFR2
      text: '99.9% uptime SLA'
    # ... all NFRs

  epics:
    - number: 1
      title: 'Foundation & Core Infrastructure'
      goal: 'Establish project setup and core services'
    - number: 2
      title: 'User Management & Auth'
    # ... all epics

architecture_data:
  tech_stack:
    - category: Backend
      component: 'FastAPI + Python 3.11+'
    - category: Frontend
      component: 'React 18 + TypeScript'
    - category: Database
      component: 'PostgreSQL 15+'
    # ... all components

  coding_standards:
    python:
      formatter: Black
      line_length: 100
      type_hints: required
      docstring_style: Google
    typescript:
      linter: 'ESLint + Prettier'
      line_length: 80
      strict_mode: true
    critical_rules:
      - 'All API responses use ApiResponse wrapper'
      - 'Database access through repository pattern only'
      - 'No console.log in production code'

  security_policies:
    authentication: 'JWT with refresh tokens'
    encryption_at_rest: 'AES-256 for sensitive data'
    encryption_in_transit: 'TLS 1.3 required'
    input_validation: 'Pydantic models mandatory'
    rate_limiting: '100 req/min per user'

  test_strategy:
    approach: 'TDD with 90% coverage minimum'
    unit_testing: 'pytest + mocking all external deps'
    integration_testing: 'Testcontainers for DB/queue'
    e2e_testing: 'Playwright for critical paths'

processing:
  prd_processed: false
  architecture_processed: false
```

**This file signals to PM and Architect that preset data is available.**

---

## Step 5: Confirmation and Next Steps

Show activation confirmation with immediate actions:

```
✅ Preset 'my-api-standard' activated!

Import Mode: Suggest (preset values as defaults)
Preset Location: ~/.bmad-document-presets/my-api-standard/
Active Until: Both PRD and Architecture are created

What would you like to do next?

1. Create PRD with PM agent
   → PM will use preset for Technical Assumptions
   → FRs, NFRs, and Epics pre-filled for review

2. Create Architecture with Architect agent
   → Architect will use preset for Tech Stack
   → Coding Standards and Security pre-filled

3. Do both in sequence (PM → Architect)
   → Full document creation with preset

4. Exit (preset remains active for later)

Choose (1-4): _
```

**Option Handlers:**

**If option 1 (PM only):**

- Display: "Launching PM agent with preset 'my-api-standard'..."
- Inform user: "PM will detect the active preset and use it during PRD creation"
- Exit task (user continues with PM agent)

**If option 2 (Architect only):**

- Check if `docs/prd.md` exists
- If NOT found:

  ```
  ⚠️ Warning: PRD not found

  Architect requires an existing PRD to create Architecture.

  Options:
    1. Create PRD first (recommended)
    2. Continue anyway (Architect will prompt for PRD)
    3. Cancel

  Choose (1-3): _
  ```

- If found or user confirms: Launch Architect with preset

**If option 3 (Both in sequence):**

- Display: "Starting document creation sequence..."
- Display: "Step 1: Creating PRD with PM agent"
- Inform: "After PM completes, Architect will launch automatically"
- Launch PM agent
- (PM completion triggers Architect automatically)

**If option 4 (Exit):**

```
Preset remains active.

When ready:
  • Run PM agent - it will detect and use the preset
  • Run Architect agent - it will detect and use the preset

The preset will auto-clear after both documents are created.
```

---

## Error Handling

### Invalid Preset Path

```
❌ Cannot access preset

Path: /invalid/path/preset-name/

Reason: Directory does not exist or no read permission

Please:
  1. Verify path is correct
  2. Check permissions
  3. Choose different preset

Try again? (y/n): _
```

### Corrupted Preset Files

```
❌ Preset validation failed

File: ~/.bmad-document-presets/my-preset/preset-config.yaml

Reason: Invalid YAML syntax at line 12

The preset file appears to be corrupted.

Options:
  1. Choose different preset
  2. Try importing from source project again
  3. Cancel

Choose (1-3): _
```

### Active Preset Already Exists

```
⚠️ Active preset already loaded

Current: 'existing-preset' (loaded 2025-10-01)
New: 'my-api-standard'

Replace existing preset with new one?

1. Yes, replace (discard 'existing-preset')
2. No, keep current (cancel import)
3. View current preset details

Choose (1-3): _
```

### Preset Already Used

If `docs/prd.md` and `docs/architecture.md` both exist:

```
ℹ️ Documents already exist

Found:
  ✓ docs/prd.md
  ✓ docs/architecture.md

Presets are typically used before creating these documents.

Options:
  1. Import anyway (for reference)
  2. Export these as new preset instead
  3. Cancel

Choose (1-3): _
```

---

## Implementation Notes

### File Structure

```
.ai/
├── document-preset-active.yaml    # Active preset (created by this task)
├── temp-preset-import/            # Temp storage for project imports
│   ├── preset-config.yaml
│   ├── prd-preset.yaml
│   └── architecture-preset.yaml
└── document-presets/              # Local presets (if any)
    └── {preset-name}/
        ├── preset-config.yaml
        ├── prd-preset.yaml
        └── architecture-preset.yaml
```

### Preset Detection Order

1. User selects option from list
2. If option 1-3: Load from that numbered preset
3. If option 4: Prompt for custom path, validate, load
4. If option 5: Prompt for project path, detect, extract, load
5. Generate preview from loaded data
6. Configure import mode
7. Write `.ai/document-preset-active.yaml`
8. Offer next steps

### Integration with Agents

- PM agent checks for `.ai/document-preset-active.yaml` on activation
- Architect agent checks for `.ai/document-preset-active.yaml` on activation
- Both agents read `import_mode` to determine behavior
- Architect cleans up file after both documents created
