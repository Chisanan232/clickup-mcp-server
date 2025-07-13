"""
Unit tests for ClickUp models.

This module tests all Pydantic models used in the ClickUp MCP server,
including validation, serialization, and helper functions.
"""

import pytest
from pydantic import ValidationError
from typing import Any, Dict, List

from clickup_mcp.models import (
    # Base models
    ClickUpBaseModel,
    snake_to_camel,
    
    # Team models
    TeamRequest,
    TeamMembersRequest,
    
    # Space models
    SpaceRequest,
    SpacesRequest,
    CreateSpaceRequest,
    
    # Folder models
    FolderRequest,
    FoldersRequest,
    CreateFolderRequest,
    
    # List models
    ListRequest,
    ListsRequest,
    CreateListRequest,
    
    # Task models
    TaskRequest,
    TasksRequest,
    CreateTaskRequest,
    UpdateTaskRequest,
    DeleteTaskRequest,
    CustomField,
    
    # User models
    UserRequest,
    
    # Response models
    ClickUpUser,
    ClickUpTeam,
    ClickUpSpace,
    ClickUpFolder,
    ClickUpList,
    ClickUpTask,
    
    # Helper functions
    extract_create_task_data,
    extract_update_task_data,
    extract_tasks_params,
    extract_create_space_data,
    extract_create_list_data,
)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_snake_to_camel(self):
        """Test snake_case to camelCase conversion."""
        assert snake_to_camel("snake_case") == "snakeCase"
        assert snake_to_camel("single") == "single"
        assert snake_to_camel("multiple_word_test") == "multipleWordTest"
        assert snake_to_camel("") == ""
        assert snake_to_camel("a_b_c_d") == "aBCD"


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


class TestTeamModels:
    """Test team-related models."""
    
    def test_team_request(self):
        """Test TeamRequest model."""
        request = TeamRequest(team_id="123")
        assert request.team_id == "123"
        
        # Test validation
        with pytest.raises(ValidationError):
            TeamRequest()
    
    def test_team_members_request(self):
        """Test TeamMembersRequest model."""
        request = TeamMembersRequest(team_id="team123")
        assert request.team_id == "team123"
        
        # Test validation
        with pytest.raises(ValidationError):
            TeamMembersRequest()


class TestSpaceModels:
    """Test space-related models."""
    
    def test_space_request(self):
        """Test SpaceRequest model."""
        request = SpaceRequest(space_id="space123")
        assert request.space_id == "space123"
        
        # Test validation
        with pytest.raises(ValidationError):
            SpaceRequest()
    
    def test_spaces_request(self):
        """Test SpacesRequest model."""
        request = SpacesRequest(team_id="team123")
        assert request.team_id == "team123"
        
        # Test validation
        with pytest.raises(ValidationError):
            SpacesRequest()
    
    def test_create_space_request(self):
        """Test CreateSpaceRequest model."""
        # Minimal request
        request = CreateSpaceRequest(team_id="team123", name="Test Space")
        assert request.team_id == "team123"
        assert request.name == "Test Space"
        assert request.description is None
        assert request.multiple_assignees is None
        assert request.features is None
        assert request.private is None
        
        # Full request
        features = {"time_tracking": True, "custom_fields": True}
        request = CreateSpaceRequest(
            team_id="team123",
            name="Test Space",
            description="A test space",
            multiple_assignees=True,
            features=features,
            private=False
        )
        assert request.team_id == "team123"
        assert request.name == "Test Space"
        assert request.description == "A test space"
        assert request.multiple_assignees is True
        assert request.features == features
        assert request.private is False
        
        # Test validation
        with pytest.raises(ValidationError):
            CreateSpaceRequest(team_id="team123")  # Missing name
        
        with pytest.raises(ValidationError):
            CreateSpaceRequest(name="Test Space")  # Missing team_id


