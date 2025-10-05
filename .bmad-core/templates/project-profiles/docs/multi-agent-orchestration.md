# Multi-Agent Orchestration Guide

**Version:** 1.0.0
**Last Updated:** 2025-10-02
**Purpose:** Guide for implementing multi-agent architecture in BMAD Policy Manager

---

## 📋 Overview

The BMAD Policy Manager uses a **multi-agent architecture** to handle brownfield project detection while preserving context efficiency. This guide documents how agents collaborate, delegate tasks, and manage context budgets.

### Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                    Agent 1: UI Handler                  │
│                  (Persistent, 50K budget)               │
│                                                         │
│  • Manages conversation flow                           │
│  • Delegates file operations                           │
│  • Stores compressed results                           │
│  • Presents findings to user                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Task Tool Invocation
                     │ (JSON request)
                     ↓
┌─────────────────────────────────────────────────────────┐
│                Agent 2: File Operations                 │
│                (Ephemeral, 20K per task)                │
│                                                         │
│  • Analyzes files for conventions                      │
│  • Compresses data (15K → 500 tokens)                  │
│  • Writes policy/profile files                         │
│  • Context cleared after task                          │
└─────────────────────────────────────────────────────────┘
                     │
                     │ JSON Response
                     │ (~500 tokens)
                     ↓
                 [Agent 1]
```

### Key Principles

1. **No File-Based Exchange:** Agents exchange data via Task tool return values only
2. **Deferred Writes:** No files written until final user approval
3. **Context Preservation:** Agent 1 stays under 50K, Agent 2 cleared after each task
4. **Data Compression:** Agent 2 compresses 15K+ tokens to ~500 token JSON response
5. **Single Responsibility:** Agent 1 = UI, Agent 2 = File Operations

---

## 🤖 Agent 1: UI/Conversation Handler

### Role & Responsibilities

**Primary Role:** Persistent conversation handler and wizard orchestrator

**Key Responsibilities:**

- Manage wizard flow and user interaction
- Store conversation state and detected conventions
- Delegate file analysis to Agent 2
- Present findings to user for validation
- Delegate file writes to Agent 2 after approval
- Handle errors and context overflow

**Context Budget:**

- **Total Budget:** 50,000 tokens (persistent)
- **Conversation:** ~30,000 tokens
- **Compressed Data:** ~500 tokens per Agent 2 response
- **Reserved:** ~10,000 tokens for final operations

### When to Delegate to Agent 2

**Delegate for Detection when:**

- User selects Automatic or Hinted brownfield detection
- Files need to be analyzed for conventions
- Raw file contents should NOT pollute Agent 1's context

**Delegate for Writes when:**

- User has approved final summary
- Policy and profile YAML files need to be created
- Agent 1 must NOT write files directly

**Do NOT delegate when:**

- User selects Manual specification (no file analysis needed)
- User is answering questions (standard wizard flow)
- Greenfield project (no brownfield detection)

### Task Invocation Format

#### Detection Task

```markdown
<invoke name="Task">
  <parameter name="subagent_type">general-purpose</parameter>
  <parameter name="description">Detect brownfield project conventions</parameter>
  <parameter name="prompt">
    Analyze these files and extract coding conventions:

    Files to analyze:
    - pyproject.toml (config)
    - .ruff.toml (config)
    - src/main.py (source sample)
    - tests/test_main.py (test sample)

    Extract and return ONLY these values (NOT raw file contents):
    - Language version (from config)
    - Formatter and line length (from config)
    - Testing framework (from config/imports)
    - Docstring style (from code samples via regex)
    - Type hints usage % (count annotations in samples)
    - Average function/file sizes (measure in samples)

    Return compact JSON:
    {
      "detected_conventions": {
        "python_version": ">=3.11",
        "formatter": "ruff",
        "line_length": 100,
        "testing_framework": "pytest",
        "docstring_style": "google",
        "type_hints_usage": "90%",
        "avg_function_lines": 25,
        "avg_file_lines": 180
      },
      "confidence": {
        "python_version": 1.0,
        "formatter": 0.95,
        "docstring_style": 0.8
      },
      "sources": {
        "python_version": "pyproject.toml:requires-python",
        "formatter": "pyproject.toml:[tool.ruff]"
      }
    }

    CRITICAL RULES:
    1. Return ONLY extracted values (NO raw file contents)
    2. Keep response under 1000 tokens
    3. Use pattern matching for extraction (see brownfield-detection-template.yaml)
    4. Your context will be cleared after this task

  </parameter>
