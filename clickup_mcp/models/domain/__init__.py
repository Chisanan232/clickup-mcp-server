"""
Domain models for the ClickUp MCP application.

This package contains domain models that represent core business entities
in the ClickUp MCP application.
"""

from .space import ClickUpSpace, Space
from .team import ClickUpTeam, ClickUpTeamMember, ClickUpUser, Team

__all__ = [
    # Space models
    "ClickUpSpace",
    "Space",  # Backwards compatibility alias
    
    # Team models
    "ClickUpTeam",
    "ClickUpTeamMember",
    "ClickUpUser",
    "Team",  # Backwards compatibility alias
]
