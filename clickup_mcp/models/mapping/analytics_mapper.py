"""
Analytics DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Analytics resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic Analytics domain entity.

The mapper follows a unidirectional flow:
1. API Response DTO → Domain Entity (to_domain)
2. Domain Entity → MCP Output (to_analytics_result_output)

Special Handling:
- Date normalization: Ensures epoch milliseconds are consistent
- Metrics aggregation: Handles metrics data transformations

Usage Examples:
    # Python - Map API response to domain
    from clickup_mcp.models.mapping.analytics_mapper import AnalyticsMapper

    analytics_domain = AnalyticsMapper.to_domain(api_response_dto)

    # Python - Map domain to MCP output
    mcp_output = AnalyticsMapper.to_analytics_result_output(analytics_domain)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from clickup_mcp.models.domain.analytics import ListAnalytics, SpaceAnalytics, TaskAnalytics, TeamAnalytics
from clickup_mcp.models.dto.analytics import (
    ListAnalyticsResponse,
    SpaceAnalyticsResponse,
    TaskAnalyticsResponse,
    TeamAnalyticsResponse,
)

if TYPE_CHECKING:  # type hints only; avoid importing mcp_server package at runtime
    from clickup_mcp.mcp_server.models.inputs.analytics import (
        ListAnalyticsInput,
        SpaceAnalyticsInput,
        TaskAnalyticsInput,
        TeamAnalyticsInput,
    )

logger = logging.getLogger(__name__)


class AnalyticsMapper:
    """
    Static mapper for converting between Analytics DTOs and domain entities.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Analytics data:

    1. **API Response → Domain**: Converts ClickUp API responses to domain entities
    2. **Domain → MCP Output**: Converts domain entities to user-facing MCP output models

    Key Design Principles:
    - **Separation of Concerns**: Domain logic is isolated from transport details
    - **Unidirectional Flow**: Data flows in one direction through the mapper
    - **Testability**: Each mapping can be tested independently
    - **Maintainability**: Changes to DTOs don't affect domain logic

    Attributes:
        None - This is a static utility class with no instance state

    Usage Examples:
        # Python - Convert API response to domain
        from clickup_mcp.models.mapping.analytics_mapper import AnalyticsMapper

        analytics_domain = AnalyticsMapper.to_domain(api_response_dto)

        # Python - Convert domain to MCP output
        mcp_output = AnalyticsMapper.to_analytics_result_output(analytics_domain)
    """

    @staticmethod
    def task_analytics_from_input(mcp_input: "TaskAnalyticsInput") -> TaskAnalytics:
        """
        Convert MCP input model to TaskAnalytics domain entity.

        Args:
            mcp_input: MCP input model from task analytics request

        Returns:
            TaskAnalytics: Domain entity with business logic

        Examples:
            AnalyticsMapper.task_analytics_from_input(
                TaskAnalyticsInput(team_id="team_123", start_date=1640995200000, end_date=1643673600000)
            )
        """
        return TaskAnalytics(
            id="temp",  # Temporary ID, will be replaced by API response
            team_id=mcp_input.team_id,
            start_date=mcp_input.start_date,
            end_date=mcp_input.end_date,
        )

    @staticmethod
    def team_analytics_from_input(mcp_input: "TeamAnalyticsInput") -> TeamAnalytics:
        """
        Convert MCP input model to TeamAnalytics domain entity.

        Args:
            mcp_input: MCP input model from team analytics request

        Returns:
            TeamAnalytics: Domain entity with business logic

        Examples:
            AnalyticsMapper.team_analytics_from_input(
                TeamAnalyticsInput(team_id="team_123", start_date=1640995200000, end_date=1643673600000)
            )
        """
        return TeamAnalytics(
            id="temp",  # Temporary ID, will be replaced by API response
            team_id=mcp_input.team_id,
            start_date=mcp_input.start_date,
            end_date=mcp_input.end_date,
        )

    @staticmethod
    def list_analytics_from_input(mcp_input: "ListAnalyticsInput") -> ListAnalytics:
        """
        Convert MCP input model to ListAnalytics domain entity.

        Args:
            mcp_input: MCP input model from list analytics request

        Returns:
            ListAnalytics: Domain entity with business logic

        Examples:
            AnalyticsMapper.list_analytics_from_input(
                ListAnalyticsInput(list_id="list_123", start_date=1640995200000, end_date=1643673600000)
            )
        """
        return ListAnalytics(
            id="temp",  # Temporary ID, will be replaced by API response
            list_id=mcp_input.list_id,
            start_date=mcp_input.start_date,
            end_date=mcp_input.end_date,
        )

    @staticmethod
    def space_analytics_from_input(mcp_input: "SpaceAnalyticsInput") -> SpaceAnalytics:
        """
        Convert MCP input model to SpaceAnalytics domain entity.

        Args:
            mcp_input: MCP input model from space analytics request

        Returns:
            SpaceAnalytics: Domain entity with business logic

        Examples:
            AnalyticsMapper.space_analytics_from_input(
                SpaceAnalyticsInput(space_id="space_123", start_date=1640995200000, end_date=1643673600000)
            )
        """
        return SpaceAnalytics(
            id="temp",  # Temporary ID, will be replaced by API response
            space_id=mcp_input.space_id,
            start_date=mcp_input.start_date,
            end_date=mcp_input.end_date,
        )

    @staticmethod
    def task_analytics_to_domain(response: TaskAnalyticsResponse) -> TaskAnalytics:
        """
        Convert API response DTO to TaskAnalytics domain entity.

        Args:
            response: API response DTO from ClickUp

        Returns:
            TaskAnalytics: Domain entity with business logic

        Examples:
            AnalyticsMapper.task_analytics_to_domain(TaskAnalyticsResponse.deserialize(api_data))
        """
        return TaskAnalytics(
            id=response.id,
            team_id=response.team_id,
            list_id=response.list_id,
            start_date=response.start_date,
            end_date=response.end_date,
            total_tasks=response.total_tasks,
            completed_tasks=response.completed_tasks,
            in_progress_tasks=response.in_progress_tasks,
            blocked_tasks=response.blocked_tasks,
            average_completion_time=response.average_completion_time,
            assignee_metrics=response.assignee_metrics,
            status_metrics=response.status_metrics,
        )

    @staticmethod
    def team_analytics_to_domain(response: TeamAnalyticsResponse) -> TeamAnalytics:
        """
        Convert API response DTO to TeamAnalytics domain entity.

        Args:
            response: API response DTO from ClickUp

        Returns:
            TeamAnalytics: Domain entity with business logic

        Examples:
            AnalyticsMapper.team_analytics_to_domain(TeamAnalyticsResponse.deserialize(api_data))
        """
        return TeamAnalytics(
            id=response.id,
            team_id=response.team_id,
            start_date=response.start_date,
            end_date=response.end_date,
            total_tasks=response.total_tasks,
            completed_tasks=response.completed_tasks,
            total_lists=response.total_lists,
            active_users=response.active_users,
            average_task_completion_time=response.average_task_completion_time,
        )

    @staticmethod
    def list_analytics_to_domain(response: ListAnalyticsResponse) -> ListAnalytics:
        """
        Convert API response DTO to ListAnalytics domain entity.

        Args:
            response: API response DTO from ClickUp

        Returns:
            ListAnalytics: Domain entity with business logic

        Examples:
            AnalyticsMapper.list_analytics_to_domain(ListAnalyticsResponse.deserialize(api_data))
        """
        return ListAnalytics(
            id=response.id,
            list_id=response.list_id,
            start_date=response.start_date,
            end_date=response.end_date,
            total_tasks=response.total_tasks,
            completed_tasks=response.completed_tasks,
            overdue_tasks=response.overdue_tasks,
            average_completion_time=response.average_completion_time,
        )

    @staticmethod
    def space_analytics_to_domain(response: SpaceAnalyticsResponse) -> SpaceAnalytics:
        """
        Convert API response DTO to SpaceAnalytics domain entity.

        Args:
            response: API response DTO from ClickUp

        Returns:
            SpaceAnalytics: Domain entity with business logic

        Examples:
            AnalyticsMapper.space_analytics_to_domain(SpaceAnalyticsResponse.deserialize(api_data))
        """
        return SpaceAnalytics(
            id=response.id,
            space_id=response.space_id,
            start_date=response.start_date,
            end_date=response.end_date,
            total_tasks=response.total_tasks,
            completed_tasks=response.completed_tasks,
            total_lists=response.total_lists,
            total_folders=response.total_folders,
        )

    @staticmethod
    def task_analytics_to_output(domain: TaskAnalytics) -> dict[str, object]:
        """
        Convert TaskAnalytics domain entity to MCP result output format.

        Args:
            domain: TaskAnalytics domain entity

        Returns:
            dict[str, object]: MCP output format for task analytics result

        Examples:
            AnalyticsMapper.task_analytics_to_output(analytics_domain)
        """
        return {
            "id": domain.analytics_id,
            "team_id": domain.team_id,
            "list_id": domain.list_id,
            "start_date": domain.start_date,
            "end_date": domain.end_date,
            "total_tasks": domain.total_tasks,
            "completed_tasks": domain.completed_tasks,
            "in_progress_tasks": domain.in_progress_tasks,
            "blocked_tasks": domain.blocked_tasks,
            "average_completion_time": domain.average_completion_time,
            "assignee_metrics": domain.assignee_metrics,
            "status_metrics": domain.status_metrics,
        }

    @staticmethod
    def team_analytics_to_output(domain: TeamAnalytics) -> dict[str, object]:
        """
        Convert TeamAnalytics domain entity to MCP result output format.

        Args:
            domain: TeamAnalytics domain entity

        Returns:
            dict[str, object]: MCP output format for team analytics result

        Examples:
            AnalyticsMapper.team_analytics_to_output(analytics_domain)
        """
        return {
            "id": domain.analytics_id,
            "team_id": domain.team_id,
            "start_date": domain.start_date,
            "end_date": domain.end_date,
            "total_tasks": domain.total_tasks,
            "completed_tasks": domain.completed_tasks,
            "total_lists": domain.total_lists,
            "active_users": domain.active_users,
            "average_task_completion_time": domain.average_task_completion_time,
        }

    @staticmethod
    def list_analytics_to_output(domain: ListAnalytics) -> dict[str, object]:
        """
        Convert ListAnalytics domain entity to MCP result output format.

        Args:
            domain: ListAnalytics domain entity

        Returns:
            dict[str, object]: MCP output format for list analytics result

        Examples:
            AnalyticsMapper.list_analytics_to_output(analytics_domain)
        """
        return {
            "id": domain.analytics_id,
            "list_id": domain.list_id,
            "start_date": domain.start_date,
            "end_date": domain.end_date,
            "total_tasks": domain.total_tasks,
            "completed_tasks": domain.completed_tasks,
            "overdue_tasks": domain.overdue_tasks,
            "average_completion_time": domain.average_completion_time,
        }

    @staticmethod
    def space_analytics_to_output(domain: SpaceAnalytics) -> dict[str, object]:
        """
        Convert SpaceAnalytics domain entity to MCP result output format.

        Args:
            domain: SpaceAnalytics domain entity

        Returns:
            dict[str, object]: MCP output format for space analytics result

        Examples:
            AnalyticsMapper.space_analytics_to_output(analytics_domain)
        """
        return {
            "id": domain.analytics_id,
            "space_id": domain.space_id,
            "start_date": domain.start_date,
            "end_date": domain.end_date,
            "total_tasks": domain.total_tasks,
            "completed_tasks": domain.completed_tasks,
            "total_lists": domain.total_lists,
            "total_folders": domain.total_folders,
        }
