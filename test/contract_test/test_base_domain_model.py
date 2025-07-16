"""
Contract tests for domain models.

This module provides tests that verify the contract between BaseDomainModel
and its implementations, ensuring consistent behavior across all domain models.
"""

import inspect
import pytest
from typing import Dict, Any, Type, List

from pydantic import BaseModel, ConfigDict, Field

from clickup_mcp.models.domain.base import BaseDomainModel
from clickup_mcp.models.domain.space import ClickUpSpace


class TestBaseDomainModelContract:
    """Tests that verify the contract between BaseDomainModel and implementations."""
    
    def get_all_domain_models(self) -> List[Type[BaseDomainModel]]:
        """
        Get all domain model classes that extend BaseDomainModel.
        
        For now, we're manually listing them, but this could be automated
        using module inspection in the future.
        
        Returns:
            List of BaseDomainModel subclasses
        """
        return [ClickUpSpace]
    
    def test_base_domain_model_is_abstract(self):
        """Test that BaseDomainModel has the expected abstract layer characteristics."""
        # BaseDomainModel should extend Pydantic's BaseModel
        assert issubclass(BaseDomainModel, BaseModel)
        
        # It should have model_config defined
        assert hasattr(BaseDomainModel, 'model_config')
        
        # It should implement model_dump
        assert hasattr(BaseDomainModel, 'model_dump')
        assert callable(getattr(BaseDomainModel, 'model_dump'))
    
    def test_all_domain_models_extend_base_class(self):
        """Test that all domain models extend BaseDomainModel."""
        for model_class in self.get_all_domain_models():
            assert issubclass(model_class, BaseDomainModel), \
                f"{model_class.__name__} should extend BaseDomainModel"
    
    def test_all_domain_models_have_required_configuration(self):
        """Test that all domain models have the required configuration."""
        for model_class in self.get_all_domain_models():
            # Should have model_config
            assert hasattr(model_class, 'model_config'), \
                f"{model_class.__name__} should have model_config"
            
            # Should have populate_by_name=True for flexible deserialization
            assert model_class.model_config.get('populate_by_name') is True, \
                f"{model_class.__name__} should have populate_by_name=True"
            
            # Should have extra='allow' for handling unknown fields
            assert model_class.model_config.get('extra') == 'allow', \
                f"{model_class.__name__} should have extra='allow'"
    
    def test_all_domain_models_override_model_dump(self):
        """Test that all domain models override model_dump if needed."""
        base_model_dump = BaseDomainModel.model_dump
        
        for model_class in self.get_all_domain_models():
            # If the model needs custom serialization, it should override model_dump
            model_dump = getattr(model_class, 'model_dump')
            
            # Check if the method is overridden (not the same as base class)
            method_overridden = model_dump.__code__ is not base_model_dump.__code__
            
            # If overridden, model_dump should call super().model_dump
            if method_overridden:
                source = inspect.getsource(model_dump)
                assert "super().model_dump" in source, \
                    f"{model_class.__name__}.model_dump should call super().model_dump"
    
    def test_domain_model_serialization_contract(self):
        """Test the serialization contract of domain models."""
        # Create a simple test implementation to verify base behavior
        class TestDomainModel(BaseDomainModel):
            field1: str = Field(...)
            field2: int = Field(default=0)
        
        model = TestDomainModel(field1="test")
        
        # Basic serialization should work
        data = model.model_dump()
        assert isinstance(data, dict)
        assert data["field1"] == "test"
        assert data["field2"] == 0
        
        # Exclude should work
        data = model.model_dump(exclude={"field2"})
        assert "field1" in data
        assert "field2" not in data
        
        # Include should work
        data = model.model_dump(include={"field1"})
        assert "field1" in data
        assert "field2" not in data


class TestClickUpSpaceContractImplementation:
    """Tests specific to ClickUpSpace's implementation of the domain model contract."""
    
    def test_clickup_space_id_property_contract(self):
        """Test that ClickUpSpace correctly implements the ID property contract."""
        space = ClickUpSpace(
            space_id="test123",
            name="Test Space"
        )
        
        # id property should return space_id for backward compatibility
        assert space.id == space.space_id
    
    def test_clickup_space_model_dump_contract(self):
        """Test that ClickUpSpace correctly implements the model_dump contract."""
        space = ClickUpSpace(
            space_id="test123",
            name="Test Space"
        )
        
        # Basic serialization should include both id and space_id
        data = space.model_dump()
        assert "id" in data
        assert "space_id" in data
        assert data["id"] == data["space_id"]
        
        # When excluding space_id, id should still be present
        data = space.model_dump(exclude={"space_id"})
        assert "id" in data
        assert data["id"] == "test123"
        
        # When including only name, id should still be present
        data = space.model_dump(include={"name"})
        assert "name" in data
        assert "id" in data
        assert data["id"] == "test123"
        
        # With exclude_unset=True, id should still be present
        data = space.model_dump(exclude_unset=True)
        assert "id" in data
        assert data["id"] == "test123"


class TestCreateDomainModelFromDict:
    """Tests for creating domain models from dictionaries."""
    
    def test_create_model_from_api_response(self):
        """Test creating domain models from API response dictionaries."""
        # Simulate an API response with 'id' instead of 'space_id'
        api_response = {
            "id": "space123",
            "name": "API Space",
            "private": True,
            "statuses": [
                {"id": "status1", "name": "To Do", "color": "#ff0000"},
                {"id": "status2", "name": "Done", "color": "#00ff00"}
            ],
            "features": {
                "time_tracking": True,
                "priorities": False
            },
            "extra_field": "This should be allowed"
        }
        
        # Create model from API response
        space = ClickUpSpace(**api_response)
        
        # Verify field mapping
        assert space.space_id == "space123"  # Should map from 'id'
        assert space.id == "space123"  # Property should work
        assert space.name == "API Space"
        assert space.private is True
        assert len(space.statuses) == 2
        assert space.features is not None
        assert space.features["time_tracking"] is True
        
        # With extra="allow", extra fields should be preserved in model_dump
        # but not as explicit model attributes
        dumped_data = space.model_dump()
        assert "extra_field" in dumped_data
        assert dumped_data["extra_field"] == "This should be allowed"
        
        # Verify the fields defined in the model are in the __dict__ of the instance
        assert hasattr(space, "space_id")
        assert hasattr(space, "name")
    
    def test_field_aliasing_works_bidirectionally(self):
        """Test that field aliasing works in both directions."""
        # Create with space_id
        space1 = ClickUpSpace(space_id="123", name="Test")
        assert space1.space_id == "123"
        assert space1.id == "123"
        
        # Create with id (alias)
        space2 = ClickUpSpace(id="456", name="Test")
        assert space2.space_id == "456"
        assert space2.id == "456"
        
        # Serialization should include both
        data1 = space1.model_dump()
        assert data1["space_id"] == "123"
        assert data1["id"] == "123"
        
        data2 = space2.model_dump()
        assert data2["space_id"] == "456"
        assert data2["id"] == "456"
