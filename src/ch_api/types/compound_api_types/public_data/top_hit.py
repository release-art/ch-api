"""A common API pattern is having a lazy list with the `top hit` field."""

import typing

import pydantic

from . import pagination


class TopHitList(
    pagination.PaginatedEntity[
        pagination.CONTAINER_T,
        pagination.ITEM_T,
    ]
):
    """Advanced search results with customised links section."""

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The ETag of the resource",
            default=None,
        ),
    ]

    kind: typing.Annotated[
        str,
        pydantic.Field(
            description="The type of response returned.",
            default="__uninitialised__",
        ),
    ]

    top_hit: typing.Annotated[
        pagination.ITEM_T | None,
        pydantic.Field(
            description="The best matching item in the search results",
            default=None,
        ),
    ]
