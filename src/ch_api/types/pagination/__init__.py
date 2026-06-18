"""Pagination support for Companies House API list endpoints.

All paginated endpoints on ``Client`` accept ``page_size`` and ``result_count``
and return a ``MultipageList[T]``. ``result_count`` sets the minimum number of
items to collect in one call; ``get_next`` fetches the next batch::

    page = await client.search_companies("Apple", result_count=50)
    while page.pagination.has_next:
        page = await page.get_next()

``pagination.next_page`` is a self-contained cursor (it embeds the endpoint and
its arguments), so a fresh process can resume statelessly with only the token —
endpoints do not take a ``next_page`` argument; resume goes through
``fetch_next_page``::

    page2 = await client.fetch_next_page(token)

Key Classes
-----------
- :class:`types.MultipageList` - Result-batch container with a ``get_next`` handle
- :class:`types.PaginationInfo` - Pagination metadata
- :class:`types.NextPageToken` - Self-contained, restartable opaque cursor
- :class:`types.PageTokenSerializer` - Optional token encryption protocol
"""

from . import types
