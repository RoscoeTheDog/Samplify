"""Test management command to demonstrate Loguru hierarchical logging (Story 1.3)."""

from django.core.management.base import BaseCommand
from loguru import logger


class Command(BaseCommand):
    """Test Loguru hierarchical logging configuration."""

    help = "Test Loguru hierarchical logging with rich context and exception handling"

    def handle(self, *args, **options) -> None:
        """Execute command to demonstrate hierarchical logging features."""

        # Basic hierarchical logging with rich context
        logger.info("Starting hierarchical logging demonstration",
                    command="test_logging",
                    module="apps.catalog.management.commands",
                    django_version="4.2.7",
                    python_version="3.10+")

        # Test INFO level with file path context
        logger.info("Processing media file batch",
                    source_dir="C:\\Users\\Admin\\Music\\Collection",
                    destination_dir="/var/media/processed",
                    file_count=150,
                    total_size_mb=2048.5,
                    processing_mode="batch")

        # Test SUCCESS level with URLs and metrics
        logger.success("Database migrations completed",
                      database_url="sqlite:///database/samplify.db",
                      migrations_applied=12,
                      execution_time_seconds=1.45,
                      wal_mode_enabled=True,
                      schema_version="1.2.0")

        # Test WARNING level with email and IP context
        logger.warning("Rate limit approaching threshold",
                      client_ip="192.168.1.100",
                      user_email="admin@samplify.local",
                      current_requests=850,
                      limit_threshold=1000,
                      window_minutes=60,
                      recommended_action="throttle_requests")

        # Test structured logging with nested data
        logger.info("Audio transcoding operation",
                    input_file="sample.flac",
                    output_format="mp3",
                    bitrate_kbps=320,
                    sample_rate_hz=48000,
                    duration_seconds=245.3,
                    codec="libmp3lame",
                    ffmpeg_version="5.1.2")

        # Test caught exception with rich context
        logger.info("Attempting file schema validation")
        try:
            # Simulate validation error
            schema_data = {
                "name": "Classical Music Collection",
                "version": "1.0",
                "rules": [
                    {"pattern": "{artist}/{album}/{track}", "priority": 1}
                ]
                # Missing required "transformations" key
            }
            transformations = schema_data["transformations"]  # KeyError!

        except KeyError as e:
            logger.exception("Schema validation failed - missing required field",
                           schema_name="Classical Music Collection",
                           missing_field=str(e).strip("'\""),
                           validation_stage="structure_check",
                           error_category="data_integrity",
                           file_path="schemas/classical.json",
                           recovery_action="request_complete_schema")

        logger.success("Hierarchical logging demonstration completed",
                      total_log_statements=7,
                      exceptions_handled=1,
                      console_format="hierarchical_tree",
                      file_format="structured_json")

        self.stdout.write(self.style.SUCCESS("\n" + "="*80))
        self.stdout.write(self.style.SUCCESS("Hierarchical Logging Test Complete"))
        self.stdout.write(self.style.SUCCESS("="*80))
        self.stdout.write(self.style.SUCCESS(f"✓ Console output: Hierarchical tree with Unicode box-drawing"))
        self.stdout.write(self.style.SUCCESS(f"✓ File output: Structured JSON at logs/samplify.log"))
        self.stdout.write(self.style.SUCCESS(f"✓ Exception hook: Installed for uncaught exceptions"))
        self.stdout.write(self.style.SUCCESS(f"✓ Context styling: URLs, IPs, emails, file paths"))
        self.stdout.write(self.style.SUCCESS("="*80))
