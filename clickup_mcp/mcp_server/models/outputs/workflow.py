"""Result models for Workflow tools.

Concise shapes for LLM planning; no raw ClickUp payloads leak.

Usage Examples:
    # Python - Single workflow result
    from clickup_mcp.mcp_server.models.outputs.workflow import WorkflowResult

    wf = WorkflowResult(
        id="wf_1",
        team_id="team_789",
        name="Auto-assign on create",
        trigger_type="task_created",
        is_active=True
    )

    # Python - List result
    lr = WorkflowListResult(items=[WorkflowListItem(id="wf_1", team_id="team_789", name="Auto-assign on create", trigger_type="task_created", is_active=True)])
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class WorkflowResult(BaseModel):
    """Concise workflow automation detail."""

    id: str = Field(..., description="Workflow automation ID", examples=["wf_1", "wf_abc"])
    team_id: str = Field(..., description="Team/workspace ID", examples=["team_789"])
    name: str = Field(..., description="Workflow automation name", examples=["Auto-assign on create"])
    description: Optional[str] = Field(None, description="Description", examples=["Auto-assign tasks when created"])
    trigger_type: str = Field(..., description="Trigger type", examples=["task_created", "status_changed"])
    trigger_config: Optional[dict] = Field(None, description="Trigger configuration", examples=[{"list_id": "456"}])
    actions: List[dict] = Field(default_factory=list, description="Actions to execute", examples=[[{"type": "assign", "user_id": "789"}]])
    is_active: bool = Field(..., description="Whether the workflow is active", examples=[True, False])
    priority: Optional[int] = Field(None, description="Execution priority", examples=[1, 2, 3])
    date_created: Optional[int] = Field(
        None, description="Creation date in epoch milliseconds", examples=[1702000000000]
    )
    date_updated: Optional[int] = Field(
        None, description="Last update date in epoch milliseconds", examples=[1702100000000]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "wf_1",
                    "team_id": "team_789",
                    "name": "Auto-assign on create",
                    "trigger_type": "task_created",
                    "is_active": True,
                }
            ]
        }
    }


class WorkflowListItem(BaseModel):
    """
    Item shape for workflow automation summaries returned by MCP tools.

    Attributes:
        id: Workflow automation ID
        team_id: Team/workspace ID
        name: Workflow automation name
        trigger_type: Trigger type
        is_active: Whether the workflow is active
        priority: Execution priority
    """

    id: str = Field(..., description="Workflow automation ID", examples=["wf_1", "wf_abc"])
    team_id: str = Field(..., description="Team/workspace ID", examples=["team_789"])
    name: str = Field(..., description="Workflow automation name", examples=["Auto-assign on create"])
    trigger_type: str = Field(..., description="Trigger type", examples=["task_created", "status_changed"])
    is_active: bool = Field(..., description="Whether the workflow is active", examples=[True, False])
    priority: Optional[int] = Field(None, description="Execution priority", examples=[1, 2, 3])


class WorkflowListResult(BaseModel):
    """Paged listing, capped to API limit; includes cursor."""

    items: List[WorkflowListItem] = Field(
        default_factory=list,
        examples=[
            [
                {
                    "id": "wf_1",
                    "team_id": "team_789",
                    "name": "Auto-assign on create",
                    "trigger_type": "task_created",
                    "is_active": True,
                }
            ]
        ],
    )
    next_cursor: Optional[str] = Field(None, description="Pass to fetch next page (if present)", examples=["page=2"])
    truncated: bool = Field(False, description="True if items were trimmed to budget", examples=[False])
