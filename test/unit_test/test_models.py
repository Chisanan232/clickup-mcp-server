"""
Unit tests for ClickUp models.

This module tests all Pydantic models used in the ClickUp MCP server,
including validation, serialization, and helper functions.
"""

import pytest
from pydantic import ValidationError

from clickup_mcp.models import (  # Base models; Domain models; Task models; Response models
    ClickUpBaseModel,
    ClickUpFolder,
    ClickUpList,
    ClickUpListDomain,
    ClickUpSpace,
    ClickUpTeam,
    ClickUpUser,
    CustomField,
    Folder,
    List,
    Space,
    Task,
    Team,
    User,
    snake_to_camel,
)


class TestUtilityFunctions:
    """Test utility functions."""

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("snake_case", "snakeCase"),
            ("single", "single"),
            ("multiple_word_test", "multipleWordTest"),
            ("", ""),
            ("a_b_c_d", "aBCD"),
        ],
    )
    def test_snake_to_camel(self, input_str, expected_output):
        """Test snake_case to camelCase conversion."""
        assert snake_to_camel(input_str) == expected_output


class TestBaseModel:
    """Test the base ClickUp model."""

    def test_base_model_configuration(self):
        """Test base model configuration."""

        class TestModel(ClickUpBaseModel):
            test_field: str
            another_field: int

        # Test alias generation
        model = TestModel(test_field="test", another_field=42)
        assert model.test_field == "test"
        assert model.another_field == 42

        # Test serialization with aliases
        data = model.model_dump(by_alias=True)
        assert "testField" in data
        assert "anotherField" in data
        assert data["testField"] == "test"
        assert data["anotherField"] == 42


