import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_r5e_company_charges(live_env_test_client: ch_api.api.Client, r5e_company_number):
    response = await live_env_test_client.get_company_charges(r5e_company_number)
    assert response
    assert response.total_count == 0, "Hopefully this company has no charges!"
    assert not response.items


@pytest.fixture
def ipc_company_number():
    # https://find-and-update.company-information.service.gov.uk/company/09759161/charges
    # They have 13 charges as of Jan 2026
    return "09759161"


@pytest.mark.asyncio
async def test_get_ipc_company_charges(live_env_test_client: ch_api.api.Client, ipc_company_number):
    response = await live_env_test_client.get_company_charges(ipc_company_number)
    assert response
    assert response.total_count == 13, "This company should have 13 charges!"
    assert len(response.items) == 13


@pytest.mark.asyncio
async def test_get_ipc_company_charge_details(live_env_test_client: ch_api.api.Client, ipc_company_number):
    response = await live_env_test_client.get_company_charge_details(ipc_company_number, "HVTZfIRVvr6JnB-wvL9VxKRuzLM")
    assert response
    assert response.charge_number == 12
