"""
Tests for XML template import functionality.

Covers:
- XML parsing (all brownfield rule types)
- Database import with transaction rollback
- Import validation
- Error handling
"""

import os
import tempfile
from io import StringIO

import pytest
from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase

from apps.catalog.models import DirectoryMapping, Schema, SchemaRule


class XMLImportTest(TestCase):
    """Test XML import functionality."""

    def test_import_basic_template(self):
        """Test importing a simple XML template."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <samplify>
            <name>Basic Test</name>
            <libraries>
                <directory path="/test/input"/>
            </libraries>
            <outputDirectories>
                <directory path="/test/output">
                    <rules>
                        <containsVideo>true</containsVideo>
                    </rules>
                    <governor>
                        <comparison>AND</comparison>
                    </governor>
                </directory>
            </outputDirectories>
        </samplify>"""

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = tmp.name

        try:
            # Import
            call_command("import_xml_template", tmp_path)

            # Verify schema created
            schema = Schema.objects.get(name="Basic Test")
            assert schema.source_type == "imported"
            assert schema.xml_source is not None
            assert len(schema.xml_source) > 0

            # Verify rules imported
            assert schema.rules.count() == 1
            rule = schema.rules.first()
            assert rule.rule_type == "media_type"
            assert rule.rule_value == "video"
            assert rule.logic_operator == "AND"

            # Verify directory mappings
            assert schema.directory_mappings.count() == 1
            mapping = schema.directory_mappings.first()
            assert mapping.input_path == "/test/input"
            assert mapping.output_path == "/test/output"

        finally:
            os.unlink(tmp_path)

    def test_import_all_brownfield_rule_types(self):
        """Test import supports all brownfield XML rule types (CR4)."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <samplify>
            <name>Brownfield Rules Test</name>
            <libraries>
                <directory path="/test/input"/>
            </libraries>
            <outputDirectories>
                <directory path="/test/video">
                    <rules>
                        <containsVideo>true</containsVideo>
                        <videoOutputContainer>.mp4</videoOutputContainer>
                    </rules>
                    <governor><comparison>AND</comparison></governor>
                </directory>
                <directory path="/test/image">
                    <rules>
                        <containsImage>true</containsImage>
                        <imageFormat>PNG</imageFormat>
                        <exportType>.png</exportType>
                    </rules>
                    <governor><comparison>AND</comparison></governor>
                </directory>
                <directory path="/test/audio">
                    <rules>
                        <containsAudio>true</containsAudio>
                        <expression>Kick</expression>
                        <extensions>.wav</extensions>
                        <audioFormat>pcm</audioFormat>
                        <audioSampleRate>48000</audioSampleRate>
                        <audioBitrate>128</audioBitrate>
                        <audioChannels>2</audioChannels>
                        <audioNormalize>True</audioNormalize>
                        <audioPreserve>False</audioPreserve>
                    </rules>
                    <governor><comparison>OR</comparison></governor>
                </directory>
            </outputDirectories>
        </samplify>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = tmp.name

        try:
            call_command("import_xml_template", tmp_path)

            schema = Schema.objects.get(name="Brownfield Rules Test")

            # Verify all rule types imported
            rule_types = set(schema.rules.values_list("rule_type", flat=True))
            assert "media_type" in rule_types  # containsVideo, containsAudio, containsImage
            assert "extension" in rule_types  # videoOutputContainer, extensions, exportType
            assert "keyword" in rule_types  # expression
            assert "attribute" in rule_types  # audio attributes

            # Verify specific rules
            video_rules = schema.rules.filter(rule_type="media_type", rule_value="video")
            assert video_rules.count() == 1

            audio_rules = schema.rules.filter(rule_type="media_type", rule_value="audio")
            assert audio_rules.count() == 1

            keyword_rules = schema.rules.filter(rule_type="keyword")
            assert keyword_rules.count() == 1
            assert keyword_rules.first().rule_value == "Kick"

        finally:
            os.unlink(tmp_path)

    def test_import_dry_run(self):
        """Test import dry run mode (no database changes)."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <samplify>
            <name>Dry Run Test</name>
            <libraries><directory path="/test"/></libraries>
            <outputDirectories/>
        </samplify>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = tmp.name

        try:
            # Run with --dry-run
            out = StringIO()
            call_command("import_xml_template", tmp_path, "--dry-run", stdout=out)

            # Verify no schema created
            assert not Schema.objects.filter(name="Dry Run Test").exists()

            # Verify output message
            output = out.getvalue()
            assert "Dry run" in output
            assert "Dry Run Test" in output

        finally:
            os.unlink(tmp_path)

    def test_import_invalid_xml(self):
        """Test import with malformed XML."""
        xml_content = """<?xml version="1.0"?>
        <samplify>
            <name>Invalid XML</name>
            <!-- Missing closing tag -->
            <libraries>
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = tmp.name

        try:
            with pytest.raises(Exception):  # Should raise ParseError
                call_command("import_xml_template", tmp_path)

        finally:
            os.unlink(tmp_path)

    def test_import_missing_name(self):
        """Test import with missing template name."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <samplify>
            <libraries/>
            <outputDirectories/>
        </samplify>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = tmp.name

        try:
            with pytest.raises(Exception):  # Should raise CommandError
                call_command("import_xml_template", tmp_path)

        finally:
            os.unlink(tmp_path)


class XMLImportTransactionTest(TransactionTestCase):
    """Test transaction rollback on import failures."""

    def test_rollback_on_duplicate_name(self):
        """Test transaction rollback when duplicate schema name exists."""
        # Create existing schema
        Schema.objects.create(name="Duplicate Test", source_type="web")

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <samplify>
            <name>Duplicate Test</name>
            <libraries/>
            <outputDirectories/>
        </samplify>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = tmp.name

        try:
            # Import should fail
            with pytest.raises(Exception):
                call_command("import_xml_template", tmp_path)

            # Verify only one schema exists (original not overwritten)
            assert Schema.objects.filter(name="Duplicate Test").count() == 1
            original = Schema.objects.get(name="Duplicate Test")
            assert original.source_type == "web"  # Original preserved

        finally:
            os.unlink(tmp_path)

    def test_import_preserves_original_xml(self):
        """Test that original XML is preserved in xml_source field."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <samplify>
            <name>XML Preservation Test</name>
            <libraries>
                <directory path="/test/input"/>
            </libraries>
            <outputDirectories>
                <directory path="/test/output">
                    <rules>
                        <containsVideo>true</containsVideo>
                    </rules>
                    <governor><comparison>AND</comparison></governor>
                </directory>
            </outputDirectories>
        </samplify>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = tmp.name

        try:
            call_command("import_xml_template", tmp_path)

            schema = Schema.objects.get(name="XML Preservation Test")

            # Verify XML preserved
            assert schema.xml_source is not None
            assert "<samplify>" in schema.xml_source
            assert "XML Preservation Test" in schema.xml_source
            assert "containsVideo" in schema.xml_source

        finally:
            os.unlink(tmp_path)
