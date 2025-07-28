"""
Team domain models.

This module provides domain models for ClickUp Teams/Workspaces.
"""

from typing import List

from pydantic import ConfigDict, Field

from clickup_mcp.models.domain.base import BaseDomainModel


class ClickUpUser(BaseDomainModel):
    """User within a team."""

    user_id: int | None = Field(None, alias="id")
    username: str | None = None
    email: str | None = None
    color: str | None = None
    profile_picture: str | None = Field(None, alias="profilePicture")
    initials: str | None = None

    # Fields with aliases for backward compatibility
    id: int | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )


class ClickUpTeamMember(BaseDomainModel):
    """Team member with associated user information."""

    user: ClickUpUser | None = None


class ClickUpTeam(BaseDomainModel):
    """
    ClickUp Team/Workspace domain model.

    This model represents a team/workspace in ClickUp.
    """

    team_id: str | None = Field(None, alias="id")
    name: str | None = None
    color: str | None = None
    avatar: str | None = None
    members: List[ClickUpTeamMember] | None = None

    # Fields with aliases for backward compatibility
    id: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )


# Backward compatibility alias
Team = ClickUpTeam
