# /export-document-preset Task

When this command is used, execute the following task:

<!-- Powered by BMAD™ Core -->

# Export Document Preset

## Purpose

Extract PRD and Architecture documents from current project, allow customization, and save as reusable preset for future projects.

## When to Use

- After completing PRD and Architecture for a project
- When you want to reuse project patterns in similar projects
- To share project standards with team members
- After refining documents to create team standards

---

## Step 1: Validate Documents Exist

Check for both required documents:

1. Verify `docs/prd.md` exists
2. Verify `docs/architecture.md` exists
3. If either missing:
   - Show error message
   - List which documents are missing
   - Suggest creating them first
   - Exit task

**Implementation:**

```
Checking for required documents...

✓ docs/prd.md - found
✓ docs/architecture.md - found

Both documents found. Ready to proceed.
```

**Error Case:**

```
❌ Required documents not found:
✗ docs/prd.md - NOT FOUND
✓ docs/architecture.md - found

Cannot export preset without both documents.

Please create PRD first:
- Run PM agent to create PRD
- Or create PRD manually

Then try export again.
```

---

## Step 2: Extract and Summarize Documents

Read both documents and extract all sections with full details:

### From PRD:

**Technical Assumptions:**

- List each language with version
- List each framework with version
- List database choices
- Repository structure
- Architecture pattern
- Testing approach

**Functional Requirements:**

- Show each FR with ID and full text
- If > 5 items, show first 5 and "... and X more"

**Non-Functional Requirements:**

- Show each NFR with ID and full text
- If > 5 items, show first 5 and "... and X more"

**Epics:**

- List each epic number and title
- Show goal statement if present

### From Architecture:

**Tech Stack:**

- List each component with category
- Show full stack table if present

**Coding Standards:**

- List language-specific rules
- Show formatter, line length, type requirements
- List all critical rules (not truncated)

**Security Policies:**

- List each policy with details
- Authentication method
- Encryption requirements
- Input validation approach
- Rate limiting rules

**Test Strategy:**

- Testing philosophy/approach
- Coverage requirements
- Unit test framework and approach
- Integration test approach
- E2E test approach

**Display format:**

```
═══ PRD Document Summary ═══

Technical Assumptions:
✓ Languages:
  • Python 3.11+
  • TypeScript 5.0+
✓ Frameworks:
  • FastAPI 0.104+
  • React 18
✓ Database:
  • PostgreSQL 15+
✓ Repository: Monorepo
✓ Architecture: Microservices
✓ Testing: Full pyramid

Functional Requirements (12):
  • FR1: User authentication with JWT
  • FR2: CRUD operations for resources
  • FR3: Real-time notifications
  • FR4: File upload with virus scanning
  • FR5: Role-based access control
  ... and 7 more

Non-Functional Requirements (8):
  • NFR1: Response time < 200ms for API
  • NFR2: 99.9% uptime SLA
  • NFR3: GDPR compliance required
  ... and 5 more

Epics (4):
  • Epic 1: Foundation & Core Infrastructure
    Goal: Establish project setup and core services
  • Epic 2: User Management & Auth
    Goal: Complete user lifecycle management
  • Epic 3: Core Business Logic
    Goal: Implement primary features
  • Epic 4: Reporting & Analytics
    Goal: Build analytics and reporting

═══ Architecture Document Summary ═══

Tech Stack (8 components):
  • Backend: FastAPI + Python 3.11+
  • Frontend: React 18 + TypeScript
  • Database: PostgreSQL 15+
  • Caching: Redis 7
  • Message Queue: RabbitMQ
  ... and 3 more

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
```

---

## Step 3: Interactive Policy Editing

Allow user to customize through natural language:

```
What would you like to customize? (or 'done' to proceed)

Commands:
  - "remove all React items"
  - "keep only Python standards"
  - "remove Epic 4"
  - "add NFR for HIPAA compliance"
  - "change database to MySQL"
  - "show tech stack" (view current state)
  - "show requirements" (view current FRs/NFRs)
  - "reset" (restore original)
  - "done" (save and continue)

Your command: _
```

