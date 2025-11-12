"""MCP tools for ClickUp Workspaces (a.k.a Teams in v2).

Tool: workspace.list -> List workspaces available to the token.
"""

from typing import Any, Dict, List

from .app import mcp
from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.mcp_server.models.outputs.workspace import (
    WorkspaceListItem,
    WorkspaceListResult,
)


@mcp.tool(
    name="workspace.list",
    description=(
        "List workspaces (teams) the token can access. Use this first to discover team IDs, then call "
        "`space.list` to enumerate spaces. HTTP: GET /team. Returns { workspaces: [{ team_id, name }] }."
    ),
)
async def workspace_list() -> WorkspaceListResult:
    """List workspaces (teams). HTTP: GET /team"""
    client = ClickUpAPIClientFactory.get()
    try:
        async with client:
            teams = await client.team.get_authorized_teams()
        items: List[WorkspaceListItem] = []
        for t in teams:
            items.append(WorkspaceListItem(team_id=str(t.team_id or t.id), name=t.name or ""))
        return WorkspaceListResult(items=items)
    except Exception as e:
        raise ValueError(f"Error listing workspaces: {e}")
