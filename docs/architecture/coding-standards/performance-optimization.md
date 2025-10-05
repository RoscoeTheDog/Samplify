# Performance & Optimization

### Code Optimization Preferences

#### Premature Optimization
**Pattern**: Profile first, then optimize (Donald Knuth's wisdom)

```python
# ✅ Write clear code first
def process_schemas(user):
    schemas = Schema.objects.filter(owner=user, is_active=True)
    results = []
    for schema in schemas:
        if schema.has_valid_fields():
            results.append(validate_and_process(schema))
    return results


# Then if profiling shows slow, optimize specifically
def process_schemas(user):
    # Profile showed N+1 query problem
    schemas = Schema.objects.filter(
        owner=user, is_active=True
    ).select_related('owner').prefetch_related('fields')
    # ... rest of logic
```

#### List vs Generator
**Pattern**: Context-dependent (lists for small/reusable, generators for large/single-pass)

```python
# ✅ List - small collection, need multiple passes
schemas = list(Schema.objects.filter(owner=user))
print(f"Found {len(schemas)} schemas")


# ✅ Generator - large data, single pass
def process_large_file(filepath):
    with open(filepath) as f:
        for line in f:  # Generator
            yield process_line(line)
```

#### Database Query Optimization
**Pattern**: Add select_related/prefetch_related when N+1 detected

```python
# ✅ Add optimization when N+1 detected
class SchemaListView(ListView):
    def get_queryset(self):
        return Schema.objects.filter(
            owner=self.request.user
        ).select_related('owner').prefetch_related('rules')
```

#### Caching Strategy
**Pattern**: Cache based on profiling data

```python
# ✅ Add caching after profiling shows it's needed
from django.core.cache import cache

def get_user_statistics(user):
    cache_key = f'user_stats_{user.id}'
    stats = cache.get(cache_key)

    if stats is None:
        stats = calculate_expensive_stats(user)
        cache.set(cache_key, stats, 300)  # 5 minutes

    return stats
```

#### Readability vs Performance
**Pattern**: Readability wins by default; performance-critical code can be optimized with documentation

```python
# ✅ Performance-critical - document why optimized
def process_audio_samples(samples):
    """Process audio samples using vectorized operations.

    Note: Uses NumPy for performance (10x faster than pure Python).
    """
    import numpy as np
    samples_array = np.array(samples, dtype=np.float32)
    # Optimized vectorized operations
```

---
