"""
Analytics DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Analytics
operations, including query parameters and response parsing. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create analytics query
    from clickup_mcp.models.dto.analytics import TaskAnalyticsQuery

    query = TaskAnalyticsQuery(start_date=1640995200000, end_date=1643673600000).to_query()
    # => {"start_date": "1640995200000", "end_date": "1643673600000"}
"""

from typing import Any, Dict

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class TaskAnalyticsQuery(BaseRequestDTO):
    """
    DTO for task analytics query parameters.

    API:
        GET /team/{team_id}/analytics/task

    Attributes:
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        assignee_id: Filter by assignee
        status: Filter by status
        limit: Page size (cap 100)

    Examples:
        TaskAnalyticsQuery(start_date=1640995200000, end_date=1643673600000).to_query()
    """

    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    assignee_id: str | None = Field(default=None, description="Filter by assignee ID")
    status: str | None = Field(default=None, description="Filter by status")
    limit: int = Field(default=100, description="Page size (cap 100 by API)")

    def to_query(self) -> Dict[str, str]:
        """
        Convert the DTO into ClickUp query parameters.

        Returns:
            Dict[str, str]: Query parameters as string values.
        """
        query: Dict[str, str] = {}
        query["start_date"] = str(self.start_date)
        query["end_date"] = str(self.end_date)
        if self.assignee_id is not None:
            query["assignee_id"] = self.assignee_id
        if self.status is not None:
            query["status"] = self.status
        if self.limit is not None:
            query["limit"] = str(self.limit)
        return query


class TeamAnalyticsQuery(BaseRequestDTO):
    """
    DTO for team analytics query parameters.

    API:
        GET /team/{team_id}/analytics/team

    Attributes:
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds

    Examples:
        TeamAnalyticsQuery(start_date=1640995200000, end_date=1643673600000).to_query()
    """

    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")

    def to_query(self) -> Dict[str, str]:
        """
        Convert the DTO into ClickUp query parameters.

        Returns:
            Dict[str, str]: Query parameters as string values.
        """
        query: Dict[str, str] = {}
        query["start_date"] = str(self.start_date)
        query["end_date"] = str(self.end_date)
        return query


class ListAnalyticsQuery(BaseRequestDTO):
    """
    DTO for list analytics query parameters.

    API:
        GET /list/{list_id}/analytics

    Attributes:
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds

    Examples:
        ListAnalyticsQuery(start_date=1640995200000, end_date=1643673600000).to_query()
    """

    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")

    def to_query(self) -> Dict[str, str]:
        """
        Convert the DTO into ClickUp query parameters.

        Returns:
            Dict[str, str]: Query parameters as string values.
        """
        query: Dict[str, str] = {}
        query["start_date"] = str(self.start_date)
        query["end_date"] = str(self.end_date)
        return query


class SpaceAnalyticsQuery(BaseRequestDTO):
    """
    DTO for space analytics query parameters.

    API:
        GET /space/{space_id}/analytics

    Attributes:
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds

    Examples:
        SpaceAnalyticsQuery(start_date=1640995200000, end_date=1643673600000).to_query()
    """

    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")

    def to_query(self) -> Dict[str, str]:
        """
        Convert the DTO into ClickUp query parameters.

        Returns:
            Dict[str, str]: Query parameters as string values.
        """
        query: Dict[str, str] = {}
        query["start_date"] = str(self.start_date)
        query["end_date"] = str(self.end_date)
        return query


