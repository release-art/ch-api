import typing

import pydantic

from ch_api.types import shared
from ch_api.types.public_data import (
    psc as base_psc,
)

from . import pagination


class OfficerAppointments(pagination.PaginatedEntity[base_psc.PSCList, base_psc.ListSummary]):
    """Officer appointments with customised links section."""

    active_count: typing.Annotated[
        int,
        pydantic.Field(description="The number of active persons with significant control in this result set."),
    ]

    ceased_count: typing.Annotated[
        int,
        pydantic.Field(description="The number of ceased persons with significant control in this result set."),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]


class StatementList(pagination.PaginatedEntity[base_psc.StatementList, base_psc.Statement]):
    """Officer appointments with customised links section."""

    active_count: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of active persons with significant control in this result set.",
            default=0,
        ),
    ]

    ceased_count: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of ceased persons with significant control in this result set.",
            default=0,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(description="A set of URLs related to the resource, including self.", default=None),
    ]
