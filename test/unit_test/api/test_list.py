"""
Unit tests for List API.
"""

from test.unit_test._base import BaseAPIClientTestSuite
from unittest.mock import AsyncMock, Mock

import pytest

from clickup_mcp.api.list import ListAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.dto.list import ListCreate, ListResp, ListUpdate


class TestListAPI(BaseAPIClientTestSuite):
    """Test cases for ListAPI."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        client = Mock(spec=ClickUpAPIClient)
        client.post = AsyncMock()
        client.get = AsyncMock()
        client.put = AsyncMock()
        client.delete = AsyncMock()
        return client

    @pytest.fixture
    def list_api(self, mock_api_client):
        """Create a ListAPI instance with a mock client."""
        return ListAPI(mock_api_client)

    @pytest.fixture
    def sample_list_data(self):
        """Return sample list data."""
        return {
            "id": "list_123",
            "name": "Test List",
            "orderindex": 1,
            "status": "active",
            "priority": 1,
            "task_count": 10,
            "folder": {"id": "folder_123", "name": "Test Folder"},
            "space": {"id": "space_123", "name": "Test Space"},
            "archived": False,
        }

    @pytest.mark.asyncio
    async def test_create_list(self, list_api, mock_api_client, sample_list_data):
        """Test creating a new list."""
        # Arrange
        folder_id = "folder_123"
        list_create = ListCreate(name="Test List")
        mock_api_client.post.return_value = APIResponse(
            success=True, status_code=200, data=sample_list_data, headers={}
        )

        # Act
        result = await list_api.create(folder_id, list_create)

        # Assert
        mock_api_client.post.assert_called_once_with(f"/folder/{folder_id}/list", data={"name": "Test List"})
        assert isinstance(result, ListResp)
        assert result.id == "list_123"
        assert result.name == "Test List"

    @pytest.mark.asyncio
    async def test_get_all_in_folder(self, list_api, mock_api_client, sample_list_data):
        """Test getting all lists in a folder."""
        # Arrange
        folder_id = "folder_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data={"lists": [sample_list_data]}, headers={}
        )

        # Act
        result = await list_api.get_all_in_folder(folder_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/folder/{folder_id}/list")
        assert len(result) == 1
        assert isinstance(result[0], ListResp)
        assert result[0].id == "list_123"

    @pytest.mark.asyncio
    async def test_get_all_folderless(self, list_api, mock_api_client, sample_list_data):
        """Test getting all folderless lists in a space."""
        # Arrange
        space_id = "space_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data={"lists": [sample_list_data]}, headers={}
        )

        # Act
        result = await list_api.get_all_folderless(space_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/space/{space_id}/list")
        assert len(result) == 1
        assert isinstance(result[0], ListResp)

    @pytest.mark.asyncio
    async def test_get_list(self, list_api, mock_api_client, sample_list_data):
        """Test getting a list by ID."""
        # Arrange
        list_id = "list_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_list_data, headers={}
        )

        # Act
        result = await list_api.get(list_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/list/{list_id}")
        assert isinstance(result, ListResp)
        assert result.id == "list_123"

    @pytest.mark.asyncio
    async def test_get_list_returns_none_on_404(self, list_api, mock_api_client):
        """Test getting a list that doesn't exist returns None."""
        # Arrange
        list_id = "nonexistent"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=404, data={"err": "List not found"}, headers={}
        )

        # Act
        result = await list_api.get(list_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_list(self, list_api, mock_api_client, sample_list_data):
        """Test updating a list."""
        # Arrange
        list_id = "list_123"
        list_update = ListUpdate(name="Updated List")
        updated_data = sample_list_data.copy()
        updated_data["name"] = "Updated List"
        mock_api_client.put.return_value = APIResponse(
            success=True, status_code=200, data=updated_data, headers={}
        )

        # Act
        result = await list_api.update(list_id, list_update)

        # Assert
        mock_api_client.put.assert_called_once_with(f"/list/{list_id}", data={"name": "Updated List"})
        assert isinstance(result, ListResp)
        assert result.name == "Updated List"

    @pytest.mark.asyncio
    async def test_delete_list(self, list_api, mock_api_client):
        """Test deleting a list."""
        # Arrange
        list_id = "list_123"
        mock_api_client.delete.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await list_api.delete(list_id)

        # Assert
        mock_api_client.delete.assert_called_once_with(f"/list/{list_id}")
        assert result is True

    @pytest.mark.asyncio
    async def test_add_task_to_list(self, list_api, mock_api_client):
        """Test adding a task to a list (TIML)."""
        # Arrange
        list_id = "list_123"
        task_id = "task_456"
        mock_api_client.post.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await list_api.add_task(list_id, task_id)

        # Assert
        mock_api_client.post.assert_called_once_with(f"/list/{list_id}/task/{task_id}")
        assert result is True

    @pytest.mark.asyncio
    async def test_add_task_to_list_returns_false_on_failure(self, list_api, mock_api_client):
        """Test adding a task that fails returns False."""
        # Arrange
        list_id = "list_123"
        task_id = "task_456"
        mock_api_client.post.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await list_api.add_task(list_id, task_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_remove_task_from_list(self, list_api, mock_api_client):
        """Test removing a task from a list (TIML)."""
        # Arrange
        list_id = "list_123"
        task_id = "task_456"
        mock_api_client.delete.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await list_api.remove_task(list_id, task_id)

        # Assert
        mock_api_client.delete.assert_called_once_with(f"/list/{list_id}/task/{task_id}")
        assert result is True
