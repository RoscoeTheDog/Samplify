"""Context processor to inject Django and Python version information."""

import sys

import django


def version_info(request):  # noqa: ARG001
    """
    Add Django and Python version information to template context.

    Args:
        request: HttpRequest object (unused but required by Django)

    Returns:
        dict: Context variables for templates
    """
    return {
        "django_version": django.get_version(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
