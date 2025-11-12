from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.list import (
    list_add_task,
    list_create,
    list_delete,
    list_get,
    list_list_in_folder,
    list_list_in_space_folderless,
    list_remove_task,
    list_update,
)
from clickup_mcp.mcp_server.models.inputs.list_ import (
    ListAddTaskInput,
    ListCreateInput,
    ListDeleteInput,
    ListGetInput,
    ListListInFolderInput,
    ListListInSpaceFolderlessInput,
    ListRemoveTaskInput,
    ListUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult, OperationResult
from clickup_mcp.mcp_server.models.outputs.list import ListListResult, ListResult


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.list.ClickUpAPIClientFactory.get")
async def test_list_crud_and_listing_return_result_models(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    # DTO-like responses with attributes used by mapper
    folder_ref = type("FolderRef", (), {"id": "f1"})()
    space_ref = type("SpaceRef", (), {"id": "s1"})()
    user_ref = type("UserRef", (), {"id": 123})()
    created = type(
        "ListDTO",
        (),
        {
            "id": "L1",
            "name": "Sprint 12",
            "status": "Open",
            "folder": folder_ref,
            "space": space_ref,
            "assignee": user_ref,
            "content": None,
            "priority": None,
            "due_date": None,
            "due_date_time": None,
        },
    )()
    got = created
    updated = type(
        "ListDTO",
        (),
        {
            "id": "L1",
            "name": "Sprint 13",
            "status": "Open",
            "folder": folder_ref,
            "space": space_ref,
            "assignee": user_ref,
            "content": None,
            "priority": None,
            "due_date": None,
            "due_date_time": None,
        },
    )()

    mock_client.list.create = AsyncMock(return_value=created)
    mock_client.list.get = AsyncMock(return_value=got)
    mock_client.list.update = AsyncMock(return_value=updated)
    mock_client.list.delete = AsyncMock(return_value=True)
    mock_client.list.get_all_in_folder = AsyncMock(return_value=[created])
    mock_client.list.get_all_folderless = AsyncMock(return_value=[created])
    mock_client.list.add_task = AsyncMock(return_value=True)
    mock_client.list.remove_task = AsyncMock(return_value=True)

    mock_get_client.return_value = mock_client

    c = await list_create(ListCreateInput(folder_id="f1", name="Sprint 12"))
    assert isinstance(c, ListResult) and c.id == "L1"

    g = await list_get(ListGetInput(list_id="L1"))
    assert isinstance(g, ListResult) and g.name == "Sprint 12"

    u = await list_update(ListUpdateInput(list_id="L1", name="Sprint 13"))
    assert isinstance(u, ListResult) and u.name == "Sprint 13"

    d = await list_delete(ListDeleteInput(list_id="L1"))
    assert isinstance(d, DeletionResult) and d.deleted is True

    lf = await list_list_in_folder(ListListInFolderInput(folder_id="f1"))
    assert isinstance(lf, ListListResult) and [i.id for i in lf.items] == ["L1"]

    ls = await list_list_in_space_folderless(ListListInSpaceFolderlessInput(space_id="s1"))
    assert isinstance(ls, ListListResult) and [i.id for i in ls.items] == ["L1"]

    add = await list_add_task(ListAddTaskInput(list_id="L1", task_id="t1"))
    assert isinstance(add, OperationResult) and add.ok is True
    rem = await list_remove_task(ListRemoveTaskInput(list_id="L1", task_id="t1"))
    assert isinstance(rem, OperationResult) and rem.ok is True