</invoke>
```

#### Write Task

````markdown
<invoke name="Task">
  <parameter name="subagent_type">general-purpose</parameter>
  <parameter name="description">Write approved policy and profile files</parameter>
  <parameter name="prompt">
    Write the following YAML files:

    File 1: bmad-core/templates/project-profiles/policies/user-policies/my-project-coding-v1.yaml
    Content:
    ```yaml
    policy:
      id: my-project-coding-v1
      name: "My Project Coding Standards"
      type: user
      category: code-quality
      protected: false
      created: "2025-10-02T10:30:00Z"
      updated: "2025-10-02T10:30:00Z"

    rules:
      philosophy: pragmatic
      max_file_lines: 500
      formatter: ruff
      line_length: 100
      require_type_hints: true
      docstring_style: google
    ```

    File 2: bmad-core/templates/project-profiles/policies/user-policies/my-project-security-v1.yaml
    Content:
    ```yaml
    [full YAML content...]
    ```

    [... additional files ...]

    After writing all files, return:
    {
      "status": "success",
      "files_written": 4,
      "files": [
        "bmad-core/templates/project-profiles/policies/user-policies/my-project-coding-v1.yaml",
        "bmad-core/templates/project-profiles/policies/user-policies/my-project-security-v1.yaml",
        "bmad-core/templates/project-profiles/policies/user-policies/my-project-testing-v1.yaml",
        "bmad-core/templates/project-profiles/profiles/my-project.yaml"
      ]
    }

    If any write fails, return:
    {
      "status": "error",
      "message": "description of error",
      "files_written": 2,
      "files": ["successful paths"],
      "failed": ["failed paths"]
    }

  </parameter>
</invoke>
````

### Handling Agent 2 Responses

#### Detection Response

**Expected Format:**

```json
{
  "detected_conventions": {
    "python_version": ">=3.11",
    "formatter": "ruff",
    "line_length": 100,
    "testing_framework": "pytest",
    "docstring_style": "google",
    "type_hints_usage": "90%",
    "avg_function_lines": 25,
    "avg_file_lines": 180
  },
  "confidence": {
    "python_version": 1.0,
    "formatter": 0.95,
    "testing_framework": 1.0,
    "docstring_style": 0.8,
    "type_hints_usage": 0.85
  },
  "sources": {
    "python_version": "pyproject.toml:requires-python",
    "formatter": "pyproject.toml:[tool.ruff]",
    "testing_framework": "pyproject.toml:[tool.pytest]",
    "docstring_style": "src/main.py:pattern_analysis"
  }
}
```

**Agent 1 Actions:**

1. Store conventions in memory: `{detected_conventions} = response.detected_conventions`
2. Present findings to user with confidence scores
3. Prompt for confirmation: "Are these correct? (y/n)"
4. If no, prompt for corrections
5. Continue wizard with detected/corrected values

**Presentation Format:**

```
═══ Detected Conventions ═══

I analyzed your Python project and detected these conventions:

Language & Tools:
  • Python 3.11+ (from pyproject.toml) [confidence: 100%]
  • Ruff formatter, 100 line length (from pyproject.toml) [confidence: 95%]
  • pytest for testing (from pyproject.toml) [confidence: 100%]

Code Style (from sample files):
  • Google docstring style (detected in 4/5 files) [confidence: 80%]
  • Type hints used consistently (90% of functions) [confidence: 85%]
  • Average function length: 25 lines
  • Average file length: 180 lines

