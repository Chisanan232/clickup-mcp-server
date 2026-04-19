"""
Time Tracking DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Time Entry
operations, including create, update, list, and query operations. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create time entry payload
    from clickup_mcp.models.dto.time import TimeEntryCreate

    payload = TimeEntryCreate(
        task_id="task_123",
        description="Implementation work",
        duration=3600000,
    ).to_payload()
    # => {"task_id": "task_123", "description": "Implementation work", "duration": 3600000}

    # Python - Build time entry list query
    from clickup_mcp.models.dto.time import TimeEntryListQuery

    query = TimeEntryListQuery(task_id="task_123", limit=50).to_query()
    # => {"task_id": "task_123", "limit": 50}
"""

from typing import Any, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO, PaginatedResponseDTO
from .common import EpochMs, UserId

PROPERTY_DESCRIPTION_DESCRIPTION: str = "Description of the time entry"
PROPERTY_START_DESCRIPTION: str = "Start time in epoch milliseconds"
PROPERTY_END_DESCRIPTION: str = "End time in epoch milliseconds"
PROPERTY_DURATION_DESCRIPTION: str = "Duration in milliseconds"
PROPERTY_BILLABLE_DESCRIPTION: str = "Whether the time entry is billable"


class TimeEntryCreate(BaseRequestDTO):
    """
    DTO for creating a new time entry.

    API:
        POST /team/{team_id}/time_entries
        Docs: https://developer.clickup.com/reference/createtimeentry

    Notes:
        Requires either duration or both start and end times.

    Attributes:
        task_id: Task ID to log time against
        description: Optional description of the time entry
        start: Start time in epoch ms
        end: End time in epoch ms
        duration: Duration in milliseconds
        billable: Whether the time entry is billable

    Examples:
        # Python - payload build with duration
        TimeEntryCreate(
            task_id="task_123",
            description="Implementation work",
            duration=3600000,
        ).to_payload()
    """

    task_id: str = Field(description="Task ID to log time against")
    description: str | None = Field(default=None, description=PROPERTY_DESCRIPTION_DESCRIPTION)
    start: EpochMs | None = Field(default=None, description=PROPERTY_START_DESCRIPTION)
    end: EpochMs | None = Field(default=None, description=PROPERTY_END_DESCRIPTION)
    duration: EpochMs | None = Field(default=None, description=PROPERTY_DURATION_DESCRIPTION)
    billable: bool = Field(default=False, description=PROPERTY_BILLABLE_DESCRIPTION)


class TimeEntryUpdate(BaseRequestDTO):
    """
    DTO for updating an existing time entry.

    API:
        PUT /team/{team_id}/time_entries/{time_entry_id}
        Docs: https://developer.clickup.com/reference/updatetimeentry

    Notes:
        Only include fields that need to be updated.

    Attributes:
        description: New description
        start: New start time in epoch ms
        end: New end time in epoch ms
        duration: New duration in milliseconds
        billable: New billable status

    Examples:
        # Python - update duration
        TimeEntryUpdate(duration=7200000).to_payload()
    """

    description: str | None = Field(default=None, description=PROPERTY_DESCRIPTION_DESCRIPTION)
    start: EpochMs | None = Field(default=None, description=PROPERTY_START_DESCRIPTION)
    end: EpochMs | None = Field(default=None, description=PROPERTY_END_DESCRIPTION)
    duration: EpochMs | None = Field(default=None, description=PROPERTY_DURATION_DESCRIPTION)
    billable: bool | None = Field(default=None, description=PROPERTY_BILLABLE_DESCRIPTION)