class TestFolderModels:
    """Test folder-related models."""
    
    def test_folder_request(self):
        """Test FolderRequest model."""
        request = FolderRequest(folder_id="folder123")
        assert request.folder_id == "folder123"
        
        # Test validation
        with pytest.raises(ValidationError):
            FolderRequest()
    
    def test_folders_request(self):
        """Test FoldersRequest model."""
        request = FoldersRequest(space_id="space123")
        assert request.space_id == "space123"
        
        # Test validation
        with pytest.raises(ValidationError):
            FoldersRequest()
    
    def test_create_folder_request(self):
        """Test CreateFolderRequest model."""
        request = CreateFolderRequest(space_id="space123", name="Test Folder")
        assert request.space_id == "space123"
        assert request.name == "Test Folder"
        
        # Test validation
        with pytest.raises(ValidationError):
            CreateFolderRequest(space_id="space123")  # Missing name
        
        with pytest.raises(ValidationError):
            CreateFolderRequest(name="Test Folder")  # Missing space_id


class TestListModels:
    """Test list-related models."""
    
    def test_list_request(self):
        """Test ListRequest model."""
        request = ListRequest(list_id="list123")
        assert request.list_id == "list123"
        
        # Test validation
        with pytest.raises(ValidationError):
            ListRequest()
    
    def test_lists_request(self):
        """Test ListsRequest model."""
        # Test with folder_id
        request = ListsRequest(folder_id="folder123")
        assert request.folder_id == "folder123"
        assert request.space_id is None
        
        # Test with space_id
        request = ListsRequest(space_id="space123")
        assert request.space_id == "space123"
        assert request.folder_id is None
        
        # Test with both
        request = ListsRequest(folder_id="folder123", space_id="space123")
        assert request.folder_id == "folder123"
        assert request.space_id == "space123"
        
        # Test validation - both missing
        with pytest.raises(ValidationError):
            ListsRequest()
    
    def test_create_list_request(self):
        """Test CreateListRequest model."""
        # Minimal request with folder_id
        request = CreateListRequest(name="Test List", folder_id="folder123")
        assert request.name == "Test List"
        assert request.folder_id == "folder123"
        assert request.space_id is None
        
        # Minimal request with space_id
        request = CreateListRequest(name="Test List", space_id="space123")
        assert request.name == "Test List"
        assert request.space_id == "space123"
        assert request.folder_id is None
        
        # Full request
        request = CreateListRequest(
            name="Test List",
            folder_id="folder123",
            content="List description",
            due_date=1640995200,
            due_date_time=True,
            priority=1,
            assignee="user123",
            status="open"
        )
        assert request.name == "Test List"
        assert request.folder_id == "folder123"
        assert request.content == "List description"
        assert request.due_date == 1640995200
        assert request.due_date_time is True
        assert request.priority == 1
        assert request.assignee == "user123"
        assert request.status == "open"
        
        # Test validation
        with pytest.raises(ValidationError):
            CreateListRequest(name="Test List")  # Missing both folder_id and space_id


