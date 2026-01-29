import ch_api


def test_simple():
    assert ch_api.api.Client is not None


# @pytest.mark.asyncio
# async def test_get_registered_office_address(raw_client):
#     response = await raw_client.registered_office_address("00000006")
#     assert response.status_code == 200
