"""Team Domain  MCP Output mappers.

Translate between Team domain entities and Workspace MCP output models.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List

from clickup_mcp.models.domain.team import ClickUpTeam

if TYPE_CHECKING:
    from clickup_mcp.mcp_server.models.outputs.workspace import (
        WorkspaceListItem,
        WorkspaceListResult,
    )


class TeamMapper:
    """Static helpers to convert Team domain entities to MCP outputs."""

    @staticmethod
    def to_workspace_list_item_output(team: ClickUpTeam) -> "WorkspaceListItem":
        from clickup_mcp.mcp_server.models.outputs.workspace import WorkspaceListItem

        team_id_val = team.team_id or team.id or ""
        name_val = team.name or ""
        return WorkspaceListItem(team_id=str(team_id_val), name=name_val)

    @staticmethod
    def to_workspace_list_result_output(teams: Iterable[ClickUpTeam]) -> "WorkspaceListResult":
        from clickup_mcp.mcp_server.models.outputs.workspace import (
            WorkspaceListItem,
            WorkspaceListResult,
        )

        items: List[WorkspaceListItem] = [TeamMapper.to_workspace_list_item_output(t) for t in teams]
        return WorkspaceListResult(items=items)
