"""Tests for API client methods to improve coverage."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

import ch_api
from ch_api import api, api_settings
from ch_api.types import test_data_generator


class TestCreateTestCompany:
    """Test create_test_company method."""

    @pytest.mark.asyncio
    async def test_create_test_company_success(self):
        """Test successful create_test_company call (lines 281-289)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth, settings=api_settings.TEST_API_SETTINGS)

        # Mock the _execute_request method
        response_data = MagicMock()
        client._execute_request = AsyncMock(return_value=response_data)

        # Create a mock company object
        company = test_data_generator.CreateTestCompanyRequest(
            company_name="Test Company Ltd",
            company_number="12345678",
        )

        result = await client.create_test_company(company)

        assert result == response_data
        client._execute_request.assert_called_once()

        # Verify the request was built correctly
        call_args = client._execute_request.call_args
        request = call_args[0][0]
        assert request.method == "POST"
        assert "test-companies" in request.url.path

    @pytest.mark.asyncio
    async def test_create_test_company_no_url_raises_error(self):
        """Test that create_test_company raises RuntimeError when URL not configured (line 352)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        # Use LIVE_API_SETTINGS which doesn't have test_data_generator_url
        client = api.Client(credentials=auth, settings=api_settings.LIVE_API_SETTINGS)

        # Create a mock company object
        company = test_data_generator.CreateTestCompanyRequest(
            company_name="Test Company Ltd",
            company_number="12345678",
        )

        # Should raise RuntimeError when test_data_generator_url is None
        with pytest.raises(RuntimeError) as exc_info:
            await client.create_test_company(company)

        assert "Test Data Generator URL is not configured" in str(exc_info.value)


class TestPaginatedSearchResultErrors:
    """Test _get_paginated_search_result error handling."""

    @pytest.mark.asyncio
    async def test_get_paginated_search_result_416_returns_empty(self):
        """Test that 416 status returns (None, []) (line 424-426)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create a mock response that raises 416 error
        response = MagicMock()
        response.status_code = 416

        http_error = httpx.HTTPStatusError(
            message="Range Not Satisfiable",
            request=MagicMock(),
            response=response,
        )

        # Mock the _get_resource method to raise 416 error
        client._get_resource = AsyncMock(side_effect=http_error)

        # Create a target for pagination
        from ch_api.types.pagination import types as pagination_types

        target = pagination_types.FetchPageCallArg(
            first_known_item=None,
            last_known_item=None,
            last_fetched_page=-1,
            current_total_list_len=0,
        )

        result = await client._get_paginated_search_result(
            output_t=str,
            base_url="https://api.example.com/search",
            query_params={"query": "test"},
            target=target,
        )

        # Should return (None, []) for 416 status
        assert result == (None, [])

    @pytest.mark.asyncio
    async def test_get_paginated_search_result_other_error_reraises(self):
        """Test that non-416 HTTPStatusError is re-raised (line 427)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create a mock response that raises 500 error
        response = MagicMock()
        response.status_code = 500

        http_error = httpx.HTTPStatusError(
            message="Internal Server Error",
            request=MagicMock(),
            response=response,
        )

        # Mock the _get_resource method to raise 500 error
        client._get_resource = AsyncMock(side_effect=http_error)

        # Create a target for pagination
        from ch_api.types.pagination import types as pagination_types

        target = pagination_types.FetchPageCallArg(
            first_known_item=None,
            last_known_item=None,
            last_fetched_page=-1,
            current_total_list_len=0,
        )

        # Should re-raise the error for non-416 status codes (line 427)
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client._get_paginated_search_result(
                output_t=str,
                base_url="https://api.example.com/search",
                query_params={"query": "test"},
                target=target,
            )

        assert exc_info.value.response.status_code == 500

    @pytest.mark.asyncio
    async def test_get_paginated_search_result_successful_with_items(self):
        """Test successful _get_paginated_search_result with items (line 431)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create a mock successful result with items
        from ch_api.types.public_data import search_companies

        mock_result = MagicMock(spec=search_companies.GenericSearchResult)
        mock_result.items = ["item1", "item2", "item3"]
        mock_result.start_index = 0
        mock_result.items_per_page = 20
        mock_result.total_results = 100

        # Mock the _get_resource method to return the result
        client._get_resource = AsyncMock(return_value=mock_result)

        # Create a target for pagination
        from ch_api.types.pagination import types as pagination_types

        target = pagination_types.FetchPageCallArg(
            first_known_item=None,
            last_known_item=None,
            last_fetched_page=-1,
            current_total_list_len=0,
        )

        result = await client._get_paginated_search_result(
            output_t=str,
            base_url="https://api.example.com/search",
            query_params={"query": "test"},
            target=target,
        )

        # Verify the result structure
        page_info, items = result
        assert page_info is not None
        assert items == ["item1", "item2", "item3"]
        assert page_info.page == 0  # last_fetched_page + 1 = -1 + 1
        assert page_info.per_page == 20
        assert page_info.has_next is True  # 3 items < 100 total

    @pytest.mark.asyncio
    async def test_get_paginated_search_result_with_none_items(self):
        """Test _get_paginated_search_result when items is None (line 431)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create a mock result with items=None
        from ch_api.types.public_data import search_companies

        mock_result = MagicMock(spec=search_companies.GenericSearchResult)
        mock_result.items = None
        mock_result.start_index = 0
        mock_result.items_per_page = 20
        mock_result.total_results = 50

        # Mock the _get_resource method to return the result
        client._get_resource = AsyncMock(return_value=mock_result)

        # Create a target for pagination
        from ch_api.types.pagination import types as pagination_types

        target = pagination_types.FetchPageCallArg(
            first_known_item=None,
            last_known_item=None,
            last_fetched_page=0,
            current_total_list_len=0,
        )

        result = await client._get_paginated_search_result(
            output_t=str,
            base_url="https://api.example.com/search",
            query_params={"query": "test"},
            target=target,
        )

        # When items is None, items should be [] (line 431: items = result.items or [])
        page_info, items = result
        assert items == []
        assert page_info.has_next is False  # No items, so no next page


class TestCompanyOfficersMethod:
    """Test get_officer_list method."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("only_type", ["secretaries", "directors", "llp-members"])
    async def test_get_officer_list_with_only_type_parameter(self, only_type):
        """Test get_officer_list method with only_type parameter (line 475)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Mock the _get_paginated_search_result method
        client._get_paginated_search_result = AsyncMock(return_value=(None, []))

        result = await client.get_officer_list(
            company_number="12345678",
            only_type=only_type,
            order_by="surname",
        )

        # Verify the result is a MultipageList
        assert hasattr(result, "_fetch_page_cb")


class TestAdvancedCompanySearch:
    """Test advanced_company_search method."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "filter_args",
        [
            {"company_status": "active"},
            {"company_type": "test-type"},
            {"company_subtype": "test-subtype"},
            {"dissolved_to": "2023-12-31"},
            {"location": "london"},
            {"sic_codes": ["12345", "67890"]},
        ],
    )
    async def test_advanced_company_search_with_string_company_status(self, mocker, filter_args):
        """Test advanced_company_search with company_status as string (line 591)."""
        import datetime

        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Mock the _get_paginated_advanced_search_result method
        client._get_paginated_advanced_search_result = AsyncMock(return_value=(None, None))

        # Create a mock result that will be returned by from_api_paginated_list
        mock_result = MagicMock()

        async def mock_from_api_paginated_list(fetch_page_fn, convert_item_fn):
            # Call the fetch_page_fn to ensure the code path is executed
            from ch_api.types.pagination import types as pagination_types

            target = pagination_types.FetchPageCallArg(
                first_known_item=None,
                last_known_item=None,
                last_fetched_page=-1,
                current_total_list_len=0,
            )
            await fetch_page_fn(target)
            return mock_result

        mock_fn = mocker.patch.object(
            ch_api.types.compound_api_types.public_data.search_companies.AdvancedSearchResult,
            "from_api_paginated_list",
            side_effect=mock_from_api_paginated_list,
        )

        result = await client.advanced_company_search(
            company_name_includes="Test", dissolved_from=datetime.date(2020, 1, 1), **filter_args
        )

        # Verify result is returned
        assert result is mock_result


