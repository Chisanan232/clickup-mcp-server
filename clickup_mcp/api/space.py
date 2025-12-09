"""
Space API resource manager.

This module provides a resource manager for interacting with ClickUp Spaces.
It follows the Resource Manager pattern described in the project documentation.
"""

import logging
from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.dto.space import SpaceCreate, SpaceResp, SpaceUpdate

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class SpaceAPI:
    """
    Space API resource manager for ClickUp Spaces.

    This class provides methods for interacting with ClickUp Spaces through
    the ClickUp API. It follows the Resource Manager pattern, receiving
    a shared HTTP client instance and providing domain-specific methods.

    A Space in ClickUp is a container for organizing work within a team.
    Spaces can contain folders and lists, and are the top-level organizational
    unit after teams.

    Attributes:
        _client: The ClickUpAPIClient instance used for API requests

    Usage Examples:
        # Python - Create a space
        async with ClickUpAPIClient(api_token="pk_...") as client:
            space_create = SpaceCreate(name="My Space")
            space = await client.space.create(team_id="123", space_create=space_create)

        # Python - Get all spaces in a team
        async with ClickUpAPIClient(api_token="pk_...") as client:
            spaces = await client.space.get_all(team_id="123")

        # Python - Get a specific space
        async with ClickUpAPIClient(api_token="pk_...") as client:
            space = await client.space.get(space_id="456")
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """
        Initialize the SpaceAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.

        Usage Examples:
            # Python - Initialize (typically done automatically by ClickUpAPIClient)
            from clickup_mcp.api.space import SpaceAPI
            space_api = SpaceAPI(client)
        """
        self._client = client

    async def create(self, team_id: str, space_create: SpaceCreate) -> Optional[SpaceResp]:
        """
        Create a new space in a team.

        Creates a new space within the specified team/workspace. The space
        will be empty initially and can contain folders and lists.

        API Reference:
            POST /team/{team_id}/space
            https://developer.clickup.com/reference/createspace

        Args:
            team_id: The ID of the team/workspace where the space will be created
            space_create: SpaceCreate DTO with space details (name, color, etc.)

        Returns:
            SpaceResp DTO representing the created space, or None if creation failed.

        Usage Examples:
            # Python - Create a space with a name
            from clickup_mcp.models.dto.space import SpaceCreate

            space_create = SpaceCreate(name="My New Space")
            space = await client.space.create(team_id="123", space_create=space_create)

            # curl - Create a space
            curl -X POST \\
                 -H "Authorization: pk_..." \\
                 -H "Content-Type: application/json" \\
                 -d '{"name": "My New Space"}' \\
                 https://api.clickup.com/api/v2/team/123/space

            # wget - Create a space
            wget --method=POST \\
                 --header="Authorization: pk_..." \\
                 --header="Content-Type: application/json" \\
                 --body-data='{"name": "My New Space"}' \\
                 https://api.clickup.com/api/v2/team/123/space
        """
        response = await self._client.post(f"/team/{team_id}/space", data=space_create.serialize())

        # Some APIs may return 201 Created on success
        if not response.success or response.status_code not in (200, 201):
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return SpaceResp(**response.data)

    async def get_all(self, team_id: str) -> list[SpaceResp]:
        """
        Get all spaces in a team/workspace.

        Retrieves a list of all spaces within the specified team. This is useful
        for discovering available spaces and their properties.

        API Reference:
            GET /team/{team_id}/space
            https://developer.clickup.com/reference/getspaces

        Args:
            team_id: The ID of the team/workspace to retrieve spaces from

        Returns:
            List of SpaceResp DTOs representing spaces in the team.
            Returns an empty list if the request fails or no spaces exist.

        Usage Examples:
            # Python - Get all spaces
            spaces = await client.space.get_all(team_id="123")
            for space in spaces:
                print(f"Space: {space.name} (ID: {space.id})")

            # curl - Get all spaces
            curl -H "Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/team/123/space

            # wget - Get all spaces
            wget --header="Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/team/123/space
        """
        response = await self._client.get(f"/team/{team_id}/space")

        if not response.success or response.status_code != 200:
            return []

        if response.data is None or not isinstance(response.data, dict):
            return []

        spaces_data = response.data.get("spaces", [])
        if not isinstance(spaces_data, list):
            return []

        logger.debug(f"All spaces: {spaces_data}")
        return [SpaceResp(**space_data) for space_data in spaces_data]

    async def get(self, space_id: str) -> Optional[SpaceResp]:
        """
        Get a space by ID.

        Retrieves detailed information about a specific space by its ID.
        This includes the space's name, color, and other properties.

        API Reference:
            GET /space/{space_id}

        Args:
            space_id: The ID of the space to retrieve.

        Returns:
            SpaceResp DTO representing the space, or None if not found.

        Usage Examples:
            # Python - Get a space by ID
            space = await client.space.get(space_id="456")
            if space:
                print(f"Space: {space.name}")

            # curl - Get a space
            curl -H "Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/space/456

            # wget - Get a space
            wget --header="Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/space/456
        """
        response = await self._client.get(f"/space/{space_id}")

        if not response.success or response.status_code == 404:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        logger.debug(f"Space API response: {response.data}")
        return SpaceResp(**response.data)

    async def update(self, space_id: str, space_update: SpaceUpdate) -> Optional[SpaceResp]:
        """
        Update a space.

        Updates the properties of an existing space, such as its name or color.
        Only the fields provided in the SpaceUpdate DTO will be modified.

        API Reference:
            PUT /space/{space_id}

        Args:
            space_id: The ID of the space to update
            space_update: SpaceUpdate DTO with updated space details (name, color, etc.)

        Returns:
            SpaceResp DTO representing the updated space, or None if update failed.

        Usage Examples:
            # Python - Update a space name
            from clickup_mcp.models.dto.space import SpaceUpdate

            space_update = SpaceUpdate(name="Updated Space Name")
            space = await client.space.update(space_id="456", space_update=space_update)

            # curl - Update a space
            curl -X PUT \\
                 -H "Authorization: pk_..." \\
                 -H "Content-Type: application/json" \\
                 -d '{"name": "Updated Space Name"}' \\
                 https://api.clickup.com/api/v2/space/456

            # wget - Update a space
            wget --method=PUT \\
                 --header="Authorization: pk_..." \\
                 --header="Content-Type: application/json" \\
                 --body-data='{"name": "Updated Space Name"}' \\
                 https://api.clickup.com/api/v2/space/456
        """
        response = await self._client.put(f"/space/{space_id}", data=space_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return SpaceResp(**response.data)

    async def delete(self, space_id: str) -> bool:
        """
        Delete a space.

        Permanently deletes a space and all of its contents (folders, lists, tasks).
        This action cannot be undone, so use with caution.

        API Reference:
            DELETE /space/{space_id}

        Args:
            space_id: The ID of the space to delete

        Returns:
            True if deletion was successful, False otherwise.

        Usage Examples:
            # Python - Delete a space
            success = await client.space.delete(space_id="456")
            if success:
                print("Space deleted successfully")

            # curl - Delete a space
            curl -X DELETE \\
                 -H "Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/space/456

            # wget - Delete a space
            wget --method=DELETE \\
                 --header="Authorization: pk_..." \\
                 https://api.clickup.com/api/v2/space/456
        """
        response = await self._client.delete(f"/space/{space_id}")
        return response.success and response.status_code in (200, 204)
