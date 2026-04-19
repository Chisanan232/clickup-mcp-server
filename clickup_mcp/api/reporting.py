"""
Time Report API resource manager.

This module provides a resource manager for interacting with ClickUp Time Reports.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Create time reports for teams
- Retrieve time report by ID
- List time reports with filters

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.reporting import TimeReportCreate

    async with ClickUpAPIClient(api_token="pk_...") as client:
        report_api = client.reporting
        report = await report_api.create(
            team_id="team_1",
            report_create=TimeReportCreate(start_date=1702080000000, end_date=1702166400000)
        )

    # curl - Get a time report
    # GET /team/{team_id}/time_tracking
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/team/team_1/time_tracking?start_date=1702080000000

    # wget - List time reports
    # GET /team/{team_id}/time_tracking
    wget --header="Authorization: pk_..." \
         "https://api.clickup.com/api/v2/team/team_1/time_tracking?limit=50"
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.reporting import (
    TimeReportCreate,
    TimeReportListQuery,
    TimeReportListResponse,
)
from clickup_mcp.types import ClickUpTeamID

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class ReportingAPI:
    """
    Time Report API resource manager.

    Provides domain-specific methods to interact with ClickUp Time Reports using a shared
    HTTP client. Methods return DTOs (e.g., `TimeReportListResponse`) or booleans for write ops.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.reporting import TimeReportCreate

        async with ClickUpAPIClient(api_token="pk_...") as client:
            report_api = client.reporting
            # Create
            created = await report_api.create("team_1", TimeReportCreate(start_date=1702080000000, end_date=1702166400000))
            # List
            from clickup_mcp.models.dto.reporting import TimeReportListQuery
            reports = await report_api.list("team_1", TimeReportListQuery(limit=50))
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the ReportingAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, team_id: ClickUpTeamID, report_create: TimeReportCreate) -> Optional[TimeReportListResponse]:
        """
        Create a time report for a team.

        API:
            POST /team/{team_id}/time_tracking
            Docs: https://developer.clickup.com/reference/getfilteredtimeentries

        Notes:
            - Requires start_date and end_date to define the reporting period
            - Returns a list of time entries matching the criteria

        Args:
            team_id: The ID of the team/workspace
            report_create: TimeReportCreate DTO with report criteria

        Returns:
            TimeReportListResponse | None: The time entries matching the report criteria, or None if request failed

        Examples:
            # Python (async)
            created = await report_api.create("team_1", TimeReportCreate(start_date=1702080000000, end_date=1702166400000))

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"start_date":1702080000000,"end_date":1702166400000}' \
              https://api.clickup.com/api/v2/team/team_1/time_tracking

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"start_date":1702080000000,"end_date":1702166400000}' \
              https://api.clickup.com/api/v2/team/team_1/time_tracking
        """
        response = await self._client.post(f"/team/{team_id}/time_tracking", data=report_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TimeReportListResponse(**response.data)

    async def list(self, team_id: ClickUpTeamID, query: TimeReportListQuery) -> Optional[TimeReportListResponse]:
        """
        List time entries for a report with filters.

        API:
            GET /team/{team_id}/time_tracking
            Docs: https://developer.clickup.com/reference/getfilteredtimeentries

        Args:
            team_id: The ID of the team/workspace
            query: TimeReportListQuery with filters and pagination

        Returns:
            TimeReportListResponse | None: The paginated list of time entries, or None if request failed

        Examples:
            # Python (async)
            from clickup_mcp.models.dto.reporting import TimeReportListQuery
            entries = await report_api.list("team_1", TimeReportListQuery(start_date=1702080000000, end_date=1702166400000, limit=50))

            # curl
            curl -H "Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/team/team_1/time_tracking?start_date=1702080000000&limit=50"

            # wget
            wget --header="Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/team/team_1/time_tracking?start_date=1702080000000&limit=50"
        """
        response = await self._client.get(f"/team/{team_id}/time_tracking", params=query.to_query())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TimeReportListResponse(**response.data)
