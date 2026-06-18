"""Branch coverage tests for api.py — covers all remaining uncovered lines."""

import datetime
import json
from unittest.mock import MagicMock

import httpx
import pydantic
import pytest

from ch_api import api, api_settings, exc
from ch_api.types.pagination import types as pagination_types
from ch_api.types.public_data import (
    search as search_types,
    search_companies as sc,
)


def _make_client(serializer=None):
    auth = api_settings.AuthSettings(api_key="test-key")
    return api.Client(
        credentials=auth,
        settings=api_settings.LIVE_API_SETTINGS,
        page_token_serializer=serializer,
    )


def _http_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "http://example.com")
    response = httpx.Response(status, request=request)
    return httpx.HTTPStatusError("error", request=request, response=response)


def _alpha_company(cursor: str = "KEY:12345678") -> sc.AlphabeticalCompany:
    return sc.AlphabeticalCompany(
        company_name="Test Co",
        company_number="12345678",
        company_status="active",
        company_type="ltd",
        links=sc.AlphabeticalCompanyLinks(),
        ordered_alpha_key_with_id=cursor,
        kind="search-results#alphabetical-search",
    )


def _dissolved_company() -> sc.DissolvedCompany:
    return sc.DissolvedCompany(
        company_name="Old Co",
        company_number="12345678",
        date_of_cessation=datetime.date(2020, 1, 1),
        date_of_creation=datetime.date(2010, 1, 1),
        ordered_alpha_key_with_id="OLD:12345678",
    )


class TestPageTokenSerializer:
    """Lines 313, 320 — serialize/deserialize via PageTokenSerializer."""

    def test_encode_calls_serialize(self):
        """Line 313: serializer.serialize is called."""
        serializer = MagicMock()
        serializer.serialize = MagicMock(return_value="ENCRYPTED")
        client = _make_client(serializer=serializer)
        state = pagination_types._PageState(start_index=5)
        result = client._encode_next_page(state)
        assert result == "ENCRYPTED"
        serializer.serialize.assert_called_once()

    def test_decode_calls_deserialize(self):
        """Line 320: serializer.deserialize is called."""
        raw = pagination_types._PageState(start_index=5).encode()
        serializer = MagicMock()
        serializer.deserialize = MagicMock(return_value=raw)
        client = _make_client(serializer=serializer)
        state = client._decode_next_page("ENCRYPTED")
        assert state.start_index == 5
        serializer.deserialize.assert_called_once_with("ENCRYPTED")


