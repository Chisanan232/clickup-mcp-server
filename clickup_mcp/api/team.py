"""
Team API resource manager.

This module provides a resource manager for interacting with ClickUp Teams/Workspaces.
It follows the Resource Manager pattern described in the project documentation.
"""

import logging
from typing import TYPE_CHECKING, List

from clickup_mcp.models.domain.team import ClickUpTeam
from clickup_mcp.models.dto.space import SpaceResp

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class TeamAPI:
    """Team API resource manager.

    This class provides methods for interacting with ClickUp Teams/Workspaces through
    the ClickUp API. It follows the Resource Manager pattern, receiving
    a shared HTTP client instance and providing domain-specific methods.
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the TeamAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def get_authorized_teams(self) -> List[ClickUpTeam]:
        """Get authorized teams/workspaces available to the authenticated user.

        Returns:
            A list of ClickUpTeam instances representing the authorized teams/workspaces.
            Returns an empty list if no teams are found or if an error occurs.
        """
        response = await self._client.get("/team")

        if not response.success or response.status_code != 200:
            return []

        # Ensure response.data is a valid dictionary before processing
        if response.data is None or not isinstance(response.data, dict) or "teams" not in response.data:
            return []

        teams_data = response.data["teams"]
        if not isinstance(teams_data, list):
            return []

        logger.debug(f"Authorized teams: {teams_data}")
        # Create a list of ClickUpTeam instances
        return [ClickUpTeam(**team_data) for team_data in teams_data]

    async def get_spaces(self, team_id: str) -> list[SpaceResp]:
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

        logger.debug(f"All spaces: {spaces_data}")
        return [SpaceResp(**space_data) for space_data in spaces_data]
