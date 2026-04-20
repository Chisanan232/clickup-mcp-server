"""
Insights Generation API resource manager.

This module provides a resource manager for interacting with ClickUp Insights Generation.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Generate insights from analytics data

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.insights import InsightsGenerationQuery

    async with ClickUpAPIClient(api_token="pk_...") as client:
        insights_api = client.insights
        insights = await insights_api.generate(
            team_id="team_1",
            query=InsightsGenerationQuery(start_date=1640995200000, end_date=1643673600000, insight_type="productivity")
        )
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.insights import InsightsGenerationQuery, InsightsGenerationResponse

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class InsightsAPI:
    """
    Insights Generation API resource manager.

    Provides domain-specific methods to interact with ClickUp Insights Generation using a shared
    HTTP client. Methods return DTOs (e.g., `InsightsGenerationResponse`) or None if the request fails.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.insights import InsightsGenerationQuery

        async with ClickUpAPIClient(api_token="pk_...") as client:
            insights_api = client.insights
            # Generate insights
            insights = await insights_api.generate(
                "team_1",
                InsightsGenerationQuery(start_date=1640995200000, end_date=1643673600000, insight_type="productivity")
            )
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the InsightsAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def generate(
        self, team_id: str, query: InsightsGenerationQuery
    ) -> Optional[InsightsGenerationResponse]:
        """
        Generate insights from analytics data.

        API:
            GET /team/{team_id}/analytics/insights

        Notes:
            Generates actionable recommendations based on analytics data.

        Args:
            team_id: Team/workspace ID
            query: DTO containing query parameters

        Returns:
            InsightsGenerationResponse: Insights generation data, or None if request failed

        Examples:
            await insights_api.generate(
                "team_1",
                InsightsGenerationQuery(start_date=1640995200000, end_date=1643673600000, insight_type="productivity")
            )
        """
        endpoint = f"/team/{team_id}/analytics/insights"
        query_params = query.to_query()

        logger.info(f"Generating insights for team {team_id}")
        response = await self._client.get(endpoint, params=query_params)

        if response and "data" in response:
            return InsightsGenerationResponse.deserialize(response["data"])
        return None
