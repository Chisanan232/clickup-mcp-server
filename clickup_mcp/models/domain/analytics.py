"""
Domain model for ClickUp Analytics.

Represents analytics aggregates with business behaviors and invariants.
References related aggregates by identity only (team_id, list_id, space_id);
does not embed nested aggregates to maintain loose coupling.

Analytics provide insights into task completion, team performance, and workflow efficiency.
They help identify bottlenecks and optimize processes.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., date validation)
- References other aggregates by ID only (no embedded objects)
- Provides behavior methods that enforce domain rules
- Uses epoch milliseconds for time fields (vendor-agnostic)

Usage Examples:
    # Python - Create task analytics domain entity
    from clickup_mcp.models.domain.analytics import TaskAnalytics

    analytics = TaskAnalytics(
        id="analytics_123",
        team_id="team_001",
        start_date=1640995200000,
        end_date=1643673600000,
        total_tasks=100,
        completed_tasks=75
    )

    # Python - Use domain behaviors
    completion_rate = analytics.get_completion_rate()
"""

from typing import Dict, List, Optional

from pydantic import Field

from .base import BaseDomainModel


class TaskAnalytics(BaseDomainModel):
    """
    Domain model for task-level analytics with core behaviors and invariants.

    This model represents analytics data for tasks within a team/workspace.
    It includes metrics like task counts, completion rates, and performance indicators.

    In ClickUp's hierarchy:
    - Team (workspace) → Tasks → Task Analytics

    Attributes:
        analytics_id: The unique identifier for the analytics (aliased as 'id' for compatibility)
        team_id: The ID of the team/workspace
        list_id: Optional list ID for filtered analytics
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_tasks: Total number of tasks
        completed_tasks: Number of completed tasks
        in_progress_tasks: Number of tasks in progress
        blocked_tasks: Number of blocked tasks
        average_completion_time: Average time to complete tasks in milliseconds
        assignee_metrics: Metrics per assignee
        status_metrics: Metrics per status

    Key Design Features:
    - Backward-compatible 'id' property that returns analytics_id
    - Behavior methods for calculating metrics
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.analytics import TaskAnalytics

        analytics = TaskAnalytics(
            id="analytics_123",
            team_id="team_001",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=100,
            completed_tasks=75
        )

        # Python - Use domain behaviors
        completion_rate = analytics.get_completion_rate()
    """

    analytics_id: str = Field(alias="id", description="The unique identifier for the analytics")
    team_id: str = Field(description="Team/workspace ID")
    list_id: Optional[str] = Field(default=None, description="List ID for filtered analytics")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    in_progress_tasks: int = Field(default=0, description="Number of tasks in progress")
    blocked_tasks: int = Field(default=0, description="Number of blocked tasks")
    average_completion_time: Optional[int] = Field(default=None, description="Average completion time in milliseconds")
    assignee_metrics: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Metrics per assignee")
    status_metrics: Dict[str, int] = Field(default_factory=dict, description="Metrics per status")

    @property
    def id(self) -> str:
        """Get the analytics ID for backward compatibility."""
        return self.analytics_id

    def get_completion_rate(self) -> float:
        """
        Calculate the task completion rate.

        Returns:
            float: Completion rate as a percentage (0-100)

        Raises:
            ValueError: If total_tasks is zero

        Usage Examples:
            analytics = TaskAnalytics(id="a1", team_id="t1", start_date=1, end_date=2, total_tasks=100, completed_tasks=75)
            rate = analytics.get_completion_rate()  # 75.0
        """
        if self.total_tasks == 0:
            raise ValueError("Cannot calculate completion rate with zero total tasks")
        return (self.completed_tasks / self.total_tasks) * 100

    def get_average_completion_time_hours(self) -> Optional[float]:
        """
        Get average completion time in hours.

        Returns:
            Optional[float]: Average completion time in hours, or None if not available

        Usage Examples:
            analytics = TaskAnalytics(id="a1", team_id="t1", start_date=1, end_date=2, average_completion_time=86400000)
            hours = analytics.get_average_completion_time_hours()  # 24.0
        """
        if self.average_completion_time is None:
            return None
        return self.average_completion_time / (1000 * 60 * 60)


