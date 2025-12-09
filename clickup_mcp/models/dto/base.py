"""
Base DTOs for ClickUp API requests and responses.

These base classes provide common behavior for all DTOs, including:
- Deterministic serialization (excludes None)
- Flexible field population via aliases (populate_by_name=True)
- Forward-compatible parsing (extra="allow")

Usage Examples:
    # Define a request DTO and serialize to API payload
    from typing import Optional
    from clickup_mcp.models.dto.base import BaseRequestDTO, BaseResponseDTO, PaginatedResponseDTO

    class MyRequest(BaseRequestDTO):
        name: str
        description: Optional[str] = None

    payload = MyRequest(name="New Space").to_payload()
    # payload == {"name": "New Space"}

    # Deserialize a response DTO
    class MyResponse(BaseResponseDTO):
        id: str
        name: str

    resp = MyResponse.deserialize({"id": "spc_1", "name": "Engineering"})
    # resp.id == "spc_1"

    # Paginated results
    class MyList(PaginatedResponseDTO[MyResponse]):
        items: list[MyResponse]

    listing = MyList(items=[resp], next_page="cursor=2")
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseDTO(BaseModel):
    """
    Base class for all DTOs.

    Features:
    - Allows population by field name or alias
    - Permissive to unknown fields for forward compatibility
    - Provides helper serialization with None filtering
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )

    def serialize(self) -> dict[str, Any]:
        """
        Convert the DTO into a plain dictionary.

        Returns:
            dict[str, Any]: Dictionary representation with None values removed

        Examples:
            dto.serialize()  # { ... }
        """
        return self.model_dump(exclude_none=True)


class BaseRequestDTO(BaseDTO):
    """
    Base class for request DTOs.

    Notes:
        Use `to_payload()` to produce API-ready request bodies. This method
        filters out None values to avoid sending unset fields.
    """

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "BaseRequestDTO":
        """
        Create a request DTO instance from a dictionary.

        Args:
            data: Raw mapping (e.g., user input) to construct the DTO

        Returns:
            BaseRequestDTO: Parsed and validated instance
        """
        return cls(**data)

    def to_payload(self) -> dict[str, Any]:
        """
        Serialize the DTO into an API payload.

        Returns:
            dict[str, Any]: Dictionary suitable for JSON request bodies with None values removed

        Examples:
            # Only non-None fields are included
            # MyRequest(name="X", description=None).to_payload() -> {"name": "X"}
        """
        return self.model_dump(exclude_none=True)


class BaseResponseDTO(BaseDTO):
    """
    Base class for response DTOs.

    Notes:
        Use `deserialize()` to build from raw JSON responses.
    """

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "BaseResponseDTO":
        """
        Create a response DTO instance from a dictionary.

        Args:
            data: Raw API JSON mapping to construct the DTO

        Returns:
            BaseResponseDTO: Parsed and validated instance
        """
        return cls(**data)


class PaginatedResponseDTO(BaseResponseDTO, Generic[T]):
    """
    Base class for paginated response DTOs.

    Attributes:
        items: The current page of items
        next_page: Cursor/token to request the next page (if present)
        prev_page: Cursor/token to request the previous page (if present)
        total: Total number of items if provided by the API

    Examples:
        # Build a typed page of results
        page = PaginatedResponseDTO[MyResponse](
            items=[MyResponse(id="1", name="A")],
            next_page="cursor=2",
        )
    """

    items: list[T]
    next_page: str | None = None
    prev_page: str | None = None
    total: int | None = None
