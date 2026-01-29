import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_psc_list(live_env_test_client: ch_api.api.Client, r5e_company_number):
    result = await live_env_test_client.get_company_psc_list(r5e_company_number)
    assert result
    assert result.active_count == 1
    assert result.ceased_count == 0
    all_data = await result.items.get_all()
    assert len(all_data) == 1
    assert all_data[0].name == "Mr Ilja Orlovs"


@pytest.mark.asyncio
async def test_get_lloyds_psc_list(live_env_test_client: ch_api.api.Client, lloyds_company_number):
    result = await live_env_test_client.get_company_psc_list(lloyds_company_number)
    assert result
    assert result.active_count == 1
    pscs = await result.items.get_all()
    assert len(pscs) == 1
    assert pscs[0].name == "Lloyds Banking Group Plc"


@pytest.mark.asyncio
async def test_get_r5e_statements(live_env_test_client: ch_api.api.Client, r5e_company_number):
    result = await live_env_test_client.get_company_psc_statements(r5e_company_number)
    assert result
    assert result.active_count == 0
    assert result.ceased_count == 0
    all_data = await result.items.get_all()
    # no statements for R5E
    assert len(all_data) == 0


@pytest.mark.asyncio
async def test_someones_psc_statements(live_env_test_client: ch_api.api.Client):
    result = await live_env_test_client.get_company_psc_statements("SC549056")
    assert result
    assert result.active_count > 0
    assert result.ceased_count == 0
    all_data = await result.items.get_all()
    assert len(all_data) == 1
    assert all_data[0].statement == "no-individual-or-entity-with-signficant-control"


@pytest.mark.asyncio
async def test_get_corporate_psc(live_env_test_client: ch_api.api.Client, lloyds_company_number):
    result = await live_env_test_client.get_company_corporate_psc(lloyds_company_number, "rTHhnY4-WO4nqU_grhl-RUEB6z0")
    assert result
    assert result.name == "Lloyds Banking Group Plc"


@pytest.mark.asyncio
async def test_get_individual_ben_owner(live_env_test_client: ch_api.api.Client):
    result = await live_env_test_client.get_company_individual_psc_beneficial_owner(
        "OE000003", "SZAhW70tVwifoSKtlDKjT9t_kcg"
    )
    assert result
    assert result.name == "Mr Michael Hanley"


@pytest.mark.asyncio
async def test_get_corporate_ben_owner(live_env_test_client: ch_api.api.Client):
    result = await live_env_test_client.get_company_corporate_psc_beneficial_owner(
        "OE027795", "VstvxOcTxg_Bpo0RWnj0BzoC9CM"
    )
    assert result
    assert result.name == "Oak Trust (Guernsey) Limited"


@pytest.mark.asyncio
async def test_get_legal_ben_owner(live_env_test_client: ch_api.api.Client):
    # PEOPLE'S BANK OF CHINA - Peoples Republic Of China
    result = await live_env_test_client.get_company_legal_person_psc_beneficial_owner(
        "OE023610", "tC4-Moq5xgafxiamsuUJylZO4SU"
    )
    assert result
    assert result.name == "Peoples Republic Of China"


@pytest.mark.asyncio
async def test_get_individual_psc(live_env_test_client: ch_api.api.Client, r5e_company_number):
    result = await live_env_test_client.get_company_individual_psc(r5e_company_number, "okPgMloal1WI0_Og6oKOaBbbyvE")
    assert result
    assert result.name == "Mr Ilja Orlovs"


@pytest.mark.asyncio
async def test_get_uk_legal_person_psc(live_env_test_client: ch_api.api.Client):
    result = await live_env_test_client.get_company_legal_person_psc("13249188", "ilKOJwF-P67FxYhB9CdNImuTsss")
    assert result
    assert result.name == "Government Of Catalonia"
