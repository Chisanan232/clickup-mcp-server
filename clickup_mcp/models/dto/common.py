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
    if v < 0:
        raise ValueError("epoch ms must be >= 0")
    return v


EpochMs = Annotated[int, AfterValidator(_ms)]


class Priority(IntEnum):
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in progress"
    REVIEW = "review"
    CLOSED = "closed"