Are these correct? (y/n): _
```

#### Write Response

**Success:**

```json
{
  "status": "success",
  "files_written": 4,
  "files": [
    "bmad-core/templates/project-profiles/policies/user-policies/my-project-coding-v1.yaml",
    "bmad-core/templates/project-profiles/policies/user-policies/my-project-security-v1.yaml",
    "bmad-core/templates/project-profiles/policies/user-policies/my-project-testing-v1.yaml",
    "bmad-core/templates/project-profiles/profiles/my-project.yaml"
  ]
}
```

**Agent 1 Actions:**

1. Confirm success: "✅ Profile 'my-project' saved successfully!"
2. List created files
3. If directory changed, prompt to return to original directory
4. Return to main menu

**Error:**

```json
{
  "status": "error",
  "message": "Permission denied writing to bmad-core/templates/...",
  "files_written": 2,
  "files": ["file1.yaml", "file2.yaml"],
  "failed": ["file3.yaml", "file4.yaml"]
}
```

**Agent 1 Actions:**

1. Show error to user
2. Retry with fresh Agent 2 (context overflow) OR
3. Ask for elevated permissions OR
4. Offer alternative save location

---

## 🛠️ Agent 2: File Operations Handler

### Role & Responsibilities

**Primary Role:** Ephemeral file analyzer and writer

**Key Responsibilities:**

- Read and analyze files for brownfield detection
- Extract conventions using pattern matching (NOT AST parsing)
- Compress data from 15K+ tokens to ~500 tokens
- Write policy/profile YAML files
- Return structured JSON responses

**Context Budget:**

- **Total Budget:** 20,000 tokens per task
- **File Reads:** ~15,000 tokens (raw contents)
- **Processing:** ~3,000 tokens (pattern matching, calculations)
- **Response:** ~1,000 tokens (JSON return)
- **Context Cleared:** After each task completion

### Convention Extraction Strategy

#### Pattern Matching (NOT AST Parsing)

**Language Version Detection:**

```python
# Python example
patterns = [
    r'requires-python\s*=\s*["\']([^"\']+)["\']',  # pyproject.toml
    r'python_requires\s*=\s*["\']([^"\']+)["\']',  # setup.py
]
```

**Formatter Detection:**

```python
patterns = [
    r'\[tool\.black\]',      # Black formatter
    r'\[tool\.ruff\]',       # Ruff formatter
    r'\[tool\.autopep8\]',   # autopep8
]
```

**Docstring Style Detection:**

```python
google_patterns = [
    r'Args:\n',
    r'Returns:\n',
    r'Raises:\n',
]

numpy_patterns = [
    r'Parameters\n\s*----------',
    r'Returns\n\s*-------',
]

# Count occurrences, use most_common
```

**Type Hints Usage:**

```python
# Count annotated vs non-annotated functions
param_type_pattern = r'def [^(]+\([^)]*:\s*\w+'
return_type_pattern = r'def [^(]+\([^)]*\)\s*->\s*\w+'

usage_percent = annotated_count / total_functions
```

#### File Sampling Rules

**Automatic Mode - Python:**

1. **Priority configs (all that exist):**
   - pyproject.toml
   - setup.py
   - .ruff.toml
   - requirements.txt

2. **Source samples (max 5 files, 300 lines each):**
   - Main entry: src/main.py, app.py, \_\_init\_\_.py
   - Core modules: src/\*\*/\*.py (limit 2)
   - Test files: tests/\*\*/\*.py (limit 2)

3. **Skip patterns:**
   - \*/venv/\*
   - \*/.venv/\*
   - \*/\_\_pycache\_\_/\*
   - \*\_pb2.py

**Hinted Mode:**

- User specifies max 8 files (3 docs + 5 modules)
- Validate all paths exist
- Read specified files only

#### Data Compression

**Input:** 15,000 tokens (raw file contents)
**Output:** 500-1,000 tokens (JSON)
**Ratio:** 15-30x compression

**Compression Techniques:**

1. Extract values only (no raw file contents)
2. Use pattern matching (not full parsing)
3. Count/measure instead of storing code
4. Return compact JSON structure
5. Include only what Agent 1 needs

**Example Compression:**

Input (3,000 tokens):

```python
# pyproject.toml (500 lines)
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.11"
...

[tool.ruff]
line-length = 100
target-version = "py311"
...

[tool.pytest.ini_options]
testpaths = ["tests"]
...

# src/main.py (200 lines)
def process_data(items: list[str]) -> dict[str, int]:
    """Process items and return counts.

    Args:
        items: List of items to process

    Returns:
        Dictionary mapping items to counts
    """
    ...
