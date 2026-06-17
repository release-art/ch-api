"""Pagination support for Companies House API list endpoints.

All paginated endpoints on ``Client`` accept ``page_size``, ``next_page``, and
``result_count``, and return a ``MultipageList[T]``. ``result_count`` sets the
minimum number of items to collect in one call; ``get_next`` fetches the next
batch::

    page = await client.search_companies("Apple", result_count=50)
    while page.pagination.has_next:
        page = await page.get_next()

Key Classes
-----------
- :class:`types.MultipageList` - Result-batch container with a ``get_next`` handle
- :class:`types.PaginationInfo` - Pagination metadata
- :class:`types.NextPageToken` - Opaque cursor type
- :class:`types.PageTokenSerializer` - Optional token encryption protocol
"""

from . import types
