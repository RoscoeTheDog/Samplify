# Django Setup Guide

This guide explains the Django project setup and how to get started with development.

## Project Structure

```
Samplify/
├── manage.py                    # Django CLI entry point
├── samplify/                    # Django project directory
│   ├── __init__.py
│   ├── settings.py              # Project settings
│   ├── urls.py                  # URL routing
│   ├── wsgi.py                  # WSGI entry point
│   ├── asgi.py                  # ASGI entry point
│   └── context_processors/      # Custom context processors
├── templates/                   # Django templates
│   ├── base.html                # Base template
│   └── home.html                # Homepage
├── static/                      # Static files (CSS, JS, vendor libs)
│   ├── css/
│   ├── js/
│   └── vendor/
│       ├── bootstrap/           # Bootstrap 5.3.3 (local)
│       └── jquery/              # jQuery 3.7.1 (local)
├── database/                    # SQLite database location
└── requirements.txt             # Python dependencies
```

## Initial Setup

### 1. Create Virtual Environment

```bash
# Windows
setup_env.bat

# macOS/Linux
./setup_env.sh
```

### 2. Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Run Django Checks

```bash
python manage.py check
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Start Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/` to see the application.

## Key Django Commands

### Check System

```bash
python manage.py check
```

### Create Database Migrations

```bash
python manage.py makemigrations
```

### Apply Migrations

```bash
python manage.py migrate
```

### Run Development Server

```bash
python manage.py runserver

# Custom port
python manage.py runserver 8080

# Custom host and port
python manage.py runserver 0.0.0.0:8000
```

### Django Shell

```bash
python manage.py shell
```

### Collect Static Files (Production)

```bash
python manage.py collectstatic
```

## Django Configuration Highlights

### Authentication DISABLED

Per NFR13 (open local interface), Django authentication is **disabled**:

```python
# In settings.py INSTALLED_APPS:
# "django.contrib.admin",  # DISABLED
# "django.contrib.auth",   # DISABLED

# In settings.py MIDDLEWARE:
# "django.contrib.auth.middleware.AuthenticationMiddleware",  # DISABLED
```

### CSRF Protection ENABLED

CSRF protection remains **enabled** for security:

```python
# In settings.py MIDDLEWARE:
"django.middleware.csrf.CsrfViewMiddleware",  # ENABLED
```

### Static Files (No CDN)

All static files are served **locally** (NFR3: no CDN dependencies):

- **Bootstrap 5.3.3**: `static/vendor/bootstrap/`
- **jQuery 3.7.1**: `static/vendor/jquery/`
- **Custom CSS**: `static/css/samplify.css`

Static files are configured in `settings.py`:

```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
```

### Database

SQLite database configured at `database/samplify.db`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "database" / "samplify.db",
    }
}
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
python manage.py runserver 8080
```

### Import Errors

Make sure your virtual environment is activated:

```bash
# Check if (venv) appears in your prompt
# If not, activate it:

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Static Files Not Loading

During development, Django serves static files automatically if `DEBUG=True`.

If static files aren't loading:

1. Check `settings.py`: `DEBUG = True`
2. Check `settings.py`: `STATIC_URL = "/static/"`
3. Verify files exist in `static/` directory

### Database Issues

If you see database errors, try:

```bash
# Delete the database (WARNING: loses all data)
rm database/samplify.db

# Run migrations again
python manage.py migrate
```

## Next Steps

After completing Story 1.1 (Django Project Setup), the next stories will add:

- **Story 1.2A-C**: Database models (File, Schema, etc.)
- **Story 1.3**: Loguru logging configuration
- **Story 1.4**: FFmpeg detection and download service
- **Story 1.5+**: Backend services and frontend UI

See `docs/stories/index.md` for the complete story roadmap.

## Additional Resources

- [Django 4.2 Documentation](https://docs.djangoproject.com/en/4.2/)
- [Project Architecture](docs/architecture/index.md)
- [Coding Standards](docs/architecture/coding-standards.md)
- [Tech Stack Details](docs/architecture/tech-stack.md)
