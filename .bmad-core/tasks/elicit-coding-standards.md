# Coding Standards Elicitation Wizard

## Purpose

Gather detailed coding standard preferences through interactive elicitation to refine and expand the project's coding conventions beyond the baseline CS1-CS13 requirements.

## Instructions

This wizard will guide you through multiple categories of coding preferences. Answer each question thoughtfully - your responses will be used to update the coding standards document with specific, actionable requirements.

---

## Section 1: Naming Conventions Deep Dive

### 1.1 Variable Naming Preferences

**Question**: How do you prefer to name variables for different contexts?

**a) Boolean variables - which prefix style do you prefer?**
- [ ] `is_` prefix (e.g., `is_active`, `is_processing`, `is_valid`)
- [ ] `has_` prefix (e.g., `has_errors`, `has_permission`, `has_data`)
- [ ] `can_` prefix (e.g., `can_process`, `can_delete`, `can_modify`)
- [ ] Mixed approach (explain when to use each): _________________

**b) Counter/Index variables - what naming do you prefer?**
- [ ] Single letter acceptable in loops (e.g., `i`, `j`, `k`)
- [ ] Descriptive always (e.g., `file_index`, `worker_count`, `iteration_number`)
- [ ] Context-dependent (when is single letter OK?): _________________

**c) Collection variables - how should they be named?**
- [ ] Plural nouns (e.g., `files`, `transformations`, `results`)
- [ ] Suffix with type (e.g., `file_list`, `transformation_queue`, `result_dict`)
- [ ] Both (explain when): _________________

**d) Temporary variables - what's acceptable?**
- [ ] Avoid completely - always use descriptive names
- [ ] Allow `temp_` prefix (e.g., `temp_result`, `temp_path`)
- [ ] Allow short names in small scopes (e.g., `result`, `data`)
- [ ] Other preference: _________________

**e) Constants - how should they be formatted?**
- [ ] SCREAMING_SNAKE_CASE for all constants (e.g., `MAX_WORKERS = 8`)
- [ ] SCREAMING_SNAKE_CASE only for "magic numbers" (hardcoded values)
- [ ] Context-dependent (explain): _________________

---

### 1.2 Function Naming Preferences

**Question**: How do you prefer to name functions for clarity?

**a) Action functions - verb preference?**
- [ ] Strong verbs (e.g., `execute_`, `process_`, `transform_`)
- [ ] Get/Set pattern (e.g., `get_files()`, `set_status()`)
- [ ] Verb-Noun pattern (e.g., `validate_input()`, `parse_template()`)
- [ ] Mixed (when to use which?): _________________

**b) Query/Lookup functions - what pattern?**
- [ ] `get_` prefix (e.g., `get_file_by_id()`, `get_active_schema()`)
- [ ] `find_` prefix (e.g., `find_file_by_id()`, `find_active_schema()`)
- [ ] `fetch_` prefix (e.g., `fetch_file_by_id()`, `fetch_active_schema()`)
- [ ] `retrieve_` prefix (e.g., `retrieve_file_by_id()`)
- [ ] Context-dependent (explain): _________________

**c) Boolean-returning functions - what pattern?**
- [ ] `is_` prefix (e.g., `is_valid()`, `is_processable()`)
- [ ] `check_` prefix (e.g., `check_valid()`, `check_processable()`)
- [ ] `has_` prefix (e.g., `has_errors()`, `has_permission()`)
- [ ] `can_` prefix (e.g., `can_process()`, `can_delete()`)
- [ ] Mixed (when to use which?): _________________

**d) Private/Internal functions - naming convention?**
- [ ] Single underscore prefix (e.g., `_internal_helper()`)
- [ ] Descriptive with "internal" in name (e.g., `internal_calculate_hash()`)
- [ ] No special marking, rely on docstring
- [ ] Other: _________________

**e) Helper/Utility functions - how to distinguish?**
- [ ] `_helper_` prefix (e.g., `_helper_parse_xml()`)
- [ ] `util_` prefix (e.g., `util_parse_xml()`)
- [ ] Descriptive name in `utils/` module (e.g., `utils.parse_xml()`)
- [ ] No special naming, just good names
- [ ] Other: _________________

---

### 1.3 Class and Module Naming

**Question**: Class and module naming preferences?

