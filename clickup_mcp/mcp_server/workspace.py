"""MCP tools for ClickUp Workspaces (a.k.a Teams in v2).

Tool: workspace.list -> List workspaces available to the token.
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.outputs.workspace import (
    WorkspaceListResult,
)
from clickup_mcp.models.mapping.team_mapper import TeamMapper

from .app import mcp


@mcp.tool(
    name="workspace.list",
    description=(
        "List workspaces (teams) the token can access. Use this first to discover team IDs, then call "
        "`space.list` to enumerate spaces. HTTP: GET /team. Returns { workspaces: [{ team_id, name }] }."
    ),
)
@handle_tool_errors
async def workspace_list() -> WorkspaceListResult:
    """List workspaces (teams). HTTP: GET /team"""
    client = ClickUpAPIClientFactory.get()
    async with client:
        teams = await client.team.get_authorized_teams()
    return TeamMapper.to_workspace_list_result_output(teams)
