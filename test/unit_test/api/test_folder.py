"""
Unit tests for Folder API.
"""

from test.unit_test._base import BaseAPIClientTestSuite
from unittest.mock import AsyncMock, Mock

import pytest

from clickup_mcp.api.folder import FolderAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.dto.folder import FolderCreate, FolderResp, FolderUpdate


class TestFolderAPI(BaseAPIClientTestSuite):
    """Test cases for FolderAPI."""

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
    def folder_api(self, mock_api_client):
        """Create a FolderAPI instance with a mock client."""
        return FolderAPI(mock_api_client)

    @pytest.fixture
    def sample_folder_data(self):
        """Return sample folder data."""
        return {
            "id": "folder_123",
            "name": "Test Folder",
            "orderindex": 1,
            "override_statuses": False,
            "hidden": False,
            "space": {"id": "space_123", "name": "Test Space"},
            "task_count": 5,
            "lists": [],
        }

    @pytest.mark.asyncio
    async def test_create_folder(self, folder_api, mock_api_client, sample_folder_data):
        """Test creating a new folder."""
        # Arrange
        space_id = "space_123"
        folder_create = FolderCreate(name="Test Folder")
        mock_api_client.post.return_value = APIResponse(
            success=True, status_code=200, data=sample_folder_data, headers={}
        )

        # Act
        result = await folder_api.create(space_id, folder_create)

        # Assert
        mock_api_client.post.assert_called_once_with(f"/space/{space_id}/folder", data={"name": "Test Folder"})
        assert isinstance(result, FolderResp)
        assert result.id == "folder_123"
        assert result.name == "Test Folder"

    @pytest.mark.asyncio
    async def test_create_folder_returns_none_on_failure(self, folder_api, mock_api_client):
        """Test creating a folder that fails returns None."""
        # Arrange
        space_id = "space_123"
        folder_create = FolderCreate(name="Test Folder")
        mock_api_client.post.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await folder_api.create(space_id, folder_create)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_folders(self, folder_api, mock_api_client, sample_folder_data):
        """Test getting all folders in a space."""
        # Arrange
        space_id = "space_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data={"folders": [sample_folder_data]}, headers={}
        )

        # Act
        result = await folder_api.get_all(space_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/space/{space_id}/folder")
        assert len(result) == 1
        assert isinstance(result[0], FolderResp)
        assert result[0].id == "folder_123"

    @pytest.mark.asyncio
    async def test_get_all_folders_returns_empty_list_on_failure(self, folder_api, mock_api_client):
        """Test getting folders that fails returns empty list."""
        # Arrange
        space_id = "space_123"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await folder_api.get_all(space_id)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_folder(self, folder_api, mock_api_client, sample_folder_data):
        """Test getting a folder by ID."""
        # Arrange
        folder_id = "folder_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_folder_data, headers={}
        )

        # Act
        result = await folder_api.get(folder_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/folder/{folder_id}")
        assert isinstance(result, FolderResp)
        assert result.id == "folder_123"
        assert result.name == "Test Folder"

    @pytest.mark.asyncio
    async def test_get_folder_returns_none_on_404(self, folder_api, mock_api_client):
        """Test getting a folder that doesn't exist returns None."""
        # Arrange
        folder_id = "nonexistent"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Folder not found"}, headers={}
        )

        # Act
        result = await folder_api.get(folder_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_folder(self, folder_api, mock_api_client, sample_folder_data):
        """Test updating a folder."""
        # Arrange
        folder_id = "folder_123"
        folder_update = FolderUpdate(name="Updated Folder")
        updated_data = sample_folder_data.copy()
        updated_data["name"] = "Updated Folder"
        mock_api_client.put.return_value = APIResponse(
            success=True, status_code=200, data=updated_data, headers={}
        )

        # Act
        result = await folder_api.update(folder_id, folder_update)

        # Assert
        mock_api_client.put.assert_called_once_with(f"/folder/{folder_id}", data={"name": "Updated Folder"})
        assert isinstance(result, FolderResp)
        assert result.name == "Updated Folder"

    @pytest.mark.asyncio
    async def test_delete_folder(self, folder_api, mock_api_client):
        """Test deleting a folder."""
        # Arrange
        folder_id = "folder_123"
        mock_api_client.delete.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await folder_api.delete(folder_id)

        # Assert
        mock_api_client.delete.assert_called_once_with(f"/folder/{folder_id}")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_folder_returns_false_on_failure(self, folder_api, mock_api_client):
        """Test deleting a folder that fails returns False."""
        # Arrange
        folder_id = "folder_123"
        mock_api_client.delete.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Folder not found"}, headers={}
        )

        # Act
        result = await folder_api.delete(folder_id)

        # Assert
        assert result is False