**a) Class names - what style for different types?**
- [ ] PascalCase for all (e.g., `FileProcessor`, `SchemaManager`)
- [ ] Suffix with type for clarity (e.g., `FileProcessorService`, `SchemaManagerHandler`)
- [ ] Descriptive without suffix (e.g., `MediaProcessor`, `ConfigurationManager`)
- [ ] Other: _________________

**b) Module names - what conventions?**
- [ ] snake_case, singular (e.g., `file_processor.py`, `schema_manager.py`)
- [ ] snake_case, plural when containing multiple (e.g., `utils.py`, `handlers.py`)
- [ ] Match primary class name (e.g., `FileProcessor.py`)
- [ ] Other: _________________

**c) Django app names - what pattern?**
- [ ] Plural nouns (e.g., `apps/schemas/`, `apps/files/`)
- [ ] Singular nouns (e.g., `apps/schema/`, `apps/file/`)
- [ ] Descriptive purpose (e.g., `apps/processing/`, `apps/catalog/`)
- [ ] Other: _________________

---

## Section 2: Code Organization and Structure

### 2.1 File Organization

**Question**: How should code be organized within files?

**a) Import section organization - preferred order within groups?**
- [ ] Alphabetical strictly
- [ ] Alphabetical, but group related imports (e.g., all `django.db` imports together)
- [ ] By usage frequency (most used first)
- [ ] Other: _________________

**b) Constant definitions - where should they go?**
- [ ] Top of file after imports
- [ ] Separate `constants.py` module
- [ ] Near the functions that use them
- [ ] `settings.py` for Django settings, file-level for others
- [ ] Other: _________________

**c) Class organization - preferred order of members?**
Order these from 1 (first) to 7 (last):
- [ ] Class variables/constants: _____
- [ ] `__init__` constructor: _____
- [ ] Class methods (`@classmethod`): _____
- [ ] Static methods (`@staticmethod`): _____
- [ ] Public methods: _____
- [ ] Private methods (underscore prefix): _____
- [ ] Properties (`@property`): _____

**d) Function organization within modules - how to group?**
- [ ] By functionality (all database functions together, all processing functions together)
- [ ] By call order (caller before callee)
- [ ] Alphabetically
- [ ] Public functions first, private functions last
- [ ] Other: _________________

**e) Maximum file length - when to split?**
- [ ] No limit, organize by logical purpose
- [ ] 500 lines maximum
- [ ] 1000 lines maximum
- [ ] When file has more than X classes/functions: _____
- [ ] Other: _________________

---

### 2.2 Code Block Organization

**Question**: How should code blocks be structured?

**a) Blank lines between logical sections - how many?**
- [ ] 1 blank line between all logical blocks
- [ ] 2 blank lines between major sections, 1 between minor blocks
- [ ] Varies by context (explain): _________________

**b) Related statements grouping - preferences?**
- [ ] Group all variable declarations together at top of function
- [ ] Declare variables near first use
- [ ] Mix (explain when to use each): _________________

**c) Error handling placement - where in function?**
- [ ] Input validation at top, then logic
- [ ] Try-except wrapping entire function body
- [ ] Error handling inline where needed
- [ ] Mix (explain pattern): _________________

**d) Return statements - how many per function?**
- [ ] Single return at end only (use intermediate variables)
- [ ] Multiple returns OK for early exit conditions
- [ ] Guard clauses at top with early returns, then single return
- [ ] No preference, depends on clarity
- [ ] Other: _________________

---

## Section 3: Comments and Documentation Deep Dive

### 3.1 Comment Density and Style

**Question**: Comment preferences beyond basic requirements?

**a) TODO comments - what format?**
- [ ] `# TODO: Description` (simple)
- [ ] `# TODO(author): Description with owner`
- [ ] `# TODO: Description [YYYY-MM-DD]` with date
- [ ] `# TODO(author, YYYY-MM-DD): Description with owner and date`
- [ ] Other: _________________

**b) FIXME/HACK comments - how to mark technical debt?**
- [ ] `# FIXME: Description` for bugs
- [ ] `# HACK: Description` for workarounds
- [ ] `# XXX: Description` for warnings
- [ ] Custom tags (specify): _________________
- [ ] Prefer issue tracker, minimal inline comments

