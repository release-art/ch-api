=================================================
Understanding the Companies House API
=================================================

The package provides a Python client for the `Companies House API <https://developer.company-information.service.gov.uk/>`_. 
This API gives access to public information about UK companies, including company profiles, officers, filing history, and persons with significant control.

The base URL for all API requests is:

.. code:: shell

   https://api.company-information.service.gov.uk

.. _ch-api.resources-and-endpoints:

Resources and Endpoints
=======================

The Companies House API provides access to various types of company information:

- **Company Profile** - Basic company information including name, number, status, registered office address, and company type
- **Officers** - Current and resigned company officers (directors, secretaries, etc.)
- **Persons with Significant Control (PSC)** - Information about individuals or entities with significant control over the company
- **Filing History** - Historical records of documents filed at Companies House
- **Charges** - Charges registered against company assets (mortgages, debentures, etc.)
- **Insolvency** - Insolvency proceedings and practitioner appointments
- **Exemptions** - PSC exemptions from disclosure requirements
- **UK Establishments** - Overseas companies with UK establishments
- **Registers** - Optional company registers (e.g., PSC register, directors register)
- **Company Search** - Search for companies by name or other criteria
- **Officer Search** - Search for officers across all companies
- **Disqualified Officers** - Information about disqualified company directors

.. _ch-api.authentication:

Authentication
==============

All API requests require authentication using an API key. You can obtain an API key by:

1. `Registering for a Companies House account <https://developer.company-information.service.gov.uk/get-started>`_
2. Creating an application in your account
3. Obtaining the API key for your application

The API key should be provided via HTTP Basic Authentication, using the API key as the username and an empty password:

.. code:: python

   from ch_api import Client, api_settings

   auth = api_settings.AuthSettings(api_key="your-api-key-here")
   client = Client(credentials=auth)

.. _ch-api.rate-limiting:

Rate Limiting
=============

The Companies House API applies rate limiting to ensure fair usage. According to the official documentation:

- **Rate limit**: 600 requests per 5 minutes per API key
- **Breaches**: Exceeding the rate limit results in HTTP 429 (Too Many Requests) errors

.. warning::

   Please use the API and this library responsibly. Do not make excessive requests or use it in an inappropriate way.

You can integrate rate limiting using an async rate limiter:

.. code:: python

   from asyncio_throttle import Throttler

   # Allow 600 requests per 5 minutes (300 seconds)
   throttler = Throttler(rate_limit=600, period=300)
   
   async def limiter():
       async with throttler:
           yield

   client = Client(credentials=auth, limiter=limiter)

.. _ch-api.company-requests:

Company Requests
================

Companies are identified by their unique company number. The following endpoints are available:

.. list-table::
   :align: left
   :widths: 75 15 30
   :header-rows: 1

   * - API Endpoint
     - Request Method
     - Parameters
   * - ``/company/{company_number}``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/officers``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/persons-with-significant-control``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/filing-history``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/charges``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/insolvency``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/exemptions``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/uk-establishments``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/registers``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/registered-office-address``
     - GET
     - company_number (str)

Example:

.. code:: python

   # Get company profile
   company = await client.get_company_profile("09370755")
   print(f"Company: {company.company_name}")
   print(f"Status: {company.company_status}")

.. _ch-api.officer-requests:

Officer Requests
================

Officers can be retrieved by officer ID, and you can search for officer appointments:

.. list-table::
   :align: left
   :widths: 75 15 30
   :header-rows: 1

   * - API Endpoint
     - Request Method
     - Parameters
   * - ``/officers/{officer_id}/appointments``
     - GET
     - officer_id (str)

Example:

.. code:: python

   # Get officer appointments
   appointments = await client.get_officer_appointments("abc123xyz")
   async for appointment in appointments:
       print(f"Company: {appointment.appointed_to.company_name}")

.. _ch-api.psc-requests:

PSC Requests
============

Persons with Significant Control can be retrieved for individual companies:

.. list-table::
   :align: left
   :widths: 75 15 30
   :header-rows: 1

   * - API Endpoint
     - Request Method
     - Parameters
   * - ``/company/{company_number}/persons-with-significant-control``
     - GET
     - company_number (str)
   * - ``/company/{company_number}/persons-with-significant-control/individual/{psc_id}``
     - GET
     - company_number (str), psc_id (str)
   * - ``/company/{company_number}/persons-with-significant-control/corporate-entity/{psc_id}``
     - GET
     - company_number (str), psc_id (str)
   * - ``/company/{company_number}/persons-with-significant-control/legal-person/{psc_id}``
     - GET
     - company_number (str), psc_id (str)

