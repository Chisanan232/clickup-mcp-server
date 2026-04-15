"""
Team API resource manager.

This module provides a resource manager for interacting with ClickUp Teams/Workspaces.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- List authorized teams/workspaces for the current token
- List spaces within a team

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient

    async with ClickUpAPIClient(api_token="pk_...") as client:
        team_api = client.team
        teams = await team_api.get_authorized_teams()

    # curl - List spaces in a team
    # GET /team/{team_id}/space
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/team/123/space

    # wget - Get teams (implicit via /team)
    wget --header="Authorization: pk_..." \
         https://api.clickup.com/api/v2/team
"""

import logging
from typing import TYPE_CHECKING, List, Optional

from clickup_mcp.models.domain.team import ClickUpTeam
from clickup_mcp.models.dto.space import SpaceResp
from clickup_mcp.models.dto.workspace import WorkspaceCreate, WorkspaceResp, WorkspaceUpdate
from clickup_mcp.types import ClickUpTeamID

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class TeamAPI:
    """
    Team API resource manager.

    Provides methods for interacting with ClickUp Teams/Workspaces using a shared
    HTTP client instance.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient

        async with ClickUpAPIClient(api_token="pk_...") as client:
            team_api = client.team
            teams = await team_api.get_authorized_teams()
            spaces = await team_api.get_spaces("123")
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the TeamAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def get_authorized_teams(self) -> List[ClickUpTeam]:
        """
        Get teams/workspaces authorized for the current token.

        API:
            GET /team

        Returns:
            list[ClickUpTeam]: Authorized teams/workspaces. Returns an empty list on errors
            or when no teams are available.

        Examples:
            # Python (async)
            teams = await team_api.get_authorized_teams()
            for t in teams:
                print(t.name)

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/team

            # wget
            wget --header="Authorization: pk_..." \
                 https://api.clickup.com/api/v2/team
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

    async def get_spaces(self, team_id: ClickUpTeamID) -> list[SpaceResp]:
        """
        Get all spaces in a team/workspace.

        API:
            GET /team/{team_id}/space
            Docs: https://developer.clickup.com/reference/getspaces

        Args:
            team_id: The ID of the team/workspace

        Returns:
            list[SpaceResp]: Spaces belonging to the team. Returns an empty list on errors
            or when no spaces are present.

        Examples:
            # Python (async)
            spaces = await team_api.get_spaces("123")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/team/123/space

            # wget
            wget --header="Authorization: pk_..." \
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

    async def create_workspace(self, workspace_create: WorkspaceCreate) -> Optional[WorkspaceResp]:
        """
        Create a new workspace (team).

        API:
            POST /team
            Docs: https://developer.clickup.com/reference/createteam

        Args:
            workspace_create: Workspace creation DTO with name, color, and avatar

        Returns:
            WorkspaceResp: Created workspace details, or None on failure

        Examples:
            # Python (async)
            from clickup_mcp.models.dto.workspace import WorkspaceCreate

            workspace_create = WorkspaceCreate(name="Engineering Team", color="#3498db")
            workspace = await team_api.create_workspace(workspace_create)

            # curl
            curl -X POST -H "Authorization: pk_..." \
                 -H "Content-Type: application/json" \
                 -d '{"name": "Engineering Team", "color": "#3498db"}' \
                 https://api.clickup.com/api/v2/team
        """
        response = await self._client.post("/team", json=workspace_create.to_payload())

        if not response.success or response.status_code != 200:
            logger.error(f"Failed to create workspace: {response.status_code}")
            return None

        if response.data is None or not isinstance(response.data, dict):
            logger.error("Invalid response data for workspace creation")
            return None

        logger.debug(f"Created workspace: {response.data}")
        return WorkspaceResp(**response.data)

    async def get_workspace(self, team_id: ClickUpTeamID) -> Optional[WorkspaceResp]:
        """
        Get a specific workspace by ID.

        API:
            GET /team/{team_id}

        Args:
            team_id: The workspace ID to retrieve

        Returns:
            WorkspaceResp: Workspace details, or None on failure

        Examples:
            # Python (async)
            workspace = await team_api.get_workspace("9018752317")

            # curl
            curl -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/team/9018752317
        """
        response = await self._client.get(f"/team/{team_id}")

        if not response.success or response.status_code != 200:
            logger.error(f"Failed to get workspace: {response.status_code}")
            return None

        if response.data is None or not isinstance(response.data, dict):
            logger.error("Invalid response data for workspace retrieval")
            return None

        logger.debug(f"Retrieved workspace: {response.data}")
        return WorkspaceResp(**response.data)

    async def update_workspace(self, team_id: ClickUpTeamID, workspace_update: WorkspaceUpdate) -> Optional[WorkspaceResp]:
        """
        Update an existing workspace.

        API:
            PUT /team/{team_id}

        Args:
            team_id: The workspace ID to update
            workspace_update: Workspace update DTO with fields to update

        Returns:
            WorkspaceResp: Updated workspace details, or None on failure

        Examples:
            # Python (async)
            from clickup_mcp.models.dto.workspace import WorkspaceUpdate

            workspace_update = WorkspaceUpdate(name="Updated Team Name")
            workspace = await team_api.update_workspace("9018752317", workspace_update)

            # curl
            curl -X PUT -H "Authorization: pk_..." \
                 -H "Content-Type: application/json" \
                 -d '{"name": "Updated Team Name"}' \
                 https://api.clickup.com/api/v2/team/9018752317
        """
        response = await self._client.put(f"/team/{team_id}", json=workspace_update.to_payload())

        if not response.success or response.status_code != 200:
            logger.error(f"Failed to update workspace: {response.status_code}")
            return None

        if response.data is None or not isinstance(response.data, dict):
            logger.error("Invalid response data for workspace update")
            return None

        logger.debug(f"Updated workspace: {response.data}")
        return WorkspaceResp(**response.data)

    async def delete_workspace(self, team_id: ClickUpTeamID) -> bool:
        """
        Delete a workspace.

        API:
            DELETE /team/{team_id}

        Args:
            team_id: The workspace ID to delete

        Returns:
            bool: True if deletion was successful, False otherwise

        Examples:
            # Python (async)
            success = await team_api.delete_workspace("9018752317")

            # curl
            curl -X DELETE -H "Authorization: pk_..." \
                 https://api.clickup.com/api/v2/team/9018752317
        """
        response = await self._client.delete(f"/team/{team_id}")

        if not response.success or response.status_code != 200:
            logger.error(f"Failed to delete workspace: {response.status_code}")
            return False

        logger.debug(f"Deleted workspace: {team_id}")
        return True
