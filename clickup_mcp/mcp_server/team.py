"""
MCP functions for ClickUp Teams.

This module provides MCP functions for interacting with ClickUp Teams/Workspaces.
These functions follow the FastMCP pattern for easy integration into MCP servers.
"""

from typing import List

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.outputs.workspace import (
    WorkspaceListItem,
    WorkspaceListResult,
)

from .app import mcp


@mcp.tool(
    name="get_authorized_teams",
    title="Get ClickUp Teams",
    description="Retrieve all teams/workspaces that the authenticated user has access to.",
)
@handle_tool_errors
async def get_authorized_teams() -> WorkspaceListResult:
    """
    Get all teams/workspaces available to the authenticated user.

    This function retrieves all teams/workspaces from ClickUp that the authenticated user
    has access to. It returns a list of team domain models with full details including
    team members if available.

    Returns:
        A list of ClickUpTeam domain models as dictionaries. Returns an empty list
        if no teams are found.

    Raises:
        ValueError: If the API token is not found or if there's an error retrieving teams.
    """
    client = ClickUpAPIClientFactory.get()

    # Get the teams using the client
    async with client:
        teams = await client.team.get_authorized_teams()
    # Map domain models to MCP output model
    items: List[WorkspaceListItem] = []
    for team in teams:
        team_id_val = team.team_id or team.id or ""
        name_val = team.name or ""
        items.append(WorkspaceListItem(team_id=str(team_id_val), name=name_val))
    return WorkspaceListResult(items=items)
