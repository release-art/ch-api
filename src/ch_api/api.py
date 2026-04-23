"""Async Companies House API client.

Provides direct access to the Companies House public data API with authentication,
rate limiting, and automatic pagination support.

Example:
    Basic usage::

        >>> from ch_api import Client, api_settings
        >>> @run_async_func
        ... async def basic_example(client):
        ...     company = await client.get_company_profile("09370755")
        ...     return True

See Also:
    https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
"""

import contextlib
import datetime
import logging
import typing
import urllib.parse

import httpx
import pydantic

from . import api_settings, exc, types

logger = logging.getLogger(__name__)

LimiterContextT = typing.Callable[[], typing.AsyncContextManager[None]]
ModelT = typing.TypeVar("ModelT", bound=types.base.BaseModel)

CompanyNumberStrT = typing.Annotated[
    str,
    pydantic.StringConstraints(min_length=1, pattern="^[A-Za-z0-9]{1,8}$"),
]

OfficerIdStrT = typing.Annotated[
    str,
    pydantic.StringConstraints(min_length=1),
]

PscIdStrT = typing.Annotated[
    str,
    pydantic.StringConstraints(min_length=1),
]


@contextlib.asynccontextmanager
async def _noop_limiter() -> typing.AsyncGenerator[None, None]:
    yield None


