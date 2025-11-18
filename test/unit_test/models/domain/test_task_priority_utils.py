"""Unit tests for DomainPriority converters."""

import pytest

from clickup_mcp.models.domain.task_priority import (
    DomainPriority,
    domain_priority_label,
    domain_priority_to_int,
    int_to_domain_priority,
)


def test_int_to_domain_priority_round_trip_valid() -> None:
    assert int_to_domain_priority(1) == DomainPriority.URGENT
    assert int_to_domain_priority(2) == DomainPriority.HIGH
    assert int_to_domain_priority(3) == DomainPriority.NORMAL
    assert int_to_domain_priority(4) == DomainPriority.LOW

    assert domain_priority_to_int(DomainPriority.URGENT) == 1
    assert domain_priority_to_int(DomainPriority.HIGH) == 2
    assert domain_priority_to_int(DomainPriority.NORMAL) == 3
    assert domain_priority_to_int(DomainPriority.LOW) == 4


def test_int_to_domain_priority_invalid_raises() -> None:
    with pytest.raises(ValueError):
        int_to_domain_priority(0)
    with pytest.raises(ValueError):
        int_to_domain_priority(5)


def test_domain_priority_label() -> None:
    assert domain_priority_label(DomainPriority.URGENT) == "URGENT"
    assert domain_priority_label(DomainPriority.HIGH) == "HIGH"
    assert domain_priority_label(DomainPriority.NORMAL) == "NORMAL"
    assert domain_priority_label(DomainPriority.LOW) == "LOW"


def test_domain_priority_to_int_invalid_type_raises_with_message() -> None:
    # Passing a non-DomainPriority should raise ValueError via the KeyError branch
    with pytest.raises(ValueError) as excinfo:
        domain_priority_to_int("INVALID")  # type: ignore[arg-type]
    assert "unknown DomainPriority" in str(excinfo.value)

    # Also verify with a different enum instance
    from enum import Enum

    class Fake(Enum):
        FOO = "FOO"

    with pytest.raises(ValueError):
        domain_priority_to_int(Fake.FOO)  # type: ignore[arg-type]
