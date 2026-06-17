"""Pagination support for Companies House API list endpoints.

All paginated endpoints on ``Client`` accept ``next_page`` and ``page_size``
and return a single-page ``MultipageList[T]``. Advance one page at a time with
``get_next``::

    page = await client.search_companies("Apple")
    while page.pagination.has_next:
        page = await page.get_next()

Key Classes
-----------
- :class:`types.MultipageList` - Single-page result container with ``get_next``
- :class:`types.PaginationInfo` - Pagination metadata
- :class:`types.NextPageToken` - Opaque cursor type
- :class:`types.PageTokenSerializer` - Optional token encryption protocol
"""

from . import types