class TestPageSizeBoundsEnforced:
    """page_size bounds must actually be enforced (regression: conint nested in
    Annotated silently dropped the constraint — Field is required)."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("page_size", [0, 999])
    async def test_search_companies_rejects_out_of_range(self, page_size):
        client = _make_client()
        with pytest.raises(pydantic.ValidationError):
            await client.search_companies("x", page_size=page_size)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("page_size", [0, 101])
    async def test_filing_history_rejects_out_of_range(self, page_size):
        client = _make_client()
        with pytest.raises(pydantic.ValidationError):
            await client.get_company_filing_history("12345678", page_size=page_size)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("page_size", [0, 5001])
    async def test_advanced_search_rejects_out_of_range(self, page_size):
        client = _make_client()
        with pytest.raises(pydantic.ValidationError):
            await client.advanced_company_search(company_name_includes="x", page_size=page_size)


class TestFetchNextPage:
    """Self-contained next_page token: stateless resume via Client.fetch_next_page."""

    @pytest.mark.asyncio
    async def test_token_is_self_contained_and_resumes(self):
        """Token embeds endpoint + params; fetch_next_page resumes from token alone."""
        client = _make_client()
        urls = []

        async def fake(url, result_type):
            urls.append(url)
            result = MagicMock()
            result.items = [search_types.CompanySearchItem.model_construct() for _ in range(2)]
            result.total_results = 4
            return result

        client._get_resource = fake
        page = await client.search_companies("Apple", page_size=2)
        token = page.pagination.next_page
        decoded = json.loads(token)
        assert decoded["endpoint"] == "search_companies"
        assert decoded["params"]["query"] == "Apple"
        assert decoded["params"]["page_size"] == 2
        assert decoded["start_index"] == 2

        urls.clear()
        # a fresh call with ONLY the token — no query re-supplied
        page2 = await client.fetch_next_page(token)
        assert len(page2.data) == 2
        assert any("start_index=2" in u and "q=Apple" in u for u in urls)

    @pytest.mark.asyncio
    async def test_cursor_token_is_self_contained(self):
        """Cursor endpoints embed endpoint + params + search_below."""
        client = _make_client()
        calls = 0

        async def fake(url, result_type):
            nonlocal calls
            calls += 1
            result = MagicMock()
            result.items = [_alpha_company("KEY:1")] if calls == 1 else []
            return result

        client._get_resource = fake
        page = await client.alphabetical_companies_search("Barclays", page_size=1)
        decoded = json.loads(page.pagination.next_page)
        assert decoded["endpoint"] == "alphabetical_companies_search"
        assert decoded["search_below"] == "KEY:1"
        assert decoded["params"]["query"] == "Barclays"

    @pytest.mark.asyncio
    async def test_date_params_round_trip(self):
        """datetime.date args serialise to ISO and coerce back on resume."""
        client = _make_client()
        urls = []

        async def fake(url, result_type):
            urls.append(url)
            result = MagicMock()
            result.items = [sc.AdvancedCompany.model_construct() for _ in range(2)]
            result.hits = 4
            return result

        client._get_resource = fake
        page = await client.advanced_company_search(
            company_name_includes="x", dissolved_from=datetime.date(2020, 1, 1), page_size=2
        )
        assert json.loads(page.pagination.next_page)["params"]["dissolved_from"] == "2020-01-01"

        urls.clear()
        await client.fetch_next_page(page.pagination.next_page)  # must coerce "2020-01-01" -> date
        assert any("dissolved_from=2020-01-01" in u for u in urls)

    @pytest.mark.asyncio
    async def test_tampered_endpoint_rejected(self):
        """A token naming a non-resumable method is rejected (no arbitrary dispatch)."""
        client = _make_client()
        bad = json.dumps({"endpoint": "aclose", "params": {}, "start_index": 0})
        with pytest.raises(ValueError, match="resumable endpoint"):
            await client.fetch_next_page(bad)

    @pytest.mark.asyncio
    async def test_resume_via_serializer(self):
        """fetch_next_page works through a PageTokenSerializer (opaque/encrypted token)."""
        serializer = MagicMock()
        serializer.serialize = lambda t: "ENC:" + t
        serializer.deserialize = lambda t: t[len("ENC:") :]
        client = _make_client(serializer=serializer)
        urls = []

        async def fake(url, result_type):
            urls.append(url)
            result = MagicMock()
            result.items = [search_types.CompanySearchItem.model_construct() for _ in range(2)]
            result.total_results = 4
            return result

        client._get_resource = fake
        page = await client.search_companies("Apple", page_size=2)
        assert page.pagination.next_page.startswith("ENC:")

        urls.clear()
        await client.fetch_next_page(page.pagination.next_page)
        assert any("start_index=2" in u for u in urls)

    @pytest.mark.asyncio
    async def test_with_client_rebinds_get_next(self):
        """A page with no client can be re-bound so get_next works again."""
        client = _make_client()

        async def fake(url, result_type):
            result = MagicMock()
            result.items = [search_types.CompanySearchItem.model_construct() for _ in range(2)]
            result.total_results = 4
            return result

        client._get_resource = fake
        page = await client.search_companies("Apple", page_size=2)
        # simulate a reconstructed page that lost its client binding
        page._client = None
        with pytest.raises(RuntimeError, match="no client bound"):
            await page.get_next()
        page.with_client(client)
        page2 = await page.get_next()
        assert len(page2.data) == 2


class TestMultipageListGetNext:
    """MultipageList.get_next error paths on manually-constructed instances."""

    @pytest.mark.asyncio
    async def test_get_next_on_last_page_raises_no_more_pages(self):
        """has_next is False → NoMorePagesError."""
        page = pagination_types.MultipageList(
            data=[],
            pagination=pagination_types.PaginationInfo(has_next=False),
        )
        with pytest.raises(exc.NoMorePagesError):
            await page.get_next()

    @pytest.mark.asyncio
    async def test_get_next_without_client_raises_runtime_error(self):
        """has_next True but no bound client (e.g. deserialized) → RuntimeError."""
        page = pagination_types.MultipageList(
            data=[],
            pagination=pagination_types.PaginationInfo(has_next=True, next_page="tok"),
        )
        with pytest.raises(RuntimeError, match="no client bound"):
            await page.get_next()


class TestOffsetPagination:
    """Offset accumulation to result_count + get_next advances the batch via fetch_next_page."""

    @pytest.mark.asyncio
    async def test_get_next_offset(self):
        """get_next fetches the next batch from the next offset (page_size 2, total 4)."""
        client = _make_client()
        urls = []

        async def fake(url, result_type):
            urls.append(url)
            result = MagicMock()
            result.items = [search_types.CompanySearchItem.model_construct() for _ in range(2)]
            result.total_results = 4
            return result

        client._get_resource = fake
        page = await client.search_companies("x", page_size=2)
        assert len(page.data) == 2
        assert page.pagination.has_next
        assert any("start_index=0" in u for u in urls)

        urls.clear()
        page2 = await page.get_next()
        assert len(page2.data) == 2
        assert not page2.pagination.has_next
        assert any("start_index=2" in u for u in urls)


class TestCursorPaginationContinuation:
    """Cursor accumulation loop continuation (result_count spanning pages)."""

    @pytest.mark.asyncio
    async def test_cursor_loop_continues(self):
        """result_count spanning pages drives a second loop iteration (cursor = next_cursor)."""
        client = _make_client()
        calls = 0

        async def fake(url, result_type):
            nonlocal calls
            calls += 1
            result = MagicMock()
            result.items = [_alpha_company(f"KEY:{calls}")] if calls <= 2 else []
            return result

        client._get_resource = fake
        page = await client.alphabetical_companies_search("q", page_size=1, result_count=2)
        assert len(page.data) == 2  # accumulated across two cursor pages
        assert calls == 2
        assert page.pagination.has_next


class TestAlphabeticalSearchBranches:
    """Lines 719, 729 — search_below param + empty items in alphabetical search."""

    @pytest.mark.asyncio
    async def test_search_below_added_via_fetch_next_page(self):
        """Resuming a cursor token via fetch_next_page adds the search_below param."""
        client = _make_client()
        token = client._encode_next_page(
            pagination_types._PageState(
                search_below="KEY:12345678",
                endpoint="alphabetical_companies_search",
                params={"query": "test", "page_size": 10, "result_count": 1},
            )
        )
        urls_seen = []

        async def fake_get_resource(url, result_type):
            urls_seen.append(url)
            return MagicMock(items=[])

        client._get_resource = fake_get_resource
        await client.fetch_next_page(token)
        assert any("search_below=KEY%3A12345678" in u or "search_below=KEY:12345678" in u for u in urls_seen)

    @pytest.mark.asyncio
    async def test_empty_items_returns_none_cursor(self):
        """Line 729: empty items from API → return [], None stops pagination."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return MagicMock(items=[])

        client._get_resource = fake_get_resource
        page = await client.alphabetical_companies_search("test")
        assert page.data == []
        assert not page.pagination.has_next

    @pytest.mark.asyncio
    async def test_none_result_stops_pagination(self):
        """Line 727: None result → items = [] → stops pagination."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.alphabetical_companies_search("test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_get_next_via_alphabetical_search_uses_search_below(self):
        """alphabetical_companies_search: get_next carries the search_below cursor."""
        client = _make_client()
        call_count = 0
        item = _alpha_company("KEY_ALPHA:00000001")
        urls_seen = []

        async def fake_get_resource(url, result_type):
            nonlocal call_count
            call_count += 1
            urls_seen.append(url)
            result = MagicMock()
            result.items = [item] if call_count == 1 else []
            return result

        client._get_resource = fake_get_resource
        page = await client.alphabetical_companies_search("test", page_size=1)
        assert len(page.data) == 1
        assert page.pagination.has_next
        assert call_count == 1

        page2 = await page.get_next()
        assert page2.data == []
        assert call_count == 2
        assert any("search_below=KEY_ALPHA" in u for u in urls_seen)


class TestDissolvedSearchBranches:
    """Lines 766, 776 — search_below param + empty items in dissolved search."""

    @pytest.mark.asyncio
    async def test_search_below_added_via_fetch_next_page(self):
        """Resuming a cursor token via fetch_next_page adds the search_below param."""
        client = _make_client()
        token = client._encode_next_page(
            pagination_types._PageState(
                search_below="OLD:12345678",
                endpoint="search_dissolved_companies",
                params={"query": "test", "page_size": 10, "type": "alphabetical", "result_count": 1},
            )
        )
        urls_seen = []

        async def fake_get_resource(url, result_type):
            urls_seen.append(url)
            return MagicMock(items=[])

        client._get_resource = fake_get_resource
        await client.fetch_next_page(token)
        assert any("search_below" in u for u in urls_seen)

    @pytest.mark.asyncio
    async def test_empty_items_returns_none_cursor(self):
        """Line 776: empty items → return [], None stops pagination."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return MagicMock(items=[])

        client._get_resource = fake_get_resource
        page = await client.search_dissolved_companies("test")
        assert page.data == []


