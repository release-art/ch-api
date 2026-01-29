import typing

import pydantic

from ch_api.types.public_data import (
    search_companies as base_search_companies,
)

from . import pagination, top_hit


class AdvancedSearchResult(
    top_hit.TopHitList[
        base_search_companies.AdvancedSearchResult[pagination.ITEM_T],
        pagination.ITEM_T,
    ]
):
    """Advanced search results with customised links section."""

    hits: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of matches found using advanced search",
            default=0,
        ),
    ]
