"""Domain-level priority enum and converters.

Source of truth for app-internal semantics. ClickUp provider mapping:
1 = URGENT, 2 = HIGH, 3 = NORMAL, 4 = LOW.
"""

from __future__ import annotations

from enum import Enum


class DomainPriority(str, Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


def int_to_domain_priority(i: int) -> DomainPriority:
    if i == 1:
        return DomainPriority.URGENT
    if i == 2:
        return DomainPriority.HIGH
    if i == 3:
        return DomainPriority.NORMAL
    if i == 4:
        return DomainPriority.LOW
    raise ValueError("priority int must be 1..4")


def domain_priority_to_int(p: DomainPriority) -> int:
    mapping = {
        DomainPriority.URGENT: 1,
        DomainPriority.HIGH: 2,
        DomainPriority.NORMAL: 3,
        DomainPriority.LOW: 4,
    }
    try:
        return mapping[p]
    except KeyError as e:
        raise ValueError(f"unknown DomainPriority: {p}") from e


def domain_priority_label(p: DomainPriority) -> str:
    return p.value
