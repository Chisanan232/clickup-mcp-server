"""
Domain models for the ClickUp MCP application.

This package contains domain models that represent core business entities
in the ClickUp MCP application.
"""

from .analytics import ListAnalytics, SpaceAnalytics, TaskAnalytics, TeamAnalytics
from .folder import ClickUpFolder, Folder
from .goal import Goal
from .insights import InsightsGeneration
from .key_result import KeyResult
from .list import ClickUpList, List
from .space import ClickUpSpace, Space
from .task import ClickUpTask, Task
from .team import ClickUpTeam, ClickUpTeamMember, ClickUpUser, Team
from .workflow import Workflow
from .workflow_context import WorkflowContext

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
    # Goal models
    "Goal",
    # Key result models
    "KeyResult",
    # Workflow models
    "Workflow",
    # Workflow context models
    "WorkflowContext",
    # Analytics models
    "TaskAnalytics",
    "TeamAnalytics",
    "ListAnalytics",
    "SpaceAnalytics",
    # Insights generation models
    "InsightsGeneration",
]
