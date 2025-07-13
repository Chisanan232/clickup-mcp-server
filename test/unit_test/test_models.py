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

    # Task models
    CustomField,

    # Response models
    ClickUpUser,
    ClickUpTeam,
    ClickUpSpace,
    ClickUpFolder,
    ClickUpList,
    ClickUpTask,
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


class TestTaskModels:
    """Test task-related models."""

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
