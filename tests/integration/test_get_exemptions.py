import httpx
import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_r5e_company_exemptions(live_env_test_client: ch_api.api.Client, r5e_company_number):
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await live_env_test_client.get_company_exemptions(r5e_company_number)
    assert exc_info.value.response.status_code == 404


@pytest.mark.asyncio
async def test_get_barclays_exemptions(live_env_test_client: ch_api.api.Client, barclays_plc_company_number):
    result = await live_env_test_client.get_company_exemptions(barclays_plc_company_number)  # Barclays PLC
    assert result
    assert result.exemptions.psc_exempt_as_trading_on_uk_regulated_market
