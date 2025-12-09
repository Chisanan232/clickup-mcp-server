"""
List API resource manager.

This module provides a resource manager for interacting with ClickUp Lists.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Create lists inside a folder
- List lists within a folder
- List folderless lists within a space
- Retrieve a list by ID
- Update list properties
- Delete a list
- Add/remove tasks to/from a list (TIML)

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.list import ListCreate, ListUpdate

    async with ClickUpAPIClient(api_token="pk_...") as client:
        list_api = client.list
        created = await list_api.create("folder_1", ListCreate(name="Sprint Backlog"))

    # curl - Get list by ID
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/list/lst_1

    # wget - List folderless lists in a space
    wget --header="Authorization: pk_..." \
         https://api.clickup.com/api/v2/space/spc_1/list
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.list import ListCreate, ListResp, ListUpdate

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class ListAPI:
    """
    List API resource manager.

    Provides methods to interact with ClickUp Lists using a shared HTTP client.
    Methods return DTOs (e.g., `ListResp`) or booleans for write operations.

    Usage Examples:
        # Python (async)
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.list import ListCreate, ListUpdate

        async with ClickUpAPIClient(api_token="pk_...") as client:
            list_api = client.list
            created = await list_api.create("folder_1", ListCreate(name="Sprint Backlog"))
            got = await list_api.get("lst_1")
            in_folder = await list_api.get_all_in_folder("folder_1")
            folderless = await list_api.get_all_folderless("space_1")
            updated = await list_api.update("lst_1", ListUpdate(name="Sprint 12"))
            deleted = await list_api.delete("lst_1")
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the ListAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, folder_id: str, list_create: ListCreate) -> Optional[ListResp]:
        """
        Create a new list inside a folder.

        API:
            POST /folder/{folder_id}/list
            Docs: https://developer.clickup.com/reference/createlist

        Args:
            folder_id: The ID of the folder
            list_create: ListCreate DTO with list details

        Returns:
            ListResp | None: The created list, or None if creation failed

        Examples:
            # Python (async)
            created = await list_api.create("folder_1", ListCreate(name="Sprint Backlog"))

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"name":"Sprint Backlog"}' \
              https://api.clickup.com/api/v2/folder/folder_1/list

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"name":"Sprint Backlog"}' \
              https://api.clickup.com/api/v2/folder/folder_1/list
        """
        response = await self._client.post(f"/folder/{folder_id}/list", data=list_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return ListResp(**response.data)

    async def get_all_in_folder(self, folder_id: str) -> list[ListResp]:
        """
        Get all lists in a folder.

        API:
            GET /folder/{folder_id}/list

        Args:
            folder_id: The ID of the folder

        Returns:
            list[ListResp]: Lists in the folder (empty if none or request failed)

        Examples:
            # Python (async)
            lists = await list_api.get_all_in_folder("folder_1")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/folder/folder_1/list

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/folder/folder_1/list
        """
        response = await self._client.get(f"/folder/{folder_id}/list")

        if not response.success or response.status_code != 200:
            return []

        if response.data is None or not isinstance(response.data, dict):
            return []

        lists_data = response.data.get("lists", [])
        if not isinstance(lists_data, list):
            return []

        logger.debug(f"All lists: {lists_data}")
        return [ListResp(**list_data) for list_data in lists_data]

    async def get_all_folderless(self, space_id: str) -> list[ListResp]:
        """
        Get all folderless lists in a space.

        API:
            GET /space/{space_id}/list

        Args:
            space_id: The ID of the space

        Returns:
            list[ListResp]: Folderless lists in the space (empty if none or request failed)

        Examples:
            # Python (async)
            lists = await list_api.get_all_folderless("space_1")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/space/space_1/list

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/space/space_1/list
        """
        response = await self._client.get(f"/space/{space_id}/list")

        if not response.success or response.status_code != 200:
            return []

        if response.data is None or not isinstance(response.data, dict):
            return []

        lists_data = response.data.get("lists", [])
        if not isinstance(lists_data, list):
            return []

        logger.debug(f"All folderless lists: {lists_data}")
        return [ListResp(**list_data) for list_data in lists_data]

    async def get(self, list_id: str) -> Optional[ListResp]:
        """
        Get a list by ID.

        API:
            GET /list/{list_id}
            Docs: https://developer.clickup.com/reference/getlist

        Args:
            list_id: The ID of the list to retrieve.

        Returns:
            ListResp | None: The list, or None if not found

        Examples:
            # Python (async)
            lst = await list_api.get("lst_1")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/list/lst_1

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/list/lst_1
        """
        response = await self._client.get(f"/list/{list_id}")

        if not response.success or response.status_code == 404:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        logger.debug(f"List API response: {response.data}")
        return ListResp(**response.data)

    async def update(self, list_id: str, list_update: ListUpdate) -> Optional[ListResp]:
        """
        Update a list's properties.

        API:
            PUT /list/{list_id}

        Args:
            list_id: The ID of the list to update
            list_update: ListUpdate DTO with updated list details

        Returns:
            ListResp | None: The updated list, or None if update failed

        Examples:
            # Python (async)
            updated = await list_api.update("lst_1", ListUpdate(name="Sprint 12"))

            # curl
            curl -X PUT \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"name":"Sprint 12"}' \
              https://api.clickup.com/api/v2/list/lst_1

            # wget
            wget --method=PUT \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"name":"Sprint 12"}' \
              https://api.clickup.com/api/v2/list/lst_1
        """
        response = await self._client.put(f"/list/{list_id}", data=list_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return ListResp(**response.data)

    async def delete(self, list_id: str) -> bool:
        """
        Delete a list.

        API:
            DELETE /list/{list_id}

        Args:
            list_id: The ID of the list to delete

        Returns:
            bool: True if deletion was successful, otherwise False

        Examples:
            # Python (async)
            ok = await list_api.delete("lst_1")

            # curl
            curl -X DELETE -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/list/lst_1

            # wget
            wget --method=DELETE --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/list/lst_1
        """
        response = await self._client.delete(f"/list/{list_id}")
        return response.success and response.status_code in (200, 204)

    async def add_task(self, list_id: str, task_id: str) -> bool:
        """
        Add a task to a list (TIML - Tasks in Multiple Lists).

        API:
            POST /list/{list_id}/task/{task_id}
            Docs: https://developer.clickup.com/reference/addtasktolist

        Requires ClickApp. Allows a task to be added to multiple lists.

        Args:
            list_id: The ID of the list
            task_id: The ID of the task to add

        Returns:
            bool: True if task was successfully added, otherwise False

        Examples:
            # Python (async)
            ok = await list_api.add_task("lst_1", "tsk_1")

            # curl
            curl -X POST -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/list/lst_1/task/tsk_1

            # wget
            wget --method=POST --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/list/lst_1/task/tsk_1
        """
        response = await self._client.post(f"/list/{list_id}/task/{task_id}")
        return response.success and response.status_code in (200, 204)

    async def remove_task(self, list_id: str, task_id: str) -> bool:
        """
        Remove a task from a list (TIML - Tasks in Multiple Lists).

        API:
            DELETE /list/{list_id}/task/{task_id}

        Args:
            list_id: The ID of the list
            task_id: The ID of the task to remove

        Returns:
            bool: True if task was successfully removed, otherwise False

        Examples:
            # Python (async)
            ok = await list_api.remove_task("lst_1", "tsk_1")

            # curl
            curl -X DELETE -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/list/lst_1/task/tsk_1

            # wget
            wget --method=DELETE --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/list/lst_1/task/tsk_1
        """
        response = await self._client.delete(f"/list/{list_id}/task/{task_id}")
        return response.success and response.status_code in (200, 204)