```

Output (150 tokens):

```json
{
  "detected_conventions": {
    "python_version": ">=3.11",
    "formatter": "ruff",
    "line_length": 100,
    "testing_framework": "pytest",
    "docstring_style": "google",
    "type_hints_usage": "95%",
    "avg_function_lines": 22,
    "avg_file_lines": 175
  },
  "confidence": {
    "python_version": 1.0,
    "formatter": 0.95,
    "testing_framework": 1.0,
    "docstring_style": 0.85,
    "type_hints_usage": 0.9
  },
  "sources": {
    "python_version": "pyproject.toml:requires-python",
    "formatter": "pyproject.toml:[tool.ruff]",
    "testing_framework": "pyproject.toml:[tool.pytest]",
    "docstring_style": "src/main.py:pattern_analysis"
  }
}
```

### File Writing Strategy

**Agent 2 receives complete YAML content from Agent 1:**

1. Parse file list and YAML content
2. Validate paths and permissions
3. Write files sequentially
4. Track successes/failures
5. Return status JSON

**Success Criteria:**

- All files written successfully
- Paths created if needed
- Permissions validated

**Failure Handling:**

- Continue writing remaining files
- Track failed paths separately
- Return detailed error with partial success

---

## 🔄 Task Delegation Protocol

### Detection Task Flow

```
┌─────────────┐
│   Agent 1   │
│             │
│ 1. User     │
│    selects  │
│    automatic│
└──────┬──────┘
       │
       │ 2. Select files (smart selection)
       │
       ↓
┌─────────────────────────────────────┐
│ Task Invocation                     │
│                                     │
│ subagent: general-purpose           │
│ description: "Detect conventions"   │
│ prompt:                             │
│   - Files to analyze: [list]        │
│   - Extract: [specific values]      │
│   - Return: compact JSON            │
│   - Rules: NO raw contents          │
└──────────┬──────────────────────────┘
           │
           ↓
    ┌─────────────┐
    │   Agent 2   │
    │             │
    │ 3. Read     │
    │    files    │
    │    (15K)    │
    │             │
    │ 4. Pattern  │
    │    match    │
    │             │
    │ 5. Extract  │
    │    values   │
    │             │
    │ 6. Compress │
    │    to JSON  │
    │    (500)    │
    └──────┬──────┘
           │
           ↓
    ┌──────────────────┐
    │ JSON Response    │
    │                  │
    │ {                │
    │   "detected...", │
    │   "confidence",  │
    │   "sources"      │
    │ }                │
    └──────┬───────────┘
           │
           ↓
    ┌─────────────┐
    │   Agent 1   │
    │             │
    │ 7. Store    │
    │    data     │
    │             │
    │ 8. Present  │
    │    to user  │
    │             │
    │ 9. Validate │
    └─────────────┘
```

### Write Task Flow

```
┌─────────────┐
│   Agent 1   │
│             │
│ 1. User     │
│    approves │
│    summary  │
└──────┬──────┘
       │
       │ 2. Prepare YAML content
       │
       ↓
┌─────────────────────────────────────┐
│ Task Invocation                     │
│                                     │
│ subagent: general-purpose           │
│ description: "Write files"          │
│ prompt:                             │
│   - File 1: path + YAML content     │
│   - File 2: path + YAML content     │
│   - ...                             │
│   - Return: status JSON             │
└──────────┬──────────────────────────┘
           │
           ↓
    ┌─────────────┐
    │   Agent 2   │
    │             │
    │ 3. Parse    │
    │    files    │
    │             │
    │ 4. Write    │
    │    each     │
    │    file     │
    │             │
    │ 5. Track    │
    │    status   │
    └──────┬──────┘
           │
           ↓
    ┌──────────────────┐
    │ Status Response  │
    │                  │
    │ {                │
    │   "status": "ok",│
    │   "files": [...] │
    │ }                │
    └──────┬───────────┘
           │
           ↓
    ┌─────────────┐
    │   Agent 1   │
    │             │
    │ 6. Confirm  │
    │    success  │
    │             │
    │ 7. Return   │
    │    to menu  │
    └─────────────┘
```

---

## 🧠 Context Management Strategy

### Token Budget Allocation

**Agent 1 (50K Total):**

- Conversation history: ~30,000 tokens
- Wizard state: ~5,000 tokens
- Compressed conventions: ~500 tokens per detection
- Final YAML preparation: ~10,000 tokens
- Safety margin: ~4,500 tokens

**Agent 2 (20K Per Task):**

- File reads: ~15,000 tokens
- Pattern matching/processing: ~3,000 tokens
- Response generation: ~1,000 tokens
- Safety margin: ~1,000 tokens

### Context Clearing Rules

**Agent 2 Context Cleared:**

- ✅ After detection task completes
- ✅ After write task completes
- ✅ On error/timeout
- ✅ Before retry operations

**Agent 1 Context Preserved:**

- ✅ Throughout wizard session
- ✅ Across multiple Agent 2 delegations
- ✅ During user corrections/validations
- ✅ Until final completion

### Data Flow & Compression

**Phase 1: Detection**

```
Agent 2 reads:     15,000 tokens (raw files)
Agent 2 processes:  3,000 tokens (pattern matching)
Agent 2 returns:      500 tokens (JSON)
Agent 1 stores:       500 tokens (conventions)