class TestDomainModels:
    """Test domain models and their operations."""

    @pytest.mark.parametrize(
        "request_method, team_id, expected_attr",
        [
            ("get_request", "123", "team_id"),
            ("get_members_request", "456", "team_id"),
        ],
    )
    def test_team_operations(self, request_method, team_id, expected_attr):
        """Test Team domain model operations."""
        method = getattr(Team, request_method)
        request = method(team_id=team_id)
        assert getattr(request, expected_attr) == team_id

    @pytest.mark.parametrize(
        "request_method, param_name, param_value, expected_attr",
        [
            ("get_request", "space_id", "space123", "space_id"),
            ("list_request", "team_id", "team123", "team_id"),
        ],
    )
    def test_space_operations_basic(self, request_method, param_name, param_value, expected_attr):
        """Test basic Space domain model operations."""
        method = getattr(Space, request_method)
        kwargs = {param_name: param_value}
        request = method(**kwargs)
        assert getattr(request, expected_attr) == param_value

    def test_space_create_request(self):
        """Test Space create request with all parameters."""
        space_create_req = Space.create_request(
            team_id="team123",
            name="New Space",
            description="Test space",
            multiple_assignees=True,
            features={"time_tracking": True},
            private=False,
        )
        assert space_create_req.team_id == "team123"
        assert space_create_req.name == "New Space"
        assert space_create_req.description == "Test space"
        assert space_create_req.multiple_assignees is True
        assert space_create_req.features == {"time_tracking": True}
        assert space_create_req.private is False

        # Test validation
        with pytest.raises(ValueError, match="team_id is required when creating a space"):
            Space(name="Test Space").validate_create_request()

        # Test extract_create_data
        create_data = space_create_req.extract_create_data()
        assert create_data["name"] == "New Space"
        assert create_data["description"] == "Test space"
        assert create_data["multiple_assignees"] is True
        assert create_data["features"] == {"time_tracking": True}
        assert create_data["private"] is False

    @pytest.mark.parametrize(
        "request_method, param_name, param_value, expected_attr",
        [
            ("get_request", "folder_id", "folder123", "folder_id"),
            ("list_request", "space_id", "space123", "space_id"),
        ],
    )
    def test_folder_operations_basic(self, request_method, param_name, param_value, expected_attr):
        """Test basic Folder domain model operations."""
        method = getattr(Folder, request_method)
        kwargs = {param_name: param_value}
        request = method(**kwargs)
        assert getattr(request, expected_attr) == param_value

    def test_folder_create_request(self):
        """Test Folder create request."""
        folder_create_req = Folder.create_request(space_id="space123", name="New Folder")
        assert folder_create_req.space_id == "space123"
        assert folder_create_req.name == "New Folder"

        # Test validation
        with pytest.raises(ValueError, match="space_id is required when creating a folder"):
            Folder(name="Test Folder").validate_create_request()

        # Test extract_create_data
        create_data = folder_create_req.extract_create_data()
        assert create_data["name"] == "New Folder"

    def test_list_operations(self):
        """Test ClickUpListDomain model operations."""
        # Get request
        list_req = ClickUpListDomain.get_request(list_id="list123")
        assert list_req.list_id == "list123"

        # List request with folder_id
        list_folder_req = ClickUpListDomain.list_request(folder_id="folder123")
        assert list_folder_req.folder_id == "folder123"

        # List request with space_id
        list_space_req = ClickUpListDomain.list_request(space_id="space123")
        assert list_space_req.space_id == "space123"

        # Test list request validation error
        with pytest.raises(ValueError, match="Either folder_id or space_id must be provided"):
            ClickUpListDomain.list_request()

        # Create request with folder_id
        list_create_folder_req = ClickUpListDomain.create_request(
            name="New List",
            folder_id="folder123",
            content="List description",
            due_date=1640995200,
            due_date_time=True,
            priority=1,
            assignee="user123",
            status="in progress",
        )
        assert list_create_folder_req.name == "New List"
        assert list_create_folder_req.folder_id == "folder123"
        assert list_create_folder_req.content == "List description"

        # Create request with space_id
        list_create_space_req = ClickUpListDomain.create_request(name="New List", space_id="space123")
        assert list_create_space_req.name == "New List"
        assert list_create_space_req.space_id == "space123"

        # Test validation
        with pytest.raises(ValueError, match="Either folder_id or space_id must be provided when creating a list"):
            ClickUpListDomain(name="Test List").validate_create_request()

        # Test extract_create_data with all fields
        create_data = list_create_folder_req.extract_create_data()
        assert create_data["name"] == "New List"
        assert create_data["content"] == "List description"
        assert create_data["due_date"] == 1640995200
        assert create_data["due_date_time"] is True
        assert create_data["priority"] == 1
        assert create_data["assignee"] == "user123"
        assert create_data["status"] == "in progress"

        # Test backward compatibility
        list_instance = ClickUpList.create_request(name="Backwards", folder_id="folder456")
        assert isinstance(list_instance, ClickUpListDomain)

    def test_task_get_request_operations(self):
        """Test Task domain model get request operations."""
        # Get request
        task_req = Task.get_request(task_id="task123")
        assert task_req.task_id == "task123"

        # Get request with custom_task_ids and team_id
        task_custom_req = Task.get_request(task_id="TASK-123", custom_task_ids=True, team_id="team123")
        assert task_custom_req.task_id == "TASK-123"
        assert task_custom_req.custom_task_ids is True
        assert task_custom_req.team_id == "team123"

    def test_task_list_request_operations(self):
        """Test Task domain model list request operations."""
        # List request
        task_list_req = Task.list_request(
            list_id="list123",
            page=1,
            order_by="due_date",
            reverse=True,
            subtasks=True,
            include_closed=True,
            statuses=["in progress", "review"],
            assignees=["user1", "user2"],
            tags=["important", "urgent"],
            due_date_gt=1640995200,
            due_date_lt=1641081600,
            date_created_gt=1640908800,
            date_created_lt=1640995200,
            date_updated_gt=1640995200,
            date_updated_lt=1641081600,
            custom_fields=[{"field_id": "field1", "value": "high"}],
        )
        assert task_list_req.list_id == "list123"
        assert task_list_req.page == 1
        assert task_list_req.order_by == "due_date"
        assert task_list_req.reverse is True

        # Test extract_list_params
        list_params = task_list_req.extract_list_params()
        assert list_params["page"] == 1
        assert list_params["order_by"] == "due_date"
        assert list_params["reverse"] is True
        assert list_params["subtasks"] is True
        assert list_params["include_closed"] is True
        assert list_params["statuses[]"] == ["in progress", "review"]
        assert list_params["assignees[]"] == ["user1", "user2"]
        assert list_params["tags[]"] == ["important", "urgent"]
        assert list_params["due_date_gt"] == 1640995200
        assert list_params["due_date_lt"] == 1641081600
        assert list_params["date_created_gt"] == 1640908800
        assert list_params["date_created_lt"] == 1640995200
        assert list_params["date_updated_gt"] == 1640995200
        assert list_params["date_updated_lt"] == 1641081600
        assert list_params["custom_fields"] == [{"field_id": "field1", "value": "high"}]

    def test_task_create_request_operations(self):
        """Test Task domain model create request operations."""
        # Create request
        custom_fields = [
            CustomField(id="field1", name="Priority", type="drop_down", value="high"),
            {"field_id": "field2", "value": "medium"},
        ]
        task_create_req = Task.create_request(
            list_id="list123",
            name="New Task",
            description="Task description",
            assignees=["user1", "user2"],
            tags=["important"],
            status="open",
            priority=1,  # High priority
            due_date=1641081600,
            due_date_time=True,
            time_estimate=3600000,
            start_date=1640995200,
            start_date_time=True,
            notify_all=True,
            parent="parent123",
            links_to="linked123",
            check_required_custom_fields=True,
            custom_fields=custom_fields,
        )
        assert task_create_req.list_id == "list123"
        assert task_create_req.name == "New Task"
        assert task_create_req.priority == 1

        # Test extract_create_data
        create_data = task_create_req.extract_create_data()
        assert create_data["name"] == "New Task"
        assert create_data["description"] == "Task description"
        assert create_data["assignees"] == ["user1", "user2"]
        assert create_data["tags"] == ["important"]
        assert create_data["status"] == "open"
        assert create_data["priority"] == 1
        assert create_data["due_date"] == 1641081600
        assert create_data["due_date_time"] is True
        assert create_data["time_estimate"] == 3600000
        assert create_data["start_date"] == 1640995200
        assert create_data["start_date_time"] is True
        assert create_data["notify_all"] is True
        assert create_data["parent"] == "parent123"
        assert create_data["links_to"] == "linked123"
        assert create_data["check_required_custom_fields"] is True
        assert len(create_data["custom_fields"]) == 2
        assert create_data["custom_fields"][0]["field_id"] == "field1"
        assert create_data["custom_fields"][1]["field_id"] == "field2"

    def test_task_update_and_delete_operations(self):
        """Test Task domain model update and delete operations."""
        # Update request
        task_update_req = Task.update_request(
            task_id="task123",
            name="Updated Task",
            description="Updated description",
            assignees=["user3"],
            tags=["completed"],
            status="done",
            priority=4,  # Low priority
            due_date=1641168000,
            time_estimate=7200000,
            start_date=1641081600,
            custom_fields=[{"field_id": "field1", "value": "low"}],
        )
        assert task_update_req.task_id == "task123"
        assert task_update_req.name == "Updated Task"

        # Test extract_update_data
        update_data = task_update_req.extract_update_data()
        assert update_data["name"] == "Updated Task"
        assert update_data["description"] == "Updated description"
        assert update_data["assignees"] == ["user3"]
        assert update_data["tags"] == ["completed"]
        assert update_data["status"] == "done"
        assert update_data["priority"] == 4
        assert update_data["due_date"] == 1641168000
        assert update_data["time_estimate"] == 7200000
        assert update_data["start_date"] == 1641081600
        assert update_data["custom_fields"][0]["field_id"] == "field1"
        assert update_data["custom_fields"][0]["value"] == "low"

        # Delete request
        task_delete_req = Task.delete_request(task_id="task123")
        assert task_delete_req.task_id == "task123"

        # Delete request with custom_task_ids and team_id
        task_custom_delete_req = Task.delete_request(task_id="TASK-123", custom_task_ids=True, team_id="team123")
        assert task_custom_delete_req.task_id == "TASK-123"
        assert task_custom_delete_req.custom_task_ids is True
        assert task_custom_delete_req.team_id == "team123"

    @pytest.mark.parametrize(
        "priority_value, expected_result, should_raise",
        [
            (0, 0, False),  # No priority
            (1, 1, False),  # Urgent
            (2, 2, False),  # High
            (3, 3, False),  # Normal
            (4, 4, False),  # Low
            (5, None, True),  # Invalid - too high
            (-1, None, True),  # Invalid - negative
        ],
    )
    def test_task_priority_validation(self, priority_value, expected_result, should_raise):
        """Test priority validation."""
        if should_raise:
            with pytest.raises(ValueError, match=r"Priority must be between 0 \(no priority\) and 4 \(low\)"):
                Task(priority=priority_value).validate_priority(priority_value)
        else:
            assert Task.validate_priority(priority_value) == expected_result

    def test_user_operations(self):
        """Test User domain model operations."""
        # Get request
        user_req = User.get_request()
        assert isinstance(user_req, User)

    def test_space_update_data(self):
        """Test Space update_data method."""
        # Test with all parameters
        update_data = Space.update_data(
            name="Updated Space",
            description="Updated description",
            multiple_assignees=False,
            features={"time_tracking": False},
            private=True,
            custom_field="custom_value"
        )
        assert update_data["name"] == "Updated Space"
        assert update_data["description"] == "Updated description"
        assert update_data["multiple_assignees"] is False
        assert update_data["features"] == {"time_tracking": False}
        assert update_data["private"] is True
        assert update_data["custom_field"] == "custom_value"

        # Test with partial parameters
        partial_update = Space.update_data(name="Updated Space", description="Updated description")
        assert partial_update["name"] == "Updated Space"
        assert partial_update["description"] == "Updated description"
        assert "multiple_assignees" not in partial_update
        assert "features" not in partial_update
        assert "private" not in partial_update
        
        # Test with None values
        none_update = Space.update_data(name=None, description="Updated description")
        assert "name" not in none_update
        assert none_update["description"] == "Updated description"

    @pytest.mark.parametrize(
        "space_params",
        [
            # Test with minimal parameters
            {"name": "Test Space", "team_id": "team123"},
            # Test with all parameters
            {
                "name": "Full Space", 
                "team_id": "team456", 
                "description": "Complete space",
                "multiple_assignees": True,
                "features": {"time_tracking": True},
                "private": False
            },
            # Test with custom parameters
            {
                "name": "Custom Space", 
                "team_id": "team789", 
                "custom_field": "custom_value",
                "extra_data": {"key": "value"}
            }
        ],
    )
    def test_space_initial(self, space_params):
        """Test Space initial method with various parameters."""
        space = Space.initial(**space_params)
        
        # Check all parameters were correctly set
        for key, value in space_params.items():
            assert getattr(space, key) == value

    def test_folder_update_data(self):
        """Test Folder update_data method."""
        # Test with name only
        update_data = Folder.update_data(name="Updated Folder")
        assert update_data["name"] == "Updated Folder"
        
        # Test with additional parameters
        update_data_with_extras = Folder.update_data(
            name="Updated Folder",
            custom_field="custom_value",
            another_field=123
        )
        assert update_data_with_extras["name"] == "Updated Folder"
        assert update_data_with_extras["custom_field"] == "custom_value"
        assert update_data_with_extras["another_field"] == 123
        
        # Test with None name
        none_update = Folder.update_data(name=None, custom_field="value")
        assert "name" not in none_update
        assert none_update["custom_field"] == "value"

    @pytest.mark.parametrize(
        "folder_params",
        [
            # Test with minimal parameters
            {"name": "Test Folder", "space_id": "space123"},
            # Test with custom parameters
            {
                "name": "Custom Folder", 
                "space_id": "space456", 
                "custom_field": "custom_value",
                "extra_data": {"key": "value"}
            }
        ],
    )
    def test_folder_initial(self, folder_params):
        """Test Folder initial method with various parameters."""
        folder = Folder.initial(**folder_params)
        
        # Check all parameters were correctly set
        for key, value in folder_params.items():
            assert getattr(folder, key) == value

    @pytest.mark.parametrize(
        "update_params, expected_data",
        [
            (
                {"name": "Updated List", "content": "Updated description"},
                {"name": "Updated List", "content": "Updated description"}
            ),
            (
                {"name": "Priority List", "priority": 1, "assignee": "user123"},
                {"name": "Priority List", "priority": 1, "assignee": "user123"}
            ),
            (
                {
                    "due_date": 1640995200, 
                    "due_date_time": True, 
                    "start_date": 1640908800, 
                    "start_date_time": False
                },
                {
                    "due_date": 1640995200, 
                    "due_date_time": True, 
                    "start_date": 1640908800, 
                    "start_date_time": False
                }
            ),
            (
                {"status": "in progress", "custom_field": "custom_value"},
                {"status": "in progress", "custom_field": "custom_value"}
            ),
        ],
    )
    def test_list_update_data(self, update_params, expected_data):
        """Test ClickUpList update_data method with various parameters."""
        update_data = ClickUpList.update_data(**update_params)
        
        # Check all parameters were correctly included
        for key, value in expected_data.items():
            assert update_data[key] == value
            
        # Check None values are excluded
        none_update = ClickUpList.update_data(name=None, content="content", status=None)
        assert "name" not in none_update
        assert none_update["content"] == "content"
        assert "status" not in none_update

    def test_list_extract_create_data(self):
        """Test ClickUpList extract_create_data method."""
        # Test with folder_id
        list_folder = ClickUpList.create_request(
            name="Folder List",
            folder_id="folder123",
            content="List description",
            due_date=1640995200,
            priority=1
        )
        create_data_folder = list_folder.extract_create_data()
        assert create_data_folder["name"] == "Folder List"
        assert create_data_folder["content"] == "List description"
        assert create_data_folder["due_date"] == 1640995200
        assert create_data_folder["priority"] == 1
        
        # Test with space_id
        list_space = ClickUpList.create_request(
            name="Space List",
            space_id="space123",
            content="List description",
            assignee="user123",
            status="in progress"
        )
        create_data_space = list_space.extract_create_data()
        assert create_data_space["name"] == "Space List"
        assert create_data_space["content"] == "List description"
        assert create_data_space["assignee"] == "user123"
        assert create_data_space["status"] == "in progress"


