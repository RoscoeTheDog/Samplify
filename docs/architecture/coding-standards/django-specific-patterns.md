# Django-Specific Patterns

### Model Preferences

#### Model Method Organization
**Standard Django order (1-6)**:

```python
class Schema(models.Model):
    # 1. Field definitions
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # 2. Meta class
    class Meta:
        ordering = ['-created_at']

    # 3. __str__() method
    def __str__(self):
        return self.name

    # 4. Class methods and managers
    @classmethod
    def create_default(cls, owner):
        return cls.objects.create(name=f"{owner.username}'s Schema", owner=owner)

    # 5. Properties
    @property
    def rule_count(self):
        return self.rules.count()

    # 6. Instance methods
    def activate(self):
        self.is_active = True
        self.save(update_fields=['is_active'])
```

#### Model Validation
**Pattern**: Mix all three - field validators, clean(), save()

```python
class Schema(models.Model):
    # Field-level validators (simple, reusable)
    name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3)]
    )

    # Model-level validation (cross-field, complex logic)
    def clean(self):
        super().clean()
        if self.is_active and not self.owner.is_active:
            raise ValidationError('Cannot activate schema when owner is inactive')

    # Override save for auto-computation (not validation)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not kwargs.pop('skip_validation', False):
            self.full_clean()
        super().save(*args, **kwargs)
```

#### QuerySet Methods
**Pattern**: QuerySet with as_manager() for chainable methods

```python
class SchemaQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def for_user(self, user):
        return self.filter(owner=user)


class Schema(models.Model):
    objects = SchemaQuerySet.as_manager()


# Usage - methods are chainable
Schema.objects.active().for_user(request.user)
```

#### Related Name Conventions
**Pattern**: Plural of source model (add prefix for collisions)

```python
# ✅ Standard - Plural
class Rule(models.Model):
    schema = models.ForeignKey(Schema, related_name='rules')


# Usage
schema.rules.all()


# ✅ Prefix when multiple relations to same model
class Article(models.Model):
    author = models.ForeignKey(User, related_name='authored_articles')
    editor = models.ForeignKey(User, related_name='edited_articles')
```

---

### View Preferences

#### View Organization
**Pattern**: CBV for CRUD, FBV for custom logic

```python
# ✅ CBV for standard CRUD
class SchemaListView(ListView):
    model = Schema

    def get_queryset(self):
        return Schema.objects.filter(owner=self.request.user).active()


# ✅ FBV for custom/complex business logic
@login_required
def process_audio_upload(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # Complex multi-step logic
    # ...
```

#### View Docstrings
**Pattern**: URL pattern, HTTP methods, parameters

```python
@api_view(['POST'])
def create_schema(request):
    """Create a new schema for the authenticated user.

    URL: POST /api/schemas/

    Request Body:
        {
            "name": str (required) - Schema name
            "fields": list[dict] (required) - Field definitions
        }

    Returns:
        201: Schema created
        400: Validation error
    """
    pass
```

#### Business Logic in Views
**Pattern**: Simple logic OK in views, complex in services

```python
# ✅ Simple logic in view
@login_required
def toggle_schema(request, schema_id):
    schema = get_object_or_404(Schema, id=schema_id, owner=request.user)
    schema.is_active = not schema.is_active
    schema.save(update_fields=['is_active'])
    return redirect('schema-detail', pk=schema_id)


# ✅ Complex logic in service layer
def process_audio(request):
    result = audio_service.process_file(
        file=request.FILES['file'],
        schema_id=request.data['schema_id'],
        user=request.user
    )
    return Response({'result_id': result.id}, status=202)
```

#### Response Formatting
**Pattern**: Named variable for complex responses

```python
# ✅ Named variable for complex responses
@api_view(['POST'])
def create_schema(request):
    serializer = SchemaSerializer(data=request.data)

    if not serializer.is_valid():
        error_response = {
            'status': 'error',
            'errors': serializer.errors
        }
        return Response(error_response, status=400)

    schema = serializer.save(owner=request.user)
    success_response = {
        'status': 'success',
        'data': {'id': schema.id, 'name': schema.name}
    }
    return Response(success_response, status=201)
```

---
