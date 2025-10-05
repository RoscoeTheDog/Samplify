# Logging & Debugging

### Logging Preferences (Enhanced Loguru)

#### Log Levels
**Extended Loguru levels**:

- **TRACE**: Fine-grained debugging (loop iterations, variable states)
- **DEBUG**: Diagnostic info; automatic with function tracing
- **INFO**: General messages; smart context styling auto-highlights
- **SUCCESS**: Operation completion (Loguru-specific)
- **WARNING**: Potential issues
- **ERROR**: Operation failures; exception hooks provide beautiful tracebacks
- **CRITICAL**: System failures; triggers comprehensive diagnostics

#### Log Message Format
**Pattern**: Structured with bind() + template system

```python
from loguru import logger

# ✅ Structured with bind() + smart context styling
logger.bind(
    file_path=file_path,
    schema_id=schema_id,
    user_id=user.id
).info("File processing started")


# ✅ Configure dual streams
logger.configure_streams(
    console=dict(template="beautiful", level="INFO"),
    file=dict(sink="app.log", template="minimal", level="DEBUG"),
    json=dict(sink="data.jsonl", serialize=True)
)
```

#### Exception Logging
**Pattern**: Use exception hooks + context-aware logging

```python
from loguru import logger
from loguru._exception_hook import install_exception_hook

# ✅ Install global exception hook
install_exception_hook(logger, template="beautiful")


# ✅ Use @logger.catch for automatic exception handling
@logger.catch
def process_file(file_path):
    # Any exception automatically logged with beautiful formatting
    data = parse_audio(file_path)
    return transform(data)
```

#### Sensitive Data in Logs
**Pattern**: Smart masking with custom patterns

```python
def mask_email(email):
    username, domain = email.split('@')
    return f"{username[0]}***@{domain}"

logger.bind(
    user_email=mask_email(user.email),
    user_id=user.id
).info("User action performed")
```

#### Log Statement Density
**Pattern**: Use function tracing instead of manual entry/exit logs

```python
from loguru._tracing import FunctionTracer

tracer = FunctionTracer(logger, "beautiful")

@tracer.trace
def process_audio_pipeline(file_path, schema_id):
    # Entry/exit automatically logged!
    audio_data = load_audio(file_path)
    return apply_transformations(audio_data, schema_id)
```

#### Advanced Function Tracing
**Pattern**: Use performance and development tracers with rule-based configuration

```python
from loguru._tracing import FunctionTracer, PerformanceTracer

# ✅ Configure tracing rules by pattern
tracer = FunctionTracer(logger, "beautiful")

tracer.add_rule(
    pattern=r"^process_.*",  # All process_* functions
    log_args=True,
    log_result=True,
    log_duration=True,
    level="DEBUG"
)

tracer.add_rule(
    pattern=r"^_.*",  # Private functions
    enabled=False  # Don't trace
)

# ✅ Performance monitoring with thresholds
perf_tracer = PerformanceTracer(logger)

@perf_tracer.trace_performance(threshold_ms=500)
def slow_operation():
    # Automatic alert if > 500ms
    time.sleep(0.6)
    return "result"

# Get performance statistics
stats = perf_tracer.get_performance_stats("slow_operation")

# ✅ Development vs Production tracers
from loguru._tracing import create_development_tracer, create_production_tracer

if settings.DEBUG:
    tracer = create_development_tracer(logger)  # Verbose
else:
    tracer = create_production_tracer(logger)  # Minimal
```

#### Global Exception Hooks
**Pattern**: Beautiful exception formatting for all unhandled exceptions

```python
from loguru._exception_hook import install_exception_hook, ExceptionContext

# ✅ Install global exception hook
hook = install_exception_hook(logger, template="beautiful")

# Now all unhandled exceptions are beautifully formatted
def risky_function():
    return 1 / 0  # Caught and styled automatically

# ✅ Temporary exception hooks for code blocks
with ExceptionContext(logger, "beautiful") as ctx:
    risky_operation()
    another_risky_operation()
# Hook automatically removed when exiting

# ✅ Development hook with enhanced context
from loguru._exception_hook import create_development_hook

dev_hook = create_development_hook(logger)
dev_hook.install()
# Captures local variables, provides rich debugging context

# ✅ Thread exception handling
# Exception hooks automatically capture exceptions from all threads
import threading

def background_task():
    raise ValueError("Background error")  # Automatically caught and logged

thread = threading.Thread(target=background_task)
thread.start()
```

#### Log Analysis and Monitoring
**Pattern**: Use built-in analysis tools for health checks and debugging

```python
from loguru import (
    analyze_log_file,
    check_health,
    quick_stats,
    get_error_summary,
    find_log_patterns
)

# ✅ Daily health checks
def daily_log_health_check():
    """Automated log health monitoring."""
    health = check_health("production.log")

    if health['status'] == 'critical':
        logger.critical("Critical log issues detected", extra=health['issues'])
        send_alert(health)

# ✅ Quick stats for debugging
stats = quick_stats("app.log")
print(stats)  # One-line summary

# ✅ Error investigation
errors = get_error_summary("app.log")
logger.info("Error summary", extra={'error_count': errors['error_count']})

# ✅ Pattern-based debugging
database_errors = find_log_patterns("app.log", r"database.*error")

# ✅ Comprehensive analysis
full_analysis = analyze_log_file("app.log")
# Returns: error counts, performance metrics, health status, patterns

# ✅ Generate formatted reports
from loguru import generate_report

report = generate_report("app.log", format="markdown")
with open("logs/daily_report.md", "w") as f:
    f.write(report)
```

**Available analysis functions**:
- `analyze_log_file()` - Comprehensive analysis
- `check_health()` - Health assessment with scoring
- `quick_stats()` - One-line summary
- `get_error_summary()` - Error-focused analysis
- `get_performance_summary()` - Performance metrics
- `find_log_patterns()` - Regex pattern search
- `generate_report()` - Formatted reports (markdown, JSON, HTML)

---

### Debug Code

#### Print Statements
**Pattern**: Never - use Loguru (just as easy!)

```python
# ❌ NEVER
print(f"Processing {file_path}")


# ✅ ALWAYS
logger.debug(f"Processing {file_path}")


# ✅ Even easier with function tracing
@tracer.trace
def process_file(file_path):
    # Automatic logging!
    pass
```

#### Debugger Breakpoints
**Pattern**: Conditional via env vars + Loguru's dynamic debugging

```python
import os

DEBUG_BREAKPOINTS = os.getenv('DEBUG_BREAKPOINTS', 'False') == 'True'

def process_data(data):
    if DEBUG_BREAKPOINTS:
        breakpoint()
    return transform(data)
```

#### Debug Modes
**Pattern**: Layered approach (env vars → Django settings → feature flags)

```python
# settings.py
import os

DEBUG = os.getenv('DEBUG', 'False') == 'True'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG_SQL = os.getenv('DEBUG_SQL', str(DEBUG)) == 'True'

def configure_logging():
    if ENVIRONMENT == 'development':
        logger.configure_style("beautiful")
        logger.level("TRACE" if DEBUG else "DEBUG")
    else:
        logger.configure_streams(
            console=dict(template="minimal", level="WARNING"),
            file=dict(sink="logs/production.log", serialize=True)
        )
```

---
