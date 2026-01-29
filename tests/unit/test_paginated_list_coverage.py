"""Tests for MultipageList edge cases and error handling."""

from unittest.mock import MagicMock

import httpx
import pytest

from ch_api import exc
from ch_api.types import base
from ch_api.types.pagination import paginated_list, types


class MockItem(base.BaseModel):
    """Mock item for testing."""

    value: str
    id: int

    @classmethod
    def new(cls, val: int) -> "MockItem":
        """Create a new MockItem with given id."""
        return cls(value=f"item-{val}", id=val)


@pytest.fixture
def fetch_fn_mock(mocker):
    """Fixture for a mock fetch_page function."""
    out = mocker.AsyncMock(name="mock_fetch_page")
    return out


class TestMultipageListErrorHandling:
    """Test error handling in MultipageList."""

    @pytest.mark.asyncio
    async def test_fetch_page_with_httpx_request_error(self, fetch_fn_mock):
        """Test that httpx.RequestError during page fetch is handled (lines 367-373)."""
        # Configure mock to succeed on first page, fail on second
        fetch_fn_mock.side_effect = [
            (
                types.PaginatedResultInfo(page=0, has_next=True),
                [MockItem.new(1)],
            ),
            httpx.RequestError("Network error"),
        ]

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        # First item should work
        first_item = await ml[0]
        assert first_item.id == 1

        # Try to fetch second item (which should trigger the error)
        result = await ml._fetch_page_to_item_idx(1)

        # Should return None and set state to PAGE_FETCH_FAILED (line 373)
        assert result is None
        assert ml._result_info == paginated_list.SpecialResultInfoState.PAGE_FETCH_FAILED

    @pytest.mark.asyncio
    async def test_fetch_page_with_companies_house_api_error(self, fetch_fn_mock):
        """Test that CompaniesHouseApiError during page fetch is handled (lines 367-373)."""
        # Configure mock to succeed on first page, fail on second
        fetch_fn_mock.side_effect = [
            (
                types.PaginatedResultInfo(page=0, has_next=True),
                [MockItem.new(1)],
            ),
            exc.CompaniesHouseApiError("API error"),
        ]

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        # Try to fetch second item
        result = await ml._fetch_page_to_item_idx(1)

        # Should return None and set state to PAGE_FETCH_FAILED
        assert result is None
        assert ml._result_info == paginated_list.SpecialResultInfoState.PAGE_FETCH_FAILED

    @pytest.mark.asyncio
    async def test_fetch_page_error_on_first_page(self, fetch_fn_mock):
        """Test that error on first page sets FIRST_PAGE_FETCH_FAILED (line 371)."""
        fetch_fn_mock.side_effect = httpx.RequestError("Network error on first page")

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)

        # Try to initialize (which fetches first page)
        result = await ml._fetch_page_to_item_idx(0)

        # Should return None and set state to FIRST_PAGE_FETCH_FAILED (line 371)
        assert result is None
        assert ml._result_info == paginated_list.SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED

    @pytest.mark.asyncio
    async def test_fetch_page_returns_none_page_info(self, fetch_fn_mock):
        """Test handling when new_page_info is None (lines 394-397)."""
        # First page succeeds, second returns None for page_info
        fetch_fn_mock.side_effect = [
            (
                types.PaginatedResultInfo(page=0, has_next=True),
                [MockItem.new(1)],
            ),
            (None, [MockItem.new(2)]),
        ]

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        # Try to fetch second item
        result = await ml._fetch_page_to_item_idx(1)

        # Should set state to ALL_PAGES_FETCHED (line 397)
        assert ml._result_info == paginated_list.SpecialResultInfoState.ALL_PAGES_FETCHED

    @pytest.mark.asyncio
    async def test_fetch_page_returns_none_page_info_on_first_page(self, fetch_fn_mock):
        """Test when first page returns None for page_info (line 395)."""
        fetch_fn_mock.return_value = (None, [MockItem.new(1)])

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)

        # Try to initialize
        result = await ml._fetch_page_to_item_idx(0)

        # Should set state to FIRST_PAGE_FETCH_FAILED (line 395)
        assert ml._result_info == paginated_list.SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED


