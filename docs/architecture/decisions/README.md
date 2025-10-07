# Architecture Decision Records (ADRs)

**Purpose**: This directory contains Architecture Decision Records documenting significant architectural decisions made during the Samplify project.

---

## What is an ADR?

An **Architecture Decision Record (ADR)** is a document that captures an important architectural decision made along with its context and consequences.

**When to Create an ADR**:
- Choosing between architectural patterns (e.g., monolith vs microservices)
- Selecting frameworks, libraries, or technologies
- Defining data models or database schemas
- Making security or performance trade-offs
- Resolving NFR (Non-Functional Requirement) interpretations
- Any decision that has long-term impact on the codebase

**When NOT to Create an ADR**:
- Routine code changes or bug fixes
- Obvious best practices (e.g., "use version control")
- Decisions easily reversed without cost
- Implementation details that don't affect architecture

---

## ADR Process

### 1. Proposal Phase
- Copy `ADR-TEMPLATE.md` to new file `ADR-XXX-[short-title].md`
- Set **Status**: `Proposed`
- Fill out Context, Decision, Alternatives sections
- Share with team for review

### 2. Review Phase
- Discuss in architecture review meeting or async (Slack/GitHub)
- Update ADR based on feedback
- Address open questions

### 3. Acceptance Phase
- Product Owner or Tech Lead approves
- Set **Status**: `Accepted`
- Implement decision

### 4. Implementation Phase
- Make required code changes
- Update documentation
- Fill out "Lessons Learned" section

### 5. Maintenance Phase
- Review periodically (see "Review Date" in ADR)
- If conditions change, either:
  - **Deprecate**: Set **Status**: `Deprecated`, create new ADR
  - **Supersede**: Create new ADR, reference old one

---

## ADR Index

### Active ADRs

| ID | Title | Status | Date | Deciders | Related Stories |
|----|-------|--------|------|----------|-----------------|
| [0001](0001-admin-framework-enabled.md) | Django Admin Framework Enabled | Accepted (Retroactive) | 2025-10-06 | Quinn (QA), Dev Team | 1.1, 1.2A, 1.2B |
| [0002](0002-single-table-inheritance-for-media-files.md) | Single-Table Inheritance for Media Files | Accepted (Retroactive) | 2025-10-05 | Dev Team | 1.2A, 1.2B |
| [0003](0003-busy-wait-pattern-accepted-for-cr2-compatibility.md) | Busy-Wait Pattern (CR2 Compatibility) | Accepted (Tech Debt) | 2025-10-05 | Dev Team | 1.6 |
| [0004](0004-sqlite-wal-mode-for-concurrent-access.md) | SQLite WAL Mode for Concurrency | Accepted (Retroactive) | 2025-10-05 | Dev Team | 1.2C |

### Deprecated ADRs

*None yet*

---

## ADR Statuses

- **Proposed**: Under discussion, not yet implemented
- **Accepted**: Approved and being/been implemented
- **Deprecated**: No longer valid, replaced by newer decision
- **Superseded**: Replaced by specific newer ADR (link provided)

---

## Quick Reference

### Creating a New ADR

```bash
# Copy template
cp ADR-TEMPLATE.md ADR-XXX-[short-title].md

# Edit new file
# Fill out Context, Decision, Alternatives
# Set Status: Proposed

# Share for review
git add ADR-XXX-[short-title].md
git commit -m "docs: Propose ADR-XXX [short-title]"
git push
```

### Approving an ADR

```bash
# Update Status in ADR file
Status: Accepted

# Update this README index

# Commit
git commit -m "docs: Accept ADR-XXX [short-title]"
git push
```

### Deprecating an ADR

```bash
# Update old ADR
Status: Deprecated
Supersedes: ADR-YYY [new ADR]

# Create new ADR
# Reference old ADR in "Supersedes" field

# Update README index
# Move old ADR from Active to Deprecated

# Commit
git commit -m "docs: Deprecate ADR-XXX, superseded by ADR-YYY"
git push
```

---

## Best Practices

### Writing Good ADRs

1. **Be Concise**: Aim for 2-3 pages. If longer, split into multiple ADRs.
2. **Use Clear Language**: Avoid jargon; explain acronyms on first use.
3. **Document Alternatives**: Show you considered other options (builds confidence).
4. **Be Honest About Trade-offs**: Every decision has pros/cons.
5. **Link to Context**: Reference stories, PRD, NFRs, external resources.
6. **Keep It Updated**: Fill out "Lessons Learned" after implementation.

### Common Pitfalls

- ❌ **Too Late**: Don't write ADR after decision implemented (document during decision-making)
- ❌ **Too Vague**: "We'll use a database" → ❌ | "We'll use PostgreSQL 15+ for ACID compliance" → ✅
- ❌ **No Alternatives**: Shows lack of due diligence; always document at least 2 alternatives
- ❌ **Ignoring Consequences**: Every decision has trade-offs; document them honestly
- ❌ **Never Reviewing**: Set review dates; revisit when assumptions change

---

## ADR Template Sections

A complete ADR includes:

1. **Context**: Why is this decision needed? What's the problem?
2. **Decision**: What are we doing? (Clear, actionable statement)
3. **Consequences**: Positive outcomes, negative trade-offs, risks
4. **Alternatives Considered**: Other options evaluated (and why rejected)
5. **Implementation**: Required changes, migration plan, rollback strategy
6. **Validation**: How we'll measure success
7. **References**: Links to related docs, discussions, external resources

---

## Related Documentation

- **PRD**: `docs/prd/` - Product Requirements (includes NFRs, CRs)
- **Stories**: `docs/stories/` - User stories referencing ADRs
- **QA Reports**: `docs/qa/` - Quality assessments that may trigger ADRs
- **Remediation Backlog**: `docs/qa/REMEDIATION-BACKLOG.md` - Technical debt requiring ADRs

---

## Questions?

**Who approves ADRs?**
- Product Owner (business/product decisions)
- Tech Lead or Architect (technical decisions)
- Scrum Master (process decisions)

**How long should an ADR take to write?**
- Simple decisions: 30 minutes - 1 hour
- Complex decisions: 2-4 hours (including research)

**Can I update an ADR after acceptance?**
- Yes! Use the Changelog section to track updates.
- Major changes may warrant a new ADR (set old one to "Superseded")

**What if I disagree with an ADR?**
- Raise concerns during Proposal phase
- Document your alternative in the ADR (include in "Alternatives Considered")
- If ADR is Accepted and you still disagree, follow team escalation process

---

## Retroactive ADRs Note

**ADRs 0001-0004 were created retroactively** on 2025-10-06 during architectural review of Stories 1.1-1.8. These document critical decisions made during implementation but not formally captured at the time.

**Lesson Learned:** Future stories will create ADRs **during** the decision-making process, not after implementation. This ensures architectural context is captured when decisions are fresh and trade-offs are being actively evaluated.

---

**Last Updated**: 2025-10-06
**Maintainer**: Winston (Architect)
