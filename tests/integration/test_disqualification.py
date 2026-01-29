import pytest

import ch_api


@pytest.mark.asyncio
async def test_natural_disq(live_env_test_client: ch_api.api.Client):
    response = await live_env_test_client.get_natural_officer_disqualification("z5BD9sANUiUtsFTa5vRE6yZlA4s")
    assert response
    assert response.forename == "Paul"


@pytest.mark.asyncio
async def test_corporate_disq(live_env_test_client: ch_api.api.Client):
    response = await live_env_test_client.get_corporate_officer_disqualification("DaL_5s20VD_N3rszcL92RD4RwOM")
    assert response
    assert response.name == "WAATASSIMOU FOUNDATION"
