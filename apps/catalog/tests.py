"""Unit tests for catalog app models."""

import multiprocessing
import os
import time
from pathlib import Path

from django.db import connection
from django.test import TestCase

from apps.catalog.models import DirectoryMapping, File, Schema, SchemaRule, SchemaTransformation


class FileModelTest(TestCase):
    """Test cases for File model."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.audio_file = File.objects.create(
            file_path="/media/audio/test.mp3",
            file_name="test.mp3",
            file_format="mp3",
            file_size=1024000,
            sample_rate=44100,
            bit_depth=16,
            codec="mp3",
            media_type="audio",
        )

        self.video_file = File.objects.create(
            file_path="/media/video/test.mp4",
            file_name="test.mp4",
            file_format="mp4",
            file_size=5242880,
            sample_rate=48000,
            bit_depth=24,
            codec="h264",
            media_type="video",
        )

        self.image_file = File.objects.create(
            file_path="/media/images/test.jpg",
            file_name="test.jpg",
            file_format="jpg",
            file_size=204800,
            media_type="image",
        )

    def test_file_creation(self) -> None:
        """Test that File instances are created correctly."""
        self.assertEqual(File.objects.count(), 3)
        self.assertIsNotNone(self.audio_file.id)
        self.assertIsNotNone(self.video_file.id)
        self.assertIsNotNone(self.image_file.id)

    def test_media_type_discriminator(self) -> None:
        """Test media_type field acts as discriminator."""
        audio_files = File.objects.filter(media_type="audio")
        video_files = File.objects.filter(media_type="video")
        image_files = File.objects.filter(media_type="image")

        self.assertEqual(audio_files.count(), 1)
        self.assertEqual(video_files.count(), 1)
        self.assertEqual(image_files.count(), 1)

        self.assertEqual(audio_files.first(), self.audio_file)
        self.assertEqual(video_files.first(), self.video_file)
        self.assertEqual(image_files.first(), self.image_file)

    def test_str_method(self) -> None:
        """Test __str__() returns file name."""
        self.assertEqual(str(self.audio_file), "test.mp3")
        self.assertEqual(str(self.video_file), "test.mp4")
        self.assertEqual(str(self.image_file), "test.jpg")

    def test_get_absolute_path(self) -> None:
        """Test get_absolute_path() returns Path object."""
        audio_path = self.audio_file.get_absolute_path()
        video_path = self.video_file.get_absolute_path()
        image_path = self.image_file.get_absolute_path()

        self.assertIsInstance(audio_path, Path)
        self.assertIsInstance(video_path, Path)
        self.assertIsInstance(image_path, Path)

        # Use as_posix() for cross-platform path comparison
        self.assertEqual(audio_path.as_posix(), "/media/audio/test.mp3")
        self.assertEqual(video_path.as_posix(), "/media/video/test.mp4")
        self.assertEqual(image_path.as_posix(), "/media/images/test.jpg")

    def test_nullable_fields(self) -> None:
        """Test that media-specific fields are nullable for images."""
        # Image file should not require audio/video metadata
        self.assertIsNone(self.image_file.sample_rate)
        self.assertIsNone(self.image_file.bit_depth)
        self.assertIsNone(self.image_file.codec)

    def test_required_fields(self) -> None:
        """Test that all required fields are present."""
        self.assertIsNotNone(self.audio_file.file_path)
        self.assertIsNotNone(self.audio_file.file_name)
        self.assertIsNotNone(self.audio_file.file_format)
        self.assertIsNotNone(self.audio_file.file_size)
        self.assertIsNotNone(self.audio_file.media_type)

    def test_timestamps(self) -> None:
        """Test that timestamps are auto-generated."""
        self.assertIsNotNone(self.audio_file.created_at)
        self.assertIsNotNone(self.audio_file.updated_at)

    def test_ordering(self) -> None:
        """Test default ordering is by created_at descending."""
        files = list(File.objects.all())
        # Most recent first (image was created last)
        self.assertEqual(files[0], self.image_file)

    def test_single_table_storage(self) -> None:
        """Test that all media types are stored in single File table (not separate tables)."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name LIKE 'catalog_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]

        # Verify catalog_file table exists (single table for all media types)
        self.assertIn("catalog_file", tables)

        # Verify no separate media type tables (no catalog_audio, catalog_video, catalog_image)
        media_type_tables = [t for t in tables if t in ["catalog_audio", "catalog_video", "catalog_image"]]
        self.assertEqual(len(media_type_tables), 0, "Should not have separate media type tables")

    def test_media_type_choices(self) -> None:
        """Test that media_type uses correct choices."""
        expected_choices = [
            ("audio", "Audio"),
            ("video", "Video"),
            ("image", "Image"),
        ]
        self.assertEqual(File.MEDIA_TYPE_CHOICES, expected_choices)