class TeamAnalytics(BaseDomainModel):
    """
    Domain model for team-level analytics with core behaviors and invariants.

    This model represents overall analytics data for a team/workspace.
    It includes aggregated metrics across all tasks and lists.

    In ClickUp's hierarchy:
    - Team (workspace) → Team Analytics

    Attributes:
        analytics_id: The unique identifier for the analytics (aliased as 'id' for compatibility)
        team_id: The ID of the team/workspace
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_tasks: Total number of tasks across the team
        completed_tasks: Number of completed tasks
        total_lists: Number of lists in the team
        active_users: Number of active users
        average_task_completion_time: Average task completion time in milliseconds

    Key Design Features:
    - Backward-compatible 'id' property that returns analytics_id
    - Behavior methods for calculating team metrics
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.analytics import TeamAnalytics

        analytics = TeamAnalytics(
            id="analytics_123",
            team_id="team_001",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=500,
            completed_tasks=400
        )

        # Python - Use domain behaviors
        completion_rate = analytics.get_completion_rate()
    """

    analytics_id: str = Field(alias="id", description="The unique identifier for the analytics")
    team_id: str = Field(description="Team/workspace ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks across the team")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    total_lists: int = Field(default=0, description="Number of lists in the team")
    active_users: int = Field(default=0, description="Number of active users")
    average_task_completion_time: Optional[int] = Field(default=None, description="Average task completion time in milliseconds")

    @property
    def id(self) -> str:
        """Get the analytics ID for backward compatibility."""
        return self.analytics_id

    def get_completion_rate(self) -> float:
        """
        Calculate the team task completion rate.

        Returns:
            float: Completion rate as a percentage (0-100)

        Raises:
            ValueError: If total_tasks is zero

        Usage Examples:
            analytics = TeamAnalytics(id="a1", team_id="t1", start_date=1, end_date=2, total_tasks=500, completed_tasks=400)
            rate = analytics.get_completion_rate()  # 80.0
        """
        if self.total_tasks == 0:
            raise ValueError("Cannot calculate completion rate with zero total tasks")
        return (self.completed_tasks / self.total_tasks) * 100

    def get_tasks_per_user(self) -> Optional[float]:
        """
        Calculate average tasks per active user.

        Returns:
            Optional[float]: Average tasks per user, or None if no active users

        Usage Examples:
            analytics = TeamAnalytics(id="a1", team_id="t1", start_date=1, end_date=2, total_tasks=500, active_users=10)
            tasks_per_user = analytics.get_tasks_per_user()  # 50.0
        """
        if self.active_users == 0:
            return None
        return self.total_tasks / self.active_users


