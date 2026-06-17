import pytest


@pytest.fixture
def r5e_company_number():
    return "14200734"  # R5E art


@pytest.fixture
def barclays_plc_company_number():
    return "00048839"


@pytest.fixture
def lloyds_company_number():
    return "00002065"  # Lloyds Banking Group PLC


@pytest.fixture
def tesco_company_number():
    return "00445790"  # Tesco PLC


@pytest.fixture
def collect_pages():
    """Walk a MultipageList via ``get_next``, accumulating items.

    Returns an async helper ``collect(page, minimum=None)`` that follows the
    ``get_next`` chain until at least ``minimum`` items are gathered (or every
    page is exhausted when ``minimum`` is None).
    """

    async def _collect(page, minimum=None):
        items = list(page.data)
        while (minimum is None or len(items) < minimum) and page.pagination.has_next:
            page = await page.get_next()
            items.extend(page.data)
        return items

    return _collect
