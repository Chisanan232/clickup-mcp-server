"""
Workflow Context DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Workflow Context
operations, including create, update, and list queries. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create context payload
    from clickup_mcp.models.dto.workflow_context import WorkflowContextCreate

    payload = WorkflowContextCreate(
        name="Production Context",
        variables={"priority": "high", "assignee": "user_789"}
    ).to_payload()
    # => {"name": "Production Context", "variables": {"priority": "high", "assignee": "user_789"}}
"""

from typing import Any, Dict, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class WorkflowContextCreate(BaseRequestDTO):
    """
    DTO for creating a new workflow context.

    API:
        POST /workflow/{workflow_id}/context

    Attributes:
        name: Context name
        description: Description of the context
        variables: Dictionary of context variables
        conditions: List of execution conditions
        is_active: Whether the context is active

    Examples:
        WorkflowContextCreate(
            name="Production Context",
            variables={"priority": "high", "assignee": "user_789"}
        ).to_payload()
    """

    name: str = Field(description="Context name")
    description: str | None = Field(default=None, description="Description of the context")
    variables: Dict[str, str] = Field(default_factory=dict, description="Dictionary of context variables")
    conditions: List[str] = Field(default_factory=list, description="List of execution conditions")
    is_active: bool = Field(default=True, description="Whether the context is active")

    def to_payload(self) -> Dict[str, Any]:
        """
        Convert the DTO into a ClickUp create-context request body.

        Returns:
            Dict[str, Any]: JSON-serializable payload with None values removed.
        """
        return self.model_dump(exclude_none=True)


class WorkflowContextUpdate(BaseRequestDTO):
    """
    DTO for updating a workflow context.

    API:
        PUT /workflow/{workflow_id}/context/{context_id}

    Attributes:
        name: New context name
        description: New description
        variables: New variables dictionary
        conditions: New conditions list
        is_active: New active status

    Examples:
        WorkflowContextUpdate(name="Updated Context", is_active=False).to_payload()
    """

    name: str | None = Field(default=None, description="New context name")
    description: str | None = Field(default=None, description="New description")
    variables: Dict[str, str] | None = Field(default=None, description="New variables dictionary")
    conditions: List[str] | None = Field(default=None, description="New conditions list")
    is_active: bool | None = Field(default=None, description="New active status")

    def to_payload(self) -> Dict[str, Any]:
        """
        Convert the DTO into a ClickUp update-context request body.

        Returns:
            Dict[str, Any]: JSON-serializable payload with None values removed.
        """
        return self.model_dump(exclude_none=True)


class WorkflowContextListQuery(BaseRequestDTO):
    """
    DTO for listing workflow contexts with query parameters.

    API:
        GET /workflow/{workflow_id}/context

    Attributes:
        page: Page number (0-indexed)
        limit: Page size (cap 100)

    Examples:
        WorkflowContextListQuery(limit=50).to_query()
    """

    page: int = Field(default=0, description="Page number (0-indexed)")
    limit: int = Field(default=100, description="Page size (cap 100 by API)")

    def to_query(self) -> Dict[str, str]:
        """
        Convert the DTO into ClickUp query parameters.

        Returns:
            Dict[str, str]: Query parameters as string values.
        """
        query: Dict[str, str] = {}
        if self.page is not None:
            query["page"] = str(self.page)
        if self.limit is not None:
            query["limit"] = str(self.limit)
        return query


class WorkflowContextResponse(BaseResponseDTO):
    """
    DTO for workflow context API responses.

    API:
        GET /workflow/{workflow_id}/context/{context_id}
        POST /workflow/{workflow_id}/context
        PUT /workflow/{workflow_id}/context/{context_id}

    Attributes:
        id: Context ID
        workflow_id: Workflow ID
        name: Context name
        description: Description of the context
        variables: Dictionary of context variables
        conditions: List of execution conditions
        is_active: Whether the context is active
        date_created: Creation date in epoch milliseconds
        date_updated: Last update date in epoch milliseconds

    Examples:
        WorkflowContextResponse.deserialize(api_response_data)
    """

    id: str = Field(description="Context ID")
    workflow_id: str = Field(description="Workflow ID")
    name: str = Field(description="Context name")
    description: str | None = Field(default=None, description="Description of the context")
    variables: Dict[str, str] = Field(default_factory=dict, description="Dictionary of context variables")
    conditions: List[str] = Field(default_factory=list, description="List of execution conditions")
    is_active: bool = Field(default=True, description="Whether the context is active")
    date_created: int | None = Field(default=None, description="Creation date in epoch milliseconds")
    date_updated: int | None = Field(default=None, description="Last update date in epoch milliseconds")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "WorkflowContextResponse":
        """
        Deserialize API response data into a WorkflowContextResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            WorkflowContextResponse: Deserialized DTO instance

        Examples:
            WorkflowContextResponse.deserialize({"id": "ctx_123", "name": "Production", ...})
        """
        return cls(**data)


class WorkflowContextListResponse(BaseResponseDTO):
    """
    DTO for workflow context list API responses.

    API:
        GET /workflow/{workflow_id}/context

    Attributes:
        items: List of workflow context responses
        page: Current page number
        limit: Page size
        total: Total number of contexts

    Examples:
        WorkflowContextListResponse.deserialize(api_response_data)
    """

    items: List[WorkflowContextResponse] = Field(default_factory=list, description="List of workflow contexts")
    page: int = Field(default=0, description="Current page number")
    limit: int = Field(default=100, description="Page size")
    total: int | None = Field(default=None, description="Total number of contexts")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "WorkflowContextListResponse":
        """
        Deserialize API response data into a WorkflowContextListResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            WorkflowContextListResponse: Deserialized DTO instance

        Examples:
            WorkflowContextListResponse.deserialize({"items": [...], "page": 0, "limit": 100})
        """
        items_data = data.get("items", [])
        items = [WorkflowContextResponse.deserialize(item) for item in items_data]
        return cls(
            items=items,
            page=data.get("page", 0),
            limit=data.get("limit", 100),
            total=data.get("total"),
        )