class Client:
    """Async client for the Companies House API.

    This client provides direct access to the Companies House API endpoints
    with minimal abstraction and data validation. It handles all HTTP communication,
    authentication, and automatic pagination for list endpoints.

    The Companies House API returns live, real-time data about UK companies,
    including profiles, officers, charges, filing history, and persons with
    significant control (PSCs).

    API Documentation:
        https://developer-specs.company-information.service.gov.uk/guides/gettingStarted

    Attributes:
        _api_session (httpx.AsyncClient): The underlying async HTTP session
        _api_limiter (LimiterContextT): Optional rate limiter for API calls
        _settings (api_settings.ApiSettings): API endpoint configuration

    Example:
        Create a client and fetch company information::

            >>> from ch_api import Client, api_settings
            >>> @run_async_func  # doctest: +ELLIPSIS
            ... async def client_example(client):
            ...     # Fetch a company's profile
            ...     profile = await client.get_company_profile("09370755")
            ...     print(f"{profile.company_name} - Status: {profile.company_status}")
            ...     # Fetch company officers
            ...     officers = await client.get_officer_list("09370755")
            ...     async for officer in officers:
            ...         print(f"Officer: {officer.name}")
            ...     # Search for companies
            ...     results = await client.search_companies("Apple")
            ...     async for result in results:
            ...         print(f"Found: {result.title} ({result.company_number})")
            ...
            ...  # doctest: +SKIP

    Note:
        All methods are asynchronous and must be called with ``await``.
        This client is designed for rate-limited access to the Companies House API.

    See Also:
        - :mod:`ch_api.api_settings`: Configuration and authentication settings
        - :mod:`ch_api.types`: Pydantic models for API responses
    """

    #: All instances must have this private attribute to store API session state
    _api_session: httpx.AsyncClient
    _api_limiter: LimiterContextT
    _settings: api_settings.ApiSettings
    _owns_session: bool  # Track if we created the session (for cleanup)
    _session_auth: typing.Optional[httpx.BasicAuth]  # Stored to allow session restart
    _page_token_serializer: typing.Optional[types.pagination.types.PageTokenSerializer]

    def __init__(
        self,
        credentials: typing.Union[
            api_settings.AuthSettings,
            httpx.AsyncClient,
        ],
        settings: api_settings.ApiSettings = api_settings.LIVE_API_SETTINGS,
        api_limiter: typing.Optional[LimiterContextT] = None,
        page_token_serializer: typing.Optional[types.pagination.types.PageTokenSerializer] = None,
    ) -> None:
        """Initialize the Companies House API client.

        Parameters
        ----------
        credentials : Union[AuthSettings, httpx.AsyncClient]
            Authentication credentials for the API. Can be either:

            - An :class:`~ch_api.api_settings.AuthSettings` instance containing an API key
            - A pre-configured :class:`httpx.AsyncClient` with authentication headers already set

        settings : api_settings.ApiSettings, optional
            API endpoint configuration. Defaults to :data:`~ch_api.api_settings.LIVE_API_SETTINGS`.
            Use :data:`~ch_api.api_settings.TEST_API_SETTINGS` for the sandbox environment.

        api_limiter : Callable, optional
            An optional async context manager callable that acts as a rate limiter
            for API calls. If provided, the limiter is called for each API request
            to control request velocity.

            The limiter should be a callable that returns an async context manager::

                async def my_limiter():
                    # Control request rate here
                    async with some_rate_limiter:
                        yield

            A good option is `asyncio-throttle <https://pypi.org/project/asyncio-throttle/>`_
            for implementing token bucket rate limiting.

            If ``None`` (default), no rate limiting is applied.

        Raises
        ------
        ValueError
            If ``credentials`` is neither an ``AuthSettings`` instance nor an
            ``httpx.AsyncClient``.

        Example
        -------
        Create a client with API key authentication::

            from ch_api import Client, api_settings

            auth = api_settings.AuthSettings(api_key="your-api-key")
            client = Client(credentials=auth)

        Create a client with a custom rate limiter::

            import asyncio_throttle
            from ch_api import Client, api_settings

            auth = api_settings.AuthSettings(api_key="your-api-key")
            limiter = asyncio_throttle.AsyncThrottle(max_rate=2, time_period=1.0)

            # Limiter expects a callable returning an async context manager
            def rate_limiter():
                return limiter

            client = Client(credentials=auth, api_limiter=rate_limiter)

        Use as async context manager for automatic cleanup::

            async with Client(credentials=auth) as client:
                company = await client.get_company_profile("09370755")

        See Also
        --------
        ch_api.api_settings.AuthSettings : API key credential container
        ch_api.api_settings.LIVE_API_SETTINGS : Production API settings
        ch_api.api_settings.TEST_API_SETTINGS : Sandbox API settings
        """
        self._settings = settings
        if isinstance(credentials, httpx.AsyncClient):
            self._api_session = credentials
            self._owns_session = False
            self._session_auth = None
        elif isinstance(credentials, api_settings.AuthSettings):
            self._session_auth = httpx.BasicAuth(username=credentials.api_key, password="")
            self._api_session = self._new_session()
            self._owns_session = True
        else:
            raise ValueError(
                f"credentials must be either an AuthSettings instance or an httpx.AsyncClient, "
                f"got {type(credentials).__name__} instead."
            )
        if api_limiter is None:
            self._api_limiter = _noop_limiter
        else:
            self._api_limiter = api_limiter
        self._page_token_serializer = page_token_serializer

    def _new_session(self) -> httpx.AsyncClient:
        """Create a fresh AsyncClient using the stored auth credentials."""
        return httpx.AsyncClient(
            auth=self._session_auth,
            headers={"ACCEPT": "application/json"},
        )

    async def __aenter__(self) -> "Client":
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[typing.Any],
    ) -> None:
        """Exit async context manager and cleanup resources."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the HTTP session if owned by this client.

        This method should be called when you're done with the client to properly
        clean up network resources. If the client was initialized with an
        AuthSettings object (meaning it created its own session), this will close
        the underlying HTTP session. If initialized with an external AsyncClient,
        the session is not closed as it's assumed to be managed externally.

        Example
        -------
        Manual cleanup::

            >>> @run_async_func
            ... async def manual_cleanup(client):
            ...     c = Client(credentials=client._api_session)
            ...     try:
            ...         company = await c.get_company_profile("09370755")
            ...     finally:
            ...         await c.aclose()

        Or use as context manager for automatic cleanup::

            >>> @run_async_func
            ... async def context_cleanup(client):
            ...     async with client:
            ...         company = await client.get_company_profile("09370755")
        """
        if self._owns_session:
            await self._api_session.aclose()

    async def _execute_request(
        self,
        request: httpx.Request,
        expected_out: typing.Type[ModelT] | None,
    ) -> ModelT | None:
        """Placeholder for request execution logic."""
        async with self._api_limiter():
            try:
                response = await self._api_session.send(request)
            except RuntimeError as err:
                if self._owns_session and "has been closed" in str(err):
                    logger.warning("HTTP session was closed; reopening and retrying.")
                    self._api_session = self._new_session()
                    response = await self._api_session.send(request)
                else:
                    raise
        if response.status_code == 404:
            # Resource not found
            return None
        response.raise_for_status()
        if expected_out is not None:
            if response.status_code in (httpx.codes.NO_CONTENT,):
                raise exc.UnexpectedApiResponseError(
                    f"Expected response body but got status code {response.status_code} (no content)."
                )
            elif not response.content:
                raise exc.UnexpectedApiResponseError("Expected response body but got empty content.")
            return expected_out.model_validate(response.json())  # type: ignore[return-value]

    async def _get_resource(
        self,
        url: str,
        result_type: typing.Type[ModelT],
    ) -> typing.Optional[ModelT]:  # noqa: C901
        """Helper method for simple GET requests.

        Reduces duplication for endpoints that just need to fetch a resource.

        Parameters
        ----------
        url : str
            The full API endpoint URL
        result_type : Type[ModelT]
            The expected response model type

        Returns
        -------
        ModelT
            The validated API response
        """
        request = self._api_session.build_request(method="GET", url=url)
        return await self._execute_request(request, result_type)

    # ------------------------------------------------------------------
    # Token encode / decode helpers
    # ------------------------------------------------------------------

    def _encode_next_page(self, state: types.pagination.types._PageState) -> types.pagination.types.NextPageToken:
        """Encode a page state into an externally-safe NextPageToken."""
        raw = state.encode()
        if self._page_token_serializer is not None:
            return self._page_token_serializer.serialize(raw)
        return raw

    def _decode_next_page(self, token: types.pagination.types.NextPageToken) -> types.pagination.types._PageState:
        """Decode a caller-provided NextPageToken into internal page state."""
        raw = token
        if self._page_token_serializer is not None:
            raw = self._page_token_serializer.deserialize(token)
        return types.pagination.types._PageState.decode(raw)

    # ------------------------------------------------------------------
    # Core pagination helpers
    # ------------------------------------------------------------------

    async def _fetch_paginated(
        self,
        fetch_page_fn: typing.Callable[[int], typing.Awaitable[tuple[list, typing.Optional[int]]]],
        next_page: typing.Optional[types.pagination.types.NextPageToken],
        result_count: int,
    ) -> types.pagination.types.MultipageList:
        """Fetch one or more offset-based API pages and return a MultipageList.

        Args:
            fetch_page_fn: Callable taking ``start_index`` (int), returning a
                tuple of ``(items, total_count)``. ``total_count`` may be None
                if unknown; in that case no further pages will be fetched.
            next_page: Cursor from a previous call, or None to start from offset 0.
            result_count: Minimum number of items to collect. The method fetches
                at least one page regardless of this value.

        Returns:
            A MultipageList with the collected items and pagination metadata.
        """
        page_state = (
            self._decode_next_page(next_page) if next_page is not None else types.pagination.types._PageState.first()
        )
        current_start = page_state.start_index
        items: list = []
        total_count: typing.Optional[int] = None
        has_next = False
        last_page_len = 0

        while True:
            page_items, page_total = await fetch_page_fn(current_start)
            last_page_len = len(page_items)
            if page_total is not None:
                total_count = page_total
            items.extend(page_items)

            has_next = bool(total_count is not None and page_items and (current_start + last_page_len) < total_count)

            if not has_next or len(items) >= result_count:
                break

            current_start += last_page_len

        next_page_out: typing.Optional[types.pagination.types.NextPageToken] = None
        if has_next:
            next_state = types.pagination.types._PageState(start_index=current_start + last_page_len)
            next_page_out = self._encode_next_page(next_state)

        return types.pagination.types.MultipageList(
            data=items,
            pagination=types.pagination.types.PaginationInfo(
                has_next=has_next,
                next_page=next_page_out,
                size=total_count,
            ),
        )

    async def _fetch_paginated_cursor(
        self,
        fetch_page_fn: typing.Callable[[typing.Optional[str]], typing.Awaitable[tuple[list, typing.Optional[str]]]],
        next_page: typing.Optional[types.pagination.types.NextPageToken],
        result_count: int,
    ) -> types.pagination.types.MultipageList:
        """Fetch one or more cursor-based API pages and return a MultipageList.

        Used for endpoints that paginate via ``search_below`` / ``search_above``
        cursors (e.g. alphabetical company search) rather than ``start_index``.

        Args:
            fetch_page_fn: Callable taking the current ``search_below`` cursor
                (None for the first page), returning ``(items, next_cursor)``.
                ``next_cursor`` is None when no further pages exist.
            next_page: Cursor from a previous call, or None to start from the
                beginning.
            result_count: Minimum number of items to collect.

        Returns:
            A MultipageList with the collected items and pagination metadata.
            ``pagination.size`` is always None for cursor-based endpoints.
        """
        page_state = (
            self._decode_next_page(next_page) if next_page is not None else types.pagination.types._PageState.first()
        )
        cursor = page_state.search_below
        items: list = []
        has_next = False
        next_cursor: typing.Optional[str] = None

        while True:
            page_items, next_cursor = await fetch_page_fn(cursor)
            items.extend(page_items)
            has_next = next_cursor is not None

            if not has_next or len(items) >= result_count:
                break

            cursor = next_cursor

        next_page_out: typing.Optional[types.pagination.types.NextPageToken] = None
        if has_next and next_cursor is not None:
            next_state = types.pagination.types._PageState(search_below=next_cursor)
            next_page_out = self._encode_next_page(next_state)

        return types.pagination.types.MultipageList(
            data=items,
            pagination=types.pagination.types.PaginationInfo(
                has_next=has_next,
                next_page=next_page_out,
                size=None,
            ),
        )

    @pydantic.validate_call
    async def create_test_company(
        self, company: types.test_data_generator.CreateTestCompanyRequest
    ) -> typing.Optional[types.test_data_generator.CreateTestCompanyResponse]:
        """Create a test company using the Test Data Generator API.

        Parameters
        ----------
            company: CreateTestCompanyRequest
                The request data for creating the test company.

        Returns
        -------
            CreateTestCompanyResponse
                The response data containing details of the created test company.
        """

        if self._settings.test_data_generator_url is None:
            raise RuntimeError("Test Data Generator URL is not configured in the current ApiSettings.")
        url = f"{self._settings.test_data_generator_url}/test-companies"
        request = self._api_session.build_request(
            method="POST",
            url=url,
            json=company.model_dump(mode="json"),
        )
        return await self._execute_request(request, types.test_data_generator.CreateTestCompanyResponse)

    @pydantic.validate_call
    async def get_company_profile(
        self, company_number: CompanyNumberStrT
    ) -> typing.Optional[types.public_data.company_profile.CompanyProfile]:
        """Fetch the company profile for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the profile for.

        Returns
        -------
            types.public_data.company_profile.CompanyProfile
                The company profile data.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/company/{company_number}",
            types.public_data.company_profile.CompanyProfile,
        )

    @pydantic.validate_call
    async def registered_office_address(
        self, company_number: CompanyNumberStrT
    ) -> types.public_data.registered_office.RegisteredOfficeAddress | None:
        """Fetch the registered office address for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the registered office address for.

        Returns
        -------
            types.public_data.registered_office.RegisteredOfficeAddress
                The registered office address data for the company.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/company/{company_number}/registered-office-address",
            types.public_data.registered_office.RegisteredOfficeAddress,
        )

    @pydantic.validate_call
    async def get_officer_list(
        self,
        company_number: CompanyNumberStrT,
        only_type: typing.Optional[
            typing.Literal[
                "directors",
                "secretaries",
                "llp-members",
            ]
        ] = None,
        order_by: typing.Literal["appointed_on", "resigned_on", "surname"] = "appointed_on",
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.company_officers.OfficerSummary]:
        """Fetch the list of company officers for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the officers for.
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).

        Returns
        -------
            types.pagination.types.MultipageList[OfficerSummary]
                One page of company officers with pagination metadata.
        """
        query_params: dict[str, typing.Union[str, list[str]]] = {"order_by": order_by}
        if only_type is not None:
            query_params |= {"register_type": only_type, "register_view": "true"}
        base_url = f"{self._settings.api_url}/company/{company_number}/officers"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            params = query_params | {"start_index": start_index, "items_per_page": 200}
            url = f"{base_url}?{urllib.parse.urlencode(params, doseq=True)}"
            try:
                result = await self._get_resource(
                    url,
                    types.public_data.search_companies.GenericSearchResult[  # type: ignore[arg-type]
                        types.public_data.company_officers.OfficerSummary
                    ],
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.total_results

        return await self._fetch_paginated(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def get_officer_appointment(
        self,
        company_number: CompanyNumberStrT,
        appointment_id: str,
    ) -> types.public_data.company_officers.OfficerSummary | None:
        url = f"{self._settings.api_url}/company/{company_number}/appointments/{appointment_id}"
        return await self._get_resource(url, types.public_data.company_officers.OfficerSummary)

    @pydantic.validate_call
    async def get_company_registers(
        self,
        company_number: CompanyNumberStrT,
    ) -> types.public_data.company_registers.CompanyRegister | None:
        url = f"{self._settings.api_url}/company/{company_number}/registers"
        return await self._get_resource(url, types.public_data.company_registers.CompanyRegister)

    @pydantic.validate_call
    async def search(
        self,
        query: str,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.search.AnySearchResultT]:
        """Search for companies using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_url = f"{self._settings.api_url}/search"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            url = (
                f"{base_url}?{urllib.parse.urlencode({'q': query, 'start_index': start_index, 'items_per_page': 200})}"
            )
            try:
                result = await self._get_resource(
                    url,
                    types.public_data.search_companies.GenericSearchResult[  # type: ignore[arg-type]
                        types.public_data.search.AnySearchResultT
                    ],
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.total_results

        return await self._fetch_paginated(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def advanced_company_search(  # noqa: C901
        self,
        /,
        company_name_includes: typing.Optional[str] = None,
        company_name_excludes: typing.Optional[str] = None,
        company_status: typing.Optional[typing.Sequence[str] | str] = None,
        company_type: typing.Optional[typing.Sequence[str] | str] = None,
        company_subtype: typing.Optional[typing.Sequence[str] | str] = None,
        dissolved_from: typing.Optional[datetime.date] = None,
        dissolved_to: typing.Optional[datetime.date] = None,
        incorporated_from: typing.Optional[datetime.date] = None,
        incorporated_to: typing.Optional[datetime.date] = None,
        location: typing.Optional[str] = None,
        sic_codes: typing.Optional[typing.Sequence[str]] = None,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.search_companies.AdvancedCompany]:
        """Perform an advanced search for companies using the Companies House search API."""
        query_params: dict = {}
        if company_name_includes:
            query_params["company_name_includes"] = company_name_includes
        if company_name_excludes:
            query_params["company_name_excludes"] = company_name_excludes
        if company_status:
            if isinstance(company_status, str):
                company_status = [company_status]
            query_params["company_status"] = list(company_status)
        if company_type:
            if isinstance(company_type, str):
                company_type = [company_type]
            query_params["company_type"] = list(company_type)
        if company_subtype:
            if isinstance(company_subtype, str):
                company_subtype = [company_subtype]
            query_params["company_subtype"] = list(company_subtype)
        if dissolved_from:
            query_params["dissolved_from"] = dissolved_from.isoformat()
        if dissolved_to:
            query_params["dissolved_to"] = dissolved_to.isoformat()
        if incorporated_from:
            query_params["incorporated_from"] = incorporated_from.isoformat()
        if incorporated_to:
            query_params["incorporated_to"] = incorporated_to.isoformat()
        if location:
            query_params["location"] = location
        if sic_codes:
            query_params["sic_codes"] = list(sic_codes)
        base_url = f"{self._settings.api_url}/advanced-search/companies"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            params = query_params | {"start_index": start_index}
            url = f"{base_url}?{urllib.parse.urlencode(params, doseq=True)}"
            try:
                result = await self._get_resource(
                    url,
                    types.public_data.search_companies.AdvancedSearchResult[  # type: ignore[arg-type]
                        types.public_data.search_companies.AdvancedCompany
                    ],
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.hits

        return await self._fetch_paginated(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def alphabetical_companies_search(
        self,
        query: str,
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 10,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.search_companies.AlphabeticalCompany]:
        """Search for companies alphabetically using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
            page_size: int
                Number of results per API page (1-100, default 10).
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_url = f"{self._settings.api_url}/alphabetical-search/companies"

        async def _fetch(
            search_below: typing.Optional[str],
        ) -> tuple[list, typing.Optional[str]]:
            params: dict = {"q": query, "size": str(page_size)}
            if search_below is not None:
                params["search_below"] = search_below
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            result = await self._get_resource(
                url,
                types.public_data.search_companies.AlphabeticalCompanySearchResult[  # type: ignore[arg-type]
                    types.public_data.search_companies.AlphabeticalCompany
                ],
            )
            items = result.items if result is not None else []
            if not items:
                return [], None
            next_cursor = items[-1].ordered_alpha_key_with_id
            return items, next_cursor

        return await self._fetch_paginated_cursor(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def search_dissolved_companies(
        self,
        query: str,
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 10,
        type: typing.Literal["alphabetical", "best-match", "previous-name-dissolved"] = "alphabetical",  # noqa: A002
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.search_companies.DissolvedCompany]:
        """Search for dissolved companies using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
            page_size: int
                Number of results per API page (1-100, default 10).
            type: str
                Search type (alphabetical, best-match, previous-name-dissolved).
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_url = f"{self._settings.api_url}/dissolved-search/companies"

        async def _fetch(
            search_below: typing.Optional[str],
        ) -> tuple[list, typing.Optional[str]]:
            params: dict = {"q": query, "size": str(page_size), "search_type": type}
            if search_below is not None:
                params["search_below"] = search_below
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            result = await self._get_resource(
                url,
                types.public_data.search_companies.AlphabeticalCompanySearchResult[  # type: ignore[arg-type]
                    types.public_data.search_companies.DissolvedCompany
                ],
            )
            items = result.items if result is not None else []
            if not items:
                return [], None
            next_cursor = items[-1].ordered_alpha_key_with_id
            return items, next_cursor

        return await self._fetch_paginated_cursor(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def search_companies(
        self,
        query: str,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.search.CompanySearchItem]:
        """Search for companies using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_url = f"{self._settings.api_url}/search/companies"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            url = (
                f"{base_url}?{urllib.parse.urlencode({'q': query, 'start_index': start_index, 'items_per_page': 200})}"
            )
            try:
                result = await self._get_resource(
                    url,
                    types.public_data.search_companies.GenericSearchResult[  # type: ignore[arg-type]
                        types.public_data.search.CompanySearchItem
                    ],
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.total_results

        return await self._fetch_paginated(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def search_officers(
        self,
        query: str,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.search.OfficerSearchItem]:
        """Search for officers using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_url = f"{self._settings.api_url}/search/officers"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            url = (
                f"{base_url}?{urllib.parse.urlencode({'q': query, 'start_index': start_index, 'items_per_page': 200})}"
            )
            try:
                result = await self._get_resource(
                    url,
                    types.public_data.search_companies.GenericSearchResult[  # type: ignore[arg-type]
                        types.public_data.search.OfficerSearchItem
                    ],
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.total_results

        return await self._fetch_paginated(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def search_disqualified_officers(
        self,
        query: str,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.search.DisqualifiedOfficerSearchItem]:
        """Search for disqualified officers using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_url = f"{self._settings.api_url}/search/disqualified-officers"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            url = (
                f"{base_url}?{urllib.parse.urlencode({'q': query, 'start_index': start_index, 'items_per_page': 200})}"
            )
            try:
                result = await self._get_resource(
                    url,
                    types.public_data.search_companies.GenericSearchResult[  # type: ignore[arg-type]
                        types.public_data.search.DisqualifiedOfficerSearchItem
                    ],
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.total_results

        return await self._fetch_paginated(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def get_company_charges(
        self,
        company_number: CompanyNumberStrT,
    ) -> types.public_data.charges.ChargeList | None:
        """Fetch all charges for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the charges for.

        Returns
        -------
            types.public_data.charges.ChargeList
                The list of charges for the company.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/company/{company_number}/charges",
            types.public_data.charges.ChargeList,
        )

    @pydantic.validate_call
    async def get_company_charge_details(
        self,
        company_number: CompanyNumberStrT,
        charge_id: str,
    ) -> types.public_data.charges.ChargeDetails | None:
        """Fetch all charges for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the charges for.
            charge_id: str
                The charge ID to fetch details for.

        Returns
        -------
            types.public_data.charges.ChargeDetails
                The details of the charge for the company.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/company/{company_number}/charges/{charge_id}",
            types.public_data.charges.ChargeDetails,
        )

    @pydantic.validate_call
    async def get_company_filing_history(
        self,
        company_number: CompanyNumberStrT,
        categories: typing.Tuple[
            typing.Literal[
                "accounts",
                "address",
                "annual-return",
                "capital",
                "change-of-name",
                "incorporation",
                "liquidation",
                "miscellaneous",
                "mortgage",
                "officers",
                "resolution",
            ],
            ...,
        ]
        | None = None,
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 25,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.filing_history.FilingHistoryItem]:
        """Fetch the filing history for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the filing history for.
            categories: tuple, optional
                Filter by filing categories.
            page_size: int
                Number of items per API page (1-100, default 25).
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_query_params: dict = {}
        if categories is not None:
            base_query_params["category"] = ",".join(categories)
        base_url = f"{self._settings.api_url}/company/{company_number}/filing-history"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            params = base_query_params | {"start_index": start_index, "items_per_page": page_size}
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            try:
                result = await self._get_resource(url, types.public_data.filing_history.FilingHistoryList)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.total_count

        return await self._fetch_paginated(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def get_filing_history_item(
        self,
        company_number: CompanyNumberStrT,
        filing_history_id: str,
    ) -> types.public_data.filing_history.FilingHistoryItem | None:
        """Fetch a specific filing history item for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the filing history item for.
            filing_history_id: str
                The filing history ID to fetch.

        Returns
        -------
            types.public_data.filing_history.FilingHistoryItem
                The filing history item data.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/company/{company_number}/filing-history/{filing_history_id}",
            types.public_data.filing_history.FilingHistoryItem,
        )

    # ------------------------------------------------------------------
    # Document API  (separate host)
    # ------------------------------------------------------------------

    @pydantic.validate_call
    async def get_document_metadata(
        self,
        document_id: str,
    ) -> types.public_data.documents.DocumentMetadata | None:
        """Fetch metadata for a Companies House filed document.

        Queries the Document API (a separate host from the main API) and returns
        metadata describing the document, including available content types and
        their sizes.  Use :meth:`get_document_url` to obtain a download URL for
        a specific content type.

        Parameters
        ----------
        document_id : str
            The document ID (typically found in a filing history item's links).

        Returns
        -------
        types.public_data.documents.DocumentMetadata | None
            Document metadata, or ``None`` if the document was not found.

        Example
        -------
        ::

            meta = await client.get_document_metadata("L_X0y9bwYnkyEMwLe3TNQUfmBpMG0FIj0tLzr5b5s2o")
            if meta:
                for mime_type, info in (meta.resources or {}).items():
                    print(f"{mime_type}: {info.content_length} bytes")
        """
        url = f"{self._settings.document_api_url}/document/{document_id}"
        return await self._get_resource(url, types.public_data.documents.DocumentMetadata)

    @pydantic.validate_call
    async def get_document_url(
        self,
        document_id: str,
        content_type: str = "application/pdf",
    ) -> str | None:
        """Return a pre-signed download URL for a Companies House filed document.

        Sends a request to the Document API content endpoint, which responds
        with an HTTP 302 redirect.  This method follows the redirect one level
        and returns the ``Location`` URL without downloading the content — callers
        can fetch it with any HTTP client.

        Parameters
        ----------
        document_id : str
            The document ID (typically found in a filing history item's links).
        content_type : str
            MIME type of the desired format (default ``application/pdf``).
            Available types for a document are listed in
            :attr:`~types.public_data.documents.DocumentMetadata.resources`.
            Common values: ``application/pdf``, ``application/json``,
            ``application/xml``, ``application/xhtml+xml``, ``text/csv``.

        Returns
        -------
        str | None
            The pre-signed download URL, or ``None`` if the document was not found.

        Raises
        ------
        httpx.HTTPStatusError
            If the API returns an unexpected error status (e.g. 406 if the
            requested content type is not available for this document).

        Example
        -------
        ::

            url = await client.get_document_url(
                "L_X0y9bwYnkyEMwLe3TNQUfmBpMG0FIj0tLzr5b5s2o",
                content_type="application/pdf",
            )
            if url:
                print(url)
        """
        url = f"{self._settings.document_api_url}/document/{document_id}/content"
        request = self._api_session.build_request(
            method="GET",
            url=url,
            headers={"Accept": content_type},
        )
        async with self._api_limiter():
            try:
                # follow_redirects=False is the httpx default; stated explicitly for clarity
                response = await self._api_session.send(request)
            except RuntimeError as err:
                if self._owns_session and "has been closed" in str(err):
                    logger.warning("HTTP session was closed; reopening and retrying.")
                    self._api_session = self._new_session()
                    response = await self._api_session.send(request)
                else:
                    raise
        if response.status_code == httpx.codes.NOT_FOUND:
            return None
        if response.status_code in (httpx.codes.FOUND, httpx.codes.MOVED_PERMANENTLY):
            return response.headers.get("Location")
        response.raise_for_status()
        # Unexpected non-redirect success: return Location if present, else None
        return response.headers.get("Location")

    @contextlib.asynccontextmanager
    async def get_document_content(
        self,
        document_id: str,
        content_type: str = "application/pdf",
    ) -> typing.AsyncIterator[httpx.Response | None]:
        """Async context manager that downloads a Companies House filed document.

        Resolves the pre-signed S3 download URL (via :meth:`get_document_url`)
        and fetches the document using an unauthenticated request.  The underlying
        HTTP client is kept alive for the duration of the ``async with`` block so
        that callers can stream the response body without worrying about the
        connection being closed prematurely.

        Parameters
        ----------
        document_id : str
            The document ID (typically found in a filing history item's links).
        content_type : str
            MIME type of the desired format (default ``application/pdf``).
            Available types for a document are listed in
            :attr:`~types.public_data.documents.DocumentMetadata.resources`.
            Common values: ``application/pdf``, ``application/json``,
            ``application/xml``, ``application/xhtml+xml``, ``text/csv``.

        Yields
        ------
        httpx.Response | None
            The HTTP response from S3, or ``None`` if the document was not found.
            Call :attr:`httpx.Response.content` to read the full body into memory,
            or use :meth:`httpx.Response.aiter_bytes` for streaming.

        Raises
        ------
        httpx.HTTPStatusError
            If the API or the S3 download returns an unexpected error status.

        Example
        -------
        Read entire document into memory::

            async with client.get_document_content(
                "L_X0y9bwYnkyEMwLe3TNQUfmBpMG0FIj0tLzr5b5s2o",
                content_type="application/pdf",
            ) as response:
                if response is not None:
                    pathlib.Path("confirmation_statement.pdf").write_bytes(response.content)

        Stream the document in chunks::

            async with client.get_document_content("DOC_ID") as response:
                if response is not None:
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        process(chunk)
        """
        download_url = await self.get_document_url(document_id, content_type=content_type)
        if download_url is None:
            yield None
            return
        async with httpx.AsyncClient() as download_client:
            response = await download_client.get(download_url)
            response.raise_for_status()
            yield response

    @pydantic.validate_call
    async def get_company_insolvency(
        self,
        company_number: CompanyNumberStrT,
    ) -> types.public_data.insolvency.CompanyInsolvency | None:
        """Fetch insolvency information for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch insolvency information for.

        Returns
        -------
            types.public_data.insolvency.CompanyInsolvency
                The company insolvency data.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/company/{company_number}/insolvency",
            types.public_data.insolvency.CompanyInsolvency,
        )

    @pydantic.validate_call
    async def get_company_exemptions(
        self,
        company_number: CompanyNumberStrT,
    ) -> types.public_data.exemptions.CompanyExemptions | None:
        """Fetch exemptions information for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch exemptions for.

        Returns
        -------
            types.public_data.exemptions.CompanyExemptions
                The exemptions data.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/company/{company_number}/exemptions",
            types.public_data.exemptions.CompanyExemptions,
        )

    @pydantic.validate_call
    async def get_corporate_officer_disqualification(
        self, officer_id: OfficerIdStrT
    ) -> types.public_data.disqualifications.CorporateDisqualification | None:
        """Fetch the corporate officer disqualification for a given officer.

        Parameters
        ----------
            officer_id: str
                The officer ID to fetch the disqualification for.

        Returns
        -------
            types.public_data.disqualifications.CorporateDisqualification
                The corporate officer disqualification data.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/disqualified-officers/corporate/{officer_id}",
            types.public_data.disqualifications.CorporateDisqualification,
        )

    @pydantic.validate_call
    async def get_natural_officer_disqualification(
        self, officer_id: OfficerIdStrT
    ) -> types.public_data.disqualifications.NaturalDisqualification | None:
        """Fetch the natural officer disqualification for a given officer.

        Parameters
        ----------
            officer_id: str
                The officer ID to fetch the disqualification for.

        Returns
        -------
            types.public_data.disqualifications.NaturalDisqualification
                The natural officer disqualification data.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/disqualified-officers/natural/{officer_id}",
            types.public_data.disqualifications.NaturalDisqualification,
        )

    @pydantic.validate_call
    async def get_officer_appointments(
        self,
        officer_id: OfficerIdStrT,
        filter: typing.Optional[typing.Literal["active"]] = None,  # noqa: A002
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 25,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.officer_appointments.OfficerAppointmentSummary]:
        """Fetch the officer appointments for a given officer.

        Parameters
        ----------
            officer_id: str
                The officer ID to fetch the appointments for.
            filter: str, optional
                Filter appointments (e.g. 'active').
            page_size: int
                Number of items per API page (1-100, default 25).
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_url = f"{self._settings.api_url}/officers/{officer_id}/appointments"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            params: dict = {"items_per_page": str(page_size), "start_index": str(start_index)}
            if filter is not None:
                params["filter"] = filter
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            try:
                result = await self._get_resource(url, types.public_data.officer_appointments.AppointmentList)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.total_results

        return await self._fetch_paginated(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def get_company_uk_establishments(
        self,
        company_number: CompanyNumberStrT,
    ) -> types.public_data.uk_establishments.CompanyUKEstablishments | None:
        """Fetch the UK establishments for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the UK establishments for.

        Returns
        -------
            types.public_data.uk_establishments.CompanyUKEstablishments
                The UK establishments data.
        """
        return await self._get_resource(
            f"{self._settings.api_url}/company/{company_number}/uk-establishments",
            types.public_data.uk_establishments.CompanyUKEstablishments,
        )

    @pydantic.validate_call
    async def get_company_psc_list(
        self,
        company_number: CompanyNumberStrT,
        register_view: bool = False,
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 25,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.psc.ListSummary]:
        """Fetch the list of persons with significant control for a given company.

        Parameters
        ----------
            company_number: str
                The company number.
            register_view: bool
                If True, only show PSCs active or terminated during election period.
            page_size: int
                Number of items per API page (1-100, default 25).
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_url = f"{self._settings.api_url}/company/{company_number}/persons-with-significant-control"
        register_view_str = "true" if register_view else "false"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            params = {
                "items_per_page": str(page_size),
                "start_index": str(start_index),
                "register_view": register_view_str,
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            try:
                result = await self._get_resource(url, types.public_data.psc.PSCList)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.total_results

        return await self._fetch_paginated(_fetch, next_page, result_count)

    @pydantic.validate_call
    async def get_company_psc_statements(
        self,
        company_number: CompanyNumberStrT,
        register_view: bool = False,
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 25,
        next_page: typing.Optional[types.pagination.types.NextPageToken] = None,
        result_count: int = 1,
    ) -> types.pagination.types.MultipageList[types.public_data.psc.Statement]:
        """Fetch the PSC statements for a given company.

        Parameters
        ----------
            company_number: str
                The company number.
            register_view: bool
                If True, only show PSCs active or terminated during election period.
            page_size: int
                Number of items per API page (1-100, default 25).
            next_page: str, optional
                Cursor from a previous call to continue pagination.
            result_count: int
                Minimum number of results to return (default 1 = one API page).
        """
        base_url = f"{self._settings.api_url}/company/{company_number}/persons-with-significant-control-statements"
        register_view_str = "true" if register_view else "false"

        async def _fetch(start_index: int) -> tuple[list, typing.Optional[int]]:
            params = {
                "items_per_page": str(page_size),
                "start_index": str(start_index),
                "register_view": register_view_str,
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            try:
                result = await self._get_resource(url, types.public_data.psc.StatementList)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                    return [], None
                raise
            if result is None:
                return [], None
            return result.items or [], result.total_results

        return await self._fetch_paginated(_fetch, next_page, result_count)

    async def _get_psc_by_type(
        self,
        company_number: str,
        psc_id: str,
        psc_type: str,
        result_type: typing.Type[ModelT],
    ) -> ModelT | None:
        """Helper method to fetch PSC records by type.

        This reduces code duplication across the multiple PSC endpoint methods.

        Parameters
        ----------
        company_number : str
            The company number
        psc_id : str
            The PSC identifier
        psc_type : str
            The PSC type path component (e.g., 'individual', 'corporate-entity')
        result_type : Type[ModelT]
            The expected response model type

        Returns
        -------
        ModelT | None
            The validated PSC record, or None if not found
        """
        return await self._get_resource(
            f"{self._settings.api_url}/company/{company_number}/persons-with-significant-control/{psc_type}/{psc_id}",
            result_type,
        )

    @pydantic.validate_call
    async def get_company_corporate_psc(
        self,
        company_number: CompanyNumberStrT,
        psc_id: PscIdStrT,
    ) -> types.public_data.psc.CorporateEntity | None:
        return await self._get_psc_by_type(
            company_number,
            psc_id,
            "corporate-entity",
            types.public_data.psc.CorporateEntity,
        )

    @pydantic.validate_call
    async def get_company_corporate_psc_beneficial_owner(
        self,
        company_number: CompanyNumberStrT,
        psc_id: PscIdStrT,
    ) -> types.public_data.psc.CorporateEntityBeneficialOwner | None:
        return await self._get_psc_by_type(
            company_number,
            psc_id,
            "corporate-entity-beneficial-owner",
            types.public_data.psc.CorporateEntityBeneficialOwner,
        )

    @pydantic.validate_call
    async def get_company_individual_psc_beneficial_owner(
        self,
        company_number: CompanyNumberStrT,
        psc_id: PscIdStrT,
    ) -> types.public_data.psc.IndividualBeneficialOwner | None:
        return await self._get_psc_by_type(
            company_number,
            psc_id,
            "individual-beneficial-owner",
            types.public_data.psc.IndividualBeneficialOwner,
        )

    @pydantic.validate_call
    async def get_company_individual_psc(
        self,
        company_number: CompanyNumberStrT,
        psc_id: PscIdStrT,
    ) -> types.public_data.psc.Individual | None:
        return await self._get_psc_by_type(
            company_number,
            psc_id,
            "individual",
            types.public_data.psc.Individual,
        )

    @pydantic.validate_call
    async def get_company_legal_person_psc_beneficial_owner(
        self,
        company_number: CompanyNumberStrT,
        psc_id: PscIdStrT,
    ) -> types.public_data.psc.LegalPersonBeneficialOwner | None:
        return await self._get_psc_by_type(
            company_number,
            psc_id,
            "legal-person-beneficial-owner",
            types.public_data.psc.LegalPersonBeneficialOwner,
        )

    @pydantic.validate_call
    async def get_company_legal_person_psc(
        self,
        company_number: CompanyNumberStrT,
        psc_id: PscIdStrT,
    ) -> types.public_data.psc.LegalPerson | None:
        return await self._get_psc_by_type(
            company_number,
            psc_id,
            "legal-person",
            types.public_data.psc.LegalPerson,
        )

    @pydantic.validate_call
    async def get_company_super_secure_psc(
        self,
        company_number: CompanyNumberStrT,
        psc_id: PscIdStrT,
    ) -> types.public_data.psc.SuperSecure | None:  # pragma: no cover - can't test
        return await self._get_psc_by_type(
            company_number,
            psc_id,
            "super-secure",
            types.public_data.psc.SuperSecure,
        )

    @pydantic.validate_call
    async def get_company_super_secure_beneficial_owner_psc(
        self,
        company_number: CompanyNumberStrT,
        psc_id: PscIdStrT,
    ) -> types.public_data.psc.SuperSecureBeneficialOwner | None:  # pragma: no cover - can't test
        return await self._get_psc_by_type(
            company_number,
            psc_id,
            "super-secure-beneficial-owner",
            types.public_data.psc.SuperSecureBeneficialOwner,
        )
