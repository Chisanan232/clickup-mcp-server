"""
Domain models for the ClickUp MCP application.

This package contains domain models that represent core business entities
in the ClickUp MCP application.
"""

from .space import ClickUpSpace, Space
from .team import ClickUpTeam, ClickUpTeamMember, ClickUpUser, Team
from .folder import ClickUpFolder, Folder
from .list import ClickUpList, List
from .task import ClickUpTask, Task

__all__ = [
    # Space models
    "ClickUpSpace",
    "Space",  # Backwards compatibility alias
    # Folder models
    "ClickUpFolder",
    "Folder",  # Backwards compatibility alias
    # List models
    "ClickUpList",
    "List",  # Backwards compatibility alias
    # Task models
    "ClickUpTask",
    "Task",  # Backwards compatibility alias
    # Team models
    "ClickUpTeam",
    "ClickUpTeamMember",
    "ClickUpUser",
    "Team",  # Backwards compatibility alias
]