**Parsing Logic:**

- REMOVE intent: "remove", "delete", "drop", "exclude"
- ADD intent: "add", "include", "create"
- CHANGE intent: "change", "update", "modify", "replace"
- SHOW intent: "show", "list", "display", "view"

**After each edit, show what changed:**

```
✓ Removed: All React-related items

  - Framework: React 18
  - Tech Stack: React 18 + TypeScript
  - Coding Standard: TypeScript ESLint rules

Updated summary available. Continue editing? (y/n): _
```

---

## Step 4: Choose Save Location

Present storage options:

```
Where would you like to save this preset?

1. Global presets (available to all projects)
   Location: ~/.bmad-document-presets/
   Benefits: Persists across all projects, survives project deletion

2. Project local (this project only)
   Location: ./.ai/document-presets/
   Benefits: Project-specific, can commit to git

3. Custom location (you specify full path)
   Location: [you enter path]
   Benefits: Shared network drive, Dropbox, team folder

Choose (1-3): _
```

**For Option 3 (Custom):**

```
Enter full directory path:

> /Users/team/shared-presets

Validating path... ✓
Directory exists and is writable.

Preset will be saved to: /Users/team/shared-presets/{preset-name}/
Continue? (y/n): _
```

**Prompt for preset name:**

```
Enter preset name (lowercase, hyphens only):

> my-api-standard

✓ Valid name

Enter description (one line):

> FastAPI microservices with PostgreSQL and React frontend

✓ Description saved
```

---

## Step 5: Save Preset Files

Create directory and three YAML files:

**Directory structure:**

```
{chosen-location}/{preset-name}/
├── preset-config.yaml
├── prd-preset.yaml
└── architecture-preset.yaml
```

**File: preset-config.yaml**

```yaml
preset:
  id: my-api-standard
  name: 'FastAPI Microservices Standard'
  version: 1.0
  created: 2025-10-02T10:30:00Z
  storage_location: global # or 'local' or 'custom'
  custom_path: null # full path if custom

source_project:
  name: 'ACME API'
  prd_file: docs/prd.md
  architecture_file: docs/architecture.md
  exported_by: export-document-preset
  bmad_version: 4.0
```

**File: prd-preset.yaml**

```yaml
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
  # ... all NFRs

epics:
  - number: 1
    title: 'Foundation & Core Infrastructure'
    goal: 'Establish project setup and core services'
  # ... all epics
```

**File: architecture-preset.yaml**

```yaml
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
```

---

## Step 6: Confirmation and Next Steps

Show success message with details:

```
✅ Document preset 'my-api-standard' saved!

Storage: Global presets
Location: ~/.bmad-document-presets/my-api-standard/

Files created:
  • preset-config.yaml (metadata)
  • prd-preset.yaml (PRD sections)
  • architecture-preset.yaml (Architecture sections)

Size: 12.4 KB total

To use in another project:

1. Open the new project
2. Run: *import-document-preset
3. Select 'my-api-standard' from available presets

Or import from any BMAD-enabled project:

1. Run: *import-document-preset
2. Choose option 5 (Import from BMAD project)
3. Point to project directory

Preset is ready to use! ✅
```

---

## Error Handling

Handle common errors gracefully:

### Missing Documents

```
❌ Required documents not found:
✗ docs/prd.md - NOT FOUND
✓ docs/architecture.md - found

Cannot export preset without both documents.

Please create PRD first:
- Run PM agent to create PRD
- Or create PRD manually

Then try export again.
```

### Invalid Storage Path

```
❌ Cannot write to path: /invalid/path/

Reason: Directory does not exist or no write permission

Please:
1. Choose different location, or
2. Create directory first, or
3. Check permissions

Try again? (y/n): _
```

### Preset Name Conflict

```
⚠️ Preset 'my-api-standard' already exists!

Location: ~/.bmad-document-presets/my-api-standard/
Created: 2025-09-15
Version: 1.0

Options:
1. Overwrite existing preset
2. Create new version (my-api-standard-v2)
3. Choose different name
4. Cancel

Choose (1-4): _
```
