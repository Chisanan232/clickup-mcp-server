"""
Additional edge case unit tests for TaskAPI.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from clickup_mcp.api.task import TaskAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.dto.task import TaskCreate, TaskListQuery, TaskUpdate


@pytest.fixture
def mock_api_client() -> Mock:
    client = Mock(spec=ClickUpAPIClient)
    client.post = AsyncMock()
    client.get = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def task_api(mock_api_client: Mock) -> TaskAPI:
    return TaskAPI(mock_api_client)


@pytest.fixture
def sample_task_data() -> dict:
    return {
        "id": "task_1",
        "name": "T1",
        "description": "D",
        "status": {"id": "st1", "status": "open"},
        "priority": {"id": "p1", "priority": "high"},
        "assignees": [],
        "custom_fields": [],
        "tags": [],
        "watchers": [],
        "checklists": [],
    }


# create
@pytest.mark.asyncio
async def test_create_task_failure_status(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.post.return_value = APIResponse(success=False, status_code=400, data={"err": "bad"}, headers={})
    dto = TaskCreate(name="T1")

    result = await task_api.create("list-1", dto)

    assert result is None


@pytest.mark.asyncio
async def test_create_task_data_none(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    dto = TaskCreate(name="T1")

    result = await task_api.create("list-1", dto)

    assert result is None


@pytest.mark.asyncio
async def test_create_task_invalid_dict_raises(task_api: TaskAPI, mock_api_client: Mock):
    # Some environments may raise ValidationError, others may raise TypeError from pydantic internals.
    mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data={"x": 1}, headers={})
    dto = TaskCreate(name="T1")

    with pytest.raises(Exception):
        await task_api.create("list-1", dto)


# get
@pytest.mark.asyncio
async def test_get_task_non_404_failure(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=False, status_code=500, data={"err": "oops"}, headers={})
    result = await task_api.get("task-1")
    assert result is None


@pytest.mark.asyncio
async def test_get_task_data_none(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    result = await task_api.get("task-1")
    assert result is None


@pytest.mark.asyncio
async def test_get_task_custom_ids_without_team(task_api: TaskAPI, mock_api_client: Mock, sample_task_data: dict):
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data=sample_task_data, headers={})
    await task_api.get("CT-1", custom_task_ids=True)
    # should include custom_task_ids param but not team_id
    call_args = mock_api_client.get.call_args
    assert call_args[1]["params"]["custom_task_ids"] == "true"
    assert "team_id" not in call_args[1]["params"]


# list_in_list
@pytest.mark.asyncio
async def test_list_in_list_failure_breaks(task_api: TaskAPI, mock_api_client: Mock):
    query = TaskListQuery()
    mock_api_client.get.return_value = APIResponse(success=False, status_code=500, data=None, headers={})
    result = await task_api.list_in_list("list-1", query)
    assert result == []


@pytest.mark.asyncio
async def test_list_in_list_data_none_breaks(task_api: TaskAPI, mock_api_client: Mock):
    query = TaskListQuery()
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    result = await task_api.list_in_list("list-1", query)
    assert result == []


@pytest.mark.asyncio
async def test_list_in_list_tasks_not_list_breaks(task_api: TaskAPI, mock_api_client: Mock):
    query = TaskListQuery()
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data={"tasks": {}}, headers={})
    result = await task_api.list_in_list("list-1", query)
    assert result == []


# update
@pytest.mark.asyncio
async def test_update_task_failure_returns_none(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.put.return_value = APIResponse(success=False, status_code=400, data={"err": "bad"}, headers={})
    dto = TaskUpdate(name="U")
    result = await task_api.update("task-1", dto)
    assert result is None


@pytest.mark.asyncio
async def test_update_task_data_none_returns_none(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.put.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    dto = TaskUpdate(name="U")
    result = await task_api.update("task-1", dto)
    assert result is None


# custom fields
@pytest.mark.asyncio
async def test_set_custom_field_failure_returns_false(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.post.return_value = APIResponse(success=False, status_code=400, data=None, headers={})
    result = await task_api.set_custom_field("task-1", "field-1", 123)
    assert result is False


@pytest.mark.asyncio
async def test_clear_custom_field_failure_returns_false(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.delete.return_value = APIResponse(success=False, status_code=400, data=None, headers={})
    result = await task_api.clear_custom_field("task-1", "field-1")
    assert result is False


# dependency
@pytest.mark.asyncio
async def test_add_dependency_failure_returns_false(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.post.return_value = APIResponse(success=False, status_code=400, data=None, headers={})
    result = await task_api.add_dependency("task-1", "task-2")
    assert result is False


# delete
@pytest.mark.asyncio
async def test_delete_task_success_200(task_api: TaskAPI, mock_api_client: Mock):
    mock_api_client.delete.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    result = await task_api.delete("task-1")
    assert result is True
