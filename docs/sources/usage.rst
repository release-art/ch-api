=====
Usage
=====

The library provides an async client (:py:class:`ch_api.api.Client`) that returns typed Pydantic models and handles pagination automatically.

Getting Started
===============

The client requires a Companies House API key for authentication. Here's a simple example:

.. code-block:: python

   import asyncio
   from ch_api import Client, api_settings


   async def main() -> None:
       auth = api_settings.AuthSettings(api_key="your-api-key-here")
       client = Client(credentials=auth)
       
       # Get a company profile
       company = await client.get_company_profile("09370755")
       print(f"Company: {company.company_name}")
       print(f"Status: {company.company_status}")


   if __name__ == "__main__":
       asyncio.run(main())

Or using the test client with run_async_func::

    >>> async def get_company_demo(client):
    ...     company = await client.get_company_profile("09370755")
    ...     return company is not None
    >>> run_async_func(get_company_demo)
    True

The client returns rich Pydantic models defined in :mod:`ch_api.types` and uses :class:`ch_api.types.pagination.types.MultipageList` for all paginated results. See :doc:`api-reference` for the full API surface.

.. _usage.authentication:

Authentication
==============

All requests to the Companies House API require authentication via an API key. You can obtain an API key by:

1. `Registering for a Companies House account <https://developer.company-information.service.gov.uk/get-started>`_
2. Creating an application in your account
3. Obtaining the API key for your application

Pass your API key to the client using :class:`ch_api.api_settings.AuthSettings`:

.. code:: python

   from ch_api import Client, api_settings

   auth = api_settings.AuthSettings(api_key="your-api-key-here")
   client = Client(credentials=auth)

.. _usage.company-data:

Working with Company Data
=========================

Company Profile
---------------

The company profile contains core information about a company::

    >>> async def company_profile_example(client):
    ...     company = await client.get_company_profile("09370755")
    ...     return company.company_name is not None and company.company_number is not None
    >>> run_async_func(company_profile_example)
    True

Officers
--------

Get information about company officers (directors, secretaries, etc.)::

    >>> async def officers_example(client):
    ...     officers = await client.get_officer_list("09370755", result_count=1)
    ...     return len(officers.data) >= 1
    >>> run_async_func(officers_example)
    True

Persons with Significant Control (PSC)
---------------------------------------

Get information about persons with significant control::

    >>> async def psc_example(client):
    ...     result = await client.get_company_psc_list("09370755")
    ...     return result is not None
    >>> run_async_func(psc_example)
    True

Filing History
--------------

Access a company's filing history:

.. code:: python

   # Get filing history
   filings = await client.get_company_filing_history("09370755", result_count=100)
   for filing in filings.data:
       print(f"Description: {filing.description}")
       print(f"Date: {filing.date}")
       print(f"Category: {filing.category}")

Charges
-------

Get information about charges registered against a company:

.. code:: python

   # Get charges
   charges = await client.get_company_charges("09370755", result_count=100)
   for charge in charges.data:
       print(f"Charge Number: {charge.charge_number}")
       print(f"Created: {charge.created_on}")
       print(f"Status: {charge.status}")
       print(f"Persons Entitled: {charge.persons_entitled}")

.. _usage.search:

Searching
=========

Company Search
--------------

Search for companies by name::

    >>> async def search_companies_example(client):
    ...     results = await client.search_companies("Apple", result_count=1)
    ...     return len(results.data) >= 1
    >>> run_async_func(search_companies_example)
    True

Advanced Company Search
-----------------------

Use advanced search with multiple criteria:

.. code:: python

   from ch_api.types.public_data.search_companies import CompanySearchQuery
   
   # Advanced search with filters
   results = await client.advanced_company_search(
       company_name_includes="tech",
       company_status="active",
       company_type="ltd",
       location="London",
       result_count=100,
   )
   for company in results.data:
       print(f"{company.company_name} ({company.company_number})")

Officer Search
--------------

Search for officers across all companies:

.. code:: python

   results = await client.search_officers("John Smith", result_count=100)
   for officer in results.data:
       print(f"Name: {officer.title}")
       print(f"Date of Birth: {officer.date_of_birth}")
       # Note: Appointments not included in search results
       # Use get_officer_appointments() for details

Disqualified Officers
---------------------

Search for disqualified officers:

.. code:: python

   results = await client.search_disqualified_officers("Smith", result_count=100)
   for officer in results.data:
       print(f"Name: {officer.title}")
       print(f"Date of Birth: {officer.date_of_birth}")

.. _usage.pagination:

Working with Pagination
=======================

