"""
Contract tests for base DTO classes.

These tests verify that the base DTO classes in clickup_mcp.dto.base
adhere to their contract and function as expected.
"""

from typing import Any, Dict, Optional

import pytest
from pydantic import ConfigDict, Field

from clickup_mcp.models.dto.base import (
    BaseDTO,
    BaseRequestDTO,
    BaseResponseDTO,
    PaginatedResponseDTO,
)


class TestBaseDTO:
    """Test the BaseDTO class."""

    def test_model_config(self):
        """Test that the model_config is correctly set."""
        # Verify the model_config settings
        assert BaseDTO.model_config["populate_by_name"] is True
        assert BaseDTO.model_config["extra"] == "allow"
        assert BaseDTO.model_config["arbitrary_types_allowed"] is True

    def test_serialize(self):
        """Test that to_dict correctly converts the model to a dictionary."""

        class TestDTO(BaseDTO):
            name: str
            value: Optional[int] = None

        test_dto = TestDTO(name="test", value=123)
        result = test_dto.serialize()

        assert result == {"name": "test", "value": 123}

    def test_serialize_excludes_none(self):
        """Test that to_dict excludes None values."""

        class TestDTO(BaseDTO):
            name: str
            value: Optional[int] = None

        test_dto = TestDTO(name="test")  # value is None by default
        result = test_dto.serialize()

        assert result == {"name": "test"}
        # Verify that None values are excluded
        assert "value" not in result

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed in the model."""

        class TestDTO(BaseDTO):
            name: str

        # Extra field that's not in the model definition
        test_dto = TestDTO(name="test", extra_field="extra")

        # Verify we can access the extra field
        assert test_dto.extra_field == "extra"

        # Verify it's included in the dict output
        assert test_dto.serialize() == {"name": "test", "extra_field": "extra"}

    def test_field_aliases(self):
        """Test that field aliases work correctly."""

        class TestDTO(BaseDTO):
            proper_name: str = Field(alias="name")

        # Create with aliased field name
        test_dto = TestDTO(name="test")

        # Verify the proper field name contains the value
        assert test_dto.proper_name == "test"

        # Also verify it works when creating with the proper field name
        test_dto2 = TestDTO(proper_name="test2")
        assert test_dto2.proper_name == "test2"

        # Verify both appear correctly in the dict output
        assert test_dto.serialize() == {"proper_name": "test"}
        assert test_dto2.serialize() == {"proper_name": "test2"}


class TestBaseRequestDTO:
    """Test the BaseRequestDTO class."""

    def test_inheritance(self):
        """Test that BaseRequestDTO inherits from BaseDTO."""
        assert issubclass(BaseRequestDTO, BaseDTO)

    def test_deserialize(self):
        """Test that from_dict correctly creates a model from a dictionary."""

        class TestRequestDTO(BaseRequestDTO):
            name: str
            value: Optional[int] = None

        data = {"name": "test", "value": 123}
        test_dto = TestRequestDTO.deserialize(data)

        assert test_dto.name == "test"
        assert test_dto.value == 123

    def test_deserialize_with_extra_fields(self):
        """Test that from_dict handles extra fields correctly."""

        class TestRequestDTO(BaseRequestDTO):
            name: str

        data = {"name": "test", "extra_field": "extra"}
        test_dto = TestRequestDTO.deserialize(data)

        assert test_dto.name == "test"
        assert test_dto.extra_field == "extra"

    def test_round_trip_conversion(self):
        """Test that converting to dict and back preserves data."""

        class TestRequestDTO(BaseRequestDTO):
            name: str
            value: Optional[int] = None

        original = TestRequestDTO(name="test", value=123)
        dict_data = original.serialize()
        recreated = TestRequestDTO.deserialize(dict_data)

        assert recreated.name == original.name
        assert recreated.value == original.value


class TestBaseResponseDTO:
    """Test the BaseResponseDTO class."""

    def test_inheritance(self):
        """Test that BaseResponseDTO inherits from BaseDTO."""
        assert issubclass(BaseResponseDTO, BaseDTO)

    def test_deserialize(self):
        """Test that from_dict correctly creates a model from a dictionary."""

        class TestResponseDTO(BaseResponseDTO):
            id: str
            name: str
            data: Optional[Dict[str, Any]] = None

        data = {"id": "123", "name": "test", "data": {"key": "value"}}
        test_dto = TestResponseDTO.deserialize(data)

        assert test_dto.id == "123"
        assert test_dto.name == "test"
        assert test_dto.data == {"key": "value"}

    def test_nested_models(self):
        """Test that nested models are handled correctly."""

        class NestedDTO(BaseDTO):
            nested_id: str
            nested_name: str

        class TestResponseDTO(BaseResponseDTO):
            id: str
            nested: NestedDTO

        data = {"id": "123", "nested": {"nested_id": "456", "nested_name": "nested"}}
        test_dto = TestResponseDTO.deserialize(data)

        assert test_dto.id == "123"
        assert test_dto.nested.nested_id == "456"
        assert test_dto.nested.nested_name == "nested"

        # Verify the dict output contains the nested model
        dict_output = test_dto.serialize()
        assert dict_output["nested"]["nested_id"] == "456"
        assert dict_output["nested"]["nested_name"] == "nested"


class TestPaginatedResponseDTO:
    """Test the PaginatedResponseDTO class."""

    def test_inheritance(self):
        """Test that PaginatedResponseDTO inherits from BaseResponseDTO."""
        assert issubclass(PaginatedResponseDTO, BaseResponseDTO)

    def test_generic_type(self):
        """Test that the generic type is handled correctly."""

        class ItemDTO(BaseDTO):
            id: str
            name: str

        class TestPaginatedDTO(PaginatedResponseDTO[ItemDTO]):
            pass

        # Create test data
        items_data = [{"id": "1", "name": "item1"}, {"id": "2", "name": "item2"}]
        data = {"items": items_data, "next_page": "next", "prev_page": None, "total": 2}

        test_dto = TestPaginatedDTO(**data)

        # Verify the items are properly typed as ItemDTO instances
        assert len(test_dto.items) == 2
        assert isinstance(test_dto.items[0], ItemDTO)
        assert test_dto.items[0].id == "1"
        assert test_dto.items[1].name == "item2"

        # Verify pagination data
        assert test_dto.next_page == "next"
        assert test_dto.prev_page is None
        assert test_dto.total == 2

    def test_optional_pagination_fields(self):
        """Test that optional pagination fields can be omitted."""

        class ItemDTO(BaseDTO):
            id: str

        class TestPaginatedDTO(PaginatedResponseDTO[ItemDTO]):
            pass

        # Create with only required fields
        items_data = [{"id": "1"}, {"id": "2"}]
        data = {"items": items_data}

        test_dto = TestPaginatedDTO(**data)

        assert len(test_dto.items) == 2
        assert test_dto.next_page is None
        assert test_dto.prev_page is None
        assert test_dto.total is None


class TestSubclassCustomization:
    """Test that subclasses can customize their configuration."""

    def test_custom_config(self):
        """Test that subclasses can override the model_config."""

        class CustomDTO(BaseDTO):
            model_config = ConfigDict(
                populate_by_name=True,
                extra="forbid",  # Changed from allow to forbid
                arbitrary_types_allowed=True,
                frozen=True,  # Added frozen
            )

            name: str

        # Verify the config settings
        assert CustomDTO.model_config["extra"] == "forbid"
        assert CustomDTO.model_config["frozen"] is True

        # Test that extra fields are now forbidden
        with pytest.raises(ValueError):
            CustomDTO(name="test", extra_field="should fail")
