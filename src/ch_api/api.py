"""Async Companies House API client.

Provides direct access to the Companies House public data API with authentication,
rate limiting, and automatic pagination support.

Example:
    Basic usage::

        >>> from ch_api import Client, api_settings
        >>> auth = api_settings.AuthSettings(api_key="your-api-key")
        >>> client = Client(credentials=auth)
        >>> company = await client.get_company_profile("09370755")  # doctest: +SKIP

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
            >>> auth = api_settings.AuthSettings(api_key="your-api-key")
            >>> client = Client(credentials=auth)  # doctest: +SKIP
            ...
            >>> # Fetch a company's profile
            >>> profile = await client.get_company_profile("09370755")  # doctest: +SKIP
            >>> print(f"{profile.company_name} - Status: {profile.company_status}")  # doctest: +SKIP
            ...
            >>> # Fetch company officers
            >>> officers = await client.get_officer_list("09370755")  # doctest: +SKIP
            >>> async for officer in officers:  # doctest: +SKIP
            ...     print(f"Officer: {officer.name}")
            ...
            >>> # Search for companies
            >>> results = await client.search_companies("Apple")  # doctest: +SKIP
            >>> async for result in results:  # doctest: +SKIP
            ...     print(f"Found: {result.title} ({result.company_number})")

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

    def __init__(
        self,
        credentials: typing.Union[
            api_settings.AuthSettings,
            httpx.AsyncClient,
        ],
        settings: api_settings.ApiSettings = api_settings.LIVE_API_SETTINGS,
        api_limiter: typing.Optional[LimiterContextT] = None,
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
        elif isinstance(credentials, api_settings.AuthSettings):
            auth = httpx.BasicAuth(username=credentials.api_key, password="")
            self._api_session = httpx.AsyncClient(
                auth=auth,
                headers={
                    "ACCEPT": "application/json",
                },
            )
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

            >>> client = Client(credentials=auth)  # doctest: +SKIP
            >>> try:
            ...     company = await client.get_company_profile("09370755")
            ... finally:
            ...     await client.aclose()

        Or use as context manager for automatic cleanup::

            >>> async with Client(credentials=auth) as client:  # doctest: +SKIP
            ...     company = await client.get_company_profile("09370755")
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
            response = await self._api_session.send(request)
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

    async def _create_paginated_list(
        self,
        output_t: typing.Type[ModelT],
        base_url: str,
        query_params: dict[str, typing.Union[str, list[str]]],
        items_per_page: int = 200,
    ) -> types.pagination.paginated_list.MultipageList[ModelT]:
        """Helper to create and initialize a paginated list for search endpoints.

        Parameters
        ----------
        output_t : Type[ModelT]
            The type of items in the list
        base_url : str
            The base API endpoint URL
        query_params : dict
            Query parameters for the search
        items_per_page : int
            Number of items per page (default: 200)

        Returns
        -------
        MultipageList[ModelT]
            Initialized paginated list ready for iteration
        """
        result = types.pagination.paginated_list.MultipageList(
            fetch_page=lambda target: self._get_paginated_search_result(
                output_t=output_t,
                base_url=base_url,
                query_params=query_params,
                target=target,
                items_per_page=items_per_page,
            ),
        )
        await result._async_init()
        return result

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

    async def _get_paginated_search_result(
        self,
        output_t: typing.Type[ModelT],
        base_url: str,
        query_params: dict[str, typing.Union[str, list[str]]],
        target: types.pagination.types.FetchPageCallArg,
        items_per_page: int = 20,
    ) -> types.pagination.types.FetchPageRvT[ModelT]:
        my_query_params = query_params.copy() | {
            "start_index": target.current_total_list_len,
            "items_per_page": items_per_page,
        }
        assert my_query_params
        this_url = f"{base_url}?{urllib.parse.urlencode(my_query_params, doseq=True)}"
        try:
            result = await self._get_resource(
                this_url,
                types.public_data.search_companies.GenericSearchResult[output_t],  # type: ignore[arg-type]
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                # No results
                return (None, [])
            else:
                raise
        assert result is not None
        items = result.items or []
        if not items:
            has_next = False
        else:
            has_next = (result.start_index + len(items)) < result.total_results
        return (
            types.pagination.types.PaginatedResultInfo.model_validate(
                {
                    "page": target.last_fetched_page + 1,
                    "per_page": result.items_per_page,
                    "total_count": result.total_results,
                    "has_next": has_next,
                }
            ),
            items,
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
    ) -> types.pagination.paginated_list.MultipageList[types.public_data.company_officers.OfficerSummary]:
        """Fetch the list of company officers for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the officers for.

        Returns
        -------
            types.pagination.async_list.MultipageList[types.public_data.company_officers.OfficerSummary]
                The list of company officers.
        """
        query_params: dict[str, typing.Union[str, list[str]]] = {
            "order_by": order_by,
        }
        if only_type is not None:
            query_params |= {
                "register_type": only_type,
                "register_view": "true",
            }

        out = types.pagination.paginated_list.MultipageList(
            fetch_page=lambda target: self._get_paginated_search_result(
                output_t=types.public_data.company_officers.OfficerSummary,
                base_url=f"{self._settings.api_url}/company/{company_number}/officers",
                query_params=query_params,
                target=target,
            ),
        )
        await out._async_init()
        return out

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
        self, query: str
    ) -> types.pagination.paginated_list.MultipageList[types.public_data.search.AnySearchResultT]:
        """Search for companies using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
        """
        out = types.pagination.paginated_list.MultipageList(
            fetch_page=lambda target: self._get_paginated_search_result(
                output_t=types.public_data.search.AnySearchResultT,  # type: ignore[arg-type]
                base_url=f"{self._settings.api_url}/search",
                query_params={"q": query},
                target=target,
                items_per_page=200,
            ),
        )
        await out._async_init()
        return out

    async def _get_paginated_advanced_search_result(
        self,
        output_t: typing.Type[ModelT],
        base_url: str,
        query_params: dict[str, typing.Union[str, list[str]]],
        target: types.pagination.types.FetchPageCallArg[ModelT],
    ) -> tuple[
        typing.Optional[types.pagination.types.PaginatedResultInfo],
        typing.Optional[types.public_data.search_companies.AdvancedSearchResult[ModelT]],
    ]:
        my_query_params = query_params.copy() | {
            "start_index": target.current_total_list_len,
        }
        assert my_query_params
        this_url = f"{base_url}?{urllib.parse.urlencode(my_query_params, doseq=True)}"
        request = self._api_session.build_request(
            method="GET",
            url=this_url,
        )

        return await self._fetch_paginated_container(
            request=request,
            output_t=types.public_data.search_companies.AdvancedSearchResult[output_t],  # type: ignore[arg-type]
            to_pagination_info_args=lambda result: {
                "has_next": (target.current_total_list_len + len(result.items or [])) < result.hits,
                "page": target.last_fetched_page + 1,
            },
        )

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
        max_results: typing.Annotated[int, pydantic.conint(ge=1, le=5000)] = 100,
    ) -> types.compound_api_types.public_data.search_companies.AdvancedSearchResult[
        types.public_data.search.CompanySearchItem
    ]:
        """Perform an advanced search for companies using the Companies House search API."""
        query_params = {
            "size": str(max_results),
        }
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

        async def _fetch_page(
            target: types.pagination.types.FetchPageCallArg[types.public_data.search_companies.AdvancedCompany],
        ) -> types.pagination.types.FetchPageRvT[types.public_data.search_companies.AdvancedCompany]:
            return await self._get_paginated_advanced_search_result(
                output_t=types.public_data.search_companies.AdvancedCompany,
                base_url=f"{self._settings.api_url}/advanced-search/companies",
                query_params=query_params,
                target=target,
            )  # type: ignore[arg-type]

        return await types.compound_api_types.public_data.search_companies.AdvancedSearchResult.from_api_paginated_list(  # type: ignore[return-value]
            fetch_page_fn=_fetch_page,
            convert_item_fn=lambda fetched_list: fetched_list.items or [],
        )

    async def _get_next_alphabetical_search_page(
        self,
        base_url: str,
        output_t: typing.Type[ModelT],
        query_params: dict[str, str],
        target: types.pagination.types.FetchPageCallArg[ModelT],
    ) -> typing.Tuple[
        typing.Optional[types.pagination.types.PaginatedResultInfo],
        typing.Optional[types.public_data.search_companies.AlphabeticalCompanySearchResult[ModelT]],
    ]:
        # Alphabetical search uses cursor-based pagination with search_above/search_below
        # parameters. Currently only forward pagination (search_below) is implemented.
        # Backward pagination would require tracking search_above cursors from previous pages.
        if target.last_fetched_page > 0:
            return (None, None)

        search_below = (
            target.last_known_item.ordered_alpha_key_with_id  # type: ignore[union-attr]
            if target.last_known_item
            else None
        )
        search_above = (
            target.first_known_item.ordered_alpha_key_with_id  # type: ignore[union-attr]
            if target.first_known_item
            else None
        )

        if (None in (search_above, search_below)) and target.last_fetched_page > 0:
            # search_below = None indicates start of list, so if we have already fetched at least one page
            return (None, None)

        my_query_params = query_params.copy()
        if search_above is not None:
            my_query_params["search_above"] = search_above
        if search_below is not None:
            my_query_params["search_below"] = search_below
        assert my_query_params

        this_url = f"{base_url}?{urllib.parse.urlencode(my_query_params, doseq=True)}"
        request = self._api_session.build_request(
            method="GET",
            url=this_url,
        )

        return await self._fetch_paginated_container(
            request=request,
            output_t=types.public_data.search_companies.AlphabeticalCompanySearchResult[output_t],  # type: ignore[arg-type]
            to_pagination_info_args=lambda result: {
                "page": target.last_fetched_page + 1,
                "has_next": (len(result.items or []) > 0),
            },
        )

    @pydantic.validate_call
    async def alphabetical_companies_search(
        self, query: str, page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 10
    ) -> types.compound_api_types.public_data.top_hit.TopHitList[
        types.public_data.search_companies.AlphabeticalCompanySearchResult[
            types.public_data.search_companies.AlphabeticalCompany
        ],
        types.public_data.search_companies.AlphabeticalCompany,
    ]:
        async def _fetch_page(target: types.pagination.types.FetchPageCallArg):
            return await self._get_next_alphabetical_search_page(
                base_url=f"{self._settings.api_url}/alphabetical-search/companies",
                output_t=types.public_data.search_companies.AlphabeticalCompany,
                query_params={
                    "q": query,
                    "size": str(page_size),
                },
                target=target,
            )

        return await types.compound_api_types.public_data.top_hit.TopHitList.from_api_paginated_list(  # type: ignore[return-value]
            fetch_page_fn=_fetch_page,
            convert_item_fn=lambda fetched_list: fetched_list.items or [],
        )

    @pydantic.validate_call
    async def search_dissolved_companies(
        self,
        query: str,
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 10,
        type: typing.Literal["alphabetical", "best-match", "previous-name-dissolved"] = "alphabetical",  # noqa: A002
    ) -> types.compound_api_types.public_data.top_hit.TopHitList[
        types.public_data.search_companies.AlphabeticalCompanySearchResult[
            types.public_data.search_companies.DissolvedCompany
        ],
        types.public_data.search_companies.DissolvedCompany,
    ]:
        """Search for dissolved companies using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
        """

        async def _fetch_page(target: types.pagination.types.FetchPageCallArg):
            return await self._get_next_alphabetical_search_page(
                base_url=f"{self._settings.api_url}/dissolved-search/companies",
                output_t=types.public_data.search_companies.DissolvedCompany,
                query_params={
                    "q": query,
                    "size": str(page_size),
                    "search_type": type,
                },
                target=target,
            )

        return await types.compound_api_types.public_data.top_hit.TopHitList.from_api_paginated_list(  # type: ignore[return-value]
            fetch_page_fn=_fetch_page,
            convert_item_fn=lambda fetched_list: fetched_list.items or [],
        )

    @pydantic.validate_call
    async def search_companies(
        self, query: str
    ) -> types.pagination.paginated_list.MultipageList[types.public_data.search.CompanySearchItem]:
        """Search for companies using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
        """
        return await self._create_paginated_list(
            types.public_data.search.CompanySearchItem,
            f"{self._settings.api_url}/search/companies",
            {"q": query},
        )

    @pydantic.validate_call
    async def search_officers(
        self, query: str
    ) -> types.pagination.paginated_list.MultipageList[types.public_data.search.OfficerSearchItem]:
        """Search for officers using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
        """
        return await self._create_paginated_list(
            types.public_data.search.OfficerSearchItem,
            f"{self._settings.api_url}/search/officers",
            {"q": query},
        )

    @pydantic.validate_call
    async def search_disqualified_officers(
        self, query: str
    ) -> types.pagination.paginated_list.MultipageList[types.public_data.search.DisqualifiedOfficerSearchItem]:
        """Search for disqualified officers using the Companies House search API.

        Parameters
        ----------
            query: str
                The search query string.
        """
        return await self._create_paginated_list(
            types.public_data.search.DisqualifiedOfficerSearchItem,
            f"{self._settings.api_url}/search/disqualified-officers",
            {"q": query},
        )

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

    async def _get_filing_history_page(
        self,
        base_url: str,
        query_params: dict[str, typing.Union[str, list[str]]],
        target: types.pagination.types.FetchPageCallArg,
        items_per_page: int = 20,
    ) -> types.pagination.types.FetchPageRvT[types.public_data.filing_history.FilingHistoryItem]:
        my_query_params = query_params.copy() | {
            "start_index": target.current_total_list_len,
            "items_per_page": items_per_page,
        }
        assert my_query_params
        this_url = f"{base_url}?{urllib.parse.urlencode(my_query_params, doseq=True)}"
        try:
            result = await self._get_resource(this_url, types.public_data.filing_history.FilingHistoryList)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                # No results
                return (None, [])
            else:
                raise
        assert result is not None
        items = result.items or []
        if not items:
            has_next = False
        else:
            has_next = (result.start_index + len(items)) < result.total_count
        return (
            types.pagination.types.PaginatedResultInfo.model_validate(
                {
                    "page": target.last_fetched_page + 1,
                    "per_page": result.items_per_page,
                    "total_count": result.total_count,
                    "has_next": has_next,
                }
            ),
            items,
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
    ) -> types.pagination.paginated_list.MultipageList[types.public_data.filing_history.FilingHistoryItem]:
        """Fetch the filing history for a given company.

        Parameters
        ----------
            company_number: str
                The company number to fetch the filing history for.

        Returns
        -------
            types.public_data.filing_history.FilingHistoryList
                The filing history data.
        """
        query_params = {}
        if categories is not None:
            query_params["category"] = ",".join(categories)
        out = types.pagination.paginated_list.MultipageList(
            fetch_page=lambda target: self._get_filing_history_page(
                base_url=f"{self._settings.api_url}/company/{company_number}/filing-history",
                items_per_page=page_size,
                query_params=query_params,
                target=target,
            ),
        )
        await out._async_init()
        return out

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
        filter: typing.Optional[typing.Literal["active", "active"]] = None,  # noqa: A002
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 25,
    ) -> types.compound_api_types.public_data.officer_appointments.OfficerAppointments:
        """Fetch the officer appointments for a given officer.

        Parameters
        ----------
            officer_id: str
                The officer ID to fetch the appointments for.

        Returns
        -------
            types.compound_api_types.OfficerAppointments
                The officer appointments data.
        """
        url = f"{self._settings.api_url}/officers/{officer_id}/appointments"

        async def _get_page(target: types.pagination.types.FetchPageCallArg):
            query_params = {
                "items_per_page": str(page_size),
                "start_index": str(target.current_total_list_len),
            }
            if filter is not None:
                query_params["filter"] = filter
            this_url = f"{url}?{urllib.parse.urlencode(query_params, doseq=True)}"
            request = self._api_session.build_request(
                method="GET",
                url=this_url,
            )
            return await self._fetch_paginated_container(
                request=request,
                output_t=types.public_data.officer_appointments.AppointmentList,
                to_pagination_info_args=lambda rv_list: {
                    "page": (target.last_fetched_page + 1),
                    "per_page": rv_list.items_per_page,
                    "total_count": rv_list.total_results,
                    "has_next": (rv_list.start_index + len(rv_list.items or [])) < rv_list.total_results,
                },
            )

        return (
            await types.compound_api_types.public_data.officer_appointments.OfficerAppointments.from_api_paginated_list(  # type: ignore[return-value]
                fetch_page_fn=_get_page,
                convert_item_fn=lambda item: item.items or (),
            )
        )

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

    async def _fetch_paginated_container(
        self,
        request: httpx.Request,
        output_t: typing.Type[ModelT],
        to_pagination_info_args: typing.Callable[[ModelT], dict],
    ) -> typing.Tuple[
        typing.Optional[types.pagination.types.PaginatedResultInfo],
        typing.Optional[ModelT],
    ]:
        try:
            rv_list = await self._execute_request(request, output_t)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE:
                # No results
                rv_list = None
            else:
                raise
        if rv_list is None:
            pagination_info = None
        else:
            pagination_info = types.pagination.types.PaginatedResultInfo.model_validate(
                to_pagination_info_args(rv_list)
            )
        return pagination_info, rv_list

    @pydantic.validate_call
    async def get_company_psc_list(
        self,
        company_number: CompanyNumberStrT,
        register_view: bool = False,
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 25,
    ) -> types.compound_api_types.public_data.psc.OfficerAppointments:
        """
        register_view - Display register specific information. If register is held at Companies House and
           register_view is set to true, only PSCs which are active or were terminated during election
           period are shown.
        """
        base_url = f"{self._settings.api_url}/company/{company_number}/persons-with-significant-control"

        register_view_arg = {
            True: "true",
            False: "false",
        }[register_view]

        async def fetch_page(target: types.pagination.types.FetchPageCallArg):
            query_params = {
                "items_per_page": str(page_size),
                "start_index": str(target.current_total_list_len),
                "register_view": register_view_arg,
            }

            this_url = f"{base_url}?{urllib.parse.urlencode(query_params, doseq=True)}"
            request = self._api_session.build_request(
                method="GET",
                url=this_url,
            )
            return await self._fetch_paginated_container(
                request=request,
                output_t=types.public_data.psc.PSCList,
                to_pagination_info_args=lambda rv_list: {
                    "page": (target.last_fetched_page + 1),
                    "per_page": rv_list.items_per_page,
                    "total_count": rv_list.total_results,
                    "has_next": (rv_list.start_index + len(rv_list.items or [])) < rv_list.total_results,
                },
            )

        return await types.compound_api_types.public_data.psc.OfficerAppointments.from_api_paginated_list(  # type: ignore[return-value]
            fetch_page_fn=fetch_page,
            convert_item_fn=lambda fetched_list: fetched_list.items or (),
        )

    @pydantic.validate_call
    async def get_company_psc_statements(
        self,
        company_number: CompanyNumberStrT,
        register_view: bool = False,
        page_size: typing.Annotated[int, pydantic.conint(ge=1, le=100)] = 25,
    ) -> types.compound_api_types.public_data.psc.StatementList:
        """
        register_view - Display register specific information. If register is held at Companies House and
           register_view is set to true, only PSCs which are active or were terminated during election
           period are shown.
        """
        base_url = f"{self._settings.api_url}/company/{company_number}/persons-with-significant-control-statements"

        register_view_arg = {
            True: "true",
            False: "false",
        }[register_view]

        async def fetch_page(target: types.pagination.types.FetchPageCallArg):
            query_params = {
                "items_per_page": str(page_size),
                "start_index": str(target.current_total_list_len),
                "register_view": register_view_arg,
            }

            this_url = f"{base_url}?{urllib.parse.urlencode(query_params, doseq=True)}"
            request = self._api_session.build_request(
                method="GET",
                url=this_url,
            )
            return await self._fetch_paginated_container(
                request=request,
                output_t=types.public_data.psc.StatementList,
                to_pagination_info_args=lambda rv_list: {
                    "page": (target.last_fetched_page + 1),
                    "per_page": rv_list.items_per_page,
                    "total_count": rv_list.total_results,
                    "has_next": (rv_list.start_index + len(rv_list.items or [])) < rv_list.total_results,
                },
            )

        return await types.compound_api_types.public_data.psc.StatementList.from_api_paginated_list(  # type: ignore[return-value]
            fetch_page_fn=fetch_page,
            convert_item_fn=lambda fetched_list: fetched_list.items or (),
        )

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
