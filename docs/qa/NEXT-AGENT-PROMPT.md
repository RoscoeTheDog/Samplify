# Next QA Agent Activation Prompt

**Session:** 4
**Priority:** TIER 2 Completion (Error Categorization)
**Estimated Duration:** 3-9 hours

---

## 🎯 Agent Activation Prompt

```
You are Quinn, the Test Architect & Quality Advisor for the Samplify project.

CONTEXT:
- Session 3 just completed with major achievements:
  ✅ TIER 1 COMPLETE (100%) - Both critical stories at PASS (90/100)
  ✅ GUIDE 2 complete: Performance benchmark validated (18,844 files/sec)
  ✅ GUIDE 3 complete: Network retry logic implemented
  🟡 TIER 2 at 50% - 1 of 2 guides complete

CURRENT STATUS:
- Story 1.3: PASS (90/100) ✅
- Story 1.4: PASS (90/100) ✅
- Story 1.5: PASS (90/100) ✅
- Overall sprint progress: 30% (3/10 guides complete)

YOUR MISSION:
Complete TIER 2 by implementing GUIDE 8: Enhanced Error Categorization for Story 1.5.

IMMEDIATE TASK:
Read the complete handoff document at docs/qa/HANDOFF-SESSION-4.md for full context,
then begin GUIDE 8 implementation following the detailed checklist provided.

GUIDE 8 OVERVIEW:
- Priority: HIGH (TIER 2)
- Effort: 3-5 hours
- Goal: Add error classification and retry logic for FFmpeg failures
- Impact: Story 1.5: 90/100 → 95/100 (optional quality enhancement)

IMPLEMENTATION STEPS (from handoff):
1. Create FFmpegErrorType enum (6 error categories)
2. Implement parse_ffmpeg_error() function
3. Add retry logic for transient errors (network failures)
4. Enhance logging with error categorization
5. Add 5 comprehensive tests

TESTING REQUIREMENTS:
- All existing tests must pass (33 FFmpeg + 23 scanning = 56 total)
- Add 5 new error categorization tests
- Verify retry logic with exponential backoff
- Test error skipping for permanent failures
- Test abort behavior for critical errors

SUCCESS CRITERIA:
✅ FFmpegErrorType enum implemented
✅ Error parser with pattern matching complete
✅ Retry logic for network errors working
✅ Enhanced logging with structured data
✅ All 5 new tests passing
✅ Story 1.5 ready for 95/100 (optional)
✅ TIER 2 complete (100%)

FILES TO MODIFY:
- samplify/management/commands/scan_input.py (error classification + retry)
- samplify/utils/ffmpeg.py (may need to return error details)
- tests/test_file_scanning.py (add error categorization tests)

IMPORTANT NOTES:
- Follow test-driven development: write tests first
- Use existing retry pattern from GUIDE 3 as reference
- Maintain brownfield CR1 algorithm preservation
- Update quality gate after completion
- Document all changes in REMEDIATION-TRACKING.md

After completing GUIDE 8, you may optionally continue to TIER 3 quick wins:
- GUIDE 5: Error Message Enhancement (1-2 hours)
- GUIDE 9: Transaction Isolation (1-2 hours)
- GUIDE 4: Loguru Enhancement (2-3 hours)

ACTIVATION COMMAND:
Start by running: /BMad:agents:qa

Then immediately state: "I've read the handoff document. Beginning GUIDE 8
implementation for error categorization. First, I'll create the FFmpegErrorType
enum and error parser function."
```

---

## 📋 Quick Reference Checklist

### Pre-Implementation
- [ ] Read `docs/qa/HANDOFF-SESSION-4.md` completely
- [ ] Review current test status: `pytest tests/ -v` (should show 56 passing)
- [ ] Review GUIDE 8 details in `docs/qa/REMEDIATION-TRACKING.md` lines 211-256
- [ ] Understand current error handling in `samplify/management/commands/scan_input.py`

### Implementation Phase
- [ ] **Step 1:** Create `FFmpegErrorType` enum (30 min)
- [ ] **Step 2:** Implement `parse_ffmpeg_error()` function (1 hour)
- [ ] **Step 3:** Add retry logic for transient errors (1-2 hours)
- [ ] **Step 4:** Enhance logging with categorization (30 min)
- [ ] **Step 5:** Add 5 comprehensive tests (1-2 hours)

### Testing Phase
- [ ] Run `pytest tests/test_file_scanning.py -v` (should show 28 passing)
- [ ] Run `pytest tests/test_ffmpeg_utils.py -v` (should show 33 passing)
- [ ] Verify error categorization working correctly
- [ ] Test retry behavior with mocked network failures
- [ ] Validate logging output structure

### Documentation Phase
- [ ] Update `docs/qa/REMEDIATION-TRACKING.md` GUIDE 8 to COMPLETE
- [ ] Update `docs/qa/gates/1.5-file-scanning-service.yml` (optional: 90→95/100)
- [ ] Update `docs/stories/story-15-file-scanning-service.md` QA Results
- [ ] Document any challenges or lessons learned

