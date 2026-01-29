import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_appointments(live_env_test_client: ch_api.api.Client):
    result = await live_env_test_client.get_officer_appointments("_y4370DCOaJgIqvAlmHtJ7HdiqU")
    assert result
    out = await result.items.get_all()
    assert len(out) > 0
    assert result.name == "Paul BRESNIHAN"
