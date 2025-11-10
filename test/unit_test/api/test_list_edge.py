"""
Additional edge case unit tests for ListAPI.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from clickup_mcp.api.list import ListAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.dto.list import ListCreate, ListResp, ListUpdate


@pytest.fixture
def mock_api_client() -> Mock:
    client = Mock(spec=ClickUpAPIClient)
    client.post = AsyncMock()
    client.get = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def list_api(mock_api_client: Mock) -> ListAPI:
    return ListAPI(mock_api_client)


@pytest.fixture
def sample_list_data() -> dict:
    return {
        "id": "list_1",
        "name": "L1",
        "orderindex": 1,
        "status": "active",
        "priority": 1,
        "task_count": 0,
        "folder": {"id": "f1"},
        "space": {"id": "s1"},
        "archived": False,
    }


# create
@pytest.mark.asyncio
async def test_create_list_failure_status(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.post.return_value = APIResponse(success=False, status_code=400, data={"err": "bad"}, headers={})
    dto = ListCreate(name="L1")

    result = await list_api.create("folder-1", dto)

    assert result is None


@pytest.mark.asyncio
async def test_create_list_data_none(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    dto = ListCreate(name="L1")

    result = await list_api.create("folder-1", dto)

    assert result is None


@pytest.mark.asyncio
async def test_create_list_invalid_dict_raises(list_api: ListAPI, mock_api_client: Mock):
    from pydantic import ValidationError

    mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data={"x": 1}, headers={})
    dto = ListCreate(name="L1")

    with pytest.raises(ValidationError):
        await list_api.create("folder-1", dto)


@pytest.mark.asyncio
async def test_create_list_201_treated_as_failure_current_behavior(list_api: ListAPI, mock_api_client: Mock):
    # Document current implementation: only 200 is accepted
    mock_api_client.post.return_value = APIResponse(success=True, status_code=201, data={}, headers={})
    dto = ListCreate(name="L1")

    result = await list_api.create("folder-1", dto)

    assert result is None


# get_all_in_folder
@pytest.mark.asyncio
async def test_get_all_in_folder_failure(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=False, status_code=500, data={"err": "oops"}, headers={})
    result = await list_api.get_all_in_folder("folder-1")
    assert result == []


@pytest.mark.asyncio
async def test_get_all_in_folder_data_none(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    result = await list_api.get_all_in_folder("folder-1")
    assert result == []


@pytest.mark.asyncio
async def test_get_all_in_folder_lists_not_list(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data={"lists": "x"}, headers={})
    result = await list_api.get_all_in_folder("folder-1")
    assert result == []


# get_all_folderless
@pytest.mark.asyncio
async def test_get_all_folderless_failure(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=False, status_code=500, data={"err": "oops"}, headers={})
    result = await list_api.get_all_folderless("space-1")
    assert result == []


@pytest.mark.asyncio
async def test_get_all_folderless_data_none(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    result = await list_api.get_all_folderless("space-1")
    assert result == []


@pytest.mark.asyncio
async def test_get_all_folderless_lists_not_list(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data={"lists": {}}, headers={})
    result = await list_api.get_all_folderless("space-1")
    assert result == []


# get
@pytest.mark.asyncio
async def test_get_list_non_404_failure(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=False, status_code=500, data={"err": "oops"}, headers={})
    result = await list_api.get("list-1")
    assert result is None


@pytest.mark.asyncio
async def test_get_list_data_none(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    result = await list_api.get("list-1")
    assert result is None


# update
@pytest.mark.asyncio
async def test_update_list_failure(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.put.return_value = APIResponse(success=False, status_code=400, data={"err": "bad"}, headers={})
    dto = ListUpdate(name="U")

    result = await list_api.update("list-1", dto)

    assert result is None


@pytest.mark.asyncio
async def test_update_list_data_none(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.put.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    dto = ListUpdate(name="U")

    result = await list_api.update("list-1", dto)

    assert result is None


# delete
@pytest.mark.asyncio
async def test_delete_list_success_200(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.delete.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    result = await list_api.delete("list-1")
    assert result is True


@pytest.mark.asyncio
async def test_delete_list_failure(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.delete.return_value = APIResponse(success=False, status_code=404, data=None, headers={})
    result = await list_api.delete("list-1")
    assert result is False


# TIML operations
@pytest.mark.asyncio
async def test_add_task_200(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    result = await list_api.add_task("list-1", "task-1")
    assert result is True


@pytest.mark.asyncio
async def test_remove_task_failure(list_api: ListAPI, mock_api_client: Mock):
    mock_api_client.delete.return_value = APIResponse(success=False, status_code=400, data=None, headers={})
    result = await list_api.remove_task("list-1", "task-1")
    assert result is False
