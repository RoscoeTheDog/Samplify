# Comments & Documentation

### Comment Density and Style

#### TODO Comments
**Format**: `# TODO(author): Description` with owner

```python
# ✅ GOOD - Include owner for accountability
# TODO(jsmith): Add error handling for network timeouts
# TODO(alee): Optimize this query - currently O(n²)
# TODO(bob): Remove this after migration to v2 API

# Easy to search
# git grep "TODO(jsmith)"
```

**Rationale**: Clear accountability, searchable, standard in Google/major projects.

**Avoid dates inline** - they become stale. Use issue trackers for time-tracking.

#### FIXME/HACK Comments
**Pattern**: Prefer issue tracker, minimal inline comments

```python
# ✅ For production code - create tickets, minimal inline markers
# FIXME: Memory leak in batch processing - see issue #1234
# HACK: Workaround for Django bug #32123 - remove after Django 5.0

# ✅ Better - Use issue tracker and link
# See issue #1234 for memory leak details

# ✅ Inline OK for temporary workarounds
# HACK: API returns invalid JSON on empty results
# Workaround until v2 API is deployed
if response == "":
    response = "[]"
```

**Standard tags**:
- **FIXME**: Known bugs that need fixing
- **HACK**: Workarounds for external issues (library bugs, API limitations)
- **XXX**: Less common, some teams use for warnings

**Rationale**: TODOs/FIXMEs proliferate and become noise, no tracking/visibility, get outdated.

**Keep it minimal** - if explanation is >2 lines, create a ticket and link it.

#### Algorithm Complexity Comments
**Pattern**: Only for complex algorithms (O(n²) or worse)

```python
# ✅ Include for non-obvious complexity
def find_duplicates(items: List[str]) -> List[str]:
    """Find duplicate items in list.

    Note: O(n²) complexity - consider optimization for large lists.
    """
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items[i+1:]):
            if item == other:
                duplicates.append(item)
    return duplicates


# ✅ Include for optimized solutions
def find_duplicates_fast(items: List[str]) -> List[str]:
    """Find duplicate items using set lookup.

    Complexity: O(n) time, O(n) space
    """
    seen = set()
    duplicates = []
    for item in items:
        if item in seen:
            duplicates.append(item)
        seen.add(item)
    return duplicates


# ❌ Don't include for obvious cases
def sum_list(numbers: List[int]) -> int:
    """Sum all numbers in list."""
    # No need to say "O(n)" - it's obvious
    return sum(numbers)
```

**When to include**:
- Non-obvious complexity (quadratic, exponential)
- Performance-critical code
- Explicit trade-offs (space vs time)
- Counterintuitive complexity

**Where to put it**:
- Docstring for overall function complexity
- Inline comment for specific section if needed

#### Magic Number Explanations
**Pattern**: Named constant with comment explaining origin

```python
# ✅ GOOD - Named constant with context
# Based on RFC 2616 - standard HTTP timeout recommendation
HTTP_TIMEOUT_SECONDS = 30

# Determined from production metrics (95th percentile response time)
API_TIMEOUT_SECONDS = 45

# Maximum file size for free tier (product requirement)
MAX_FILE_SIZE_MB = 10


def fetch_data(url: str) -> dict:
    response = requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)
    return response.json()


# ✅ Explains WHY the value
RETRY_ATTEMPTS = 3  # Balances reliability vs latency - tested in prod

# ❌ Redundant comment
RETRY_ATTEMPTS = 3  # Number of retry attempts (obvious!)

# ✅ Self-documenting, no comment needed
MAX_LOGIN_ATTEMPTS = 3
```

**Comment should explain**:
- Origin (where the number comes from)
- Rationale (why this specific value)
- Constraints (business rules, external requirements)
- Trade-offs (why not higher/lower)

#### Commented-Out Code
**Pattern**: Never commit commented-out code

