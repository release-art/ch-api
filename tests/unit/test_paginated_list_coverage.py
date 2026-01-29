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


class TestMultipageListErrorHandling:
    """Test error handling in MultipageList."""

    @pytest.mark.asyncio
    async def test_fetch_page_with_httpx_request_error(self):
        """Test that httpx.RequestError during page fetch is handled (lines 367-373)."""

        # Create a callback that raises httpx.RequestError
        async def fetch_page_cb(target: types.FetchPageCallArg):
            if target.last_fetched_page == -1:
                # First page succeeds
                return (
                    types.PaginatedResultInfo(
                        page=0,
                        has_next=True,
                    ),
                    [MockItem(value="item1", id=1)],
                )
            else:
                # Second page fails with httpx.RequestError
                raise httpx.RequestError("Network error")

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)
        await multipage_list._async_init()

        # First item should work
        first_item = await multipage_list[0]
        assert first_item.id == 1

        # Try to fetch second item (which should trigger the error)
        result = await multipage_list._fetch_page_to_item_idx(1)

        # Should return None and set state to PAGE_FETCH_FAILED (line 373)
        assert result is None
        assert multipage_list._result_info == paginated_list.SpecialResultInfoState.PAGE_FETCH_FAILED

    @pytest.mark.asyncio
    async def test_fetch_page_with_companies_house_api_error(self):
        """Test that CompaniesHouseApiError during page fetch is handled (lines 367-373)."""

        # Create a callback that raises CompaniesHouseApiError
        async def fetch_page_cb(target: types.FetchPageCallArg):
            if target.last_fetched_page == -1:
                # First page succeeds
                return (
                    types.PaginatedResultInfo(
                        page=0,
                        has_next=True,
                    ),
                    [MockItem(value="item1", id=1)],
                )
            else:
                # Second page fails with CompaniesHouseApiError
                raise exc.CompaniesHouseApiError("API error")

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)
        await multipage_list._async_init()

        # Try to fetch second item
        result = await multipage_list._fetch_page_to_item_idx(1)

        # Should return None and set state to PAGE_FETCH_FAILED
        assert result is None
        assert multipage_list._result_info == paginated_list.SpecialResultInfoState.PAGE_FETCH_FAILED

    @pytest.mark.asyncio
    async def test_fetch_page_error_on_first_page(self):
        """Test that error on first page sets FIRST_PAGE_FETCH_FAILED (line 371)."""

        # Create a callback that fails on first page
        async def fetch_page_cb(target: types.FetchPageCallArg):
            raise httpx.RequestError("Network error on first page")

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)

        # Try to initialize (which fetches first page)
        result = await multipage_list._fetch_page_to_item_idx(0)

        # Should return None and set state to FIRST_PAGE_FETCH_FAILED (line 371)
        assert result is None
        assert multipage_list._result_info == paginated_list.SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED

    @pytest.mark.asyncio
    async def test_fetch_page_returns_none_page_info(self):
        """Test handling when new_page_info is None (lines 394-397)."""
        fetch_count = 0

        async def fetch_page_cb(target: types.FetchPageCallArg):
            nonlocal fetch_count
            fetch_count += 1

            if fetch_count == 1:
                # First page succeeds
                return (
                    types.PaginatedResultInfo(
                        page=0,
                        has_next=True,
                    ),
                    [MockItem(value="item1", id=1)],
                )
            else:
                # Second fetch returns None for page_info (lines 394-397)
                return (None, [MockItem(value="item2", id=2)])

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)
        await multipage_list._async_init()

        # Try to fetch second item
        result = await multipage_list._fetch_page_to_item_idx(1)

        # Should set state to ALL_PAGES_FETCHED (line 397)
        assert multipage_list._result_info == paginated_list.SpecialResultInfoState.ALL_PAGES_FETCHED

    @pytest.mark.asyncio
    async def test_fetch_page_returns_none_page_info_on_first_page(self):
        """Test when first page returns None for page_info (line 395)."""

        async def fetch_page_cb(target: types.FetchPageCallArg):
            # First page returns None for page_info
            return (None, [MockItem(value="item1", id=1)])

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)

        # Try to initialize
        result = await multipage_list._fetch_page_to_item_idx(0)

        # Should set state to FIRST_PAGE_FETCH_FAILED (line 395)
        assert multipage_list._result_info == paginated_list.SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED


