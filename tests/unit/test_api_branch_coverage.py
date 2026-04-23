"""Branch coverage tests for api.py — covers all remaining uncovered lines."""

import datetime
from unittest.mock import MagicMock

import httpx
import pydantic
import pytest

from ch_api import api, api_settings
from ch_api.types.pagination import types as pagination_types
from ch_api.types.public_data import search_companies as sc


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


class TestCursorPaginationContinuation:
    """Line 422 — cursor=next_cursor loop continuation."""

    @pytest.mark.asyncio
    async def test_cursor_loop_continues(self):
        """Line 422: second iteration sets cursor = next_cursor."""
        client = _make_client()
        call_count = 0

        class _Item(pydantic.BaseModel):
            val: int = 0

        async def fetch_fn(cursor):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                assert cursor is None
                return [_Item(val=1)], "CURSOR_A"
            assert cursor == "CURSOR_A"
            return [_Item(val=2)], None

        page = await client._fetch_paginated_cursor(fetch_fn, None, 2)
        assert len(page.data) == 2
        assert call_count == 2


class TestAlphabeticalSearchBranches:
    """Lines 719, 729 — search_below param + empty items in alphabetical search."""

    @pytest.mark.asyncio
    async def test_search_below_added_from_next_page_token(self):
        """Line 719: search_below query param added when cursor from token."""
        client = _make_client()
        state = pagination_types._PageState(search_below="KEY:12345678")
        next_page_token = state.encode()
        urls_seen = []

        async def fake_get_resource(url, result_type):
            urls_seen.append(url)
            return MagicMock(items=[])

        client._get_resource = fake_get_resource
        await client.alphabetical_companies_search("test", next_page=next_page_token)
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
    async def test_cursor_loop_via_alphabetical_search(self):
        """Line 422 via alphabetical_companies_search: second call uses search_below."""
        client = _make_client()
        call_count = 0
        item = _alpha_company("KEY_ALPHA:00000001")

        async def fake_get_resource(url, result_type):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                result = MagicMock()
                result.items = [item]
                return result
            result = MagicMock()
            result.items = []
            return result

        client._get_resource = fake_get_resource
        page = await client.alphabetical_companies_search("test", page_size=1, result_count=2)
        assert len(page.data) == 1
        assert call_count == 2


class TestDissolvedSearchBranches:
    """Lines 766, 776 — search_below param + empty items in dissolved search."""

    @pytest.mark.asyncio
    async def test_search_below_added_from_next_page_token(self):
        """Line 766: search_below query param added when cursor from token."""
        client = _make_client()
        state = pagination_types._PageState(search_below="OLD:12345678")
        next_page_token = state.encode()
        urls_seen = []

        async def fake_get_resource(url, result_type):
            urls_seen.append(url)
            return MagicMock(items=[])

        client._get_resource = fake_get_resource
        await client.search_dissolved_companies("test", next_page=next_page_token)
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
