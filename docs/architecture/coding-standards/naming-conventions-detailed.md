# Naming Conventions (Detailed)

### Variable Naming

#### Boolean Variables
**Pattern**: Use prefix that reads like a natural question

```python
# ✅ State checks - is_ prefix
is_valid = check_validation(data)
is_active = user.status == "active"
is_empty = len(items) == 0

# ✅ Possession/existence - has_ prefix
has_permission = user.check_permission("edit")
has_errors = len(error_list) > 0
has_children = len(node.children) > 0

# ✅ Ability/capability - can_ prefix
can_process = is_valid and has_permission
can_delete = user.is_admin or user.is_owner
can_access = check_access_rights()

# ❌ AVOID - check_ prefix (too vague, doesn't indicate boolean)
check_valid = validate(data)  # Unclear if boolean or function call
```

**Rule**: The prefix should make it read like a natural question: "Is it valid?", "Has permission?", "Can process?"

#### Counter/Index Variables
**Pattern**: Always use descriptive names

```python
# ✅ GOOD - Descriptive names
for file_index in range(len(files)):
    process_file(files[file_index], position=file_index)

worker_count = multiprocessing.cpu_count()
iteration_number = 0

# ❌ AVOID - Single letter variables
for i in range(len(files)):  # What does i represent?
    process_file(files[i], position=i)
```

**Exception**: Single letters acceptable in mathematics/algorithms where conventional (i, j, k for loops in academic contexts).

#### Collection Variables
**Pattern**: Suffix with type for clarity

```python
# ✅ GOOD - Type-suffixed collections
file_list: List[File] = []
transformation_queue: Deque[Transform] = deque()
result_dict: Dict[str, Any] = {}
error_set: Set[str] = set()

# ❌ AVOID - Plural without type (ambiguous)
files = []  # List? Set? Tuple?
transformations = deque()  # Not clear it's a queue
```

**Rationale**: Type suffix makes collection type explicit, especially important when type isn't obvious from context.

#### Temporary Variables
**Pattern**: Use short names in small scopes, make outer scope specific if shadowing

```python
# ✅ GOOD - Short names in small scopes
def process_data(input_data):
    result = transform(input_data)
    output = format_result(result)
    return output

# ✅ GOOD - Contextual prefixes when shadowing
def process_files(file_list):
    total_size = 0
    for file_item in file_list:  # Avoid shadowing "file" builtin
        file_size = file_item.stat().st_size
        total_size += file_size

# ✅ GOOD - Outer scope more specific if inner scope shadows
def batch_process(input_file_list):
    for input_file in input_file_list:
        # Inner scope uses simple "file"
        with open(input_file) as file:
            data = file.read()
```

#### Constants
**Pattern**: SCREAMING_SNAKE_CASE for all constants

```python
# ✅ GOOD - All constants
MAX_WORKERS = 8
DEFAULT_TIMEOUT_SECONDS = 30
API_ENDPOINT = "https://api.example.com"
ALLOWED_EXTENSIONS = [".wav", ".mp3", ".flac"]

# Configuration constants
RETRY_ATTEMPTS = 3
BATCH_SIZE = 100
```

---

### Function Naming

#### Action Functions
**Pattern**: Mixed approach based on action type

```python
# ✅ Verb-Noun for transformations
def validate_input(data):
    pass

def parse_template(xml_string):
    pass

def transform_audio(input_path, output_format):
    pass

# ✅ Strong verbs for processes
def process_files(file_list):
    pass

def execute_query(sql):
    pass

# ✅ Get/Set for simple property access
def get_status():
    return self._status

def set_timeout(seconds):
    self._timeout = seconds
```

#### Query/Lookup Functions
**Pattern**: Context-dependent with clear semantics

```python
# ✅ get_ - Direct access, expected to exist (raises if not found)
def get_user_by_id(user_id: int) -> User:
    """Get user by ID. Raises UserNotFoundError if not found."""
    user = User.objects.get(id=user_id)
    return user

def get_config(key: str) -> str:
    """Get configuration value. Raises KeyError if not found."""
    return settings.CONFIG[key]

# ✅ find_ - Search operation, may not exist (returns None)
def find_user_by_email(email: str) -> Optional[User]:
    """Find user by email. Returns None if not found."""
    return User.objects.filter(email=email).first()

def find_first_match(pattern: str, items: List[str]) -> Optional[str]:
    """Find first item matching pattern. Returns None if no match."""
    for item in items:
        if re.match(pattern, item):
            return item
    return None

# ✅ fetch_ - Remote/database retrieval, implies I/O operation
def fetch_from_api(endpoint: str) -> dict:
    """Fetch data from API endpoint."""
    response = requests.get(endpoint)
    return response.json()

def fetch_from_database(query: str) -> List[dict]:
    """Fetch records from database."""
    return db.execute(query).fetchall()

# ✅ retrieve_ - Less common, formal variant of fetch
def retrieve_archived_data(archive_id: str) -> bytes:
    """Retrieve data from archive storage."""
    pass
```

**Semantic Distinctions**:
- **get_**: Expected to exist, raises exception if not found
- **find_**: Search that may fail, returns None/empty
- **fetch_**: I/O operation (network, database, file)
- **retrieve_**: Formal/archive retrieval operation

