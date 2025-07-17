"""
Contract tests for BaseDomainModel.

This module verifies the contract that BaseDomainModel establishes for all domain models
without depending on actual model implementations. Instead, it uses fake/spy objects
to test the base model contract in isolation.
"""

from typing import Any, ClassVar, Dict

from pydantic import BaseModel, Field

from clickup_mcp.models.domain.base import BaseDomainModel


class FakeDomainModel(BaseDomainModel):
    """A fake domain model for testing the BaseDomainModel contract."""

    # Basic fields for testing
    id: str = Field(..., description="The model's primary identifier")
    name: str = Field(..., description="The model's name")
    active: bool = Field(default=True, description="Whether the model is active")

    # Track method calls for spying
    spy_model_dump_called: ClassVar[bool] = False

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override model_dump to track calls and add special fields."""
        # Track that model_dump was called
        type(self).spy_model_dump_called = True

        # Call super implementation
        result = super().model_dump(**kwargs)

        # Add an extra field for contract verification
        if "extra_contract_field" not in result and not (
            kwargs.get("exclude") and "extra_contract_field" in kwargs["exclude"]
        ):
            result["extra_contract_field"] = "This field should be in all serialized models"

        return result


class FakeDomainModelWithIdAlias(BaseDomainModel):
    """A fake domain model that implements ID aliasing pattern seen in real models."""

    entity_id: str = Field(..., alias="id", description="Primary identifier with 'id' alias")
    name: str = Field(..., description="The model's name")

    @property
    def id(self) -> str:
        """ID property for backward compatibility."""
        return self.entity_id


class TestBaseDomainModelContract:
    """Tests that verify the contract between BaseDomainModel and implementations."""

    def test_base_domain_model_inheritance(self):
        """Test that BaseDomainModel inherits from Pydantic's BaseModel."""
        assert issubclass(BaseDomainModel, BaseModel), "BaseDomainModel must inherit from Pydantic BaseModel"

    def test_base_domain_model_has_config(self):
        """Test that BaseDomainModel has the required configuration."""
        assert hasattr(BaseDomainModel, "model_config"), "BaseDomainModel must have model_config"

        # Test config values
        assert (
            BaseDomainModel.model_config.get("populate_by_name") is True
        ), "model_config should have populate_by_name=True"
        assert BaseDomainModel.model_config.get("extra") == "allow", "model_config should have extra='allow'"

    def test_base_domain_model_has_model_dump(self):
        """Test that BaseDomainModel has model_dump method."""
        assert hasattr(BaseDomainModel, "model_dump"), "BaseDomainModel must have model_dump method"
        assert callable(getattr(BaseDomainModel, "model_dump")), "model_dump must be callable"

    def test_fake_domain_model_inheritance(self):
        """Test that fake domain models can inherit from BaseDomainModel."""
        assert issubclass(FakeDomainModel, BaseDomainModel), "Fake models should inherit from BaseDomainModel"
        assert issubclass(
            FakeDomainModelWithIdAlias, BaseDomainModel
        ), "Fake models with ID alias should inherit from BaseDomainModel"

    def test_fake_domain_model_inherits_config(self):
        """Test that fake domain models inherit config from BaseDomainModel."""
        assert (
            FakeDomainModel.model_config.get("populate_by_name") is True
        ), "Fake model should inherit populate_by_name=True"
        assert FakeDomainModel.model_config.get("extra") == "allow", "Fake model should inherit extra='allow'"

    def test_basic_serialization(self):
        """Test basic serialization of a domain model."""
        # Create a model instance
        model = FakeDomainModel(id="test123", name="Test Model")

        # Reset tracking
        FakeDomainModel.spy_model_dump_called = False

        # Test basic serialization
        data = model.model_dump()
        assert isinstance(data, dict), "model_dump should return a dict"
        assert data["id"] == "test123", "id should be correctly serialized"
        assert data["name"] == "Test Model", "name should be correctly serialized"
        assert data["active"] is True, "default values should be serialized"

        # Verify our contract addition
        assert (
            data["extra_contract_field"] == "This field should be in all serialized models"
        ), "model_dump should follow contract extensions"

        # Verify the spy tracked the call
        assert FakeDomainModel.spy_model_dump_called, "model_dump should have been called"

    def test_serialization_with_exclude(self):
        """Test serialization with exclude parameter."""
        model = FakeDomainModel(id="test123", name="Test Model")

        # Reset tracking
        FakeDomainModel.spy_model_dump_called = False

        # Test serialization with exclude
        data = model.model_dump(exclude={"active", "extra_contract_field"})
        assert "id" in data, "id should be included"
        assert "name" in data, "name should be included"
        assert "active" not in data, "active should be excluded"
        assert "extra_contract_field" not in data, "extra_contract_field should be excluded"

        # Verify the spy tracked the call
        assert FakeDomainModel.spy_model_dump_called, "model_dump should have been called"

    def test_serialization_with_include(self):
        """Test serialization with include parameter."""
        model = FakeDomainModel(id="test123", name="Test Model")

        # Reset tracking
        FakeDomainModel.spy_model_dump_called = False

        # Test serialization with include
        data = model.model_dump(include={"id", "name"})
        assert "id" in data, "id should be included"
        assert "name" in data, "name should be included"
        assert "active" not in data, "active should not be included"

        # The contract field is added after filtering, so it's still present
        assert "extra_contract_field" in data, "extra_contract_field should be included"

        # Verify the spy tracked the call
        assert FakeDomainModel.spy_model_dump_called, "model_dump should have been called"

    def test_serialization_with_exclude_unset(self):
        """Test serialization with exclude_unset parameter."""
        # Create a model with only required fields
        model = FakeDomainModel(id="test123", name="Test Model")

        # Reset tracking
        FakeDomainModel.spy_model_dump_called = False

        # Test serialization with exclude_unset
        data = model.model_dump(exclude_unset=True)
        assert "id" in data, "id should be included"
        assert "name" in data, "name should be included"
        # active is using the default value so it may be excluded with exclude_unset

        # Verify the spy tracked the call
        assert FakeDomainModel.spy_model_dump_called, "model_dump should have been called"

    def test_id_aliasing_pattern(self):
        """Test the ID aliasing pattern used in real models."""
        # Create model with entity_id (using 'id' alias)
        model1 = FakeDomainModelWithIdAlias(id="test123", name="Test Model")
        assert model1.entity_id == "test123", "entity_id should be set from 'id' alias"
        assert model1.id == "test123", "id property should return entity_id"

        # Create model with explicit entity_id
        model2 = FakeDomainModelWithIdAlias(entity_id="test456", name="Another Model")
        assert model2.entity_id == "test456", "entity_id should be set directly"
        assert model2.id == "test456", "id property should return entity_id"

    def test_id_aliasing_serialization(self):
        """Test serialization with ID aliasing."""
        model = FakeDomainModelWithIdAlias(id="test123", name="Test Model")

        # Test basic serialization
        data = model.model_dump()
        assert "entity_id" in data, "entity_id should be in serialized data"
        assert "id" not in data, "id should not be in serialized data"
        assert data["entity_id"] == "test123", "entity_id should have correct value"

        # Test serialization with by_alias=True
        data_with_alias = model.model_dump(by_alias=True)
        assert "id" in data_with_alias, "id should be in serialized data"
        assert data_with_alias["id"] == "test123", "id should have correct value"
        assert "entity_id" not in data_with_alias, "entity_id should not be in serialized data"

        # Test exclude entity_id but keep id
        data = model.model_dump(exclude={"entity_id"})
        assert "entity_id" not in data, "entity_id should be excluded"
        assert "id" not in data, "id should still not be included"

        # Test include only name, but id should still be present
        data = model.model_dump(include={"name"})
        assert "name" in data, "name should be included"
        assert "entity_id" not in data, "entity_id should not be included"
        assert "id" not in data, "id should still not be included"


class TestModelInstantiation:
    """Tests for model instantiation behavior."""

    def test_create_from_dict_with_extra_fields(self):
        """Test creating a model from a dict with extra fields."""
        # Create with extra fields
        data = {"id": "test123", "name": "Test Model", "unknown_field": "This should be allowed"}

        model = FakeDomainModel(**data)
        assert model.id == "test123", "id should be set correctly"
        assert model.name == "Test Model", "name should be set correctly"

        # Extra fields should be preserved in serialization
        serialized = model.model_dump()
        assert "unknown_field" in serialized, "Extra fields should be preserved in serialization"
        assert serialized["unknown_field"] == "This should be allowed"

    def test_field_aliasing_works(self):
        """Test that field aliasing works correctly."""
        # Create model using the aliased field name
        model = FakeDomainModelWithIdAlias(id="test123", name="Test Model")
        assert model.entity_id == "test123", "Alias 'id' should set entity_id"

        # Serialize to verify both fields are present
        data = model.model_dump(by_alias=True)
        assert data["id"] == "test123"
        assert "entity_id" not in data