class TaskAnalyticsResponse(BaseResponseDTO):
    """
    DTO for task analytics API responses.

    API:
        GET /team/{team_id}/analytics/task

    Attributes:
        id: Analytics ID
        team_id: Team/workspace ID
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

    Examples:
        TaskAnalyticsResponse.deserialize(api_response_data)
    """

    id: str = Field(description="Analytics ID")
    team_id: str = Field(description="Team/workspace ID")
    list_id: str | None = Field(default=None, description="List ID for filtered analytics")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    in_progress_tasks: int = Field(default=0, description="Number of tasks in progress")
    blocked_tasks: int = Field(default=0, description="Number of blocked tasks")
    average_completion_time: int | None = Field(default=None, description="Average completion time in milliseconds")
    assignee_metrics: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Metrics per assignee")
    status_metrics: Dict[str, int] = Field(default_factory=dict, description="Metrics per status")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "TaskAnalyticsResponse":
        """
        Deserialize API response data into a TaskAnalyticsResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            TaskAnalyticsResponse: Deserialized DTO instance

        Examples:
            TaskAnalyticsResponse.deserialize({"id": "a1", "team_id": "t1", ...})
        """
        return cls(**data)


class TeamAnalyticsResponse(BaseResponseDTO):
    """
    DTO for team analytics API responses.

    API:
        GET /team/{team_id}/analytics/team

    Attributes:
        id: Analytics ID
        team_id: Team/workspace ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_tasks: Total number of tasks across the team
        completed_tasks: Number of completed tasks
        total_lists: Number of lists in the team
        active_users: Number of active users
        average_task_completion_time: Average task completion time in milliseconds

    Examples:
        TeamAnalyticsResponse.deserialize(api_response_data)
    """

    id: str = Field(description="Analytics ID")
    team_id: str = Field(description="Team/workspace ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks across the team")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    total_lists: int = Field(default=0, description="Number of lists in the team")
    active_users: int = Field(default=0, description="Number of active users")
    average_task_completion_time: int | None = Field(default=None, description="Average task completion time in milliseconds")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "TeamAnalyticsResponse":
        """
        Deserialize API response data into a TeamAnalyticsResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            TeamAnalyticsResponse: Deserialized DTO instance

        Examples:
            TeamAnalyticsResponse.deserialize({"id": "a1", "team_id": "t1", ...})
        """
        return cls(**data)


class ListAnalyticsResponse(BaseResponseDTO):
    """
    DTO for list analytics API responses.

    API:
        GET /list/{list_id}/analytics

    Attributes:
        id: Analytics ID
        list_id: List ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_tasks: Total number of tasks in the list
        completed_tasks: Number of completed tasks
        overdue_tasks: Number of overdue tasks
        average_completion_time: Average task completion time in milliseconds

    Examples:
        ListAnalyticsResponse.deserialize(api_response_data)
    """

    id: str = Field(description="Analytics ID")
    list_id: str = Field(description="List ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks in the list")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    overdue_tasks: int = Field(default=0, description="Number of overdue tasks")
    average_completion_time: int | None = Field(default=None, description="Average task completion time in milliseconds")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "ListAnalyticsResponse":
        """
        Deserialize API response data into a ListAnalyticsResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            ListAnalyticsResponse: Deserialized DTO instance

        Examples:
            ListAnalyticsResponse.deserialize({"id": "a1", "list_id": "l1", ...})
        """
        return cls(**data)


class SpaceAnalyticsResponse(BaseResponseDTO):
    """
    DTO for space analytics API responses.

    API:
        GET /space/{space_id}/analytics

    Attributes:
        id: Analytics ID
        space_id: Space ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_tasks: Total number of tasks in the space
        completed_tasks: Number of completed tasks
        total_lists: Number of lists in the space
        total_folders: Number of folders in the space

    Examples:
        SpaceAnalyticsResponse.deserialize(api_response_data)
    """

    id: str = Field(description="Analytics ID")
    space_id: str = Field(description="Space ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks in the space")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    total_lists: int = Field(default=0, description="Number of lists in the space")
    total_folders: int = Field(default=0, description="Number of folders in the space")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "SpaceAnalyticsResponse":
        """
        Deserialize API response data into a SpaceAnalyticsResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            SpaceAnalyticsResponse: Deserialized DTO instance

        Examples:
            SpaceAnalyticsResponse.deserialize({"id": "a1", "space_id": "s1", ...})
        """
        return cls(**data)
