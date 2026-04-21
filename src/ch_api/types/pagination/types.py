"""Pagination types for Companies House API responses.

Public types (fca-api compatible):
    NextPageToken: Opaque string cursor passed between calls to page through results.
    PageTokenSerializer: Protocol for encrypting/decrypting pagination tokens.
    PaginationInfo: Pagination metadata returned alongside each page of results.
    MultipageList: Generic value object containing one page of results.

Internal types (not part of the public API):
    _PageState: Encodes CH API pagination state (start_index / search_below cursor).
"""

import dataclasses
import json
import typing

import pydantic

_ItemT = typing.TypeVar("_ItemT")


# ---------------------------------------------------------------------------
# Internal: page state codec
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _PageState:
    """Encodes CH API pagination state as a portable JSON string.

    Not part of the public API — callers only ever see ``NextPageToken`` (str).

    For offset-based endpoints (most CH API endpoints), ``start_index`` stores
    the next offset to request. For cursor-based endpoints (alphabetical
    search), ``search_below`` stores the ordered_alpha_key_with_id cursor.
    """

    start_index: int = 0
    search_below: typing.Optional[str] = None

    def encode(self) -> str:
        data: dict[str, typing.Any] = {"start_index": self.start_index}
        if self.search_below is not None:
            data["search_below"] = self.search_below
        return json.dumps(data)

    @classmethod
    def decode(cls, token: str) -> "_PageState":
        data = json.loads(token)
        return cls(
            start_index=data.get("start_index", 0),
            search_below=data.get("search_below"),
        )

    @classmethod
    def first(cls) -> "_PageState":
        return cls(start_index=0)


# ---------------------------------------------------------------------------
# Public: pagination token type
# ---------------------------------------------------------------------------

NextPageToken = typing.Annotated[
    str,
    pydantic.Field(
        description=(
            "Opaque pagination cursor. Pass this value unchanged to the same endpoint "
            "to retrieve the next page of results. Treat it as an opaque string — "
            "do not construct, parse, or modify it."
        )
    ),
]
"""An opaque string cursor for retrieving the next page of results.

Returned in ``PaginationInfo.next_page`` when more results exist. Pass it
back to the same endpoint method (as the ``next_page`` argument) to fetch
the next batch.

The internal format is an implementation detail and may change. Always treat
this value as opaque.
"""


# ---------------------------------------------------------------------------
# Public: token serializer protocol
# ---------------------------------------------------------------------------


@typing.runtime_checkable
class PageTokenSerializer(typing.Protocol):
    """Protocol for encrypting and decrypting pagination tokens.

    Implement this interface to protect ``next_page`` tokens from tampering
    or inspection when they leave the service boundary (e.g. returned to API
    callers and submitted back on a subsequent request).

    Pass an instance to ``Client`` at construction time::

        class HmacSerializer:
            def serialize(self, token: str) -> str:
                # sign / encrypt the raw token
                ...

            def deserialize(self, token: str) -> str:
                # verify / decrypt back to the raw token
                ...

        client = Client(
            credentials=auth,
            page_token_serializer=HmacSerializer(),
        )

    When a serializer is configured:

    * Tokens returned by endpoint methods are passed through ``serialize``
      before being placed in ``PaginationInfo.next_page``.
    * Tokens received by endpoint methods are passed through ``deserialize``
      before being decoded internally.
    """

    def serialize(self, token: str) -> str:
        """Transform a raw pagination token for external use (e.g. encrypt or sign)."""
        ...

    def deserialize(self, token: str) -> str:
        """Recover the raw pagination token from an external value (e.g. decrypt or verify)."""
        ...


# ---------------------------------------------------------------------------
# Public: pagination metadata model
# ---------------------------------------------------------------------------


class PaginationInfo(pydantic.BaseModel):
    """Pagination state for a result set returned by the CH API.

    Returned alongside every page of results from the async client. Use
    ``next_page`` in a subsequent call to the same endpoint to retrieve
    the next batch of items.

    Example::

        page = await client.search_companies("Apple", result_count=25)

        while page.pagination.has_next:
            page = await client.search_companies(
                "Apple",
                next_page=page.pagination.next_page,
                result_count=25,
            )
    """

    model_config = pydantic.ConfigDict(frozen=True)

    has_next: bool = pydantic.Field(description="True if more results are available beyond this page.")
    next_page: typing.Optional[NextPageToken] = pydantic.Field(
        default=None,
        description="Cursor to pass to the same endpoint to fetch the next page. None when has_next is False.",
    )
    size: typing.Optional[int] = pydantic.Field(
        default=None,
        description=(
            "Estimated total number of items in the collection as reported by the CH API. May be approximate."
        ),
    )


# ---------------------------------------------------------------------------
# Public: result page model
# ---------------------------------------------------------------------------


class MultipageList(pydantic.BaseModel, typing.Generic[_ItemT]):
    """A page of typed results from a paginated CH API endpoint.

    Contains the fetched data items and the pagination metadata needed to
    retrieve subsequent pages. Returned by all paginated methods on
    ``Client``.

    Type Parameters:
        _ItemT: The type of items in ``data``.

    Fetching pages::

        # First page
        page = await client.search_companies("Apple")
        print(f"Got {len(page.data)} of ~{page.pagination.size} total results")

        # Subsequent pages
        while page.pagination.has_next:
            page = await client.search_companies(
                "Apple",
                next_page=page.pagination.next_page,
                result_count=25,
            )
            # process page.data ...

    Fetching a larger batch in one call::

        # Request at least 100 items (may trigger multiple underlying API calls)
        page = await client.search_companies("Apple", result_count=100)
        # page.data has >= 100 items (or all available if fewer exist)
    """

    model_config = pydantic.ConfigDict(frozen=True, arbitrary_types_allowed=True)

    data: typing.List[_ItemT] = pydantic.Field(description="The result items for this page.")
    pagination: PaginationInfo = pydantic.Field(
        description="Pagination state, including whether more results exist and how to fetch them."
    )
