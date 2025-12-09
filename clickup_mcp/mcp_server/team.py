"""
MCP functions for ClickUp Teams.

This module provides MCP functions for interacting with ClickUp Teams/Workspaces.
These functions follow the FastMCP pattern for easy integration into MCP servers.
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.outputs.workspace import (
    WorkspaceListResult,
)
from clickup_mcp.models.mapping.team_mapper import TeamMapper

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

    API:
        GET /team

    Returns:
        WorkspaceListResult: Items containing `team_id` and `name` for each workspace.

    Error Handling:
        This function is wrapped by `@handle_tool_errors` and returns a ToolResponse at runtime.
        On failure, `ok=False` with one or more issues (e.g., PERMISSION_DENIED, RATE_LIMIT,
        TRANSIENT). On success, `ok=True` and `result` contains WorkspaceListResult.

    Examples:
        # Python (async)
        response = await get_authorized_teams()
        if response.ok:
            for ws in response.result.items:
                print(ws.team_id, ws.name)
        else:
            for iss in response.issues:
                print(iss.code, iss.message)
    """
    client = ClickUpAPIClientFactory.get()

    # Get the teams using the client
    async with client:
        teams = await client.team.get_authorized_teams()
    # Map domain models to MCP output model via mapper
    return TeamMapper.to_workspace_list_result_output(teams)