class TestTaskModels:
    """Test task-related models."""
    
    def test_task_request(self):
        """Test TaskRequest model."""
        request = TaskRequest(task_id="task123")
        assert request.task_id == "task123"
        assert request.custom_task_ids is False
        assert request.team_id is None
        
        # Full request
        request = TaskRequest(
            task_id="task123",
            custom_task_ids=True,
            team_id="team123"
        )
        assert request.task_id == "task123"
        assert request.custom_task_ids is True
        assert request.team_id == "team123"
        
        # Test validation
        with pytest.raises(ValidationError):
            TaskRequest()  # Missing task_id
    
    def test_tasks_request(self):
        """Test TasksRequest model."""
        # Minimal request
        request = TasksRequest(list_id="list123")
        assert request.list_id == "list123"
        assert request.page == 0
        assert request.order_by == "created"
        assert request.reverse is False
        assert request.subtasks is False
        assert request.include_closed is False
        
        # Full request
        request = TasksRequest(
            list_id="list123",
            page=1,
            order_by="updated",
            reverse=True,
            subtasks=True,
            statuses=["open", "in progress"],
            include_closed=True,
            assignees=["user1", "user2"],
            tags=["tag1", "tag2"],
            due_date_gt=1640995200,
            due_date_lt=1641081600,
            date_created_gt=1640995200,
            date_created_lt=1641081600,
            date_updated_gt=1640995200,
            date_updated_lt=1641081600,
            custom_fields=[{"id": "field1", "value": "value1"}]
        )
        assert request.list_id == "list123"
        assert request.page == 1
        assert request.order_by == "updated"
        assert request.reverse is True
        assert request.subtasks is True
        assert request.statuses == ["open", "in progress"]
        assert request.include_closed is True
        assert request.assignees == ["user1", "user2"]
        assert request.tags == ["tag1", "tag2"]
        assert request.due_date_gt == 1640995200
        assert request.due_date_lt == 1641081600
        assert request.date_created_gt == 1640995200
        assert request.date_created_lt == 1641081600
        assert request.date_updated_gt == 1640995200
        assert request.date_updated_lt == 1641081600
        assert request.custom_fields == [{"id": "field1", "value": "value1"}]
        
        # Test validation
        with pytest.raises(ValidationError):
            TasksRequest()  # Missing list_id
    
    def test_custom_field(self):
        """Test CustomField model."""
        field = CustomField(
            id="field123",
            name="Priority",
            type="drop_down",
            value="high"
        )
        assert field.id == "field123"
        assert field.name == "Priority"
        assert field.type == "drop_down"
        assert field.value == "high"
        
        # Test validation
        with pytest.raises(ValidationError):
            CustomField(name="Priority", type="drop_down", value="high")  # Missing id
    
    def test_create_task_request(self):
        """Test CreateTaskRequest model."""
        # Minimal request
        request = CreateTaskRequest(list_id="list123", name="Test Task")
        assert request.list_id == "list123"
        assert request.name == "Test Task"
        assert request.description is None
        assert request.assignees is None
        assert request.priority is None
        assert request.due_date_time is False
        assert request.start_date_time is False
        assert request.notify_all is True
        assert request.check_required_custom_fields is True
        
        # Full request
        custom_fields = [
            CustomField(id="field1", name="Priority", type="drop_down", value="high"),
            CustomField(id="field2", name="Department", type="text", value="Engineering")
        ]
        request = CreateTaskRequest(
            list_id="list123",
            name="Test Task",
            description="A test task",
            assignees=["user1", "user2"],
            tags=["tag1", "tag2"],
            status="open",
            priority=1,
            due_date=1640995200,
            due_date_time=True,
            time_estimate=3600000,
            start_date=1640908800,
            start_date_time=True,
            notify_all=False,
            parent="parent123",
            links_to="linked123",
            check_required_custom_fields=False,
            custom_fields=custom_fields
        )
        assert request.list_id == "list123"
        assert request.name == "Test Task"
        assert request.description == "A test task"
        assert request.assignees == ["user1", "user2"]
        assert request.tags == ["tag1", "tag2"]
        assert request.status == "open"
        assert request.priority == 1
        assert request.due_date == 1640995200
        assert request.due_date_time is True
        assert request.time_estimate == 3600000
        assert request.start_date == 1640908800
        assert request.start_date_time is True
        assert request.notify_all is False
        assert request.parent == "parent123"
        assert request.links_to == "linked123"
        assert request.check_required_custom_fields is False
        assert request.custom_fields == custom_fields
        
        # Test priority validation
        with pytest.raises(ValidationError):
            CreateTaskRequest(list_id="list123", name="Test Task", priority=5)  # Invalid priority
        
        # Priority 0 is valid (no priority)
        request = CreateTaskRequest(list_id="list123", name="Test Task", priority=0)
        assert request.priority == 0
        
        # Test validation
        with pytest.raises(ValidationError):
            CreateTaskRequest(list_id="list123")  # Missing name
        
        with pytest.raises(ValidationError):
            CreateTaskRequest(name="Test Task")  # Missing list_id
    
    def test_update_task_request(self):
        """Test UpdateTaskRequest model."""
        # Minimal request
        request = UpdateTaskRequest(task_id="task123")
        assert request.task_id == "task123"
        assert request.name is None
        assert request.description is None
        assert request.notify_all is True
        assert request.check_required_custom_fields is True
        
        # Full request
        custom_fields = [
            CustomField(id="field1", name="Priority", type="drop_down", value="high")
        ]
        request = UpdateTaskRequest(
            task_id="task123",
            name="Updated Task",
            description="Updated description",
            assignees=["user1"],
            tags=["tag1"],
            status="in progress",
            priority=2,
            due_date=1640995200,
            due_date_time=True,
            time_estimate=7200000,
            start_date=1640908800,
            start_date_time=True,
            notify_all=False,
            parent="parent123",
            links_to="linked123",
            check_required_custom_fields=False,
            custom_fields=custom_fields
        )
        assert request.task_id == "task123"
        assert request.name == "Updated Task"
        assert request.description == "Updated description"
        assert request.assignees == ["user1"]
        assert request.tags == ["tag1"]
        assert request.status == "in progress"
        assert request.priority == 2
        assert request.due_date == 1640995200
        assert request.due_date_time is True
        assert request.time_estimate == 7200000
        assert request.start_date == 1640908800
        assert request.start_date_time is True
        assert request.notify_all is False
        assert request.parent == "parent123"
        assert request.links_to == "linked123"
        assert request.check_required_custom_fields is False
        assert request.custom_fields == custom_fields
        
        # Test priority validation
        with pytest.raises(ValidationError):
            UpdateTaskRequest(task_id="task123", priority=5)  # Invalid priority
        
        # Priority 0 is valid (no priority)
        request = UpdateTaskRequest(task_id="task123", priority=0)
        assert request.priority == 0
        
        # Test validation
        with pytest.raises(ValidationError):
            UpdateTaskRequest()  # Missing task_id
    
    def test_delete_task_request(self):
        """Test DeleteTaskRequest model."""
        # Minimal request
        request = DeleteTaskRequest(task_id="task123")
        assert request.task_id == "task123"
        assert request.custom_task_ids is False
        assert request.team_id is None
        
        # Full request
        request = DeleteTaskRequest(
            task_id="task123",
            custom_task_ids=True,
            team_id="team123"
        )
        assert request.task_id == "task123"
        assert request.custom_task_ids is True
        assert request.team_id == "team123"
        
        # Test validation
        with pytest.raises(ValidationError):
            DeleteTaskRequest()  # Missing task_id