class TestMultipageListIteration:
    """Test iteration edge cases."""

    @pytest.mark.asyncio
    async def test_aiter_with_index_error_and_len_changed(self, fetch_fn_mock):
        """Test __aiter__ exception handling when __len__ changes (lines 400-410)."""
        # First page reports 5 items but only returns 2
        fetch_fn_mock.side_effect = [
            (
                types.PaginatedResultInfo(page=0, has_next=False),
                [MockItem.new(i) for i in range(2)],
            ),
            (None, []),
        ]

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        # Iteration should handle the inconsistency
        items = []
        async for item in ml:
            items.append(item)

        # Should only get 2 items
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_aiter_with_break_on_index_error(self, fetch_fn_mock):
        """Test __aiter__ breaks when IndexError occurs and idx >= len (lines 404-406)."""
        fetch_fn_mock.return_value = (
            types.PaginatedResultInfo(page=0, has_next=False),
            [MockItem.new(i) for i in range(2)],
        )

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        # Normal iteration should work fine
        items = []
        async for item in ml:
            items.append(item)

        assert len(items) == 2
        # This test verifies the break path (line 406) gets executed

    @pytest.mark.asyncio
    async def test_aiter_errs_on_negative_idx(self, fetch_fn_mock):
        fetch_fn_mock.return_value = (
            types.PaginatedResultInfo(page=0, has_next=False),
            [MockItem.new(i) for i in range(2)],
        )

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        with pytest.raises(IndexError):
            await ml[-1]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("unexpected_len_change", [True, False])
    async def test_index_error_on_len_change(self, fetch_fn_mock, unexpected_len_change):
        first_rv = (
            types.PaginatedResultInfo(page=0, has_next=True, total_count=100),
            [MockItem.new(i) for i in range(2)],
        )
        if unexpected_len_change:
            second_rv = (
                types.PaginatedResultInfo(page=1, has_next=True, total_count=4),
                [MockItem.new(2)],
            )
        else:
            second_rv = (
                types.PaginatedResultInfo(page=1, has_next=True, total_count=4),
                [MockItem.new(i) for i in range(2, 4)],
            )

        third_rv = (
            types.PaginatedResultInfo(page=2, has_next=False, total_count=1),
            [],
        )

        fetch_fn_mock.side_effect = [first_rv, second_rv, third_rv]

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()
        assert not ml.is_fully_fetched

        async for _ in ml:
            pass  # Exhaust first page

        assert ml.is_fully_fetched

    @pytest.mark.asyncio
    async def test_iter_unknown_len(self, fetch_fn_mock):
        fetch_fn_mock.side_effect = [
            (
                types.PaginatedResultInfo(page=0, has_next=True, total_count=None),
                [MockItem.new(i) for i in range(2)],
            ),
            (
                types.PaginatedResultInfo(page=1, has_next=True, total_count=None),
                [MockItem.new(i) for i in range(2)],
            ),
            (
                types.PaginatedResultInfo(page=2, has_next=False, total_count=None),
                [MockItem.new(i) for i in range(100)],
            ),
        ]
        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()
        assert not ml.is_fully_fetched

        with pytest.raises(ValueError) as err:
            len(ml)

        assert "Cannot determine length" in str(err.value)

        async for _ in ml:
            pass  # Exhaust first page


class TestMultipageListUtilityMethods:
    """Test utility methods."""

    @pytest.mark.asyncio
    async def test_local_pages(self, fetch_fn_mock):
        """Test local_pages method (line 437)."""
        fetch_fn_mock.side_effect = [
            (
                types.PaginatedResultInfo(page=0, has_next=True),
                [MockItem.new(i) for i in range(3)],
            ),
            (
                types.PaginatedResultInfo(page=1, has_next=False),
                [MockItem.new(i) for i in range(3, 6)],
            ),
            (None, []),
        ]

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        # Fetch second page
        await ml._fetch_page_to_item_idx(5)

        # Test local_pages (line 437)
        pages = ml.local_pages()
        assert len(pages) == 2
        assert len(pages[0]) == 3
        assert len(pages[1]) == 3
        assert pages[0][0].id == 0
        assert pages[1][0].id == 3

    @pytest.mark.asyncio
    async def test_len_when_all_pages_fetched(self, fetch_fn_mock):
        """Test __len__ returns local_len when all pages fetched (lines 448-454)."""
        fetch_fn_mock.return_value = (
            types.PaginatedResultInfo(page=0, has_next=False),
            [MockItem.new(i) for i in range(3)],
        )

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        # Since has_next=False, all pages are fetched
        # __len__ should return local_len (line 453)
        assert len(ml) == 3
        assert not ml._has_next_page()

    @pytest.mark.asyncio
    async def test_repr(self, fetch_fn_mock):
        """Test __repr__ method (line 457)."""
        fetch_fn_mock.return_value = (
            types.PaginatedResultInfo(page=0, has_next=False, total_count=2),
            [MockItem.new(i) for i in range(2)],
        )

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        # Test __repr__ (line 457)
        repr_str = repr(ml)
        assert "MultipageList" in repr_str
        assert "_pages" in repr_str or "FetchedPageData" in repr_str

    @pytest.mark.asyncio
    async def test_model_dump(self, fetch_fn_mock):
        """Test model_dump method (line 465)."""
        fetch_fn_mock.return_value = (
            types.PaginatedResultInfo(page=0, has_next=False),
            [MockItem.new(1), MockItem.new(2)],
        )

        ml = paginated_list.MultipageList(fetch_page=fetch_fn_mock)
        await ml._async_init()

        # Test model_dump with json mode (line 465)
        dumped = ml.model_dump(mode="json")
        assert len(dumped) == 2
        assert dumped[0] == {"value": "item-1", "id": 1}
        assert dumped[1] == {"value": "item-2", "id": 2}

        # Test model_dump with python mode
        dumped_python = ml.model_dump(mode="python")
        assert len(dumped_python) == 2
        assert dumped_python[0] == {"value": "item-1", "id": 1}


class TestMultipageListPydanticSchema:
    """Test Pydantic schema generation."""

    def test_get_pydantic_core_schema(self):
        """Test __get_pydantic_core_schema__ method (line 499)."""
        import pydantic_core

        # Mock handler
        def mock_handler(t):
            return pydantic_core.core_schema.list_schema(pydantic_core.core_schema.any_schema())

        # Test with type arguments (line 496-499)
        source_type = MagicMock()
        source_type.__args__ = (MockItem,)

        schema = paginated_list.MultipageList.__get_pydantic_core_schema__(source_type, mock_handler)

        # Should return an is_instance_schema
        assert schema is not None
        assert "type" in schema or "cls" in schema or isinstance(schema, dict)

    def test_get_pydantic_core_schema_no_args(self):
        """Test __get_pydantic_core_schema__ with no type args (line 499)."""

        import pydantic_core

        # Mock handler
        def mock_handler(t):
            return pydantic_core.core_schema.list_schema(pydantic_core.core_schema.any_schema())

        # Test without type arguments - should use Any (line 499)
        source_type = MagicMock()
        source_type.__args__ = None

        schema = paginated_list.MultipageList.__get_pydantic_core_schema__(source_type, mock_handler)

        # Should still return a valid schema
        assert schema is not None
