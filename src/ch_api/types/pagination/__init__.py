"""Pagination support for Companies House API list endpoints.

All paginated endpoints on ``Client`` accept ``next_page`` and ``result_count``
and return ``MultipageList[T]``::

    page = await client.search_companies("Apple")
    while page.pagination.has_next:
        page = await client.search_companies(
            "Apple",
            next_page=page.pagination.next_page,
            result_count=25,
        )

Key Classes
-----------
- :class:`types.MultipageList` - Simple paginated result container
- :class:`types.PaginationInfo` - Pagination metadata
- :class:`types.NextPageToken` - Opaque cursor type
- :class:`types.PageTokenSerializer` - Optional token encryption protocol
"""

from . import types
