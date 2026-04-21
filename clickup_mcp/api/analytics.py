"""
Analytics API resource manager.

This module provides a resource manager for interacting with ClickUp Analytics.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Get task analytics for a team
- Get team analytics
- Get list analytics
- Get space analytics

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.analytics import TaskAnalyticsQuery

    async with ClickUpAPIClient(api_token="pk_...") as client:
        analytics_api = client.analytics
        task_analytics = await analytics_api.get_task_analytics(
            team_id="team_1",
            query=TaskAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
        )
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.analytics import (
    ListAnalyticsQuery,
    ListAnalyticsResponse,
    SpaceAnalyticsQuery,
    SpaceAnalyticsResponse,
    TaskAnalyticsQuery,
    TaskAnalyticsResponse,
    TeamAnalyticsQuery,
    TeamAnalyticsResponse,
)

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class AnalyticsAPI:
    """
    Analytics API resource manager.

    Provides domain-specific methods to interact with ClickUp Analytics using a shared
    HTTP client. Methods return DTOs (e.g., `TaskAnalyticsResponse`) or None if the request fails.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.analytics import TaskAnalyticsQuery

        async with ClickUpAPIClient(api_token="pk_...") as client:
            analytics_api = client.analytics
            # Get task analytics
            task_analytics = await analytics_api.get_task_analytics(
                "team_1",
                TaskAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
            )
            # Get team analytics
            team_analytics = await analytics_api.get_team_analytics(
                "team_1",
                TeamAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
            )
            # Get list analytics
            list_analytics = await analytics_api.get_list_analytics(
                "list_1",
                ListAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
            )
            # Get space analytics
            space_analytics = await analytics_api.get_space_analytics(
                "space_1",
                SpaceAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
            )
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the AnalyticsAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def get_task_analytics(self, team_id: str, query: TaskAnalyticsQuery) -> Optional[TaskAnalyticsResponse]:
        """
        Get task analytics for a team.

        API:
            GET /team/{team_id}/analytics/task

        Notes:
            Retrieves analytics data for tasks within a team/workspace.

        Args:
            team_id: Team/workspace ID
            query: DTO containing query parameters

        Returns:
            TaskAnalyticsResponse: Task analytics data, or None if request failed

        Examples:
            await analytics_api.get_task_analytics(
                "team_1",
                TaskAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
            )
        """
        endpoint = f"/team/{team_id}/analytics/task"
        query_params = query.to_query()

        logger.info(f"Getting task analytics for team {team_id}")
        response = await self._client.get(endpoint, params=query_params)

        if response and "data" in response:
            return TaskAnalyticsResponse.deserialize(response["data"])
        return None

    async def get_team_analytics(self, team_id: str, query: TeamAnalyticsQuery) -> Optional[TeamAnalyticsResponse]:
        """
        Get team analytics.

        API:
            GET /team/{team_id}/analytics/team

        Notes:
            Retrieves overall analytics data for a team/workspace.

        Args:
            team_id: Team/workspace ID
            query: DTO containing query parameters

        Returns:
            TeamAnalyticsResponse: Team analytics data, or None if request failed

        Examples:
            await analytics_api.get_team_analytics(
                "team_1",
                TeamAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
            )
        """
        endpoint = f"/team/{team_id}/analytics/team"
        query_params = query.to_query()

        logger.info(f"Getting team analytics for team {team_id}")
        response = await self._client.get(endpoint, params=query_params)

        if response and "data" in response:
            return TeamAnalyticsResponse.deserialize(response["data"])
        return None

    async def get_list_analytics(self, list_id: str, query: ListAnalyticsQuery) -> Optional[ListAnalyticsResponse]:
        """
        Get list analytics.

        API:
            GET /list/{list_id}/analytics

        Notes:
            Retrieves analytics data for a specific list.

        Args:
            list_id: List ID
            query: DTO containing query parameters

        Returns:
            ListAnalyticsResponse: List analytics data, or None if request failed

        Examples:
            await analytics_api.get_list_analytics(
                "list_1",
                ListAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
            )
        """
        endpoint = f"/list/{list_id}/analytics"
        query_params = query.to_query()

        logger.info(f"Getting list analytics for list {list_id}")
        response = await self._client.get(endpoint, params=query_params)

        if response and "data" in response:
            return ListAnalyticsResponse.deserialize(response["data"])
        return None

    async def get_space_analytics(self, space_id: str, query: SpaceAnalyticsQuery) -> Optional[SpaceAnalyticsResponse]:
        """
        Get space analytics.

        API:
            GET /space/{space_id}/analytics

        Notes:
            Retrieves analytics data for a specific space.

        Args:
            space_id: Space ID
            query: DTO containing query parameters

        Returns:
            SpaceAnalyticsResponse: Space analytics data, or None if request failed

        Examples:
            await analytics_api.get_space_analytics(
                "space_1",
                SpaceAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
            )
        """
        endpoint = f"/space/{space_id}/analytics"
        query_params = query.to_query()

        logger.info(f"Getting space analytics for space {space_id}")
        response = await self._client.get(endpoint, params=query_params)

        if response and "data" in response:
            return SpaceAnalyticsResponse.deserialize(response["data"])
        return None
