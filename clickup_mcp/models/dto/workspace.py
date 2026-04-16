"""
Workspace DTOs for ClickUp API requests and responses.

These DTOs provide serialization/deserialization helpers for Workspace operations
(create, update, get, delete). Request DTOs inherit from `BaseRequestDTO` and exclude
None values; response DTOs inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create workspace payload
    from clickup_mcp.models.dto.workspace import WorkspaceCreate

    payload = WorkspaceCreate(
        name="Engineering Team",
        color="#3498db"
    ).to_payload()
    # => {"name": "Engineering Team", "color": "#3498db"}
"""

from typing import Any

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO

PROPERTY_NAME_DESCRIPTION: str = "The name of the workspace"


class WorkspaceCreate(BaseRequestDTO):
    """
    DTO for creating a new workspace.

    API:
        POST /team
        Docs: https://developer.clickup.com/reference/createteam

    Attributes:
        name: Workspace name
        color: Optional hex color for the workspace
        avatar: Optional avatar URL for the workspace

    Examples:
        # Python - Serialize create payload
        WorkspaceCreate(name="Engineering Team", color="#3498db").to_payload()
    """

    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    color: str | None = Field(default=None, description="Hex color for the workspace", pattern=r"^#[0-9A-Fa-f]{6}$")
    avatar: str | None = Field(default=None, description="Avatar URL for the workspace")


class WorkspaceUpdate(BaseRequestDTO):
    """
    DTO for updating an existing workspace.

    API:
        PUT /team/{team_id}

    Attributes:
        name: New workspace name
        color: Hex color for the workspace
        avatar: Avatar URL for the workspace

    Examples:
        # Python
        WorkspaceUpdate(name="Updated Team Name").to_payload()
    """

    name: str | None = Field(default=None, description=PROPERTY_NAME_DESCRIPTION)
    color: str | None = Field(default=None, description="Hex color for the workspace", pattern=r"^#[0-9A-Fa-f]{6}$")
    avatar: str | None = Field(default=None, description="Avatar URL for the workspace")


class WorkspaceResp(BaseResponseDTO):
    """
    DTO for workspace API responses.

    Represents a workspace returned from the ClickUp API.

    Attributes:
        id: Workspace ID
        name: Workspace name
        color: Workspace color
        avatar: Workspace avatar URL
        members: List of workspace members
        settings: Workspace settings

    Examples:
        # Python - Deserialize from API JSON
        WorkspaceResp.deserialize({"id": "9018752317", "name": "Engineering Team"})
    """

    id: str = Field(description="The unique identifier for the workspace")
    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    color: str | None = Field(default=None, description="Hex color for the workspace")
    avatar: str | None = Field(default=None, description="Avatar URL for the workspace")
    members: list[dict[str, Any]] = Field(default_factory=list, description="List of workspace members")
    settings: dict[str, Any] | None = Field(default=None, description="Workspace settings")
