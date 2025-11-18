"""Shared priority parsing helpers used across mappers and handlers.

These helpers avoid duplication and handle common ClickUp variations:
- id as int (1..4)
- id as numeric string ("1")
- id as suffixed string ("priority_1")
- fallback label ("Urgent"|"High"|"Normal"|"Low")
"""

from __future__ import annotations

from typing import Any

from clickup_mcp.models.domain.task_priority import (
    DomainPriority,
    domain_priority_to_int,
)


def parse_priority_id(value: Any) -> int | None:
    """Parse a priority id from common forms into 1..4.

    Accepts int, numeric string, or suffixed forms like "priority_1".
    Returns None when unrecognized or out of range.
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
    """Map human label to ClickUp int value.

    Returns None if label isn't a string or isn't recognized.
    """
    if not isinstance(label, str):
        return None
    lookup = {"urgent": 1, "high": 2, "normal": 3, "low": 4}
    return lookup.get(label.strip().lower())


def parse_priority_obj(obj: Any) -> int | None:
    """Duck-type parse from an object with optional 'id' and 'priority' fields.

    Tries id first via parse_priority_id(); then falls back to mapping the
    'priority' field (often a human-readable label).
    """
    if obj is None:
        return None
    pr = parse_priority_id(getattr(obj, "id", None))
    if pr is not None:
        return pr
    return priority_label_to_int(getattr(obj, "priority", None))


def normalize_priority_input(p: int | str | None) -> int | None:
    """Normalize user/input priority to ClickUp integer 1..4.

    Accepts either 1..4 or label (case-insensitive): URGENT/HIGH/NORMAL/LOW.
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
