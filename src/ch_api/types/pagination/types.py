"""Pagination types and utilities for Companies House API responses.

This module provides type definitions and models for handling paginated
responses from the Companies House API.

Key Types
-----
- :class:`PaginatedResultInfo` - Metadata about a page of results
- :class:`FetchPageCallArg` - Arguments for page fetch callbacks
- :class:`FetchPageRvT` - Return type for page fetching functions
- :class:`FetchPageCallableT` - Type signature for page fetch callbacks

Pagination Model
-----
The Companies House API uses cursor-based pagination with:
- ``start_index`` - Position to start retrieving items
- ``items_per_page`` - Number of items to return
- Response includes total count for pagination calculations

See Also
--------
ch_api.types.pagination.paginated_list : MultipageList container for paginated results
"""

import dataclasses
import typing

import pydantic

T = typing.TypeVar("T", bound=pydantic.BaseModel)


class PaginatedResultInfo(pydantic.BaseModel):
    """Pagination metadata from Companies House API responses.

    This model represents pagination information returned by the Companies House API,
    including the current page number, whether more pages are available, and page size.

    Attributes
    ----------
    page : int
        The current page number (1-based). Page 1 is the first page of results.

    has_next : bool
        Whether there are more pages available after this one.
        - ``True`` if there are additional pages to fetch
        - ``False`` if this is the last page

    per_page : int, optional
        Number of items per page (if available from API response).

    total_count : int, optional
        Total number of items across all pages (if available from API response).

    Example
    -------
    Access pagination metadata::

        info = PaginatedResultInfo(
            page=1,
            has_next=True,
            per_page=50,
            total_count=250
        )

        print(f"Page {info.page}")
        if info.has_next:
            print("More pages available")

    Note
    ----
    This is used internally by the :class:`~ch_api.types.pagination.paginated_list.MultipageList`
    class to manage pagination automatically. Most users don't interact with this directly.

    See Also
    --------
    MultipageList : Automatically handles pagination using this metadata
    """

    page: int
    has_next: bool


#: Type alias for the return type of page fetch functions.
#:
#: This is a tuple containing:
#: 1. Optional PaginatedResultInfo: Metadata about the fetched page (None if fetch failed)
#: 2. Sequence of items: The actual items from this page
#:
#: Used internally for pagination callbacks.
FetchPageRvT = typing.Tuple[
    typing.Optional[PaginatedResultInfo],
    typing.Sequence[T],
]


@dataclasses.dataclass(frozen=True, kw_only=True)
class FetchPageCallArg(typing.Generic[T]):
    """Arguments passed to page fetch callback functions.

    This dataclass contains information about the current pagination state,
    used by the pagination system to determine what page to fetch next.

    Attributes
    ----------
    first_known_item : Optional[T]
        The first item currently cached in the MultipageList (None if empty).
        Used for cursor-based pagination strategies.

    last_known_item : Optional[T]
        The last item currently cached (None if empty).
        Used for cursor-based pagination strategies.

    current_total_list_len : int
        Total number of items currently cached across all fetched pages.
        Useful for calculating the start_index for the next page fetch.

    last_fetched_page : int
        The page number of the most recently fetched page (0-based).
        Use this to calculate which page to fetch next.

    Example
    -------
    Use in a page fetch callback::

        async def fetch_page(target: FetchPageCallArg[MyItem]) -> FetchPageRvT[MyItem]:
            # Calculate offset for next page
            start_index = target.current_total_list_len

            # Build API request for next page
            response = await api.get_page(
                start_index=start_index,
                items_per_page=50
            )

            page_info = PaginatedResultInfo(
                page=target.last_fetched_page + 1,
                has_next=has_more_pages,
                per_page=50,
                total_count=response.total
            )

            return (page_info, response.items)

    See Also
    --------
    FetchPageCallableT : Type alias for page fetch callbacks
    """

    first_known_item: typing.Optional[T]
    last_known_item: typing.Optional[T]
    current_total_list_len: int
    last_fetched_page: int


#: Type alias for page fetch callback functions.
#:
#: A callable that takes :class:`FetchPageCallArg` and returns an awaitable
#: that yields :class:`FetchPageRvT`.
#:
#: Example signature::
#:
#:     async def fetch_page(target: FetchPageCallArg[Item]) -> FetchPageRvT[Item]:
#:         # Fetch and return page data
#:         ...
#:
#: See Also:
#:     FetchPageCallArg : Arguments to page fetch callbacks
#:     FetchPageRvT : Return type of page fetch callbacks
FetchPageCallableT = typing.Callable[[FetchPageCallArg], typing.Awaitable[FetchPageRvT[T]]]


#: Sentinel value representing the end of a paginated list.
#:
#: This is returned by page fetching to indicate no more pages are available.
#: It's a tuple of (None, empty_sequence) to match the FetchPageRvT type.
LIST_EOT = (
    None,
    (),
)
