import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_r5e_company_insolvency(live_env_test_client: ch_api.api.Client, r5e_company_number):
    result = await live_env_test_client.get_company_insolvency(r5e_company_number)
    assert result is None


@pytest.mark.asyncio
async def test_get_john_insolvency(live_env_test_client: ch_api.api.Client):
    result = await live_env_test_client.get_company_insolvency("07560766")
    assert result
    assert len(result.cases) > 0
