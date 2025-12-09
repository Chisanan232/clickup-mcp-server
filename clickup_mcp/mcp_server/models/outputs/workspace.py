"""
Result models for Workspace (Team) tools.

These are concise, high-signal shapes returned by MCP tools when listing
workspaces (teams). Optimized for LLM consumption.

Usage Examples:
    # Python - Single item
    from clickup_mcp.mcp_server.models.outputs.workspace import WorkspaceListItem, WorkspaceListResult
    item = WorkspaceListItem(team_id="team_1", name="Engineering")

    # Python - List result
    result = WorkspaceListResult(items=[item])
"""

from typing import List

from pydantic import BaseModel, Field


class WorkspaceListItem(BaseModel):
    """
    Tiny projection for a workspace (team).

    Attributes:
        team_id: Workspace (team) ID
        name: Workspace (team) display name
    """

    team_id: str = Field(..., description="Workspace (team) ID", examples=["team_1", "9018752317"])
    name: str = Field(..., description="Workspace name", examples=["Engineering", "Ops"])


class WorkspaceListResult(BaseModel):
    """
    Result wrapper for `workspace.list` tool.

    Attributes:
        items: Workspaces available to the current token
    """

    items: List[WorkspaceListItem] = Field(
        default_factory=list,
        description="List of workspaces",
        examples=[[{"team_id": "team_1", "name": "Engineering"}]],
    )

    model_config = {"json_schema_extra": {"examples": [{"items": [{"team_id": "team_1", "name": "Engineering"}]}]}}
