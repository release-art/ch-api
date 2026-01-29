"""Unit tests for base model functionality."""

import pydantic
import pytest

from ch_api.types import base


class TestBaseModelValidate:
    """Test BaseModel.model_validate method."""

    def test_model_validate_with_whitespace_in_field_names(self):
        """Test model_validate trims whitespace from field names."""

        class TestModel(base.BaseModel):
            field_one: str
            field_two: str

        # API response with whitespace in field names
        data = {
            " field_one ": "value1",
            "  field_two  ": "value2",
        }

        result = TestModel.model_validate(data)

        assert result.field_one == "value1"
        assert result.field_two == "value2"

    def test_model_validate_filters_notinuse_fields(self):
        """Test model_validate removes fields marked as [notinuse]."""

        class TestModel(base.BaseModel):
            company_name: str

        # API response with [notinuse] field
        data = {
            "company_name": "Test Corp",
            "[notinuse]_field": "should_be_removed",
        }

        result = TestModel.model_validate(data)

        assert result.company_name == "Test Corp"
        # Should not raise an error about unexpected field

    def test_model_validate_with_multiple_notinuse_fields(self):
        """Test multiple [notinuse] fields are filtered."""

        class TestModel(base.BaseModel):
            name: str

        data = {
            "name": "Test",
            "[notinuse]_field1": "value1",
            "[notinuse]_field2": "value2",
            "[notinuse]_field3": "value3",
        }

        result = TestModel.model_validate(data)

        assert result.name == "Test"

    def test_model_validate_with_non_dict_data(self):
        """Test model_validate passes non-dict data directly to pydantic."""

        class TestModel(base.BaseModel):
            value: int

        # Should handle non-dict data (list, string, etc.)
        # Pydantic will handle validation appropriately
        with pytest.raises(pydantic.ValidationError):
            TestModel.model_validate([1, 2, 3])

    def test_model_validate_preserves_none_values(self):
        """Test model_validate preserves None values in data."""

        class TestModel(base.BaseModel):
            name: str
            optional_field: str | None = None

        data = {
            "name": "Test",
            "optional_field": None,
        }

        result = TestModel.model_validate(data)

        assert result.name == "Test"
        assert result.optional_field is None

    def test_model_validate_already_lowercase_fields(self):
        """Test model_validate with already lowercase field names."""

        class TestModel(base.BaseModel):
            field: str

        data = {"field": "value"}

        result = TestModel.model_validate(data)

        assert result.field == "value"

    def test_model_validate_mixed_case_preservation_in_values(self):
        """Test that mixed case in values is preserved (only field names normalized)."""

        class TestModel(base.BaseModel):
            description: str

        data = {
            "description": "This Has MixedCase Values",
        }

        result = TestModel.model_validate(data)

        # Value should preserve original case
        assert result.description == "This Has MixedCase Values"

    def test_model_validate_lowercase_conversion(self):
        """Test that field names are converted to lowercase."""

        class TestModel(base.BaseModel):
            test_field: str

        # Uppercase field name should be converted to lowercase
        data = {"TEST_FIELD": "value"}
        result = TestModel.model_validate(data)
        assert result.test_field == "value"

    def test_model_validate_notinuse_prefix_filtering(self):
        """Test that fields with [notinuse] prefix are removed."""

        class TestModel(base.BaseModel):
            field: str

        # Field with [notinuse] prefix should be filtered out
        data = {
            "field": "value",
            "[notinuse]something": "ignored",
        }

        result = TestModel.model_validate(data)
        assert result.field == "value"


class TestBaseModelInheritance:
    """Test BaseModel inheritance."""

    def test_base_model_inherits_correctly(self):
        """Test that custom models inherit from BaseModel correctly."""

        class CustomModel(base.BaseModel):
            name: str

        # Should be instance of pydantic.BaseModel
        assert isinstance(CustomModel.model_validate({"name": "test"}), pydantic.BaseModel)

        # Should have custom validate method
        assert hasattr(CustomModel, "model_validate")

    def test_base_model_field_validation(self):
        """Test that BaseModel validates fields correctly."""

        class CustomModel(base.BaseModel):
            count: int
            name: str

        result = CustomModel.model_validate({"count": 5, "name": "test"})
        assert result.count == 5
        assert result.name == "test"

        # Should fail with invalid type
        with pytest.raises(pydantic.ValidationError):
            CustomModel.model_validate({"count": "not_an_int", "name": "test"})
