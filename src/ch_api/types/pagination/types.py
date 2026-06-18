"""Pagination types for Companies House API responses.

Public types (fca-api compatible):
    NextPageToken: Opaque string cursor passed between calls to page through results.
    PageTokenSerializer: Protocol for encrypting/decrypting pagination tokens.
    PaginationInfo: Pagination metadata returned alongside each page of results.
    MultipageList: Generic value object holding one batch of results plus a get_next handle.

Internal types (not part of the public API):
    _PageState: Self-contained, restartable pagination cursor (the encoded NextPageToken).
"""

import typing

import pydantic

from ... import exc

_ItemT = typing.TypeVar("_ItemT", bound=pydantic.BaseModel)


# ---------------------------------------------------------------------------
# Internal: page state codec
# ---------------------------------------------------------------------------


class _PageState(pydantic.BaseModel, frozen=True):
    """A self-contained, restartable pagination cursor, encoded as the JSON ``NextPageToken``.

    Internal — callers only ever see the opaque ``NextPageToken`` (str). Holds
    everything needed to resume from a fresh process:

    * ``endpoint`` / ``params`` — the ``Client`` method and its arguments to
      re-dispatch (params are JSON-safe values).
    * ``start_index`` — next offset for offset-based endpoints.
    * ``search_below`` — cursor for cursor-based endpoints (alphabetical / dissolved).

    The ``@paginated`` decorator also publishes a position-less instance (just
    ``endpoint`` / ``params``) as the active call's resume context; the fetch
    helpers read it and fill in the position when stamping the next token.
    """

    start_index: int = 0
    search_below: typing.Optional[str] = None
    endpoint: str = ""
    params: typing.Dict[str, typing.Any] = pydantic.Field(default_factory=dict)

    def encode(self) -> str:
        return self.model_dump_json()

    @classmethod
    def decode(cls, token: str) -> "_PageState":
        return cls.model_validate_json(token)

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
            "Opaque pagination cursor. Pass this value unchanged to "
            "``Client.fetch_next_page`` to retrieve the next page of results. Treat "
            "it as an opaque string — do not construct, parse, or modify it."
        )
    ),
]
"""An opaque string cursor for retrieving the next page of results.

Returned in ``PaginationInfo.next_page`` when more results exist. Pass it to
``Client.fetch_next_page`` to fetch the next batch (or call
``MultipageList.get_next``, which does this for you).

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
    ``MultipageList.get_next`` (or pass ``next_page`` to
    ``Client.fetch_next_page``) to retrieve the next page of items.

    Example::

        page = await client.search_companies("Apple")

        while page.pagination.has_next:
            page = await page.get_next()
    """

    model_config = pydantic.ConfigDict(frozen=True)

    has_next: bool = pydantic.Field(description="True if more results are available beyond this page.")
    next_page: typing.Optional[NextPageToken] = pydantic.Field(
        default=None,
        description="Cursor to pass to Client.fetch_next_page to fetch the next page. None when has_next is False.",
    )
    size: typing.Optional[int] = pydantic.Field(
        default=None,
        description=(
            "Estimated total number of items in the collection as reported by the CH API. May be approximate."
        ),
    )


# ---------------------------------------------------------------------------
# Internal: client handle used by MultipageList.get_next
# ---------------------------------------------------------------------------


@typing.runtime_checkable
class _NextPageFetcher(typing.Protocol):
    """Minimal client interface :meth:`MultipageList.get_next` needs (``Client`` satisfies it)."""

    async def fetch_next_page(self, next_page: str) -> typing.Any: ...


# ---------------------------------------------------------------------------
# Public: result page model
# ---------------------------------------------------------------------------


class MultipageList(pydantic.BaseModel, typing.Generic[_ItemT]):
    """A batch of typed results from a paginated CH API endpoint.

    Holds the items from one client call — at least ``result_count``, or all
    remaining if fewer — plus pagination metadata. A plain value object: advance
    with :meth:`get_next` (or pass ``pagination.next_page`` to
    :meth:`Client.fetch_next_page`); it does not fetch lazily or merge batches.

    Type Parameters:
        _ItemT: The type of items in ``data``.

    Walking the whole result set with ``get_next``::

        page = await client.search_companies("Apple")
        while True:
            for company in page.data:
                ...  # process this batch's items
            if not page.pagination.has_next:
                break
            page = await page.get_next()

    Fetching a larger batch in one call::

        # Collect at least 100 items (may issue several underlying requests)
        page = await client.search_companies("Apple", result_count=100)
        # page.data has >= 100 items (or all available if fewer exist)

    Resuming statelessly from a self-contained token (e.g. a fresh request in an
    async server or agent tool — only the token is needed, not the query)::

        page = await client.search_companies("Apple")
        token = page.pagination.next_page  # opaque, restartable cursor

        # ... later, in a new process with only `token` ...
        page2 = await client.fetch_next_page(token)
    """

    model_config = pydantic.ConfigDict(frozen=True, arbitrary_types_allowed=True)

    data: typing.List[_ItemT] = pydantic.Field(description="The result items for this page.")
    pagination: PaginationInfo = pydantic.Field(
        description="Pagination state, including whether more results exist and how to fetch them."
    )

    _client: typing.Optional[_NextPageFetcher] = pydantic.PrivateAttr(default=None)
    """Client used by :meth:`get_next`. Set when the list is produced; ``None`` on
    deserialized instances (resume those via ``Client.fetch_next_page(token)``)."""

    async def get_next(self) -> "MultipageList[_ItemT]":
        """Fetch the next batch via :meth:`Client.fetch_next_page` and this list's token.

        Raises:
            NoMorePagesError: If ``pagination.has_next`` is ``False``.
            RuntimeError: If no client is bound (e.g. a deserialized list); resume
                with ``client.fetch_next_page(pagination.next_page)`` instead.
        """
        if not self.pagination.has_next:
            raise exc.NoMorePagesError("This is the last page; no more results to fetch.")
        if self._client is None or self.pagination.next_page is None:
            raise RuntimeError(
                "MultipageList has no client bound — it was likely constructed manually "
                "or deserialized. Resume with `client.fetch_next_page(pagination.next_page)`."
            )
        return await self._client.fetch_next_page(self.pagination.next_page)
