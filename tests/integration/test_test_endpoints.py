import pytest

import ch_api


@pytest.fixture
def test_company_1():
    return ch_api.types.test_data_generator.CreateTestCompanyRequest()


# @pytest.mark.asyncio
# async def test_get_registered_office_address(test_client: ch_api.api.Client, test_company_1):
#     response = await test_client.create_test_company(test_company_1)
