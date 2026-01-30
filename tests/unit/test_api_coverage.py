"""Tests for API client methods to improve coverage."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

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


class TestGetCompanyRegistersNotFound:
    """Test get_company_registers with NOT_FOUND status."""

    @pytest.mark.asyncio
    async def test_get_company_registers_not_found_returns_none(self):
        """Test that 404 status returns None (lines 461)."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create a mock response that raises 404 error
        response = MagicMock()
        response.status_code = 404

        http_error = httpx.HTTPStatusError(
            message="Not Found",
            request=MagicMock(),
            response=response,
        )

        # Mock the API session
        mock_request = MagicMock()
        client._api_session.build_request = MagicMock(return_value=mock_request)
        client._api_session.send = AsyncMock(side_effect=http_error)

        result = await client.get_company_registers("12345678")

        # Should return None for 404 status
        assert result is None
