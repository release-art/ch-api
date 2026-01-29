import httpx
import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_r5e_company_insolvency(live_env_test_client: ch_api.api.Client, r5e_company_number):
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await live_env_test_client.get_company_insolvency(r5e_company_number)
    assert exc_info.value.response.status_code == 404


@pytest.mark.asyncio
async def test_get_john_insolvency(live_env_test_client: ch_api.api.Client):
    result = await live_env_test_client.get_company_insolvency("07560766")
    assert result
    assert len(result.cases) > 0
