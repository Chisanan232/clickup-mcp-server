import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from clickup_mcp.mcp_server.folder import folder_create, folder_get, folder_update, folder_delete, folder_list_in_space
from clickup_mcp.mcp_server.models.inputs.folder import (
    FolderCreateInput,
    FolderGetInput,
    FolderUpdateInput,
    FolderDeleteInput,
    FolderListInSpaceInput,
)
from clickup_mcp.mcp_server.models.outputs.folder import FolderResult, FolderListResult
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult


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

    c = await folder_create(FolderCreateInput(space_id="s1", name="Planning"))
    assert isinstance(c, FolderResult) and c.id == "f1"

    g = await folder_get(FolderGetInput(folder_id="f1"))
    assert isinstance(g, FolderResult) and g.name == "Planning"

    u = await folder_update(FolderUpdateInput(folder_id="f1", name="Plan 2"))
    assert isinstance(u, FolderResult) and u.name == "Plan 2"

    d = await folder_delete(FolderDeleteInput(folder_id="f1"))
    assert isinstance(d, DeletionResult) and d.deleted is True

    l = await folder_list_in_space(FolderListInSpaceInput(space_id="s1"))
    assert isinstance(l, FolderListResult)
    assert [i.id for i in l.items] == ["f1", "f1"]
