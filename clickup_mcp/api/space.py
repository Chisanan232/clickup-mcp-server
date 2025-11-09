"""
Space API resource manager.

This module provides a resource manager for interacting with ClickUp Spaces.
It follows the Resource Manager pattern described in the project documentation.
"""

from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.domain.space import ClickUpSpace
from clickup_mcp.models.dto.space import SpaceCreate, SpaceResp, SpaceUpdate

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient


class SpaceAPI:
    """Space API resource manager.

    This class provides methods for interacting with ClickUp Spaces through
    the ClickUp API. It follows the Resource Manager pattern, receiving
    a shared HTTP client instance and providing domain-specific methods.
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the SpaceAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, team_id: str, space_create: SpaceCreate) -> Optional[SpaceResp]:
        """Create a new space.

        POST /team/{team_id}/space
        https://developer.clickup.com/reference/createspace

        Args:
            team_id: The ID of the team/workspace
            space_create: SpaceCreate DTO with space details

        Returns:
            SpaceResp DTO representing the created space, or None if creation failed.
        """
        response = await self._client.post(f"/team/{team_id}/space", data=space_create.serialize())

        # Some APIs may return 201 Created on success
        if not response.success or response.status_code not in (200, 201):
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return SpaceResp(**response.data)

    async def get_all(self, team_id: str) -> list[SpaceResp]:
        """Get all spaces in a team/workspace.

        GET /team/{team_id}/space
        https://developer.clickup.com/reference/getspaces

        Args:
            team_id: The ID of the team/workspace

        Returns:
            List of SpaceResp DTOs representing spaces in the team.
        """
        response = await self._client.get(f"/team/{team_id}/space")

        if not response.success or response.status_code != 200:
            return []

        if response.data is None or not isinstance(response.data, dict):
            return []

        spaces_data = response.data.get("spaces", [])
        if not isinstance(spaces_data, list):
            return []

        return [SpaceResp(**space_data) for space_data in spaces_data]

    async def get(self, space_id: str) -> Optional[SpaceResp]:
        """Get a space by ID.

        GET /space/{space_id}

        Args:
            space_id: The ID of the space to retrieve.

        Returns:
            SpaceResp DTO representing the space, or None if not found.
        """
        response = await self._client.get(f"/space/{space_id}")

        if not response.success or response.status_code == 404:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return SpaceResp(**response.data)

    async def update(self, space_id: str, space_update: SpaceUpdate) -> Optional[SpaceResp]:
        """Update a space.

        PUT /space/{space_id}

        Args:
            space_id: The ID of the space to update
            space_update: SpaceUpdate DTO with updated space details

        Returns:
            SpaceResp DTO representing the updated space, or None if update failed.
        """
        response = await self._client.put(f"/space/{space_id}", data=space_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return SpaceResp(**response.data)

    async def delete(self, space_id: str) -> bool:
        """Delete a space.

        DELETE /space/{space_id}

        Args:
            space_id: The ID of the space to delete

        Returns:
            True if deletion was successful, False otherwise.
        """
        response = await self._client.delete(f"/space/{space_id}")
        return response.success and response.status_code in (200, 204)