class TestFilingHistoryPagination:
    """Test _get_filing_history_page error handling."""

    @pytest.mark.asyncio
    async def test_get_filing_history_page_416_returns_empty(self):
        """Test that 416 status returns (None, []) in filing history (lines 858-860)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create a mock response that raises 416 error
        response = MagicMock()
        response.status_code = 416

        http_error = httpx.HTTPStatusError(
            message="Range Not Satisfiable",
            request=MagicMock(),
            response=response,
        )

        # Mock the _get_resource method to raise 416 error
        client._get_resource = AsyncMock(side_effect=http_error)

        # Create a target for pagination
        from ch_api.types.pagination import types as pagination_types

        target = pagination_types.FetchPageCallArg(
            first_known_item=None,
            last_known_item=None,
            last_fetched_page=-1,
            current_total_list_len=0,
        )

        result = await client._get_filing_history_page(
            base_url="https://api.example.com/company/12345678/filing-history",
            query_params={},
            target=target,
        )

        # Should return (None, []) for 416 status
        assert result == (None, [])

    @pytest.mark.asyncio
    async def test_get_filing_history_page_other_error_reraises(self):
        """Test that non-416 HTTPStatusError is re-raised in filing history (line 863)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create a mock response that raises 500 error
        response = MagicMock()
        response.status_code = 500

        http_error = httpx.HTTPStatusError(
            message="Internal Server Error",
            request=MagicMock(),
            response=response,
        )

        # Mock the _get_resource method to raise 500 error
        client._get_resource = AsyncMock(side_effect=http_error)

        # Create a target for pagination
        from ch_api.types.pagination import types as pagination_types

        target = pagination_types.FetchPageCallArg(
            first_known_item=None,
            last_known_item=None,
            last_fetched_page=-1,
            current_total_list_len=0,
        )

        # Should re-raise the error for non-416 status codes (line 863)
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client._get_filing_history_page(
                base_url="https://api.example.com/company/12345678/filing-history",
                query_params={},
                target=target,
            )

        assert exc_info.value.response.status_code == 500


