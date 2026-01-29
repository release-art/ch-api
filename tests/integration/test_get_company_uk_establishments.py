import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_r5e_establishments(live_env_test_client: ch_api.api.Client, r5e_company_number):
    response = await live_env_test_client.get_company_uk_establishments(r5e_company_number)
    assert len(response.items) == 0, "release.art does not have UK establishments"


@pytest.mark.asyncio
async def test_get_someones_establishments(live_env_test_client: ch_api.api.Client):
    response = await live_env_test_client.get_company_uk_establishments("FC030084")
    assert len(response.items) == 1
    assert response.items[0].company_name == "EBI"
