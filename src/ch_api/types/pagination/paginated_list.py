"""Pagination support for Companies House API list endpoints.

This module provides utilities for handling paginated API responses from the
Companies House API. The main class, :class:`MultipageList`, implements a
list-like interface for paginated results with automatic page fetching,
async iteration, and indexing support.

The Companies House API uses cursor-based pagination for many endpoints
(search, officers, filing history, etc.). This module abstracts away the
complexity of managing page fetches and provides a familiar Python list interface.

Pagination System
-----------------
The pagination system supports:

- **Lazy loading**: Pages are only fetched when accessed
- **Async iteration**: Full support for ``async for`` loops
- **List-like interface**: ``len()``, indexing, and slicing
- **Automatic caching**: Already-fetched pages are cached in memory
- **Random access**: Jump to any index without fetching all pages

Key Features
---------------------
- Automatic page fetching on demand
- Efficient memory usage (pages are kept in cache)
- Full async iteration support with ``async for``
- Standard list operations: ``len()``, ``[]``, ``async for``
- Manual control with :meth:`MultipageList.fetch_all_pages`

Example
-------
Working with paginated results::

    # Get paginated search results from Companies House API
    results = await client.search_companies("Apple")

    # Check total count without loading all pages
    print(f"Total results: {len(results)}")

    # Iterate through all results (loads pages as needed)
    async for company in results:
        print(f"{company.title} ({company.company_number})")

    # Access specific items by index (loads page if needed)
    if len(results) > 0:
        first_company = results[0]
        print(f"First result: {first_company.title}")

    # Load all pages at once for bulk processing
    await results.fetch_all_pages()

    # Now all data is locally cached
    for company in results.local_items():
        process_company(company)

API Pagination Details
----------------------
The Companies House API uses ``start_index`` and ``items_per_page`` query
parameters for pagination. The response includes:

- ``start_index``: The index of the first item in the response
- ``items_per_page``: Number of items in this response
- ``total_results``: Total number of results available

This module automatically calculates when the next page is available and
fetches it on demand.

References
----------
- https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
- https://developer-specs.company-information.service.gov.uk/guides/developerGuidelines

See Also
--------
MultipageList : The main paginated list container
PaginatedResultInfo : Metadata about a page of results
FetchedPageData : Cached page data
"""

import asyncio
import dataclasses
import enum
import logging
import typing

import httpx
import pydantic
import pydantic_core

from ... import exc
from . import types

logger = logging.getLogger(__name__)

T = typing.TypeVar("T", bound=pydantic.BaseModel)


@enum.unique
class SpecialResultInfoState(enum.Enum):
    UNINITIALIZED = enum.auto()
    FIRST_PAGE_FETCH_FAILED = enum.auto()
    ALL_PAGES_FETCHED = enum.auto()
    PAGE_FETCH_FAILED = enum.auto()


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class FetchedPageData(typing.Generic[T]):
    items: typing.Sequence[T]
    page_info: typing.Optional[types.PaginatedResultInfo]


