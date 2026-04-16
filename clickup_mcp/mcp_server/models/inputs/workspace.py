"""MCP input models for workspace operations.

High-signal schemas for FastMCP: include constraints and examples to aid LLMs.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreateInput(BaseModel):
    """
    Create a workspace. HTTP: POST /team

    When to use: You want to create a new workspace with custom settings.
    Notes: Workspaces are the top-level organization in ClickUp.

    Attributes:
        name: Workspace name
        color: Workspace color for UI
        avatar: Workspace avatar URL

    Examples:
        WorkspaceCreateInput(name="Engineering Team", color="#3498db")
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"name": "Engineering Team", "color": "#3498db"}]})

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Workspace name.",
        examples=["Engineering Team", "Product", "Marketing"],
    )
    color: Optional[str] = Field(
        None,
        description="Workspace color in hex format.",
        examples=["#3498db", "#e74c3c", "#2ecc71"],
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    avatar: Optional[str] = Field(
        None,
        description="Workspace avatar URL.",
        examples=["https://example.com/avatar.png"],
    )


class WorkspaceGetInput(BaseModel):
    """
    Get a workspace. HTTP: GET /team/{team_id}

    When to use: Retrieve details for a single workspace by ID.

    Attributes:
        workspace_id: Workspace ID

    Examples:
        WorkspaceGetInput(workspace_id="9018752317")
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"workspace_id": "9018752317"}]})

    workspace_id: str = Field(..., min_length=1, description="Workspace ID.", examples=["9018752317", "team_1"])


class WorkspaceUpdateInput(BaseModel):
    """
    Update a workspace. HTTP: PUT /team/{team_id}

    When to use: Change workspace attributes like name, color, or avatar.

    Attributes:
        workspace_id: Workspace ID
        name: New workspace name
        color: New workspace color
        avatar: New workspace avatar URL

    Examples:
        WorkspaceUpdateInput(workspace_id="9018752317", name="Updated Team Name")
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"workspace_id": "9018752317", "name": "Updated Team Name"},
                {"workspace_id": "9018752317", "color": "#e74c3c"},
            ]
        }
    )

    workspace_id: str = Field(..., min_length=1, description="Workspace ID.", examples=["9018752317", "team_1"])
    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Workspace name.", examples=["Engineering Team", "Product"]
    )
    color: Optional[str] = Field(
        None,
        description="Workspace color in hex format.",
        examples=["#3498db", "#e74c3c", "#2ecc71"],
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    avatar: Optional[str] = Field(
        None,
        description="Workspace avatar URL.",
        examples=["https://example.com/avatar.png"],
    )


class WorkspaceDeleteInput(BaseModel):
    """
    Delete a workspace. HTTP: DELETE /team/{team_id}

    When to use: Permanently remove a workspace. Ensure no critical data is lost.

    Attributes:
        workspace_id: Workspace ID

    Examples:
        WorkspaceDeleteInput(workspace_id="9018752317")
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"workspace_id": "9018752317"}]})

    workspace_id: str = Field(..., min_length=1, description="Workspace ID.", examples=["9018752317", "team_1"])


class WorkspaceListInput(BaseModel):
    """
    List workspaces. HTTP: GET /team

    When to use: Discover all workspaces accessible to the user.

    Examples:
        WorkspaceListInput()
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{}]})
