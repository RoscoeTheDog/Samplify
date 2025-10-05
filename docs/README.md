# Samplify Documentation

**Project**: Samplify - Django Web UI Modernization
**Version**: 1.2
**Last Updated**: 2025-10-04

---

## 📋 Documentation Structure

This documentation uses a **sharded structure** for maintainability and parallel development. All primary documents are split into focused sections organized by directory.

### **Active Documentation** (Use These)

#### 📘 Product Requirements (PRD)
**Location**: `/docs/prd/`
**Entry Point**: [`prd/index.md`](prd/index.md)

Comprehensive product requirements document split into:
- Project analysis and context
- Functional and non-functional requirements
- User interface enhancement goals
- Technical constraints and integration
- Epic and story structure
- Next steps

#### 🏗️ Architecture Documentation
**Location**: `/docs/architecture/`
**Entry Point**: [`architecture/index.md`](architecture/index.md)

Complete brownfield architecture analysis and Django migration design:
- High-level architecture
- Tech stack specifications
- Database schema design
- API endpoints
- Frontend components
- FFmpeg integration
- Testing strategy
- Coding standards (CS1-CS13)

#### 📝 User Stories
**Location**: `/docs/stories/`
**Entry Point**: [`stories/index.md`](stories/index.md)

Individual story files for Epic 1 (Django Web UI Modernization):
- Story 1.0: Repository & Environment Foundation
- Story 1.1: Django Project Setup & Configuration
- Story 1.2: Database Models (A/B/C sub-tasks)
- Story 1.3-1.9: Backend services and infrastructure
- Story 1.10-1.15: Frontend UI components
- Story 1.16: Complete Setup Script
- Story 1.17: Integration Testing & Validation

---

## 📚 Supporting Documentation

### Developer Handoff Essentials

| Document | Purpose | Size |
|----------|---------|------|
| [`brief.md`](brief.md) | Project overview, problem statement, target users | 32KB |

**Note**: Setup instructions, git workflow, and implementation checklists are embedded in the PRD and story specifications:
- **Setup**: See Story 1.0 acceptance criteria
- **Git Workflow**: See PRD Development Workflow Requirements (DW1-DW5)
- **Implementation Checklist**: Each story has Definition of Done

### Dependencies & Configuration

| File | Purpose |
|------|---------|
| `requirements.txt` | Production Python dependencies |
| `requirements-dev.txt` | Development tools and testing dependencies |
| `.gitignore` | Git exclusion patterns |

---

## 🗂️ Archive

**Location**: `/docs/archive/`

Contains superseded monolithic documentation files:
- `prd.md` → Replaced by `/docs/prd/` (sharded)
- `architecture.md` → Replaced by `/docs/architecture/` (sharded)
- `stories.md` → Replaced by `/docs/stories/` (sharded)

**⚠️ DO NOT USE ARCHIVED FILES** - They are kept for historical reference only. See [`archive/README.md`](archive/README.md) for details.

---

## 🚀 Quick Start for Developers

### 1. Read Core Documents (in order)
1. [`brief.md`](brief.md) - Understand the project
2. [`prd/index.md`](prd/index.md) - Read full requirements (includes DW1-DW5 git workflow)
3. [`architecture/index.md`](architecture/index.md) - Understand technical design
4. [`architecture/coding-standards.md`](architecture/coding-standards.md) - Review CS1-CS13 standards
5. [`stories/index.md`](stories/index.md) - Review story details

### 2. Start with Story 1.0
Story 1.0 contains **complete setup instructions** in its acceptance criteria:
- Virtual environment creation
- requirements.txt installation
- Pre-commit hooks setup
- Git workflow configuration

Begin here: [`stories/story-10-repository-environment-foundation.md`](stories/story-10-repository-environment-foundation.md)

---

## 📊 Documentation Statistics

- **Total Files**: 63 markdown files
- **PRD**: 9 files, 801 lines
- **Architecture**: 21 files, 8,455 lines
- **Stories**: 19+ individual story files
- **Supporting Docs**: 6 essential files

---

## 🔍 Finding Information

### By Topic

| Topic | Location |
|-------|----------|
| **Requirements** | `/docs/prd/requirements.md` |
| **Database Schema** | `/docs/architecture/database-schema-design.md` |
| **API Endpoints** | `/docs/architecture/api-endpoints.md` |
| **Frontend UI** | `/docs/architecture/frontend-components.md` |
| **Coding Standards** | `/docs/architecture/coding-standards.md` |
| **Testing Strategy** | `/docs/architecture/testing-strategy.md` |
| **Tech Stack** | `/docs/architecture/tech-stack.md` |
| **FFmpeg Integration** | `/docs/architecture/ffmpeg-sources.md` |
| **Git Workflow** | `/docs/prd/requirements.md` (DW1-DW5) |

### By Development Phase

| Phase | Documents |
|-------|-----------|
| **Planning** | `brief.md`, `prd/` directory |
| **Architecture** | `architecture/` directory |
| **Story Implementation** | `stories/` directory (each story has setup instructions) |
| **Testing** | `architecture/testing-strategy.md` |

---

## 🎯 Documentation Best Practices

### For Developers
- Always reference **sharded versions** (not archive)
- Use index.md files for navigation
- Follow coding standards (CS1-CS13) in `architecture/coding-standards.md`
- Update story status in `stories/index.md` as work progresses

### For PMs/Architects
- Keep sharded files under 1,000 lines
- Update version numbers and dates consistently
- Cross-reference between documents using relative paths
- Document all architectural decisions in relevant architecture/ files

---

## 📝 Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-10-04 | 1.2 | Documentation cleanup - archived monolithic files | PM Agent (John) |
| 2025-10-04 | 1.1 | Critical gaps resolved (tech stack, FFmpeg, testing) | BA Agent (Mary) |
| 2025-10-03 | 1.0 | Documentation sharding completed | PM Agent (John) |
| 2025-10-03 | 0.9 | Initial PRD and architecture documents created | PM Agent (John) |

---

## 🆘 Need Help?

- **Can't find something?** Check the relevant index.md file (`prd/`, `architecture/`, `stories/`)
- **Documentation unclear?** File an issue or contact PM Agent
- **Missing information?** Check `documentation-assessment.md` for known gaps

---

**Status**: ✅ **READY FOR DEVELOPER HANDOFF**

All critical documentation is complete, structured, and validated. Begin development with Story 1.0.
