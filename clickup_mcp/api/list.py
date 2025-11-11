"""
List API resource manager.

This module provides a resource manager for interacting with ClickUp Lists.
It follows the Resource Manager pattern described in the project documentation.
"""

import logging

from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.list import ListCreate, ListResp, ListUpdate

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class ListAPI:
    """List API resource manager.

    This class provides methods for interacting with ClickUp Lists through
    the ClickUp API. It follows the Resource Manager pattern, receiving
    a shared HTTP client instance and providing domain-specific methods.
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the ListAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, folder_id: str, list_create: ListCreate) -> Optional[ListResp]:
        """Create a new list.

        POST /folder/{folder_id}/list
        https://developer.clickup.com/reference/createlist

        Args:
            folder_id: The ID of the folder
            list_create: ListCreate DTO with list details

        Returns:
            ListResp DTO representing the created list, or None if creation failed.
        """
        response = await self._client.post(f"/folder/{folder_id}/list", data=list_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return ListResp(**response.data)

    async def get_all_in_folder(self, folder_id: str) -> list[ListResp]:
        """Get all lists in a folder.

        GET /folder/{folder_id}/list

        Args:
            folder_id: The ID of the folder

        Returns:
            List of ListResp DTOs representing lists in the folder.
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
        """Get all folderless lists in a space.

        GET /space/{space_id}/list

        Args:
            space_id: The ID of the space

        Returns:
            List of ListResp DTOs representing folderless lists in the space.
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
        """Get a list by ID.

        GET /list/{list_id}
        https://developer.clickup.com/reference/getlist

        Args:
            list_id: The ID of the list to retrieve.

        Returns:
            ListResp DTO representing the list, or None if not found.
        """
        response = await self._client.get(f"/list/{list_id}")

        if not response.success or response.status_code == 404:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        logger.debug(f"List API response: {response.data}")
        return ListResp(**response.data)

    async def update(self, list_id: str, list_update: ListUpdate) -> Optional[ListResp]:
        """Update a list.

        PUT /list/{list_id}

        Args:
            list_id: The ID of the list to update
            list_update: ListUpdate DTO with updated list details

        Returns:
            ListResp DTO representing the updated list, or None if update failed.
        """
        response = await self._client.put(f"/list/{list_id}", data=list_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return ListResp(**response.data)

    async def delete(self, list_id: str) -> bool:
        """Delete a list.

        DELETE /list/{list_id}

        Args:
            list_id: The ID of the list to delete

        Returns:
            True if deletion was successful, False otherwise.
        """
        response = await self._client.delete(f"/list/{list_id}")
        return response.success and response.status_code in (200, 204)

    async def add_task(self, list_id: str, task_id: str) -> bool:
        """Add a task to a list (TIML - Tasks in Multiple Lists).

        POST /list/{list_id}/task/{task_id}
        https://developer.clickup.com/reference/addtasktolist

        Requires ClickApp. Allows a task to be added to multiple lists.

        Args:
            list_id: The ID of the list
            task_id: The ID of the task to add

        Returns:
            True if task was successfully added, False otherwise.
        """
        response = await self._client.post(f"/list/{list_id}/task/{task_id}")
        return response.success and response.status_code in (200, 204)

    async def remove_task(self, list_id: str, task_id: str) -> bool:
        """Remove a task from a list (TIML - Tasks in Multiple Lists).

        DELETE /list/{list_id}/task/{task_id}

        Args:
            list_id: The ID of the list
            task_id: The ID of the task to remove

        Returns:
            True if task was successfully removed, False otherwise.
        """
        response = await self._client.delete(f"/list/{list_id}/task/{task_id}")
        return response.success and response.status_code in (200, 204)
