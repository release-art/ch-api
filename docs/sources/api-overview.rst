=================================================
API Overview
=================================================

Python client for the `Companies House API <https://developer.company-information.service.gov.uk/>`_ 
providing access to UK company information.

Base URL: ``https://api.company-information.service.gov.uk``

Resources
=========

- **Company** - Profiles, officers, PSC, charges, filing history
- **Search** - Companies, officers, disqualified directors
- **Sandbox** - Test data generation

Authentication
==============

All requests require an API key via HTTP Basic Auth:

    >>> from ch_api import Client, api_settings  # doctest: +SKIP
    >>> auth = api_settings.AuthSettings(api_key="your-api-key")  # doctest: +SKIP
    >>> client = Client(credentials=auth)  # doctest: +SKIP

Get an API key: https://developer.company-information.service.gov.uk/get-started

Rate Limiting
=============

- **Limit**: 600 requests per 5 minutes
- **Exceeded**: Returns HTTP 429

Integrate a rate limiter:

    >>> from asyncio_throttle import Throttler  # doctest: +SKIP
    >>> throttler = Throttler(rate_limit=600, period=300)  # doctest: +SKIP
    >>> client = Client(credentials=auth, limiter=throttler)  # doctest: +SKIP

Key Endpoints
=============

.. list-table::
   :widths: 40 60
   :header-rows: 1

   * - Endpoint
     - Method
   * - ``/company/{company_number}``
     - ``get_company_profile(company_number)``
   * - ``/company/{company_number}/officers``
     - ``get_officer_list(company_number)``
   * - ``/company/{company_number}/persons-with-significant-control``
     - ``get_company_psc_list(company_number)``
   * - ``/company/{company_number}/filing-history``
     - ``get_company_filing_history(company_number)``
   * - ``/company/{company_number}/charges``
     - ``get_company_charges(company_number)``
   * - ``/search/companies``
     - ``search_companies(query)``
   * - ``/search/officers``
     - ``search_officers(query)``
   * - ``/search/disqualified-officers``
     - ``search_disqualified_officers(query)``

Pagination
==========

List endpoints return ``MultipageList`` with lazy-loading:

    >>> async def pagination_example(client):
    ...     results = await client.search_companies("tech")
    ...     # Check total count
    ...     print(f"Results: {len(results)}")
    ...     # Iterate (pages fetched on demand)
    ...     count = 0
    ...     async for company in results:
    ...         count += 1
    ...         if count <= 2:
    ...             print(f"Company: {company.title}")
    ...         if count >= 3:
    ...             break
    ...     # Or fetch all at once
    ...     await results.fetch_all_pages()
    ...     return True
    >>> run_async_func(pagination_example)  # doctest: +ELLIPSIS
    Results: ...
    Company: ...
    Company: ...
    True

Error Handling
==============

    >>> import httpx
    >>> from ch_api.exc import CompaniesHouseApiError
    >>> async def error_handling_example(client):
    ...     # get_company_profile returns None for not found
    ...     company = await client.get_company_profile("00000000")
    ...     if company is None:
    ...         print("Company not found")
    ...     
    ...     # Other operations may raise HTTPStatusError
    ...     try:
    ...         results = await client.search_companies("test")
    ...         return True
    ...     except httpx.HTTPStatusError as e:
    ...         if e.response.status_code == 429:
    ...             print("Rate limit exceeded")
    ...         elif e.response.status_code == 401:
    ...             print("Authentication failed")
    ...     except CompaniesHouseApiError as e:
    ...         print(f"API error: {e}")
    >>> run_async_func(error_handling_example)
    Company not found
    True

Async Usage
===========

All calls are async and must be awaited:

    >>> import asyncio
    >>> from ch_api import Client, api_settings
    >>> async def async_example(client):
    ...     company = await client.get_company_profile("09370755")
    ...     print(f"Company: {company.company_name}")
    ...     
    ...     results = await client.search_companies("Apple")
    ...     count = 0
    ...     async for company in results:
    ...         count += 1
    ...         if count <= 1:
    ...             print(f"Found: {company.title}")
    ...         if count >= 2:
    ...             break
    ...     return True
    >>> run_async_func(async_example)  # doctest: +ELLIPSIS
    Company: ...
    Found: ...
    True

Sandbox Environment
===================

Use ``TEST_API_SETTINGS`` for development and testing:

    >>> from ch_api import Client, api_settings  # doctest: +SKIP
    >>> client = Client(  # doctest: +SKIP
    ...     credentials=auth,
    ...     settings=api_settings.TEST_API_SETTINGS
    ... )  # doctest: +SKIP

Create test companies:

    >>> from ch_api.types import test_data_generator
    >>> async def create_test_company_example(client):
    ...     request = test_data_generator.CreateTestCompanyRequest(
    ...         company_type="ltd",
    ...         company_status="active"
    ...     )
    ...     response = await client.create_test_company(request)
    ...     print(f"Test company: {response.company_number}")
    ...     return True
    >>> run_async_func(create_test_company_example)  # doctest: +SKIP
    True

Custom HTTP Session
===================

Provide your own httpx.AsyncClient:

    >>> import httpx  # doctest: +SKIP
    >>> session = httpx.AsyncClient(timeout=30.0)  # doctest: +SKIP
    >>> client = Client(credentials=auth, api_session=session)  # doctest: +SKIP

See Also
========

- `Companies House API Docs <https://developer.company-information.service.gov.uk/>`_
- `API Specs <https://developer-specs.company-information.service.gov.uk/>`_
- :doc:`Usage Guide <usage>`
- :doc:`API Reference <api-reference>`
