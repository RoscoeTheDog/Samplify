from django.apps import AppConfig
from django.db.backends.signals import connection_created


def enable_wal_mode(sender, connection, **kwargs) -> None:
    """Enable WAL mode for SQLite connections (Story 1.2C).

    WAL (Write-Ahead Logging) enables concurrent access:
    - Multiple readers can access database simultaneously
    - One writer can operate while readers are active
    - Prevents "database is locked" errors in multiprocessing

    Reference: NFR2 concurrent access requirement
    """
    if connection.vendor == "sqlite":
        cursor = connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()


class CatalogConfig(AppConfig):
    """Configuration for the catalog app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"

    def ready(self) -> None:
        """Connect signals when app is ready."""
        # Enable WAL mode on every database connection (Story 1.2C)
        connection_created.connect(enable_wal_mode)
