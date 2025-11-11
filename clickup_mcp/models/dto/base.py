"""
Base DTOs for ClickUp API requests and responses.

These base classes provide common functionality for all DTOs in the system.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseDTO(BaseModel):
    """Base class for all DTOs in the system."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )

    def serialize(self) -> dict[str, Any]:
        """Convert the DTO to a dictionary, excluding None values."""
        return self.model_dump(exclude_none=True)


class BaseRequestDTO(BaseDTO):
    """Base class for request DTOs."""

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "BaseRequestDTO":
        """Create a DTO from a dictionary."""
        return cls(**data)

    def to_payload(self) -> dict[str, Any]:
        """Default payload serialization with snake_case keys and no None values."""
        return self.model_dump(exclude_none=True)


class BaseResponseDTO(BaseDTO):
    """Base class for response DTOs."""

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "BaseResponseDTO":
        """Create a DTO from a dictionary."""
        return cls(**data)


class PaginatedResponseDTO(BaseResponseDTO, Generic[T]):
    """Base class for paginated response DTOs."""

    items: list[T]
    next_page: str | None = None
    prev_page: str | None = None
    total: int | None = None