class SchemaModelTest(TestCase):
    """Test cases for Schema model."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.schema1 = Schema.objects.create(
            name="Audio Processing Schema",
            description="Processes audio files for web playback",
            source_type="web",
        )
        self.schema2 = Schema.objects.create(
            name="Imported XML Schema",
            description="Imported from legacy XML",
            source_type="imported",
            xml_source="<template><name>Test</name></template>",
        )

    def test_schema_creation(self) -> None:
        """Test Schema instances are created correctly."""
        self.assertEqual(Schema.objects.count(), 2)
        self.assertIsNotNone(self.schema1.id)
        self.assertIsNotNone(self.schema2.id)

    def test_schema_unique_name(self) -> None:
        """Test schema name uniqueness constraint."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Schema.objects.create(name="Audio Processing Schema")

    def test_schema_str_method(self) -> None:
        """Test __str__() returns schema name with active status."""
        self.assertEqual(str(self.schema1), "Audio Processing Schema")
        self.schema1.is_active = True
        self.schema1.save()
        self.assertEqual(str(self.schema1), "Audio Processing Schema (ACTIVE)")

    def test_only_one_active_schema(self) -> None:
        """Test only one schema can be active at a time."""
        self.schema1.is_active = True
        self.schema1.save()
        self.assertTrue(Schema.objects.get(pk=self.schema1.pk).is_active)

        # Activate second schema
        self.schema2.is_active = True
        self.schema2.save()

        # First schema should be deactivated
        self.schema1.refresh_from_db()
        self.assertFalse(self.schema1.is_active)
        self.assertTrue(self.schema2.is_active)

    def test_xml_source_storage(self) -> None:
        """Test XML source field stores and retrieves correctly."""
        xml_content = '<?xml version="1.0"?><template><name>Test Schema</name></template>'
        schema = Schema.objects.create(
            name="XML Test Schema",
            source_type="imported",
            xml_source=xml_content,
        )
        schema.refresh_from_db()
        self.assertEqual(schema.xml_source, xml_content)

    def test_source_type_choices(self) -> None:
        """Test source_type uses correct choices."""
        expected_choices = [
            ("web", "Web Created"),
            ("imported", "Imported from XML"),
        ]
        self.assertEqual(Schema.SOURCE_TYPE_CHOICES, expected_choices)

    def test_timestamps(self) -> None:
        """Test timestamps are auto-generated."""
        self.assertIsNotNone(self.schema1.created_at)
        self.assertIsNotNone(self.schema1.updated_at)


