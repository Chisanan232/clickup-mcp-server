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
    title="List Workspaces",
    description=(
        "List workspaces (teams) the token can access. Use this first to discover team IDs, then call "
        "`space.list` to enumerate spaces. HTTP: GET /team. Returns { workspaces: [{ team_id, name }] }."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def workspace_list() -> WorkspaceListResult:
    """
    List workspaces (teams) accessible to the current token.

    API:
        GET /team

    Returns:
        WorkspaceListResult: Items containing `team_id` and `name` for each workspace.

    Error Handling:
        This function is wrapped by `@handle_tool_errors` and returns a ToolResponse at runtime.
        On failure, `ok=False` with one or more issues (with canonical codes like VALIDATION_ERROR,
        RATE_LIMIT, INTERNAL). On success, `ok=True` and `result` contains WorkspaceListResult.

    Examples:
        # Python (async)
        response = await workspace_list()
        if response.ok:
            for ws in response.result.items:
                print(ws.team_id, ws.name)
        else:
            for iss in response.issues:
                print(iss.code, iss.message)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        teams = await client.team.get_authorized_teams()
    return TeamMapper.to_workspace_list_result_output(teams)