class TestFetchPaginatedContainer:
    """Test _fetch_paginated_container error handling."""

    @pytest.mark.asyncio
    async def test_fetch_paginated_container_416_returns_none(self):
        """Test that 416 status returns (None, None) (lines 1128-1130)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create a mock response that raises 416 error
        response = MagicMock()
        response.status_code = 416

        http_error = httpx.HTTPStatusError(
            message="Range Not Satisfiable",
            request=MagicMock(),
            response=response,
        )

        # Mock the _execute_request method to raise 416 error
        client._execute_request = AsyncMock(side_effect=http_error)

        # Create a mock request
        mock_request = MagicMock(spec=httpx.Request)

        result = await client._fetch_paginated_container(
            request=mock_request,
            output_t=MagicMock,
            to_pagination_info_args=lambda x: {"page": 1},
        )

        # Should return (None, None) for 416 status
        assert result == (None, None)

    @pytest.mark.asyncio
    async def test_fetch_paginated_container_other_error_reraises(self):
        """Test that non-416 HTTPStatusError is re-raised (line 1131)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create a mock response that raises 500 error
        response = MagicMock()
        response.status_code = 500

        http_error = httpx.HTTPStatusError(
            message="Internal Server Error",
            request=MagicMock(),
            response=response,
        )

        # Mock the _execute_request method to raise 500 error
        client._execute_request = AsyncMock(side_effect=http_error)

        # Create a mock request
        mock_request = MagicMock(spec=httpx.Request)

        # Should re-raise the error for non-416 status codes (line 1131)
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client._fetch_paginated_container(
                request=mock_request,
                output_t=MagicMock,
                to_pagination_info_args=lambda x: {"page": 1},
            )

        assert exc_info.value.response.status_code == 500


class TestGetOfficerAppointments:
    """Test get_officer_appointments method."""

    @pytest.mark.asyncio
    async def test_get_officer_appointments_with_filter(self):
        """Test get_officer_appointments method with filter parameter (line 1069)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Mock the _fetch_paginated_container method
        client._fetch_paginated_container = AsyncMock(return_value=(None, None))

        # Create a mock result
        mock_result = MagicMock()

        # Mock the OfficerAppointments.from_api_paginated_list
        from ch_api.types.compound_api_types.public_data import officer_appointments

        original_method = officer_appointments.OfficerAppointments.from_api_paginated_list

        async def mock_from_api_paginated_list(fetch_page_fn, convert_item_fn):
            # Call the fetch_page_fn to ensure code path is executed
            from ch_api.types.pagination import types as pagination_types

            target = pagination_types.FetchPageCallArg(
                first_known_item=None,
                last_known_item=None,
                last_fetched_page=-1,
                current_total_list_len=0,
            )
            await fetch_page_fn(target)
            return mock_result

        officer_appointments.OfficerAppointments.from_api_paginated_list = staticmethod(mock_from_api_paginated_list)

        try:
            result = await client.get_officer_appointments(
                officer_id="officer123",
                filter="active",  # This triggers line 1069
            )

            # Verify result is returned
            assert result is mock_result
        finally:
            # Restore the original method
            officer_appointments.OfficerAppointments.from_api_paginated_list = original_method