### Completion Validation
- [ ] All tests passing (61 total: 33 FFmpeg + 28 scanning)
- [ ] TIER 2 marked as COMPLETE (100%)
- [ ] Quality gates updated with new scores
- [ ] Sprint progress updated to 40%

---

## 🔧 Useful Commands

### Test Execution
```bash
# Run all tests
pytest tests/ -v

# Run only scanning tests
pytest tests/test_file_scanning.py -v

# Run only FFmpeg tests
pytest tests/test_ffmpeg_utils.py -v

# Run with coverage
pytest tests/test_file_scanning.py --cov=samplify.management.commands.scan_input --cov-report=html

# Run specific test
pytest tests/test_file_scanning.py::TestErrorCategorization::test_network_error_retry -v
```

### Code Review
```bash
# Check current implementation
cat samplify/management/commands/scan_input.py | grep -A 10 "extract_metadata"

# Review error handling
grep -n "except" samplify/management/commands/scan_input.py

# Check test coverage
pytest --cov-report=term-missing tests/test_file_scanning.py
```

### Git Status
```bash
# View current changes
git status
git diff

# View recent commits
git log --oneline -10

# Check branch
git branch --show-current
```

---

## 📊 Expected Outcomes

### After GUIDE 8 Completion

**Test Results:**
- Total tests: 61 (33 FFmpeg + 28 scanning)
- New tests: 5 error categorization tests
- Pass rate: 100%

**Quality Gate Updates:**
- Story 1.5: 90/100 → 95/100 (optional enhancement)
- TIER 2: 50% → 100% COMPLETE ✅

**Sprint Progress:**
- Overall: 30% → 40%
- TIER 1: 100% ✅
- TIER 2: 100% ✅
- TIER 3: 0% ⏳
- TIER 4: 0% ⏳

**Production Readiness:**
- All critical issues resolved
- Enhanced error resilience
- Better operational visibility
- Production-ready with optional enhancements

---

## 🎯 Session 4 Goals

### Primary Goal (MUST DO)
✅ Complete GUIDE 8 - Error Categorization
✅ Achieve TIER 2 100% completion

### Secondary Goals (SHOULD DO)
✅ Start TIER 3 work (GUIDE 5 or GUIDE 9)
✅ Reach 50% overall sprint progress

### Stretch Goals (NICE TO HAVE)
✅ Complete 2-3 TIER 3 guides
✅ Reach 60% overall sprint progress
✅ Elevate Story 1.5 to 95/100

---

## 💡 Tips for Success

### Development Approach
1. **Read handoff document FIRST** - Contains critical context
2. **Follow TDD** - Write failing tests, then make them pass
3. **Use existing patterns** - Reference GUIDE 3 retry logic
4. **Incremental validation** - Test each component before moving on
5. **Update docs immediately** - Don't defer documentation

### Common Pitfalls to Avoid
- ❌ Skipping test coverage for edge cases
- ❌ Forgetting to update quality gates
- ❌ Not testing retry exhaustion scenarios
- ❌ Incomplete error pattern matching
- ❌ Missing structured logging fields

### Best Practices
- ✅ Use descriptive error messages
- ✅ Log with structured data (extra fields)
- ✅ Test both success and failure paths
- ✅ Document design decisions in code comments
- ✅ Keep changes focused and incremental

---

## 📞 Support Resources

### Documentation
- **Primary:** `docs/qa/HANDOFF-SESSION-4.md`
- **Guide Details:** `docs/qa/REMEDIATION-TRACKING.md` (GUIDE 8)
- **Sprint Plan:** `docs/qa/SPRINT-PLAN-REMEDIATION.md`

### Code References
- **Current Implementation:** `samplify/management/commands/scan_input.py`
- **Retry Pattern:** `samplify/utils/ffmpeg.py` (GUIDE 3 implementation)
- **Existing Tests:** `tests/test_file_scanning.py`

### Quality Gates
- **Story 1.5:** `docs/qa/gates/1.5-file-scanning-service.yml`
- **Story 1.4:** `docs/qa/gates/1.4-ffmpeg-detection-download-service.yml`
- **Story 1.3:** `docs/qa/gates/1.3-loguru-configuration.yml`

---

## 🚀 Activation Sequence

1. **Run:** `/BMad:agents:qa`
2. **State:** "I've read the handoff document at docs/qa/HANDOFF-SESSION-4.md"
3. **Confirm:** Review current test status (56 tests should pass)
4. **Begin:** Start GUIDE 8 Step 1 - Create FFmpegErrorType enum

---

**Session 4 Mission:** Complete TIER 2 (100%) by implementing GUIDE 8

**Expected Duration:** 3-5 hours (core) + 2-4 hours (optional TIER 3)

**Let's achieve excellence!** 🎯

---

*Prepared by: Quinn (Test Architect)*
*Session: 3 → 4*
*Date: 2025-10-06 23:30*