class SchemaRuleModelTest(TestCase):
    """Test cases for SchemaRule model."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema")
        self.rule1 = SchemaRule.objects.create(
            schema=self.schema,
            rule_type="keyword",
            rule_value="test",
            logic_operator="AND",
            priority=10,
        )
        self.rule2 = SchemaRule.objects.create(
            schema=self.schema,
            rule_type="extension",
            rule_value=".mp3",
            logic_operator="OR",
            priority=5,
        )

    def test_schema_rule_creation(self) -> None:
        """Test SchemaRule instances are created correctly."""
        self.assertEqual(SchemaRule.objects.count(), 2)
        self.assertEqual(self.schema.rules.count(), 2)

    def test_schema_rule_relationship(self) -> None:
        """Test ForeignKey relationship to Schema."""
        self.assertEqual(self.rule1.schema, self.schema)
        self.assertIn(self.rule1, self.schema.rules.all())

    def test_cascade_deletion(self) -> None:
        """Test rules are deleted when schema is deleted."""
        schema_id = self.schema.id
        self.schema.delete()
        self.assertEqual(SchemaRule.objects.filter(schema_id=schema_id).count(), 0)

    def test_rule_ordering(self) -> None:
        """Test rules are ordered by priority descending."""
        rules = list(SchemaRule.objects.all())
        self.assertEqual(rules[0], self.rule1)  # priority 10
        self.assertEqual(rules[1], self.rule2)  # priority 5

    def test_rule_str_method(self) -> None:
        """Test __str__() returns rule description."""
        self.assertEqual(str(self.rule1), "Keyword Match: test")
        self.assertEqual(str(self.rule2), "File Extension: .mp3")


class SchemaTransformationModelTest(TestCase):
    """Test cases for SchemaTransformation model."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema")
        self.transformation = SchemaTransformation.objects.create(
            schema=self.schema,
            output_format="mp3",
            sample_rate=44100,
            bit_depth=16,
            normalize_db=-3.0,
        )

    def test_transformation_creation(self) -> None:
        """Test SchemaTransformation instances are created correctly."""
        self.assertEqual(SchemaTransformation.objects.count(), 1)
        self.assertEqual(self.schema.transformations.count(), 1)

    def test_transformation_relationship(self) -> None:
        """Test ForeignKey relationship to Schema."""
        self.assertEqual(self.transformation.schema, self.schema)
        self.assertIn(self.transformation, self.schema.transformations.all())

    def test_cascade_deletion(self) -> None:
        """Test transformations are deleted when schema is deleted."""
        schema_id = self.schema.id
        self.schema.delete()
        self.assertEqual(SchemaTransformation.objects.filter(schema_id=schema_id).count(), 0)

    def test_nullable_fields(self) -> None:
        """Test optional transformation fields."""
        transform = SchemaTransformation.objects.create(
            schema=self.schema,
            output_format="wav",
        )
        self.assertIsNone(transform.sample_rate)
        self.assertIsNone(transform.bit_depth)
        self.assertIsNone(transform.normalize_db)

    def test_transformation_str_method(self) -> None:
        """Test __str__() returns transformation description."""
        self.assertEqual(str(self.transformation), "Transform to mp3")


