"""
Base DTOs for ClickUp API requests and responses.

These base classes provide common functionality for all DTOs in the system.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseDTO(BaseModel):
    """Base class for all DTOs in the system."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )

    def serialize(self) -> Dict[str, Any]:
        """Convert the DTO to a dictionary, excluding None values."""
        return self.model_dump(exclude_none=True)


class BaseRequestDTO(BaseDTO):
    """Base class for request DTOs."""

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "BaseRequestDTO":
        """Create a DTO from a dictionary."""
        return cls(**data)


class BaseResponseDTO(BaseDTO):
    """Base class for response DTOs."""

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "BaseResponseDTO":
        """Create a DTO from a dictionary."""
        return cls(**data)


class PaginatedResponseDTO(BaseResponseDTO, Generic[T]):
    """Base class for paginated response DTOs."""

    items: List[T]
    next_page: Optional[str] = None
    prev_page: Optional[str] = None
    total: Optional[int] = None