Many API endpoints return paginated results as :class:`ch_api.types.pagination.types.MultipageList`, a simple value object with ``data`` (list of items) and ``pagination`` (cursor metadata).

Fetching a page::

    >>> async def lazy_loading_example(client):
    ...     results = await client.search_companies("tech", result_count=1)
    ...     return len(results.data) >= 1
    >>> run_async_func(lazy_loading_example)
    True

Fetching multiple pages
-----------------------

Use ``result_count`` to fetch more items in one call, or loop with ``next_page``:

.. code:: python

   # Fetch at least 100 items (may make multiple underlying requests)
   page = await client.search_companies("tech", result_count=100)
   for company in page.data:
       print(company.title)

   # Manual cursor-based paging
   page = await client.search_companies("tech", result_count=25)
   while page.pagination.has_next:
       page = await client.search_companies(
           "tech",
           next_page=page.pagination.next_page,
           result_count=25,
       )

.. _usage.rate-limiting:

Rate Limiting
=============

The Companies House API has rate limits (600 requests per 5 minutes). You can integrate rate limiting using an async rate limiter:

.. code:: python

   from asyncio_throttle import Throttler
   
   # Allow 600 requests per 5 minutes (300 seconds)
   throttler = Throttler(rate_limit=600, period=300)
   
   async def limiter():
       async with throttler:
           yield
   
   # Pass the limiter to the client
   client = Client(credentials=auth, limiter=limiter)
   
   # Now all requests will be rate limited
   company = await client.get_company_profile("09370755")

.. _usage.error-handling:

Error Handling
==============

The library provides custom exceptions and uses httpx exceptions for HTTP errors:

.. code:: python

   import httpx
   from ch_api.exc import CompaniesHouseApiError, UnexpectedApiResponseError
   
   # get_company_profile returns None for not found (404)
   company = await client.get_company_profile("00000000")
   if company is None:
       print("Company not found")
   
   # Other operations may raise HTTPStatusError
   try:
       results = await client.search_companies("test")
   except httpx.HTTPStatusError as e:
       if e.response.status_code == 429:
           print("Rate limit exceeded - wait before retrying")
       elif e.response.status_code == 401:
           print("Authentication error")
   except UnexpectedApiResponseError as e:
       print(f"Unexpected API response: {e}")
   except CompaniesHouseApiError as e:
       print(f"API error: {e}")

.. _usage.advanced:

Advanced Usage
==============

Custom HTTP Session
-------------------

You can provide your own httpx.AsyncClient for advanced HTTP configuration:

.. code:: python

   import httpx
   
   # Create custom session with timeout and connection limits
   session = httpx.AsyncClient(
       timeout=30.0,
       limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
   )
   
   client = Client(
       credentials=auth,
       api_session=session
   )
   
   # Remember to close the session when done
   await session.aclose()

Using the Sandbox Environment
------------------------------

Companies House provides a sandbox environment for testing. Use the test settings:

.. code:: python

   from ch_api import api_settings
   
   # Use sandbox environment
   auth = api_settings.AuthSettings(api_key="test-key")
   client = Client(
       credentials=auth,
       settings=api_settings.TEST_API_SETTINGS
   )
   
   # The sandbox has a test data generator
   from ch_api.types.test_data_generator import CreateTestCompanyRequest
   
   request = CreateTestCompanyRequest(
       company_type="ltd",
       company_status="active"
   )
   
   response = await client.create_test_company(request)
   print(f"Created test company: {response.company_number}")
   print(f"Auth code: {response.auth_code}")
   
   # You can now use this company number for testing
   company = await client.get_company_profile(response.company_number)

Type Hints and IDE Support
---------------------------

All methods and return types are fully typed, providing excellent IDE support:

.. code:: python

   # Your IDE will show:
   # - Available methods on the client
   # - Expected parameter types
   # - Return type information
   # - Available fields on returned models
   
   company = await client.get_company_profile("09370755")
   
   # IDE knows company is a CompanyProfile instance
   # and will autocomplete its fields:
   print(company.company_name)      # str
   print(company.date_of_creation)  # datetime.date
   print(company.company_status)    # str

Accessing Underlying Data
--------------------------

All Pydantic models support conversion to dictionaries:

.. code:: python

   company = await client.get_company_profile("09370755")
   
   # Convert to dictionary
   company_dict = company.model_dump()
   
   # Convert to JSON
   company_json = company.model_dump_json()
   
   # For paginated results
   results = await client.search_companies("Apple", result_count=25)

   # Convert all items to dictionaries
   companies_list = [c.model_dump() for c in results.data]

