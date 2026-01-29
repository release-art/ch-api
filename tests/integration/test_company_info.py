import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_company_profile(live_env_test_client: ch_api.api.Client, r5e_company_number):
    response = await live_env_test_client.get_company_profile(r5e_company_number)
    assert response is not None
    assert response.company_name == "RELEASE.ART LIMITED"
    assert response.company_number == r5e_company_number


@pytest.mark.asyncio
async def test_get_registered_office_address(live_env_test_client: ch_api.api.Client, r5e_company_number):
    response = await live_env_test_client.registered_office_address(r5e_company_number)
    assert response is not None
    assert response.postal_code == "EC1V 2NX"


@pytest.mark.asyncio
async def test_get_officer_list(live_env_test_client: ch_api.api.Client, r5e_company_number):
    officer_list = await live_env_test_client.get_officer_list(r5e_company_number)
    assert officer_list is not None
    all_officers = await officer_list.get_all()
    assert len(all_officers) == 1
    assert all_officers[0].name == "ORLOVS, Ilja"  # Hey there, it's me!


@pytest.mark.asyncio
async def test_get_officer_appointment(live_env_test_client: ch_api.api.Client, r5e_company_number):
    officer_appointment = await live_env_test_client.get_officer_appointment(
        r5e_company_number, "UndJhrGEDKSjtYtjKacokU1YApY"
    )
    assert officer_appointment.name == "ORLOVS, Ilja"  # Hey there, it's me!


@pytest.mark.asyncio
async def test_get_company_registers(live_env_test_client: ch_api.api.Client, r5e_company_number):
    company_registers = await live_env_test_client.get_company_registers(r5e_company_number)
    assert company_registers is None, "R5E ART LIMITED has no company registers"


@pytest.mark.asyncio
async def test_get_company_registers_barclays(live_env_test_client: ch_api.api.Client, barclays_plc_company_number):
    company_registers = await live_env_test_client.get_company_registers(barclays_plc_company_number)
    assert company_registers is None, "Barclays PLC has no company registers"


# TODO: find a company with company registers to test against