.. _ch-api.search-requests:

Search Requests
===============

Search endpoints allow you to find companies, officers, and disqualified directors:

.. list-table::
   :align: left
   :widths: 75 15 30
   :header-rows: 1

   * - API Endpoint
     - Request Method
     - Parameters
   * - ``/search/companies``
     - GET
     - q (query string)
   * - ``/search/officers``
     - GET
     - q (query string)
   * - ``/search/disqualified-officers``
     - GET
     - q (query string)
   * - ``/advanced-search/companies``
     - GET
     - Various filters

Example:

.. code:: python

   # Search for companies
   results = await client.search_companies("Apple")
   async for company in results:
       print(f"Found: {company.title} ({company.company_number})")

.. _ch-api.pagination:

Pagination
==========

Many API endpoints return paginated results. This library handles pagination automatically using the ``MultipageList`` class.

Pagination is lazy by default - pages are only fetched when needed:

.. code:: python

   # Search returns a MultipageList
   results = await client.search_companies("tech")
   
   # First page is fetched automatically
   print(f"Total results: {len(results)}")
   
   # Iterate through all results - pages load on demand
   async for company in results:
       print(company.title)
   
   # Or fetch all pages at once
   await results.fetch_all_pages()
   all_companies = results.local_items()

.. _ch-api.data-models:

Data Models
===========

All API responses are validated using Pydantic models. This provides:

- **Type safety**: All fields have defined types
- **Validation**: Data is validated against expected formats
- **Auto-completion**: IDEs can provide intelligent code completion
- **Documentation**: Field descriptions are available in docstrings

Models are organized in the ``ch_api.types`` module:

- ``ch_api.types.public_data.company_profile`` - Company profile data
- ``ch_api.types.public_data.company_officers`` - Officer information
- ``ch_api.types.public_data.psc`` - PSC data
- ``ch_api.types.public_data.filing_history`` - Filing history
- ``ch_api.types.public_data.charges`` - Charges
- And many more...

.. _ch-api.error-handling:

Error Handling
==============

The library provides custom exceptions for common error scenarios:

.. code:: python

   from ch_api.exc import (
       CompaniesHouseException,  # Base exception
       NotFoundError,             # 404 errors
       RateLimitError,            # 429 errors  
       AuthenticationError,       # 401 errors
   )

   try:
       company = await client.get_company_profile("invalid")
   except NotFoundError:
       print("Company not found")
   except RateLimitError:
       print("Rate limit exceeded - wait before retrying")
   except CompaniesHouseException as e:
       print(f"API error: {e}")

.. _ch-api.async-usage:

Async/Await Usage
=================

All API calls are asynchronous and must be awaited:

.. code:: python

   import asyncio
   from ch_api import Client, api_settings

   async def main():
       auth = api_settings.AuthSettings(api_key="your-api-key")
       client = Client(credentials=auth)
       
       # All API calls need await
       company = await client.get_company_profile("09370755")
       
       # Paginated results need async for
       results = await client.search_companies("Apple")
       async for company in results:
           print(company.title)
   
   # Run the async function
   asyncio.run(main())

.. _ch-api.advanced-features:

Advanced Features
=================

Test Data Generator
-------------------

The sandbox environment provides a test data generator endpoint for creating mock companies:

.. code:: python

   from ch_api import Client, api_settings
   
   # Use the sandbox/test environment
   auth = api_settings.AuthSettings(api_key="test-key")
   client = Client(
       credentials=auth,
       settings=api_settings.TEST_API_SETTINGS
   )
   
   # Create a test company
   request = types.test_data_generator.CreateTestCompanyRequest(
       company_type="ltd",
       company_status="active"
   )
   
   response = await client.create_test_company(request)
   print(f"Created test company: {response.company_number}")

Custom HTTP Session
-------------------

You can provide your own httpx.AsyncClient for advanced HTTP configuration:

.. code:: python

   import httpx
   
   # Create custom session with timeout and retry settings
   session = httpx.AsyncClient(
       timeout=30.0,
       limits=httpx.Limits(max_connections=10)
   )
   
   client = Client(
       credentials=auth,
       api_session=session
   )

.. _ch-api.further-reading:

Further Reading
===============

- `Official Companies House API Documentation <https://developer.company-information.service.gov.uk/>`_
- `API Reference Guide <https://developer-specs.company-information.service.gov.uk/>`_
- :doc:`Usage Examples <usage>`
- :doc:`API Reference <api-reference>`