class TestUserModels:
    """Test user-related models."""
    
    def test_user_request(self):
        """Test UserRequest model."""
        request = UserRequest()
        # No fields required for user request
        assert request is not None


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
            timezone="America/New_York"
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
        
        # Test minimal user
        user = ClickUpUser(id="user123", username="testuser", email="test@example.com")
        assert user.id == "user123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.color is None
        assert user.profile_picture is None
    
    def test_clickup_team(self):
        """Test ClickUpTeam model."""
        members = [
            ClickUpUser(id="user1", username="user1", email="user1@example.com"),
            ClickUpUser(id="user2", username="user2", email="user2@example.com")
        ]
        team = ClickUpTeam(
            id="team123",
            name="Test Team",
            color="#00FF00",
            avatar="https://example.com/team.jpg",
            members=members
        )
        assert team.id == "team123"
        assert team.name == "Test Team"
        assert team.color == "#00FF00"
        assert team.avatar == "https://example.com/team.jpg"
        assert len(team.members) == 2
        assert team.members[0].id == "user1"
        assert team.members[1].id == "user2"
    
    def test_clickup_space(self):
        """Test ClickUpSpace model."""
        features = {"time_tracking": True, "custom_fields": True}
        statuses = [{"status": "open", "color": "#FF0000"}]
        space = ClickUpSpace(
            id="space123",
            name="Test Space",
            color="#0000FF",
            private=False,
            avatar="https://example.com/space.jpg",
            admin_can_manage=True,
            statuses=statuses,
            multiple_assignees=True,
            features=features
        )
        assert space.id == "space123"
        assert space.name == "Test Space"
        assert space.color == "#0000FF"
        assert space.private is False
        assert space.avatar == "https://example.com/space.jpg"
        assert space.admin_can_manage is True
        assert space.statuses == statuses
        assert space.multiple_assignees is True
        assert space.features == features
    
    def test_clickup_task(self):
        """Test ClickUpTask model."""
        creator = ClickUpUser(id="user1", username="creator", email="creator@example.com")
        assignees = [ClickUpUser(id="user2", username="assignee", email="assignee@example.com")]
        custom_fields = [
            CustomField(id="field1", name="Priority", type="drop_down", value="high")
        ]
        
        task = ClickUpTask(
            id="task123",
            name="Test Task",
            text_content="Task content",
            description="Task description",
            status={"status": "open", "color": "#FF0000"},
            orderindex="1",
            date_created=1640995200,
            date_updated=1640995300,
            archived=False,
            creator=creator,
            assignees=assignees,
            tags=[{"name": "important"}],
            priority={"priority": "high", "color": "#FF0000"},
            due_date=1641081600,
            start_date=1640908800,
            time_estimate=3600000,
            custom_fields=custom_fields,
            team_id="team123",
            url="https://app.clickup.com/t/task123"
        )
        assert task.id == "task123"
        assert task.name == "Test Task"
        assert task.text_content == "Task content"
        assert task.description == "Task description"
        assert task.status == {"status": "open", "color": "#FF0000"}
        assert task.orderindex == "1"
        assert task.date_created == 1640995200
        assert task.date_updated == 1640995300
        assert task.archived is False
        assert task.creator == creator
        assert task.assignees == assignees
        assert task.tags == [{"name": "important"}]
        assert task.priority == {"priority": "high", "color": "#FF0000"}
        assert task.due_date == 1641081600
        assert task.start_date == 1640908800
        assert task.time_estimate == 3600000
        assert task.custom_fields == custom_fields
        assert task.team_id == "team123"
        assert task.url == "https://app.clickup.com/t/task123"


