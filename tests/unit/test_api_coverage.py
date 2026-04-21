"""Tests for API client methods."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from ch_api import api, api_settings
from ch_api.types import test_data_generator


class TestCreateTestCompany:
    """Test create_test_company method."""

    @pytest.mark.asyncio
    async def test_create_test_company_success(self):
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth, settings=api_settings.TEST_API_SETTINGS)

        response_data = MagicMock()
        client._execute_request = AsyncMock(return_value=response_data)

        company = test_data_generator.CreateTestCompanyRequest(
            company_name="Test Company Ltd",
            company_number="12345678",
        )

        result = await client.create_test_company(company)

        assert result == response_data
        client._execute_request.assert_called_once()

        call_args = client._execute_request.call_args
        request = call_args[0][0]
        assert request.method == "POST"
        assert "test-companies" in request.url.path

    @pytest.mark.asyncio
    async def test_create_test_company_no_url_raises_error(self):
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth, settings=api_settings.LIVE_API_SETTINGS)

        company = test_data_generator.CreateTestCompanyRequest(
            company_name="Test Company Ltd",
            company_number="12345678",
        )

        with pytest.raises(RuntimeError) as exc_info:
            await client.create_test_company(company)

        assert "Test Data Generator URL is not configured" in str(exc_info.value)
