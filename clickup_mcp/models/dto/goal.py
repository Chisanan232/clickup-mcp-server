"""
Goal DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Goal
operations, including create, update, list, and query operations. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create goal payload
    from clickup_mcp.models.dto.goal import GoalCreate

    payload = GoalCreate(
        name="Q1 Revenue Goal",
        description="Achieve $1M in revenue",
        due_date=1702080000000,
    ).to_payload()
    # => {"name": "Q1 Revenue Goal", "description": "Achieve $1M in revenue", "due_date": 1702080000000}

    # Python - Build goal list query
    from clickup_mcp.models.dto.goal import GoalListQuery

    query = GoalListQuery(status="active", limit=50).to_query()
    # => {"status": "active", "limit": 50}
"""

from typing import Any, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO, PaginatedResponseDTO
from .common import EpochMs

PROPERTY_NAME_DESCRIPTION: str = "Goal name/title"
PROPERTY_DESCRIPTION_DESCRIPTION: str = "Description of the goal"
PROPERTY_DUE_DATE_DESCRIPTION: str = "Due date in epoch milliseconds"
PROPERTY_STATUS_DESCRIPTION: str = "Goal status (e.g., 'active', 'completed', 'paused')"


class GoalCreate(BaseRequestDTO):
    """
    DTO for creating a new goal.

    API:
        POST /team/{team_id}/goal
        Docs: https://developer.clickup.com/reference/creategoal

    Notes:
        Requires name and due_date to define the goal.

    Attributes:
        name: Goal name/title
        description: Description of the goal
        due_date: Due date in epoch ms
        key_results: List of key result names
        multiple_owners: Whether multiple users can own this goal
        owners: List of user IDs who own this goal

    Examples:
        # Python - payload build
        GoalCreate(
            name="Q1 Revenue Goal",
            description="Achieve $1M in revenue",
            due_date=1702080000000,
        ).to_payload()
    """

    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    description: str | None = Field(default=None, description=PROPERTY_DESCRIPTION_DESCRIPTION)
    due_date: EpochMs | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    key_results: List[str] = Field(default_factory=list, description="List of key result names")
    multiple_owners: bool = Field(default=False, description="Whether multiple users can own this goal")
    owners: List[str] = Field(default_factory=list, description="List of user IDs who own this goal")


class GoalUpdate(BaseRequestDTO):
    """
    DTO for updating an existing goal.

    API:
        PUT /goal/{goal_id}
        Docs: https://developer.clickup.com/reference/updategoal

    Notes:
        Only include fields that need to be updated.

    Attributes:
        name: New goal name
        description: New description
        due_date: New due date in epoch ms
        key_results: New list of key result names
        owners: New list of user IDs who own this goal
        status: New goal status

    Examples:
        # Python - update name
        GoalUpdate(name="Updated Goal Name").to_payload()
    """

    name: str | None = Field(default=None, description=PROPERTY_NAME_DESCRIPTION)
    description: str | None = Field(default=None, description=PROPERTY_DESCRIPTION_DESCRIPTION)
    due_date: EpochMs | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    key_results: List[str] | None = Field(default=None, description="New list of key result names")
    owners: List[str] | None = Field(default=None, description="New list of user IDs")
    status: str | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)


class GoalListQuery(BaseRequestDTO):
    """
    DTO for querying goals in a team.

    API:
        GET /team/{team_id}/goal
        Docs: https://developer.clickup.com/reference/getgoals

    Attributes:
        status: Filter by goal status
        owner: Filter by user ID
        start_date: Filter by start date (epoch ms)
        end_date: Filter by end date (epoch ms)
        page: Page number (0-indexed)
        limit: Page size (max 100)

    Examples:
        # Python - query with status filter
        GoalListQuery(status="active", limit=50).to_query()
    """

    status: str | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)
    owner: str | None = Field(default=None, description="Filter by user ID")
    start_date: EpochMs | None = Field(default=None, description="Filter by start date (epoch ms)")
    end_date: EpochMs | None = Field(default=None, description="Filter by end date (epoch ms)")
    page: int = Field(default=0, description="Page number (0-indexed)")
    limit: int = Field(default=100, description="Number of goals per page (max 100)")

    def to_query(self) -> dict[str, Any]:
        """
        Convert to query parameters for API request.

        Returns:
            dict[str, Any]: Query parameters with limit capped at 100.

        Examples:
            GoalListQuery(limit=150, status="active").to_query()
            # {"status": "active", "page": 0, "limit": 100}
        """
        query: dict[str, Any] = {
            "page": self.page,
            "limit": min(self.limit, 100),
        }

        if self.status:
            query["status"] = self.status

        if self.owner:
            query["owner"] = self.owner

        if self.start_date:
            query["start_date"] = self.start_date

        if self.end_date:
            query["end_date"] = self.end_date

        return query


class GoalResponse(BaseResponseDTO):
    """
    DTO for goal API responses.

    Attributes:
        id: Goal ID
        team_id: Team/workspace ID this goal belongs to
        name: Goal name/title
        description: Description of the goal
        due_date: Due date in epoch milliseconds
        status: Goal status
        key_results: List of key result names
        owners: List of user IDs who own this goal
        multiple_owners: Whether multiple users can own this goal
        date_created: Creation date in epoch milliseconds
        date_updated: Last update date in epoch milliseconds

    Examples:
        # Python - deserialize API response
        GoalResponse.deserialize({
            "id": "goal_123",
            "team_id": "team_001",
            "name": "Q1 Revenue Goal",
            "due_date": 1702080000000,
        })
    """

    id: str = Field(description="Goal ID")
    team_id: str = Field(description="Team/workspace ID this goal belongs to")
    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    description: str | None = Field(default=None, description=PROPERTY_DESCRIPTION_DESCRIPTION)
    due_date: EpochMs | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    status: str = Field(default="active", description=PROPERTY_STATUS_DESCRIPTION)
    key_results: List[str] = Field(default_factory=list, description="List of key result names")
    owners: List[str] = Field(default_factory=list, description="List of user IDs who own this goal")
    multiple_owners: bool = Field(default=False, description="Whether multiple users can own this goal")
    date_created: EpochMs | None = Field(default=None, description="Creation date in epoch milliseconds")
    date_updated: EpochMs | None = Field(default=None, description="Last update date in epoch milliseconds")


class GoalListResponse(PaginatedResponseDTO[GoalResponse]):
    """
    DTO for paginated goal list responses.

    Attributes:
        items: List of goals
        next_page: Cursor for next page (if available)
        prev_page: Cursor for previous page (if available)
        total: Total number of goals (if provided)

    Examples:
        # Python - deserialize paginated response
        GoalListResponse.deserialize({
            "items": [{"id": "goal_123", "name": "Q1 Revenue Goal", ...}],
            "next_page": "cursor=2",
        })
    """

    items: List[GoalResponse] = Field(description="List of goals")
