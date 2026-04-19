"""
Time Entry API resource manager.

This module provides a resource manager for interacting with ClickUp Time Entries.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Create time entries for tasks
- Retrieve time entry by ID
- List time entries with filters
- Update time entry details
- Delete time entries
- Start time tracking on a task
- Stop time tracking on a task
- Get time tracking status

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.time import TimeEntryCreate

    async with ClickUpAPIClient(api_token="pk_...") as client:
        time_api = client.time
        entry = await time_api.create(
            team_id="team_1",
            time_entry_create=TimeEntryCreate(task_id="task_123", duration=3600000)
        )

    # curl - Get a time entry
    # GET /team/{team_id}/time_entries/{time_entry_id}
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/team/team_1/time_entries/entry_123

    # wget - List time entries
    # GET /team/{team_id}/time_entries?task_id=task_123&limit=50
    wget --header="Authorization: pk_..." \
         "https://api.clickup.com/api/v2/team/team_1/time_entries?task_id=task_123&limit=50"
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

from clickup_mcp.models.dto.time import (
    TimeEntryCreate,
    TimeEntryListQuery,
    TimeEntryListResponse,
    TimeEntryResponse,
    TimeEntryUpdate,
    TimeTrackingStatusResponse,
)
from clickup_mcp.types import ClickUpTeamID

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class TimeAPI:
    """
    Time Entry API resource manager.

    Provides domain-specific methods to interact with ClickUp Time Entries using a shared
    HTTP client. Methods return DTOs (e.g., `TimeEntryResponse`) or booleans for write ops.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.time import TimeEntryCreate

        async with ClickUpAPIClient(api_token="pk_...") as client:
            time_api = client.time
            # Create
            created = await time_api.create("team_1", TimeEntryCreate(task_id="task_123", duration=3600000))
            # Get
            fetched = await time_api.get("team_1", "entry_123")
            # List
            from clickup_mcp.models.dto.time import TimeEntryListQuery
            entries = await time_api.list("team_1", TimeEntryListQuery(task_id="task_123", limit=50))
            # Update
            from clickup_mcp.models.dto.time import TimeEntryUpdate
            updated = await time_api.update("team_1", "entry_123", TimeEntryUpdate(duration=7200000))
            # Delete
            ok = await time_api.delete("team_1", "entry_123")
            # Start tracking
            ok = await time_api.start_tracking("task_123")
            # Stop tracking
            ok = await time_api.stop_tracking("task_123", "Completed work")
            # Get tracking status
            status = await time_api.get_tracking_status("task_123")
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the TimeAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(
        self, team_id: ClickUpTeamID, time_entry_create: TimeEntryCreate
    ) -> Optional[TimeEntryResponse]:
        """
        Create a new time entry for a task.

        API:
            POST /team/{team_id}/time_entries
            Docs: https://developer.clickup.com/reference/createtimeentry

        Notes:
            - Requires either duration or both start and end times
            - Returns None on non-200 responses or unexpected payloads

        Args:
            team_id: The ID of the team/workspace
            time_entry_create: TimeEntryCreate DTO with time entry details

        Returns:
            TimeEntryResponse | None: The created time entry, or None if creation failed

        Examples:
            # Python (async)
            created = await time_api.create("team_1", TimeEntryCreate(task_id="task_123", duration=3600000))

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"task_id":"task_123","duration":3600000}' \
              https://api.clickup.com/api/v2/team/team_1/time_entries

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"task_id":"task_123","duration":3600000}' \
              https://api.clickup.com/api/v2/team/team_1/time_entries
        """
        response = await self._client.post(f"/team/{team_id}/time_entries", data=time_entry_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TimeEntryResponse(**response.data)

    async def get(self, team_id: ClickUpTeamID, time_entry_id: str) -> Optional[TimeEntryResponse]:
        """
        Get a time entry by ID.

        API:
            GET /team/{team_id}/time_entries/{time_entry_id}
            Docs: https://developer.clickup.com/reference/gettimeentry

        Args:
            team_id: The ID of the team/workspace
            time_entry_id: The ID of the time entry to retrieve

        Returns:
            TimeEntryResponse | None: The time entry if found, otherwise None

        Examples:
            # Python (async)
            entry = await time_api.get("team_1", "entry_123")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/team/team_1/time_entries/entry_123

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/team/team_1/time_entries/entry_123
        """
        response = await self._client.get(f"/team/{team_id}/time_entries/{time_entry_id}")

        if not response.success or response.status_code == 404:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        logger.debug(f"Time entry API response: {response.data}")
        return TimeEntryResponse(**response.data)

    async def list(self, team_id: ClickUpTeamID, query: TimeEntryListQuery) -> Optional[TimeEntryListResponse]:
        """
        List time entries with filters.

        API:
            GET /team/{team_id}/time_entries
            Docs: https://developer.clickup.com/reference/getfilteredtimeentries

        Args:
            team_id: The ID of the team/workspace
            query: TimeEntryListQuery with filters and pagination

        Returns:
            TimeEntryListResponse | None: The paginated list of time entries, or None if request failed

        Examples:
            # Python (async)
            from clickup_mcp.models.dto.time import TimeEntryListQuery
            entries = await time_api.list("team_1", TimeEntryListQuery(task_id="task_123", limit=50))

            # curl
            curl -H "Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/team/team_1/time_entries?task_id=task_123&limit=50"

            # wget
            wget --header="Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/team/team_1/time_entries?task_id=task_123&limit=50"
        """
        response = await self._client.get(f"/team/{team_id}/time_entries", params=query.to_query())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TimeEntryListResponse(**response.data)

    async def update(
        self, team_id: ClickUpTeamID, time_entry_id: str, time_entry_update: TimeEntryUpdate
    ) -> Optional[TimeEntryResponse]:
        """
        Update a time entry.

        API:
            PUT /team/{team_id}/time_entries/{time_entry_id}
            Docs: https://developer.clickup.com/reference/updatetimeentry

        Args:
            team_id: The ID of the team/workspace
            time_entry_id: The ID of the time entry to update
            time_entry_update: TimeEntryUpdate DTO with updated details

        Returns:
            TimeEntryResponse | None: The updated time entry, or None if update failed

        Examples:
            # Python (async)
            from clickup_mcp.models.dto.time import TimeEntryUpdate
            updated = await time_api.update("team_1", "entry_123", TimeEntryUpdate(duration=7200000))

            # curl
            curl -X PUT \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"duration":7200000}' \
              https://api.clickup.com/api/v2/team/team_1/time_entries/entry_123

            # wget
            wget --method=PUT \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"duration":7200000}' \
              https://api.clickup.com/api/v2/team/team_1/time_entries/entry_123
        """
        response = await self._client.put(
            f"/team/{team_id}/time_entries/{time_entry_id}", data=time_entry_update.serialize()
        )

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TimeEntryResponse(**response.data)

    async def delete(self, team_id: ClickUpTeamID, time_entry_id: str) -> bool:
        """
        Delete a time entry.

        API:
            DELETE /team/{team_id}/time_entries/{time_entry_id}
            Docs: https://developer.clickup.com/reference/deletetimeentry

        Args:
            team_id: The ID of the team/workspace
            time_entry_id: The ID of the time entry to delete

        Returns:
            bool: True if deletion was successful, False otherwise

        Examples:
            # Python (async)
            ok = await time_api.delete("team_1", "entry_123")

            # curl
            curl -X DELETE \
              -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/team/team_1/time_entries/entry_123

            # wget
            wget --method=DELETE \
              --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/team/team_1/time_entries/entry_123
        """
        response = await self._client.delete(f"/team/{team_id}/time_entries/{time_entry_id}")

        return response.success and response.status_code == 200

    async def start_tracking(self, task_id: str) -> bool:
        """
        Start time tracking for a task.

        API:
            POST /task/{task_id}/time_tracking/start
            Docs: https://developer.clickup.com/reference/starttimer

        Args:
            task_id: The ID of the task to start tracking

        Returns:
            bool: True if tracking was started successfully, False otherwise

        Examples:
            # Python (async)
            ok = await time_api.start_tracking("task_123")

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/task/task_123/time_tracking/start

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/task/task_123/time_tracking/start
        """
        response = await self._client.post(f"/task/{task_id}/time_tracking/start")

        return response.success and response.status_code == 200

    async def stop_tracking(self, task_id: str, description: str | None = None) -> bool:
        """
        Stop time tracking for a task.

        API:
            POST /task/{task_id}/time_tracking/stop
            Docs: https://developer.clickup.com/reference/stoptimer

        Args:
            task_id: The ID of the task to stop tracking
            description: Optional description for the time entry

        Returns:
            bool: True if tracking was stopped successfully, False otherwise

        Examples:
            # Python (async)
            ok = await time_api.stop_tracking("task_123", "Completed implementation")

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"description":"Completed implementation"}' \
              https://api.clickup.com/api/v2/task/task_123/time_tracking/stop

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"description":"Completed implementation"}' \
              https://api.clickup.com/api/v2/task/task_123/time_tracking/stop
        """
        data = {}
        if description is not None:
            data["description"] = description

        response = await self._client.post(
            f"/task/{task_id}/time_tracking/stop", data=data if data else None
        )

        return response.success and response.status_code == 200

    async def get_tracking_status(self, task_id: str) -> Optional[TimeTrackingStatusResponse]:
        """
        Get time tracking status for a task.

        API:
            GET /task/{task_id}/time_tracking
            Docs: https://developer.clickup.com/reference/gettimer

        Args:
            task_id: The ID of the task to get tracking status for

        Returns:
            TimeTrackingStatusResponse | None: The tracking status if found, otherwise None

        Examples:
            # Python (async)
            status = await time_api.get_tracking_status("task_123")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/task/task_123/time_tracking

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/task/task_123/time_tracking
        """
        response = await self._client.get(f"/task/{task_id}/time_tracking")

        if not response.success or response.status_code == 404:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TimeTrackingStatusResponse(**response.data)
