from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.models.inputs.space import (
    SpaceCreateInput,
    SpaceDeleteInput,
    SpaceGetInput,
    SpaceListInput,
    SpaceUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.space import SpaceListResult, SpaceResult
from clickup_mcp.mcp_server.space import (
    space_create,
    space_delete,
    space_get,
    space_list,
    space_update,
)


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_space_get_returns_result_model(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    # Fake DTO-like with attributes used by mapper
    dto = type(
        "SpaceDTO",
        (),
        {
            "id": "s1",
            "name": "Engineering",
            "private": False,
            "team_id": "t1",
            "statuses": [],
            "multiple_assignees": False,
            "features": None,
        },
    )()
    mock_client.space.get = AsyncMock(return_value=dto)
    mock_get_client.return_value = mock_client

    envelope = await space_get(SpaceGetInput(space_id="s1"))
    assert envelope.ok is True
    assert isinstance(envelope.result, SpaceResult)
    assert envelope.result.id == "s1" and envelope.result.name == "Engineering" and envelope.result.team_id == "t1"


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_space_list_returns_result_list(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    base = {"private": False, "team_id": "t1", "statuses": [], "multiple_assignees": False, "features": None}
    dto1 = type("SpaceDTO", (), dict({"id": "s1", "name": "Eng"}, **base))()
    dto2 = type("SpaceDTO", (), dict({"id": "s2", "name": "Ops"}, **base))()
    mock_client.team.get_spaces = AsyncMock(return_value=[dto1, dto2])
    mock_get_client.return_value = mock_client

    envelope = await space_list(SpaceListInput(team_id="t1"))
    assert envelope.ok is True
    assert isinstance(envelope.result, SpaceListResult)
    assert [i.id for i in envelope.result.items] == ["s1", "s2"]


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_space_create_update_delete_return_result_models(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    created = type(
        "SpaceDTO",
        (),
        {
            "id": "s1",
            "name": "Eng",
            "private": False,
            "team_id": "t1",
            "statuses": [],
            "multiple_assignees": False,
            "features": None,
        },
    )()
    updated = type(
        "SpaceDTO",
        (),
        {
            "id": "s1",
            "name": "Eng2",
            "private": True,
            "team_id": "t1",
            "statuses": [],
            "multiple_assignees": True,
            "features": None,
        },
    )()
    mock_client.space.create = AsyncMock(return_value=created)
    mock_client.space.update = AsyncMock(return_value=updated)
    mock_client.space.delete = AsyncMock(return_value=True)
    mock_get_client.return_value = mock_client

    c_env = await space_create(SpaceCreateInput(team_id="t1", name="Eng"))
    assert c_env.ok is True and isinstance(c_env.result, SpaceResult)
    u_env = await space_update(SpaceUpdateInput(space_id="s1", name="Eng2", private=True))
    assert u_env.ok is True and isinstance(u_env.result, SpaceResult)
    d_env = await space_delete(SpaceDeleteInput(space_id="s1"))
    assert d_env.ok is True and d_env.result.deleted is True
