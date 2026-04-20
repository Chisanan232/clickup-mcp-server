"""MCP input models for workflow automation operations.

These inputs are LLM-friendly contracts used by FastMCP tools. They map to
Domain entities first, then DTOs for ClickUp wire format.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkflowCreateInput(BaseModel):
    """
    Create a workflow automation. HTTP: POST /team/{team_id}/workflow

    When to use: Create an automation rule that triggers actions based on events.

    Constraints:
        - `trigger_type` must be a valid ClickUp trigger type
        - At least one action must be specified
        - Time fields are epoch milliseconds

    Attributes:
        team_id: Team/workspace ID
        name: Workflow automation name
        description: Description of the automation
        trigger_type: Type of trigger (e.g., task_created, status_changed)
        trigger_config: Configuration for the trigger
        actions: List of actions to execute
        is_active: Whether the workflow is active
        priority: Execution priority

    Examples:
        WorkflowCreateInput(team_id="123", name="Auto-assign on create", trigger_type="task_created")
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "team_id": "123",
                    "name": "Auto-assign on create",
                    "trigger_type": "task_created",
                    "trigger_config": {"list_id": "456"},
                    "actions": [{"type": "assign", "user_id": "789"}],
                    "is_active": True,
                }
            ]
        }
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["123", "team_1"])
    name: str = Field(..., min_length=1, description="Workflow automation name.", examples=["Auto-assign on create"])
    description: Optional[str] = Field(
        None, description="Description of the automation.", examples=["Auto-assign tasks when created in list 456"]
    )
    trigger_type: str = Field(
        ...,
        min_length=1,
        description="Type of trigger (e.g., task_created, status_changed).",
        examples=["task_created", "status_changed"],
    )
    trigger_config: Optional[dict] = Field(
        None, description="Configuration for the trigger.", examples=[{"list_id": "456"}, {"status": "done"}]
    )
    actions: List[dict] = Field(
        default_factory=list,
        description="List of actions to execute.",
        examples=[[{"type": "assign", "user_id": "789"}]],
    )
    is_active: bool = Field(True, description="Whether the workflow is active.", examples=[True, False])
    priority: Optional[int] = Field(None, description="Execution priority.", examples=[1, 2, 3])


class WorkflowUpdateInput(BaseModel):
    """
    Update a workflow automation. HTTP: PUT /workflow/{workflow_id}

    When to use: Modify an existing workflow automation's configuration.

    Attributes:
        workflow_id: Workflow automation ID
        name: New workflow name
        description: New description
        trigger_type: New trigger type
        trigger_config: New trigger configuration
        actions: New list of actions
        is_active: New active status
        priority: New priority

    Examples:
        WorkflowUpdateInput(workflow_id="wf_123", name="Updated name", is_active=False)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"workflow_id": "wf_123", "name": "Updated name", "is_active": False},
            ]
        }
    )

    workflow_id: str = Field(..., min_length=1, description="Workflow automation ID.", examples=["wf_123"])
    name: Optional[str] = Field(None, min_length=1, description="New workflow name.", examples=["Updated name"])
    description: Optional[str] = Field(None, description="New description.", examples=["Updated description"])
    trigger_type: Optional[str] = Field(None, description="New trigger type.", examples=["status_changed"])
    trigger_config: Optional[dict] = Field(
        None, description="New trigger configuration.", examples=[{"status": "done"}]
    )
    actions: Optional[List[dict]] = Field(
        None, description="New list of actions.", examples=[[{"type": "assign", "user_id": "789"}]]
    )
    is_active: Optional[bool] = Field(None, description="New active status.", examples=[True, False])
    priority: Optional[int] = Field(None, description="New priority.", examples=[1, 2, 3])


class WorkflowGetInput(BaseModel):
    """
    Get a workflow automation. HTTP: GET /workflow/{workflow_id}

    When to use: Retrieve details of a specific workflow automation.

    Attributes:
        workflow_id: Workflow automation ID

    Examples:
        WorkflowGetInput(workflow_id="wf_123")
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"workflow_id": "wf_123"},
            ]
        }
    )

    workflow_id: str = Field(..., min_length=1, description="Workflow automation ID.", examples=["wf_123"])


class WorkflowDeleteInput(BaseModel):
    """
    Delete a workflow automation. HTTP: DELETE /workflow/{workflow_id}

    When to use: Remove a workflow automation.

    Attributes:
        workflow_id: Workflow automation ID

    Examples:
        WorkflowDeleteInput(workflow_id="wf_123")
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"workflow_id": "wf_123"},
            ]
        }
    )

    workflow_id: str = Field(..., min_length=1, description="Workflow automation ID.", examples=["wf_123"])


class WorkflowListInput(BaseModel):
    """
    List workflow automations. HTTP: GET /team/{team_id}/workflow

    When to use: Retrieve all workflow automations for a team.

    Constraints:
        - `limit` ≤ 100 per API

    Attributes:
        team_id: Team/workspace ID
        page: Page number (0-indexed)
        limit: Page size (cap 100)
        is_active: Filter by active status

    Examples:
        WorkflowListInput(team_id="123", limit=50)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"team_id": "123", "limit": 50},
                {"team_id": "123", "is_active": True},
            ]
        }
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["123", "team_1"])
    page: int = Field(0, ge=0, description="Page number (0-indexed).", examples=[0, 1, 2])
    limit: int = Field(100, ge=1, le=100, description="Page size (cap 100 by API).", examples=[25, 50, 100])
    is_active: Optional[bool] = Field(None, description="Filter by active status.", examples=[True, False])
