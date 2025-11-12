from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.models.inputs.task import (
    TaskAddDependencyInput,
    TaskClearCustomFieldInput,
    TaskCreateInput,
    TaskGetInput,
    TaskListInListInput,
    TaskSetCustomFieldInput,
    TaskUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult, OperationResult
from clickup_mcp.mcp_server.models.outputs.task import TaskListResult, TaskResult
from clickup_mcp.mcp_server.task import (
    task_add_dependency,
    task_clear_custom_field,
    task_create,
    task_delete,
    task_get,
    task_list_in_list,
    task_set_custom_field,
    task_update,
)
from clickup_mcp.models.dto.task import TaskResp


def _fake_task_resp(**overrides: Any) -> TaskResp:
    # Minimal shape used by _taskresp_* mappers in handler
    status_obj = type("Status", (), {"status": overrides.get("status", "open")})()
    priority_obj = type("Prio", (), {"id": str(overrides.get("priority_id", "3"))})()
    list_obj = type("ListRef", (), {"id": overrides.get("list_id", "L1")})()
    user = type("UserRef", (), {"id": 42})()
    base = {
        "id": overrides.get("id", "t1"),
        "name": overrides.get("name", "Test"),
        "status": status_obj,
        "priority": priority_obj,
        "list": list_obj,
        "assignees": overrides.get("assignees", [user]),
        "due_date": overrides.get("due_date", 1731004800000),
        "url": overrides.get("url", "https://app.clickup.com/t/t1"),
        "parent": overrides.get("parent", None),
    }
    return type("TaskResp", (), base)()


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.task.ClickUpAPIClientFactory.get")
async def test_task_create_and_get_return_taskresult(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.task.create = AsyncMock(return_value=_fake_task_resp(id="t1", name="Ship"))
    mock_client.task.get = AsyncMock(return_value=_fake_task_resp(id="t1", name="Ship"))
    mock_get_client.return_value = mock_client

    create_res = await task_create(TaskCreateInput(list_id="L1", name="Ship"))
    assert isinstance(create_res, TaskResult)
    assert create_res.id == "t1" and create_res.name == "Ship"

    get_res = await task_get(TaskGetInput(task_id="t1"))
    assert isinstance(get_res, TaskResult)
    assert get_res.id == "t1"


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.task.ClickUpAPIClientFactory.get")
async def test_task_list_in_list_truncates_and_forwards_timl(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    # Return more than limit to exercise truncation
    tasks = [_fake_task_resp(id=f"t{i}") for i in range(105)]

    async def _list_in_list(list_id, query):
        # Assert include_timl flag is forwarded as set
        assert query.include_timl is True
        assert query.limit <= 100
        return tasks

    mock_client.task.list_in_list = AsyncMock(side_effect=_list_in_list)
    mock_get_client.return_value = mock_client

    res = await task_list_in_list(TaskListInListInput(list_id="L1", limit=50, include_timl=True))
    assert isinstance(res, TaskListResult)
    assert len(res.items) == 50
    assert res.truncated is True
    # We do not fabricate next_cursor in current implementation
    assert res.next_cursor is None


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.task.ClickUpAPIClientFactory.get")
async def test_task_update_and_misc_ops(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.task.update = AsyncMock(return_value=_fake_task_resp(id="t1", name="Edited"))
    mock_client.task.set_custom_field = AsyncMock(return_value=True)
    mock_client.task.clear_custom_field = AsyncMock(return_value=True)
    mock_client.task.add_dependency = AsyncMock(return_value=True)
    mock_client.task.delete = AsyncMock(return_value=True)
    mock_get_client.return_value = mock_client

    upd = await task_update(TaskUpdateInput(task_id="t1", name="Edited"))
    assert isinstance(upd, TaskResult)
    ok = await task_set_custom_field(TaskSetCustomFieldInput(task_id="t1", field_id="f1", value="v"))
    assert isinstance(ok, OperationResult) and ok.ok is True
    ok2 = await task_clear_custom_field(TaskClearCustomFieldInput(task_id="t1", field_id="f1"))
    assert isinstance(ok2, OperationResult) and ok2.ok is True
    ok3 = await task_add_dependency(TaskAddDependencyInput(task_id="t1", depends_on="t2"))
    assert isinstance(ok3, OperationResult) and ok3.ok is True
    delres = await task_delete("t1")
    assert isinstance(delres, DeletionResult) and delres.deleted is True
