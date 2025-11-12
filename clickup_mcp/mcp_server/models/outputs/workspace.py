"""Result models for Workspace (Team) tools.

These are concise, high-signal shapes returned by MCP tools.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class WorkspaceListItem(BaseModel):
    """Tiny projection for a workspace (team)."""

    team_id: str = Field(..., description="Workspace (team) ID")
    name: str = Field(..., description="Workspace name")


class WorkspaceListResult(BaseModel):
    """Result for workspace.list tool."""

    items: List[WorkspaceListItem] = Field(default_factory=list, description="List of workspaces")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"items": [{"team_id": "team_1", "name": "Engineering"}]}
            ]
        }
    }
