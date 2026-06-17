import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_appointments(live_env_test_client: ch_api.api.Client):
    result = await live_env_test_client.get_officer_appointments("_y4370DCOaJgIqvAlmHtJ7HdiqU", result_count=100)
    assert result
    assert len(result.data) > 0
