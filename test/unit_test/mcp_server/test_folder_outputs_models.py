from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from clickup_mcp.mcp_server.errors import IssueCode

from clickup_mcp.mcp_server.folder import (
    folder_create,
    folder_delete,
    folder_get,
    folder_list_in_space,
    folder_update,
)
from clickup_mcp.mcp_server.models.inputs.folder import (
    FolderCreateInput,
    FolderDeleteInput,
    FolderGetInput,
    FolderListInSpaceInput,
    FolderUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult
from clickup_mcp.mcp_server.models.outputs.folder import FolderListResult, FolderResult


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.folder.ClickUpAPIClientFactory.get")
async def test_folder_crud_and_list_return_result_models(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    created = type(
        "FolderDTO",
        (),
        {
            "id": "f1",
            "name": "Planning",
            "space": type("S", (), {"id": "s1"})(),
            "override_statuses": False,
            "hidden": False,
        },
    )()
    got = created
    updated = type(
        "FolderDTO",
        (),
        {
            "id": "f1",
            "name": "Plan 2",
            "space": type("S", (), {"id": "s1"})(),
            "override_statuses": False,
            "hidden": False,
        },
    )()
    mock_client.folder.create = AsyncMock(return_value=created)
    mock_client.folder.get = AsyncMock(return_value=got)
    mock_client.folder.update = AsyncMock(return_value=updated)
    mock_client.folder.delete = AsyncMock(return_value=True)
    mock_client.folder.get_all = AsyncMock(return_value=[created, updated])
    mock_get_client.return_value = mock_client

    c_env = await folder_create(FolderCreateInput(space_id="s1", name="Planning"))
    assert c_env.ok is True and isinstance(c_env.result, FolderResult) and c_env.result.id == "f1"

    g_env = await folder_get(FolderGetInput(folder_id="f1"))
    assert g_env.ok is True and isinstance(g_env.result, FolderResult) and g_env.result.name == "Planning"

    u_env = await folder_update(FolderUpdateInput(folder_id="f1", name="Plan 2"))
    assert u_env.ok is True and isinstance(u_env.result, FolderResult) and u_env.result.name == "Plan 2"

    d_env = await folder_delete(FolderDeleteInput(folder_id="f1"))
    assert d_env.ok is True and isinstance(d_env.result, DeletionResult) and d_env.result.deleted is True

    l_env = await folder_list_in_space(FolderListInSpaceInput(space_id="s1"))
    assert l_env.ok is True and isinstance(l_env.result, FolderListResult)
    assert [i.id for i in l_env.result.items] == ["f1", "f1"]


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.folder.ClickUpAPIClientFactory.get")
async def test_folder_create_empty_response_maps_to_internal(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.folder.create = AsyncMock(return_value=None)
    mock_get_client.return_value = mock_client

    env = await folder_create(FolderCreateInput(space_id="s1", name="X"))
    assert env.ok is False
    assert env.issues and env.issues[0].code == IssueCode.INTERNAL


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.folder.ClickUpAPIClientFactory.get")
async def test_folder_get_empty_response_maps_to_not_found(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.folder.get = AsyncMock(return_value=None)
    mock_get_client.return_value = mock_client

    env = await folder_get(FolderGetInput(folder_id="f-missing"))
    assert env.ok is False
    assert env.issues and env.issues[0].code == IssueCode.NOT_FOUND


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.folder.ClickUpAPIClientFactory.get")
async def test_folder_update_empty_response_maps_to_not_found(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.folder.update = AsyncMock(return_value=None)
    mock_get_client.return_value = mock_client

    env = await folder_update(FolderUpdateInput(folder_id="f-missing", name="New"))
    assert env.ok is False
    assert env.issues and env.issues[0].code == IssueCode.NOT_FOUND
