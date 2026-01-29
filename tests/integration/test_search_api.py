import datetime

import pytest

import ch_api


class TestGenericSearch:
    @pytest.mark.asyncio
    async def test_search_company(self, live_env_test_client: ch_api.api.Client, r5e_company_number):
        search_response = await live_env_test_client.search("R5E ART LIMITED")
        all_data = await search_response.get_all()
        assert len(all_data) > 300

        one_found = False
        for el in all_data:
            if el.company_number == r5e_company_number:
                one_found = True
                break
        assert one_found, f"Company number {r5e_company_number} not found in search results"

    @pytest.mark.asyncio
    async def test_search_director(self, live_env_test_client: ch_api.api.Client):
        search_response = await live_env_test_client.search("Orlovs")
        all_data = await search_response.get_all()
        assert len(all_data) > 50

        one_found = False
        for el in all_data:
            if not isinstance(el, ch_api.types.public_data.search.OfficerSearchItem):
                continue
            if el.title == "Ilja ORLOVS":
                one_found = el
                break
        assert one_found


class TestAdvancedSearch:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "query, expected_count",
        [
            ({"company_name_includes": "RELEASE.ART LIMITED"}, 1),
            ({"company_name_includes": "Nonexistent Company 123456789"}, 0),
            (
                {
                    "company_name_includes": "RELEASE.ART LIMITED",
                    "company_name_excludes": "potato",
                },
                1,
            ),
            (
                {
                    "company_name_includes": "RELEASE.ART LIMITED",
                    "incorporated_from": datetime.date(2000, 1, 1),
                },
                1,
            ),
            (
                {
                    "company_name_includes": "RELEASE.ART LIMITED",
                    "incorporated_from": datetime.date(2000, 1, 1),
                    "incorporated_to": datetime.date(2001, 1, 1),
                },
                0,
            ),
        ],
    )
    async def test_simple(self, live_env_test_client: ch_api.api.Client, query, expected_count):
        search_response = await live_env_test_client.advanced_company_search(**query)
        if expected_count == 0:
            assert search_response.top_hit is None
        else:
            assert search_response.top_hit is not None
        all_data = await search_response.items.get_all()
        assert len(all_data) == expected_count


@pytest.mark.asyncio
async def test_alphabetical_companies_search(live_env_test_client: ch_api.api.Client):
    result = await live_env_test_client.alphabetical_companies_search("Barclays", page_size=100)
    assert result.top_hit is not None
    all_data = await result.items.get_all()
    assert len(all_data) >= 100
    all_names = [el.company_name for el in all_data]
    assert all("BARCLAY" in name.upper() for name in all_names)


@pytest.mark.asyncio
async def test_search_companies(live_env_test_client: ch_api.api.Client, r5e_company_number):
    search_response = await live_env_test_client.search_companies("R5E ART LIMITED")
    all_data = await search_response.get_all()
    assert len(all_data) > 300

    one_found = False
    for el in all_data:
        assert isinstance(el, ch_api.types.public_data.search.CompanySearchItem)
        if el.company_number == r5e_company_number:
            one_found = True
            break
    assert one_found, f"Company number {r5e_company_number} not found in search results"


@pytest.mark.asyncio
async def test_search_officers(live_env_test_client: ch_api.api.Client):
    search_response = await live_env_test_client.search_officers("Ilja Orlovs")
    all_data = await search_response.get_all()
    assert len(all_data) > 10

    one_found = False
    for el in all_data:
        assert isinstance(el, ch_api.types.public_data.search.OfficerSearchItem)
        if el.title == "Ilja ORLOVS":
            one_found = True
            break
    assert one_found


@pytest.mark.asyncio
async def test_search_disqualified_officers(live_env_test_client: ch_api.api.Client):
    search_response = await live_env_test_client.search_disqualified_officers("bob")
    all_data = await search_response.get_all()
    assert len(all_data) > 0

    one_found = False
    for el in all_data:
        assert isinstance(el, ch_api.types.public_data.search.DisqualifiedOfficerSearchItem)
        if el.title == "Bobby KALIA":
            one_found = True
            break
    assert one_found


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query_type, exp_company_name",
    [
        ("alphabetical", "BOAZ OFRI FILM PRODUCTIONS LTD."),
        ("best-match", "BOB INTERNATIONAL LIMITED"),
        ("previous-name-dissolved", "G. & H. MOTOR ENGINEERS LIMITED"),
    ],
)
async def test_search_dissolved_companies(live_env_test_client: ch_api.api.Client, query_type, exp_company_name):
    search_response = await live_env_test_client.search_dissolved_companies("bob", type=query_type)
    assert search_response.top_hit is not None
    all_data = await search_response.items.get_all()
    assert len(all_data) >= 10
