"""
Common DTO primitives, enums, and strong ID aliases used across ClickUp models.

This module defines:
- Strongly-typed ID aliases (TeamId, SpaceId, FolderId, ListId, TaskId, UserId)
- EpochMs annotated type with validation (non-negative milliseconds)
- Priority enum mapped to ClickUp's 1..4 values
- TaskStatus enum with common lifecycle states

Usage Examples:
    # Python - Validate EpochMs
    from clickup_mcp.models.dto.common import EpochMs
    def takes_epoch_ms(ts: EpochMs) -> None: ...
    takes_epoch_ms(1702080000000)  # OK
    # takes_epoch_ms(-1)  # Raises ValueError

    # Python - Use Priority
    from clickup_mcp.models.dto.common import Priority
    assert Priority.URGENT == 1

    # Python - Use TaskStatus
    from clickup_mcp.models.dto.common import TaskStatus
    assert TaskStatus.OPEN == "open"
"""

from enum import Enum, IntEnum
from typing import Annotated, NewType

from pydantic import AfterValidator

# Strong ID aliases
TeamId = NewType("TeamId", str)
SpaceId = NewType("SpaceId", str)
FolderId = NewType("FolderId", str)
ListId = NewType("ListId", str)
TaskId = NewType("TaskId", str)
UserId = NewType("UserId", int)


def _ms(v: int) -> int:
    """
    Validate non-negative epoch milliseconds.

    Args:
        v: Epoch timestamp in milliseconds

    Returns:
        int: The validated value when v >= 0

    Raises:
        ValueError: If v < 0
    """
    if v < 0:
        raise ValueError("epoch ms must be >= 0")
    return v


EpochMs = Annotated[int, AfterValidator(_ms)]
"""Annotated integer representing epoch milliseconds (non-negative)."""


class Priority(IntEnum):
    """
    ClickUp priority levels mapped to integers 1..4.

    Values:
        URGENT (1), HIGH (2), NORMAL (3), LOW (4)
    """

    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class TaskStatus(str, Enum):
    """
    Common task lifecycle statuses used in ClickUp.

    Values:
        OPEN, IN_PROGRESS, REVIEW, CLOSED
    """

    OPEN = "open"
    IN_PROGRESS = "in progress"
    REVIEW = "review"
    CLOSED = "closed"
