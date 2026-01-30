"""Company officers and director information models for Companies House API.

This module contains Pydantic models for the company officers endpoint, which
provides information about directors, secretaries, and other officers managing
UK limited companies.

API Endpoint
-----
GET /company/{company_number}/officers

Returns a paginated list of officers for the specified company.

Officer Types
-----
The API returns different types of company officers:
- Directors - Board members of the company
- Secretaries - Company secretaries
- LLP Members - Members of Limited Liability Partnerships

Officer Information
-----
Each officer record includes:
- Full name and name elements (forename, surname, honours)
- Appointment and resignation dates
- Service address
- Nationality
- Date of birth (if public)
- Occupation
- Links to detailed appointment records

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/companyOfficerList.json

Models in this Module
-----
- :class:`OfficerSummary` - Summary information about an officer
- :class:`ItemLinkTypes` - Links to officer resources
- :class:`OfficerAppointmentDates` - Appointment and resignation dates
- And other supporting officer models

Example Usage
-----
Fetch officers for a company::

    >>> from ch_api import Client, api_settings
    >>> auth = api_settings.AuthSettings(api_key="your-key")
    >>> client = Client(credentials=auth)
    ...
    >>> officers = await client.get_officer_list("09370755")
    >>> async for officer in officers:
    ...     print(f"{officer.name} - Appointed: {officer.appointed_on}")
    ...

Filter by Officer Type
-----
Optionally filter by officer type::

    directors = await client.get_officer_list(
        "09370755",
        only_type="directors"
    )

See Also
--------
ch_api.Client.get_officer_list : Fetch officers for a company
ch_api.types.public_data.officer_changes : Historical officer changes
ch_api.types.public_data.officer_appointments : Detailed appointment records
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared
from . import officer_changes


class ItemLinkTypes(base.BaseModel):
    """Links to other resources associated with this officer list item."""

    self: typing.Annotated[
        str,
        pydantic.Field(
            description="Link to this individual company officer appointment resource.",
        ),
    ]

    officer: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="Links to other officer resources associated with this officer list item.",
        ),
    ]


class Address(base.BaseModel):
    """Address information for an officer."""

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

    country: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country e.g. United Kingdom.",
            default=None,
        ),
    ]

    locality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The locality e.g. London.",
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


class PrincipalOfficeAddress(base.BaseModel):
    """Principal office address of a corporate managing officer."""

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

    country: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country e.g. United Kingdom.",
            default=None,
        ),
    ]

    locality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The locality e.g. London.",
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


class ContactDetails(base.BaseModel):
    """Contact details for a corporate managing officer."""

    contact_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The name of the contact.",
            default=None,
        ),
    ]


class DateOfBirth(base.BaseModel):
    """Date of birth information for an officer."""

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


class OfficerSummary(base.BaseModel):
    """Summary information for an individual officer appointment."""

    address: typing.Annotated[
        Address | None,
        pydantic.Field(
            description="The correspondence address of the officer.",
            default=None,
        ),
    ]

    appointed_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date on which the officer was appointed. For the officer roles of "
                "`corporate-managing-officer` and `managing-officer` this is the date on which "
                "Companies House was notified about the officer."
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

    date_of_birth: typing.Annotated[
        DateOfBirth | None,
        pydantic.Field(
            description="Details of director date of birth.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        ItemLinkTypes,
        pydantic.Field(
            description="Links to other resources associated with this officer list item.",
        ),
    ]

    name: typing.Annotated[
        str,
        pydantic.Field(
            description="Corporate or natural officer name.",
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
            description="The officer's job title.",
            default=None,
        ),
    ]

    officer_role: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "cic-manager",
            "corporate-director",
            "corporate-llp-designated-member",
            "corporate-llp-member",
            "corporate-manager-of-an-eeig",
            "corporate-managing-officer",
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
            "managing-officer",
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
            description="The officer's role.",
        ),
    ]

    person_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Unique person identifier as displayed in bulk products 195, 198, 208, 209 and 216.",
            default=None,
        ),
    ]

    principal_office_address: typing.Annotated[
        PrincipalOfficeAddress | None,
        pydantic.Field(
            description=(
                "The principal/registered office address of a `corporate-managing-officer` "
                "of a `registered-overseas-entity`."
            ),
            default=None,
        ),
    ]

    resigned_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date the officer was resigned. For the officer roles of "
                "`corporate-managing-officer` and `managing-officer` this is the date on which "
                "Companies House was notified about the officers cessation."
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
                "Only one from `eea`, `non-eea`, `uk-limited-company`, `other-corporate-body-or-firm` "
                "or `registered-overseas-entity-corporate-managing-officer` can be supplied, "
                "not multiples of them."
            ),
            default=None,
        ),
    ]

    identity_verification_details: typing.Annotated[
        officer_changes.IdentityVerificationDetails,
        pydantic.Field(
            description="Information relating to the identity verification of the officer",
            default=None,
        ),
    ]

    appointed_before: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The date the officer was appointed before. Only present when the "
                "<code>is_pre_1992_appointment</code> attribute is <code>true</code>."
            ),
            default=None,
        ),
    ]

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The Etag of the resource",
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
