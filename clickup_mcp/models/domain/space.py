"""
Domain model for ClickUp Space.

This module defines the domain model for a ClickUp Space, which is used
throughout the application to represent a space in ClickUp.
"""

from typing import Any

from pydantic import ConfigDict, Field, model_validator

from clickup_mcp.models.dto.space import PROPERTY_NAME_DESCRIPTION

from .base import BaseDomainModel


class ClickUpSpace(BaseDomainModel):
    """Domain model for a ClickUp Space.

    This model represents a Space in ClickUp and includes all relevant fields
    from the ClickUp API.
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
        """Validate the space model.

        Skip team_id validation when handling API responses with space_id.
        """
        return self

    @property
    def id(self) -> str:
        """Get the space ID for backward compatibility.

        Returns:
            str: The space ID
        """
        return self.space_id


# Backward compatibility alias
Space = ClickUpSpace
