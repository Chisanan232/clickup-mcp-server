"""
Time Reporting DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Time Report
operations, including create, get, and list queries. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create time report payload
    from clickup_mcp.models.dto.reporting import TimeReportCreate

    payload = TimeReportCreate(
        start_date=1702080000000,
        end_date=1702166400000,
    ).to_payload()
    # => {"start_date": 1702080000000, "end_date": 1702166400000}

    # Python - Build time report list query
    from clickup_mcp.models.dto.reporting import TimeReportListQuery

    query = TimeReportListQuery(limit=50).to_query()
    # => {"page": 0, "limit": 50}
"""

from typing import Any, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO, PaginatedResponseDTO
from .common import EpochMs

PROPERTY_START_DATE_DESCRIPTION: str = "Start date in epoch milliseconds"
PROPERTY_END_DATE_DESCRIPTION: str = "End date in epoch milliseconds"
PROPERTY_TOTAL_DURATION_DESCRIPTION: str = "Total duration in milliseconds"


class TimeReportCreate(BaseRequestDTO):
    """
    DTO for creating a time report.

    API:
        POST /team/{team_id}/time_tracking
        Docs: https://developer.clickup.com/reference/getfilteredtimeentries

    Notes:
        Requires start_date and end_date to define the reporting period.

    Attributes:
        start_date: Start date in epoch ms
        end_date: End date in epoch ms
        assignee: Filter by user ID
        task_id: Filter by task ID

    Examples:
        # Python - payload build with date range
        TimeReportCreate(
            start_date=1702080000000,
            end_date=1702166400000,
        ).to_payload()
    """

    start_date: EpochMs = Field(description=PROPERTY_START_DATE_DESCRIPTION)
    end_date: EpochMs = Field(description=PROPERTY_END_DATE_DESCRIPTION)
    assignee: str | None = Field(default=None, description="Filter by user ID")
    task_id: str | None = Field(default=None, description="Filter by task ID")


class TimeReportListQuery(BaseRequestDTO):
    """
    DTO for querying time reports in a team.

    API:
        GET /team/{team_id}/time_tracking
        Docs: https://developer.clickup.com/reference/getfilteredtimeentries

    Attributes:
        assignee: Filter by user ID
        task_id: Filter by task ID
        start_date: Filter by start date (epoch ms)
        end_date: Filter by end date (epoch ms)
        page: Page number (0-indexed)
        limit: Page size (max 100)

    Examples:
        # Python - query with date range
        TimeReportListQuery(start_date=1702080000000, end_date=1702166400000, limit=50).to_query()
    """

    assignee: str | None = Field(default=None, description="Filter by user ID")
    task_id: str | None = Field(default=None, description="Filter by task ID")
    start_date: EpochMs | None = Field(default=None, description=PROPERTY_START_DATE_DESCRIPTION)
    end_date: EpochMs | None = Field(default=None, description=PROPERTY_END_DATE_DESCRIPTION)
    page: int = Field(default=0, description="Page number (0-indexed)")
    limit: int = Field(default=100, description="Number of entries per page (max 100)")

    def to_query(self) -> dict[str, Any]:
        """
        Convert to query parameters for API request.

        Returns:
            dict[str, Any]: Query parameters with limit capped at 100.

        Examples:
            TimeReportListQuery(limit=150, start_date=1702080000000).to_query()
            # {"start_date": 1702080000000, "page": 0, "limit": 100}
        """
        query = {
            "page": self.page,
            "limit": min(self.limit, 100),
        }

        if self.assignee:
            query["assignee"] = self.assignee

        if self.task_id:
            query["task_id"] = self.task_id

        if self.start_date:
            query["start_date"] = self.start_date

        if self.end_date:
            query["end_date"] = self.end_date

        return query


class TimeReportResponse(BaseResponseDTO):
    """
    DTO for time report API responses.

    Attributes:
        id: Time report ID
        team_id: Team/workspace ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_duration: Total duration in milliseconds
        user_id: Filter by user ID (if applicable)
        task_id: Filter by task ID (if applicable)

    Examples:
        # Python - deserialize API response
        TimeReportResponse.deserialize({
            "id": "report_123",
            "team_id": "team_001",
            "start_date": 1702080000000,
            "end_date": 1702166400000,
            "total_duration": 3600000
        })
    """

    id: str = Field(description="Time report ID")
    team_id: str = Field(description="Team/workspace ID")
    start_date: EpochMs = Field(description=PROPERTY_START_DATE_DESCRIPTION)
    end_date: EpochMs = Field(description=PROPERTY_END_DATE_DESCRIPTION)
    total_duration: EpochMs | None = Field(default=None, description=PROPERTY_TOTAL_DURATION_DESCRIPTION)
    user_id: str | None = Field(default=None, description="Filter by user ID")
    task_id: str | None = Field(default=None, description="Filter by task ID")


class TimeReportListResponse(PaginatedResponseDTO[TimeReportResponse]):
    """
    DTO for paginated time report list responses.

    Attributes:
        items: List of time reports
        next_page: Cursor for next page (if available)
        prev_page: Cursor for previous page (if available)
        total: Total number of reports (if provided)

    Examples:
        # Python - deserialize paginated response
        TimeReportListResponse.deserialize({
            "items": [{"id": "report_123", "team_id": "team_001", ...}],
            "next_page": "cursor=2",
        })
    """

    items: List[TimeReportResponse] = Field(description="List of time reports")
