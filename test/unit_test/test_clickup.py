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

    # Parameterized tests for getting specific resources
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "resource_id, method_name, expected_url, response_data",
        [
            (
                "123",
                "get_team",
                "/team/123",
                {"id": "123", "name": "Test Team"},
            ),
            (
                "space123",
                "get_space",
                "/space/space123",
                {"id": "space123", "name": "Test Space"},
            ),
            (
                "folder123",
                "get_folder",
                "/folder/folder123",
                {"id": "folder123", "name": "Test Folder"},
            ),
            (
                "list123",
                "get_list",
                "/list/list123",
                {"id": "list123", "name": "Test List"},
            ),
        ],
    )
    async def test_get_specific_resource(
        self, resource_client: ClickUpResourceClient, resource_id: str, 
        method_name: str, expected_url: str, response_data: dict
    ) -> None:
        """Test getting a specific resource by ID."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data=response_data)) as mock_get:
            # Call the appropriate method dynamically
            method = getattr(resource_client, method_name)
            await method(resource_id)
            mock_get.assert_called_once_with(expected_url)

    # Parameterized tests for getting resource collections
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "parent_id, method_name, endpoint",
        [
            ("team123", "get_spaces", "/team/team123/space"),
            ("space123", "get_folders", "/space/space123/folder"),
        ],
    )
    async def test_get_resource_collections(
        self, resource_client: ClickUpResourceClient, parent_id: str, method_name: str, endpoint: str
    ) -> None:
        """Test getting collections of resources (spaces, folders)."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200)) as mock_get:
            method = getattr(resource_client, method_name)
            await method(parent_id)
            mock_get.assert_called_once_with(endpoint)

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
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"id": "space123", "name": "Test Space"})) as mock_get:
            await resource_client.get_space("space123")
            mock_get.assert_called_once_with("/space/space123")

    @pytest.mark.asyncio
    async def test_create_space_minimal(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a space with minimal data."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "space123", "name": "Test Space"})) as mock_post:
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
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"id": "folder123", "name": "Test Folder"})) as mock_get:
            await resource_client.get_folder("folder123")
            mock_get.assert_called_once_with("/folder/folder123")

    @pytest.mark.asyncio
    async def test_create_folder(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a folder."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "folder123", "name": "Test Folder"})) as mock_post:
            await resource_client.create_folder("space123", "Test Folder")
            mock_post.assert_called_once_with("/space/space123/folder", data={"name": "Test Folder"})

    # Parameterized tests for get_lists with different container types
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "container_id, container_type, endpoint",
        [
            ("folder123", "folder", "/folder/folder123/list"),
            ("space123", "space", "/space/space123/list"),
        ],
    )
    async def test_get_lists_from_container(
        self, resource_client: ClickUpResourceClient, container_id: str, container_type: str, endpoint: str
    ) -> None:
        """Test getting lists from different containers (folder, space)."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"lists": []})) as mock_get:
            await resource_client.get_lists(container_id, container_type=container_type)
            mock_get.assert_called_once_with(endpoint)

    @pytest.mark.asyncio
    async def test_get_lists_no_parent_raises_error(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting lists with empty request raises error."""
        with pytest.raises(ValueError, match="Container ID not found in request"):
            await resource_client.get_lists({})

    # Parameterized tests for creating lists in different containers
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "container_id, container_type, endpoint",
        [
            ("folder123", "folder", "/folder/folder123/list"),
            ("space123", "space", "/space/space123/list"),
        ],
    )
    async def test_create_list_in_container(
        self, resource_client: ClickUpResourceClient, container_id: str, container_type: str, endpoint: str
    ) -> None:
        """Test creating a list in different containers (folder, space)."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "list123", "name": "Test List"})) as mock_post:
            if container_type == "folder":
                await resource_client.create_list(container_id, "Test List")
            else:
                await resource_client.create_list(container_id, "Test List", container_type=container_type)

            mock_post.assert_called_once_with(endpoint, data={"name": "Test List"})

    @pytest.mark.asyncio
    async def test_create_list_with_extra_params(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a list with additional parameters."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "list123", "name": "Test List"})) as mock_post:
            await resource_client.create_list(
                "folder123", "Test List", content="Description", due_date=1609459200000
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

        assert "Name is required when providing container_id as string" in str(exc_info.value)

    # Parameterized tests for task retrieval scenarios
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "scenario, request_type, list_id, kwargs, expected_params",
        [
            (
                "minimal",
                "string", 
                "list123",
                {},
                {
                    "page": 0,
                    "order_by": "created",
                    "reverse": False,
                    "subtasks": False,
                    "include_closed": False,
                }
            ),
            (
                "with_filters",
                "object", 
                "list123",
                {
                    "page": 1,
                    "statuses": ["open", "in progress"],
                    "assignees": ["user1", "user2"],
                    "due_date_gt": 1609459200000,
                    "tags": ["urgent", "bug"],
                    "custom_fields": [{"field_id": "123", "value": "test"}],
                },
                {
                    "page": 1,
                    "statuses[]": ["open", "in progress"],
                    "assignees[]": ["user1", "user2"],
                    "due_date_gt": 1609459200000,
                    "tags[]": ["urgent", "bug"],
                    "custom_fields": [{"field_id": "123", "value": "test"}],
                }
            ),
            (
                "with_date_filters",
                "object", 
                "list123",
                {
                    "date_created_gt": 1609459200000,
                    "date_created_lt": 1609545600000,
                    "date_updated_gt": 1609372800000,
                    "date_updated_lt": 1609459200000,
                    "due_date_lt": 1609718400000,
                },
                {
                    "page": 0,
                    "order_by": "created",
                    "reverse": False,
                    "subtasks": False,
                    "include_closed": False,
                    "date_created_gt": 1609459200000,
                    "date_created_lt": 1609545600000,
                    "date_updated_gt": 1609372800000,
                    "date_updated_lt": 1609459200000,
                    "due_date_lt": 1609718400000,
                }
            ),
        ],
    )
    async def test_get_tasks_scenarios(
        self, resource_client: ClickUpResourceClient, scenario: str, 
        request_type: str, list_id: str, kwargs: dict, expected_params: dict
    ) -> None:
        """Test getting tasks with different parameter scenarios."""
        from clickup_mcp.models import Task
        
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"tasks": []})) as mock_get:
            if request_type == "string":
                await resource_client.get_tasks(list_id, **kwargs)
            else:
                # Create a task request object
                task_request = Task.list_request(list_id=list_id, **kwargs)
                await resource_client.get_tasks(task_request)
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == f"/list/{list_id}/task"
            
            params = call_args[1]["params"]
            for key, value in expected_params.items():
                assert params[key] == value, f"Parameter {key} does not match expected value"

    # Parameterized tests for task creation scenarios
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "scenario, args, kwargs, expected_data",
        [
            (
                "minimal",
                ["list123", "Test Task"],
                {},
                {
                    "name": "Test Task", 
                    "due_date_time": False, 
                    "start_date_time": False
                }
            ),
            (
                "with_description_and_priority",
                ["list123", "Test Task"],
                {
                    "description": "A test task",
                    "priority": 3,
                    "due_date": 1609459200000,
                },
                {
                    "name": "Test Task",
                    "description": "A test task",
                    "priority": 3,
                    "due_date": 1609459200000,
                    "due_date_time": False,
                    "start_date_time": False,
                }
            ),
        ],
    )
    async def test_create_task_scenarios(
        self, resource_client: ClickUpResourceClient, scenario: str, args: list, kwargs: dict, expected_data: dict
    ) -> None:
        """Test creating tasks with different parameter scenarios."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "task123", "name": "Test Task"})) as mock_post:
            await resource_client.create_task(*args, **kwargs)
            mock_post.assert_called_once_with(f"/list/{args[0]}/task", data=expected_data)

    @pytest.mark.asyncio
    async def test_create_task_full(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with all optional data."""
        from clickup_mcp.models import Task
        
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "task123", "name": "Test Task"})) as mock_post:
            # Create a task request with all parameters
            task_request = Task.create_request(
                list_id="list123",
                name="Test Task",
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
            
            await resource_client.create_task(task_request)

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

    # Parameterized tests for task update scenarios
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "scenario, task_id, kwargs, expected_data, expected_params",
        [
            (
                "no_data",
                "task123", 
                {}, 
                {}, 
                {}
            ),
            (
                "with_name_and_status",
                "task123", 
                {"name": "Updated Task", "status": "completed"}, 
                {"name": "Updated Task", "status": "completed"}, 
                {}
            ),
            (
                "with_custom_task_ids",
                "TASK-123", 
                {"name": "Updated Task", "custom_task_ids": True, "team_id": "team456"}, 
                {"name": "Updated Task"}, 
                {"custom_task_ids": "true"}
            ),
        ],
    )
    async def test_update_task_scenarios(
        self, resource_client: ClickUpResourceClient, scenario: str, 
        task_id: str, kwargs: dict, expected_data: dict, expected_params: dict
    ) -> None:
        """Test updating tasks with different parameter scenarios."""
        with patch.object(resource_client.client, "put", return_value=APIResponse(status_code=200, data={"id": task_id, "name": kwargs.get("name", "Task")})) as mock_put:
            # Extract non-API parameters
            api_kwargs = kwargs.copy()
            custom_task_ids = api_kwargs.pop("custom_task_ids", False)
            team_id = api_kwargs.pop("team_id", None)
            
            if custom_task_ids and team_id:
                await resource_client.update_task(task_id, custom_task_ids=custom_task_ids, team_id=team_id, **api_kwargs)
                endpoint = f"/task/{team_id}/{task_id}"
            else:
                await resource_client.update_task(task_id, **kwargs)
                endpoint = f"/task/{task_id}"
            
            mock_put.assert_called_once_with(endpoint, data=expected_data, params=expected_params)

    # User operations tests
    @pytest.mark.asyncio
    async def test_get_user(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting the authenticated user's information."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"id": "user123", "username": "testuser", "email": "test@example.com"})) as mock_get:
            await resource_client.get_user()
            mock_get.assert_called_once_with("/user")


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
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"lists": []})) as mock_get:
            await resource_client.get_lists({"folder_id": "folder123", "space_id": "space456"})
            mock_get.assert_called_once_with("/folder/folder123/list")

    # Edge case tests for create_list
    @pytest.mark.asyncio
    async def test_create_list_both_params_provided(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a list when both folder_id and space_id are provided - should use folder_id."""
        from clickup_mcp.models import ClickUpList

        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "list123", "name": "Test List"})) as mock_post:
            list_request = ClickUpList(name="Test List", folder_id="folder123", space_id="space456")
            await resource_client.create_list(list_request)
            mock_post.assert_called_once_with("/folder/folder123/list", data={"name": "Test List"})

    # Test get_tasks with params dict
    @pytest.mark.asyncio
    async def test_get_tasks_with_params(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting tasks with params dict."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"tasks": []})) as mock_get:
            params = {"page": 1, "order_by": "created", "reverse": False}
            await resource_client.get_tasks("list123", params)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/list/list123/task"

    # Test create_task with boolean parameters
    @pytest.mark.asyncio
    async def test_create_task_with_boolean_edge_cases(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with boolean notify_all parameter."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "task123", "name": "Test Task"})) as mock_post:
            await resource_client.create_task(
                "list123",
                "Test Task",
                notify_all=False,
            )

            expected_data = {
                "name": "Test Task",
                "due_date_time": False,
                "start_date_time": False,
                "notify_all": False,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    # Test create_task with priority edge cases
    @pytest.mark.asyncio
    async def test_create_task_with_priority_zero(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with priority 0."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "task123", "name": "Test Task"})) as mock_post:
            await resource_client.create_task("list123", "Test Task", priority=0)

            expected_data = {
                "name": "Test Task",
                "priority": 0,
                "due_date_time": False,
                "start_date_time": False,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    # Test create_task with empty strings
    @pytest.mark.asyncio
    async def test_create_task_with_empty_strings(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with empty strings for optional parameters (should be filtered out)."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "task123", "name": "Test Task"})) as mock_post:
            await resource_client.create_task("list123", "Test Task", description="", status="", parent="", links_to="")

            # Empty strings should be filtered out, only required fields and defaults should remain
            expected_data = {
                "name": "Test Task",
                "due_date_time": False,
                "start_date_time": False,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    # Test update_task with complex data types
    @pytest.mark.asyncio
    async def test_update_task_with_complex_data(self, resource_client: ClickUpResourceClient) -> None:
        """Test updating a task with complex data structures."""
        with patch.object(resource_client.client, "put", return_value=APIResponse(status_code=200, data={"id": "task123", "name": "Updated Task"})) as mock_put:
            complex_data = {
                "name": "Updated Task",
                "assignees": ["user1", "user2"],
                "tags": ["tag1", "tag2"],
                "custom_fields": [{"field_id": "123", "value": "test"}, {"field_id": "456", "value": 42}],
                "priority": 1,
                "due_date": 1609459200000,
            }

            await resource_client.update_task("task123", data=complex_data)

            mock_put.assert_called_once_with("/task/task123", data=complex_data, params={})

    # Test delete_task with all parameter combinations
    @pytest.mark.asyncio
    async def test_delete_task_all_combinations(self, resource_client: ClickUpResourceClient) -> None:
        """Test deleting a task with all parameter combinations."""
        with patch.object(resource_client.client, "delete", return_value=APIResponse(status_code=200)) as mock_delete:
            # Test with custom_task_ids=True, no team_id - should use standard endpoint
            await resource_client.delete_task("task123", custom_task_ids=True)
            mock_delete.assert_called_with("/task/task123", params={})

            # Test with custom_task_ids=True, with team_id - should use custom endpoint
            await resource_client.delete_task("task123", custom_task_ids=True, team_id="team456")
            mock_delete.assert_called_with("/task/team456/task123", params={"custom_task_ids": "true"})

    # Test get_task with all parameter combinations
    @pytest.mark.asyncio
    async def test_get_task_all_combinations(self, resource_client: ClickUpResourceClient) -> None:
        """Test getting a task with all parameter combinations."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"id": "task123", "name": "Test Task", "list": {"id": "list123"}})) as mock_get:
            # Test with custom_task_ids=True, no team_id - should use standard endpoint
            await resource_client.get_task("task123", custom_task_ids=True)
            mock_get.assert_called_with("/task/task123", params={})

            # Test with custom_task_ids=True, with team_id - should use custom endpoint
            await resource_client.get_task("task123", custom_task_ids=True, team_id="team456")
            mock_get.assert_called_with("/task/team456/task123", params={"custom_task_ids": "true"})

    # Test create_space with various additional parameters
    @pytest.mark.asyncio
    async def test_create_space_with_many_params(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a space with many additional parameters."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "space123", "name": "Test Space"})) as mock_post:
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
        """Test getting tasks with string parameters."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"tasks": []})) as mock_get:
            # Create a Task object with parameters
            from clickup_mcp.models import Task
            task_params = Task(
                list_id="list123",
                name="",
                order_by="updated",
                reverse=True,
                subtasks=True,
                include_closed=True
            )
            await resource_client.get_tasks(task_params)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/list/list123/task"

    @pytest.mark.asyncio
    async def test_resource_client_with_empty_string_ids(self, resource_client: ClickUpResourceClient) -> None:
        """Test resource client methods with empty string IDs."""
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"id": "", "name": ""})) as mock_get:
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
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"teams": []})) as mock_get:

            async def use_client() -> list:
                return await resource_client.get_teams()

            response = await use_client()
            assert isinstance(response, list)
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
        with patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"tasks": []})) as mock_get:
            from clickup_mcp.models import Task
            task_params = Task(list_id="list123", name="", page=999999)
            await resource_client.get_tasks(task_params)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/list/list123/task"

    @pytest.mark.asyncio
    async def test_create_task_with_large_time_estimate(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with large due date."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "task123", "name": "Test Task"})) as mock_post:
            await resource_client.create_task("list123", "Test Task", due_date=99999999999)  # Large number

            expected_data = {
                "name": "Test Task",
                "due_date": 99999999999,
                "due_date_time": False,
                "start_date_time": False,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)

    @pytest.mark.asyncio
    async def test_create_task_with_unicode_characters(self, resource_client: ClickUpResourceClient) -> None:
        """Test creating a task with unicode characters."""
        with patch.object(resource_client.client, "post", return_value=APIResponse(status_code=200, data={"id": "task123", "name": "Test Task 测试任务 🚀"})) as mock_post:
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
                "due_date_time": False,
                "start_date_time": False,
            }

            mock_post.assert_called_once_with("/list/list123/task", data=expected_data)