```python
# ❌ NEVER DO THIS
def process_data(data: dict) -> dict:
    # Old implementation - keeping just in case
    # result = old_process(data)
    # if result:
    #     return transform(result)

    # New implementation
    return new_process(data)


# ✅ DO THIS - Just delete it
def process_data(data: dict) -> dict:
    return new_process(data)

# If you need the old code: git log, git blame, git show
```

**Why never commit commented code**:
- Creates confusion ("should I uncomment this?")
- Makes code harder to read
- Git history exists for this purpose
- Rots quickly (becomes outdated)
- False sense of safety (usually never used again)

**Extremely rare exception** - Educational context:

```python
# ✅ Acceptable: Showing what NOT to do
def secure_query(user_id: int) -> dict:
    # DON'T DO THIS - security vulnerability
    # query = f"SELECT * FROM users WHERE id = {user_id}"

    # DO THIS - use parameterized queries
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,)).fetchone()
```

---

### Docstring Standards

#### Type Hints in Docstrings
**Pattern**: No duplication - types in signature, descriptions in docstring

```python
# ✅ GOOD - Type hints in signature, descriptions in docstring
def process_file(path: str, max_size: int = 1024) -> Dict[str, Any]:
    """Process a file and return parsed data.

    Args:
        path: Path to the file to process
        max_size: Maximum file size in bytes

    Returns:
        Dictionary containing parsed file data with 'content' and 'metadata' keys
    """
    pass


# ❌ REDUNDANT - Don't duplicate types
def process_file(path: str, max_size: int = 1024) -> Dict[str, Any]:
    """Process a file and return parsed data.

    Args:
        path (str): Path to the file to process  # Redundant!
        max_size (int): Maximum file size in bytes  # Redundant!

    Returns:
        dict[str, Any]: Dictionary containing...  # Redundant!
    """
    pass
```

**Exception** - Complex types that need explanation:

```python
# ✅ OK - Explanation adds value
def transform_data(
    data: Dict[str, List[Tuple[int, str]]]
) -> List[ProcessedItem]:
    """Transform nested data structure.

    Args:
        data: Mapping of category names to lists of (id, value) tuples.
              Example: {"users": [(1, "alice"), (2, "bob")]}

    Returns:
        List of ProcessedItem objects, one per tuple in input
    """
    pass
```

**Rationale**: DRY principle, type hints are tool-checked, docstrings get out of sync.

#### Default Values in Docstrings
**Pattern**: Include only when default behavior is complex

```python
# ✅ No need to mention simple defaults
def fetch_data(url: str, timeout: int = 30) -> dict:
    """Fetch data from URL.

    Args:
        url: URL to fetch from
        timeout: Request timeout in seconds
    """
    pass


# ✅ Explain complex/non-obvious defaults
def process_batch(
    items: List,
    batch_size: Optional[int] = None,
    retry_failed: bool = True
) -> List:
    """Process items in batches.

    Args:
        items: Items to process
        batch_size: Items per batch. Defaults to CPU count * 2 if not specified
        retry_failed: Whether to retry failed items. Defaults to True for
                     production; automatically set to False in test environments
    """
    pass


# ✅ Explain when None has special meaning
def save_file(path: str, data: bytes, mode: Optional[str] = None) -> None:
    """Save data to file.

    Args:
        path: Destination path
        data: Data to write
        mode: File mode. If None (default), automatically determined from
              file extension ('.gz' uses gzip compression, etc.)
    """
    pass
```

**When to include defaults**:
- Default value has special meaning beyond the literal value
- Default behavior is computed/dynamic
- Understanding the default is important for correct usage

#### Side Effects Documentation
**Pattern**: Only if side effects are non-obvious