**c) Algorithm complexity comments - when and how?**
- [ ] Always include Big-O notation (e.g., `# O(n log n) complexity`)
- [ ] Only for complex algorithms (O(n²) or worse)
- [ ] In docstring only, not inline
- [ ] Not needed if code is clear
- [ ] Other: _________________

**d) Magic number explanations - how verbose?**
- [ ] Always use named constant, comment explains origin
- [ ] Inline comment with number (e.g., `timeout = 30  # 30 seconds based on avg response time`)
- [ ] Named constant only, no additional comment
- [ ] Other: _________________

**e) Commented-out code - acceptable or not?**
- [ ] Never commit commented code (use git history)
- [ ] OK temporarily with `# TEMP:` marker
- [ ] OK with explanation why it's kept
- [ ] Other: _________________

---

### 3.2 Docstring Enhancements

**Question**: Additional docstring requirements?

**a) Type hints in docstrings - necessary?**
- [ ] Yes, always duplicate type hints in Args section for clarity
- [ ] No, type hints in signature are sufficient
- [ ] Only for complex types that need explanation
- [ ] Other: _________________

**b) Default values in docstrings - how to handle?**
- [ ] Include in Args section (e.g., `param: Description (default: 10)`)
- [ ] Omit, covered by function signature
- [ ] Include only when default behavior is complex
- [ ] Other: _________________

**c) Side effects documentation - required?**
- [ ] Always document in separate "Side Effects:" section
- [ ] Document in main description
- [ ] Document in "Note:" section
- [ ] Only if side effects are non-obvious
- [ ] Other: _________________

**d) Performance characteristics - when to document?**
- [ ] Always include Big-O complexity
- [ ] Only for performance-critical functions
- [ ] In "Note:" section when relevant
- [ ] Not needed
- [ ] Other: _________________

**e) Related functions/classes - cross-reference?**
- [ ] Yes, in "See Also:" section with links
- [ ] In description only when directly related
- [ ] No, rely on IDE "find references"
- [ ] Other: _________________

---

## Section 4: Control Flow and Logic Patterns

### 4.1 Conditional Logic Preferences

**Question**: How should conditionals be written?

**a) Complex boolean expressions - how to structure?**
```python
# Option 1: Inline with parentheses
if (user.is_active and user.has_permission('edit') and not user.is_locked):
    pass

# Option 2: Multi-line with backslash
if user.is_active and \
   user.has_permission('edit') and \
   not user.is_locked:
    pass

# Option 3: Intermediate boolean variables
is_active_user = user.is_active
has_edit_permission = user.has_permission('edit')
is_not_locked = not user.is_locked
if is_active_user and has_edit_permission and is_not_locked:
    pass

# Option 4: Multi-line with parentheses
if (
    user.is_active
    and user.has_permission('edit')
    and not user.is_locked
):
    pass
```
- [ ] Option 1
- [ ] Option 2
- [ ] Option 3
- [ ] Option 4
- [ ] Context-dependent (when to use which?): _________________

**b) Guard clauses vs nested ifs - preference?**
```python
# Guard clause style (early returns)
def process_file(file_path):
    if not file_path.exists():
        return None
    if not is_valid_format(file_path):
        return None
    # Main logic here
    return result

# Nested if style
def process_file(file_path):
    if file_path.exists():
        if is_valid_format(file_path):
            # Main logic here
            return result
    return None
```
- [ ] Guard clauses (early returns)
- [ ] Nested ifs
- [ ] Mix (when to use which?): _________________

**c) Ternary operators - when acceptable?**
- [ ] Never, always use explicit if/else
- [ ] Only for simple assignments (e.g., `status = 'active' if enabled else 'inactive'`)
- [ ] OK when it improves readability
- [ ] Other: _________________

**d) Short-circuit evaluation - rely on it?**
```python
# Relying on short-circuit
if user and user.is_active:
    pass

# Explicit checks
if user is not None:
    if user.is_active:
        pass
```
- [ ] Use short-circuit (first example)
- [ ] Explicit checks always (second example)
- [ ] Context-dependent (when?): _________________

---

### 4.2 Loop and Iteration Patterns

**Question**: Loop and iteration preferences?

**a) For loops vs comprehensions - when to use each?**
- [ ] Comprehensions for simple transforms, loops for complex logic
- [ ] Always use comprehensions when possible (more Pythonic)
- [ ] Prefer explicit loops for readability
- [ ] No strong preference
- [ ] Other: _________________

