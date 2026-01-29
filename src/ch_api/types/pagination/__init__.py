"""Pagination support for Companies House API list endpoints.

This package provides utilities and types for handling paginated API responses,
including the main ``MultipageList`` container and related type definitions.

Modules
-------
- :mod:`paginated_list` - MultipageList container for paginated results
- :mod:`types` - Type definitions for pagination

Key Classes
-----------
- :class:`paginated_list.MultipageList` - Main paginated list container
- :class:`types.PaginatedResultInfo` - Pagination metadata
- :class:`types.FetchPageCallArg` - Arguments for page fetch callbacks

Usage
-----
Paginated results are returned automatically by search and list methods::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    # Returns MultipageList
    results = await client.search_companies("Apple")

    # Check total count
    print(f"Total: {len(results)}")

    # Iterate through all results
    async for company in results:
        print(f"Company: {company.title}")

    # Access by index
    if len(results) > 10:
        eleventh = results[10]

    # Fetch all pages
    await results.fetch_all_pages()
    for company in results.local_items():
        process(company)

Features
--------
- **Lazy loading**: Pages fetched only when accessed
- **Async iteration**: ``async for`` support
- **List-like interface**: ``len()``, indexing, slicing
- **Caching**: Fetched pages are cached in memory
- **Non-blocking**: Fully asynchronous operations

See Also
--------
paginated_list.MultipageList : Main container class
types.PaginatedResultInfo : Pagination metadata
"""

from . import paginated_list, types
