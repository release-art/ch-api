"""Detailed officer appointment models for Companies House API.

This module contains Pydantic models for the officer appointments endpoint,
which provides detailed information about individual officer appointments.

API Endpoints
-----
GET /officers/{officer_id}/appointments - List officer appointments
GET /company/{company_number}/appointments/{appointment_id} - Get appointment details

Officer Appointments
-----
Officer appointments provide detailed information about each time an officer
was appointed to a company role. Each appointment record includes:
- Appointment date
- Resignation date (if applicable)
- Officer name and details
- Appointment role/capacity
- Director/Secretary/LLP member status
- Service address
- Nationality
- Date of birth (if public)
- Occupation
- Responsible periods
- Links to detailed records

Appointment History
-----
By querying the officer appointments endpoint, you can see all appointments
for a specific officer across different companies and time periods.

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/officerAppointmentList.json

Models in this Module
-----
- :class:`AppointmentList` - Paginated list of appointments
- :class:`Appointment` - Individual appointment record
- And other supporting models

Example Usage
-----
Fetch appointments for an officer::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    appointments = await client.get_officer_appointments("officer_id")
    for appointment in appointments.items or []:
        print(f"Company: {appointment.company_name}")
        print(f"Role: {appointment.appointed_to}")

See Also
--------
ch_api.Client.get_officer_appointments : Fetch officer appointments
ch_api.types.public_data.company_officers : Officer summary information
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared


class Address(base.BaseModel):
    """Address information."""

    address_line_1: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The first line of the address.",
            default=None,
        ),
    ]

    address_line_2: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The second line of the address.",
            default=None,
        ),
    ]

    care_of: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The care of name.",
            default=None,
        ),
    ]

    premises: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The property name or number.",
            default=None,
        ),
    ]

    locality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The locality. For example London.",
            default=None,
        ),
    ]

    region: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The region. For example Surrey.",
            default=None,
        ),
    ]

    po_box: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The post-office box number.",
            default=None,
        ),
    ]

    postal_code: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The postal code. For example CF14 3UZ.",
            default=None,
        ),
    ]

    country: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country. For example, UK.",
            default=None,
        ),
    ]


class DateOfBirth(base.BaseModel):
    """Officer's date of birth details."""

    month: typing.Annotated[
        int,
        pydantic.Field(
            description="The month the officer was born in.",
        ),
    ]

    year: typing.Annotated[
        int,
        pydantic.Field(
            description="The year the officer was born in.",
        ),
    ]


class FormerNames(base.BaseModel):
    """Former names for the officer."""

    forenames: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Former forenames of the officer.",
            default=None,
        ),
    ]

    surname: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Former surnames of the officer.",
            default=None,
        ),
    ]


class NameElements(base.BaseModel):
    """Separate elements of a natural officer's name."""

    surname: typing.Annotated[
        str,
        pydantic.Field(
            description="The surname of the officer.",
        ),
    ]

    forename: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The forename of the officer.",
            default=None,
        ),
    ]

    other_forenames: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Other forenames of the officer.",
            default=None,
        ),
    ]

    title: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Title of the officer.",
            default=None,
        ),
    ]

    honours: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Honours an officer might have.",
            default=None,
        ),
    ]


class CorporateIdent(base.BaseModel):
    """Corporate officer identification information."""

    identification_type: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "eea",
            "non-eea",
            "uk-limited-company",
            "other-corporate-body-or-firm",
            "registered-overseas-entity-corporate-managing-officer",
        ),
        pydantic.Field(
            description="The officer's identity type",
            default=None,
        ),
    ]

    legal_authority: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The legal authority supervising the company.",
            default=None,
        ),
    ]

    legal_form: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The legal form of the company as defined by its country of registration.",
            default=None,
        ),
    ]

    place_registered: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Place registered.",
            default=None,
        ),
    ]

    registration_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Company registration number.",
            default=None,
        ),
    ]


class AppointedTo(base.BaseModel):
    """The company information of the appointment."""

    company_number: typing.Annotated[
        str,
        pydantic.Field(
            description="The number of the company the officer is acting for.",
        ),
    ]

    company_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The name of the company the officer is acting for.",
            default=None,
        ),
    ]

    company_status: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The status of the company the officer is acting for.",
            default=None,
        ),
    ]


class ContactDetails(base.BaseModel):
    """Contact details for corporate managing officer."""

    contact_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The name of the contact.",
            default=None,
        ),
    ]


