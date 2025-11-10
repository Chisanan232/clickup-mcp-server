"""
Unit tests for Task API.
"""

from test.unit_test._base import BaseAPIClientTestSuite
from unittest.mock import AsyncMock, Mock

import pytest

from clickup_mcp.api.task import TaskAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.dto.task import TaskCreate, TaskListQuery, TaskResp, TaskUpdate


class TestTaskAPI(BaseAPIClientTestSuite):
    """Test cases for TaskAPI."""

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
    def task_api(self, mock_api_client):
        """Create a TaskAPI instance with a mock client."""
        return TaskAPI(mock_api_client)

    @pytest.fixture
    def sample_task_data(self):
        """Return sample task data."""
        return {
            "id": "task_123",
            "name": "Test Task",
            "description": "Test Description",
            "status": {"id": "status_1", "status": "Open"},
            "priority": {"id": "priority_1", "priority": "High"},
            "assignees": [{"id": 1, "username": "user1"}],
            "due_date": 1234567890000,
            "time_estimate": 3600000,
            "custom_fields": [],
            "tags": [],
            "watchers": [],
            "checklists": [],
        }

    @pytest.mark.asyncio
    async def test_create_task(self, task_api, mock_api_client, sample_task_data):
        """Test creating a new task."""
        # Arrange
        list_id = "list_123"
        task_create = TaskCreate(name="Test Task", description="Test Description")
        mock_api_client.post.return_value = APIResponse(
            success=True, status_code=200, data=sample_task_data, headers={}
        )

        # Act
        result = await task_api.create(list_id, task_create)

        # Assert
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == f"/list/{list_id}/task"
        assert isinstance(result, TaskResp)
        assert result.id == "task_123"

    @pytest.mark.asyncio
    async def test_create_task_with_custom_fields(self, task_api, mock_api_client, sample_task_data):
        """Test creating a task with custom fields."""
        # Arrange
        list_id = "list_123"
        custom_fields = [{"id": "field_1", "value": "custom_value"}]
        task_create = TaskCreate(name="Test Task", custom_fields=custom_fields)
        mock_api_client.post.return_value = APIResponse(
            success=True, status_code=200, data=sample_task_data, headers={}
        )

        # Act
        result = await task_api.create(list_id, task_create)

        # Assert
        assert isinstance(result, TaskResp)

    @pytest.mark.asyncio
    async def test_get_task(self, task_api, mock_api_client, sample_task_data):
        """Test getting a task by ID."""
        # Arrange
        task_id = "task_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_task_data, headers={}
        )

        # Act
        result = await task_api.get(task_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/task/{task_id}", params=None)
        assert isinstance(result, TaskResp)
        assert result.id == "task_123"

    @pytest.mark.asyncio
    async def test_get_task_with_subtasks(self, task_api, mock_api_client, sample_task_data):
        """Test getting a task with subtasks."""
        # Arrange
        task_id = "task_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_task_data, headers={}
        )

        # Act
        result = await task_api.get(task_id, subtasks=True)

        # Assert
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["subtasks"] == "true"

    @pytest.mark.asyncio
    async def test_get_task_with_custom_task_ids(self, task_api, mock_api_client, sample_task_data):
        """Test getting a task using custom task IDs."""
        # Arrange
        task_id = "custom_task_id"
        team_id = "team_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_task_data, headers={}
        )

        # Act
        result = await task_api.get(task_id, custom_task_ids=True, team_id=team_id)

        # Assert
        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["custom_task_ids"] == "true"
        assert call_args[1]["params"]["team_id"] == team_id

    @pytest.mark.asyncio
    async def test_get_task_returns_none_on_404(self, task_api, mock_api_client):
        """Test getting a task that doesn't exist returns None."""
        # Arrange
        task_id = "nonexistent"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Task not found"}, headers={}
        )

        # Act
        result = await task_api.get(task_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_in_list(self, task_api, mock_api_client, sample_task_data):
        """Test listing tasks in a list with pagination."""
        # Arrange
        list_id = "list_123"
        query = TaskListQuery(page=0, limit=100, include_timl=True)
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data={"tasks": [sample_task_data]}, headers={}
        )

        # Act
        result = await task_api.list_in_list(list_id, query)

        # Assert
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == f"/list/{list_id}/task"
        assert call_args[1]["params"]["include_timl"] == "true"
        assert len(result) == 1
        assert isinstance(result[0], TaskResp)

    @pytest.mark.asyncio
    async def test_list_in_list_with_filters(self, task_api, mock_api_client, sample_task_data):
        """Test listing tasks with status and assignee filters."""
        # Arrange
        list_id = "list_123"
        query = TaskListQuery(page=0, limit=50, statuses=["Open"], assignees=[1])
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data={"tasks": [sample_task_data]}, headers={}
        )

        # Act
        result = await task_api.list_in_list(list_id, query)

        # Assert
        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["statuses"] == ["Open"]
        assert call_args[1]["params"]["assignees"] == [1]
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_in_list_pagination(self, task_api, mock_api_client, sample_task_data):
        """Test listing tasks with pagination."""
        # Arrange
        list_id = "list_123"
        query = TaskListQuery(page=0, limit=1)
        # First page returns 1 task, second page returns empty
        mock_api_client.get.side_effect = [
            APIResponse(success=True, status_code=200, data={"tasks": [sample_task_data]}, headers={}),
            APIResponse(success=True, status_code=200, data={"tasks": []}, headers={}),
        ]

        # Act
        result = await task_api.list_in_list(list_id, query)

        # Assert
        assert len(result) == 1
        assert mock_api_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_update_task(self, task_api, mock_api_client, sample_task_data):
        """Test updating a task."""
        # Arrange
        task_id = "task_123"
        task_update = TaskUpdate(name="Updated Task", status="In Progress")
        updated_data = sample_task_data.copy()
        updated_data["name"] = "Updated Task"
        mock_api_client.put.return_value = APIResponse(
            success=True, status_code=200, data=updated_data, headers={}
        )

        # Act
        result = await task_api.update(task_id, task_update)

        # Assert
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == f"/task/{task_id}"
        assert isinstance(result, TaskResp)

    @pytest.mark.asyncio
    async def test_set_custom_field(self, task_api, mock_api_client):
        """Test setting a custom field value."""
        # Arrange
        task_id = "task_123"
        field_id = "field_1"
        value = "custom_value"
        mock_api_client.post.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await task_api.set_custom_field(task_id, field_id, value)

        # Assert
        mock_api_client.post.assert_called_once_with(
            f"/task/{task_id}/field/{field_id}", data={"value": "custom_value"}
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_set_custom_field_with_complex_value(self, task_api, mock_api_client):
        """Test setting a custom field with complex value."""
        # Arrange
        task_id = "task_123"
        field_id = "field_1"
        value = {"option": "value1"}
        mock_api_client.post.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await task_api.set_custom_field(task_id, field_id, value)

        # Assert
        call_args = mock_api_client.post.call_args
        assert call_args[1]["data"]["value"] == {"option": "value1"}
        assert result is True

    @pytest.mark.asyncio
    async def test_clear_custom_field(self, task_api, mock_api_client):
        """Test clearing a custom field value."""
        # Arrange
        task_id = "task_123"
        field_id = "field_1"
        mock_api_client.delete.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await task_api.clear_custom_field(task_id, field_id)

        # Assert
        mock_api_client.delete.assert_called_once_with(f"/task/{task_id}/field/{field_id}")
        assert result is True

    @pytest.mark.asyncio
    async def test_add_dependency(self, task_api, mock_api_client):
        """Test adding a dependency to a task."""
        # Arrange
        task_id = "task_123"
        depends_on = "task_456"
        mock_api_client.post.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await task_api.add_dependency(task_id, depends_on)

        # Assert
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == f"/task/{task_id}/dependency"
        assert call_args[1]["data"]["depends_on"] == "task_456"
        assert call_args[1]["data"]["dependency_type"] == "waiting_on"
        assert result is True

    @pytest.mark.asyncio
    async def test_add_dependency_with_custom_type(self, task_api, mock_api_client):
        """Test adding a dependency with custom type."""
        # Arrange
        task_id = "task_123"
        depends_on = "task_456"
        mock_api_client.post.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await task_api.add_dependency(task_id, depends_on, dependency_type="blocking")

        # Assert
        call_args = mock_api_client.post.call_args
        assert call_args[1]["data"]["dependency_type"] == "blocking"
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_task(self, task_api, mock_api_client):
        """Test deleting a task."""
        # Arrange
        task_id = "task_123"
        mock_api_client.delete.return_value = APIResponse(success=True, status_code=204, data=None, headers={})

        # Act
        result = await task_api.delete(task_id)

        # Assert
        mock_api_client.delete.assert_called_once_with(f"/task/{task_id}")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_task_returns_false_on_failure(self, task_api, mock_api_client):
        """Test deleting a task that fails returns False."""
        # Arrange
        task_id = "task_123"
        mock_api_client.delete.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Task not found"}, headers={}
        )

        # Act
        result = await task_api.delete(task_id)

        # Assert
        assert result is False