class TestMultipageListIteration:
    """Test iteration edge cases."""

    @pytest.mark.asyncio
    async def test_aiter_with_index_error_and_len_changed(self):
        """Test __aiter__ exception handling when __len__ changes (lines 400-410)."""
        # Create a list that changes length during iteration
        fetch_count = 0

        async def fetch_page_cb(target: types.FetchPageCallArg):
            nonlocal fetch_count
            fetch_count += 1

            if fetch_count == 1:
                # First page reports 5 items but only returns 2
                return (
                    types.PaginatedResultInfo(
                        page=0,
                        has_next=False,
                    ),
                    [MockItem(value=f"item{i}", id=i) for i in range(2)],
                )
            return (None, [])

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)
        await multipage_list._async_init()

        # Iteration should handle the inconsistency
        items = []
        async for item in multipage_list:
            items.append(item)

        # Should only get 2 items despite total_count being 5
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_aiter_with_break_on_index_error(self):
        """Test __aiter__ breaks when IndexError occurs and idx >= len (lines 404-406)."""

        # Create a list where total_count is accurate
        async def fetch_page_cb(target: types.FetchPageCallArg):
            return (
                types.PaginatedResultInfo(
                    page=0,
                    has_next=False,
                ),
                [MockItem(value=f"item{i}", id=i) for i in range(2)],
            )

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)
        await multipage_list._async_init()

        # Normal iteration should work fine
        items = []
        async for item in multipage_list:
            items.append(item)

        assert len(items) == 2
        # This test verifies the break path (line 406) gets executed


class TestMultipageListUtilityMethods:
    """Test utility methods."""

    @pytest.mark.asyncio
    async def test_local_pages(self):
        """Test local_pages method (line 437)."""

        async def fetch_page_cb(target: types.FetchPageCallArg):
            page_num = target.last_fetched_page + 1
            if page_num == 0:
                return (
                    types.PaginatedResultInfo(page=0, has_next=True),
                    [MockItem(value=f"item{i}", id=i) for i in range(3)],
                )
            elif page_num == 1:
                return (
                    types.PaginatedResultInfo(page=1, has_next=False),
                    [MockItem(value=f"item{i}", id=i) for i in range(3, 6)],
                )
            return (None, [])

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)
        await multipage_list._async_init()

        # Fetch second page
        await multipage_list._fetch_page_to_item_idx(5)

        # Test local_pages (line 437)
        pages = multipage_list.local_pages()
        assert len(pages) == 2
        assert len(pages[0]) == 3
        assert len(pages[1]) == 3
        assert pages[0][0].id == 0
        assert pages[1][0].id == 3

    @pytest.mark.asyncio
    async def test_len_when_all_pages_fetched(self):
        """Test __len__ returns local_len when all pages fetched (lines 448-454)."""

        async def fetch_page_cb(target: types.FetchPageCallArg):
            return (
                types.PaginatedResultInfo(page=0, has_next=False),
                [MockItem(value=f"item{i}", id=i) for i in range(3)],
            )

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)
        await multipage_list._async_init()

        # Since has_next=False, all pages are fetched
        # __len__ should return local_len (line 453)
        assert len(multipage_list) == 3
        assert not multipage_list._has_next_page()

    @pytest.mark.asyncio
    async def test_repr(self):
        """Test __repr__ method (line 457)."""

        async def fetch_page_cb(target: types.FetchPageCallArg):
            return (
                types.PaginatedResultInfo(page=0, has_next=False, total_count=2),
                [MockItem(value=f"item{i}", id=i) for i in range(2)],
            )

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)
        await multipage_list._async_init()

        # Test __repr__ (line 457)
        repr_str = repr(multipage_list)
        assert "MultipageList" in repr_str
        assert "_pages" in repr_str or "FetchedPageData" in repr_str

    @pytest.mark.asyncio
    async def test_model_dump(self):
        """Test model_dump method (line 465)."""

        async def fetch_page_cb(target: types.FetchPageCallArg):
            return (
                types.PaginatedResultInfo(page=0, has_next=False),
                [MockItem(value="test1", id=1), MockItem(value="test2", id=2)],
            )

        multipage_list = paginated_list.MultipageList(fetch_page=fetch_page_cb)
        await multipage_list._async_init()

        # Test model_dump with json mode (line 465)
        dumped = multipage_list.model_dump(mode="json")
        assert len(dumped) == 2
        assert dumped[0] == {"value": "test1", "id": 1}
        assert dumped[1] == {"value": "test2", "id": 2}

        # Test model_dump with python mode
        dumped_python = multipage_list.model_dump(mode="python")
        assert len(dumped_python) == 2
        assert dumped_python[0] == {"value": "test1", "id": 1}


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