class MultipageList(typing.Generic[T]):
    """A list-like container for paginated Companies House API responses.

    This class provides a seamless, Pythonic interface for working with
    paginated data from the Companies House API. It behaves like a regular
    Python list but transparently handles page fetching, caching, and
    efficient memory usage for large result sets.

    The class implements lazy loading: pages are only fetched from the API
    when actually needed (e.g., when iterating or accessing specific indices).
    This approach provides efficient memory usage even for result sets with
    thousands of items.

    Type Parameters
    ----------------
    T : Type
        The type of items contained in the list. Usually a Pydantic model
        representing API response objects (e.g., CompanyProfile, Officer).

    Key Features
    -----
    - **Lazy page loading**: Pages fetched only when accessed
    - **Async iteration**: Full support for ``async for`` loops
    - **List operations**: ``len()``, indexing ``[i]``, and slicing ``[i:j]``
    - **Caching**: Already-fetched pages are cached in memory
    - **Non-blocking**: All operations are fully asynchronous
    - **Memory efficient**: Only loaded pages consume memory

    Attributes
    ----------
    _pages : list[FetchedPageData[T]]
        List of cached pages of results
    _fetch_page_cb : Callable
        Async function to fetch individual pages from the API
    _lock : asyncio.Lock
        Lock for thread-safe concurrent access
    _result_info : PaginatedResultInfo or SpecialResultInfoState
        Current pagination state and metadata

    Example Usage
    -----
    Typical usage patterns with Companies House API::

        # Get search results (returns MultipageList)
        results = await client.search_companies("Apple")

        # Check total count without loading all pages
        total = len(results)  # First page is fetched for this
        print(f"Found {total} companies")

        # Iterate through all results (loads pages as needed)
        async for company in results:
            print(f"{company.title} ({company.company_number})")

        # Access specific items by index (loads page if needed)
        if len(results) > 10:
            tenth_company = results[9]  # 0-indexed
            print(f"10th result: {tenth_company.title}")

        # Get first few items without fetching all
        first_three = results[0:3]  # Only fetches first page

        # Bulk processing with pre-loading
        await results.fetch_all_pages()
        for company in results.local_items():
            process_company(company)

    Async Iteration
    -----
    Iterate through all results with automatic page fetching::

        async for company in results:
            print(f"Processing {company.company_number}")

    Indexing and Slicing
    -----
    Access specific items or ranges::

        first = results[0]              # First item
        last = results[-1]              # Last item
        slice = results[10:20]          # Items 10-19
        reverse = results[::-1]         # All items reversed

    State Management
    -----
    The :class:`SpecialResultInfoState` enum tracks pagination state:

    - ``UNINITIALIZED``: First page not yet fetched
    - ``FIRST_PAGE_FETCH_FAILED``: Failed to fetch first page
    - ``ALL_PAGES_FETCHED``: All pages have been retrieved
    - ``PAGE_FETCH_FAILED``: Error fetching a middle page

    Performance Considerations
    -----
    - **Lazy loading**: Perfect for large result sets you only partially process
    - **Memory usage**: Only loaded pages consume memory
    - **Network requests**: One API call per page fetched
    - **Caching**: Pages are kept in memory once fetched

    For processing entire large result sets, call :meth:`fetch_all_pages` first
    to fetch everything, then iterate through :meth:`local_items` for fastest access.

    Note
    ----
    The API requires ``start_index`` and ``items_per_page`` parameters for pagination.
    This class automatically manages these parameters across page fetches.

    See Also
    --------
    PaginatedResultInfo : Metadata about a single page
    FetchedPageData : Internal cache entry for a page
    fetch_all_pages : Fetch all remaining pages into memory
    local_items : Get cached items without fetching

    References
    ----------
    - https://developer-specs.company-information.service.gov.uk/guides/developerGuidelines
    - https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
    """

    _pages: typing.List[FetchedPageData[T]]
    _fetch_page_cb: types.FetchPageCallableT[T]
    _lock: asyncio.Lock
    _result_info: types.PaginatedResultInfo | SpecialResultInfoState

    def __init__(
        self,
        /,
        fetch_page: types.FetchPageCallableT[T],
    ) -> None:
        """Initialize a new MultipageList.

        Args:
            fetch_page: Async function that fetches a page of results given
                a page index. Should return a tuple of (pagination_info, items).

        Note:
            After initialization, call `_async_init()` to fetch the first page
            and populate metadata. This is done automatically by the high-level
            client methods.

        Example:
            Manual MultipageList creation::

                async def fetch_firms(page_idx: int):
                    response = await raw_client.search_frn("test", page=page_idx)
                    # Parse and return (info, items)

                results = MultipageList(fetch_page=fetch_firms)
                await results._async_init()  # Required!
        """
        self._pages = []
        self._lock = asyncio.Lock()
        self._fetch_page_cb = fetch_page
        self._result_info = SpecialResultInfoState.UNINITIALIZED

    def _has_next_page(self) -> bool:
        if self._result_info is SpecialResultInfoState.UNINITIALIZED:
            return True
        elif isinstance(self._result_info, SpecialResultInfoState):
            # Any other special state means that there are no more pages to fetch.
            return False
        assert isinstance(self._result_info, types.PaginatedResultInfo)
        return self._result_info.has_next

    async def _async_init(self) -> None:
        """Initialize the MultipageList by fetching the first page.

        This method must be called after construction to populate the initial
        pagination metadata. It fetches the first page to determine total
        counts, page sizes, and other pagination information.

        Raises:
            Various exceptions depending on the fetch_page callback behavior
            (typically HTTP errors, validation errors, etc.)

        Note:
            This method is called automatically by the high-level client methods.
            Manual callers must ensure this is called before using the list.

        Example:
            Manual initialization::

                results = MultipageList(fetch_page=my_fetch_function)
                await results._async_init()  # Required before use
                print(len(results))  # Now safe to call
        """
        # Fetch the first page to initialize the result info.
        await self._fetch_page_to_item_idx(0)

    async def fetch_all_pages(self) -> None:
        """Fetch all remaining pages from the API.

        This method loads all pages into local memory, which can be useful
        for bulk processing scenarios where you need to access the data
        multiple times or perform operations that require the complete dataset.

        After calling this method, all subsequent access to the list items
        will be served from the local cache without additional API calls.

        Example:
            Bulk processing pattern::

                results = await client.search_frn("test")

                # Load all data once
                await results.fetch_all_pages()

                # Now process multiple times without API calls
                authorised = [f for f in results.local_items() if f.status == "Authorised"]
                unauthorised = [f for f in results.local_items() if f.status != "Authorised"]

                print(f"Authorised: {len(authorised)}, Unauthorised: {len(unauthorised)}")

        Warning:
            This method can consume significant memory and time for large result
            sets. Use judiciously and consider whether streaming with async
            iteration might be more appropriate.
        """
        while self._has_next_page():
            await self._fetch_page_to_item_idx(self.local_len() + 1)

    async def _fetch_page_to_item_idx(self, desired_item_idx: int) -> typing.Optional[types.PaginatedResultInfo]:  # noqa: C901
        """Fetch a specific page from the API if it is not already cached.

        Args:
            desired_item_idx: The index of the desired item to fetch.
        """
        if self.local_len() > desired_item_idx or not self._has_next_page():
            return None

        new_page_info = None
        async with self._lock:
            # Double-check after acquiring the lock.
            while self.local_len() <= desired_item_idx and self._has_next_page():
                last_fetched_page = (
                    -1 if isinstance(self._result_info, SpecialResultInfoState) else self._result_info.page
                )

                first_known_item = None
                last_known_item = None

                if self._pages:
                    if first_items := self._pages[0].items:
                        first_known_item = first_items[0]
                    if last_items := self._pages[-1].items:
                        last_known_item = last_items[-1]

                call_arg = types.FetchPageCallArg(
                    first_known_item=first_known_item,
                    last_known_item=last_known_item,
                    last_fetched_page=last_fetched_page,
                    current_total_list_len=self.local_len(),
                )

                try:
                    (new_page_info, new_items) = await self._fetch_page_cb(call_arg)
                except (httpx.RequestError, exc.CompaniesHouseApiError) as e:
                    logger.exception(f"Failed to fetch page {last_fetched_page + 1}: {e}")
                    self._result_info = (
                        SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED
                        if last_fetched_page == -1
                        else SpecialResultInfoState.PAGE_FETCH_FAILED
                    )
                    return None

                self._max_fetched_page = last_fetched_page + 1
                self._pages.append(FetchedPageData(items=tuple(new_items), page_info=new_page_info))

                if new_page_info is None:
                    self._result_info = (
                        SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED
                        if last_fetched_page == -1
                        else SpecialResultInfoState.ALL_PAGES_FETCHED
                    )
                else:
                    assert new_page_info.page == last_fetched_page + 1, (
                        new_page_info.page,
                        last_fetched_page + 1,
                    )
                    self._result_info = new_page_info
        return new_page_info

    async def __getitem__(self, index: int) -> T:
        """Get an item by its index, fetching pages as necessary.

        Please note: negative indices are not supported.
        """
        if index < 0:
            raise IndexError("Negative indices are not supported.")
        await self._fetch_page_to_item_idx(index)
        return self.local_items()[index]

    async def __aiter__(self) -> typing.AsyncIterator[T]:
        cur_page_idx = 0
        while len(self._pages) > cur_page_idx:
            page = self._pages[cur_page_idx]
            for item in page.items:
                yield item
            cur_page_idx += 1
            if len(self._pages) <= cur_page_idx:
                # need to fetch next page
                if self._has_next_page():
                    await self._fetch_page_to_item_idx(self.local_len() + 1)
                else:
                    # no more pages
                    break

    def local_items(self) -> typing.Tuple[T, ...]:
        """Return the items that have been locally cached without making API calls.

        Returns:
            A tuple of locally cached items.
        """
        items = []
        for page in self._pages:
            items.extend(page.items)
        return tuple(items)

    def local_len(self) -> int:
        """Return the number of items that have been locally cached without making API calls.

        Returns:
            The number of locally cached items.
        """
        return sum(len(page.items) for page in self._pages)

    def local_pages(self) -> typing.Tuple[tuple[T, ...], ...]:
        """Return the pages that have been locally cached without making API calls.

        Returns:
            A tuple of locally cached pages, each page is a tuple of items.
        """
        return tuple(tuple(page.items) for page in self._pages)

    @property
    def is_fully_fetched(self) -> bool:
        """Check if all pages have been fetched from the API.

        Returns:
            True if all pages have been fetched and cached locally, False otherwise.

        Example:
            Check before performing operations that require all data::

                results = await client.search_companies("Apple")
                if not results.is_fully_fetched:
                    await results.fetch_all_pages()

                # Now safe to perform bulk operations
                for company in results.local_items():
                    process(company)
        """
        return not self._has_next_page()

    def __len__(self) -> int:
        """Return the total number of items reported by the API.

        When not all pages have been fetched this uses the ``total_count``
        value from the pagination metadata returned by the Companies House API, so it
        should be treated as an estimate. In rare cases where the backend
        metadata is inconsistent it is still possible to receive an
        ``IndexError`` when accessing an index that is less than this length.
        """
        if self._has_next_page():
            # while the list was not fully fetched,
            # return an estimate based on the total_count from result_info
            if isinstance(self._result_info, types.PaginatedResultInfo):
                if self._result_info.total_count is None:
                    raise ValueError("Cannot determine length: total_count is not available in result_info.")
                out = self._result_info.total_count
            else:
                raise ValueError("Cannot determine length: first page not yet fetched.")
        else:
            out = self.local_len()
        return out

    def __repr__(self) -> str:
        return f"MultipageList({self._pages})"

    def model_dump(self, mode: typing.Literal["json", "python"] = "json") -> typing.List[typing.Dict[str, typing.Any]]:
        """Dump the items in the list to a list of dictionaries.

        Returns:
            A list of dictionaries representing the items.
        """
        return [item.model_dump(mode=mode) for item in self.local_items()]

    async def get_all(self) -> typing.Tuple[T, ...]:
        """Fetch all pages and return all items as a list.

        Returns:
            A list of all items.
        """
        await self.fetch_all_pages()
        return self.local_items()

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: typing.Any,
        handler: pydantic.GetJsonSchemaHandler,
    ) -> pydantic_core.CoreSchema:
        """Get the Pydantic core schema for MultipageList.

        This schema defines how MultipageList instances are serialized to JSON
        and deserialized from JSON. The list is treated as a list[T] from
        Pydantic's perspective.

        Args:
            source_type: The source type being validated (MultipageList[T]).
            handler: The handler for getting schemas of other types.

        Returns:
            A Pydantic CoreSchema that describes how to handle MultipageList.
        """
        # Extract the type argument T from MultipageList[T]
        if hasattr(source_type, "__args__") and source_type.__args__:
            item_type = source_type.__args__[0]
        else:
            item_type = typing.Any

        # Get the schema for list[T] for serialization
        list_schema = handler(list[item_type])

        # Return a schema that accepts MultipageList instances directly
        # and serializes them as lists
        return pydantic_core.core_schema.is_instance_schema(
            cls,
            serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
                lambda v: list(v.local_items()),
                info_arg=False,
                return_schema=list_schema,
            ),
        )