**b) Nested comprehensions - acceptable?**
```python
# Nested list comprehension
result = [[process(x) for x in row] for row in matrix]

# Explicit nested loops
result = []
for row in matrix:
    row_result = []
    for x in row:
        row_result.append(process(x))
    result.append(row_result)
```
- [ ] Nested comprehensions OK if readable
- [ ] Never, always use explicit loops
- [ ] Max 2 levels of nesting
- [ ] Other: _________________

**c) Generator expressions vs list comprehensions?**
- [ ] Use generators whenever possible (memory efficient)
- [ ] Use lists for small collections, generators for large
- [ ] No strong preference
- [ ] Other: _________________

**d) `enumerate()` vs manual counter?**
```python
# enumerate
for index, item in enumerate(items):
    pass

# Manual counter
index = 0
for item in items:
    # use index
    index += 1
```
- [ ] Always use enumerate()
- [ ] Manual counter for clarity
- [ ] No preference
- [ ] Other: _________________

**e) Loop else clause - use it?**
```python
for item in items:
    if condition:
        break
else:
    # No break occurred
    handle_no_match()
```
- [ ] Yes, it's Pythonic
- [ ] No, too confusing
- [ ] Only with comment explaining behavior
- [ ] Other: _________________

---

## Section 5: Error Handling and Validation

### 5.1 Exception Handling Patterns

**Question**: Error handling preferences?

**a) Exception granularity - specific vs broad?**
- [ ] Always catch specific exceptions only
- [ ] Catch broad exceptions at top level, specific in functions
- [ ] Context-dependent (explain): _________________

**b) Exception chaining - when to use?**
- [ ] Always chain with `raise ... from ...`
- [ ] Only when adding context to exception
- [ ] Rarely, just re-raise
- [ ] Other: _________________

**c) Custom exceptions - when to create?**
- [ ] For each error category (e.g., `ValidationError`, `ProcessingError`)
- [ ] Only when built-in exceptions are inadequate
- [ ] Create exception hierarchy for domain
- [ ] Avoid, use built-in exceptions
- [ ] Other: _________________

**d) Exception messages - format preference?**
```python
# Option 1: Detailed with context
raise ValueError(
    f"Invalid sample rate: {sample_rate}. "
    f"Expected range: 8000-192000 Hz. "
    f"File: {file_path}"
)

# Option 2: Brief message
raise ValueError(f"Invalid sample rate: {sample_rate}")

# Option 3: Very verbose
raise ValueError(
    f"Sample rate validation failed for file '{file_path}'. "
    f"Received value: {sample_rate} Hz. "
    f"Valid range: 8000-192000 Hz. "
    f"Common values: 44100, 48000, 96000, 192000. "
    f"Please check input file format."
)
```
- [ ] Option 1 (detailed with context)
- [ ] Option 2 (brief)
- [ ] Option 3 (very verbose)
- [ ] Other: _________________

**e) Logging vs raising - when to do both?**
- [ ] Always log before raising
- [ ] Log only if handling exception, raise if propagating
- [ ] Never log before raising (let caller handle)
- [ ] Other: _________________

---

### 5.2 Input Validation

**Question**: Validation approach preferences?

**a) Validation timing - when to validate?**
- [ ] At function entry (fail fast)
- [ ] Just before use (lazy validation)
- [ ] Both (explain when): _________________

**b) Type checking - how strict?**
- [ ] Use `isinstance()` checks
- [ ] Rely on type hints + mypy
- [ ] Duck typing (try to use, catch errors)
- [ ] Mix (explain): _________________

**c) Validation helper functions - pattern?**
```python
# Option 1: Raise exceptions
def validate_sample_rate(rate: int) -> None:
    if not 8000 <= rate <= 192000:
        raise ValueError(f"Invalid rate: {rate}")

# Option 2: Return boolean
def is_valid_sample_rate(rate: int) -> bool:
    return 8000 <= rate <= 192000

# Option 3: Return tuple (valid, message)
def validate_sample_rate(rate: int) -> tuple[bool, str]:
    if 8000 <= rate <= 192000:
        return True, ""
    return False, f"Invalid rate: {rate}"
```
- [ ] Option 1 (raise exceptions)
- [ ] Option 2 (return boolean)
- [ ] Option 3 (return tuple)
- [ ] Mix (when to use which?): _________________