class TestTaskModels:
    """Test Task model."""

    def test_extract_task_from_response(self):
        """Test extracting task from API response."""
        response_data = {
            "id": "task123",
            "name": "Test Task",
            "description": "Task description",
            "status": {"status": "in progress", "color": "#FFFF00"},
            "priority": 1,  # Using integer instead of dict for priority
            "due_date": "1567780450202",
            "start_date": "1567780450202",
            "time_estimate": 8640000,
            "time_spent": 0,
            "list": {"id": "list123"}  # Adding list to avoid validation errors
        }
        
        # Using the correct method name from the Task model
        task = Task.extract_task_from_response(response_data)
        
        assert task.task_id == "task123"
        assert task.name == "Test Task"
        assert task.description == "Task description"
        # Use direct attribute access or string check since status might be a string in some cases
        if isinstance(task.status, dict):
            assert task.status.get("status") == "in progress"
        else:
            assert "in progress" in str(task.status)
        assert task.priority == 1  # Checking priority as integer

    def test_extract_list_tasks_response(self):
        """Test extracting list of tasks from API response."""
        response_data = {
            "tasks": [
                {
                    "id": "task1",
                    "name": "Test Task 1",
                    "status": {"status": "in progress", "color": "#FFCC00"},
                    "priority": 1,
                    "list": {"id": "list123"}  # Adding list to avoid validation errors
                },
                {
                    "id": "task2",
                    "name": "Test Task 2",
                    "status": {"status": "done", "color": "#00FF00"},
                    "priority": 3,
                    "list": {"id": "list456"}  # Adding list to avoid validation errors
                }
            ]
        }
        
        # Using individual extraction since there's no bulk extraction method
        tasks = []
        for task_data in response_data.get("tasks", []):
            tasks.append(Task.extract_task_from_response(task_data))
        
        assert len(tasks) == 2
        assert tasks[0].task_id == "task1"  # Using task_id instead of id
        assert tasks[0].name == "Test Task 1"
        assert tasks[1].task_id == "task2"  # Using task_id instead of id
        assert tasks[1].name == "Test Task 2"

    @pytest.mark.parametrize(
        "params, expected_attrs",
        [
            (
                {"list_id": "list123", "include_closed": True, "subtasks": True},
                {"include_closed": True, "subtasks": True}
            ),
            (
                {"list_id": "list123", "include_closed": False, "subtasks": False},
                {"include_closed": False, "subtasks": False}
            ),
            (
                {"list_id": "list123", "page": 2, "order_by": "updated"},
                {"page": 2, "order_by": "updated"}
            )
        ],
    )
    def test_extract_list_params(self, params, expected_attrs):
        """Test extracting list parameters."""
        task = Task.list_request(**params)
        extracted_params = task.extract_list_params()
        
        # List ID is used internally but not included in the extracted params
        # So we verify only the expected parameters that should be in the result
        for key, expected_value in expected_attrs.items():
            assert key in extracted_params
            assert extracted_params[key] == expected_value

    def test_task_extract_create_data(self):
        """Test task extract_create_data method."""
        task_data = {
            "name": "Task 1",
            "list_id": "list123",
            "description": "Task description",
            "status": "in progress",
            "priority": 2,
        }
        task = Task.create_request(**task_data)  # Use create_request factory method
        create_data = task.extract_create_data()
        
        # Check that all expected attributes are in the create data
        for key, value in task_data.items():
            # list_id might not be directly in create_data but should be accessible
            if key != "list_id":
                assert key in create_data
                assert create_data[key] == value
        
        # Basic fields expected in all create requests
        assert "notify_all" in create_data
        assert "check_required_custom_fields" in create_data

    def test_task_extract_update_data(self):
        """Test task extract_update_data method."""
        update_data = {
            "task_id": "task123",
            "name": "Updated Task",
            "description": "New description",
            "status": "done",
            "priority": 3,
            "due_date": 1567780450202,
        }
        task = Task.update_request(**update_data)  # Use update_request factory method
        extracted_data = task.extract_update_data()
        
        # Check that all expected attributes are in the update data
        for key, expected_value in update_data.items():
            # task_id is not included in update data
            if key != "task_id":
                assert key in extracted_data
                assert extracted_data[key] == expected_value


