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
    """Configure Loguru hierarchical logging for the application (Story 1.3).

    Features:
    - Hierarchical tree-based console output with Unicode box-drawing
    - Structured JSON file output for retrospective analysis
    - Global exception handling with IDE-clickable tracebacks
    - Log rotation (10 MB per file, 5 files retention)
    - Context-aware styling (URLs, IPs, emails, file paths)

    Reference: NFR7 hierarchical logging requirement, CR5 Loguru migration
    Fork: https://github.com/RoscoeTheDog/loguru
    """
    from loguru import logger
    from loguru._template_formatters import create_hierarchical_format_function
    from loguru._exception_hook import install_exception_hook
    from django.conf import settings
    import sys

    # Remove default Loguru handler
    logger.remove()

    # Get configuration
    config = settings.LOGURU_CONFIG

    # Ensure logs directory exists
    log_file = config["log_file"]
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create hierarchical format function for console output
    console_format_func = create_hierarchical_format_function(
        format_string=config["console_format"],
        template="hierarchical"
    )

    # Add console handler with hierarchical tree rendering
    logger.add(
        sys.stderr,
        format=console_format_func,
        colorize=True,
        level=config["log_level"],
        backtrace=True,  # Show full traceback
        diagnose=True,  # Show variable values in traceback
    )

    # Add JSON file handler for structured logging
    logger.add(
        str(log_file),
        format="{message}",  # Message only for JSON
        level=config["log_level"],
        rotation=config["rotation"],
        retention=config["retention"],
        compression="zip",
        serialize=True,  # Enable JSON output
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe, process-safe logging
    )

    # Install global exception hook for uncaught exceptions
    install_exception_hook(logger, "hierarchical")

    # Log startup message
    logger.info("Loguru hierarchical logging configured successfully",
                console_format="hierarchical_tree",
                file_format="structured_json",
                exception_hook="installed")


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