**d) Assertion statements - appropriate use?**
- [ ] Use for internal invariants only
- [ ] Use for all validation
- [ ] Never use (can be disabled)
- [ ] Other: _________________

---

## Section 6: Django-Specific Patterns

### 6.1 Model Preferences

**Question**: Django model coding preferences?

**a) Model method organization - preferred order?**
Order these from 1 (first) to 6 (last):
- [ ] Field definitions: _____
- [ ] Meta class: _____
- [ ] `__str__()` method: _____
- [ ] Properties: _____
- [ ] Instance methods: _____
- [ ] Class methods and managers: _____

**b) Model validation - where to implement?**
- [ ] In `clean()` method
- [ ] In custom validators
- [ ] In `save()` override
- [ ] Mix (explain): _________________

**c) QuerySet methods - where to define?**
- [ ] Custom Manager class
- [ ] Separate QuerySet class
- [ ] Both (Manager delegates to QuerySet)
- [ ] Other: _________________

**d) Related name conventions - pattern?**
```python
# Option 1: Plural of source model
class Schema(models.Model):
    pass

class Rule(models.Model):
    schema = models.ForeignKey(Schema, related_name='rules')

# Option 2: Descriptive relationship
class Rule(models.Model):
    schema = models.ForeignKey(Schema, related_name='schema_rules')

# Option 3: Verbose descriptor
class Rule(models.Model):
    schema = models.ForeignKey(Schema, related_name='associated_rules')
```
- [ ] Option 1 (plural)
- [ ] Option 2 (descriptive)
- [ ] Option 3 (verbose)
- [ ] Other: _________________

---

### 6.2 View Preferences

**Question**: Django view coding preferences?

**a) View organization - function vs class-based?**
- [ ] Class-based views (CBV) always
- [ ] Function-based views (FBV) always
- [ ] CBV for CRUD, FBV for custom logic
- [ ] Other: _________________

**b) View docstrings - what to include?**
- [ ] URL pattern, HTTP methods, parameters
- [ ] Purpose and return format only
- [ ] Full request/response examples
- [ ] Other: _________________

**c) Business logic in views - acceptable?**
- [ ] Never, use services/managers
- [ ] Simple logic OK, complex in services
- [ ] No restriction
- [ ] Other: _________________

**d) Response formatting - pattern preference?**
```python
# Option 1: Inline dict
return JsonResponse({
    'status': 'success',
    'data': results
})

# Option 2: Named variable
response_data = {
    'status': 'success',
    'data': results
}
return JsonResponse(response_data)

# Option 3: Response builder
return build_success_response(data=results)
```
- [ ] Option 1
- [ ] Option 2
- [ ] Option 3
- [ ] Other: _________________

---

## Section 7: Testing Conventions

### 7.1 Test Organization

**Question**: Test coding preferences?

**a) Test file naming - pattern?**
- [ ] `test_<module>.py` (e.g., `test_file_processor.py`)
- [ ] `<module>_test.py` (e.g., `file_processor_test.py`)
- [ ] Mirror source structure (e.g., `apps/processing/tests/test_file_processor.py`)
- [ ] Other: _________________

**b) Test class naming - convention?**
- [ ] `Test<ClassName>` (e.g., `TestFileProcessor`)
- [ ] `<ClassName>Tests` (e.g., `FileProcessorTests`)
- [ ] Descriptive (e.g., `FileProcessorUnitTests`)
- [ ] Other: _________________

**c) Test method naming - pattern?**
- [ ] `test_<method>_<condition>_<expected>` (e.g., `test_process_file_invalid_format_raises_error`)
- [ ] `test_<method>_<condition>` (e.g., `test_process_file_invalid_format`)
- [ ] `test_<behavior>` (e.g., `test_raises_error_on_invalid_format`)
- [ ] Other: _________________

**d) Test docstrings - necessary?**
- [ ] Yes, always explain what test validates
- [ ] Only for complex tests
- [ ] No, method name is sufficient
- [ ] Other: _________________

