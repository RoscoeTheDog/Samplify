# ADR-XXX: [Short Title of Decision]

**Status**: [Proposed | Accepted | Deprecated | Superseded]
**Date**: YYYY-MM-DD
**Deciders**: [List of people involved in decision]
**Related Stories**: [Story IDs, e.g., 1.1, 1.2A]
**Supersedes**: [ADR-XXX if applicable]

---

## Context

**Problem Statement**:
[What is the issue we're facing? What architectural decision needs to be made?]

**Business Impact**:
[How does this affect the product, users, or business goals?]

**Technical Context**:
[What technical factors influence this decision? Include relevant code, NFRs, CRs, etc.]

**Constraints**:
- [Technical constraints: platform, language, framework versions]
- [Business constraints: time, budget, team skills]
- [Regulatory/Compliance constraints: security, privacy, standards]

**Assumptions**:
- [What are we assuming to be true?]
- [What conditions must hold for this decision to remain valid?]

---

## Decision

**We will**: [Clear statement of the decision - what approach will be taken]

**Rationale**:
[Why this decision was chosen. Include key factors that tipped the scales.]

**Consequences**:

**Positive**:
- ✅ [Benefit 1: e.g., "Improved performance by 50%"]
- ✅ [Benefit 2: e.g., "Reduces maintenance burden"]
- ✅ [Benefit 3: e.g., "Aligns with industry best practices"]

**Negative** (Trade-offs):
- ⚠️ [Trade-off 1: e.g., "Increased complexity in deployment"]
- ⚠️ [Trade-off 2: e.g., "Requires team training"]
- ⚠️ [Trade-off 3: e.g., "Vendor lock-in risk"]

**Risks**:
- 🔴 [Risk 1: e.g., "Breaking change for existing users"]
  - *Mitigation*: [How we'll address this risk]
- 🟡 [Risk 2: e.g., "Performance degradation under load"]
  - *Mitigation*: [How we'll address this risk]

---

## Alternatives Considered

### Alternative 1: [Name/Description]

**Approach**: [Brief description of this alternative]

**Pros**:
- [Advantage 1]
- [Advantage 2]

**Cons**:
- [Disadvantage 1]
- [Disadvantage 2]

**Why Rejected**: [Specific reason this wasn't chosen]

---

### Alternative 2: [Name/Description]

**Approach**: [Brief description of this alternative]

**Pros**:
- [Advantage 1]
- [Advantage 2]

**Cons**:
- [Disadvantage 1]
- [Disadvantage 2]

**Why Rejected**: [Specific reason this wasn't chosen]

---

### Alternative 3: [Name/Description]

**Approach**: [Brief description of this alternative]

**Pros**:
- [Advantage 1]
- [Advantage 2]

**Cons**:
- [Disadvantage 1]
- [Disadvantage 2]

**Why Rejected**: [Specific reason this wasn't chosen]

---

## Implementation

**Required Changes**:
- [ ] [Code change 1: e.g., "Update settings.py INSTALLED_APPS"]
- [ ] [Code change 2: e.g., "Create migration for new field"]
- [ ] [Documentation change: e.g., "Update deployment guide"]
- [ ] [Testing: e.g., "Add integration tests for new behavior"]

**Migration Plan** (if applicable):
1. [Step 1: e.g., "Deploy backward-compatible version"]
2. [Step 2: e.g., "Migrate existing data"]
3. [Step 3: e.g., "Remove deprecated code"]

**Rollback Plan**:
[How to reverse this decision if needed. What's the exit strategy?]

**Timeline**:
- **Decision Date**: YYYY-MM-DD
- **Implementation Start**: YYYY-MM-DD
- **Completion Target**: YYYY-MM-DD
- **Review Date**: YYYY-MM-DD (when to revisit this decision)

---

## Validation

**How We'll Know This Works**:
- [Metric 1: e.g., "Response time < 200ms"]
- [Metric 2: e.g., "Zero security vulnerabilities in audit"]
- [Metric 3: e.g., "Developer productivity improves by X%"]

**Success Criteria**:
- [ ] [Criterion 1: Measurable outcome]
- [ ] [Criterion 2: Measurable outcome]
- [ ] [Criterion 3: Measurable outcome]

**Review Triggers** (when to reconsider this decision):
- [Trigger 1: e.g., "If performance degrades by >20%"]
- [Trigger 2: e.g., "If new framework version is released"]
- [Trigger 3: e.g., "After 6 months in production"]

---

## References

**Related Documents**:
- [Link to PRD, NFR, CR, or other requirements]
- [Link to technical specs or design docs]
- [Link to related stories]

**External Resources**:
- [Link to relevant articles, papers, documentation]
- [Link to framework/library docs]

**Discussion**:
- [Link to GitHub issue/PR where this was discussed]
- [Link to Slack/email thread]
- [Meeting notes from architecture review]

---

## Notes

**Follow-up Actions**:
- [ ] [Action 1: e.g., "Update architecture diagram"]
- [ ] [Action 2: e.g., "Notify team in stand-up"]
- [ ] [Action 3: e.g., "Schedule training session"]

**Open Questions**:
- [Question 1: Unresolved issue to track]
- [Question 2: Future consideration]

**Lessons Learned** (to be filled after implementation):
- [What worked well?]
- [What would we do differently?]
- [What surprised us?]

---

**Changelog**:
| Date | Version | Change | Author |
|------|---------|--------|--------|
| YYYY-MM-DD | 1.0 | Initial decision documented | [Name] |
| YYYY-MM-DD | 1.1 | Updated after implementation | [Name] |
