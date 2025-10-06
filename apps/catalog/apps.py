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


def configure_loguru() -> None:
    """Configure Loguru logging for the application (Story 1.3).

    Features:
    - Hierarchical logging with module.function.line format
    - Global exception handling
    - IDE-clickable tracebacks
    - Log rotation (10 MB per file, 5 files retention)
    - Console and file logging

    Reference: NFR7 hierarchical logging requirement, CR5 Loguru migration
    """
    from loguru import logger
    from django.conf import settings
    import sys

    # Remove default Loguru handler
    logger.remove()

    # Get configuration
    config = settings.LOGURU_CONFIG

    # Ensure logs directory exists
    log_file = config["log_file"]
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Add console handler (with colors)
    logger.add(
        sys.stderr,
        format=config["log_format"],
        level=config["log_level"],
        colorize=config["colorize"],
        backtrace=True,  # Show full traceback
        diagnose=True,  # Show variable values in traceback
    )

    # Add file handler (with rotation)
    logger.add(
        str(log_file),
        format=config["log_format"],
        level=config["log_level"],
        rotation=config["rotation"],
        retention=config["retention"],
        compression="zip",  # Compress rotated files
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe, process-safe logging
    )

    # Log startup message
    logger.info("Loguru logging configured successfully")


class CatalogConfig(AppConfig):
    """Configuration for the catalog app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"

    def ready(self) -> None:
        """Connect signals and configure logging when app is ready."""
        # Enable WAL mode on every database connection (Story 1.2C)
        connection_created.connect(enable_wal_mode)

        # Configure Loguru logging (Story 1.3)
        configure_loguru()