#### Boolean-Returning Functions
**Pattern**: Match the question (is/has/can)

```python
# ✅ is_ - State/property check
def is_valid(data: dict) -> bool:
    return all(key in data for key in REQUIRED_KEYS)

def is_active(user: User) -> bool:
    return user.status == "active"

def is_empty(collection: List) -> bool:
    return len(collection) == 0

# ✅ has_ - Possession/existence
def has_permission(user: User, permission: str) -> bool:
    return permission in user.permissions

def has_errors(result: dict) -> bool:
    return "errors" in result and len(result["errors"]) > 0

def has_children(node: TreeNode) -> bool:
    return len(node.children) > 0

# ✅ can_ - Ability/permission
def can_process(file: File) -> bool:
    return file.is_valid and file.has_permissions

def can_delete(user: User, resource: Resource) -> bool:
    return user.is_admin or resource.owner_id == user.id

def can_access(user: User, resource: Resource) -> bool:
    return user.has_role("viewer") or user.has_role("editor")

# ❌ AVOID - check_ prefix (too vague, doesn't indicate boolean return)
def check_valid(data):  # Returns bool? Raises exception? Returns errors?
    pass
```

**Rule**: Prefix should make it read like a natural question.

#### Private/Internal Functions
**Pattern**: Single underscore prefix (Python standard)

```python
# ✅ Private/internal functions
def _internal_helper():
    """Private helper function."""
    pass

def _calculate_hash(data: bytes) -> str:
    """Internal hash calculation."""
    pass

# ✅ Name mangling for very private (rare, special cases)
def __very_private():
    """Name-mangled private method."""
    pass

# ✅ Public API
def public_function():
    """Public interface function."""
    result = _internal_helper()
    return result
```

**Rationale**:
- PEP 8 language convention
- IDE/tooling support
- Import behavior (`from module import *` excludes `_` prefixed)
- Clear visual indicator

#### Helper/Utility Functions
**Pattern**: Good descriptive names, no special prefix

```python
# ✅ GOOD - Descriptive names, private if internal
def process_batch():
    data = _parse_xml(xml_string)  # Private helper
    return _transform_data(data)   # Private helper

def _parse_xml(xml_string: str) -> dict:
    """Parse XML string to dictionary."""
    pass

def _transform_data(data: dict) -> list:
    """Transform data structure."""
    pass

# ✅ GOOD - Utils module organization
from utils.xml import parse_xml  # Module organization, not naming
from utils.validation import validate_schema

# ❌ AVOID - Redundant prefixes
def _helper_parse_xml():  # "helper" adds no information
    pass

def util_parse_xml():  # "util" prefix is noise
    pass
```

**Better organization**:
- Make them private with `_` if internal to module
- Group in dedicated modules (`utils/`, `helpers/`) by functionality
- Use clear descriptive names that explain what they do

---

### Class and Module Naming

#### Class Names
**Pattern**: PascalCase, no type suffixes (except design patterns)

```python
# ✅ GOOD - Clean PascalCase
class FileProcessor:
    pass

class SchemaManager:
    pass

class UserRepository:
    pass

class AudioConverter:
    pass

# ❌ AVOID - Redundant type suffixes
class FileProcessorService:  # "Service" is redundant
    pass

class SchemaManagerHandler:  # "Handler" is redundant
    pass

class UserRepositoryClass:  # "Class" is redundant
    pass

# ✅ EXCEPTION - Design pattern names add clarity
class UserFactory:  # Factory pattern
    pass

class CommandBuilder:  # Builder pattern
    pass

class ObserverAdapter:  # Adapter pattern
    pass
```

**Rationale**: Code structure already shows it's a class, avoid redundancy.

#### Module Names
**Pattern**: Context-dependent (primarily snake_case singular)

```python
# ✅ Singular when module contains one main class/concept
file_processor.py      # Contains FileProcessor class
schema_manager.py      # Contains SchemaManager class
audio_converter.py     # Contains AudioConverter class

# ✅ Plural when module contains collections/utilities
utils.py              # Various utility functions
constants.py          # Multiple constants
exceptions.py         # Multiple exception classes
models.py             # Multiple model classes
handlers.py           # Multiple handler classes
```

**Standard Python convention (PEP 8)**:
- Always `snake_case` (never PascalCase for modules)
- Short, all-lowercase
- Singular for single-purpose modules
- Plural for collections

#### Django App Names
**Pattern**: Plural nouns (Django community standard)

```python
# ✅ GOOD - Plural (matches Django's own apps)
apps/
├── users/           # Not user/
├── schemas/         # Not schema/
├── files/           # Not file/
├── payments/        # Not payment/
└── notifications/   # Not notification/

# ✅ EXCEPTION - Singular for services/features
apps/
├── authentication/  # A service, not a collection
├── billing/         # A service
├── search/          # A feature/service
```

**Rationale**:
- Matches Django's own apps (admin, auth, contenttypes, sessions)
- Apps typically handle multiple instances
- Reads naturally: "the users app", "the payments app"
- Overwhelming community convention

---
