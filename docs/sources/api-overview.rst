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

.. code:: python

   from ch_api import Client, api_settings

   auth = api_settings.AuthSettings(api_key="your-api-key")
   client = Client(credentials=auth)

Get an API key: https://developer.company-information.service.gov.uk/get-started

Rate Limiting
=============

- **Limit**: 600 requests per 5 minutes
- **Exceeded**: Returns HTTP 429

Integrate a rate limiter:

.. code:: python

   from asyncio_throttle import Throttler

   throttler = Throttler(rate_limit=600, period=300)
   client = Client(credentials=auth, limiter=throttler)

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

.. code:: python

   results = await client.search_companies("tech")
   
   # Check total count
   print(len(results))
   
   # Iterate (pages fetched on demand)
   async for company in results:
       print(company.title)
   
   # Or fetch all at once
   await results.fetch_all_pages()
   for company in results.local_items():
       print(company.title)

Error Handling
==============

.. code:: python

   import httpx
   from ch_api.exc import CompaniesHouseApiError

   # get_company_profile returns None for not found
   company = await client.get_company_profile("00000000")
   if company is None:
       print("Company not found")
   
   # Other operations may raise HTTPStatusError
   try:
       results = await client.search_companies("test")
   except httpx.HTTPStatusError as e:
       if e.response.status_code == 429:
           print("Rate limit exceeded")
       elif e.response.status_code == 401:
           print("Authentication failed")
   except CompaniesHouseApiError as e:
       print(f"API error: {e}")

Async Usage
===========

All calls are async and must be awaited:

.. code:: python

   import asyncio
   from ch_api import Client, api_settings

   async def main():
       auth = api_settings.AuthSettings(api_key="your-api-key")
       client = Client(credentials=auth)
       
       company = await client.get_company_profile("09370755")
       print(company.company_name)
       
       results = await client.search_companies("Apple")
       async for company in results:
           print(company.title)
   
   asyncio.run(main())

Sandbox Environment
===================

Use ``TEST_API_SETTINGS`` for development and testing:

.. code:: python

   client = Client(
       credentials=auth,
       settings=api_settings.TEST_API_SETTINGS
   )

Create test companies:

.. code:: python

   from ch_api.types import test_data_generator

   request = test_data_generator.CreateTestCompanyRequest(
       company_type="ltd",
       company_status="active"
   )
   response = await client.create_test_company(request)
   print(f"Test company: {response.company_number}")

Custom HTTP Session
===================

Provide your own httpx.AsyncClient:

.. code:: python

   import httpx

   session = httpx.AsyncClient(timeout=30.0)
   client = Client(credentials=auth, api_session=session)

See Also
========

- `Companies House API Docs <https://developer.company-information.service.gov.uk/>`_
- `API Specs <https://developer-specs.company-information.service.gov.uk/>`_
- :doc:`Usage Guide <usage>`
- :doc:`API Reference <api-reference>`