class OfficerAppointmentSummary(base.BaseModel):
    """Officer appointment summary."""

    name: typing.Annotated[
        str,
        pydantic.Field(
            description="The full name of the officer.",
        ),
    ]

    officer_role: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "cic-manager",
            "corporate-director",
            "corporate-llp-designated-member",
            "corporate-llp-member",
            "corporate-managing-officer",
            "corporate-member-of-a-management-organ",
            "corporate-member-of-a-supervisory-organ",
            "corporate-member-of-an-administrative-organ",
            "corporate-nominee-director",
            "corporate-nominee-secretary",
            "corporate-secretary",
            "director",
            "judicial-factor",
            "llp-designated-member",
            "llp-member",
            "managing-officer",
            "member-of-a-management-organ",
            "member-of-a-supervisory-organ",
            "member-of-an-administrative-organ",
            "nominee-director",
            "nominee-secretary",
            "receiver-and-manager",
            "secretary",
        ),
        pydantic.Field(
            description="The officer role.",
        ),
    ]

    appointed_to: typing.Annotated[
        AppointedTo,
        pydantic.Field(
            description="The company information of the appointment.",
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="Links to other resources associated with this officer appointment item.",
        ),
    ]

    address: typing.Annotated[
        Address | None,
        pydantic.Field(
            description="The correspondence address of the officer.",
            default=None,
        ),
    ]

    appointed_before: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date the officer was appointed before. "
                "Only present when the `is_pre_1992_appointment` attribute is `true`."
            ),
            default=None,
        ),
    ]

    appointed_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date on which the officer was appointed. "
                "For the officer roles of `corporate-managing-officer` and `managing-officer` "
                "this is the date on which Companies House was notified about the officer."
            ),
            default=None,
        ),
    ]

    contact_details: typing.Annotated[
        ContactDetails | None,
        pydantic.Field(
            description="The contact at the `corporate-managing-officer` of a `registered-overseas-entity`.",
            default=None,
        ),
    ]

    country_of_residence: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The officer's country of residence.",
            default=None,
        ),
    ]

    former_names: typing.Annotated[
        list[FormerNames] | None,
        pydantic.Field(
            description="Former names for the officer, if there are any.",
            default=None,
        ),
    ]

    identification: typing.Annotated[
        CorporateIdent | None,
        pydantic.Field(
            description=(
                "Only one from `eea`, `non-eea`, `uk-limited-company`, "
                "`other-corporate-body-or-firm` or `registered-overseas-entity-corporate-managing-officer` "
                "can be supplied, not multiples of them."
            ),
            default=None,
        ),
    ]

    is_pre_1992_appointment: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Indicator representing if the officer was appointed before their appointment date.",
            default=None,
        ),
    ]

    name_elements: typing.Annotated[
        NameElements | None,
        pydantic.Field(
            description="A document encapsulating the separate elements of a natural officer's name.",
            default=None,
        ),
    ]

    nationality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The officer's nationality.",
            default=None,
        ),
    ]

    occupation: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The officer's occupation.",
            default=None,
        ),
    ]

    principal_office_address: typing.Annotated[
        Address | None,
        pydantic.Field(
            description=(
                "The principal/registered office address of a "
                "`corporate-managing-officer` of a `registered-overseas-entity`."
            ),
            default=None,
        ),
    ]

    resigned_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date the officer was resigned. "
                "For the officer roles of `corporate-managing-officer` and `managing-officer` "
                "this is the date on which Companies House was notified about the officers cessation."
            ),
            default=None,
        ),
    ]

    responsibilities: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The responsibilities of the managing officer of a `registered-overseas-entity`.",
            default=None,
        ),
    ]


class AppointmentList(base.BaseModel):
    """Officer appointment list."""

    kind: typing.Annotated[
        typing.Literal["personal-appointment"],
        pydantic.Field(
            description="The resource type.",
        ),
    ]

    etag: typing.Annotated[
        str,
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

    items: typing.Annotated[
        list[OfficerAppointmentSummary],
        pydantic.Field(
            description="The list of officer appointments.",
        ),
    ]

    items_per_page: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of officer appointments to return per page.",
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

    start_index: typing.Annotated[
        int,
        pydantic.Field(
            description=(
                "The first row of data to retrieve, starting at 0. "
                "Use this parameter as a pagination mechanism along with the `items_per_page` parameter."
            ),
        ),
    ]

    total_results: typing.Annotated[
        int,
        pydantic.Field(
            description="The total number of officer appointments in this result set.",
        ),
    ]

    date_of_birth: typing.Annotated[
        DateOfBirth | None,
        pydantic.Field(
            description="The officer's date of birth details.",
            default=None,
        ),
    ]
