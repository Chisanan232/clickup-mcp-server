"""
Bottleneck Detection API resource manager.

This module provides a resource manager for interacting with ClickUp Bottleneck Detection.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Detect bottlenecks in team workflows

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.bottleneck import BottleneckDetectionQuery

    async with ClickUpAPIClient(api_token="pk_...") as client:
        bottleneck_api = client.bottleneck
        detection = await bottleneck_api.detect(
            team_id="team_1",
            query=BottleneckDetectionQuery(start_date=1640995200000, end_date=1643673600000)
        )
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.bottleneck import (
    BottleneckDetectionQuery,
    BottleneckDetectionResponse,
)

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class BottleneckAPI:
    """
    Bottleneck Detection API resource manager.

    Provides domain-specific methods to interact with ClickUp Bottleneck Detection using a shared
    HTTP client. Methods return DTOs (e.g., `BottleneckDetectionResponse`) or None if the request fails.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.bottleneck import BottleneckDetectionQuery

        async with ClickUpAPIClient(api_token="pk_...") as client:
            bottleneck_api = client.bottleneck
            # Detect bottlenecks
            detection = await bottleneck_api.detect(
                "team_1",
                BottleneckDetectionQuery(start_date=1640995200000, end_date=1643673600000)
            )
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the BottleneckAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def detect(self, team_id: str, query: BottleneckDetectionQuery) -> Optional[BottleneckDetectionResponse]:
        """
        Detect bottlenecks in team workflows.

        API:
            GET /team/{team_id}/analytics/bottleneck

        Notes:
            Identifies process bottlenecks in task workflows and team productivity.

        Args:
            team_id: Team/workspace ID
            query: DTO containing query parameters

        Returns:
            BottleneckDetectionResponse: Bottleneck detection data, or None if request failed

        Examples:
            await bottleneck_api.detect(
                "team_1",
                BottleneckDetectionQuery(start_date=1640995200000, end_date=1643673600000)
            )
        """
        endpoint = f"/team/{team_id}/analytics/bottleneck"
        query_params = query.to_query()

        logger.info(f"Detecting bottlenecks for team {team_id}")
        response = await self._client.get(endpoint, params=query_params)

        if response and "data" in response:
            return BottleneckDetectionResponse.deserialize(response["data"])
        return None
