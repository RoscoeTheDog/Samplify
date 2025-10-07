"""
Django management command for exporting schemas as XML templates.

This command generates brownfield-compatible XML templates from
Schema database records.

Usage:
    python manage.py export_xml_template <schema_id> [--output <file_path>]

Example:
    python manage.py export_xml_template 1 --output exported_template.xml
"""

import xml.etree.ElementTree as ET
from typing import Any
from xml.dom import minidom

from django.core.management.base import BaseCommand, CommandError

from apps.catalog.models import Schema


class Command(BaseCommand):
    """Export schema as XML template."""

    help = "Export database schema as brownfield XML template"

    def add_arguments(self, parser: Any) -> None:
        """
        Add command-line arguments.

        Args:
            parser: ArgumentParser instance
        """
        parser.add_argument(
            "schema_id",
            type=int,
            help="Schema ID to export",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Output file path (default: stdout)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Execute the export command.

        Args:
            args: Positional arguments
            options: Command options dictionary

        Raises:
            CommandError: If schema not found or export fails
        """
        schema_id = options["schema_id"]
        output_file = options.get("output")

        try:
            # Fetch schema
            schema = Schema.objects.get(id=schema_id)
        except Schema.DoesNotExist:
            raise CommandError(f"Schema with ID {schema_id} not found")

        self.stdout.write(f"Exporting schema: {schema.name} (ID: {schema_id})")

        try:
            # Generate XML
            xml_str = self._generate_xml(schema)

            if output_file:
                # Write to file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(xml_str)
                self.stdout.write(self.style.SUCCESS(f"Successfully exported to: {output_file}"))
            else:
                # Print to stdout
                self.stdout.write("\n" + xml_str)

        except Exception as e:
            raise CommandError(f"Export failed: {e}")

    def _generate_xml(self, schema: Schema) -> str:
        """
        Generate brownfield XML from schema.

        Args:
            schema: Schema instance to export

        Returns:
            Pretty-printed XML string
        """
        # Create root element
        root = ET.Element("samplify")

        # Add <name>
        name_elem = ET.SubElement(root, "name")
        name_elem.text = schema.name

        # Add <libraries> (input directories)
        libraries_elem = ET.SubElement(root, "libraries")
        input_paths = set()
        for mapping in schema.directory_mappings.all():
            input_paths.add(mapping.input_path)

        for input_path in sorted(input_paths):
            dir_elem = ET.SubElement(libraries_elem, "directory")
            dir_elem.set("path", input_path)

        # Add <outputDirectories> with rules
        output_dirs_elem = ET.SubElement(root, "outputDirectories")

        # Group rules and transformations by output directory
        output_paths = set()
        for mapping in schema.directory_mappings.all():
            output_paths.add(mapping.output_path)

        for output_path in sorted(output_paths):
            # Create <directory> element
            dir_elem = ET.SubElement(output_dirs_elem, "directory")
            dir_elem.set("path", output_path)

            # Get rules for this output directory
            # NOTE: Rules are not directly linked to output directories in current model
            # We'll export all rules for the schema (brownfield compatibility)
            rules_elem = ET.SubElement(dir_elem, "rules")

            # Convert SchemaRule records back to brownfield XML elements
            self._add_rules_to_xml(rules_elem, schema)

            # Add <governor> element
            governor_elem = ET.SubElement(dir_elem, "governor")
            comparison_elem = ET.SubElement(governor_elem, "comparison")

            # Determine logic operator from first rule (fallback to AND)
            first_rule = schema.rules.first()
            comparison_elem.text = first_rule.logic_operator if first_rule else "AND"

        # Pretty print XML
        rough_string = ET.tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="    ", encoding="UTF-8").decode("utf-8")

        # Remove extra blank lines
        lines = [line for line in pretty_xml.split("\n") if line.strip()]
        return "\n".join(lines)

    def _add_rules_to_xml(self, rules_elem: ET.Element, schema: Schema) -> None:
        """
        Add SchemaRule records as brownfield XML rule elements.

        Maps SchemaRule model fields back to brownfield XML format.

        Args:
            rules_elem: XML <rules> element to populate
            schema: Schema instance
        """
        # Reverse mapping: rule_type + rule_value -> XML element name and value
        # Process rules and convert back to brownfield XML

        for rule in schema.rules.all():
            if rule.rule_type == "media_type":
                # Map media_type back to containsVideo/containsAudio/containsImage
                if rule.rule_value == "video":
                    elem = ET.SubElement(rules_elem, "containsVideo")
                    elem.text = "true"
                elif rule.rule_value == "audio":
                    elem = ET.SubElement(rules_elem, "containsAudio")
                    elem.text = "true"
                elif rule.rule_value == "image":
                    elem = ET.SubElement(rules_elem, "containsImage")
                    elem.text = "true"

            elif rule.rule_type == "extension":
                # Extensions can be videoOutputContainer, exportType, or extensions
                # Use generic "extensions" element
                elem = ET.SubElement(rules_elem, "extensions")
                elem.text = rule.rule_value

            elif rule.rule_type == "keyword":
                # Keyword -> expression
                elem = ET.SubElement(rules_elem, "expression")
                elem.text = rule.rule_value

            elif rule.rule_type == "attribute":
                # Attributes are stored as "field:value" format
                # Parse and create appropriate XML element
                if ":" in rule.rule_value:
                    field_name, field_value = rule.rule_value.split(":", 1)

                    # Map field names back to brownfield XML element names
                    field_mapping = {
                        "image_format": "imageFormat",
                        "audio_format": "audioFormat",
                        "sample_rate": "audioSampleRate",
                        "bitrate": "audioBitrate",
                        "channels": "audioChannels",
                        "normalize": "audioNormalize",
                        "preserve": "audioPreserve",
                        "datetime_start": "datetimeStart",
                        "datetime_end": "datetimeEnd",
                    }

                    xml_elem_name = field_mapping.get(field_name, field_name)
                    elem = ET.SubElement(rules_elem, xml_elem_name)
                    elem.text = field_value
                else:
                    # Fallback: create element with attribute name
                    elem = ET.SubElement(rules_elem, rule.rule_value)
                    elem.text = "true"
