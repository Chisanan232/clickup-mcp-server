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
    prio_id = overrides.get("priority_id", "3")
    prio_label = overrides.get("priority_label", None)
    prio_fields = {"id": str(prio_id)}
    if prio_label is not None:
        prio_fields["priority"] = prio_label
    priority_obj = type("Prio", (), prio_fields)()
    list_obj = type("ListRef", (), {"id": overrides.get("list_id", "L1")})()
    folder_obj = overrides.get("folder", None)
    space_obj = overrides.get("space", None)
    user = type("UserRef", (), {"id": 42})()
    base = {
        "id": overrides.get("id", "t1"),
        "name": overrides.get("name", "Test"),
        "status": status_obj,
        "priority": priority_obj,
        "list": list_obj,
        "folder": folder_obj,
        "space": space_obj,
        "assignees": overrides.get("assignees", [user]),
        "due_date": overrides.get("due_date", 1731004800000),
        "time_estimate": overrides.get("time_estimate", None),
        "custom_fields": overrides.get("custom_fields", []),
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

    create_env = await task_create(TaskCreateInput(list_id="L1", name="Ship"))
    assert create_env.ok is True and isinstance(create_env.result, TaskResult)
    assert create_env.result.id == "t1" and create_env.result.name == "Ship"
    # priority_info is populated from default fake resp (id="3" -> NORMAL)
    assert create_env.result.priority == 3
    assert create_env.result.priority_info is not None
    assert create_env.result.priority_info.value == 3
    assert create_env.result.priority_info.label == "NORMAL"

    get_env = await task_get(TaskGetInput(task_id="t1"))
    assert get_env.ok is True and isinstance(get_env.result, TaskResult)
    assert get_env.result.id == "t1"


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

    env = await task_list_in_list(TaskListInListInput(list_id="L1", limit=50, include_timl=True))
    assert env.ok is True and isinstance(env.result, TaskListResult)
    assert len(env.result.items) == 50
    assert env.result.truncated is True
    # We do not fabricate next_cursor in current implementation
    assert env.result.next_cursor is None


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.task.ClickUpAPIClientFactory.get")
async def test_task_get_priority_id_suffix_parsed_and_info_populated(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    # priority comes back as "priority_1"
    mock_client.task.get = AsyncMock(return_value=_fake_task_resp(id="t1", name="Ship", priority_id="priority_1"))
    mock_get_client.return_value = mock_client

    get_env = await task_get(TaskGetInput(task_id="t1"))
    assert get_env.ok is True and isinstance(get_env.result, TaskResult)
    assert get_env.result.priority == 1
    assert get_env.result.priority_info is not None
    assert get_env.result.priority_info.value == 1
    assert get_env.result.priority_info.label == "URGENT"


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.task.ClickUpAPIClientFactory.get")
async def test_create_accepts_priority_label_and_sends_int(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.task.create = AsyncMock(return_value=_fake_task_resp(id="t1", name="Ship", priority_id="2"))
    mock_get_client.return_value = mock_client

    await task_create(TaskCreateInput(list_id="L1", name="Ship", priority="HIGH"))
    # Assert DTO priority is 2 (from label HIGH)
    args, kwargs = mock_client.task.create.call_args
    dto = args[1]
    assert getattr(dto, "priority") == 2


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.task.ClickUpAPIClientFactory.get")
async def test_update_accepts_priority_label_and_sends_int(mock_get_client: MagicMock) -> None:
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.task.update = AsyncMock(return_value=_fake_task_resp(id="t1", name="Edited", priority_id="4"))
    mock_get_client.return_value = mock_client

    await task_update(TaskUpdateInput(task_id="t1", name="Edited", priority="LOW"))
    # Assert DTO priority is 4 (from label LOW)
    args, kwargs = mock_client.task.update.call_args
    dto = args[1]
    assert getattr(dto, "priority") == 4


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

    upd_env = await task_update(TaskUpdateInput(task_id="t1", name="Edited"))
    assert upd_env.ok is True and isinstance(upd_env.result, TaskResult)
    ok_env = await task_set_custom_field(TaskSetCustomFieldInput(task_id="t1", field_id="f1", value="v"))
    assert ok_env.ok is True and isinstance(ok_env.result, OperationResult) and ok_env.result.ok is True
    ok2_env = await task_clear_custom_field(TaskClearCustomFieldInput(task_id="t1", field_id="f1"))
    assert ok2_env.ok is True and isinstance(ok2_env.result, OperationResult) and ok2_env.result.ok is True
    ok3_env = await task_add_dependency(TaskAddDependencyInput(task_id="t1", depends_on="t2"))
    assert ok3_env.ok is True and isinstance(ok3_env.result, OperationResult) and ok3_env.result.ok is True
    del_env = await task_delete("t1")
    assert del_env.ok is True and isinstance(del_env.result, DeletionResult) and del_env.result.deleted is True