class TestOfficerListBranches:
    """Line 540 — only_type param; lines 553-558 — 416/None branches."""

    @pytest.mark.asyncio
    async def test_only_type_adds_register_params(self):
        """Line 540: query_params gets register_type and register_view."""
        client = _make_client()
        urls_seen = []

        async def fake_get_resource(url, result_type):
            urls_seen.append(url)
            return MagicMock(items=[], total_results=0)

        client._get_resource = fake_get_resource
        await client.get_officer_list("12345678", only_type="directors")
        assert any("register_type=directors" in u for u in urls_seen)
        assert any("register_view=true" in u for u in urls_seen)

    @pytest.mark.asyncio
    async def test_416_returns_empty(self):
        """Lines 553-556: 416 → return [], None."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.get_officer_list("12345678")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_none_result_returns_empty(self):
        """Lines 557-558: result is None → return [], None."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.get_officer_list("12345678")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_non_416_http_error_propagates(self):
        """Line 556: non-416 error re-raised."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(500)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_officer_list("12345678")


class TestSearchBranches:
    """Lines 611-616 — search() 416/None branches."""

    @pytest.mark.asyncio
    async def test_search_416_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.search("test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_search_none_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.search("test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_search_non_416_propagates(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(403)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.search("test")


class TestAdvancedSearchParams:
    """Lines 645-668 — optional params for advanced_company_search."""

    @pytest.mark.asyncio
    async def test_company_status_str_coerced_to_list(self):
        """Lines 646-648: str status → list."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            assert "company_status=active" in url
            return MagicMock(items=[], hits=0)

        client._get_resource = fake_get_resource
        await client.advanced_company_search(company_status="active")

    @pytest.mark.asyncio
    async def test_company_status_sequence(self):
        """Lines 645-648: sequence passes through."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            assert "company_status" in url
            return MagicMock(items=[], hits=0)

        client._get_resource = fake_get_resource
        await client.advanced_company_search(company_status=["active", "dissolved"])

    @pytest.mark.asyncio
    async def test_company_type_str(self):
        """Lines 649-652: str type → list."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            assert "company_type=ltd" in url
            return MagicMock(items=[], hits=0)

        client._get_resource = fake_get_resource
        await client.advanced_company_search(company_type="ltd")

    @pytest.mark.asyncio
    async def test_company_subtype_str(self):
        """Lines 653-656: str subtype → list."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            assert "company_subtype" in url
            return MagicMock(items=[], hits=0)

        client._get_resource = fake_get_resource
        await client.advanced_company_search(company_subtype="community-interest-company")

    @pytest.mark.asyncio
    async def test_dissolved_from_to(self):
        """Lines 657-660: dissolved_from/to dates."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            assert "dissolved_from=2020-01-01" in url
            assert "dissolved_to=2021-01-01" in url
            return MagicMock(items=[], hits=0)

        client._get_resource = fake_get_resource
        await client.advanced_company_search(
            dissolved_from=datetime.date(2020, 1, 1),
            dissolved_to=datetime.date(2021, 1, 1),
        )

    @pytest.mark.asyncio
    async def test_location_param(self):
        """Lines 665-666: location param."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            assert "location=London" in url
            return MagicMock(items=[], hits=0)

        client._get_resource = fake_get_resource
        await client.advanced_company_search(location="London")

    @pytest.mark.asyncio
    async def test_sic_codes_param(self):
        """Lines 667-668: sic_codes param."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            assert "sic_codes" in url
            return MagicMock(items=[], hits=0)

        client._get_resource = fake_get_resource
        await client.advanced_company_search(sic_codes=["62012"])

    @pytest.mark.asyncio
    async def test_page_size_adds_size_param(self):
        """page_size is forwarded as the ``size`` query parameter."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            assert "size=50" in url
            return MagicMock(items=[], hits=0)

        client._get_resource = fake_get_resource
        await client.advanced_company_search(company_name_includes="test", page_size=50)

    @pytest.mark.asyncio
    async def test_416_returns_empty(self):
        """Lines 681-684: 416 → return [], None."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.advanced_company_search(company_name_includes="test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_none_returns_empty(self):
        """Lines 685-686: result is None."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.advanced_company_search(company_name_includes="test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_non_416_propagates(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(500)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.advanced_company_search(company_name_includes="test")


class TestSearchCompaniesBranches:
    """Lines 813-818 — search_companies() 416/None branches."""

    @pytest.mark.asyncio
    async def test_416_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.search_companies("test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_none_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.search_companies("test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_non_416_propagates(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(401)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.search_companies("test")


class TestSearchOfficersBranches:
    """Lines 854-859 — search_officers() 416/None branches."""

    @pytest.mark.asyncio
    async def test_416_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.search_officers("test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_none_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.search_officers("test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_non_416_propagates(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(429)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.search_officers("test")


class TestSearchDisqualifiedOfficersBranches:
    """Lines 895-900 — search_disqualified_officers() 416/None branches."""

    @pytest.mark.asyncio
    async def test_416_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.search_disqualified_officers("test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_none_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.search_disqualified_officers("test")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_non_416_propagates(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(503)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.search_disqualified_officers("test")


class TestFilingHistoryBranches:
    """Lines 1002-1007 — get_company_filing_history() 416/None branches."""

    @pytest.mark.asyncio
    async def test_416_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.get_company_filing_history("12345678")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_none_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.get_company_filing_history("12345678")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_non_416_propagates(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(404)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_company_filing_history("12345678")


class TestOfficerAppointmentsBranches:
    """Lines 1152, 1156-1161 — filter param + 416/None branches."""

    @pytest.mark.asyncio
    async def test_filter_active_adds_param(self):
        """Line 1152: filter param added to query."""
        client = _make_client()
        urls_seen = []

        async def fake_get_resource(url, result_type):
            urls_seen.append(url)
            return MagicMock(items=[], total_results=0)

        client._get_resource = fake_get_resource
        await client.get_officer_appointments("_y4370DCOaJgIqvAlmHtJ7HdiqU", filter="active")
        assert any("filter=active" in u for u in urls_seen)

    @pytest.mark.asyncio
    async def test_416_returns_empty(self):
        """Lines 1156-1159: 416 → return [], None."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.get_officer_appointments("_y4370DCOaJgIqvAlmHtJ7HdiqU")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_none_returns_empty(self):
        """Lines 1160-1161: result is None."""
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.get_officer_appointments("_y4370DCOaJgIqvAlmHtJ7HdiqU")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_non_416_propagates(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(403)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_officer_appointments("_y4370DCOaJgIqvAlmHtJ7HdiqU")


class TestPscListBranches:
    """Lines 1224-1229 — get_company_psc_list() 416/None branches."""

    @pytest.mark.asyncio
    async def test_416_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.get_company_psc_list("12345678")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_none_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.get_company_psc_list("12345678")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_non_416_propagates(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(500)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_company_psc_list("12345678")


class TestPscStatementsBranches:
    """Lines 1270-1275 — get_company_psc_statements() 416/None branches."""

    @pytest.mark.asyncio
    async def test_416_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(416)

        client._get_resource = fake_get_resource
        page = await client.get_company_psc_statements("12345678")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_none_returns_empty(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            return None

        client._get_resource = fake_get_resource
        page = await client.get_company_psc_statements("12345678")
        assert page.data == []

    @pytest.mark.asyncio
    async def test_non_416_propagates(self):
        client = _make_client()

        async def fake_get_resource(url, result_type):
            raise _http_error(500)

        client._get_resource = fake_get_resource
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_company_psc_statements("12345678")


class TestSessionRestart:
    """_execute_request auto-restarts closed sessions (owns_session=True only)."""

    @pytest.mark.asyncio
    async def test_restarts_owned_session_on_closed_error(self, mocker):
        """Closed session is replaced and the request is retried successfully."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth, settings=api_settings.LIVE_API_SETTINGS)

        ok_response = httpx.Response(200, content=b"{}", request=httpx.Request("GET", "http://x"))

        closed_session = MagicMock()
        closed_session.build_request = MagicMock(return_value=httpx.Request("GET", "http://x"))
        closed_session.send = mocker.AsyncMock(
            side_effect=RuntimeError("Cannot send a request, as the client has been closed.")
        )

        fresh_session = MagicMock()
        fresh_session.build_request = MagicMock(return_value=httpx.Request("GET", "http://x"))
        fresh_session.send = mocker.AsyncMock(return_value=ok_response)

        client._api_session = closed_session
        client._new_session = MagicMock(return_value=fresh_session)

        # _execute_request should survive the closed-session error and return None (404-free 200)
        request = httpx.Request("GET", "http://example.com")
        await client._execute_request(request, None)

        client._new_session.assert_called_once()
        assert client._api_session is fresh_session

    @pytest.mark.asyncio
    async def test_non_closed_runtime_error_propagates(self, mocker):
        """RuntimeError unrelated to session state is re-raised."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth, settings=api_settings.LIVE_API_SETTINGS)

        broken_session = MagicMock()
        broken_session.send = mocker.AsyncMock(side_effect=RuntimeError("some other problem"))
        client._api_session = broken_session

        request = httpx.Request("GET", "http://example.com")
        with pytest.raises(RuntimeError, match="some other problem"):
            await client._execute_request(request, None)

    @pytest.mark.asyncio
    async def test_closed_error_on_external_session_propagates(self, mocker):
        """Closed-session error is NOT swallowed when the session is externally owned."""
        # Pass an AsyncClient directly → _owns_session = False
        external_session = httpx.AsyncClient()
        client = api.Client(credentials=external_session, settings=api_settings.LIVE_API_SETTINGS)

        broken_session = MagicMock()
        broken_session.send = mocker.AsyncMock(
            side_effect=RuntimeError("Cannot send a request, as the client has been closed.")
        )
        client._api_session = broken_session

        request = httpx.Request("GET", "http://example.com")
        with pytest.raises(RuntimeError, match="has been closed"):
            await client._execute_request(request, None)

        await external_session.aclose()


class TestDocumentApi:
    """Lines 1084-1156 — get_document_metadata + get_document_url."""

    @pytest.mark.asyncio
    async def test_get_document_metadata_calls_correct_url(self):
        client = _make_client()
        urls_seen = []

        async def fake_get_resource(url, result_type):
            urls_seen.append(url)
            return None

        client._get_resource = fake_get_resource
        result = await client.get_document_metadata("DOC123")
        assert result is None
        assert any("document-api" in u and "DOC123" in u for u in urls_seen)

    @pytest.mark.asyncio
    async def test_get_document_url_returns_location_on_302(self, mocker):
        client = _make_client()
        redirect_response = httpx.Response(
            302,
            headers={"Location": "https://s3.example.com/doc.pdf"},
            request=httpx.Request("GET", "http://x"),
        )
        client._api_session.send = mocker.AsyncMock(return_value=redirect_response)

        url = await client.get_document_url("DOC123", content_type="application/pdf")
        assert url == "https://s3.example.com/doc.pdf"

    @pytest.mark.asyncio
    async def test_get_document_url_returns_location_on_301(self, mocker):
        client = _make_client()
        redirect_response = httpx.Response(
            301,
            headers={"Location": "https://s3.example.com/doc.pdf"},
            request=httpx.Request("GET", "http://x"),
        )
        client._api_session.send = mocker.AsyncMock(return_value=redirect_response)

        url = await client.get_document_url("DOC123")
        assert url == "https://s3.example.com/doc.pdf"

    @pytest.mark.asyncio
    async def test_get_document_url_returns_none_on_404(self, mocker):
        client = _make_client()
        not_found = httpx.Response(404, request=httpx.Request("GET", "http://x"))
        client._api_session.send = mocker.AsyncMock(return_value=not_found)

        url = await client.get_document_url("DOC_MISSING")
        assert url is None

    @pytest.mark.asyncio
    async def test_get_document_url_raises_on_error_status(self, mocker):
        client = _make_client()
        error_response = httpx.Response(406, request=httpx.Request("GET", "http://x"))
        client._api_session.send = mocker.AsyncMock(return_value=error_response)

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_document_url("DOC123", content_type="text/plain")

    @pytest.mark.asyncio
    async def test_get_document_url_unexpected_200_returns_location(self, mocker):
        """Unexpected non-redirect 200: return Location if present."""
        client = _make_client()
        ok_response = httpx.Response(
            200,
            headers={"Location": "https://s3.example.com/doc.pdf"},
            request=httpx.Request("GET", "http://x"),
        )
        client._api_session.send = mocker.AsyncMock(return_value=ok_response)

        url = await client.get_document_url("DOC123")
        assert url == "https://s3.example.com/doc.pdf"

    @pytest.mark.asyncio
    async def test_get_document_url_session_restart(self, mocker):
        """Closed session is restarted for document URL requests too."""
        client = _make_client()
        redirect_response = httpx.Response(
            302,
            headers={"Location": "https://s3.example.com/doc.pdf"},
            request=httpx.Request("GET", "http://x"),
        )
        fresh_session = MagicMock()
        fresh_session.build_request = MagicMock(return_value=httpx.Request("GET", "http://x"))
        fresh_session.send = mocker.AsyncMock(return_value=redirect_response)

        client._api_session.send = mocker.AsyncMock(
            side_effect=RuntimeError("Cannot send a request, as the client has been closed.")
        )
        client._new_session = MagicMock(return_value=fresh_session)

        url = await client.get_document_url("DOC123")
        assert url == "https://s3.example.com/doc.pdf"
        client._new_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_document_url_non_closed_runtime_error_propagates(self, mocker):
        """RuntimeError unrelated to session state is re-raised in get_document_url."""
        client = _make_client()
        client._api_session.send = mocker.AsyncMock(side_effect=RuntimeError("some other error"))

        with pytest.raises(RuntimeError, match="some other error"):
            await client.get_document_url("DOC123")

    @pytest.mark.asyncio
    async def test_get_document_content_yields_response_on_success(self, mocker):
        """get_document_content yields the httpx.Response within the context block."""
        client = _make_client()
        client.get_document_url = mocker.AsyncMock(return_value="https://s3.example.com/doc.pdf")

        fake_response = httpx.Response(200, content=b"%PDF fake content", request=httpx.Request("GET", "http://x"))
        mock_instance = mocker.AsyncMock()
        mock_instance.__aenter__ = mocker.AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = mocker.AsyncMock(return_value=False)
        mock_instance.get = mocker.AsyncMock(return_value=fake_response)
        mocker.patch("httpx.AsyncClient", return_value=mock_instance)

        async with client.get_document_content("DOC123", content_type="application/pdf") as result:
            assert isinstance(result, httpx.Response)
            assert result.content == b"%PDF fake content"

        client.get_document_url.assert_awaited_once_with("DOC123", content_type="application/pdf")

    @pytest.mark.asyncio
    async def test_get_document_content_yields_none_when_not_found(self, mocker):
        """get_document_content yields None when get_document_url returns None."""
        client = _make_client()
        client.get_document_url = mocker.AsyncMock(return_value=None)

        async with client.get_document_content("MISSING_DOC") as result:
            assert result is None

    @pytest.mark.asyncio
    async def test_get_document_content_raises_on_s3_error(self, mocker):
        """get_document_content propagates S3 HTTP errors."""
        client = _make_client()
        client.get_document_url = mocker.AsyncMock(return_value="https://s3.example.com/doc.pdf")

        error_response = httpx.Response(403, request=httpx.Request("GET", "https://s3.example.com/doc.pdf"))
        mock_instance = mocker.AsyncMock()
        mock_instance.__aenter__ = mocker.AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = mocker.AsyncMock(return_value=False)
        mock_instance.get = mocker.AsyncMock(return_value=error_response)
        mocker.patch("httpx.AsyncClient", return_value=mock_instance)

        with pytest.raises(httpx.HTTPStatusError):
            async with client.get_document_content("DOC123"):
                pass
