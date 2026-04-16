"""
Domain model for ClickUp Workspace (Team).

This module defines the domain model for a ClickUp Workspace, which is used
throughout the application to represent a workspace in a vendor-agnostic way.

A Workspace (also called Team in ClickUp API) is the top-level organizational
unit in ClickUp. Workspaces contain Spaces, which in turn contain Folders and Lists.
Workspaces define organization-level settings like billing, users, and permissions.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Focuses on business logic and invariants
- References other aggregates by identity only
- Immutable once created (uses Pydantic's frozen model pattern)
- Type-safe with clear field definitions

Usage Examples:
    # Python - Create a workspace domain entity
    from clickup_mcp.models.domain.workspace import ClickUpWorkspace

    workspace = ClickUpWorkspace(
        id="9018752317",
        name="Engineering Team",
        color="#3498db"
    )

    # Python - Access workspace properties
    print(workspace.id)  # "9018752317"
    print(workspace.name)  # "Engineering Team"

    # Python - Check workspace settings
    if workspace.color:
        print(f"Workspace color: {workspace.color}")
"""

from typing import Any

from pydantic import ConfigDict, Field, model_validator

from .base import BaseDomainModel


class ClickUpWorkspace(BaseDomainModel):
    """
    Domain model for a ClickUp Workspace (Team).

    This model represents a Workspace (also called Team in ClickUp API) in ClickUp
    and includes all relevant fields from the ClickUp API. A Workspace is the
    top-level organizational unit containing spaces, folders, lists, and tasks.

    In ClickUp's hierarchy:
    - Workspace (Team) → Space → Folder → List → Task

    Attributes:
        workspace_id: The unique identifier for the workspace (aliased as 'id' for compatibility)
        name: The name of the workspace
        color: The workspace color in hex format for UI
        avatar: The workspace avatar URL
        members: List of workspace members
        settings: Dictionary of workspace settings

    Key Design Features:
    - Backward-compatible 'id' property that returns workspace_id
    - Flexible field population (populate_by_name=True) for API compatibility
    - Allows extra fields (extra="allow") for forward compatibility
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.workspace import ClickUpWorkspace

        workspace = ClickUpWorkspace(
            id="9018752317",
            name="Engineering Team",
            color="#3498db",
            avatar="https://example.com/avatar.png"
        )

        # Python - Access via backward-compatible id property
        print(workspace.id)  # "9018752317" (returns workspace_id)
        print(workspace.workspace_id)  # "9018752317" (direct access)

        # Python - Check workspace configuration
        if workspace.color:
            print(f"Workspace color: {workspace.color}")
        if workspace.avatar:
            print(f"Workspace avatar: {workspace.avatar}")
    """

    workspace_id: str = Field(alias="id", description="The unique identifier for the workspace")
    name: str = Field(description="The name of the workspace")
    color: str | None = Field(
        default=None, description="The workspace color in hex format for UI", pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    avatar: str | None = Field(default=None, description="The workspace avatar URL")
    members: list[dict[str, Any]] = Field(default_factory=list, description="List of workspace members")
    settings: dict[str, Any] | None = Field(default=None, description="Workspace settings")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    @model_validator(mode="after")
    def validate_workspace(self) -> "ClickUpWorkspace":
        """
        Validate the workspace model after initialization.

        This validator ensures the workspace model is valid after all fields
        are set. It validates the color format and ensures required fields are present.

        Returns:
            ClickUpWorkspace: The validated workspace instance

        Usage Examples:
            # Python - Validation happens automatically on creation
            workspace = ClickUpWorkspace(id="9018752317", name="Engineering Team")
            # validate_workspace() is called automatically by Pydantic
        """
        if self.color and not self.color.startswith("#"):
            # Auto-fix color format if missing hash
            self.color = f"#{self.color}"
        return self

    @property
    def id(self) -> str:
        """
        Get the workspace ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the workspace ID via the 'id' property, even though the field is
        named 'workspace_id'. This is useful for code that expects a generic
        'id' attribute.

        Returns:
            str: The workspace ID (same as workspace_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            workspace = ClickUpWorkspace(id="9018752317", name="Engineering Team")
            print(workspace.id)  # "9018752317"
            print(workspace.workspace_id)  # "9018752317" (same value)

            # Python - Both properties return the same value
            assert workspace.id == workspace.workspace_id
        """
        return self.workspace_id


# Backward compatibility alias
Workspace = ClickUpWorkspace
