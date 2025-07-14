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
    ClickUpTask,
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
            ClickUpListDomain(name="Test List").validate_list_request()

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


class TestTaskModels:
    """Test task-related models."""

    def test_custom_field(self):
        """Test CustomField model."""
        field = CustomField(id="field123", name="Priority", type="drop_down", value="high")
        assert field.id == "field123"
        assert field.name == "Priority"
        assert field.type == "drop_down"
        assert field.value == "high"

        # Test validation
        with pytest.raises(ValidationError):
            CustomField(name="Priority", type="drop_down", value="high")  # Missing id


class TestResponseModels:
    """Test response models."""

    def test_clickup_user(self):
        """Test ClickUpUser model."""
        user = ClickUpUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            color="#FF0000",
            profile_picture="https://example.com/avatar.jpg",
            initials="TU",
            week_start_day=1,
            global_font_support=True,
            timezone="America/New_York",
        )
        assert user.id == "user123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.color == "#FF0000"
        assert user.profile_picture == "https://example.com/avatar.jpg"
        assert user.initials == "TU"
        assert user.week_start_day == 1
        assert user.global_font_support is True
        assert user.timezone == "America/New_York"

    def test_clickup_team(self):
        """Test ClickUpTeam model."""
        team = ClickUpTeam(
            id="team123",
            name="Test Team",
            color="#00FF00",
            avatar="https://example.com/team-avatar.jpg",
            members=[
                ClickUpUser(id="user1", username="user1", email="user1@example.com"),
                ClickUpUser(id="user2", username="user2", email="user2@example.com"),
            ],
        )
        assert team.id == "team123"
        assert team.name == "Test Team"
        assert team.color == "#00FF00"
        assert team.avatar == "https://example.com/team-avatar.jpg"
        assert len(team.members) == 2
        assert team.members[0].id == "user1"
        assert team.members[1].id == "user2"

    def test_clickup_space(self):
        """Test ClickUpSpace model."""
        space = ClickUpSpace(
            id="space123",
            name="Test Space",
            private=True,
            statuses=[{"id": "status1", "status": "Open"}, {"id": "status2", "status": "Closed"}],
            multiple_assignees=True,
            features={"due_dates": True, "time_tracking": True},
        )
        assert space.id == "space123"
        assert space.name == "Test Space"
        assert space.private is True
        assert len(space.statuses) == 2
        assert space.multiple_assignees is True
        assert space.features["due_dates"] is True

    def test_clickup_folder(self):
        """Test ClickUpFolder model."""
        folder = ClickUpFolder(
            id="folder123",
            name="Test Folder",
            orderindex=1,
            override_statuses=False,
            hidden=False,
            space={"id": "space123", "name": "Test Space"},
            task_count=42,
        )
        assert folder.id == "folder123"
        assert folder.name == "Test Folder"
        assert folder.orderindex == 1
        assert folder.override_statuses is False
        assert folder.hidden is False
        assert folder.space["id"] == "space123"
        assert folder.task_count == 42

    def test_clickup_list(self):
        """Test ClickUpList model."""
        list_model = ClickUpList(
            id="list123",
            name="Test List",
            content="List description",
            orderindex=2,
            status="active",
            priority=3,
            assignee="user123",
            task_count=10,
            due_date=1641081600000,
            start_date=1640995200000,
            folder={"id": "folder123", "name": "Test Folder"},
            space={"id": "space123", "name": "Test Space"},
            permission_level="create",
            # Add required fields for validation
            folder_id="folder123"
        )
        assert list_model.id == "list123"
        assert list_model.name == "Test List"
        assert list_model.content == "List description"
        assert list_model.orderindex == 2
        assert list_model.status == "active"
        assert list_model.priority == 3
        assert list_model.assignee == "user123"
        assert list_model.task_count == 10
        assert list_model.due_date == 1641081600000
        assert list_model.start_date == 1640995200000
        assert list_model.folder["id"] == "folder123"
        assert list_model.space["id"] == "space123"
        assert list_model.permission_level == "create"

    def test_clickup_task(self):
        """Test ClickUpTask model."""
        task = ClickUpTask(
            id="task123",
            name="Test Task",
            status={"status": "open", "color": "#FF0000"},
            # Use integer value for date_created and date_updated since the model expects integers
            date_created=1609459200000,
            date_updated=1609545600000,
            date_closed=None,
            creator={"id": "user123", "username": "testuser", "email": "test@example.com"},
            assignees=[
                {"id": "user123", "username": "user1", "email": "user1@example.com"},
                {"id": "user456", "username": "user2", "email": "user2@example.com"}
            ],
            watchers=[{"id": "user789", "username": "watcher", "email": "watcher@example.com"}],
            list={"id": "list123"},
            folder={"id": "folder123"},
            space={"id": "space123"},
            url="https://app.clickup.com/t/task123",
            custom_fields=[{"id": "field123", "name": "Priority", "type": "drop_down", "value": "high"}],
            priority={"priority": "high", "color": "#FF0000"},
        )
        assert task.id == "task123"
        assert task.name == "Test Task"
        assert task.status["status"] == "open"
        assert task.date_created == 1609459200000
        assert task.date_updated == 1609545600000
        assert task.date_closed is None
        # Access creator properties based on actual object structure
        assert task.creator.id == "user123" 
        assert len(task.assignees) == 2
        assert task.assignees[0].id == "user123"
        assert task.assignees[1].id == "user456"
        assert len(task.watchers) == 1
        assert task.watchers[0].id == "user789"
        assert task.list["id"] == "list123"
        assert task.folder["id"] == "folder123"
        assert task.space["id"] == "space123"
        assert task.url == "https://app.clickup.com/t/task123"
        assert len(task.custom_fields) == 1
        assert task.custom_fields[0].id == "field123"
        assert task.custom_fields[0].name == "Priority"
        assert task.custom_fields[0].value == "high"
        assert task.priority["priority"] == "high"
        assert task.priority["color"] == "#FF0000"