Net savings: 14,500 tokens kept out of Agent 1 context
```

**Phase 2: Validation**

```
Agent 1 uses:         500 tokens (display findings)
User interaction:   1,000 tokens (corrections)
Agent 1 stores:       500 tokens (final values)

Total in Agent 1: 2,000 tokens (vs 15,000 if no Agent 2)
```

**Phase 3: Writing**

```
Agent 1 prepares:   5,000 tokens (YAML content)
Agent 2 receives:   5,000 tokens (file list + content)
Agent 2 writes:         0 tokens (disk operations)
Agent 2 returns:      200 tokens (status JSON)

Total in Agent 1: 200 tokens (vs 5,000 if Agent 1 wrote)
```

### Memory Optimization

**Agent 1 Memory Structure:**

```python
{
  "original_directory": "/path/to/start",
  "directory_changed": true,
  "project_type": "brownfield",
  "detection_method": "automatic",
  "detected_conventions": {
    "python_version": ">=3.11",
    "formatter": "ruff",
    # ... compact values only
  },
  "wizard_responses": {
    "coding_philosophy": "pragmatic",
    "security_level": "high",
    # ... user answers only
  }
}
```

**What NOT to Store:**

- ❌ Raw file contents
- ❌ Full source code
- ❌ Detailed parsing results
- ❌ Intermediate calculations

---

## ⚠️ Error Handling Procedures

### Context Overflow Recovery

**Detection Task Overflow:**

```python
# Agent 1 detects overflow in Agent 2 response
if "context overflow" in agent_2_error:
    # Strategy 1: Reduce file sample
    files_to_analyze = files_to_analyze[:3]  # Reduce from 5 to 3
    retry_with_fewer_files()

# Strategy 2: Switch to hinted mode
if retry_fails:
    prompt_user_for_key_files()  # Let user specify 3-5 files
```

**Write Task Overflow:**

```python
# Agent 1 detects write failure due to context
if agent_2_response["status"] == "error":
    if "context" in agent_2_response["message"]:
        # Spawn fresh Agent 2
        inform_user("Retrying file write with fresh context...")
        spawn_new_agent_2()
        retry_write_task()
```

### Low Confidence Detection

**Confidence Thresholds:**

- **High (≥0.8):** Use value, inform user
- **Medium (0.5-0.8):** Suggest value, ask confirmation
- **Low (<0.5):** Ask user explicitly

**Handler:**

```python
for key, confidence in response["confidence"].items():
    if confidence >= 0.8:
        use_detected_value(key)
    elif confidence >= 0.5:
        value = response["detected_conventions"][key]
        confirmed = ask_user(f"Use {value} for {key}? (y/n)")
        if confirmed:
            use_detected_value(key)
        else:
            prompt_for_value(key)
    else:
        inform_user(f"Could not detect {key}")
        prompt_for_value(key)
```

### File Not Found

**During Detection:**

```python
# Agent 2 encounters missing file
if file_not_found:
    skip_file()
    log_to_sources("file_not_found")
    continue_with_remaining_files()

# Return partial results
return {
    "detected_conventions": {/* partial */},
    "confidence": {/* lower scores */},
    "sources": {
        "formatter": "file_not_found:pyproject.toml"
    }
}
```

**Agent 1 Response:**

```python
# Check for missing files
for key, source in response["sources"].items():
    if "file_not_found" in source:
        inform_user(f"Could not find {source.split(':')[1]}")
        prompt_for_value(key)
```

### Permission Errors

**Write Failure:**

```python
# Agent 2 encounters permission error
try:
    write_file(path, content)
except PermissionError as e:
    failed_files.append(path)
    continue  # Try remaining files

# Return partial success
return {
    "status": "error",
    "message": f"Permission denied: {failed_files[0]}",
    "files_written": len(successful_files),
    "files": successful_files,
    "failed": failed_files
}
```

**Agent 1 Recovery:**

```python
if response["status"] == "error":
    if "Permission denied" in response["message"]:
        # Option 1: Retry with sudo
        if ask_user("Retry with elevated permissions? (y/n)"):
            retry_with_sudo()
        # Option 2: Alternative location
        else:
            alt_path = ask_user("Alternative save location:")
            retry_with_path(alt_path)
