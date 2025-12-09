"""
Team domain models.

This module provides domain models for ClickUp Teams/Workspaces.

A Team (also called a Workspace) is the top-level organizational unit in ClickUp.
It contains Spaces, which contain Folders, which contain Lists, which contain Tasks.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates team and user information
- References related entities by ID or as nested objects
- Maintains a neutral representation independent of API specifics

Usage Examples:
    # Python - Create a team domain entity
    from clickup_mcp.models.domain.team import ClickUpTeam, ClickUpUser

    user = ClickUpUser(
        id=123,
        username="john_doe",
        email="john@example.com",
        color="#FF6B6B"
    )

    team = ClickUpTeam(
        id="team_456",
        name="Engineering",
        color="#0066FF",
        members=[ClickUpTeamMember(user=user)]
    )

    # Python - Access team properties
    print(team.name)  # "Engineering"
    print(team.members[0].user.username)  # "john_doe"
"""

from typing import List

from pydantic import ConfigDict, Field

from clickup_mcp.models.domain.base import BaseDomainModel


class ClickUpUser(BaseDomainModel):
    """
    Domain model for a ClickUp User.

    Represents a user within a team/workspace. Contains user profile information
    and identification details.

    Attributes:
        user_id: The unique identifier for the user (aliased as 'id')
        username: The user's username
        email: The user's email address
        color: The user's assigned color (for UI display)
        profile_picture: URL to the user's profile picture
        initials: The user's initials (for avatar display)

    Key Design Features:
    - Backward-compatible 'id' field for generic access
    - Flexible field population for API compatibility
    - Allows extra fields for forward compatibility
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create a user
        from clickup_mcp.models.domain.team import ClickUpUser

        user = ClickUpUser(
            id=123,
            username="john_doe",
            email="john@example.com",
            color="#FF6B6B",
            initials="JD"
        )

        # Python - Access user properties
        print(user.username)  # "john_doe"
        print(user.email)  # "john@example.com"
        print(user.user_id)  # 123
    """

    user_id: int | None = Field(None, alias="id", description="The unique identifier for the user")
    username: str | None = Field(None, description="The user's username")
    email: str | None = Field(None, description="The user's email address")
    color: str | None = Field(None, description="The user's assigned color")
    profile_picture: str | None = Field(None, alias="profilePicture", description="URL to profile picture")
    initials: str | None = Field(None, description="The user's initials")

    # Fields with aliases for backward compatibility
    id: int | None = Field(None, description="Backward compatibility identifier")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )


class ClickUpTeamMember(BaseDomainModel):
    """
    Domain model for a Team Member.

    Represents a member of a team with associated user information.

    Attributes:
        user: The ClickUpUser object associated with this team member

    Usage Examples:
        # Python - Create a team member
        from clickup_mcp.models.domain.team import ClickUpTeamMember, ClickUpUser

        user = ClickUpUser(id=123, username="john_doe")
        member = ClickUpTeamMember(user=user)

        # Python - Access member properties
        print(member.user.username)  # "john_doe"
    """

    user: ClickUpUser | None = Field(None, description="The user associated with this team member")


class ClickUpTeam(BaseDomainModel):
    """
    ClickUp Team/Workspace domain model.

    This model represents a team/workspace in ClickUp. A Team is the top-level
    organizational unit that contains Spaces, Folders, Lists, and Tasks.

    In ClickUp's hierarchy:
    - Team (workspace) → Space → Folder → List → Task

    Attributes:
        team_id: The unique identifier for the team (aliased as 'id')
        name: The name of the team/workspace
        color: The team's assigned color
        avatar: URL to the team's avatar/logo
        members: List of team members with user information

    Key Design Features:
    - Backward-compatible 'id' field for generic access
    - Flexible field population for API compatibility
    - Allows extra fields for forward compatibility
    - Immutable once created (inherited from BaseDomainModel)
    - Supports nested member information

    Usage Examples:
        # Python - Create a team
        from clickup_mcp.models.domain.team import ClickUpTeam, ClickUpTeamMember, ClickUpUser

        user1 = ClickUpUser(id=123, username="john_doe", email="john@example.com")
        user2 = ClickUpUser(id=456, username="jane_smith", email="jane@example.com")

        team = ClickUpTeam(
            id="team_789",
            name="Engineering",
            color="#0066FF",
            avatar="https://...",
            members=[
                ClickUpTeamMember(user=user1),
                ClickUpTeamMember(user=user2)
            ]
        )

        # Python - Access team properties
        print(team.name)  # "Engineering"
        print(team.team_id)  # "team_789"
        print(len(team.members))  # 2
        print(team.members[0].user.username)  # "john_doe"

        # Python - Iterate over team members
        for member in team.members or []:
            if member.user:
                print(f"{member.user.username}: {member.user.email}")
    """

    team_id: str | None = Field(None, alias="id", description="The unique identifier for the team")
    name: str | None = Field(None, description="The name of the team/workspace")
    color: str | None = Field(None, description="The team's assigned color")
    avatar: str | None = Field(None, description="URL to the team's avatar/logo")
    members: List[ClickUpTeamMember] | None = Field(None, description="List of team members")

    # Fields with aliases for backward compatibility
    id: str | None = Field(None, description="Backward compatibility identifier")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )


# Backward compatibility alias
Team = ClickUpTeam