class ListAnalytics(BaseDomainModel):
    """
    Domain model for list-level analytics with core behaviors and invariants.

    This model represents analytics data for a specific list.
    It includes metrics specific to list performance and task distribution.

    In ClickUp's hierarchy:
    - Team (workspace) → Folder → List → List Analytics

    Attributes:
        analytics_id: The unique identifier for the analytics (aliased as 'id' for compatibility)
        list_id: The ID of the list
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_tasks: Total number of tasks in the list
        completed_tasks: Number of completed tasks
        overdue_tasks: Number of overdue tasks
        average_completion_time: Average task completion time in milliseconds

    Key Design Features:
    - Backward-compatible 'id' property that returns analytics_id
    - Behavior methods for calculating list metrics
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.analytics import ListAnalytics

        analytics = ListAnalytics(
            id="analytics_123",
            list_id="list_001",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=50,
            completed_tasks=40
        )

        # Python - Use domain behaviors
        completion_rate = analytics.get_completion_rate()
    """

    analytics_id: str = Field(alias="id", description="The unique identifier for the analytics")
    list_id: str = Field(description="List ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks in the list")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    overdue_tasks: int = Field(default=0, description="Number of overdue tasks")
    average_completion_time: Optional[int] = Field(default=None, description="Average task completion time in milliseconds")

    @property
    def id(self) -> str:
        """Get the analytics ID for backward compatibility."""
        return self.analytics_id

    def get_completion_rate(self) -> float:
        """
        Calculate the list task completion rate.

        Returns:
            float: Completion rate as a percentage (0-100)

        Raises:
            ValueError: If total_tasks is zero

        Usage Examples:
            analytics = ListAnalytics(id="a1", list_id="l1", start_date=1, end_date=2, total_tasks=50, completed_tasks=40)
            rate = analytics.get_completion_rate()  # 80.0
        """
        if self.total_tasks == 0:
            raise ValueError("Cannot calculate completion rate with zero total tasks")
        return (self.completed_tasks / self.total_tasks) * 100

    def get_overdue_rate(self) -> float:
        """
        Calculate the overdue task rate.

        Returns:
            float: Overdue rate as a percentage (0-100)

        Raises:
            ValueError: If total_tasks is zero

        Usage Examples:
            analytics = ListAnalytics(id="a1", list_id="l1", start_date=1, end_date=2, total_tasks=50, overdue_tasks=5)
            rate = analytics.get_overdue_rate()  # 10.0
        """
        if self.total_tasks == 0:
            raise ValueError("Cannot calculate overdue rate with zero total tasks")
        return (self.overdue_tasks / self.total_tasks) * 100


class SpaceAnalytics(BaseDomainModel):
    """
    Domain model for space-level analytics with core behaviors and invariants.

    This model represents analytics data for a specific space.
    It includes aggregated metrics across all lists within the space.

    In ClickUp's hierarchy:
    - Team (workspace) → Space → Space Analytics

    Attributes:
        analytics_id: The unique identifier for the analytics (aliased as 'id' for compatibility)
        space_id: The ID of the space
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_tasks: Total number of tasks in the space
        completed_tasks: Number of completed tasks
        total_lists: Number of lists in the space
        total_folders: Number of folders in the space

    Key Design Features:
    - Backward-compatible 'id' property that returns analytics_id
    - Behavior methods for calculating space metrics
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.analytics import SpaceAnalytics

        analytics = SpaceAnalytics(
            id="analytics_123",
            space_id="space_001",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=200,
            completed_tasks=150
        )

        # Python - Use domain behaviors
        completion_rate = analytics.get_completion_rate()
    """

    analytics_id: str = Field(alias="id", description="The unique identifier for the analytics")
    space_id: str = Field(description="Space ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks in the space")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    total_lists: int = Field(default=0, description="Number of lists in the space")
    total_folders: int = Field(default=0, description="Number of folders in the space")

    @property
    def id(self) -> str:
        """Get the analytics ID for backward compatibility."""
        return self.analytics_id

    def get_completion_rate(self) -> float:
        """
        Calculate the space task completion rate.

        Returns:
            float: Completion rate as a percentage (0-100)

        Raises:
            ValueError: If total_tasks is zero

        Usage Examples:
            analytics = SpaceAnalytics(id="a1", space_id="s1", start_date=1, end_date=2, total_tasks=200, completed_tasks=150)
            rate = analytics.get_completion_rate()  # 75.0
        """
        if self.total_tasks == 0:
            raise ValueError("Cannot calculate completion rate with zero total tasks")
        return (self.completed_tasks / self.total_tasks) * 100

    def get_average_tasks_per_list(self) -> Optional[float]:
        """
        Calculate average tasks per list.

        Returns:
            Optional[float]: Average tasks per list, or None if no lists

        Usage Examples:
            analytics = SpaceAnalytics(id="a1", space_id="s1", start_date=1, end_date=2, total_tasks=200, total_lists=10)
            tasks_per_list = analytics.get_average_tasks_per_list()  # 20.0
        """
        if self.total_lists == 0:
            return None
        return self.total_tasks / self.total_lists