```

### Directory Navigation Errors

**Invalid Path:**

```python
# Agent 1 validates before navigation
path = ask_user("Enter project directory:")

if not os.path.exists(path):
    error("❌ Directory not found. Please try again.")
    # Re-prompt or offer to cancel
    retry_or_cancel()
else:
    cd(path)
    confirm(f"✅ Now analyzing: {path}")
    directory_changed = True
```

---

## 📚 Example Task Invocations

### Example 1: Python Automatic Detection

**Agent 1 Invocation:**

```xml
<invoke name="Task">
  <parameter name="subagent_type">general-purpose</parameter>
  <parameter name="description">Detect Python brownfield conventions</parameter>
  <parameter name="prompt">
    You are Agent 2. Analyze this Python project and extract conventions.

    Files to analyze:
    1. pyproject.toml (config)
    2. requirements.txt (dependencies)
    3. src/main.py (entry point, 150 lines)
    4. src/core/processor.py (core module, 220 lines)
    5. tests/test_processor.py (test file, 180 lines)

    Extract these values using pattern matching:

    From pyproject.toml:
    - requires-python = "VERSION" → python_version
    - [tool.black] or [tool.ruff] → formatter
    - line-length = NUMBER → line_length
    - [tool.pytest] → testing_framework

    From source files (pattern matching):
    - Count "Args:" vs "Parameters\n---" → docstring_style
    - Count "def func(x: type)" patterns → type_hints_usage
    - Measure avg lines per function
    - Measure avg lines per file

    Return compact JSON (under 1000 tokens):
    {
      "detected_conventions": {
        "python_version": ">=3.11",
        "formatter": "black|ruff|none",
        "line_length": NUMBER,
        "testing_framework": "pytest|unittest|nose2",
        "docstring_style": "google|numpy|sphinx",
        "type_hints_usage": "PERCENT%",
        "avg_function_lines": NUMBER,
        "avg_file_lines": NUMBER
      },
      "confidence": {
        "python_version": 0.0-1.0,
        "formatter": 0.0-1.0,
        ...
      },
      "sources": {
        "python_version": "file:location",
        ...
      }
    }

    RULES:
    1. NO raw file contents in response
    2. Use regex/pattern matching only
    3. Keep response under 1000 tokens
    4. Context will be cleared after this
  </parameter>
</invoke>
```

**Agent 2 Response:**

```json
{
  "detected_conventions": {
    "python_version": ">=3.11",
    "formatter": "black",
    "line_length": 88,
    "testing_framework": "pytest",
    "docstring_style": "google",
    "type_hints_usage": "92%",
    "avg_function_lines": 18,
    "avg_file_lines": 183
  },
  "confidence": {
    "python_version": 1.0,
    "formatter": 0.95,
    "line_length": 0.95,
    "testing_framework": 1.0,
    "docstring_style": 0.85,
    "type_hints_usage": 0.9,
    "avg_function_lines": 0.9,
    "avg_file_lines": 0.9
  },
  "sources": {
    "python_version": "pyproject.toml:requires-python",
    "formatter": "pyproject.toml:[tool.black]",
    "line_length": "pyproject.toml:[tool.black].line-length",
    "testing_framework": "requirements.txt:pytest",
    "docstring_style": "src/main.py:pattern_analysis",
    "type_hints_usage": "src/core/processor.py:annotation_count",
    "avg_function_lines": "all_files:measurement",
    "avg_file_lines": "all_files:measurement"
  }
}
```

### Example 2: JavaScript Hinted Detection

**Agent 1 Invocation:**

```xml
<invoke name="Task">
  <parameter name="subagent_type">general-purpose</parameter>
  <parameter name="description">Detect JavaScript conventions from user-specified files</parameter>
  <parameter name="prompt">
    You are Agent 2. Analyze these user-specified JavaScript files.

    Files to analyze:
    1. package.json (user-specified)
    2. tsconfig.json (user-specified)
    3. .prettierrc (user-specified)
    4. src/index.ts (user-specified)
    5. src/utils/helpers.ts (user-specified)

    Extract using pattern matching:

    From package.json:
    - "engines": { "node": "VERSION" } → node_version
    - "scripts": { "test": "jest" } → testing_framework

    From tsconfig.json:
    - "strict": true/false → type_checking

    From .prettierrc:
    - "printWidth": NUMBER → line_length
    - "semi": true/false → semicolons

    From source files:
    - Count JSDoc vs TSDoc → docstring_style
    - Measure function/file sizes

    Return JSON (under 1000 tokens):
    {
      "detected_conventions": {
        "node_version": ">=18.0",
        "testing_framework": "jest|mocha|vitest",
        "type_checking": "strict|loose",
        "line_length": NUMBER,
        "semicolons": true|false,
        "docstring_style": "jsdoc|tsdoc",
        "avg_function_lines": NUMBER
      },
      "confidence": { ... },
      "sources": { ... }
    }

    RULES: NO raw contents, pattern matching only, <1000 tokens
  </parameter>