class TestClickUpResourceClientReturnTypes(BaseAPIClientTestSuite):
    """Test return types and response handling."""

    @pytest.fixture
    def resource_client(self, api_client: ClickUpAPIClient) -> ClickUpResourceClient:
        """Create a test resource client."""
        return ClickUpResourceClient(api_client)

    @pytest.mark.asyncio
    async def test_all_methods_return_domain_models(self, resource_client: ClickUpResourceClient) -> None:
        """Test that all methods return appropriate domain models."""
        with (
            patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"teams": []})) as mock_get,
            patch.object(resource_client.client, "post", return_value=APIResponse(status_code=201, data={"id": "123", "name": "test"})) as mock_post,
            patch.object(resource_client.client, "put", return_value=APIResponse(status_code=200, data={"id": "123", "name": "updated"})) as mock_put,
            patch.object(resource_client.client, "delete", return_value=APIResponse(status_code=204)) as mock_delete,
        ):

            # Test GET methods
            response = await resource_client.get_teams()
            assert isinstance(response, list)

            # Mock team data with required fields
            mock_get.return_value = APIResponse(status_code=200, data={"id": "team123", "name": "Test Team"})
            response = await resource_client.get_team("team123")
            assert response.__class__.__name__ == "ClickUpTeam"

            response = await resource_client.get_spaces("team123")
            assert isinstance(response, list)

            # Mock user data with required fields
            mock_get.return_value = APIResponse(status_code=200, data={"id": "user123", "username": "testuser", "email": "test@example.com"})
            response = await resource_client.get_user()
            assert hasattr(response, "id")
            assert hasattr(response, "username")
            assert hasattr(response, "email")

            # Test POST methods
            response = await resource_client.create_space("team123", "Test Space")
            assert hasattr(response, "id")
            assert hasattr(response, "name")

            response = await resource_client.create_task("list123", "Test Task")
            assert hasattr(response, "task_id")
            assert hasattr(response, "name")

            # Test PUT methods
            response = await resource_client.update_task("task123", name="Updated")
            assert hasattr(response, "task_id")
            assert hasattr(response, "name")

            # Test DELETE methods
            response = await resource_client.delete_task("task123")
            assert isinstance(response, APIResponse)
            assert response.status_code == 204
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
            patch.object(resource_client.client, "get", return_value=APIResponse(status_code=200, data={"teams": [], "spaces": [], "lists": [], "tasks": []})) as mock_get,
            patch.object(resource_client.client, "post", return_value=APIResponse(status_code=201, data={"id": "task123", "name": "New Task"})) as mock_post,
        ):

            # Step 1: Get teams
            await resource_client.get_teams()

            # Step 2: Get spaces in a team
            await resource_client.get_spaces("team123")

            # Step 3: Get lists in a space
            await resource_client.get_lists({"space_id": "space456"})

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
        # Test that ValueError is raised for invalid get_lists call with empty dict
        with pytest.raises(ValueError, match="Container ID not found in request"):
            await resource_client.get_lists({})  # Empty dict will raise ValueError

        # Test that ValueError is raised for invalid create_list call
        with pytest.raises(ValueError, match="Name is required when providing container_id as string"):
            await resource_client.create_list("container123")


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