```python
# ✅ Document non-obvious side effects
def update_user(user_id: int, data: dict) -> User:
    """Update user information.

    Args:
        user_id: ID of user to update
        data: Fields to update

    Returns:
        Updated user object

    Note:
        Sends email notification to user and logs audit trail to database.
        Invalidates all active sessions for this user.
    """
    pass


# ❌ Don't document obvious side effects
def save_to_database(obj: Model) -> None:
    """Save object to database.

    Side effects:  # REDUNDANT - obvious from function name!
        Writes to database
    """
    pass


# ✅ Good - side effects are clear from description
def delete_user(user_id: int) -> None:
    """Delete user and all associated data.

    Permanently removes user account, posts, comments, and uploaded files.
    This operation cannot be undone.

    Warning:
        This cascades to related records. Use with caution.
    """
    pass
```

**Document side effects when**:
- External systems affected (emails, APIs, queues)
- Database modifications beyond the obvious
- File system changes
- Global state mutations
- Cache invalidations
- Async operations triggered

**Use appropriate sections**:
- **Note**: for important side effects
- **Warning**: for dangerous side effects
- Main description if side effects are the primary purpose

#### Performance Characteristics
**Pattern**: In "Note:" section when relevant

```python
# ✅ Include for performance-critical or non-obvious complexity
def find_shortest_path(graph: Graph, start: Node, end: Node) -> List[Node]:
    """Find shortest path between nodes using Dijkstra's algorithm.

    Args:
        graph: Graph to search
        start: Starting node
        end: Destination node

    Returns:
        List of nodes representing shortest path

    Note:
        Time complexity: O(E + V log V) where E is edges, V is vertices.
        Space complexity: O(V) for priority queue.
        For graphs with >10k nodes, consider using A* algorithm instead.
    """
    pass


# ❌ Don't include for obvious operations
def get_user_by_id(user_id: int) -> User:
    """Retrieve user by ID.

    Note:
        O(1) lookup using primary key  # OBVIOUS - don't include
    """
    pass


# ✅ Include performance warnings
def calculate_similarity(items: List[str]) -> dict:
    """Calculate pairwise similarity between all items.

    Warning:
        O(n²) complexity. Not suitable for >1000 items.
        Use approximate_similarity() for large datasets.
    """
    pass
```

**When to document performance**:
- Non-obvious complexity (O(n²) or worse)
- Performance-critical code paths
- Operations that don't scale well
- When there's a better alternative for large inputs
- Memory usage concerns

**Where to put it**:
- **Note**: for informational complexity
- **Warning**: for performance pitfalls
- Docstring description if performance is key characteristic

#### Related Functions/Classes Cross-Reference
**Pattern**: In description only when directly related

```python
# ✅ Natural mentions in description
def encode_message(message: str, key: str) -> bytes:
    """Encode message with encryption key.

    Use decode_message() to reverse this operation.
    For bulk operations, see encode_messages_batch().
    """
    pass


# ✅ See Also for genuine alternatives/related functionality
def quicksort(items: List) -> List:
    """Sort items using quicksort algorithm.

    Args:
        items: List to sort

    Returns:
        Sorted list

    See Also:
        mergesort: More stable but slower for small lists
        heapsort: Better worst-case complexity O(n log n)
        timsort: Python's built-in sort (usually fastest)
    """
    pass


# ❌ Don't over-document relationships
def save_user(user: User) -> None:
    """Save user to database.

    See Also:  # TOO MUCH - becomes noise
        get_user: Retrieve user
        delete_user: Delete user
        update_user: Update user
        User: User model class
        UserSerializer: User serialization
    """
    pass


# ✅ Minimal - only when helpful
def calculate_tax(amount: Decimal, rate: Decimal) -> Decimal:
    """Calculate tax on amount.

    For tax-inclusive calculations, use calculate_tax_inclusive() instead.
    """
    pass
```

**When to cross-reference**:
- Direct alternatives (different algorithms for same task)
- Inverse operations (encode/decode, serialize/deserialize)
- Related operations users might need next
- Common confusions ("use X instead of Y for Z")

**When NOT to cross-reference**:
- Standard CRUD operations on same model (too obvious)
- Every function that touches same data
- Parent/child class relationships (use inheritance docs)
- Anything the IDE "find usages" shows easily

---
