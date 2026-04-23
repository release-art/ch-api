import pytest

import ch_api


@pytest.mark.asyncio
async def test_get_r5e_company_filing_history(live_env_test_client: ch_api.api.Client, r5e_company_number):
    response = await live_env_test_client.get_company_filing_history(r5e_company_number, result_count=100)
    assert len(response.data) >= 8
    # Check that the name change filing is present
    for filing in response.data:
        if filing.category == "change-of-name":
            # the company changed its name to "R5E LIMITED" to "RELEASE.ART LIMITED" in 2026
            assert filing.type == "CERTNM"
            assert filing.date.year == 2026
            assert filing.links.document_metadata is not None
            break
    else:
        # No break encountered
        pytest.fail("No change-of-name filing found in filing history")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cetegory_filter, exp_result_count",
    [
        (None, 8),
        (["change-of-name"], 1),
        (["miscellaneous"], 0),
    ],
)
async def test_get_r5e_company_filing_history_w_filter(
    live_env_test_client: ch_api.api.Client,
    r5e_company_number,
    cetegory_filter,
    exp_result_count,
):
    response = await live_env_test_client.get_company_filing_history(
        r5e_company_number, categories=cetegory_filter, result_count=100
    )
    assert len(response.data) == exp_result_count


@pytest.mark.asyncio
async def test_get_filing_history_item(live_env_test_client: ch_api.api.Client, r5e_company_number):
    filing_item_response = await live_env_test_client.get_filing_history_item(
        r5e_company_number, "MzQ4NTMzOTIzOGFkaXF6a2N4"
    )
    assert filing_item_response.transaction_id == "MzQ4NTMzOTIzOGFkaXF6a2N4"
    assert filing_item_response.type == "AA"
    assert filing_item_response.category == "accounts"
