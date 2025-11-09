"""
Unit tests for SpaceAPI CRUD operations, including edge cases.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from clickup_mcp.api.space import SpaceAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.dto.space import SpaceCreate, SpaceResp, SpaceUpdate


@pytest.fixture
def mock_api_client() -> ClickUpAPIClient:
    client = Mock(spec=ClickUpAPIClient)
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client  # type: ignore[return-value]


@pytest.fixture
def space_api(mock_api_client: ClickUpAPIClient) -> SpaceAPI:
    return SpaceAPI(mock_api_client)


@pytest.fixture
def sample_space_data() -> dict:
    return {
        "id": "123456",
        "name": "Test Space",
        "private": False,
        "statuses": [
            {"id": "1", "status": "Open", "color": "#ff0000"},
            {"id": "2", "status": "Closed", "color": "#00ff00"},
        ],
        "multiple_assignees": True,
        "features": {"due_dates": {"enabled": True}, "time_tracking": {"enabled": False}},
        "team_id": "999",
    }


# create
@pytest.mark.asyncio
async def test_create_space_success_200(
    space_api: SpaceAPI, mock_api_client: ClickUpAPIClient, sample_space_data: dict
):
    mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data=sample_space_data, headers={})
    dto = SpaceCreate(name="Test Space", multiple_assignees=True)

    result = await space_api.create("team-1", dto)

    mock_api_client.post.assert_called_once()
    assert isinstance(result, SpaceResp)
    assert result.id == sample_space_data["id"]


@pytest.mark.asyncio
async def test_create_space_success_201(
    space_api: SpaceAPI, mock_api_client: ClickUpAPIClient, sample_space_data: dict
):
    mock_api_client.post.return_value = APIResponse(success=True, status_code=201, data=sample_space_data, headers={})
    dto = SpaceCreate(name="Created", multiple_assignees=False)

    result = await space_api.create("team-1", dto)

    assert isinstance(result, SpaceResp)


@pytest.mark.asyncio
async def test_create_space_failure_status(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.post.return_value = APIResponse(success=False, status_code=400, data={"err": "bad"}, headers={})
    dto = SpaceCreate(name="x", multiple_assignees=False)

    result = await space_api.create("team-1", dto)

    assert result is None


@pytest.mark.asyncio
async def test_create_space_malformed_data_none(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    dto = SpaceCreate(name="x", multiple_assignees=False)

    result = await space_api.create("team-1", dto)

    assert result is None


@pytest.mark.asyncio
async def test_create_space_invalid_dict_raises(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    from pydantic import ValidationError

    # data is a dict (to satisfy APIResponse) but missing required fields for SpaceResp
    mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data={"foo": "bar"}, headers={})
    dto = SpaceCreate(name="x", multiple_assignees=False)

    with pytest.raises(ValidationError):
        await space_api.create("team-1", dto)


# get_all
@pytest.mark.asyncio
async def test_get_all_spaces_success(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient, sample_space_data: dict):
    mock_api_client.get.return_value = APIResponse(
        success=True,
        status_code=200,
        data={"spaces": [sample_space_data, {**sample_space_data, "id": "654321", "name": "Another"}]},
        headers={},
    )

    result = await space_api.get_all("team-1")

    mock_api_client.get.assert_called_once_with("/team/team-1/space")
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(x, SpaceResp) for x in result)


@pytest.mark.asyncio
async def test_get_all_spaces_missing_key(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data={}, headers={})
    result = await space_api.get_all("team-1")
    assert result == []


@pytest.mark.asyncio
async def test_get_all_spaces_spaces_not_list(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    # data is a dict, but "spaces" key is not a list -> should return []
    mock_api_client.get.return_value = APIResponse(
        success=True, status_code=200, data={"spaces": "not-a-list"}, headers={}
    )
    result = await space_api.get_all("team-1")
    assert result == []


@pytest.mark.asyncio
async def test_get_all_spaces_failure(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.get.return_value = APIResponse(success=False, status_code=500, data={"err": "oops"}, headers={})
    result = await space_api.get_all("team-1")
    assert result == []


# get
@pytest.mark.asyncio
async def test_get_space_non_404_error(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.get.return_value = APIResponse(success=False, status_code=500, data={"err": "oops"}, headers={})
    result = await space_api.get("space-1")
    assert result is None


@pytest.mark.asyncio
async def test_get_space_data_none(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.get.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    result = await space_api.get("space-1")
    assert result is None


# update
@pytest.mark.asyncio
async def test_update_space_success(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient, sample_space_data: dict):
    mock_api_client.put.return_value = APIResponse(success=True, status_code=200, data=sample_space_data, headers={})
    dto = SpaceUpdate(name="Updated")

    result = await space_api.update("space-1", dto)

    mock_api_client.put.assert_called_once()
    assert isinstance(result, SpaceResp)


@pytest.mark.asyncio
async def test_update_space_failure(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.put.return_value = APIResponse(success=False, status_code=400, data={"err": "bad"}, headers={})
    dto = SpaceUpdate(name="Updated")

    result = await space_api.update("space-1", dto)

    assert result is None


@pytest.mark.asyncio
async def test_update_space_data_none(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.put.return_value = APIResponse(success=True, status_code=200, data=None, headers={})
    dto = SpaceUpdate(name="Updated")

    result = await space_api.update("space-1", dto)

    assert result is None


# delete
@pytest.mark.asyncio
async def test_delete_space_success_200(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.delete.return_value = APIResponse(success=True, status_code=200, data=None, headers={})

    result = await space_api.delete("space-1")

    mock_api_client.delete.assert_called_once_with("/space/space-1")
    assert result is True


@pytest.mark.asyncio
async def test_delete_space_success_204(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.delete.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

    result = await space_api.delete("space-1")

    assert result is True


@pytest.mark.asyncio
async def test_delete_space_failure(space_api: SpaceAPI, mock_api_client: ClickUpAPIClient):
    mock_api_client.delete.return_value = APIResponse(success=False, status_code=404, data=None, headers={})

    result = await space_api.delete("space-1")

    assert result is False
