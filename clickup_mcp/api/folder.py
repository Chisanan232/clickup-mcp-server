"""
Folder API resource manager.

This module provides a resource manager for interacting with ClickUp Folders.
It follows the Resource Manager pattern described in the project documentation.
"""

from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.folder import FolderCreate, FolderResp, FolderUpdate

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient


class FolderAPI:
    """Folder API resource manager.

    This class provides methods for interacting with ClickUp Folders through
    the ClickUp API. It follows the Resource Manager pattern, receiving
    a shared HTTP client instance and providing domain-specific methods.
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the FolderAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, space_id: str, folder_create: FolderCreate) -> Optional[FolderResp]:
        """Create a new folder.

        POST /space/{space_id}/folder
        https://developer.clickup.com/reference/createfolder

        Args:
            space_id: The ID of the space
            folder_create: FolderCreate DTO with folder details

        Returns:
            FolderResp DTO representing the created folder, or None if creation failed.
        """
        response = await self._client.post(f"/space/{space_id}/folder", data=folder_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return FolderResp(**response.data)

    async def get_all(self, space_id: str) -> list[FolderResp]:
        """Get all folders in a space.

        GET /space/{space_id}/folder

        Args:
            space_id: The ID of the space

        Returns:
            List of FolderResp DTOs representing folders in the space.
        """
        response = await self._client.get(f"/space/{space_id}/folder")

        if not response.success or response.status_code != 200:
            return []

        if response.data is None or not isinstance(response.data, dict):
            return []

        folders_data = response.data.get("folders", [])
        if not isinstance(folders_data, list):
            return []

        return [FolderResp(**folder_data) for folder_data in folders_data]

    async def get(self, folder_id: str) -> Optional[FolderResp]:
        """Get a folder by ID.

        GET /folder/{folder_id}

        Args:
            folder_id: The ID of the folder to retrieve.

        Returns:
            FolderResp DTO representing the folder, or None if not found.
        """
        response = await self._client.get(f"/folder/{folder_id}")

        if not response.success or response.status_code == 404:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return FolderResp(**response.data)

    async def update(self, folder_id: str, folder_update: FolderUpdate) -> Optional[FolderResp]:
        """Update a folder.

        PUT /folder/{folder_id}

        Args:
            folder_id: The ID of the folder to update
            folder_update: FolderUpdate DTO with updated folder details

        Returns:
            FolderResp DTO representing the updated folder, or None if update failed.
        """
        response = await self._client.put(f"/folder/{folder_id}", data=folder_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return FolderResp(**response.data)

    async def delete(self, folder_id: str) -> bool:
        """Delete a folder.

        DELETE /folder/{folder_id}

        Args:
            folder_id: The ID of the folder to delete

        Returns:
            True if deletion was successful, False otherwise.
        """
        response = await self._client.delete(f"/folder/{folder_id}")
        return response.success and response.status_code in (200, 204)
