import typing

import pydantic

from ch_api.types import shared
from ch_api.types.public_data import (
    officer_appointments as base_officer_appointments,
)

from . import pagination


class OfficerAppointments(
    pagination.PaginatedEntity[
        base_officer_appointments.AppointmentList, base_officer_appointments.OfficerAppointmentSummary
    ]
):
    """Officer appointments with customised links section."""

    kind: typing.Annotated[
        str,
        pydantic.Field(
            description="The resource type.",
        ),
    ]

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The ETag of the resource.",
        ),
    ]

    is_corporate_officer: typing.Annotated[
        bool,
        pydantic.Field(
            description="Indicator representing if the officer is a corporate body.",
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="Links to other resources associated with this officer appointment resource.",
        ),
    ]

    name: typing.Annotated[
        str,
        pydantic.Field(
            description="The corporate or natural officer name.",
        ),
    ]

    date_of_birth: typing.Annotated[
        base_officer_appointments.DateOfBirth | None,
        pydantic.Field(
            description="The officer's date of birth details.",
            default=None,
        ),
    ]
