"""
Space API resource manager.

This module provides a resource manager for interacting with ClickUp Spaces.
It follows the Resource Manager pattern described in the project documentation.
"""

from typing import TYPE_CHECKING, Optional

from clickup_mcp.models.domain.space import ClickUpSpace

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

    async def get(self, space_id: str) -> Optional[ClickUpSpace]:
        """Get a space by ID.

        Args:
            space_id: The ID of the space to retrieve.

        Returns:
            A ClickUpSpace instance representing the space, or None if not found.
        """
        response = await self._client.get(f"/space/{space_id}")

        if not response.success or response.status_code == 404:
            return None

        return ClickUpSpace(**response.data)