</invoke>
```

### Example 3: File Write Operation

**Agent 1 Invocation:**

````xml
<invoke name="Task">
  <parameter name="subagent_type">general-purpose</parameter>
  <parameter name="description">Write user-approved policy and profile files</parameter>
  <parameter name="prompt">
    You are Agent 2. Write these YAML files to disk.

    File 1: bmad-core/templates/project-profiles/policies/user-policies/acme-api-coding-v1.yaml
    ```yaml
    policy:
      id: acme-api-coding-v1
      name: "ACME API Coding Standards"
      type: user
      category: code-quality
      protected: false
      created: "2025-10-02T14:30:00Z"
      updated: "2025-10-02T14:30:00Z"

      metadata:
        project_type: brownfield
        detection_method: automatic

    rules:
      philosophy: pragmatic
      max_file_lines: 400
      max_function_lines: 40
      formatter: ruff
      max_line_length: 100
      require_type_hints: true
      docstring_style: google
    ```

    File 2: bmad-core/templates/project-profiles/policies/user-policies/acme-api-security-v1.yaml
    ```yaml
    policy:
      id: acme-api-security-v1
      name: "ACME API Security Policy"
      type: user
      category: security
      protected: false
      created: "2025-10-02T14:30:00Z"
      updated: "2025-10-02T14:30:00Z"

      metadata:
        project_type: brownfield
        detection_method: automatic

    rules:
      security_level: high
      auth_type: jwt
      encryption_at_rest: true
      encryption_in_transit: true
      require_https: true
    ```

    File 3: bmad-core/templates/project-profiles/policies/user-policies/acme-api-testing-v1.yaml
    ```yaml
    policy:
      id: acme-api-testing-v1
      name: "ACME API Testing Standards"
      type: user
      category: testing
      protected: false
      created: "2025-10-02T14:30:00Z"
      updated: "2025-10-02T14:30:00Z"

      metadata:
        project_type: brownfield
        detection_method: automatic

    rules:
      testing_framework: pytest
      min_test_coverage: 80
      require_integration_tests: true
      test_before_merge: true
    ```

    File 4: bmad-core/templates/project-profiles/profiles/acme-api.yaml
    ```yaml
    profile:
      id: acme-api
      name: "ACME API"
      type: user
      protected: false
      created: "2025-10-02T14:30:00Z"
      updated: "2025-10-02T14:30:00Z"

      description: |
        ACME API project profile (brownfield detection)

      metadata:
        project_type: brownfield
        detection_method: automatic

      policies:
        - acme-api-coding-v1
        - acme-api-security-v1
        - acme-api-testing-v1
    ```

    INSTRUCTIONS:
    1. Write each file to specified path
    2. Create parent directories if needed
    3. Handle permissions errors gracefully
    4. Continue on partial failure

    Return JSON:
    {
      "status": "success|error",
      "files_written": NUMBER,
      "files": ["path1", "path2", ...],
      "failed": ["path3"] // if any
    }

    If error:
    {
      "status": "error",
      "message": "description",
      "files_written": NUMBER,
      "files": ["successful paths"],
      "failed": ["failed paths"]
    }
  </parameter>
</invoke>
````

**Agent 2 Success Response:**

```json
{
  "status": "success",
  "files_written": 4,
  "files": [
    "bmad-core/templates/project-profiles/policies/user-policies/acme-api-coding-v1.yaml",
    "bmad-core/templates/project-profiles/policies/user-policies/acme-api-security-v1.yaml",
    "bmad-core/templates/project-profiles/policies/user-policies/acme-api-testing-v1.yaml",
    "bmad-core/templates/project-profiles/profiles/acme-api.yaml"
  ]
}
```

---

## 🎯 Best Practices

### For Agent 1 (UI Handler)

1. **Always validate before delegation:**
   - Check if detection is needed (greenfield vs brownfield)
   - Verify file paths exist before sending to Agent 2
   - Confirm user intent before file writes

2. **Store minimal data:**
   - Keep only extracted values, not raw files
   - Compress user responses
   - Clear temporary data after use

3. **Handle errors gracefully:**
   - Always have fallback to manual input
   - Inform user of retries/recovery
   - Provide clear error messages

4. **Manage directory state:**
   - Track original directory if navigation occurs
   - Offer to return after wizard completion
   - Confirm all navigation changes

### For Agent 2 (File Operations)

1. **Optimize file reads:**
   - Skip large files (>500 lines)
   - Read first 300 lines of source files
   - Skip binary/generated files
   - Use smart sampling

2. **Use efficient extraction:**
   - Pattern matching over AST parsing
   - Count instead of storing
   - Measure metrics, don't save code
   - Compress aggressively

3. **Return structured data:**
   - Always follow JSON schema
   - Include confidence scores
   - Document sources
   - Keep under 1000 tokens

4. **Handle failures:**
   - Continue on partial errors
   - Track successes/failures separately
   - Return detailed status
   - Log error context

### General Guidelines

1. **Token Budget Awareness:**
   - Monitor Agent 1: stay under 50K
   - Monitor Agent 2: stay under 20K per task
   - Target 15-30x compression ratio
   - Reserve buffers for errors

2. **User Experience:**
   - Show confidence scores
   - Allow corrections/overrides
   - Confirm before writes
   - Provide clear progress updates

3. **Error Recovery:**
   - Always have manual fallback
   - Retry with fresh context on overflow
   - Offer alternative paths on permission errors
   - Never lose user data

---

## 📊 Performance Metrics

### Target Metrics

**Compression Ratios:**

- Detection: 15,000 tokens → 500 tokens (30x)
- Write status: 5,000 tokens → 200 tokens (25x)

**Context Usage:**

- Agent 1: <40,000 tokens (80% of budget)
- Agent 2 (detection): <18,000 tokens (90% of budget)
- Agent 2 (write): <15,000 tokens (75% of budget)

**Response Times:**

- Detection task: 10-20 seconds
- Write task: 5-10 seconds
- Total wizard: 2-5 minutes

**Accuracy:**

- Config detection: >95% confidence
- Code pattern detection: >80% confidence
- Overall success rate: >90%

### Monitoring

**Track these metrics:**

1. Token usage per agent per task
2. Compression ratios achieved
3. Detection accuracy by confidence score
4. Error rates and types
5. User correction frequency

**Success Indicators:**

- Agent 1 context <50K at all times
- Agent 2 responses <1K tokens
- <5% context overflow errors
- > 85% detection accuracy
- > 95% write success rate

---

## 🔍 Troubleshooting

### Common Issues

**Issue 1: Context Overflow in Agent 2**

- **Symptom:** Agent 2 fails with "context overflow" error
- **Cause:** Too many/large files being analyzed
- **Solution:** Reduce file count or switch to hinted mode

**Issue 2: Low Detection Confidence**

- **Symptom:** All confidence scores <0.5
- **Cause:** Non-standard project structure or missing config files
- **Solution:** Switch to manual specification mode

**Issue 3: Write Permission Errors**

- **Symptom:** Files fail to write
- **Cause:** Insufficient permissions
- **Solution:** Retry with elevated permissions or alternative path

**Issue 4: Directory Navigation Fails**

- **Symptom:** Invalid path error
- **Cause:** Path doesn't exist or has spaces
- **Solution:** Validate path, use quotes for spaces

**Issue 5: Agent 2 Returns Raw Files**

- **Symptom:** Response >10K tokens
- **Cause:** Agent 2 not following compression rules
- **Solution:** Retry with clearer instructions emphasizing JSON only

---

## 📝 Summary

The multi-agent architecture enables efficient brownfield project detection by:

1. **Separating Concerns:** UI (Agent 1) vs File Operations (Agent 2)
2. **Preserving Context:** Agent 1 stays lean, Agent 2 cleared after tasks
3. **Compressing Data:** 15K+ tokens → 500 token JSON (30x ratio)
4. **Deferring Writes:** No files until user approval
5. **Handling Errors:** Graceful fallbacks and retries

**Key Takeaway:** Agent 1 orchestrates, Agent 2 executes. Data flows via compact JSON only. Context is preserved through intelligent delegation and aggressive compression.

---

**End of Multi-Agent Orchestration Guide**
