"""
Tests for XML template export functionality.

Covers:
- XML generation from schema
- Export → Import round-trip data preservation
- Brownfield XML structure validation
"""

import os
import tempfile
import xml.etree.ElementTree as ET

from django.core.management import call_command
from django.test import TestCase

from apps.catalog.models import DirectoryMapping, Schema, SchemaRule


class XMLExportTest(TestCase):
    """Test XML export functionality."""

    def setUp(self):
        """Create test schema for export tests."""
        self.schema = Schema.objects.create(
            name="Export Test Schema",
            source_type="web",
            description="Test schema for export functionality",
        )

        # Add rules
        SchemaRule.objects.create(
            schema=self.schema,
            rule_type="media_type",
            rule_value="video",
            logic_operator="AND",
            priority=0,
        )
        SchemaRule.objects.create(
            schema=self.schema,
            rule_type="extension",
            rule_value=".mp4",
            logic_operator="AND",
            priority=1,
        )

        # Add directory mapping
        DirectoryMapping.objects.create(
            schema=self.schema,
            input_path="/test/input",
            output_path="/test/output",
        )

    def test_export_basic_template(self):
        """Test exporting a simple schema to XML."""
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Export
            call_command("export_xml_template", str(self.schema.id), output=tmp_path)

            # Verify file created
            assert os.path.exists(tmp_path)

            # Parse XML
            tree = ET.parse(tmp_path)
            root = tree.getroot()

            # Verify structure
            assert root.tag == "samplify"
            assert root.find("name") is not None
            assert root.find("name").text == "Export Test Schema"
            assert root.find("libraries") is not None
            assert root.find("outputDirectories") is not None

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_export_to_stdout(self):
        """Test exporting to stdout (no --output parameter)."""
        from io import StringIO

        out = StringIO()

        # Export to stdout
        call_command("export_xml_template", str(self.schema.id), stdout=out)

        output = out.getvalue()

        # Verify XML in output
        assert "<?xml version" in output
        assert "<samplify>" in output
        assert "Export Test Schema" in output

    def test_export_brownfield_structure(self):
        """Test exported XML matches brownfield structure."""
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            call_command("export_xml_template", str(self.schema.id), output=tmp_path)

            # Parse and validate structure
            tree = ET.parse(tmp_path)
            root = tree.getroot()

            # Verify brownfield elements exist
            assert root.tag == "samplify"
            assert root.find("name") is not None
            assert root.find("libraries") is not None
            assert root.find("outputDirectories") is not None

            # Verify libraries contains directory elements
            libraries = root.find("libraries")
            dirs = libraries.findall("directory")
            assert len(dirs) > 0

            # Verify outputDirectories structure
            output_dirs = root.find("outputDirectories")
            for dir_elem in output_dirs.findall("directory"):
                assert dir_elem.get("path") is not None
                assert dir_elem.find("rules") is not None
                assert dir_elem.find("governor") is not None
                governor = dir_elem.find("governor")
                assert governor.find("comparison") is not None

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_export_nonexistent_schema(self):
        """Test export with invalid schema ID."""
        import pytest
        from django.core.management.base import CommandError

        with pytest.raises(CommandError):
            call_command("export_xml_template", "99999")


class XMLRoundTripTest(TestCase):
    """Test export → import round-trip data preservation."""

    def test_roundtrip_preserves_data(self):
        """Test that export → import preserves all schema data."""
        # Create original schema
        original_schema = Schema.objects.create(
            name="Roundtrip Test",
            source_type="web",
            description="Test round-trip preservation",
        )

        SchemaRule.objects.create(
            schema=original_schema,
            rule_type="keyword",
            rule_value="test_keyword",
            logic_operator="AND",
            priority=0,
        )
        SchemaRule.objects.create(
            schema=original_schema,
            rule_type="media_type",
            rule_value="audio",
            logic_operator="AND",
            priority=1,
        )

        DirectoryMapping.objects.create(
            schema=original_schema,
            input_path="/roundtrip/input",
            output_path="/roundtrip/output",
        )

        # Export to XML
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            export_path = tmp.name

        try:
            call_command("export_xml_template", str(original_schema.id), output=export_path)

            # Modify name for re-import (avoid duplicate)
            tree = ET.parse(export_path)
            root = tree.getroot()
            name_elem = root.find("name")
            name_elem.text = "Roundtrip Test Reimported"

            # Save modified XML
            tree.write(export_path, encoding="UTF-8", xml_declaration=True)

            # Re-import
            call_command("import_xml_template", export_path)

            # Fetch reimported schema
            reimported_schema = Schema.objects.get(name="Roundtrip Test Reimported")

            # Verify rule counts match
            assert reimported_schema.rules.count() == original_schema.rules.count()

            # Verify directory mappings match
            assert reimported_schema.directory_mappings.count() == original_schema.directory_mappings.count()

            # Verify source type
            assert reimported_schema.source_type == "imported"

        finally:
            if os.path.exists(export_path):
                os.unlink(export_path)

    def test_roundtrip_with_complex_rules(self):
        """Test round-trip with all brownfield rule types."""
        # Import complex template
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <samplify>
            <name>Complex Roundtrip</name>
            <libraries>
                <directory path="/input1"/>
                <directory path="/input2"/>
            </libraries>
            <outputDirectories>
                <directory path="/output/video">
                    <rules>
                        <containsVideo>true</containsVideo>
                        <videoOutputContainer>.mp4</videoOutputContainer>
                    </rules>
                    <governor><comparison>AND</comparison></governor>
                </directory>
                <directory path="/output/audio">
                    <rules>
                        <containsAudio>true</containsAudio>
                        <audioSampleRate>48000</audioSampleRate>
                        <audioChannels>2</audioChannels>
                        <expression>Kick</expression>
                    </rules>
                    <governor><comparison>OR</comparison></governor>
                </directory>
            </outputDirectories>
        </samplify>"""

        # Import
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
            tmp.write(xml_content)
            import_path = tmp.name

        try:
            call_command("import_xml_template", import_path)

            # Get imported schema
            imported_schema = Schema.objects.get(name="Complex Roundtrip")

            # Export
            with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
                export_path = tmp.name

            try:
                call_command("export_xml_template", str(imported_schema.id), output=export_path)

                # Verify exported XML can be parsed
                tree = ET.parse(export_path)
                root = tree.getroot()

                # Verify name preserved
                assert root.find("name").text == "Complex Roundtrip"

                # Verify structure
                assert root.find("libraries") is not None
                assert root.find("outputDirectories") is not None

            finally:
                if os.path.exists(export_path):
                    os.unlink(export_path)

        finally:
            if os.path.exists(import_path):
                os.unlink(import_path)
