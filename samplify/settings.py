"""
Django settings for Samplify project.

Generated for Django 4.2.7 using BMAD methodology.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-dev-key-change-in-production-123456789"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    # Django built-in apps (authentication DISABLED per NFR13)
    "django.contrib.admin",  # ENABLED for Story 1.2A - model debugging
    "django.contrib.auth",  # REQUIRED by admin - but no authentication middleware
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project apps
    "apps.catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # ENABLED - security requirement
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Required by admin
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "samplify.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",  # Required by admin
                "django.contrib.messages.context_processors.messages",
                "samplify.context_processors.version.version_info",
            ],
        },
    },
]

WSGI_APPLICATION = "samplify.wsgi.application"


# ==============================================================================
# DATABASE
# ==============================================================================
# SQLite with WAL mode (Story 1.2C) - enables concurrent access for:
# - Django web server (main process)
# - Batch processing workers (multiprocessing)
# - Watch mode service (background thread)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "database" / "samplify.db",
    }
}

# WAL mode is configured via database signal in apps.catalog.apps.CatalogConfig.ready()
# This ensures WAL is enabled on every database connection


# ==============================================================================
# PASSWORD VALIDATION (Disabled since no authentication)
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = []


# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ==============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ==============================================================================

STATIC_URL = "/static/"

# Static files directories (for development)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Static files collection directory (for production)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Static files finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==============================================================================
# PROJECT-SPECIFIC SETTINGS
# ==============================================================================

# FFmpeg binary path (configured in Story 1.4)
FFMPEG_PATH = None

# Media processing settings (configured in future stories)
MEDIA_PROCESSING_ENABLED = False
