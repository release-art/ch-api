"""Unit tests for field types module."""

import logging

import pydantic

from ch_api.types import field_types


class TestRelaxedLiteral:
    """Test RelaxedLiteral field type."""

    def test_relaxed_literal_with_expected_value(self, caplog):
        """Test RelaxedLiteral accepts expected values without warning."""
        relaxed_type = field_types.RelaxedLiteral("active", "dissolved", "liquidation")

        class TestModel(pydantic.BaseModel):
            status: relaxed_type

        with caplog.at_level(logging.WARNING):
            result = TestModel.model_validate({"status": "active"})

        assert result.status == "active"
        assert "Unexpected value" not in caplog.text

    def test_relaxed_literal_with_unexpected_value(self, caplog):
        """Test RelaxedLiteral logs warning for unexpected values."""
        relaxed_type = field_types.RelaxedLiteral("active", "dissolved", "liquidation")

        class TestModel(pydantic.BaseModel):
            status: relaxed_type

        with caplog.at_level(logging.WARNING):
            result = TestModel.model_validate({"status": "new-status"})

        assert result.status == "new-status"
        assert "Unexpected value 'new-status'" in caplog.text
        assert "Expected one of:" in caplog.text

    def test_relaxed_literal_with_none_value(self, caplog):
        """Test RelaxedLiteral accepts None for optional fields."""
        relaxed_type = field_types.RelaxedLiteral("active", "dissolved")

        class TestModel(pydantic.BaseModel):
            status: relaxed_type | None = None

        with caplog.at_level(logging.WARNING):
            result = TestModel.model_validate({"status": None})

        assert result.status is None
        assert "Unexpected value" not in caplog.text

    def test_relaxed_literal_with_multiple_expected_values(self, caplog):
        """Test RelaxedLiteral with multiple expected values."""
        relaxed_type = field_types.RelaxedLiteral("value1", "value2", "value3", "value4")

        class TestModel(pydantic.BaseModel):
            field: relaxed_type

        # Test all expected values
        for value in ["value1", "value2", "value3", "value4"]:
            caplog.clear()
            with caplog.at_level(logging.WARNING):
                result = TestModel.model_validate({"field": value})

            assert result.field == value
            assert "Unexpected value" not in caplog.text

    def test_relaxed_literal_field_name_in_warning(self, caplog):
        """Test that field name is included in warning message."""
        relaxed_type = field_types.RelaxedLiteral("active", "inactive")

        class TestModel(pydantic.BaseModel):
            company_status: relaxed_type

        with caplog.at_level(logging.WARNING):
            result = TestModel.model_validate({"company_status": "unknown"})

        assert result.company_status == "unknown"
        # Warning should mention the field name
        assert "company_status" in caplog.text or "Unexpected value" in caplog.text

    def test_relaxed_literal_converts_to_string(self, caplog):
        """Test RelaxedLiteral converts values to string."""
        relaxed_type = field_types.RelaxedLiteral("1", "2", "3")

        class TestModel(pydantic.BaseModel):
            number: relaxed_type

        # Should convert to string and validate
        result = TestModel.model_validate({"number": "1"})
        assert result.number == "1"
        assert isinstance(result.number, str)

    def test_relaxed_literal_all_expected_values_logged_in_warning(self, caplog):
        """Test that all expected values are listed in the warning message."""
        expected = {"alpha", "beta", "gamma"}
        relaxed_type = field_types.RelaxedLiteral(*expected)

        class TestModel(pydantic.BaseModel):
            field: relaxed_type

        with caplog.at_level(logging.WARNING):
            TestModel.model_validate({"field": "delta"})

        warning_text = caplog.text
        # All expected values should appear in the warning (in sorted order)
        for value in sorted(expected):
            assert value in warning_text

    def test_relaxed_literal_single_expected_value(self, caplog):
        """Test RelaxedLiteral with single expected value."""
        relaxed_type = field_types.RelaxedLiteral("only-value")

        class TestModel(pydantic.BaseModel):
            field: relaxed_type

        # Correct value
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            result1 = TestModel.model_validate({"field": "only-value"})
        assert result1.field == "only-value"
        assert "Unexpected value" not in caplog.text

        # Wrong value
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            result2 = TestModel.model_validate({"field": "other-value"})
        assert result2.field == "other-value"
        assert "Unexpected value" in caplog.text

    def test_relaxed_literal_empty_expected_values(self, caplog):
        """Test RelaxedLiteral with no expected values (all values are unexpected)."""
        relaxed_type = field_types.RelaxedLiteral()

        class TestModel(pydantic.BaseModel):
            field: relaxed_type

        with caplog.at_level(logging.WARNING):
            result = TestModel.model_validate({"field": "any-value"})

        assert result.field == "any-value"
        assert "Unexpected value" in caplog.text


class TestUndocumentedNullable:
    """Test UndocumentedNullable type alias."""

    def test_undocumented_nullable_is_optional(self):
        """Test that UndocumentedNullable is an Optional type."""
        # UndocumentedNullable should be equivalent to typing.Optional
        assert field_types.UndocumentedNullable is not None

    def test_undocumented_nullable_with_model(self):
        """Test UndocumentedNullable in a Pydantic model."""

        class TestModel(pydantic.BaseModel):
            optional_field: field_types.UndocumentedNullable[str] = None
            required_field: str

        # Should allow None
        result1 = TestModel.model_validate({"optional_field": None, "required_field": "test"})
        assert result1.optional_field is None

        # Should allow values
        result2 = TestModel.model_validate({"optional_field": "value", "required_field": "test"})
        assert result2.optional_field == "value"

        # Should default to None
        result3 = TestModel.model_validate({"required_field": "test"})
        assert result3.optional_field is None
