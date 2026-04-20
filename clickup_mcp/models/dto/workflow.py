"""
Workflow DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Workflow
operations, including create, update, and list queries. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create workflow payload
    from clickup_mcp.models.dto.workflow import WorkflowCreate

    payload = WorkflowCreate(
        name="Auto-assign on create",
        trigger_type="task_created",
        trigger_config={"list_id": "456"},
        actions=[{"type": "assign", "user_id": "789"}]
    ).to_payload()
    # => {"name": "Auto-assign on create", "trigger_type": "task_created", ...}
"""

from typing import Any, Dict, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class WorkflowCreate(BaseRequestDTO):
    """
    DTO for creating a new workflow automation.

    API:
        POST /team/{team_id}/workflow

    Attributes:
        name: Workflow automation name
        description: Description of the automation
        trigger_type: Type of trigger (e.g., task_created, status_changed)
        trigger_config: Configuration for the trigger
        actions: List of actions to execute
        is_active: Whether the workflow is active
        priority: Execution priority

    Examples:
        WorkflowCreate(
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "456"},
            actions=[{"type": "assign", "user_id": "789"}]
        ).to_payload()
    """

    name: str = Field(description="Workflow automation name")
    description: str | None = Field(default=None, description="Description of the automation")
    trigger_type: str = Field(description="Type of trigger (e.g., 'task_created', 'status_changed')")
    trigger_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for the trigger")
    actions: List[Dict[str, Any]] = Field(default_factory=list, description="List of actions to execute")
    is_active: bool = Field(default=True, description="Whether the workflow is active")
    priority: int | None = Field(default=None, description="Execution priority")

    def to_payload(self) -> Dict[str, Any]:
        """
        Convert the DTO into a ClickUp create-workflow request body.

        Returns:
            Dict[str, Any]: JSON-serializable payload with None values removed.
        """
        return self.model_dump(exclude_none=True)


class WorkflowUpdate(BaseRequestDTO):
    """
    DTO for updating a workflow automation.

    API:
        PUT /workflow/{workflow_id}

    Attributes:
        name: New workflow name
        description: New description
        trigger_type: New trigger type
        trigger_config: New trigger configuration
        actions: New list of actions
        is_active: New active status
        priority: New priority

    Examples:
        WorkflowUpdate(name="Updated name", is_active=False).to_payload()
    """

    name: str | None = Field(default=None, description="New workflow name")
    description: str | None = Field(default=None, description="New description")
    trigger_type: str | None = Field(default=None, description="New trigger type")
    trigger_config: Dict[str, Any] | None = Field(default=None, description="New trigger configuration")
    actions: List[Dict[str, Any]] | None = Field(default=None, description="New list of actions")
    is_active: bool | None = Field(default=None, description="New active status")
    priority: int | None = Field(default=None, description="New priority")

    def to_payload(self) -> Dict[str, Any]:
        """
        Convert the DTO into a ClickUp update-workflow request body.

        Returns:
            Dict[str, Any]: JSON-serializable payload with None values removed.
        """
        return self.model_dump(exclude_none=True)


class WorkflowListQuery(BaseRequestDTO):
    """
    DTO for listing workflow automations with query parameters.

    API:
        GET /team/{team_id}/workflow

    Attributes:
        page: Page number (0-indexed)
        limit: Page size (cap 100)
        is_active: Filter by active status

    Examples:
        WorkflowListQuery(limit=50, is_active=True).to_query()
    """

    page: int = Field(default=0, description="Page number (0-indexed)")
    limit: int = Field(default=100, description="Page size (cap 100 by API)")
    is_active: bool | None = Field(default=None, description="Filter by active status")

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
        if self.is_active is not None:
            query["is_active"] = str(self.is_active).lower()
        return query


class WorkflowResponse(BaseResponseDTO):
    """
    DTO for workflow automation API responses.

    API:
        GET /workflow/{workflow_id}
        POST /team/{team_id}/workflow
        PUT /workflow/{workflow_id}

    Attributes:
        id: Workflow automation ID
        team_id: Team/workspace ID
        name: Workflow automation name
        description: Description of the automation
        trigger_type: Type of trigger
        trigger_config: Configuration for the trigger
        actions: List of actions to execute
        is_active: Whether the workflow is active
        priority: Execution priority
        date_created: Creation date in epoch milliseconds
        date_updated: Last update date in epoch milliseconds

    Examples:
        WorkflowResponse.deserialize(api_response_data)
    """

    id: str = Field(description="Workflow automation ID")
    team_id: str = Field(description="Team/workspace ID")
    name: str = Field(description="Workflow automation name")
    description: str | None = Field(default=None, description="Description of the automation")
    trigger_type: str = Field(description="Type of trigger")
    trigger_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for the trigger")
    actions: List[Dict[str, Any]] = Field(default_factory=list, description="List of actions to execute")
    is_active: bool = Field(default=True, description="Whether the workflow is active")
    priority: int | None = Field(default=None, description="Execution priority")
    date_created: int | None = Field(default=None, description="Creation date in epoch milliseconds")
    date_updated: int | None = Field(default=None, description="Last update date in epoch milliseconds")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "WorkflowResponse":
        """
        Deserialize API response data into a WorkflowResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            WorkflowResponse: Deserialized DTO instance

        Examples:
            WorkflowResponse.deserialize({"id": "wf_123", "name": "Auto-assign", ...})
        """
        return cls(**data)


class WorkflowListResponse(BaseResponseDTO):
    """
    DTO for workflow automation list API responses.

    API:
        GET /team/{team_id}/workflow

    Attributes:
        items: List of workflow automation responses
        page: Current page number
        limit: Page size
        total: Total number of workflows

    Examples:
        WorkflowListResponse.deserialize(api_response_data)
    """

    items: List[WorkflowResponse] = Field(default_factory=list, description="List of workflow automations")
    page: int = Field(default=0, description="Current page number")
    limit: int = Field(default=100, description="Page size")
    total: int | None = Field(default=None, description="Total number of workflows")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "WorkflowListResponse":
        """
        Deserialize API response data into a WorkflowListResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            WorkflowListResponse: Deserialized DTO instance

        Examples:
            WorkflowListResponse.deserialize({"items": [...], "page": 0, "limit": 100})
        """
        items_data = data.get("items", [])
        items = [WorkflowResponse.deserialize(item) for item in items_data]
        return cls(
            items=items,
            page=data.get("page", 0),
            limit=data.get("limit", 100),
            total=data.get("total"),
        )