**e) Test assertion messages - custom messages?**
```python
# With custom message
self.assertTrue(result, f"Expected processing to succeed for {file_path}")

# Without custom message
self.assertTrue(result)
```
- [ ] Always include custom messages
- [ ] Only for non-obvious assertions
- [ ] Rarely, assertion error is sufficient
- [ ] Other: _________________

---

## Section 8: Performance and Optimization

### 8.1 Code Optimization Preferences

**Question**: Performance and optimization preferences?

**a) Premature optimization - stance?**
- [ ] Profile first, then optimize
- [ ] Write efficient code from start
- [ ] Optimize only when performance problems arise
- [ ] Other: _________________

**b) List vs generator - default choice?**
- [ ] Always use generators for memory efficiency
- [ ] Use lists for predictability
- [ ] Profile-guided decision
- [ ] Other: _________________

**c) Database query optimization - approach?**
- [ ] Always use select_related/prefetch_related
- [ ] Add optimization when N+1 queries detected
- [ ] Optimize based on profiling
- [ ] Other: _________________

**d) Caching strategy - when to implement?**
- [ ] Cache expensive computations proactively
- [ ] Add caching when performance issues arise
- [ ] Cache based on profiling data
- [ ] Other: _________________

**e) Code readability vs performance - trade-off?**
- [ ] Readability always wins
- [ ] Performance critical sections can sacrifice readability
- [ ] Balance case-by-case
- [ ] Other: _________________

---

## Section 9: Logging and Debugging

### 9.1 Logging Preferences

**Question**: Logging strategy preferences?

**a) Log levels - when to use each?**
Define when to use:
- DEBUG: _________________
- INFO: _________________
- WARNING: _________________
- ERROR: _________________
- CRITICAL: _________________

**b) Log message format - preference?**
```python
# Option 1: Brief
logger.info(f"Processing {file_path}")

# Option 2: Detailed
logger.info(f"Starting file processing: {file_path} with schema {schema_id}")

# Option 3: Structured
logger.info(
    "File processing started",
    extra={'file_path': file_path, 'schema_id': schema_id}
)
```
- [ ] Option 1
- [ ] Option 2
- [ ] Option 3
- [ ] Other: _________________

**c) Exception logging - include traceback?**
- [ ] Always use `logger.exception()` for full traceback
- [ ] Use `logger.error()` with exception message only
- [ ] Context-dependent (when?): _________________

**d) Sensitive data in logs - how to handle?**
- [ ] Never log sensitive data
- [ ] Log with masking (e.g., `user@***.com`)
- [ ] Log in DEBUG mode only with warnings
- [ ] Other: _________________

**e) Log statement density - how often?**
- [ ] Start/end of every function
- [ ] Major operations only
- [ ] Decision points and errors only
- [ ] Other: _________________

---

### 9.2 Debug Code

**Question**: Debugging code preferences?

**a) Print statements for debugging - acceptable?**
- [ ] Never, use proper logging
- [ ] OK during development, remove before commit
- [ ] OK with `# DEBUG:` marker
- [ ] Other: _________________

**b) Debugger breakpoints - in committed code?**
- [ ] Never commit breakpoint statements
- [ ] OK with clear comment
- [ ] Use conditional breakpoints only
- [ ] Other: _________________

**c) Debug flags/modes - implementation?**
- [ ] Use Django settings.DEBUG
- [ ] Custom DEBUG_MODE setting
- [ ] Environment variable check
- [ ] Other: _________________

---

## Section 10: Git and Version Control

### 10.1 Commit Preferences

**Question**: Git commit preferences?

**a) Commit message format - preferred style?**
```
# Option 1: Conventional Commits
feat: Add FFmpeg detection service
fix: Resolve race condition in queue processor
docs: Update coding standards

# Option 2: Simple imperative
Add FFmpeg detection service
Fix race condition in queue processor
Update coding standards

# Option 3: Detailed
Add FFmpeg detection service

- Implement OS detection for Windows/macOS/Linux
- Add auto-download logic with fallback
- Include binary verification
```
- [ ] Option 1 (Conventional Commits)
- [ ] Option 2 (Simple imperative)
- [ ] Option 3 (Detailed)
- [ ] Other: _________________

**b) Commit frequency - preference?**
- [ ] Commit after each logical change (frequent)
- [ ] Commit when feature/fix is complete
- [ ] Commit at end of work session
- [ ] Other: _________________

