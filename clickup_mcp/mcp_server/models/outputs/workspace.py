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

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"items": [{"team_id": "team_1", "name": "Engineering"}]}]}
    )


class WorkspaceResult(BaseModel):
    """
    Result model for single workspace operations (create, get, update).

    Attributes:
        id: Workspace ID
        name: Workspace name
        color: Workspace color in hex format
        avatar: Workspace avatar URL
    """

    id: str = Field(..., description="Workspace ID", examples=["9018752317"])
    name: str = Field(..., description="Workspace name", examples=["Engineering Team"])
    color: Optional[str] = Field(
        None, description="Workspace color in hex format", examples=["#3498db"], pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    avatar: Optional[str] = Field(None, description="Workspace avatar URL", examples=["https://example.com/avatar.png"])

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"id": "9018752317", "name": "Engineering Team", "color": "#3498db"}]}
    )
