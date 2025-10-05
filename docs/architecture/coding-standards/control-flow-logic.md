# Control Flow & Logic

### Conditional Logic

#### Complex Boolean Expressions
**Pattern**: Multi-line with parentheses (Black/PEP 8 standard)

```python
# ✅ BEST - Multi-line with parentheses
if (
    user.is_active
    and user.has_permission('edit')
    and not user.is_locked
):
    process_edit()

# ✅ Also good for longer expressions
if (
    user.is_active
    and user.has_permission('edit')
    and not user.is_locked
    and user.email_verified
    and user.account_age_days > 30
):
    grant_advanced_access()

# ❌ AVOID - Inline (hard to read when long)
if (user.is_active and user.has_permission('edit') and not user.is_locked):
    pass

# ❌ AVOID - Backslash (fragile, easy to break)
if user.is_active and \
   user.has_permission('edit') and \
   not user.is_locked:
    pass
```

**When to use intermediate variables** - For complex/reusable logic:

```python
# ✅ Use variables for reusable logic
can_edit = (
    user.is_active
    and user.has_permission('edit')
    and not user.is_locked
)
can_delete = (
    user.is_active
    and user.has_permission('delete')
    and not user.is_locked
)

if can_edit:
    edit_item()

if can_delete:
    delete_item()

# ✅ When condition needs explanation
# User can proceed if they're active and verified, or if they're an admin
can_proceed = (
    (user.is_active and user.is_verified)
    or user.is_admin
)
if can_proceed:
    grant_access()
```

**Benefits**:
- No backslashes needed (cleaner)
- Easy to add/remove conditions
- Git diffs are cleaner (one condition per line)
- Each condition stands out clearly
- Black/autopep8 formats this way automatically

#### Guard Clauses vs Nested Ifs
**Pattern**: Guard clauses (early returns) - overwhelming preference

```python
# ✅ BEST - Guard clauses
def process_file(file_path: Path) -> Optional[dict]:
    if not file_path.exists():
        return None

    if not is_valid_format(file_path):
        return None

    if file_path.stat().st_size > MAX_SIZE:
        return None

    # Main logic is not nested - easy to read
    data = read_file(file_path)
    result = transform(data)
    return result


# ❌ AVOID - Arrow anti-pattern (nested ifs)
def process_file(file_path: Path) -> Optional[dict]:
    if file_path.exists():
        if is_valid_format(file_path):
            if file_path.stat().st_size <= MAX_SIZE:
                # Main logic buried 3 levels deep
                data = read_file(file_path)
                result = transform(data)
                return result
    return None
```

**Standard pattern**:

```python
def process_request(request: Request) -> dict:
    # All validation/guard clauses first
    if not request:
        raise ValueError("Request required")

    if not request.user:
        raise AuthenticationError("User not authenticated")

    if not request.user.has_permission('access'):
        raise PermissionError("Access denied")

    # Main logic - completely unnested
    data = fetch_data(request)
    result = process_data(data)
    return result
```

**Benefits**:
- Reduces nesting (main logic at top level)
- Fail fast (invalid cases exit immediately)
- Easier to read (validation separate from logic)
- Easier to modify (add/remove guards without restructuring)
- Clearer intent ("these are prerequisites")

#### Ternary Operators
**Pattern**: OK when it improves readability

```python
# ✅ GOOD - Simple, clear assignments
status = "active" if user.is_active else "inactive"
color = "green" if score > 80 else "red"
value = x if x is not None else default

# ✅ GOOD - Simple return values
def get_label(count: int) -> str:
    return "item" if count == 1 else "items"

# ✅ GOOD - Short conditional argument
logger.log(message, level="DEBUG" if settings.DEBUG else "INFO")


# ❌ AVOID - Nested ternaries (confusing)
value = "high" if x > 100 else "medium" if x > 50 else "low"  # Hard to read

# ✅ BETTER - Explicit if/elif/else
if x > 100:
    value = "high"
elif x > 50:
    value = "medium"
else:
    value = "low"


# ❌ AVOID - Complex expressions
result = (
    process_data(x) if validate(x) and check_permission() else fallback_process(x)
)  # Too complex

# ✅ BETTER - Explicit if/else
if validate(x) and check_permission():
    result = process_data(x)
else:
    result = fallback_process(x)
```

