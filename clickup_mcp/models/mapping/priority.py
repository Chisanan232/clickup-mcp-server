"""
Shared priority parsing helpers used across mappers and handlers.

This module provides utility functions for parsing and normalizing priority values
across different representations used in the ClickUp API and MCP server.

Priority Representations Handled:
- Integer form: 1, 2, 3, 4 (1 = Urgent, 4 = Low)
- Numeric string: "1", "2", "3", "4"
- Suffixed string: "priority_1", "priority_2", etc.
- Label form: "Urgent", "High", "Normal", "Low" (case-insensitive)

These helpers avoid duplication and handle common ClickUp variations:
- id as int (1..4)
- id as numeric string ("1")
- id as suffixed string ("priority_1")
- fallback label ("Urgent"|"High"|"Normal"|"Low")

Usage Examples:
    # Python - Parse priority ID
    from clickup_mcp.models.mapping.priority import parse_priority_id

    parse_priority_id(1)  # Returns 1
    parse_priority_id("2")  # Returns 2
    parse_priority_id("priority_3")  # Returns 3
    parse_priority_id("invalid")  # Returns None

    # Python - Parse from label
    from clickup_mcp.models.mapping.priority import priority_label_to_int

    priority_label_to_int("Urgent")  # Returns 1
    priority_label_to_int("high")  # Returns 2 (case-insensitive)
    priority_label_to_int("invalid")  # Returns None

    # Python - Normalize user input
    from clickup_mcp.models.mapping.priority import normalize_priority_input

    normalize_priority_input(1)  # Returns 1
    normalize_priority_input("HIGH")  # Returns 2
    normalize_priority_input(None)  # Returns None
"""

from __future__ import annotations

from typing import Any

from clickup_mcp.models.domain.task_priority import (
    DomainPriority,
    domain_priority_to_int,
)


def parse_priority_id(value: Any) -> int | None:
    """
    Parse a priority id from common forms into 1..4.

    Accepts int, numeric string, or suffixed forms like "priority_1".
    Returns None when unrecognized or out of range.

    Handles multiple priority ID representations:
    - Integer: 1, 2, 3, 4
    - Numeric string: "1", "2", "3", "4"
    - Suffixed string: "priority_1", "priority_2", etc.

    Args:
        value: Priority value in any supported format

    Returns:
        int: Priority level 1-4, or None if invalid/unrecognized

    Usage Examples:
        # Python - Parse integer priority
        parse_priority_id(1)  # Returns 1
        parse_priority_id(5)  # Returns None (out of range)

        # Python - Parse string priority
        parse_priority_id("2")  # Returns 2
        parse_priority_id("priority_3")  # Returns 3

        # Python - Invalid values
        parse_priority_id("invalid")  # Returns None
        parse_priority_id(None)  # Returns None
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value if 1 <= value <= 4 else None
    if isinstance(value, str):
        s = value.strip().lower()
        if s.isdigit():
            n = int(s)
            return n if 1 <= n <= 4 else None
        if s.startswith("priority_"):
            tail = s.rsplit("_", 1)[-1]
            if tail.isdigit():
                n = int(tail)
                return n if 1 <= n <= 4 else None
    return None


def priority_label_to_int(label: Any) -> int | None:
    """
    Map human-readable priority label to ClickUp integer value.

    Converts priority labels like "Urgent", "High", "Normal", "Low" to their
    corresponding integer values (1-4). Case-insensitive.

    Args:
        label: Priority label as string (e.g., "Urgent", "high", "NORMAL")

    Returns:
        int: Priority level 1-4, or None if label isn't a string or isn't recognized

    Mapping:
        - "urgent" → 1
        - "high" → 2
        - "normal" → 3
        - "low" → 4

    Usage Examples:
        # Python - Convert label to priority
        priority_label_to_int("Urgent")  # Returns 1
        priority_label_to_int("high")  # Returns 2 (case-insensitive)
        priority_label_to_int("NORMAL")  # Returns 3

        # Python - Invalid labels
        priority_label_to_int("critical")  # Returns None
        priority_label_to_int(1)  # Returns None (not a string)
        priority_label_to_int(None)  # Returns None
    """
    if not isinstance(label, str):
        return None
    lookup = {"urgent": 1, "high": 2, "normal": 3, "low": 4}
    return lookup.get(label.strip().lower())


def parse_priority_obj(obj: Any) -> int | None:
    """
    Duck-type parse priority from an object with optional 'id' and 'priority' fields.

    Attempts to extract priority from an object by trying multiple strategies:
    1. First tries to parse the 'id' field via parse_priority_id()
    2. Falls back to mapping the 'priority' field (often a human-readable label)

    This is useful for parsing priority from API response objects that may have
    different field names or formats.

    Args:
        obj: Object with optional 'id' and/or 'priority' attributes

    Returns:
        int: Priority level 1-4, or None if priority cannot be determined

    Usage Examples:
        # Python - Parse from object with id field
        class PriorityObj:
            id = 2
            priority = "high"

        parse_priority_obj(PriorityObj())  # Returns 2 (from id field)

        # Python - Parse from object with priority label
        class PriorityObj:
            id = None
            priority = "urgent"

        parse_priority_obj(PriorityObj())  # Returns 1 (from priority field)

        # Python - Invalid object
        parse_priority_obj(None)  # Returns None
        parse_priority_obj({})  # Returns None
    """
    if obj is None:
        return None
    pr = parse_priority_id(getattr(obj, "id", None))
    if pr is not None:
        return pr
    return priority_label_to_int(getattr(obj, "priority", None))


def normalize_priority_input(p: int | str | None) -> int | None:
    """
    Normalize user/input priority to ClickUp integer 1..4.

    Converts user-provided priority input (from MCP tools or other sources) to the
    standard ClickUp integer format (1-4). Accepts either numeric values or
    human-readable labels (case-insensitive).

    Args:
        p: Priority as int (1-4), string label ("URGENT"/"HIGH"/"NORMAL"/"LOW"),
           or None to clear priority

    Returns:
        int: Normalized priority level 1-4, or None if input is None

    Raises:
        ValueError: If priority is an invalid int (not 1-4) or unrecognized label

    Accepted Formats:
        - Integer: 1, 2, 3, 4
        - String labels (case-insensitive): "URGENT", "HIGH", "NORMAL", "LOW"
        - None: Returns None

    Usage Examples:
        # Python - Normalize integer priority
        normalize_priority_input(1)  # Returns 1
        normalize_priority_input(4)  # Returns 4

        # Python - Normalize string labels
        normalize_priority_input("URGENT")  # Returns 1
        normalize_priority_input("high")  # Returns 2 (case-insensitive)
        normalize_priority_input("Normal")  # Returns 3

        # Python - Handle None
        normalize_priority_input(None)  # Returns None

        # Python - Error cases
        try:
            normalize_priority_input(5)  # Raises ValueError (out of range)
        except ValueError as e:
            print(f"Error: {e}")

        try:
            normalize_priority_input("critical")  # Raises ValueError (invalid label)
        except ValueError as e:
            print(f"Error: {e}")
    """
    if p is None:
        return None
    if isinstance(p, int):
        if 1 <= p <= 4:
            return p
        raise ValueError("priority must be 1..4 or a valid label")
    if isinstance(p, str):
        up = p.strip().upper()
        try:
            return domain_priority_to_int(DomainPriority(up))
        except Exception as e:  # noqa: BLE001
            raise ValueError("priority label must be one of URGENT/HIGH/NORMAL/LOW") from e
    return None