class TestHelperFunctions:
    """Test helper functions for data extraction."""
    
    def test_extract_create_task_data(self):
        """Test extract_create_task_data function."""
        # Minimal request
        request = CreateTaskRequest(list_id="list123", name="Test Task")
        data = extract_create_task_data(request)
        assert data == {
            "name": "Test Task",
            "notify_all": True,
            "check_required_custom_fields": True
        }
        
        # Full request
        custom_fields = [
            CustomField(id="field1", name="Priority", type="drop_down", value="high")
        ]
        request = CreateTaskRequest(
            list_id="list123",
            name="Test Task",
            description="Task description",
            assignees=["user1", "user2"],
            tags=["tag1", "tag2"],
            status="open",
            priority=1,
            due_date=1640995200,
            due_date_time=True,
            time_estimate=3600000,
            start_date=1640908800,
            start_date_time=True,
            notify_all=False,
            parent="parent123",
            links_to="linked123",
            check_required_custom_fields=False,
            custom_fields=custom_fields
        )
        data = extract_create_task_data(request)
        
        expected_data = {
            "name": "Test Task",
            "description": "Task description",
            "assignees": ["user1", "user2"],
            "tags": ["tag1", "tag2"],
            "status": "open",
            "priority": 1,
            "due_date": 1640995200,
            "due_date_time": True,
            "time_estimate": 3600000,
            "start_date": 1640908800,
            "start_date_time": True,
            "notify_all": False,
            "parent": "parent123",
            "links_to": "linked123",
            "check_required_custom_fields": False,
            "custom_fields": [
                {"field_id": "field1", "value": "high"}
            ]
        }
        assert data == expected_data
    
    def test_extract_update_task_data(self):
        """Test extract_update_task_data function."""
        # Minimal request
        request = UpdateTaskRequest(task_id="task123")
        data = extract_update_task_data(request)
        assert data == {}
        
        # Full request
        custom_fields = [
            CustomField(id="field1", name="Priority", type="drop_down", value="high")
        ]
        request = UpdateTaskRequest(
            task_id="task123",
            name="Updated Task",
            description="Updated description",
            assignees=["user1"],
            tags=["tag1"],
            status="in progress",
            priority=2,
            due_date=1640995200,
            time_estimate=7200000,
            start_date=1640908800,
            custom_fields=custom_fields
        )
        data = extract_update_task_data(request)
        
        expected_data = {
            "name": "Updated Task",
            "description": "Updated description",
            "assignees": ["user1"],
            "tags": ["tag1"],
            "status": "in progress",
            "priority": 2,
            "due_date": 1640995200,
            "time_estimate": 7200000,
            "start_date": 1640908800,
            "custom_fields": [
                {"field_id": "field1", "value": "high"}
            ]
        }
        assert data == expected_data
    
    def test_extract_tasks_params(self):
        """Test extract_tasks_params function."""
        # Minimal request
        request = TasksRequest(list_id="list123")
        params = extract_tasks_params(request)
        
        expected_params = {
            "page": 0,
            "order_by": "created",
            "reverse": False,
            "subtasks": False,
            "include_closed": False
        }
        assert params == expected_params
        
        # Full request
        request = TasksRequest(
            list_id="list123",
            page=1,
            order_by="updated",
            reverse=True,
            subtasks=True,
            statuses=["open", "in progress"],
            include_closed=True,
            assignees=["user1", "user2"],
            tags=["tag1", "tag2"],
            due_date_gt=1640995200,
            due_date_lt=1641081600,
            date_created_gt=1640995200,
            date_created_lt=1641081600,
            date_updated_gt=1640995200,
            date_updated_lt=1641081600,
            custom_fields=[{"id": "field1", "value": "value1"}]
        )
        params = extract_tasks_params(request)
        
        expected_params = {
            "page": 1,
            "order_by": "updated",
            "reverse": True,
            "subtasks": True,
            "include_closed": True,
            "statuses[]": ["open", "in progress"],
            "assignees[]": ["user1", "user2"],
            "tags[]": ["tag1", "tag2"],
            "due_date_gt": 1640995200,
            "due_date_lt": 1641081600,
            "date_created_gt": 1640995200,
            "date_created_lt": 1641081600,
            "date_updated_gt": 1640995200,
            "date_updated_lt": 1641081600,
            "custom_fields": [{"id": "field1", "value": "value1"}]
        }
        assert params == expected_params
    
    def test_extract_create_space_data(self):
        """Test extract_create_space_data function."""
        # Minimal request
        request = CreateSpaceRequest(team_id="team123", name="Test Space")
        data = extract_create_space_data(request)
        assert data == {"name": "Test Space"}
        
        # Full request
        features = {"time_tracking": True, "custom_fields": True}
        request = CreateSpaceRequest(
            team_id="team123",
            name="Test Space",
            description="Space description",
            multiple_assignees=True,
            features=features,
            private=False
        )
        data = extract_create_space_data(request)
        
        expected_data = {
            "name": "Test Space",
            "description": "Space description",
            "multiple_assignees": True,
            "features": features,
            "private": False
        }
        assert data == expected_data
    
    def test_extract_create_list_data(self):
        """Test extract_create_list_data function."""
        # Minimal request
        request = CreateListRequest(name="Test List", folder_id="folder123")
        data = extract_create_list_data(request)
        assert data == {"name": "Test List"}
        
        # Full request
        request = CreateListRequest(
            name="Test List",
            folder_id="folder123",
            content="List description",
            due_date=1640995200,
            priority=1,
            assignee="user123",
            status="open"
        )
        data = extract_create_list_data(request)
        
        expected_data = {
            "name": "Test List",
            "content": "List description",
            "due_date": 1640995200,
            "priority": 1,
            "assignee": "user123",
            "status": "open"
        }
        assert data == expected_data
