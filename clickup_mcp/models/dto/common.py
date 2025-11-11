from typing import NewType, Annotated
from pydantic import AfterValidator
from enum import IntEnum, Enum

# Strong ID aliases
TeamId = NewType("TeamId", str)
SpaceId = NewType("SpaceId", str)
FolderId = NewType("FolderId", str)
ListId = NewType("ListId", str)
TaskId = NewType("TaskId", str)
UserId = NewType("UserId", int)


def _ms(v: int) -> int:
    if v < 0:
        raise ValueError("epoch ms must be >= 0")
    return v


EpochMs = Annotated[int, AfterValidator(_ms)]


class Priority(IntEnum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in progress"
    REVIEW = "review"
    CLOSED = "closed"
