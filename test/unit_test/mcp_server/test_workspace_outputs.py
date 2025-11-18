from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.models.outputs.workspace import (
    WorkspaceListItem,
    WorkspaceListResult,
)
from clickup_mcp.mcp_server.workspace import workspace_list


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_list_returns_result_models(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    # Fake team objects with attributes team_id and name
    team1 = type("Team", (), {"team_id": "t1", "name": "Eng"})()
    team2 = type("Team", (), {"team_id": "t2", "name": "Ops"})()
    mock_client.team.get_authorized_teams = AsyncMock(return_value=[team1, team2])
    mock_get_client.return_value = mock_client

    envelope = await workspace_list()
    assert envelope.ok is True
    assert isinstance(envelope.result, WorkspaceListResult)
    assert len(envelope.result.items) == 2
    assert envelope.result.items[0] == WorkspaceListItem(team_id="t1", name="Eng")
    assert envelope.result.items[1] == WorkspaceListItem(team_id="t2", name="Ops")
