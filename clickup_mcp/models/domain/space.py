"""
Domain model for ClickUp Space.

This module defines the domain model for a ClickUp Space, which is used
throughout the application to represent a space in a vendor-agnostic way.

A Space is the top-level organizational unit in ClickUp (after Teams).
Spaces contain Folders and Lists, and define workspace-level settings
like available statuses, features, and task assignment rules.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Focuses on business logic and invariants
- References other aggregates by identity only (team_id)
- Immutable once created (uses Pydantic's frozen model pattern)
- Type-safe with clear field definitions

Usage Examples:
    # Python - Create a space domain entity
    from clickup_mcp.models.domain.space import ClickUpSpace

    space = ClickUpSpace(
        id="456",
        name="Engineering",
        private=False,
        team_id="123",
        multiple_assignees=True
    )

    # Python - Access space properties
    print(space.id)  # "456"
    print(space.name)  # "Engineering"
    print(space.team_id)  # "123"

    # Python - Check space settings
    if space.multiple_assignees:
        print("Multiple assignees are allowed")
"""

from typing import Any

from pydantic import ConfigDict, Field, model_validator

from clickup_mcp.models.dto.space import PROPERTY_NAME_DESCRIPTION

from .base import BaseDomainModel


class ClickUpSpace(BaseDomainModel):
    """
    Domain model for a ClickUp Space.

    This model represents a Space in ClickUp and includes all relevant fields
    from the ClickUp API. A Space is a container for organizing work within a team,
    containing folders, lists, and tasks.

    In ClickUp's hierarchy:
    - Team (workspace) → Space → Folder → List → Task

    Attributes:
        space_id: The unique identifier for the space (aliased as 'id' for compatibility)
        name: The name of the space
        private: Whether the space is private (default: False)
        statuses: List of status definitions available in this space
        multiple_assignees: Whether tasks can have multiple assignees (default: False)
        features: Dictionary of enabled features for this space
        team_id: The ID of the team/workspace this space belongs to

    Key Design Features:
    - Backward-compatible 'id' property that returns space_id
    - Flexible field population (populate_by_name=True) for API compatibility
    - Allows extra fields (extra="allow") for forward compatibility
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.space import ClickUpSpace

        space = ClickUpSpace(
            id="456",
            name="Engineering",
            private=False,
            team_id="123",
            multiple_assignees=True,
            statuses=[{"name": "Open", "type": "open"}]
        )

        # Python - Access via backward-compatible id property
        print(space.id)  # "456" (returns space_id)
        print(space.space_id)  # "456" (direct access)

        # Python - Check space configuration
        if space.private:
            print("This is a private space")
        if space.multiple_assignees:
            print("Multiple assignees are allowed")

        # Python - Access team relationship
        if space.team_id:
            print(f"Space belongs to team: {space.team_id}")
    """

    space_id: str = Field(alias="id", description="The unique identifier for the space")
    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    private: bool = Field(default=False, description="Whether the space is private")
    statuses: list[dict[str, Any]] = Field(default_factory=list, description="The statuses defined for this space")
    multiple_assignees: bool = Field(default=False, description="Whether multiple assignees are allowed for tasks")
    features: dict[str, Any] | None = Field(default=None, description="Features enabled for this space")
    team_id: str | None = Field(default=None, description="The team ID this space belongs to")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    @model_validator(mode="after")
    def validate_space(self) -> "ClickUpSpace":
        """
        Validate the space model after initialization.

        This validator ensures the space model is valid after all fields
        are set. It skips team_id validation when handling API responses
        with space_id to allow flexibility in different contexts.

        Returns:
            ClickUpSpace: The validated space instance

        Usage Examples:
            # Python - Validation happens automatically on creation
            space = ClickUpSpace(id="456", name="Engineering")
            # validate_space() is called automatically by Pydantic
        """
        return self

    @property
    def id(self) -> str:
        """
        Get the space ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the space ID via the 'id' property, even though the field is
        named 'space_id'. This is useful for code that expects a generic
        'id' attribute.

        Returns:
            str: The space ID (same as space_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            space = ClickUpSpace(id="456", name="Engineering")
            print(space.id)  # "456"
            print(space.space_id)  # "456" (same value)

            # Python - Both properties return the same value
            assert space.id == space.space_id
        """
        return self.space_id


# Backward compatibility alias
Space = ClickUpSpace
