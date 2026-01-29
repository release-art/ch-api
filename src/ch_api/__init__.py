"""Companies House API Python Client.

This package provides a comprehensive, async-first Python client for the
Companies House API (https://www.companieshouse.gov.uk/), allowing you to
retrieve real-time information about UK companies including profiles, officers,
charges, filing history, and more.

Quick Start
-----------
Get started with just a few lines of code::

    from ch_api import Client, api_settings

    # Create credentials
    auth = api_settings.AuthSettings(api_key="your-api-key")

    # Create client
    client = Client(credentials=auth)

    # Fetch company information
    company = await client.get_company_profile("09370755")
    print(f"Company: {company.company_name} ({company.company_status})")

    # Search for companies
    results = await client.search_companies("Apple")
    async for company in results:
        print(f"Found: {company.title}")

    # Get officers
    officers = await client.get_officer_list("09370755")
    async for officer in officers:
        print(f"Officer: {officer.name}")

Core Components
---------------
- :class:`Client` - Main API client (asynchronous)
- :mod:`api_settings` - Configuration and authentication
- :mod:`types` - Pydantic models for all API responses
- :mod:`exc` - Custom exception types

API Capabilities
----------------
The client provides access to:

**Company Information**
- Company profiles and current status
- Registered office address
- Accounts and financial filing status
- Company registers

**Officers & Management**
- Directors, secretaries, and LLP members
- Officer appointment history
- Officer-specific appointments across companies

**Ownership & Control**
- Persons with Significant Control (PSC)
- PSC statements and declarations
- Beneficial ownership information

**Financial & Legal**
- Charges over company assets
- Filing history and documents
- Exemptions from filing requirements
- Insolvency proceedings

**Search Capabilities**
- General search (companies and officers)
- Advanced company search with filters
- Alphabetical company search
- Dissolved company search
- Officer search
- Disqualified officer search

Authentication
--------------
Authentication requires an API key from the Companies House Developer Portal:
1. Register at https://developer.company-information.service.gov.uk/
2. Create an application to get your API key
3. Pass credentials to the Client::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

Environments
------------
Two API environments are available:

**Production (Live)**
- Real, up-to-date company data
- Use ``api_settings.LIVE_API_SETTINGS`` (default)

**Sandbox (Test)**
- Test with dummy data
- Includes Test Data Generator API
- Use ``api_settings.TEST_API_SETTINGS``::

    client = Client(credentials=auth, settings=api_settings.TEST_API_SETTINGS)

Rate Limiting
-------------
The API enforces rate limits. Consider using an async rate limiter::

    import asyncio_throttle

    limiter = asyncio_throttle.AsyncThrottle(max_rate=5, time_period=1.0)
    client = Client(credentials=auth, api_limiter=lambda: limiter)

Async Design
------------
All API calls are asynchronous and must be called with ``await``::

    # Correct - using await
    company = await client.get_company_profile("09370755")

    # Run in async context
    import asyncio
    asyncio.run(my_async_function())

Pagination
----------
Search and list endpoints return paginated results automatically handled
via the ``MultipageList`` interface::

    results = await client.search_companies("Apple")

    # Check total without loading all pages
    print(f"Total: {len(results)}")

    # Iterate (loads pages as needed)
    async for company in results:
        print(company.title)

    # Access by index (loads page if needed)
    if len(results) > 0:
        first = results[0]

Exception Handling
------------------
Handle API errors with custom exceptions::

    from ch_api import exc

    try:
        company = await client.get_company_profile("invalid")
    except exc.UnexpectedApiResponseError as e:
        print(f"Unexpected response: {e}")
    except exc.CompaniesHouseApiError as e:
        print(f"API error: {e}")

Error Handling:
- Network errors (httpx)
- Validation errors (pydantic)
- API-specific errors (exc module)

Documentation
--------------
- Companies House API Docs: https://developer-specs.company-information.service.gov.uk/
- Getting Started: https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
- API Reference: https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/swagger.json

Examples
--------
See the Examples section in documentation for more use cases.

Modules
-------
- :mod:`api` - Client implementation
- :mod:`api_settings` - Configuration and authentication
- :mod:`types` - All Pydantic models
- :mod:`exc` - Exception types

Support & Issues
----------------
- GitHub: https://github.com/companieshouse/api-specifications
- Forum: Companies House Developer Forum
- Issues: Report via GitHub

License
-------
See LICENSE file for details.
"""

from . import __version__, api, api_settings, exc, types

__all__ = [
    "__version__",
    "api",
    "api_settings",
    "exc",
    "types",
    "Client",
    "AuthSettings",
    "ApiSettings",
    "LIVE_API_SETTINGS",
    "TEST_API_SETTINGS",
]

# Convenience imports for common classes
Client = api.Client
AuthSettings = api_settings.AuthSettings
ApiSettings = api_settings.ApiSettings
LIVE_API_SETTINGS = api_settings.LIVE_API_SETTINGS
TEST_API_SETTINGS = api_settings.TEST_API_SETTINGS
