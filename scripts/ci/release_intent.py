#!/usr/bin/env python3
"""
Release Intent Parser

Parses .github/tag_and_release/intent.yaml and validates against JSON schema.
Merges defaults with workflow_dispatch inputs and outputs both human-readable
JSON and GitHub Action outputs.

This tool follows PEP 484/585 typing standards and implements robust error
handling with schema validation.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import jsonschema
import jsonschema.exceptions
import yaml

# Type definitions following PEP 585
ReleaseIntent = Dict[str, Any]
SchemaType = Dict[str, Any]


class ReleaseIntentError(Exception):
    """Custom exception for release intent parsing errors."""


def load_schema() -> SchemaType:
    """Load and return the JSON schema for release intent validation."""
    schema_path = Path(".github/tag_and_release/schema.json")

    if not schema_path.exists():
        raise ReleaseIntentError(f"Schema file not found: {schema_path}")

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise ReleaseIntentError(f"Failed to load schema: {e}") from e


def load_intent_file() -> Optional[ReleaseIntent]:
    """Load the release intent YAML file if it exists."""
    intent_path = Path(".github/tag_and_release/intent.yaml")

    if not intent_path.exists():
        return None

    try:
        with open(intent_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:
        raise ReleaseIntentError(f"Failed to load intent file: {e}") from e


def get_workflow_dispatch_inputs() -> ReleaseIntent:
    """Extract workflow_dispatch inputs from environment variables."""
    return {
        "level": os.getenv("INPUT_LEVEL", "").strip(),
        "python": os.getenv("INPUT_PYTHON", "").strip(),
        "docker": os.getenv("INPUT_DOCKER", "").strip(),
        "docs": os.getenv("INPUT_DOCS", "").strip(),
        "notes": os.getenv("INPUT_NOTES", "").strip(),
    }


def get_defaults() -> ReleaseIntent:
    """Return default values for release intent."""
    return {
        "release": True,
        "level": "auto",
        "artifacts": {
            "python": "auto",
            "docker": "auto",
            "docs": "auto",
        },
        "notes": "",
    }


def merge_intent_data(
    defaults: ReleaseIntent, file_data: Optional[ReleaseIntent], workflow_inputs: ReleaseIntent
) -> ReleaseIntent:
    """
    Merge defaults, file data, and workflow inputs in priority order.

    Priority: workflow_inputs > file_data > defaults
    """
    # Start with deep copy of defaults
    merged = defaults.copy()
    merged["artifacts"] = defaults["artifacts"].copy()

    # Apply file data if available
    if file_data:
        # Update top-level keys
        for key, value in file_data.items():
            if key == "artifacts":
                # Handle nested artifacts dict - merge with defaults
                if isinstance(value, dict):
                    merged["artifacts"].update(value)
            else:
                merged[key] = value

    # Apply workflow dispatch inputs (highest priority)
    # Only override if the input is not empty
    if workflow_inputs["level"]:
        merged["level"] = workflow_inputs["level"]
    if workflow_inputs["python"]:
        merged["artifacts"]["python"] = workflow_inputs["python"]
    if workflow_inputs["docker"]:
        merged["artifacts"]["docker"] = workflow_inputs["docker"]
    if workflow_inputs["docs"]:
        # Handle docs carefully - don't override complex object with simple string
        if isinstance(merged["artifacts"]["docs"], dict):
            # If file config has complex docs object, only override mode if input is specific
            if workflow_inputs["docs"] in ["skip", "force"]:
                merged["artifacts"]["docs"]["mode"] = workflow_inputs["docs"]
            # Otherwise preserve the complex configuration from file
        else:
            # If file config has simple string, replace it
            merged["artifacts"]["docs"] = workflow_inputs["docs"]
    if workflow_inputs["notes"]:
        merged["notes"] = workflow_inputs["notes"]

    return merged


def parse_docs_config(docs_artifact: Any) -> tuple[str, str, str]:
    """
    Parse docs artifact and return (mode, sections, strategy).

    Args:
        docs_artifact: Either a string or dict with docs configuration

    Returns:
        Tuple of (mode, sections_json, strategy)
    """
    if isinstance(docs_artifact, str):
        # Legacy string format - convert to new format
        if docs_artifact == "skip":
            return "skip", "[]", "all"
        elif docs_artifact == "auto":
            return "auto", '["docs", "dev"]', "all"
        else:
            # Assume it's a mode value
            return docs_artifact, '["docs", "dev"]', "all"

    elif isinstance(docs_artifact, dict):
        # New object format
        mode = docs_artifact.get("mode", "auto")
        sections = docs_artifact.get("sections", ["docs", "dev"])
        strategy = docs_artifact.get("strategy", "all")

        # Convert sections list to JSON string for output
        sections_json = json.dumps(sections)

        return mode, sections_json, strategy

    else:
        # Fallback to defaults
        return "auto", '["docs", "dev"]', "all"


def validate_intent(intent: ReleaseIntent, schema: SchemaType) -> None:
    """Validate the release intent against the JSON schema."""
    try:
        validator = jsonschema.Draft202012Validator(schema)
        validator.validate(intent)
    except jsonschema.ValidationError as e:
        raise ReleaseIntentError(f"Intent validation failed: {e.message}") from e
    except (jsonschema.SchemaError, jsonschema.exceptions.UnknownType) as e:
        raise ReleaseIntentError(f"Schema validation failed: {e}") from e


def write_github_outputs(intent: ReleaseIntent) -> None:
    """Write GitHub Action outputs to $GITHUB_OUTPUT."""
    github_output = os.getenv("GITHUB_OUTPUT")
    if not github_output:
        # Running locally, skip GitHub output
        return

    # Parse docs configuration
    docs_mode, docs_sections, docs_strategy = parse_docs_config(intent["artifacts"]["docs"])

    try:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"do_release={'true' if intent['release'] else 'false'}\n")
            f.write(f"level={intent['level']}\n")
            f.write(f"python={intent['artifacts']['python']}\n")
            f.write(f"docker={intent['artifacts']['docker']}\n")
            # Legacy docs output for backward compatibility
            if isinstance(intent["artifacts"]["docs"], str):
                f.write(f"docs={intent['artifacts']['docs']}\n")
            else:
                f.write(f"docs={docs_mode}\n")
            # New docs outputs
            f.write(f"docs_mode={docs_mode}\n")
            f.write(f"docs_sections={docs_sections}\n")
            f.write(f"docs_strategy={docs_strategy}\n")
            f.write(f"notes={intent['notes']}\n")
    except OSError as e:
        raise ReleaseIntentError(f"Failed to write GitHub outputs: {e}") from e


def main() -> int:
    """
    Main entry point for the release intent parser.

    Returns:
        0 on success (including when release is skipped)
        1 on error
    """
    try:
        # Load schema
        schema = load_schema()

        # Load intent file (may not exist)
        file_data = load_intent_file()

        # Get workflow dispatch inputs
        workflow_inputs = get_workflow_dispatch_inputs()

        # Get defaults and merge all data
        defaults = get_defaults()
        merged_intent = merge_intent_data(defaults, file_data, workflow_inputs)

        # Validate merged intent
        validate_intent(merged_intent, schema)

        # Output human-readable JSON to stdout
        print(json.dumps(merged_intent, indent=2, sort_keys=True))

        # Write GitHub Action outputs
        write_github_outputs(merged_intent)

        return 0

    except ReleaseIntentError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
