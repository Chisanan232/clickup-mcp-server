"""
Unit tests for domain models.

This module contains tests for the domain models, focusing on their
validation logic, serialization, and other model-specific functionality.
"""

import pytest

from clickup_mcp.models.domain.space import ClickUpSpace


class TestClickUpSpaceModel:
    """Tests for the ClickUpSpace domain model."""

    def test_model_initialization(self):
        """Test that the ClickUpSpace model can be initialized with both id and space_id."""
        # Create with space_id directly
        space1 = ClickUpSpace(
            space_id="12345",
            name="Test Space",
            private=True,
            multiple_assignees=False
        )
        assert space1.space_id == "12345"
        assert space1.id == "12345"  # Should be accessible via property
        
        # Create with id alias
        space2 = ClickUpSpace(
            id="67890",
            name="Another Space",
            private=False,
            multiple_assignees=True
        )
        assert space2.space_id == "67890"
        assert space2.id == "67890"

    def test_model_dump_serialization_options(self):
        """Test that model_dump handles different serialization options correctly."""
        space = ClickUpSpace(
            id="123456",
            name="Test Space",
        )
        
        # Default serialization uses field names
        data = space.model_dump()
        assert "space_id" in data
        assert data["space_id"] == "123456"
        assert "id" not in data
        
        # Serialization with by_alias=True uses aliases
        data_with_alias = space.model_dump(by_alias=True)
        assert "id" in data_with_alias
        assert data_with_alias["id"] == "123456"
        assert "space_id" not in data_with_alias
        
        # Can access id via property for compatibility
        assert space.id == "123456"

    def test_model_dump_with_exclude(self):
        """Test model_dump with exclude parameter."""
        space = ClickUpSpace(
            id="123456",
            name="Test Space",
            team_id="team123",
        )
        
        # Standard serialization with exclude - exclude by field name
        data = space.model_dump(exclude={"space_id"})
        assert "space_id" not in data
        assert "id" not in data  # id is not included since we're excluding space_id
        
        # When using by_alias=True, we need to use the field name in exclude, not the alias name
        # This is Pydantic's behavior - exclude operates on internal field names
        data_with_alias = space.model_dump(by_alias=True, exclude={"space_id"})
        assert "id" not in data_with_alias  # 'id' is not present because we excluded 'space_id'
        assert "space_id" not in data_with_alias

    def test_model_dump_with_include(self):
        """Test model_dump with include parameter."""
        space = ClickUpSpace(
            id="123456",
            name="Test Space",
            team_id="team123",
        )
        
        # When only including name, id should not be present
        data = space.model_dump(include={"name"})
        assert "name" in data
        assert "space_id" not in data
        assert "id" not in data
        
        # When including space_id with default serialization
        data = space.model_dump(include={"space_id", "name"})
        assert "name" in data
        assert "space_id" in data
        assert "id" not in data
        
        # When using by_alias=True, we must use the field name in include, not the alias
        # This is Pydantic's behavior - include operates on internal field names
        data = space.model_dump(by_alias=True, include={"space_id", "name"})
        assert "name" in data
        assert "id" in data  # 'id' is present (as alias for space_id) because we included 'space_id'
        assert "space_id" not in data

    def test_model_dump_exclude_unset(self):
        """Test model_dump with exclude_unset parameter."""
        # Create with minimal fields
        space = ClickUpSpace(
            space_id="12345",
            name="Test Space"
        )
        
        # Dump with exclude_unset
        dumped_data = space.model_dump(exclude_unset=True)
        
        # Only explicitly set fields should be included
        assert "space_id" in dumped_data
        assert "name" in dumped_data
        
        # Default fields should be excluded
        # Note: Due to how Pydantic v2 works, this behavior might vary
        # so we'll need to verify the exact behavior
        
        # For alias serialization, use by_alias=True
        alias_data = space.model_dump(exclude_unset=True, by_alias=True)
        assert "id" in alias_data
        assert alias_data["id"] == "12345"

    def test_backward_compatibility_alias(self):
        """Test that the Space alias works for backward compatibility."""
        from clickup_mcp.models.domain.space import Space
        
        # Space should be the same class as ClickUpSpace
        assert Space is ClickUpSpace
        
        # Create a Space instance
        space = Space(
            space_id="12345",
            name="Test Space"
        )
        
        # Should work the same as ClickUpSpace
        assert space.space_id == "12345"
        assert space.id == "12345"
        
        # For alias serialization, use by_alias=True
        dumped_data = space.model_dump(by_alias=True)
        assert "id" in dumped_data
        assert dumped_data["id"] == "12345"

    def test_create_from_api_response(self):
        """Test creating a ClickUpSpace from an API response."""
        # Simulate an API response
        api_response = {
            "id": "12345",
            "name": "API Space",
            "private": True,
            "statuses": [{"status": "To Do", "color": "#ff0000"}],
            "multiple_assignees": False,
            "features": {"due_dates": {"enabled": True}},
            "extra_field": "extra value"
        }
        
        # Create from API response
        space = ClickUpSpace(**api_response)
        
        # Check fields were properly set
        assert space.space_id == "12345"
        assert space.name == "API Space"
        assert space.private is True
        assert len(space.statuses) == 1
        assert space.statuses[0]["status"] == "To Do"
        assert space.multiple_assignees is False
        assert space.features["due_dates"]["enabled"] is True
        
        # Extra fields should be accessible
        assert hasattr(space, "extra_field")
        assert space.extra_field == "extra value"

    def test_create_space(self):
        """Test creating a ClickUpSpace instance."""
        space = ClickUpSpace(
            space_id="space123",
            name="My Test Space",
            private=True,
            team_id="team123"
        )
        
        # Verify all fields were set correctly
        assert space.space_id == "space123"
        assert space.name == "My Test Space"
        assert space.private is True
        assert space.team_id == "team123"
        
        # Verify id property works
        assert space.id == "space123"

    def test_model_dump_by_alias(self):
        """Test serialization with by_alias parameter."""
        space = ClickUpSpace(
            id="123456",
            name="Test Space",
        )
        
        # By alias = True should use aliases for output
        data_with_alias = space.model_dump(by_alias=True)
        assert "id" in data_with_alias
        assert "space_id" not in data_with_alias
        assert data_with_alias["id"] == "123456"
        
        # By alias = False (default) should use field names for output
        data_without_alias = space.model_dump(by_alias=False)
        assert "space_id" in data_without_alias
        assert "id" not in data_without_alias
        assert data_without_alias["space_id"] == "123456"