class TimeEntryListQuery(BaseRequestDTO):
    """
    DTO for querying time entries in a team.

    API:
        GET /team/{team_id}/time_entries
        Docs: https://developer.clickup.com/reference/getfilteredtimeentries

    Attributes:
        task_id: Filter by task ID
        assignee: Filter by user ID
        start_date: Filter by start date (epoch ms)
        end_date: Filter by end date (epoch ms)
        page: Page number (0-indexed)
        limit: Page size (max 100)

    Examples:
        # Python - query with task filter
        TimeEntryListQuery(task_id="task_123", limit=50).to_query()
    """

    task_id: str | None = Field(default=None, description="Filter by task ID")
    assignee: UserId | None = Field(default=None, description="Filter by user ID")
    start_date: EpochMs | None = Field(default=None, description="Filter by start date (epoch ms)")
    end_date: EpochMs | None = Field(default=None, description="Filter by end date (epoch ms)")
    page: int = Field(default=0, description="Page number (0-indexed)")
    limit: int = Field(default=100, description="Number of entries per page (max 100)")

    def to_query(self) -> dict[str, Any]:
        """
        Convert to query parameters for API request.

        Returns:
            dict[str, Any]: Query parameters with limit capped at 100.

        Examples:
            TimeEntryListQuery(limit=150, task_id="task_123").to_query()
            # {"task_id": "task_123", "page": 0, "limit": 100}
        """
        query: dict[str, Any] = {
            "page": self.page,
            "limit": min(self.limit, 100),
        }

        if self.task_id:
            query["task_id"] = self.task_id

        if self.assignee:
            query["assignee"] = self.assignee

        if self.start_date:
            query["start_date"] = self.start_date

        if self.end_date:
            query["end_date"] = self.end_date

        return query


class TimeEntryResponse(BaseResponseDTO):
    """
    DTO for time entry API responses.

    Attributes:
        id: Time entry ID
        task_id: Task ID this time entry belongs to
        user_id: User ID who logged the time
        team_id: Team/workspace ID
        description: Description of the work done
        start: Start time in epoch milliseconds
        end: End time in epoch milliseconds
        duration: Duration in milliseconds
        billable: Whether the time entry is billable

    Examples:
        # Python - deserialize API response
        TimeEntryResponse.deserialize({
            "id": "entry_123",
            "task_id": "task_456",
            "user_id": 789,
            "team_id": "team_001",
            "description": "Implementation work",
            "duration": 3600000,
        })
    """

    id: str = Field(description="Time entry ID")
    task_id: str = Field(description="Task ID this time entry belongs to")
    user_id: int = Field(description="User ID who logged the time")
    team_id: str = Field(description="Team/workspace ID")
    description: str | None = Field(default=None, description=PROPERTY_DESCRIPTION_DESCRIPTION)
    start: EpochMs | None = Field(default=None, description=PROPERTY_START_DESCRIPTION)
    end: EpochMs | None = Field(default=None, description=PROPERTY_END_DESCRIPTION)
    duration: EpochMs | None = Field(default=None, description=PROPERTY_DURATION_DESCRIPTION)
    billable: bool = Field(default=False, description=PROPERTY_BILLABLE_DESCRIPTION)


class TimeEntryListResponse(PaginatedResponseDTO[TimeEntryResponse]):
    """
    DTO for paginated time entry list responses.

    Attributes:
        items: List of time entries
        next_page: Cursor for next page (if available)
        prev_page: Cursor for previous page (if available)
        total: Total number of entries (if provided)

    Examples:
        # Python - deserialize paginated response
        TimeEntryListResponse.deserialize({
            "items": [{"id": "entry_123", "task_id": "task_456", ...}],
            "next_page": "cursor=2",
        })
    """

    items: List[TimeEntryResponse] = Field(description="List of time entries")


class TimeTrackingStatusResponse(BaseResponseDTO):
    """
    DTO for time tracking status response.

    Attributes:
        active: Whether time tracking is currently active
        start: Start time of current tracking session (epoch ms)
        task_id: Task ID being tracked (if active)

    Examples:
        # Python - deserialize tracking status
        TimeTrackingStatusResponse.deserialize({
            "active": True,
            "start": 1702080000000,
            "task_id": "task_123",
        })
    """

    active: bool = Field(description="Whether time tracking is currently active")
    start: EpochMs | None = Field(default=None, description="Start time of current session (epoch ms)")
    task_id: str | None = Field(default=None, description="Task ID being tracked (if active)")