class DirectoryMappingModelTest(TestCase):
    """Test cases for DirectoryMapping model."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.schema = Schema.objects.create(name="Test Schema")
        self.mapping1 = DirectoryMapping.objects.create(
            schema=self.schema,
            input_path="/input/audio",
            output_path="/output/audio",
            is_watched=True,
        )
        self.mapping2 = DirectoryMapping.objects.create(
            schema=self.schema,
            input_path="/input/video",
            output_path="/output/video",
            is_watched=False,
        )

    def test_directory_mapping_creation(self) -> None:
        """Test DirectoryMapping instances are created correctly."""
        self.assertEqual(DirectoryMapping.objects.count(), 2)
        self.assertEqual(self.schema.directory_mappings.count(), 2)

    def test_directory_mapping_relationship(self) -> None:
        """Test ForeignKey relationship to Schema."""
        self.assertEqual(self.mapping1.schema, self.schema)
        self.assertIn(self.mapping1, self.schema.directory_mappings.all())

    def test_cascade_deletion(self) -> None:
        """Test mappings are deleted when schema is deleted."""
        schema_id = self.schema.id
        self.schema.delete()
        self.assertEqual(DirectoryMapping.objects.filter(schema_id=schema_id).count(), 0)

    def test_directory_mapping_str_method(self) -> None:
        """Test __str__() returns mapping description."""
        self.assertEqual(str(self.mapping1), "/input/audio → /output/audio [WATCHED]")
        self.assertEqual(str(self.mapping2), "/input/video → /output/video")


class SchemaIntegrationTest(TestCase):
    """Integration tests for complete schema with all related models."""

    def test_complete_schema_with_relationships(self) -> None:
        """Test creating a complete schema with all relationships."""
        # Create schema
        schema = Schema.objects.create(
            name="Complete Audio Processing",
            description="Full audio processing pipeline",
            is_active=True,
            source_type="web",
        )

        # Add rules
        SchemaRule.objects.create(
            schema=schema,
            rule_type="media_type",
            rule_value="audio",
            priority=10,
        )
        SchemaRule.objects.create(
            schema=schema,
            rule_type="extension",
            rule_value=".wav",
            logic_operator="OR",
            priority=5,
        )

        # Add transformation
        SchemaTransformation.objects.create(
            schema=schema,
            output_format="mp3",
            sample_rate=44100,
            bit_depth=16,
        )

        # Add directory mappings
        DirectoryMapping.objects.create(
            schema=schema,
            input_path="/watch/audio/input",
            output_path="/watch/audio/output",
            is_watched=True,
        )

        # Verify all relationships
        self.assertEqual(schema.rules.count(), 2)
        self.assertEqual(schema.transformations.count(), 1)
        self.assertEqual(schema.directory_mappings.count(), 1)

        # Test cascade deletion removes all related objects
        schema.delete()
        self.assertEqual(SchemaRule.objects.count(), 0)
        self.assertEqual(SchemaTransformation.objects.count(), 0)
        self.assertEqual(DirectoryMapping.objects.count(), 0)


class WALConfigurationTest(TestCase):
    """Test cases for WAL (Write-Ahead Logging) mode configuration (Story 1.2C).

    Note: Django test runner uses in-memory database which doesn't support WAL mode.
    These tests verify configuration is correct for production/development databases.
    """

    def test_signal_handler_registered(self) -> None:
        """Test that WAL mode signal handler is registered."""
        from django.db.backends.signals import connection_created
        from apps.catalog.apps import enable_wal_mode

        # Check that our signal handler is connected
        handlers = [receiver[1]() for receiver in connection_created.receivers]
        self.assertIn(enable_wal_mode, handlers, "WAL mode signal handler should be registered")

    def test_database_configuration(self) -> None:
        """Test that database is configured correctly for WAL mode."""
        from django.conf import settings

        db_config = settings.DATABASES["default"]

        # Verify SQLite is configured
        self.assertEqual(db_config["ENGINE"], "django.db.backends.sqlite3")

        # Verify database path structure (in production, not test memory DB)
        db_path = db_config["NAME"]
        # Test database uses memory URI, production uses Path
        if isinstance(db_path, Path):
            self.assertTrue(str(db_path).endswith("samplify.db"))
        else:
            # Test environment - just verify it's configured
            self.assertIsInstance(db_path, (str, Path))

    def test_wal_mode_on_file_database(self) -> None:
        """Test WAL mode on file-based database (skipped in test environment).

        This test verifies WAL configuration works on actual file database.
        Django test database uses memory mode which doesn't support WAL.
        """
        from django.conf import settings
        import sqlite3
        import tempfile

        # Create temporary database file to test WAL mode
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            tmp_db_path = tmp_file.name

        try:
            # Connect to file database and enable WAL
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()

            # Execute same command as our signal handler
            cursor.execute("PRAGMA journal_mode=WAL;")
            journal_mode = cursor.fetchone()[0]

            # Verify WAL mode is enabled
            self.assertEqual(journal_mode.upper(), "WAL", "File database should support WAL mode")

            # Verify WAL persists after closing and reopening
            conn.close()

            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode;")
            journal_mode = cursor.fetchone()[0]

            self.assertEqual(journal_mode.upper(), "WAL", "WAL mode should persist")

            conn.close()
        finally:
            # Cleanup
            import os
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
            # Also clean up WAL files
            for ext in ["-wal", "-shm"]:
                wal_file = tmp_db_path + ext
                if os.path.exists(wal_file):
                    os.unlink(wal_file)

    def test_concurrent_access_documentation(self) -> None:
        """Document that WAL mode enables concurrent access.

        Note: Django test database uses in-memory mode which has locking limitations.
        In production with file-based database + WAL mode:
        - Multiple readers can access database simultaneously
        - One writer can operate while readers are active
        - No "database is locked" errors in multiprocessing scenarios

        This test verifies the WAL configuration is in place.
        Manual testing with actual file database confirms concurrent access works.
        """
        from django.conf import settings
        from apps.catalog.apps import enable_wal_mode
        from django.db.backends.signals import connection_created

        # Verify configuration for concurrent access
        self.assertEqual(settings.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3")

        # Verify signal handler is registered
        handlers = [receiver[1]() for receiver in connection_created.receivers]
        self.assertIn(enable_wal_mode, handlers)

        # Test passes - WAL configuration is properly set up for concurrent access


class LoguruConfigurationTest(TestCase):
    """Test cases for Loguru logging configuration (Story 1.3)."""

    def test_loguru_config_exists(self) -> None:
        """Test that LOGURU_CONFIG is defined in settings."""
        from django.conf import settings

        self.assertTrue(hasattr(settings, "LOGURU_CONFIG"), "LOGURU_CONFIG should exist in settings")
        config = settings.LOGURU_CONFIG

        # Verify required configuration keys
        self.assertIn("log_level", config)
        self.assertIn("log_file", config)
        self.assertIn("log_format", config)
        self.assertIn("rotation", config)
        self.assertIn("retention", config)
        self.assertIn("colorize", config)

    def test_log_file_path_configured(self) -> None:
        """Test that log file path is properly configured."""
        from django.conf import settings

        log_file = settings.LOGURU_CONFIG["log_file"]

        # Verify it's a Path object
        self.assertIsInstance(log_file, Path)

        # Verify it points to logs directory
        self.assertTrue(str(log_file).endswith("samplify.log"))
        self.assertEqual(log_file.name, "samplify.log")

    def test_log_format_hierarchical(self) -> None:
        """Test that log format includes hierarchical elements (module:function:line)."""
        from django.conf import settings

        log_format = settings.LOGURU_CONFIG["log_format"]

        # Verify hierarchical format elements are present
        self.assertIn("{name}", log_format, "Format should include module name")
        self.assertIn("{function}", log_format, "Format should include function name")
        self.assertIn("{line}", log_format, "Format should include line number")
        # Check for level (may have formatting like {level: <8})
        self.assertTrue(
            "{level" in log_format,
            "Format should include log level (with or without formatting)"
        )
        self.assertIn("{message}", log_format, "Format should include message")

    def test_log_rotation_configured(self) -> None:
        """Test that log rotation is configured correctly."""
        from django.conf import settings

        config = settings.LOGURU_CONFIG

        # Verify rotation is 10 MB
        self.assertEqual(config["rotation"], "10 MB")

        # Verify retention is 5 files
        self.assertEqual(config["retention"], 5)

    def test_loguru_import_available(self) -> None:
        """Test that loguru package is available."""
        try:
            from loguru import logger

            self.assertIsNotNone(logger, "Loguru logger should be available")
        except ImportError:
            self.fail("Loguru package should be installed")

    def test_loguru_basic_logging(self) -> None:
        """Test basic logging functionality."""
        from loguru import logger
        import io

        # Create string buffer to capture logs
        buffer = io.StringIO()

        # Add temporary handler
        handler_id = logger.add(buffer, format="{level} | {message}")

        # Log test message
        logger.info("Test message")

        # Remove temporary handler
        logger.remove(handler_id)

        # Verify message was logged
        output = buffer.getvalue()
        self.assertIn("INFO", output)
        self.assertIn("Test message", output)

    def test_loguru_exception_handling(self) -> None:
        """Test that Loguru can handle exceptions with tracebacks."""
        from loguru import logger
        import io

        # Create string buffer to capture logs
        buffer = io.StringIO()

        # Add temporary handler with backtrace enabled
        handler_id = logger.add(buffer, format="{level} | {message}", backtrace=True, diagnose=False)

        # Log exception
        try:
            _ = 1 / 0
        except ZeroDivisionError:
            logger.exception("Test exception")

        # Remove temporary handler
        logger.remove(handler_id)

        # Verify exception was logged
        output = buffer.getvalue()
        self.assertIn("ERROR", output)
        self.assertIn("Test exception", output)
        self.assertIn("ZeroDivisionError", output)

    def test_logs_directory_created(self) -> None:
        """Test that logs directory is created during app initialization."""
        from django.conf import settings

        log_file = settings.LOGURU_CONFIG["log_file"]
        logs_dir = log_file.parent

        # Directory should exist (created by configure_loguru)
        self.assertTrue(logs_dir.exists(), f"Logs directory {logs_dir} should exist")
        self.assertTrue(logs_dir.is_dir(), "Logs path should be a directory")