**Guidelines**:
- **Use ternary for**: Simple variable assignment or return values
- **Must fit comfortably on one line** (< 79 characters)
- **Avoid**: Nested ternaries, complex expressions, side effects
- **Ask**: "Is this easier to read than if/else?" If no, use if/else

#### Short-Circuit Evaluation
**Pattern**: Rely on it (it's a feature, not a bug)

```python
# ✅ GOOD - Idiomatic Python (short-circuit)
if user and user.is_active:
    process(user)

if items and len(items) > 0:
    process_items(items)

if config.get('enabled') and config['timeout'] > 0:
    start_service()


# ❌ VERBOSE - Unnecessarily explicit
if user is not None:
    if user.is_active:
        process(user)

# ❌ VERBOSE
if items is not None:
    if len(items) > 0:
        process_items(items)
```

**More examples**:

```python
# ✅ Common patterns
value = user.name if user else "Anonymous"
result = cache.get(key) or compute_expensive_value()
output = data or []  # Ensure list even if None

# ✅ Safe attribute access
email = user and user.email  # None if user is None, else user.email

# ✅ Validation chains
if request and request.user and request.user.is_authenticated:
    grant_access()
```

**Why rely on short-circuit**:
- **Idiomatic Python** - expected by Python developers
- **Concise and readable** - less nesting
- **Prevents errors** - `user and user.is_active` won't raise AttributeError
- **Well-defined behavior** - Python guarantees left-to-right evaluation
- **Standard in all modern languages** (JavaScript, Java, Go, Rust, etc.)

**When to be explicit**:

```python
# ✅ When None is a valid value distinct from False
if value is not None:  # Not just "if value"
    process(value)  # 0, False, "" are valid

# ✅ When checking type explicitly
if isinstance(data, list):
    process_list(data)
```

---

### Loop and Iteration

#### For Loops vs Comprehensions
**Pattern**: Comprehensions for simple transforms, loops for complex logic

```python
# ✅ GOOD - Comprehensions for simple transforms
squares = [x**2 for x in numbers]
active_users = [u for u in users if u.is_active]
names = [user.name.upper() for user in users]

# ✅ GOOD - Loops for complex logic
results = []
for user in users:
    # Multiple statements, complex logic
    if not user.is_active:
        continue

    profile = fetch_profile(user.id)
    if profile and profile.is_verified:
        result = process_user(user, profile)
        results.append(result)
        logger.info(f"Processed {user.name}")

# ❌ AVOID - Complex comprehension (hard to read)
results = [
    process_user(user, profile)
    for user in users
    if user.is_active
    for profile in [fetch_profile(user.id)]
    if profile and profile.is_verified
]  # Too complex!

# ✅ GOOD - Dict/set comprehensions for simple transforms
user_map = {user.id: user.name for user in users}
unique_emails = {user.email.lower() for user in users}
```

**Rule of thumb**:
- **Use comprehension if**: Single expression, fits comfortably on 1-3 lines
- **Use loop if**: Multiple statements, complex conditions, side effects (logging, I/O)
- **If unsure**: Use a loop (easier to debug and modify later)

#### Nested Comprehensions
**Pattern**: Max 2 levels, only if clear and simple

```python
# ✅ OK - Simple 2-level nesting, clear intent
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [x for row in matrix for x in row]
# Result: [1, 2, 3, 4, 5, 6, 7, 8, 9]

doubled = [[x * 2 for x in row] for row in matrix]
# Result: [[2, 4, 6], [8, 10, 12], [14, 16, 18]]


# ✅ OK - 2D transformation that's easy to understand
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]


# ❌ AVOID - Too complex (3+ levels or complex conditions)
result = [
    [
        [z * 2 for z in y if z > 0]
        for y in x if len(y) > 2
    ]
    for x in data if x
]  # What does this even do?

# ✅ BETTER - Explicit loops
result = []
for x in data:
    if not x:
        continue
    x_result = []
    for y in x:
        if len(y) <= 2:
            continue
        y_result = [z * 2 for z in y if z > 0]
        x_result.append(y_result)
    result.append(x_result)
```

**Guidelines**:
- **Max 2 levels** of nesting in comprehensions
- **Must be immediately clear** what it's doing
- **No complex filters** in nested comprehensions
- **When in doubt, use explicit loops**

**Common acceptable patterns**:

```python
# ✅ Flatten 2D list
flat = [item for sublist in nested_list for item in sublist]

# ✅ Cartesian product
pairs = [(x, y) for x in list1 for y in list2]

# ✅ 2D transformation
processed = [[func(x) for x in row] for row in matrix]
```

#### Generator Expressions vs List Comprehensions
**Pattern**: Lists for small/reusable, generators for large/single-pass

```python
# ✅ List comprehension - Small, need multiple passes
user_ids = [u.id for u in users]  # ~100s of users
if user_ids:
    print(f"Found {len(user_ids)} users")  # Need length
    process_batch(user_ids)  # Use multiple times

# ✅ Generator - Large data or single pass
# Reading large file
lines = (line.strip() for line in open('huge_file.txt'))
for line in lines:
    process(line)  # Use once, don't load all into memory

# ✅ Generator - Potentially infinite
fibonacci = (fib(n) for n in itertools.count())

# ✅ Generator - Chain of transformations
numbers = (int(x) for x in file)
squares = (x**2 for x in numbers)
evens = (x for x in squares if x % 2 == 0)
result = sum(evens)  # Memory efficient pipeline


# ✅ List - Need to use multiple times or check length
results = [expensive_operation(x) for x in items]
print(f"Got {len(results)} results")  # Need length
for r in results:
    process(r)
for r in results:  # Reuse
    validate(r)

# ❌ WASTEFUL - List when only used once
total = sum([x**2 for x in range(1000000)])  # Creates huge list!

# ✅ BETTER - Generator
total = sum(x**2 for x in range(1000000))  # Memory efficient
```

**Decision tree**:
1. **Multiple passes or need `len()`?** → List comprehension
2. **Large data (>10k items)?** → Generator
3. **Single iteration?** → Generator
4. **Small data (<100 items)?** → List is fine (negligible difference)
5. **Passed to function expecting iterable?** → Check if function consumes once (generator) or multiple times (list)

**Note**: `sum()`, `max()`, `min()`, `any()`, `all()` work with generators - use them!

#### enumerate() vs Manual Counter
**Pattern**: Always use enumerate()

```python
# ✅ ALWAYS USE enumerate()
for index, item in enumerate(items):
    print(f"{index}: {item}")

# Start at 1 instead of 0
for number, item in enumerate(items, start=1):
    print(f"{number}. {item}")

# With both index and value
for i, user in enumerate(users):
    if i == 0:
        print(f"First user: {user.name}")
    process(user, position=i)


# ❌ NEVER DO THIS - Manual counter (error-prone, not Pythonic)
index = 0
for item in items:
    print(f"{index}: {item}")
    index += 1  # Easy to forget, can cause bugs


# ❌ ALSO AVOID - Range indexing when you need the value
for i in range(len(items)):
    print(f"{i}: {items[i]}")  # Unnecessary indexing

# ✅ BETTER
for i, item in enumerate(items):
    print(f"{i}: {item}")
```

**Why enumerate() is better**:
- **More Pythonic** - idiomatic Python
- **Less error-prone** - no forgetting to increment
- **More readable** - clear intent
- **Works with any iterable** - not just lists
- **Can't forget to increment** - eliminates whole class of bugs

#### Loop Else Clause
**Pattern**: Avoid; if used, require clear comment

```python
# ✅ ACCEPTABLE - With clear comment explaining else
for item in items:
    if item.matches(criteria):
        result = item
        break
else:
    # No break occurred - no matching item found
    result = None

# ✅ BETTER - More explicit (preferred by most teams)
result = None
for item in items:
    if item.matches(criteria):
        result = item
        break

if result is None:
    handle_no_match()


# ✅ BEST - Use built-in function when available
result = next((item for item in items if item.matches(criteria)), None)
if result is None:
    handle_no_match()
```

**Why it's controversial**:
- **Confusing**: "else" implies "if didn't execute", but it means "if didn't break"
- **Non-obvious**: Most developers don't expect it
- **Rare**: Not commonly used in production code
- **Alternatives are clearer**: Setting flag or using early return

**Community opinion**: Most Python style guides **discourage loop-else** or require comments.

---
