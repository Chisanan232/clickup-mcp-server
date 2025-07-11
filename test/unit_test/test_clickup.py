from unittest.mock import patch

import pytest

from clickup_mcp import ClickUpAPIClient, ClickUpResourceClient, APIResponse

from ._base import BaseAPIClientTestSuite


class TestClickUpResourceClient(BaseAPIClientTestSuite):
    """Test cases for ClickUpResourceClient."""

    @pytest.fixture
    def resource_client(self, api_client: ClickUpAPIClient) -> ClickUpResourceClient:
        """Create a test resource client."""
        return ClickUpResourceClient(api_client)

    @pytest.mark.asyncio
    async def test_get_teams(self, resource_client):
        """Test getting teams."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_teams()
            mock_get.assert_called_once_with("/team")

    @pytest.mark.asyncio
    async def test_get_team(self, resource_client):
        """Test getting a specific team."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_team("123")
            mock_get.assert_called_once_with("/team/123")

    @pytest.mark.asyncio
    async def test_create_space(self, resource_client):
        """Test creating a space."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_space("team123", "Test Space", description="A test space")

            mock_post.assert_called_once_with(
                "/team/team123/space", data={"name": "Test Space", "description": "A test space"}
            )

    @pytest.mark.asyncio
    async def test_get_tasks_with_filters(self, resource_client):
        """Test getting tasks with filters."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_tasks(
                "list123",
                page=1,
                statuses=["open", "in progress"],
                assignees=["user1", "user2"],
                due_date_gt=1609459200000,  # Example timestamp
            )

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/list/list123/task"

            params = call_args[1]["params"]
            assert params["page"] == 1
            assert params["statuses[]"] == ["open", "in progress"]
            assert params["assignees[]"] == ["user1", "user2"]
            assert params["due_date_gt"] == 1609459200000

    @pytest.mark.asyncio
    async def test_create_task_minimal(self, resource_client):
        """Test creating a task with minimal data."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task("list123", "Test Task")

            mock_post.assert_called_once_with(
                "/list/list123/task",
                data={"name": "Test Task", "notify_all": True, "check_required_custom_fields": True},
            )

    @pytest.mark.asyncio
    async def test_create_task_full(self, resource_client):
        """Test creating a task with all optional data."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task(
                "list123",
                "Test Task",
                description="A test task",
                assignees=["user1"],
                tags=["urgent"],
                status="open",
                priority=1,
                due_date=1609459200000,
                time_estimate=3600000,
            )

            expected_data = {
                "name": "Test Task",
                "description": "A test task",
                "assignees": ["user1"],
                "tags": ["urgent"],
                "status": "open",
                "priority": 1,
                "due_date": 1609459200000,
                "due_date_time": False,
                "time_estimate": 3600000,
                "notify_all": True,
                "check_required_custom_fields": True,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    @pytest.mark.asyncio
    async def test_update_task(self, resource_client):
        """Test updating a task."""
        with patch.object(resource_client.client, "put", return_value=APIResponse(status_code=200)) as mock_put:
            await resource_client.update_task("task123", name="Updated Task", status="completed")

            mock_put.assert_called_once_with("/task/task123", data={"name": "Updated Task", "status": "completed"})

    @pytest.mark.asyncio
    async def test_delete_task(self, resource_client):
        """Test deleting a task."""
        with patch.object(resource_client.client, "delete", return_value=APIResponse(status_code=200)) as mock_delete:
            await resource_client.delete_task("task123", team_id="team123")

            mock_delete.assert_called_once_with(
                "/task/task123", params={"custom_task_ids": False, "team_id": "team123"}
            )

    @pytest.mark.asyncio
    async def test_create_list_in_folder(self, resource_client):
        """Test creating a list in a folder."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_list("Test List", folder_id="folder123")

            mock_post.assert_called_once_with("/folder/folder123/list", data={"name": "Test List"})

    @pytest.mark.asyncio
    async def test_create_list_in_space(self, resource_client):
        """Test creating a list in a space."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_list("Test List", space_id="space123")

            mock_post.assert_called_once_with("/space/space123/list", data={"name": "Test List"})

    @pytest.mark.asyncio
    async def test_create_list_no_parent(self, resource_client):
        """Test creating a list without folder_id or space_id raises error."""
        with pytest.raises(ValueError) as exc_info:
            await resource_client.create_list("Test List")

        assert "Either folder_id or space_id must be provided" in str(exc_info.value)