class TestResponseModels:
    """Test response models."""

    @pytest.mark.parametrize(
        "list_data, expected_attrs",
        [
            (
                # Minimal list data with required space_id
                {
                    "id": "123",
                    "name": "Test List",
                    "orderindex": "0",  # String instead of int
                    "content": "",
                    "status": "",  # Empty string instead of None
                    "date_created": "1567780450202",
                    "date_updated": "1567780450202",
                    "space": {"id": "space123"},
                    "folder": None,  # Some lists might not have a folder
                    "space_id": "space123"  # Adding space_id to satisfy validation
                },
                {
                    "id": "123",
                    "name": "Test List"
                }
            ),
            (
                # Full list data with required folder_id
                {
                    "id": "456",
                    "name": "Complete List",
                    "content": "List description",
                    "status": "active",  # String status instead of dict
                    "orderindex": "1",  # String instead of int
                    "date_created": "1567780450202",
                    "date_updated": "1567780450202",
                    "folder": {
                        "id": "folder123",
                        "name": "Parent Folder",
                        "hidden": False,
                        "access": True
                    },
                    "folder_id": "folder123",  # Adding folder_id to satisfy validation
                    "space": {
                        "id": "space123",
                        "name": "Parent Space"
                    },
                    "task_count": 5
                },
                {
                    "id": "456",
                    "name": "Complete List",
                    "content": "List description"
                }
            )
        ],
    )
    def test_clickup_list(self, list_data, expected_attrs):
        """Test ClickUpList response model."""
        from clickup_mcp.models import ClickUpList  # Import the correct model
        
        # Using model_validate to create from dictionary
        list_response = ClickUpList.model_validate(list_data)
        
        # Check attributes
        for attr_name, expected_value in expected_attrs.items():
            assert getattr(list_response, attr_name) == expected_value
        
        # Check serialization
        serialized = list_response.model_dump()
        assert serialized["id"] == list_data["id"]
        assert serialized["name"] == list_data["name"]