**c) WIP commits - acceptable?**
- [ ] Yes, with `WIP:` prefix in message
- [ ] No, only commit complete work
- [ ] OK in feature branches only
- [ ] Other: _________________

---

## Section 11: Custom Preferences

### 11.1 Additional Requirements

**Question**: Any additional coding preferences not covered?

**a) String formatting - preferred method?**
- [ ] f-strings (e.g., `f"Processing {file}"`)
- [ ] .format() (e.g., `"Processing {}".format(file)`)
- [ ] % formatting (e.g., `"Processing %s" % file`)
- [ ] Template strings
- [ ] Other: _________________

**b) Path handling - preference?**
- [ ] pathlib.Path exclusively
- [ ] os.path functions
- [ ] Mix (when to use which?): _________________

**c) Configuration - how to manage?**
- [ ] Django settings.py only
- [ ] Environment variables
- [ ] Config files (YAML/JSON)
- [ ] Mix (explain): _________________

**d) Dependency injection - pattern?**
- [ ] Constructor injection
- [ ] Property injection
- [ ] No formal DI, pass as needed
- [ ] Other: _________________

**e) Any other preferences or requirements?**

_________________
_________________
_________________

---

## Section 12: Review and Priorities

### 12.1 Priority Ranking

**Question**: Which coding standards are most important to you?

Rank these from 1 (most important) to 10 (least important):
- [ ] Clear, descriptive naming: _____
- [ ] Comprehensive documentation/comments: _____
- [ ] Type safety (type hints): _____
- [ ] Consistent formatting (automated tools): _____
- [ ] Error handling completeness: _____
- [ ] Code readability over brevity: _____
- [ ] Performance optimization: _____
- [ ] Test coverage: _____
- [ ] Consistent patterns across codebase: _____
- [ ] Git commit quality: _____

### 12.2 Enforcement Preferences

**Question**: How should coding standards be enforced?

**a) Enforcement mechanism?**
- [ ] Pre-commit hooks (automated, blocking)
- [ ] CI/CD checks (automated, but can be bypassed locally)
- [ ] Code review only (manual)
- [ ] Mix (explain): _________________

**b) Standard violations - how to handle?**
- [ ] Block PR/commit until fixed
- [ ] Warning only, reviewer decides
- [ ] Document as tech debt, fix later
- [ ] Other: _________________

**c) Standard updates - how to manage?**
- [ ] Team discussion before any changes
- [ ] PM/Lead decides and announces
- [ ] Evolve naturally with retrospectives
- [ ] Other: _________________

---

## Section 13: AI Agent Specific Requirements

### 13.1 AI-Generated Code

**Question**: Special requirements for AI-generated code?

**a) AI code markers - should it be identified?**
- [ ] Yes, mark with `# AI-GENERATED` comment
- [ ] Yes, in commit message only
- [ ] No, treat same as human code
- [ ] Other: _________________

**b) AI code review - additional scrutiny?**
- [ ] Yes, require more thorough review
- [ ] Same standards as human code
- [ ] Focus on specific areas (which?): _________________

**c) AI agent instructions - how detailed?**
- [ ] Very detailed (explicit requirements for everything)
- [ ] High-level guidelines (let agent decide details)
- [ ] Mix (explain): _________________

**d) Cross-agent consistency - how to ensure?**
- [ ] Shared coding standards document (already done)
- [ ] Code review focuses on consistency
- [ ] Template/boilerplate code
- [ ] Other: _________________

---

## Completion

### Summary

Please review your answers and confirm:

- [ ] I have answered all relevant questions
- [ ] My preferences are consistent with project goals
- [ ] I understand these will be incorporated into formal coding standards
- [ ] I'm ready to have these standards applied to the codebase

### Additional Comments

Any final thoughts, clarifications, or special requirements?

_________________
_________________
_________________

---

**Next Steps After Completion**:
1. Review responses for consistency
2. Update `docs/coding-standards.md` with detailed preferences
3. Create code templates/examples based on preferences
4. Update story acceptance criteria with new requirements
5. Configure tools (linters, formatters) to enforce preferences
6. Brief AI agents on updated standards

---

*This elicitation wizard captures your detailed coding preferences to create a comprehensive, actionable coding standards document tailored to your development experience and project needs.*
