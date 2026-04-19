"""
Goal API resource manager.

This module provides a resource manager for interacting with ClickUp Goals.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Create goals for teams
- Retrieve goal by ID
- Update goals
- Delete goals
- List goals with filters

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.goal import GoalCreate

    async with ClickUpAPIClient(api_token="pk_...") as client:
        goal_api = client.goal
        goal = await goal_api.create(
            team_id="team_1",
            goal_create=GoalCreate(name="Q1 Revenue Goal", due_date=1702080000000)
        )

    # curl - Get a goal
    # GET /goal/{goal_id}
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/goal/goal_123

    # wget - List goals
    # GET /team/{team_id}/goal
    wget --header="Authorization: pk_..." \
         "https://api.clickup.com/api/v2/team/team_1/goal?limit=50"
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.goal import (
    GoalCreate,
    GoalListQuery,
    GoalListResponse,
    GoalUpdate,
)
from clickup_mcp.types import ClickUpGoalID, ClickUpTeamID

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class GoalAPI:
    """
    Goal API resource manager.

    Provides domain-specific methods to interact with ClickUp Goals using a shared
    HTTP client. Methods return DTOs (e.g., `GoalListResponse`) or booleans for write ops.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.goal import GoalCreate

        async with ClickUpAPIClient(api_token="pk_...") as client:
            goal_api = client.goal
            # Create
            created = await goal_api.create("team_1", GoalCreate(name="Q1 Revenue Goal", due_date=1702080000000))
            # Get
            goal = await goal_api.get("goal_123")
            # Update
            updated = await goal_api.update("goal_123", GoalUpdate(name="Updated Goal Name"))
            # Delete
            deleted = await goal_api.delete("goal_123")
            # List
            from clickup_mcp.models.dto.goal import GoalListQuery
            goals = await goal_api.list("team_1", GoalListQuery(limit=50))
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the GoalAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, team_id: ClickUpTeamID, goal_create: GoalCreate) -> Optional[GoalListResponse]:
        """
        Create a goal for a team.

        API:
            POST /team/{team_id}/goal
            Docs: https://developer.clickup.com/reference/creategoal

        Notes:
            - Requires name and due_date to define the goal
            - Returns a list response containing the created goal

        Args:
            team_id: The ID of the team/workspace
            goal_create: GoalCreate DTO with goal criteria

        Returns:
            GoalListResponse | None: The created goal in a list response, or None if request failed

        Examples:
            # Python (async)
            created = await goal_api.create("team_1", GoalCreate(name="Q1 Revenue Goal", due_date=1702080000000))

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"name":"Q1 Revenue Goal","due_date":1702080000000}' \
              https://api.clickup.com/api/v2/team/team_1/goal

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"name":"Q1 Revenue Goal","due_date":1702080000000}' \
              https://api.clickup.com/api/v2/team/team_1/goal
        """
        response = await self._client.post(f"/team/{team_id}/goal", data=goal_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return GoalListResponse(**response.data)

    async def get(self, goal_id: ClickUpGoalID) -> Optional[dict]:
        """
        Get a goal by ID.

        API:
            GET /goal/{goal_id}
            Docs: https://developer.clickup.com/reference/getgoal

        Args:
            goal_id: The ID of the goal

        Returns:
            dict | None: The goal data, or None if request failed

        Examples:
            # Python (async)
            goal = await goal_api.get("goal_123")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/goal/goal_123

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/goal/goal_123
        """
        response = await self._client.get(f"/goal/{goal_id}")

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return response.data

    async def update(self, goal_id: ClickUpGoalID, goal_update: GoalUpdate) -> Optional[dict]:
        """
        Update a goal.

        API:
            PUT /goal/{goal_id}
            Docs: https://developer.clickup.com/reference/updategoal

        Notes:
            - Only include fields that need to be updated

        Args:
            goal_id: The ID of the goal
            goal_update: GoalUpdate DTO with updated fields

        Returns:
            dict | None: The updated goal data, or None if request failed

        Examples:
            # Python (async)
            updated = await goal_api.update("goal_123", GoalUpdate(name="Updated Goal Name"))

            # curl
            curl -X PUT \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"name":"Updated Goal Name"}' \
              https://api.clickup.com/api/v2/goal/goal_123

            # wget
            wget --method=PUT \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"name":"Updated Goal Name"}' \
              https://api.clickup.com/api/v2/goal/goal_123
        """
        response = await self._client.put(f"/goal/{goal_id}", data=goal_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return response.data

    async def delete(self, goal_id: ClickUpGoalID) -> bool:
        """
        Delete a goal.

        API:
            DELETE /goal/{goal_id}
            Docs: https://developer.clickup.com/reference/deletegoal

        Args:
            goal_id: The ID of the goal

        Returns:
            bool: True if deletion was successful, False otherwise

        Examples:
            # Python (async)
            deleted = await goal_api.delete("goal_123")

            # curl
            curl -X DELETE \
              -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/goal/goal_123

            # wget
            wget --method=DELETE \
              --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/goal/goal_123
        """
        response = await self._client.delete(f"/goal/{goal_id}")

        return response.success and response.status_code == 200

    async def list(self, team_id: ClickUpTeamID, query: GoalListQuery) -> Optional[GoalListResponse]:
        """
        List goals for a team with filters.

        API:
            GET /team/{team_id}/goal
            Docs: https://developer.clickup.com/reference/getgoals

        Args:
            team_id: The ID of the team/workspace
            query: GoalListQuery with filters and pagination

        Returns:
            GoalListResponse | None: The paginated list of goals, or None if request failed

        Examples:
            # Python (async)
            from clickup_mcp.models.dto.goal import GoalListQuery
            goals = await goal_api.list("team_1", GoalListQuery(status="active", limit=50))

            # curl
            curl -H "Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/team/team_1/goal?status=active&limit=50"

            # wget
            wget --header="Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/team/team_1/goal?status=active&limit=50"
        """
        response = await self._client.get(f"/team/{team_id}/goal", params=query.to_query())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return GoalListResponse(**response.data)
