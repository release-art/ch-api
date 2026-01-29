=====
Usage
=====

The library provides an async client (:py:class:`ch_api.api.Client`) that returns typed Pydantic models and handles pagination automatically.

Getting Started
===============

The client requires a Companies House API key for authentication. Here's a simple example:

.. code:: python

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

The client returns rich Pydantic models defined in :mod:`ch_api.types` and uses :class:`ch_api.types.pagination.paginated_list.MultipageList` for all paginated results. See :doc:`api-reference` for the full API surface.

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

The company profile contains core information about a company:

.. code:: python

   company = await client.get_company_profile("09370755")
   
   print(f"Company Name: {company.company_name}")
   print(f"Company Number: {company.company_number}")
   print(f"Company Status: {company.company_status}")
   print(f"Company Type: {company.type}")
   print(f"Incorporation Date: {company.date_of_creation}")
   
   # Registered office address
   address = company.registered_office_address
   print(f"Address: {address.address_line_1}, {address.locality}, {address.postal_code}")

Officers
--------

Get information about company officers (directors, secretaries, etc.):

.. code:: python

   # Get all officers for a company
   officers = await client.get_company_officers("09370755")
   
   async for officer in officers:
       print(f"Name: {officer.name}")
       print(f"Role: {officer.officer_role}")
       print(f"Appointed: {officer.appointed_on}")
       if officer.resigned_on:
           print(f"Resigned: {officer.resigned_on}")

Persons with Significant Control (PSC)
---------------------------------------

Get information about persons with significant control:

.. code:: python

   # Get all PSCs for a company
   pscs = await client.get_company_pscs("09370755")
   
   async for psc in pscs:
       print(f"Name: {psc.name}")
       print(f"Kind: {psc.kind}")
       print(f"Notified: {psc.notified_on}")
       print(f"Nature of Control: {psc.natures_of_control}")

Filing History
--------------

Access a company's filing history:

.. code:: python

   # Get filing history
   filings = await client.get_company_filing_history("09370755")
   
   async for filing in filings:
       print(f"Description: {filing.description}")
       print(f"Date: {filing.date}")
       print(f"Category: {filing.category}")

Charges
-------

Get information about charges registered against a company:

.. code:: python

   # Get charges
   charges = await client.get_company_charges("09370755")
   
   async for charge in charges:
       print(f"Charge Number: {charge.charge_number}")
       print(f"Created: {charge.created_on}")
       print(f"Status: {charge.status}")
       print(f"Persons Entitled: {charge.persons_entitled}")

.. _usage.search:

Searching
=========

Company Search
--------------

Search for companies by name:

.. code:: python

   # Simple search
   results = await client.search_companies("Apple")
   
   print(f"Total results: {len(results)}")
   
   async for company in results:
       print(f"Company: {company.title}")
       print(f"Number: {company.company_number}")
       print(f"Status: {company.company_status}")
       print(f"Type: {company.company_type}")

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
       location="London"
   )
   
   async for company in results:
       print(f"{company.company_name} ({company.company_number})")

Officer Search
--------------

Search for officers across all companies:

.. code:: python

   results = await client.search_officers("John Smith")
   
   async for officer in results:
       print(f"Name: {officer.title}")
       print(f"Date of Birth: {officer.date_of_birth}")
       # Note: Appointments not included in search results
       # Use get_officer_appointments() for details

Disqualified Officers
---------------------

Search for disqualified officers:

.. code:: python

   results = await client.search_disqualified_officers("Smith")
   
   async for officer in results:
       print(f"Name: {officer.title}")
       print(f"Date of Birth: {officer.date_of_birth}")

.. _usage.pagination:

Working with Pagination
=======================

Many API endpoints return paginated results. This library handles pagination automatically using :class:`ch_api.types.pagination.paginated_list.MultipageList`.

Lazy Loading
------------

By default, pagination is lazy - pages are only fetched when you access them:

.. code:: python

   # Only the first page is fetched initially
   results = await client.search_companies("tech")
   
   # Total count is available from the first page
   print(f"Total results: {len(results)}")
   
   # Iterate through all results - pages load on demand
   async for company in results:
       print(company.title)

Eager Loading
-------------

You can fetch all pages at once if you need all data immediately:

.. code:: python

   results = await client.search_companies("tech")
   
   # Fetch all pages at once
   await results.fetch_all_pages()
   
   # Now you can access all items without additional API calls
   all_companies = results.local_items()
   
   for company in all_companies:
       print(company.title)

Slicing and Indexing
--------------------

You can access results by index or slice:

.. code:: python

   results = await client.search_companies("tech")
   
   # Access first item (fetches first page if needed)
   first = results[0]
   
   # Access by slice (fetches pages as needed)
   first_ten = results[0:10]
   
   # Note: Negative indexing is not supported
   # This will raise an error: results[-1]

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

The library provides custom exceptions for common error scenarios:

.. code:: python

   from ch_api.exc import (
       CompaniesHouseException,  # Base exception
       NotFoundError,             # 404 errors
       RateLimitError,            # 429 errors  
       AuthenticationError,       # 401 errors
       ValidationError,           # Invalid parameters
   )
   
   try:
       company = await client.get_company_profile("invalid-number")
   except NotFoundError:
       print("Company not found")
   except ValidationError as e:
       print(f"Invalid company number format: {e}")
   except RateLimitError:
       print("Rate limit exceeded - wait before retrying")
   except AuthenticationError:
       print("Invalid API key")
   except CompaniesHouseException as e:
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
   results = await client.search_companies("Apple")
   
   # Convert all items to dictionaries
   companies_list = results.model_dump()

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
       companies = await client.search_companies("Technology Ltd", items_per_page=5)
       
       async for company in companies:
           print(f"\\nCompany: {company.title} ({company.company_number})")
           print(f"Status: {company.company_status}")
           
           # Get officers for each company
           try:
               officers = await client.get_company_officers(company.company_number)
               print("Officers:")
               async for officer in officers:
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
       officers = await client.get_company_officers(company_number)
       await officers.fetch_all_pages()
       data['officers'] = officers.model_dump()
       
       # PSCs
       try:
           pscs = await client.get_company_pscs(company_number)
           await pscs.fetch_all_pages()
           data['pscs'] = pscs.model_dump()
       except:
           data['pscs'] = []
       
       # Filing history (first 100)
       filings = await client.get_company_filing_history(company_number, items_per_page=100)
       data['filing_history'] = filings.model_dump()
       
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
       filings = await client.get_company_filing_history(company_number, items_per_page=100)
       
       # Filter for recent filings (last 30 days)
       cutoff_date = datetime.now().date() - timedelta(days=30)
       
       print(f"Recent filings for {company_number}:\\n")
       
       async for filing in filings:
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

- Make sure you're using ``async for`` to iterate, not regular ``for``
- Check you're awaiting the initial API call
- Verify you're not trying to use negative indexing (not supported)
