"""
Folder API resource manager.

This module provides a resource manager for interacting with ClickUp Folders.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Create folders in a space
- List folders in a space
- Retrieve a folder by ID
- Update folder properties
- Delete a folder

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.folder import FolderCreate

    async with ClickUpAPIClient(api_token="pk_...") as client:
        folder_api = client.folder
        created = await folder_api.create("space_1", FolderCreate(name="Planning"))

    # curl - List folders in a space
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/space/space_1/folder

    # wget - Delete folder
    wget --method=DELETE --header="Authorization: pk_..." \
         https://api.clickup.com/api/v2/folder/fld_1
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.folder import FolderCreate, FolderResp, FolderUpdate
from clickup_mcp.types import ClickUpFolderID, ClickUpSpaceID

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class FolderAPI:
    """
    Folder API resource manager.

    Provides methods to interact with ClickUp Folders using a shared HTTP client.
    Methods return DTOs (e.g., `FolderResp`) or booleans for write operations.

    Usage Examples:
        # Python (async)
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.folder import FolderCreate, FolderUpdate

        async with ClickUpAPIClient(api_token="pk_...") as client:
            folder_api = client.folder
            created = await folder_api.create("space_1", FolderCreate(name="Planning"))
            got = await folder_api.get("fld_1")
            all_in_space = await folder_api.get_all("space_1")
            updated = await folder_api.update("fld_1", FolderUpdate(name="Plans"))
            deleted = await folder_api.delete("fld_1")
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the FolderAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, space_id: ClickUpSpaceID, folder_create: FolderCreate) -> Optional[FolderResp]:
        """
        Create a new folder in a space.

        API:
            POST /space/{space_id}/folder
            Docs: https://developer.clickup.com/reference/createfolder

        Args:
            space_id: The ID of the space
            folder_create: FolderCreate DTO with folder details

        Returns:
            FolderResp | None: The created folder, or None if creation failed

        Examples:
            # Python (async)
            created = await folder_api.create("space_1", FolderCreate(name="Planning"))

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"name":"Planning"}' \
              https://api.clickup.com/api/v2/space/space_1/folder

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"name":"Planning"}' \
              https://api.clickup.com/api/v2/space/space_1/folder
        """
        response = await self._client.post(f"/space/{space_id}/folder", data=folder_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return FolderResp(**response.data)

    async def get_all(self, space_id: ClickUpSpaceID) -> list[FolderResp]:
        """
        Get all folders in a space.

        API:
            GET /space/{space_id}/folder

        Args:
            space_id: The ID of the space

        Returns:
            list[FolderResp]: Folders in the space (empty list if none or request failed)

        Examples:
            # Python (async)
            folders = await folder_api.get_all("space_1")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/space/space_1/folder

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/space/space_1/folder
        """
        response = await self._client.get(f"/space/{space_id}/folder")

        if not response.success or response.status_code != 200:
            return []

        if response.data is None or not isinstance(response.data, dict):
            return []

        folders_data = response.data.get("folders", [])
        logger.debug(f"All folders: {folders_data}")
        if not isinstance(folders_data, list):
            return []

        return [FolderResp(**folder_data) for folder_data in folders_data]

    async def get(self, folder_id: ClickUpFolderID) -> Optional[FolderResp]:
        """
        Get a folder by ID.

        API:
            GET /folder/{folder_id}

        Args:
            folder_id: The ID of the folder to retrieve.

        Returns:
            FolderResp | None: The folder, or None if not found

        Examples:
            # Python (async)
            folder = await folder_api.get("fld_1")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/folder/fld_1

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/folder/fld_1
        """
        response = await self._client.get(f"/folder/{folder_id}")

        if not response.success or response.status_code == 404:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        logger.debug(f"Folder API response: {response.data}")
        return FolderResp(**response.data)

    async def update(self, folder_id: ClickUpFolderID, folder_update: FolderUpdate) -> Optional[FolderResp]:
        """
        Update a folder's properties.

        API:
            PUT /folder/{folder_id}

        Args:
            folder_id: The ID of the folder to update
            folder_update: FolderUpdate DTO with updated folder details

        Returns:
            FolderResp | None: The updated folder, or None if update failed

        Examples:
            # Python (async)
            updated = await folder_api.update("fld_1", FolderUpdate(name="Plans"))

            # curl
            curl -X PUT \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"name":"Plans"}' \
              https://api.clickup.com/api/v2/folder/fld_1

            # wget
            wget --method=PUT \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"name":"Plans"}' \
              https://api.clickup.com/api/v2/folder/fld_1
        """
        response = await self._client.put(f"/folder/{folder_id}", data=folder_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return FolderResp(**response.data)

    async def delete(self, folder_id: ClickUpFolderID) -> bool:
        """
        Delete a folder.

        API:
            DELETE /folder/{folder_id}

        Args:
            folder_id: The ID of the folder to delete

        Returns:
            bool: True if deletion was successful, otherwise False

        Examples:
            # Python (async)
            ok = await folder_api.delete("fld_1")

            # curl
            curl -X DELETE -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/folder/fld_1

            # wget
            wget --method=DELETE --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/folder/fld_1
        """
        response = await self._client.delete(f"/folder/{folder_id}")
        return response.success and response.status_code in (200, 204)
