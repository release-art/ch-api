"""Tests for _PaginatedEntityInitCls with custom convert_to_my_args."""

from unittest.mock import AsyncMock, MagicMock

from ch_api.types import base
from ch_api.types.compound_api_types.public_data.pagination import _PaginatedEntityInitCls


class MockContainer(base.BaseModel):
    """Mock container for testing."""

    data: str
    count: int


class MockItem(base.BaseModel):
    """Mock item for testing."""

    value: str


class TestPaginatedEntityInitCls:
    """Test _PaginatedEntityInitCls initialization with custom convert_to_my_args."""

    def test_init_with_custom_convert_to_my_args(self):
        """Test that custom convert_to_my_args is used when provided (line 48)."""
        # Create mock functions
        fetch_page_fn = AsyncMock()
        convert_item_fn = MagicMock()

        # Create a custom convert_to_my_args function
        def custom_converter(container: MockContainer | None) -> dict:
            if container is None:
                return {"custom": "empty"}
            return {"custom": "data", "value": container.data}

        # Initialize with custom convert_to_my_args - this should hit line 48
        entity = _PaginatedEntityInitCls(
            fetch_page_fn=fetch_page_fn,
            convert_item_fn=convert_item_fn,
            convert_to_my_args=custom_converter,
        )

        # Verify the custom function is assigned (line 48)
        assert entity.convert_to_my_args == custom_converter

        # Test that the custom converter works as expected
        container = MockContainer(data="test", count=5)
        result = entity.convert_to_my_args(container)
        assert result == {"custom": "data", "value": "test"}

        # Test with None
        result_none = entity.convert_to_my_args(None)
        assert result_none == {"custom": "empty"}

    def test_init_with_default_convert_to_my_args(self):
        """Test that default convert_to_my_args is used when None provided."""
        # Create mock functions
        fetch_page_fn = AsyncMock()
        convert_item_fn = MagicMock()

        # Initialize with None convert_to_my_args - should use default
        entity = _PaginatedEntityInitCls(
            fetch_page_fn=fetch_page_fn,
            convert_item_fn=convert_item_fn,
            convert_to_my_args=None,
        )

        # Verify the default converter is assigned
        assert entity.convert_to_my_args is not None

        # Test that the default converter uses model_dump
        container = MockContainer(data="test", count=5)
        result = entity.convert_to_my_args(container)
        assert result == {"data": "test", "count": 5}

        # Test with None
        result_none = entity.convert_to_my_args(None)
        assert result_none == {}