class TestUserModel:
    """Test User domain model."""

    def test_user_model_methods(self):
        """Test User domain model methods."""
        # Test initial method
        user = User.initial()
        assert isinstance(user, User)
        
        # Test get_request method
        user_req = User.get_request()
        assert isinstance(user_req, User)
        
        # Test model serialization
        serialized = user_req.model_dump()
        assert isinstance(serialized, dict)


class TestEdgeCases:
    """Test edge cases for models."""

    @pytest.mark.parametrize(
        "model_class, method_args, should_raise, error_msg",
        [
            (
                Space,
                {"name": "Test Space", "team_id": "team123"},  # Added team_id to make it valid
                False,
                "team_id is required when creating a space"
            ),
            (
                Folder,
                {"name": "Test Folder", "space_id": "space123"},  # Added space_id to make it valid
                False,
                "space_id is required when creating a folder"
            ),
            (
                ClickUpList,
                {"name": "Test List", "folder_id": "folder123"},  # Added folder_id to make it valid
                False,
                "Either folder_id or space_id must be provided when creating a list"
            ),
        ],
    )
    def test_model_validation(self, model_class, method_args, should_raise, error_msg):
        """Test model validation for edge cases."""
        # Models require their validation fields at initialization time
        model = model_class(**method_args)
        
        # Test that the model was created successfully with required fields
        assert model.name == method_args["name"]
        
        # Test we can access other added fields
        if "team_id" in method_args:
            assert model.team_id == method_args["team_id"]
        if "space_id" in method_args:
            assert model.space_id == method_args["space_id"]
        if "folder_id" in method_args:
            assert model.folder_id == method_args["folder_id"]

    @pytest.mark.parametrize(
        "model_class, invalid_args, error_msg",
        [
            (
                Space,
                {"name": "Test Space"},  # Missing team_id
                "team_id is required when creating a space"
            ),
            (
                Folder,
                {"name": "Test Folder"},  # Missing space_id
                "space_id is required when creating a folder"
            ),
            (
                ClickUpList,
                {"name": "Test List"},  # Missing folder_id or space_id
                "Either folder_id or space_id must be provided when creating a list"
            ),
        ],
    )
    def test_model_validation_errors(self, model_class, invalid_args, error_msg):
        """Test model validation errors."""
        # Since these models validate at initialization time, 
        # attempting to create them with missing required fields should fail
        with pytest.raises(ValidationError):
            model = model_class(**invalid_args)

    @pytest.mark.parametrize(
        "task_attrs, expected_params",
        [
            # Test custom fields extraction in list params
            (
                {
                    "list_id": "list123",
                    "custom_fields": [
                        {"id": "field1", "value": "value1"},
                        {"id": "field2", "value": 42}
                    ]
                },
                {
                    # list_id is stored internally but not included in extracted params
                    # test only the other parameters
                    "custom_fields": [
                        {"id": "field1", "value": "value1"},
                        {"id": "field2", "value": 42}
                    ]
                }
            ),
            # Test time-related parameters
            (
                {
                    "list_id": "list123",
                    "date_created_gt": 1640995200000,
                    "date_created_lt": 1641081600000,
                    "date_updated_gt": 1641168000000,
                    "date_updated_lt": 1641254400000
                },
                {
                    # list_id is stored internally but not included in extracted params
                    "date_created_gt": 1640995200000,
                    "date_created_lt": 1641081600000,
                    "date_updated_gt": 1641168000000,
                    "date_updated_lt": 1641254400000
                }
            ),
            # Test assignees and tags
            (
                {
                    "list_id": "list123",
                    "assignees": ["user1", "user2"],
                    "tags": ["bug", "feature"]
                },
                {
                    # list_id is stored internally but not included in extracted params
                    "assignees[]": ["user1", "user2"],
                    "tags[]": ["bug", "feature"]
                }
            )
        ],
    )
    def test_task_specialized_param_extraction(self, task_attrs, expected_params):
        """Test specialized parameter extraction in Task list_request."""
        task = Task.list_request(**task_attrs)
        params = task.extract_list_params()
    
        # Check for the expected params instead of looking for list_id
        # list_id is used internally but not included in the extracted params
        for key, expected_value in expected_params.items():
            assert key in params
            
            # For complex objects like lists, we need to check each item
            if isinstance(expected_value, list):
                assert params[key] == expected_value
            else:
                assert params[key] == expected_value
