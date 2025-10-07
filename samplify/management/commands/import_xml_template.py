"""
Django management command for importing XML templates into database.

This command parses brownfield XML templates and creates corresponding
Schema, SchemaRule, SchemaTransformation, and DirectoryMapping records.

Usage:
    python manage.py import_xml_template <xml_file_path>

Example:
    python manage.py import_xml_template C:\\Users\\Admin\\Documents\\Samplify\\Templates\\mytemplate.xml
"""

import os
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalog.models import DirectoryMapping, Schema, SchemaRule, SchemaTransformation


class Command(BaseCommand):
    """Import XML template into database."""

    help = "Import brownfield XML template into database schema"

    def add_arguments(self, parser: Any) -> None:
        """
        Add command-line arguments.

        Args:
            parser: ArgumentParser instance
        """
        parser.add_argument(
            "xml_file",
            type=str,
            help="Path to XML template file to import",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse XML without saving to database",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Execute the import command.

        Args:
            args: Positional arguments
            options: Command options dictionary

        Raises:
            CommandError: If XML file is invalid or import fails
        """
        xml_file = options["xml_file"]
        dry_run = options.get("dry_run", False)

        # Validate file exists
        if not os.path.exists(xml_file):
            raise CommandError(f"XML file not found: {xml_file}")

        self.stdout.write(f"Importing XML template from: {xml_file}")

        try:
            # Parse XML
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Read original XML content for storage
            with open(xml_file, "r", encoding="utf-8") as f:
                xml_source = f.read()

            # Extract template data
            template_data = self._parse_xml(root)

            if dry_run:
                self.stdout.write(self.style.SUCCESS(f"Dry run: Would import template '{template_data['name']}'"))
                self.stdout.write(f"  - Rules: {len(template_data['rules'])}")
                self.stdout.write(f"  - Directory mappings: {len(template_data['directory_mappings'])}")
                return

            # Import to database with transaction
            schema = self._import_to_database(template_data, xml_source)

            # Report success
            self.stdout.write(
                self.style.SUCCESS(f"Successfully imported template: {schema.name} (ID: {schema.id})")
            )
            self.stdout.write(f"  - Schema ID: {schema.id}")
            self.stdout.write(f"  - Rules imported: {schema.rules.count()}")
            self.stdout.write(f"  - Directory mappings: {schema.directory_mappings.count()}")
            self.stdout.write(f"  - Transformations: {schema.transformations.count()}")

        except ET.ParseError as e:
            raise CommandError(f"Invalid XML file: {e}")
        except Exception as e:
            raise CommandError(f"Import failed: {e}")

    def _parse_xml(self, root: ET.Element) -> Dict[str, Any]:
        """
        Parse XML template into structured data.

        Args:
            root: Root XML element (<samplify>)

        Returns:
            Dictionary containing parsed template data

        Raises:
            CommandError: If required XML elements are missing
        """
        # Extract template name
        name_elem = root.find("name")
        if name_elem is None or not name_elem.text:
            raise CommandError("XML template missing <name> element")

        template_name = name_elem.text.strip()

        # Parse input directories (libraries)
        input_directories = []
        libraries_elem = root.find("libraries")
        if libraries_elem is not None:
            for dir_elem in libraries_elem.findall("directory"):
                path = dir_elem.attrib.get("path", "").strip()
                if path:
                    input_directories.append(path)

        # Parse output directories with rules
        directory_mappings = []
        rules = []
        transformations = []

        output_dirs_elem = root.find("outputDirectories")
        if output_dirs_elem is not None:
            for dir_elem in output_dirs_elem.findall("directory"):
                output_path = dir_elem.attrib.get("path", "").strip()
                if not output_path:
                    continue

                # Parse governor/comparison for logic operator
                logic_operator = "AND"
                governor_elem = dir_elem.find("governor")
                if governor_elem is not None:
                    comparison_elem = governor_elem.find("comparison")
                    if comparison_elem is not None and comparison_elem.text:
                        logic_operator = comparison_elem.text.strip().upper()

                # Parse rules
                rules_elem = dir_elem.find("rules")
                if rules_elem is not None:
                    dir_rules = self._parse_rules(rules_elem, logic_operator, output_path)
                    rules.extend(dir_rules)

                # Create directory mapping (one per output directory)
                for input_path in input_directories:
                    directory_mappings.append(
                        {
                            "input_path": input_path,
                            "output_path": output_path,
                        }
                    )

        return {
            "name": template_name,
            "rules": rules,
            "directory_mappings": directory_mappings,
            "transformations": transformations,
        }

    def _parse_rules(self, rules_elem: ET.Element, logic_operator: str, output_path: str) -> List[Dict[str, Any]]:
        """
        Parse brownfield XML rules to SchemaRule format.

        Maps brownfield XML rule elements to SchemaRule model fields.
        Supports all CR4 rule types.

        Args:
            rules_elem: XML <rules> element
            logic_operator: AND or OR
            output_path: Output directory path (for context)

        Returns:
            List of rule dictionaries
        """
        rules = []
        priority = 0

        # Brownfield XML rule mapping
        # Format: xml_element_name -> (rule_type, value_extraction_fn)
        rule_mappings = {
            # Video rules
            "containsVideo": ("media_type", lambda elem: "video" if elem.text.lower() == "true" else None),
            "videoOutputContainer": ("extension", lambda elem: elem.text.strip() if elem.text else None),
            # Image rules
            "containsImage": ("media_type", lambda elem: "image" if elem.text.lower() == "true" else None),
            "imageFormat": ("attribute", lambda elem: f"image_format:{elem.text.strip()}" if elem.text else None),
            "exportType": ("extension", lambda elem: elem.text.strip() if elem.text else None),
            # Audio rules
            "containsAudio": ("media_type", lambda elem: "audio" if elem.text.lower() == "true" else None),
            "audioFormat": (
                "attribute",
                lambda elem: f"audio_format:{elem.text.strip()}" if elem.text and elem.text.strip() != "default" else None,
            ),
            "audioSampleRate": (
                "attribute",
                lambda elem: f"sample_rate:{elem.text.strip()}" if elem.text and elem.text.strip() != "default" else None,
            ),
            "audioBitrate": (
                "attribute",
                lambda elem: f"bitrate:{elem.text.strip()}" if elem.text and elem.text.strip() else None,
            ),
            "audioChannels": (
                "attribute",
                lambda elem: f"channels:{elem.text.strip()}" if elem.text else None,
            ),
            "audioNormalize": (
                "attribute",
                lambda elem: f"normalize:{elem.text.strip()}" if elem.text else None,
            ),
            "audioPreserve": (
                "attribute",
                lambda elem: f"preserve:{elem.text.strip()}" if elem.text else None,
            ),
            # Keyword and extension filters
            "expression": ("keyword", lambda elem: elem.text.strip() if elem.text else None),
            "extensions": ("extension", lambda elem: elem.text.strip() if elem.text else None),
            # Date range filters
            "datetimeStart": ("attribute", lambda elem: f"datetime_start:{elem.text.strip()}" if elem.text else None),
            "datetimeEnd": ("attribute", lambda elem: f"datetime_end:{elem.text.strip()}" if elem.text else None),
        }

        # Process each rule mapping
        for xml_elem_name, (rule_type, value_extractor) in rule_mappings.items():
            elem = rules_elem.find(xml_elem_name)
            if elem is not None:
                rule_value = value_extractor(elem)
                if rule_value:
                    rules.append(
                        {
                            "rule_type": rule_type,
                            "rule_value": rule_value,
                            "logic_operator": logic_operator,
                            "priority": priority,
                            "output_path": output_path,  # For context (not stored in SchemaRule)
                        }
                    )
                    priority += 1

        return rules

    @transaction.atomic
    def _import_to_database(self, template_data: Dict[str, Any], xml_source: str) -> Schema:
        """
        Import parsed template data to database.

        Creates Schema, SchemaRule, SchemaTransformation, and DirectoryMapping records
        within a transaction. Rolls back on any error.

        Args:
            template_data: Parsed template data dictionary
            xml_source: Original XML content

        Returns:
            Created Schema instance

        Raises:
            Exception: If database operations fail (triggers rollback)
        """
        # Create Schema
        schema = Schema.objects.create(
            name=template_data["name"],
            xml_source=xml_source,
            source_type="imported",
            is_active=False,  # Don't auto-activate imported templates
        )

        # Create SchemaRules
        for rule_data in template_data["rules"]:
            SchemaRule.objects.create(
                schema=schema,
                rule_type=rule_data["rule_type"],
                rule_value=rule_data["rule_value"],
                logic_operator=rule_data["logic_operator"],
                priority=rule_data["priority"],
            )

        # Create DirectoryMappings
        for mapping_data in template_data["directory_mappings"]:
            DirectoryMapping.objects.create(
                schema=schema,
                input_path=mapping_data["input_path"],
                output_path=mapping_data["output_path"],
                is_watched=False,  # Don't auto-watch imported directories
            )

        # Create SchemaTransformations (if any)
        for transformation_data in template_data["transformations"]:
            SchemaTransformation.objects.create(
                schema=schema,
                output_format=transformation_data["output_format"],
                sample_rate=transformation_data.get("sample_rate"),
                bit_depth=transformation_data.get("bit_depth"),
                normalize_db=transformation_data.get("normalize_db"),
            )

        return schema
