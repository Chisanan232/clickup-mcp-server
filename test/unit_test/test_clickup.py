from __future__ import annotations

from unittest.mock import patch

import pytest

from clickup_mcp import (
    APIResponse,
    ClickUpAPIClient,
    ClickUpResourceClient,
    create_resource_client,
)

from ._base import BaseAPIClientTestSuite


class TestClickUpResourceClient(BaseAPIClientTestSuite):
    """Test cases for ClickUpResourceClient."""

    @pytest.fixture
    def resource_client(self, api_client: ClickUpAPIClient) -> ClickUpResourceClient:
        """Create a test resource client."""
        return ClickUpResourceClient(api_client)

    # Team operations tests
    @pytest.mark.asyncio
    async def test_get_teams(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting teams."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_teams()
            mock_get.assert_called_once_with("/team")

    @pytest.mark.asyncio
    async def test_get_team(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting a specific team."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_team("123")
            mock_get.assert_called_once_with("/team/123")

    # Space operations tests
    @pytest.mark.asyncio
    async def test_get_spaces(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting spaces in a team."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_spaces("team123")
            mock_get.assert_called_once_with("/team/team123/space")

    @pytest.mark.asyncio
    async def test_get_space(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting a specific space."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_space("space123")
            mock_get.assert_called_once_with("/space/space123")

    @pytest.mark.asyncio
    async def test_create_space(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a space."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_space("team123", "Test Space", description="A test space")

            mock_post.assert_called_once_with(
                "/team/team123/space", data={"name": "Test Space", "description": "A test space"}
            )

    @pytest.mark.asyncio
    async def test_create_space_minimal(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a space with minimal data."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_space("team123", "Test Space")

            mock_post.assert_called_once_with("/team/team123/space", data={"name": "Test Space"})

    # Folder operations tests
    @pytest.mark.asyncio
    async def test_get_folders(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting folders in a space."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_folders("space123")
            mock_get.assert_called_once_with("/space/space123/folder")

    @pytest.mark.asyncio
    async def test_get_folder(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting a specific folder."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_folder("folder123")
            mock_get.assert_called_once_with("/folder/folder123")

    @pytest.mark.asyncio
    async def test_create_folder(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a folder."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_folder("space123", "Test Folder")
            mock_post.assert_called_once_with("/space/space123/folder", data={"name": "Test Folder"})

    # List operations tests
    @pytest.mark.asyncio
    async def test_get_lists_from_folder(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting lists from a folder."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_lists(folder_id="folder123")
            mock_get.assert_called_once_with("/folder/folder123/list")

    @pytest.mark.asyncio
    async def test_get_lists_from_space(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting lists from a space."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_lists(space_id="space123")
            mock_get.assert_called_once_with("/space/space123/list")

    @pytest.mark.asyncio
    async def test_get_lists_no_parent_raises_error(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting lists without folder_id or space_id raises error."""
        with pytest.raises(ValueError) as exc_info:
            await resource_client.get_lists()
        assert "Either folder_id or space_id must be provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_list(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting a specific list."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_list("list123")
            mock_get.assert_called_once_with("/list/list123")

    @pytest.mark.asyncio
    async def test_create_list_in_folder(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a list in a folder."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_list("Test List", folder_id="folder123")

            mock_post.assert_called_once_with("/folder/folder123/list", data={"name": "Test List"})

    @pytest.mark.asyncio
    async def test_create_list_in_space(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a list in a space."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_list("Test List", space_id="space123")

            mock_post.assert_called_once_with("/space/space123/list", data={"name": "Test List"})

    @pytest.mark.asyncio
    async def test_create_list_with_extra_params(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a list with additional parameters."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_list(
                "Test List", folder_id="folder123", content="Description", due_date=1609459200000
            )

            mock_post.assert_called_once_with(
                "/folder/folder123/list",
                data={"name": "Test List", "content": "Description", "due_date": 1609459200000},
            )

    @pytest.mark.asyncio
    async def test_create_list_no_parent(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a list without folder_id or space_id raises error."""
        with pytest.raises(ValueError) as exc_info:
            await resource_client.create_list("Test List")

        assert "Either folder_id or space_id must be provided" in str(exc_info.value)

    # Task operations tests
    @pytest.mark.asyncio
    async def test_get_tasks_minimal(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting tasks with minimal parameters."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_tasks("list123")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/list/list123/task"

            params = call_args[1]["params"]
            assert params["page"] == 0
            assert params["order_by"] == "created"
            assert params["reverse"] is False
            assert params["subtasks"] is False
            assert params["include_closed"] is False

    @pytest.mark.asyncio
    async def test_get_tasks_with_filters(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting tasks with filters."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_tasks(
                "list123",
                page=1,
                statuses=["open", "in progress"],
                assignees=["user1", "user2"],
                due_date_gt=1609459200000,  # Example timestamp
                tags=["urgent", "bug"],
                custom_fields=[{"field_id": "123", "value": "test"}],
            )

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/list/list123/task"

            params = call_args[1]["params"]
            assert params["page"] == 1
            assert params["statuses[]"] == ["open", "in progress"]
            assert params["assignees[]"] == ["user1", "user2"]
            assert params["due_date_gt"] == 1609459200000
            assert params["tags[]"] == ["urgent", "bug"]
            assert params["custom_fields"] == [{"field_id": "123", "value": "test"}]

    @pytest.mark.asyncio
    async def test_get_tasks_with_date_filters(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting tasks with date range filters."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_tasks(
                "list123",
                date_created_gt=1609459200000,
                date_created_lt=1609545600000,
                date_updated_gt=1609372800000,
                date_updated_lt=1609459200000,
                due_date_lt=1609718400000,
            )

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["date_created_gt"] == 1609459200000
            assert params["date_created_lt"] == 1609545600000
            assert params["date_updated_gt"] == 1609372800000
            assert params["date_updated_lt"] == 1609459200000
            assert params["due_date_lt"] == 1609718400000

    @pytest.mark.asyncio
    async def test_get_task_minimal(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting a task with minimal parameters."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_task("task123")

            mock_get.assert_called_once_with("/task/task123", params={"custom_task_ids": False})

    @pytest.mark.asyncio
    async def test_get_task_with_options(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting a task with all options."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_task("task123", custom_task_ids=True, team_id="team456")

            mock_get.assert_called_once_with("/task/task123", params={"custom_task_ids": True, "team_id": "team456"})

    @pytest.mark.asyncio
    async def test_create_task_minimal(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with minimal data."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task("list123", "Test Task")

            mock_post.assert_called_once_with(
                "/list/list123/task",
                data={"name": "Test Task", "notify_all": True, "check_required_custom_fields": True},
            )

    @pytest.mark.asyncio
    async def test_create_task_full(self, resource_client: ClickUpResourceClient) -> None:
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
                due_date_time=True,
                time_estimate=3600000,
                start_date=1609372800000,
                start_date_time=True,
                notify_all=False,
                parent="parent123",
                links_to="link456",
                check_required_custom_fields=False,
                custom_fields=[{"field_id": "123", "value": "test"}],
            )

            expected_data = {
                "name": "Test Task",
                "description": "A test task",
                "assignees": ["user1"],
                "tags": ["urgent"],
                "status": "open",
                "priority": 1,
                "due_date": 1609459200000,
                "due_date_time": True,
                "time_estimate": 3600000,
                "start_date": 1609372800000,
                "start_date_time": True,
                "notify_all": False,
                "parent": "parent123",
                "links_to": "link456",
                "check_required_custom_fields": False,
                "custom_fields": [{"field_id": "123", "value": "test"}],
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    @pytest.mark.asyncio
    async def test_create_task_partial_fields(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with some optional fields."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task(
                "list123",
                "Test Task",
                description="A test task",
                priority=3,
                due_date=1609459200000,
                # due_date_time not provided, should default to False
            )

            expected_data = {
                "name": "Test Task",
                "description": "A test task",
                "priority": 3,
                "due_date": 1609459200000,
                "due_date_time": False,
                "notify_all": True,
                "check_required_custom_fields": True,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    @pytest.mark.asyncio
    async def test_update_task(self, resource_client: ClickUpResourceClient) -> None:
        """Test updating a task."""
        with patch.object(resource_client.client, "put", return_value=APIResponse(status_code=200)) as mock_put:
            await resource_client.update_task("task123", name="Updated Task", status="completed")

            mock_put.assert_called_once_with("/task/task123", data={"name": "Updated Task", "status": "completed"})

    @pytest.mark.asyncio
    async def test_update_task_no_data(self, resource_client: ClickUpResourceClient) -> None:
        """Test updating a task with no data."""
        with patch.object(resource_client.client, "put", return_value=APIResponse(status_code=200)) as mock_put:
            await resource_client.update_task("task123")

            mock_put.assert_called_once_with("/task/task123", data={})

    @pytest.mark.asyncio
    async def test_delete_task_minimal(self, resource_client: ClickUpResourceClient) -> None:
        """Test deleting a task with minimal parameters."""
        with patch.object(resource_client.client, "delete", return_value=APIResponse(status_code=200)) as mock_delete:
            await resource_client.delete_task("task123")

            mock_delete.assert_called_once_with("/task/task123", params={"custom_task_ids": False})

    @pytest.mark.asyncio
    async def test_delete_task_with_options(self, resource_client: ClickUpResourceClient) -> None:
        """Test deleting a task with all options."""
        with patch.object(resource_client.client, "delete", return_value=APIResponse(status_code=200)) as mock_delete:
            await resource_client.delete_task("task123", custom_task_ids=True, team_id="team123")

            mock_delete.assert_called_once_with("/task/task123", params={"custom_task_ids": True, "team_id": "team123"})

    # User operations tests
    @pytest.mark.asyncio
    async def test_get_user(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting the authenticated user's information."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_user()
            mock_get.assert_called_once_with("/user")

    @pytest.mark.asyncio
    async def test_get_team_members(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting team members."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_team_members("team123")
            mock_get.assert_called_once_with("/team/team123/member")


class TestCreateResourceClient:
    """Test the create_resource_client convenience function."""

    def test_create_resource_client(self) -> None:
        """Test creating a resource client."""
        client = create_resource_client("test_token")
        assert isinstance(client, ClickUpResourceClient)
        assert isinstance(client.client, ClickUpAPIClient)
        assert client.client.api_token == "test_token"

    def test_create_resource_client_with_kwargs(self) -> None:
        """Test creating a resource client with additional kwargs."""
        client = create_resource_client("test_token", timeout=60.0, max_retries=5)
        assert isinstance(client, ClickUpResourceClient)
        assert client.client.timeout == 60.0
        assert client.client.max_retries == 5


class TestClickUpResourceClientInitialization:
    """Test ClickUpResourceClient initialization."""

    def test_initialization(self) -> None:
        """Test resource client initialization."""
        api_client = ClickUpAPIClient("test_token")
        resource_client = ClickUpResourceClient(api_client)
        assert resource_client.client is api_client


class TestClickUpResourceClientEdgeCases(BaseAPIClientTestSuite):
    """Test edge cases and error scenarios for ClickUpResourceClient."""

    @pytest.fixture
    def resource_client(self, api_client: ClickUpAPIClient) -> ClickUpResourceClient:
        """Create a test resource client."""
        return ClickUpResourceClient(api_client)

    # Edge case tests for get_lists
    @pytest.mark.asyncio
    async def test_get_lists_both_params_provided(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting lists when both folder_id and space_id are provided - should use folder_id."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_lists(folder_id="folder123", space_id="space456")
            mock_get.assert_called_once_with("/folder/folder123/list")

    # Edge case tests for create_list
    @pytest.mark.asyncio
    async def test_create_list_both_params_provided(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a list when both folder_id and space_id are provided - should use folder_id."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_list("Test List", folder_id="folder123", space_id="space456")
            mock_post.assert_called_once_with("/folder/folder123/list", data={"name": "Test List"})

    # Test get_tasks with empty optional parameters
    @pytest.mark.asyncio
    async def test_get_tasks_with_empty_lists(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting tasks with empty lists for optional parameters."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_tasks("list123", statuses=[], assignees=[], tags=[], custom_fields=[])

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[1]["params"]

            # Empty lists should not be included in params
            assert "statuses[]" not in params
            assert "assignees[]" not in params
            assert "tags[]" not in params
            assert "custom_fields" not in params

    # Test get_tasks with zero values for date parameters
    @pytest.mark.asyncio
    async def test_get_tasks_with_zero_dates(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting tasks with zero values for date parameters."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_tasks(
                "list123",
                due_date_gt=0,
                due_date_lt=0,
                date_created_gt=0,
                date_created_lt=0,
                date_updated_gt=0,
                date_updated_lt=0,
            )

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[1]["params"]

            # Zero values should be included (they're valid timestamps)
            assert params["due_date_gt"] == 0
            assert params["due_date_lt"] == 0
            assert params["date_created_gt"] == 0
            assert params["date_created_lt"] == 0
            assert params["date_updated_gt"] == 0
            assert params["date_updated_lt"] == 0

    # Test create_task with boolean parameters
    @pytest.mark.asyncio
    async def test_create_task_with_boolean_edge_cases(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with various boolean parameter combinations."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task(
                "list123",
                "Test Task",
                due_date_time=False,
                start_date_time=False,
                notify_all=False,
                check_required_custom_fields=False,
            )

            expected_data = {
                "name": "Test Task",
                "notify_all": False,
                "check_required_custom_fields": False,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    # Test create_task with priority edge cases
    @pytest.mark.asyncio
    async def test_create_task_with_priority_zero(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with priority 0."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task("list123", "Test Task", priority=0)

            expected_data = {
                "name": "Test Task",
                "priority": 0,
                "notify_all": True,
                "check_required_custom_fields": True,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    # Test create_task with empty strings
    @pytest.mark.asyncio
    async def test_create_task_with_empty_strings(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with empty strings for optional parameters (should be filtered out)."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task("list123", "Test Task", description="", status="", parent="", links_to="")

            # Empty strings should be filtered out, only required fields and defaults should remain
            expected_data = {
                "name": "Test Task",
                "notify_all": True,
                "check_required_custom_fields": True,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    # Test update_task with complex data types
    @pytest.mark.asyncio
    async def test_update_task_with_complex_data(self, resource_client: ClickUpResourceClient) -> None:
        """Test updating a task with complex data structures."""
        with patch.object(resource_client.client, "put", return_value=APIResponse(status_code=200)) as mock_put:
            complex_data = {
                "name": "Updated Task",
                "assignees": ["user1", "user2"],
                "tags": ["tag1", "tag2"],
                "custom_fields": [{"field_id": "123", "value": "test"}, {"field_id": "456", "value": 42}],
                "priority": 1,
                "due_date": 1609459200000,
                "time_estimate": 3600000,
            }

            await resource_client.update_task("task123", **complex_data)

            mock_put.assert_called_once_with("/task/task123", data=complex_data)

    # Test delete_task with all parameter combinations
    @pytest.mark.asyncio
    async def test_delete_task_all_combinations(self, resource_client: ClickUpResourceClient) -> None:
        """Test deleting a task with all parameter combinations."""
        with patch.object(resource_client.client, "delete", return_value=APIResponse(status_code=200)) as mock_delete:
            # Test with custom_task_ids=True, no team_id
            await resource_client.delete_task("task123", custom_task_ids=True)
            mock_delete.assert_called_with("/task/task123", params={"custom_task_ids": True})

            # Test with custom_task_ids=False, with team_id
            await resource_client.delete_task("task123", custom_task_ids=False, team_id="team456")
            mock_delete.assert_called_with("/task/task123", params={"custom_task_ids": False, "team_id": "team456"})

    # Test get_task with all parameter combinations
    @pytest.mark.asyncio
    async def test_get_task_all_combinations(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting a task with all parameter combinations."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            # Test with custom_task_ids=True, no team_id
            await resource_client.get_task("task123", custom_task_ids=True)
            mock_get.assert_called_with("/task/task123", params={"custom_task_ids": True})

            # Test with custom_task_ids=False, with team_id
            await resource_client.get_task("task123", custom_task_ids=False, team_id="team456")
            mock_get.assert_called_with("/task/task123", params={"custom_task_ids": False, "team_id": "team456"})

    # Test create_space with various additional parameters
    @pytest.mark.asyncio
    async def test_create_space_with_many_params(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a space with many additional parameters."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_space(
                "team123",
                "Test Space",
                multiple_assignees=True,
                features={"due_dates": {"enabled": True}},
                private=False,
            )

            expected_data = {
                "name": "Test Space",
                "multiple_assignees": True,
                "features": {"due_dates": {"enabled": True}},
                "private": False,
            }

            mock_post.assert_called_once_with("/team/team123/space", data=expected_data)


class TestClickUpResourceClientStringParameterTypes(BaseAPIClientTestSuite):
    """Test string parameter handling and type validation."""

    @pytest.fixture
    def resource_client(self, api_client: ClickUpAPIClient) -> ClickUpResourceClient:
        """Create a test resource client."""
        return ClickUpResourceClient(api_client)

    @pytest.mark.asyncio
    async def test_get_tasks_with_string_parameters(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting tasks with string parameters for order_by and other fields."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_tasks(
                "list123", order_by="updated", reverse=True, subtasks=True, include_closed=True
            )

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[1]["params"]

            assert params["order_by"] == "updated"
            assert params["reverse"] is True
            assert params["subtasks"] is True
            assert params["include_closed"] is True

    @pytest.mark.asyncio
    async def test_resource_client_with_empty_string_ids(self, resource_client: ClickUpResourceClient) -> None:
        """Test resource client methods with empty string IDs."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            # These should still make the API calls even with empty strings
            await resource_client.get_team("")
            mock_get.assert_called_with("/team/")

            await resource_client.get_space("")
            mock_get.assert_called_with("/space/")

            await resource_client.get_folder("")
            mock_get.assert_called_with("/folder/")

            await resource_client.get_list("")
            mock_get.assert_called_with("/list/")


class TestClickUpResourceClientAsyncContext(BaseAPIClientTestSuite):
    """Test async context manager behavior."""

    @pytest.mark.asyncio
    async def test_client_context_manager_usage(self, api_client: ClickUpAPIClient) -> None:
        """Test using resource client in async context manager pattern."""
        resource_client = ClickUpResourceClient(api_client)

        # Test that client can be used in async context patterns
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:

            async def use_client() -> APIResponse:
                return await resource_client.get_teams()

            response = await use_client()
            assert response.status_code == 200
            mock_get.assert_called_once_with("/team")


class TestClickUpResourceClientParameterValidation(BaseAPIClientTestSuite):
    """Test parameter validation and type safety."""

    @pytest.fixture
    def resource_client(self, api_client: ClickUpAPIClient) -> ClickUpResourceClient:
        """Create a test resource client."""
        return ClickUpResourceClient(api_client)

    @pytest.mark.asyncio
    async def test_get_tasks_with_large_page_number(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting tasks with large page numbers."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            await resource_client.get_tasks("list123", page=999999)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["page"] == 999999

    @pytest.mark.asyncio
    async def test_create_task_with_large_time_estimate(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with large time estimate."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task("list123", "Test Task", time_estimate=99999999999)  # Large number

            expected_data = {
                "name": "Test Task",
                "time_estimate": 99999999999,
                "notify_all": True,
                "check_required_custom_fields": True,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    @pytest.mark.asyncio
    async def test_create_task_with_unicode_characters(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with unicode characters."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200)) as mock_post:
            await resource_client.create_task(
                "list123",
                "Test Task 测试任务 🚀",
                description="Description with émojis and spéciål characters 你好",
                tags=["测试", "emoji🎉", "spéciål-tâg"],
            )

            expected_data = {
                "name": "Test Task 测试任务 🚀",
                "description": "Description with émojis and spéciål characters 你好",
                "tags": ["测试", "emoji🎉", "spéciål-tâg"],
                "notify_all": True,
                "check_required_custom_fields": True,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)


class TestClickUpResourceClientReturnTypes(BaseAPIClientTestSuite):
    """Test return types and response handling."""

    @pytest.fixture
    def resource_client(self, api_client: ClickUpAPIClient) -> ClickUpResourceClient:
        """Create a test resource client."""
        return ClickUpResourceClient(api_client)

    @pytest.mark.asyncio
    async def test_all_methods_return_api_response(self, resource_client: ClickUpResourceClient) -> None:
        """Test that all methods return APIResponse objects."""
        with (
            patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get,
            patch.object(resource_client.client, "post", return_value=APIResponse(status_code=201)) as mock_post,
            patch.object(resource_client.client, "put", return_value=APIResponse(status_code=200)) as mock_put,
            patch.object(resource_client.client, "delete", return_value=APIResponse(status_code=204)) as mock_delete,
        ):

            # Test GET methods
            response = await resource_client.get_teams()
            assert isinstance(response, APIResponse)
            assert response.status_code == 200

            response = await resource_client.get_team("team123")
            assert isinstance(response, APIResponse)
            assert response.status_code == 200

            response = await resource_client.get_spaces("team123")
            assert isinstance(response, APIResponse)
            assert response.status_code == 200

            response = await resource_client.get_user()
            assert isinstance(response, APIResponse)
            assert response.status_code == 200

            # Test POST methods
            response = await resource_client.create_space("team123", "Test Space")
            assert isinstance(response, APIResponse)
            assert response.status_code == 201

            response = await resource_client.create_task("list123", "Test Task")
            assert isinstance(response, APIResponse)
            assert response.status_code == 201

            # Test PUT methods
            response = await resource_client.update_task("task123", name="Updated")
            assert isinstance(response, APIResponse)
            assert response.status_code == 200

            # Test DELETE methods
            response = await resource_client.delete_task("task123")
            assert isinstance(response, APIResponse)
            assert response.status_code == 204


class TestClickUpResourceClientIntegration(BaseAPIClientTestSuite):
    """Integration-like tests for resource client functionality."""

    @pytest.fixture
    def resource_client(self, api_client: ClickUpAPIClient) -> ClickUpResourceClient:
        """Create a test resource client."""
        return ClickUpResourceClient(api_client)

    @pytest.mark.asyncio
    async def test_typical_workflow_simulation(self, resource_client: ClickUpResourceClient) -> None:
        """Test a typical workflow: get teams -> spaces -> lists -> tasks."""
        with (
            patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get,
            patch.object(resource_client.client, "post", return_value=APIResponse(status_code=201)) as mock_post,
        ):

            # Step 1: Get teams
            await resource_client.get_teams()

            # Step 2: Get spaces in a team
            await resource_client.get_spaces("team123")

            # Step 3: Get lists in a space
            await resource_client.get_lists(space_id="space456")

            # Step 4: Get tasks in a list
            await resource_client.get_tasks("list789")

            # Step 5: Create a new task
            await resource_client.create_task("list789", "New Task")

            # Verify all calls were made
            assert mock_get.call_count == 4
            assert mock_post.call_count == 1

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, resource_client: ClickUpResourceClient) -> None:
        """Test error handling in typical workflows."""
        # Test that ValueError is raised for invalid get_lists call
        with pytest.raises(ValueError, match="Either folder_id or space_id must be provided"):
            await resource_client.get_lists()

        # Test that ValueError is raised for invalid create_list call
        with pytest.raises(ValueError, match="Either folder_id or space_id must be provided"):
            await resource_client.create_list("Test List")


# Additional tests for the convenience function
class TestCreateResourceClientFunction:
    """Test the create_resource_client convenience function with various scenarios."""

    def test_create_resource_client_with_default_params(self) -> None:
        """Test creating a resource client with default parameters."""
        client = create_resource_client("test_token")
        assert isinstance(client, ClickUpResourceClient)
        assert isinstance(client.client, ClickUpAPIClient)
        assert client.client.api_token == "test_token"
        assert client.client.timeout == 30.0  # Default timeout
        assert client.client.max_retries == 3  # Default max_retries

    def test_create_resource_client_with_custom_params(self) -> None:
        """Test creating a resource client with custom parameters."""
        client = create_resource_client(
            "test_token", timeout=60.0, max_retries=5, retry_delay=2.0, rate_limit_requests_per_minute=50
        )
        assert isinstance(client, ClickUpResourceClient)
        assert client.client.timeout == 60.0
        assert client.client.max_retries == 5
        assert client.client.retry_delay == 2.0
        assert client.client.rate_limit == 50

    def test_create_resource_client_with_empty_token(self) -> None:
        """Test creating a resource client with empty token."""
        client = create_resource_client("")
        assert isinstance(client, ClickUpResourceClient)
        assert client.client.api_token == ""

    def test_create_resource_client_with_long_token(self) -> None:
        """Test creating a resource client with a very long token."""
        long_token = "a" * 1000  # 1000 character token
        client = create_resource_client(long_token)
        assert isinstance(client, ClickUpResourceClient)
        assert client.client.api_token == long_token