.. _usage.examples:

Complete Examples
=================

Find Companies and Their Officers
----------------------------------

.. code:: python

   import asyncio
   from ch_api import Client, api_settings


   async def find_companies_and_officers():
       auth = api_settings.AuthSettings(api_key="your-api-key")
       client = Client(credentials=auth)

       # Search for companies
       companies = await client.search_companies("Technology Ltd", result_count=5)

       for company in companies.data:
           print(f"\\nCompany: {company.title} ({company.company_number})")
           print(f"Status: {company.company_status}")

           # Get officers for each company
           try:
               officers = await client.get_officer_list(company.company_number, result_count=100)
               print("Officers:")
               for officer in officers.data:
                   print(f"  - {officer.name} ({officer.officer_role})")
           except Exception as e:
               print(f"  Error getting officers: {e}")


   if __name__ == "__main__":
       asyncio.run(find_companies_and_officers())

Export Company Data
-------------------

.. code:: python

   import asyncio
   import json
   from ch_api import Client, api_settings


   async def export_company_data(company_number: str, output_file: str):
       auth = api_settings.AuthSettings(api_key="your-api-key")
       client = Client(credentials=auth)
       
       # Gather all company data
       data = {}
       
       # Company profile
       data['profile'] = (await client.get_company_profile(company_number)).model_dump()
       
       # Officers
       officers = await client.get_officer_list(company_number, result_count=200)
       data['officers'] = [o.model_dump() for o in officers.data]

       # PSCs
       psc_result = await client.get_company_psc_list(company_number, result_count=200)
       data['pscs'] = [p.model_dump() for p in psc_result.data]

       # Filing history (first 100)
       filings = await client.get_company_filing_history(company_number, result_count=100)
       data['filing_history'] = [f.model_dump() for f in filings.data]
       
       # Write to file
       with open(output_file, 'w') as f:
           json.dump(data, f, indent=2, default=str)
       
       print(f"Data exported to {output_file}")


   if __name__ == "__main__":
       asyncio.run(export_company_data("09370755", "company_data.json"))

Monitor Company Changes
-----------------------

.. code:: python

   import asyncio
   from datetime import datetime, timedelta
   from ch_api import Client, api_settings


   async def monitor_recent_filings(company_number: str):
       auth = api_settings.AuthSettings(api_key="your-api-key")
       client = Client(credentials=auth)
       
       # Get filing history
       filings = await client.get_company_filing_history(company_number, result_count=100)

       # Filter for recent filings (last 30 days)
       cutoff_date = datetime.now().date() - timedelta(days=30)

       print(f"Recent filings for {company_number}:\\n")
       for filing in filings.data:
           if filing.date >= cutoff_date:
               print(f"Date: {filing.date}")
               print(f"Description: {filing.description}")
               print(f"Category: {filing.category}")
               print()


   if __name__ == "__main__":
       asyncio.run(monitor_recent_filings("09370755"))

.. _usage.best-practices:

Best Practices
==============

1. **Use Rate Limiting**: Always implement rate limiting to avoid hitting API limits
2. **Handle Errors Gracefully**: Wrap API calls in try/except blocks to handle failures
3. **Use Lazy Pagination**: Don't fetch all pages unless you need all data
4. **Close Sessions**: If using a custom session, remember to close it
5. **Cache Results**: Consider caching frequently accessed data to reduce API calls
6. **Test with Sandbox**: Use the sandbox environment for development and testing
7. **Validate Input**: Use the provided type hints and validation to catch errors early
8. **Monitor Rate Limits**: Track your API usage to stay within limits

.. _usage.troubleshooting:

Troubleshooting
===============

Rate Limit Exceeded
-------------------

If you get HTTP 429 errors:

- Implement rate limiting (see :ref:`usage.rate-limiting`)
- Reduce the number of requests per minute
- Wait 5 minutes before retrying after hitting the limit

Authentication Errors
---------------------

If you get HTTP 401 errors:

- Check your API key is correct
- Ensure you're not accidentally using test credentials in production
- Verify your API key hasn't expired

Company Not Found
-----------------

If you get HTTP 404 errors:

- Verify the company number is correct (8 characters, may include leading zeros)
- Check if the company has been dissolved or struck off
- Ensure you're using the correct format (e.g., "09370755" not "9370755")

Pagination Issues
-----------------

If pagination isn't working as expected:

- Use a regular ``for`` loop over ``result.data`` (it's a plain list)
- Pass ``result_count`` to fetch more than one page's worth of items
- Use ``result.pagination.next_page`` to fetch subsequent pages manually
