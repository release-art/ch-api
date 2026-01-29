"""Officer changes and links models for Companies House API.

This module contains Pydantic models for officer changes information,
including details about how officers are linked to companies and changes over time.

API Endpoint Context
-----
This module supports officer-related endpoints and provides models for
detailed officer-related fields and history.

Officer Changes
-----
Officer changes include:
- Appointments to new positions
- Resignations from positions
- Changes in officer details (address, occupation, etc.)
- Updates to service addresses
- Changes in director/secretary status

Change Information
-----
Each change record typically includes:
- Date of change
- Type of change (appointment, resignation, update)
- Officer details
- Company information
- Effective date of change

Documentation
-----
Full API documentation context:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/companyOfficerList.json

Models in this Module
-----
- :class:`Officer` - Officer details with change history
- :class:`OfficerLinks` - Links to officer resources
- And other supporting models

See Also
--------
ch_api.Client.get_officer_list : Fetch current officers
ch_api.types.public_data.company_officers : Current officer information
ch_api.types.public_data.officer_appointments : Detailed appointments
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared


class Address(base.BaseModel):
    """Address information for an officer."""

    address_line_1: typing.Annotated[
        str,
        pydantic.Field(
            description="The first line of the address.",
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

    country: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country e.g. United Kingdom.",
            default=None,
        ),
    ]

    locality: typing.Annotated[
        str,
        pydantic.Field(
            description="The locality e.g. London.",
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
            description="The postal code e.g. CF14 3UZ.",
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

    region: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The region e.g. Surrey.",
            default=None,
        ),
    ]


class DateOfBirth(base.BaseModel):
    """Date of birth information for an officer."""

    day: typing.Annotated[
        int | None,
        pydantic.Field(
            description="The day of the date of birth.",
            default=None,
        ),
    ]

    month: typing.Annotated[
        int,
        pydantic.Field(
            description="The month of date of birth.",
        ),
    ]

    year: typing.Annotated[
        int,
        pydantic.Field(
            description="The year of date of birth.",
        ),
    ]


class FormerNames(base.BaseModel):
    """Former names for an officer."""

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


class CorporateIdent(base.BaseModel):
    """Corporate identification information for an officer."""

    identification_type: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "eea",
            "non-eea",
            "uk-limited",
            "other-corporate-body-or-firm",
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


class IdentityVerificationDetails(base.BaseModel):
    """Information relating to the identity verification of the officer."""

    anti_money_laundering_supervisory_bodies: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description=(
                "The Anti-Money Laundering supervisory bodies that the authorised "
                "corporate service provider was registered with when verifying the officer."
            ),
            default=None,
        ),
    ]

    appointment_verification_end_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date on which the identity verification statement was removed for the appointment.",
            default=None,
        ),
    ]

    appointment_verification_statement_due_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date by which an identity verification statement must be supplied for the appointment.",
            default=None,
        ),
    ]

    appointment_verification_start_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date on which the identity verification statement was supplied for the appointment.",
            default=None,
        ),
    ]

    authorised_corporate_service_provider_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The name of the authorised corporate service provider that verified the identity of the officer."
            ),
            default=None,
        ),
    ]

    identity_verified_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date on which the authorised corporate service provider verified the identity of the officer."
            ),
            default=None,
        ),
    ]

    preferred_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The name provided to the authorised corporate service "
                "provider by which the officer prefers to be known."
            ),
            default=None,
        ),
    ]


class OfficerChange(base.BaseModel):
    """Officer change request for Companies House."""

    etag: typing.Annotated[
        str,
        pydantic.Field(
            description="The ETag of the resource.",
            json_schema_extra={"readOnly": True},
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["officer-change#officer-change"],
        pydantic.Field(
            description="The type of resource.",
            json_schema_extra={"readOnly": True},
        ),
    ]

    reference_appointment_id: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "Required for officer change and termination. The id of the current company officer "
                "appointment resource being changed or terminated "
                "(`/company/{company_number}/appointments/{officer_appointment_id}`) on the public register."
            ),
            default=None,
        ),
    ]

    reference_etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The latest etag read from the current company officer appointment resource "
                "(`/company/{company_number}/officer/{officer_id}`) on the public register. "
                "If this reference etag does not match the current register the request will be rejected."
            ),
            default=None,
        ),
    ]

    address: typing.Annotated[
        Address | None,
        pydantic.Field(
            description="The correspondence address of the officer. Required for officer appointment.",
            default=None,
        ),
    ]

    appointed_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date on which the officer was appointed. Required for officer appointment.",
            default=None,
        ),
    ]

    country_of_residence: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The officer's country of residence. Required for officer appointment.",
            default=None,
        ),
    ]

    date_of_birth: typing.Annotated[
        DateOfBirth | None,
        pydantic.Field(
            description="Details of director date of birth. Required for officer appointment.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="Links to other resources associated with this officer change resource.",
        ),
    ]

    name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Corporate or natural officer name. Required for officer appointment.",
            default=None,
        ),
    ]

    nationality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The officer's nationality. Required for officer appointment.",
            default=None,
        ),
    ]

    occupation: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The officer's job title. Required for officer appointment.",
            default=None,
        ),
    ]

    officer_role: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "cic-manager",
            "corporate-director",
            "corporate-llp-designated-member",
            "corporate-llp-member",
            "corporate-manager-of-an-eeig",
            "corporate-member-of-a-management-organ",
            "corporate-member-of-a-supervisory-organ",
            "corporate-member-of-an-administrative-organ",
            "corporate-nominee-director",
            "corporate-nominee-secretary",
            "corporate-secretary",
            "director",
            "general-partner-in-a-limited-partnership",
            "judicial-factor",
            "limited-partner-in-a-limited-partnership",
            "llp-designated-member",
            "llp-member",
            "manager-of-an-eeig",
            "member-of-a-management-organ",
            "member-of-a-supervisory-organ",
            "member-of-an-administrative-organ",
            "nominee-director",
            "nominee-secretary",
            "person-authorised-to-accept",
            "person-authorised-to-represent",
            "person-authorised-to-represent-and-accept",
            "receiver-and-manager",
            "secretary",
        ),
        pydantic.Field(
            description="The officer's role. Required for officer appointment.",
            default=None,
        ),
    ]

    resigned_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date on which the officer resigned.",
            default=None,
        ),
    ]

    former_names: typing.Annotated[
        list[FormerNames] | None,
        pydantic.Field(
            description="Former names for the officer.",
            default=None,
        ),
    ]

    identification: typing.Annotated[
        CorporateIdent | None,
        pydantic.Field(
            description=(
                "Only one from `eea`, `non-eea`, `uk-limited` or `other-corporate-body-or-firm` "
                "can be supplied, not multiples of them. Required for officer appointment."
            ),
            default=None,
        ),
    ]

    identity_verification_details: typing.Annotated[
        IdentityVerificationDetails | None,
        pydantic.Field(
            description="Information relating to the identity verification of the officer",
            default=None,
        ),
    ]
