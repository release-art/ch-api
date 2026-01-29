"""Persons with Significant Control (PSC) models for Companies House API.

This module contains Pydantic models for PSC endpoints, which provide information
about persons with significant control over UK limited companies as required by the
Economic Crime (Transparency and Enforcement) Act 2022.

API Endpoints
-----
GET /company/{company_number}/persons-with-significant-control - List PSCs
GET /company/{company_number}/persons-with-significant-control/individual/{psc_id}
GET /company/{company_number}/persons-with-significant-control/corporate-entity/{psc_id}
GET /company/{company_number}/persons-with-significant-control/legal-person/{psc_id}
GET /company/{company_number}/persons-with-significant-control/super-secure/{psc_id}
GET /company/{company_number}/persons-with-significant-control-statements

PSC Framework
-----
Persons with Significant Control (PSC) are individuals or entities that meet
one or more of the following conditions:
- Own more than 25% of shares
- Have more than 25% of voting rights
- Have the right to appoint/remove majority of board
- Exercise significant influence or control

PSC Types
-----
The API returns different PSC types:
- **Individual** - Natural person with control
- **Individual Beneficial Owner** - Individual ultimately controlling assets
- **Corporate Entity** - Company with control
- **Corporate Entity Beneficial Owner** - Corporate entity with beneficial control
- **Legal Person** - Other legal entity (e.g., foundation, trust)
- **Legal Person Beneficial Owner** - Legal entity with beneficial control
- **Super Secure** - Protected PSC (address protected for safety)
- **Super Secure Beneficial Owner** - Protected beneficial owner

Nature of Control
-----
Each PSC record specifies the nature of their control:
- Ownership of shares
- Voting rights
- Right to appoint/remove directors
- Significant influence or control
- Trustees/other types of control

PSC Statements
-----
Companies can file PSC statements when:
- No PSCs have been identified
- Information about PSCs is restricted
- There has been a change in PSC information

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/psc.json

Legal Background:
    https://www.gov.uk/government/publications/register-of-people-with-significant-control

Models in this Module
-----
- :class:`PSCList` - Paginated list of PSCs
- :class:`Individual` - Individual PSC
- :class:`IndividualBeneficialOwner` - Individual beneficial owner
- :class:`CorporateEntity` - Corporate entity PSC
- :class:`CorporateEntityBeneficialOwner` - Corporate beneficial owner
- :class:`LegalPerson` - Legal person PSC
- :class:`LegalPersonBeneficialOwner` - Legal person beneficial owner
- :class:`SuperSecure` - Protected individual PSC
- :class:`SuperSecureBeneficialOwner` - Protected beneficial owner
- :class:`PSCStatement` - PSC statement
- :class:`StatementList` - List of PSC statements
- And other supporting models

Example Usage
-----
Fetch PSC list for a company::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    psc_list = await client.get_company_psc_list("09370755")
    async for psc in psc_list.items:
        print(f"PSC: {psc.name}")

Get detailed PSC information::

    psc = await client.get_company_individual_psc(
        "09370755",
        "psc_id_123"
    )
    print(f"Name: {psc.name}")
    print(f"Nationality: {psc.nationality}")
    print(f"Date of birth: {psc.date_of_birth}")

Get PSC statements::

    statements = await client.get_company_psc_statements("09370755")
    for statement in statements.items:
        print(f"Statement: {statement.statement}")

See Also
--------
ch_api.Client.get_company_psc_list : Fetch PSC list
ch_api.Client.get_company_individual_psc : Get individual PSC details
ch_api.Client.get_company_psc_statements : Get PSC statements
ch_api.types.public_data.company_profile : Company profile

References
----------
- https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
- https://www.gov.uk/guidance/register-of-people-with-significant-control
"""

import datetime
import typing

import pydantic

from .. import base, shared


class PSCAddress(base.BaseModel):
    """Address information for a person with significant control."""

    address_line_1: typing.Annotated[
        str | None,
        pydantic.Field(description="The first line of the address.", default=None),
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
            description="Care of name.",
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

    locality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The locality. For example London.",
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
        str,
        pydantic.Field(description="The postal code. For example CF14 3UZ."),
    ]

    premises: typing.Annotated[
        str | None,
        pydantic.Field(description="The property name or number.", default=None),
    ]

    region: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The region. For example Surrey.",
            default=None,
        ),
    ]


class BeneficialOwnerAddress(base.BaseModel):
    """Address information for a beneficial owner."""

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
            description="The country. For example, United Kingdom.",
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
            description="The region. For example Surrey.",
            default=None,
        ),
    ]


class NameElements(base.BaseModel):
    """Name elements for a person with significant control."""

    forename: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The forename of the person with significant control.",
            default=None,
        ),
    ]

    title: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Title of the person with significant control.",
            default=None,
        ),
    ]

    middle_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The middle name of the person with significant control.",
            default=None,
        ),
    ]

    surname: typing.Annotated[
        str,
        pydantic.Field(description="The surname of the person with significant control."),
    ]


class BeneficialOwnerNameElements(base.BaseModel):
    """Name elements for a beneficial owner."""

    forename: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The forename of the beneficial owner.",
            default=None,
        ),
    ]

    title: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Title of the beneficial owner.",
            default=None,
        ),
    ]

    middle_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The middle name of the beneficial owner.",
            default=None,
        ),
    ]

    surname: typing.Annotated[
        str,
        pydantic.Field(description="The surname of the beneficial owner."),
    ]


class DateOfBirth(base.BaseModel):
    """Date of birth information for a PSC."""

    day: typing.Annotated[
        int | None,
        pydantic.Field(
            description="The day of the date of birth.",
            default=None,
        ),
    ]

    month: typing.Annotated[
        int,
        pydantic.Field(description="The month of date of birth."),
    ]

    year: typing.Annotated[
        int,
        pydantic.Field(description="The year of date of birth."),
    ]


class DateOfBirthPSCList(base.BaseModel):
    """Date of birth information for a PSC in a list response."""

    month: typing.Annotated[
        int,
        pydantic.Field(description="The month of date of birth."),
    ]

    year: typing.Annotated[
        int,
        pydantic.Field(description="The year of date of birth."),
    ]


class BeneficialOwnerDateOfBirth(base.BaseModel):
    """Date of birth information for a beneficial owner."""

    day: typing.Annotated[
        int | None,
        pydantic.Field(
            description="The day of the date of birth.",
            default=None,
        ),
    ]

    month: typing.Annotated[
        int | None,
        pydantic.Field(
            description="The month of date of birth.",
            default=None,
        ),
    ]

    year: typing.Annotated[
        int | None,
        pydantic.Field(
            description="The year of date of birth.",
            default=None,
        ),
    ]


class CorporateEntityIdent(base.BaseModel):
    """Identification for a corporate entity PSC."""

    legal_authority: typing.Annotated[
        str,
        pydantic.Field(description="The legal authority supervising the corporate entity with significant control."),
    ]

    legal_form: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "The legal form of the corporate entity with significant "
                "control as defined by its country of registration."
            )
        ),
    ]

    place_registered: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The place the corporate entity with significant control is registered.",
            default=None,
        ),
    ]

    registration_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The registration number of the corporate entity with significant control.",
            default=None,
        ),
    ]

    country_registered: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country or state the corporate entity with significant control is registered in.",
            default=None,
        ),
    ]


class BeneficialOwnerCorporateEntityIdent(base.BaseModel):
    """Identification for a beneficial owner corporate entity."""

    legal_authority: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The legal authority supervising the corporate entity beneficial owner.",
            default=None,
        ),
    ]

    legal_form: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The legal form of the corporate entity beneficial owner as defined by its country of registration."
            ),
            default=None,
        ),
    ]

    place_registered: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The place the corporate entity beneficial owner is registered.",
            default=None,
        ),
    ]

    registration_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The registration number of the corporate entity beneficial owner.",
            default=None,
        ),
    ]

    country_registered: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country or state the corporate entity beneficial owner is registered in.",
            default=None,
        ),
    ]


class PSCListIdent(base.BaseModel):
    """Identification for a corporate entity or legal person PSC in list."""

    legal_authority: typing.Annotated[
        str,
        pydantic.Field(
            description="The legal authority supervising the corporate entity or legal person with significant control."
        ),
    ]

    legal_form: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "The legal form of the corporate entity or legal person "
                "with significant control as defined by its country of "
                "registration."
            )
        ),
    ]

    place_registered: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The place the corporate entity with significant control is registered.",
            default=None,
        ),
    ]

    registration_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The registration number of the corporate entity with significant control.",
            default=None,
        ),
    ]

    country_registered: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country or state the corporate entity with significant control is registered in.",
            default=None,
        ),
    ]


class LegalPersonIdent(base.BaseModel):
    """Identification for a legal person PSC."""

    legal_authority: typing.Annotated[
        str,
        pydantic.Field(description="The legal authority supervising the legal person with significant control."),
    ]

    legal_form: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "The legal form of the legal person with significant control as defined by its country of registration."
            )
        ),
    ]


class LegalPersonBeneficialOwnerIdent(base.BaseModel):
    """Identification for a legal person beneficial owner."""

    legal_authority: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The legal authority supervising the legal person beneficial owner.",
            default=None,
        ),
    ]

    legal_form: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The legal form of the legal person beneficial owner as defined by its country of registration."
            ),
            default=None,
        ),
    ]


class IdentityVerificationDetails(base.BaseModel):
    """Identity verification details for a PSC."""

    anti_money_laundering_supervisory_bodies: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description=(
                "The Anti-Money Laundering supervisory bodies that the "
                "authorised corporate service provider was registered with "
                "when verifying the person with significant control"
            ),
            default=None,
        ),
    ]

    appointment_verification_end_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date on which the identity verification statement was removed for the notification",
            default=None,
        ),
    ]

    appointment_verification_statement_date: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date from which an identity verification statement can be supplied for the notification",
            default=None,
        ),
    ]

    appointment_verification_statement_due_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date by which an identity verification statement must be supplied for the notification",
            default=None,
        ),
    ]

    appointment_verification_start_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date on which the identity verification statement was supplied for the notification",
            default=None,
        ),
    ]

    authorised_corporate_service_provider_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The name of the authorised corporate service provider "
                "that verified the identity of the person with "
                "significant control"
            ),
            default=None,
        ),
    ]

    identity_verified_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date on which the authorised corporate service "
                "provider verified the identity of the person with "
                "significant control"
            ),
            default=None,
        ),
    ]

    preferred_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The name provided to the authorised corporate service "
                "provider by which the person with significant control "
                "prefers to be known"
            ),
            default=None,
        ),
    ]


class ListSummary(base.BaseModel):
    """Summary of a person with significant control in a list."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    notified_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description=("The date that Companies House was notified about this person with significant control.")
        ),
    ]

    ceased_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date that Companies House was notified about the "
                "cessation of this person with significant control."
            ),
            default=None,
        ),
    ]

    country_of_residence: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country of residence of the person with significant control.",
            default=None,
        ),
    ]

    date_of_birth: typing.Annotated[
        DateOfBirthPSCList | None,
        pydantic.Field(
            description="The date of birth of the person with significant control.",
            default=None,
        ),
    ]

    name: typing.Annotated[
        str,
        pydantic.Field(description="Name of the person with significant control."),
    ]

    name_elements: typing.Annotated[
        NameElements | None,
        pydantic.Field(
            description="A document encapsulating the separate elements of a person with significant control's name.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]

    nationality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The nationality of the person with significant control.",
            default=None,
        ),
    ]

    identification: typing.Annotated[
        PSCListIdent | None,
        pydantic.Field(
            description="Identification details of the person with significant control.",
            default=None,
        ),
    ]

    identity_verification_details: typing.Annotated[
        IdentityVerificationDetails | None,
        pydantic.Field(
            description="Information relating to the identity verification of the person with significant control",
            default=None,
        ),
    ]

    ceased: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Presence of that indicator means the person with significant control status is ceased",
            default=None,
        ),
    ]

    description: typing.Annotated[
        typing.Literal["persons-with-significant-control"] | None,
        pydantic.Field(
            description="Description of the super secure legal statement",
            default=None,
        ),
    ]

    kind: typing.Annotated[
        typing.Literal[
            "individual-person-with-significant-control",
            "corporate-entity-person-with-significant-control",
            "legal-person-with-significant-control",
            "super-secure-person-with-significant-control",
            "individual-beneficial-owner",
            "corporate-entity-beneficial-owner",
            "legal-person-beneficial-owner",
            "super-secure-beneficial-owner",
            "legal-person-person-with-significant-control",
        ]
        | None,
        pydantic.Field(
            description="The kind of person with significant control.",
            default=None,
        ),
    ]

    address: typing.Annotated[
        PSCAddress | None,
        pydantic.Field(
            description=(
                "The service address of the person with significant "
                "control. If given, this address will be shown on the "
                "public record instead of the residential address."
            ),
            default=None,
        ),
    ]

    natures_of_control: typing.Annotated[
        list[str],
        pydantic.Field(description=("Indicates the nature of control the person with significant control holds.")),
    ]

    is_sanctioned: typing.Annotated[
        bool | None,
        pydantic.Field(
            description=(
                "Flag indicating if the beneficial owner was declared "
                "as being sanctioned on the latest filing of the "
                "overseas entity"
            ),
            default=None,
        ),
    ]

    principal_office_address: typing.Annotated[
        BeneficialOwnerAddress | None,
        pydantic.Field(
            description=(
                "The principal/registered office address of a "
                "corporate-entity-beneficial-owner or "
                "legal-person-beneficial-owner of a "
                "registered-overseas-entity."
            ),
            default=None,
        ),
    ]


class PSCList(base.BaseModel):
    """List of persons with significant control."""

    items_per_page: typing.Annotated[
        int,
        pydantic.Field(description="The number of persons with significant control to return per page."),
    ]

    items: typing.Annotated[
        list[ListSummary],
        pydantic.Field(description="The list of persons with significant control."),
    ]

    start_index: typing.Annotated[
        int,
        pydantic.Field(description="The offset into the entire result set that this page starts."),
    ]

    total_results: typing.Annotated[
        int,
        pydantic.Field(description="The total number of persons with significant control in this result set."),
    ]

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


class IndividualList(base.BaseModel):
    """List of individual persons with significant control."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    items_per_page: typing.Annotated[
        int,
        pydantic.Field(description="The number of individual persons with significant control to return per page."),
    ]

    kind: typing.Annotated[
        typing.Literal["persons-with-significant-control#list-individual"],
        pydantic.Field(description="The kind of resource."),
    ]

    items: typing.Annotated[
        list[ListSummary],
        pydantic.Field(description="The list of individual persons with significant control."),
    ]

    start_index: typing.Annotated[
        int,
        pydantic.Field(description="The offset into the entire result set that this page starts."),
    ]

    total_results: typing.Annotated[
        int,
        pydantic.Field(
            description="The total number of individual persons with significant control in this result set."
        ),
    ]

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


class CorporateEntityList(base.BaseModel):
    """List of corporate entity persons with significant control."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    items_per_page: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of corporate entity persons with significant control to return per page."
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["persons-with-significant-control#list-corporate-entity"],
        pydantic.Field(description="The kind of resource."),
    ]

    items: typing.Annotated[
        list[ListSummary],
        pydantic.Field(description="The list of corporate entity persons with significant control."),
    ]

    start_index: typing.Annotated[
        int,
        pydantic.Field(description="The offset into the entire result set that this page starts."),
    ]

    total_results: typing.Annotated[
        int,
        pydantic.Field(
            description="The total number of corporate entity persons with significant control in this result set."
        ),
    ]

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


class LegalPersonList(base.BaseModel):
    """List of legal person persons with significant control."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    items_per_page: typing.Annotated[
        int,
        pydantic.Field(description="The number of legal persons with significant control to return per page."),
    ]

    kind: typing.Annotated[
        typing.Literal["persons-with-significant-control#list-legal-person"],
        pydantic.Field(description="The kind of resource."),
    ]

    items: typing.Annotated[
        list[ListSummary],
        pydantic.Field(description="The list of legal persons with significant control."),
    ]

    start_index: typing.Annotated[
        int,
        pydantic.Field(description="The offset into the entire result set that this page starts."),
    ]

    total_results: typing.Annotated[
        int,
        pydantic.Field(description="The total number of legal persons with significant control in this result set."),
    ]

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


class StatementList(base.BaseModel):
    """List of persons with significant control statements."""

    items_per_page: typing.Annotated[
        int,
        pydantic.Field(description="The number of persons with significant control statements to return per page."),
    ]

    items: typing.Annotated[
        list["Statement"],
        pydantic.Field(description="The list of persons with significant control statements."),
    ]

    start_index: typing.Annotated[
        int,
        pydantic.Field(description="The offset into the entire result set that this page starts."),
    ]

    total_results: typing.Annotated[
        int,
        pydantic.Field(
            description="The total number of persons with significant control statements in this result set."
        ),
    ]

    active_count: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of active persons with significant control statements in this result set."
        ),
    ]

    ceased_count: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of ceased persons with significant control statements in this result set."
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]


class Statement(base.BaseModel):
    """A person with significant control statement."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    kind: typing.Annotated[
        typing.Literal["persons-with-significant-control-statement"],
        pydantic.Field(description="The kind of resource."),
    ]

    notified_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description=(
                "The date that the person with significant control statement was processed by Companies House."
            )
        ),
    ]

    ceased_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date that Companies House was notified about the "
                "cessation of this person with significant control."
            ),
            default=None,
        ),
    ]

    restrictions_notice_withdrawal_reason: typing.Annotated[
        typing.Literal[
            "restrictions-notice-withdrawn-by-court-order",
            "restrictions-notice-withdrawn-by-company",
            "restrictions-notice-withdrawn-by-lp",
            "restrictions-notice-withdrawn-by-court-order-lp",
            "restrictions-notice-withdrawn-by-partnership",
            "restrictions-notice-withdrawn-by-court-order-p",
        ]
        | None,
        pydantic.Field(
            description="The reason for the company withdrawing a restrictions-notice-issued-to-psc statement",
            default=None,
        ),
    ]

    statement: typing.Annotated[
        str,
        pydantic.Field(description="Indicates the type of statement filed."),
    ]

    linked_psc_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The name of the psc linked to this statement.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]


class SuperSecure(base.BaseModel):
    """A super secure person with significant control."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    kind: typing.Annotated[
        typing.Literal["super-secure-person-with-significant-control"],
        pydantic.Field(description="The kind of resource."),
    ]

    description: typing.Annotated[
        typing.Literal["super-secure-persons-with-significant-control"],
        pydantic.Field(description="Description of the super secure legal statement"),
    ]

    identity_verification_details: typing.Annotated[
        IdentityVerificationDetails | None,
        pydantic.Field(
            description="Information relating to the identity verification of the person with significant control",
            default=None,
        ),
    ]

    ceased: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Presence of that indicator means the super secure person status is ceased",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]


class SuperSecureBeneficialOwner(base.BaseModel):
    """A super secure beneficial owner."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    kind: typing.Annotated[
        typing.Literal["super-secure-beneficial-owner"],
        pydantic.Field(description="The kind of resource."),
    ]

    description: typing.Annotated[
        typing.Literal["super-secure-beneficial-owner"],
        pydantic.Field(description="Description of the super secure legal statement"),
    ]

    ceased: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Presence of this indicator means the super secure beneficial owner status is ceased",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]


class Individual(base.BaseModel):
    """An individual person with significant control."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    notified_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date that Companies House was notified about this person with significant control."
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["individual-person-with-significant-control"],
        pydantic.Field(description="The kind of resource."),
    ]

    country_of_residence: typing.Annotated[
        str,
        pydantic.Field(description="The country of residence of the person with significant control."),
    ]

    date_of_birth: typing.Annotated[
        DateOfBirth,
        pydantic.Field(description="The date of birth of the person with significant control."),
    ]

    name: typing.Annotated[
        str,
        pydantic.Field(
            description=("Name of the person with significant control. Generated by combining the name elements.")
        ),
    ]

    name_elements: typing.Annotated[
        NameElements,
        pydantic.Field(
            description=("A document encapsulating the separate elements of a person with significant control's name.")
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]

    nationality: typing.Annotated[
        str,
        pydantic.Field(description="The nationality of the person with significant control."),
    ]

    ceased_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date that Companies House was notified about the "
                "cessation of this person with significant control."
            ),
            default=None,
        ),
    ]

    address: typing.Annotated[
        PSCAddress | None,
        pydantic.Field(
            description=(
                "The service address of the person with significant "
                "control. If given, this address will be shown on the "
                "public record instead of the residential address."
            ),
            default=None,
        ),
    ]

    natures_of_control: typing.Annotated[
        list[str],
        pydantic.Field(description=("Indicates the nature of control the person with significant control holds.")),
    ]

    identity_verification_details: typing.Annotated[
        IdentityVerificationDetails | None,
        pydantic.Field(
            description="Information relating to the identity verification of the person with significant control",
            default=None,
        ),
    ]


class IndividualBeneficialOwner(base.BaseModel):
    """An individual beneficial owner."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    kind: typing.Annotated[
        typing.Literal["individual-beneficial-owner"],
        pydantic.Field(description="The kind of resource."),
    ]

    notified_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date that Companies House was notified about this beneficial owner.",
            default=None,
        ),
    ]

    ceased_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date that Companies House was notified about the cessation of this beneficial owner.",
            default=None,
        ),
    ]

    date_of_birth: typing.Annotated[
        BeneficialOwnerDateOfBirth | None,
        pydantic.Field(
            description="The date of birth of the beneficial owner.",
            default=None,
        ),
    ]

    name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Name of the beneficial owner. Generated by combining the name elements.",
            default=None,
        ),
    ]

    name_elements: typing.Annotated[
        BeneficialOwnerNameElements | None,
        pydantic.Field(
            description="A document encapsulating the separate elements of a beneficial owner's name.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]

    nationality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The nationality of the beneficial owner.",
            default=None,
        ),
    ]

    address: typing.Annotated[
        BeneficialOwnerAddress | None,
        pydantic.Field(
            description=(
                "The service address of the beneficial owner. If given, "
                "this address will be shown on the public record instead "
                "of the residential address."
            ),
            default=None,
        ),
    ]

    natures_of_control: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description=("Indicates the nature of control the beneficial owner holds."),
            default=None,
        ),
    ]

    is_sanctioned: typing.Annotated[
        bool | None,
        pydantic.Field(
            description=(
                "Flag indicating if the beneficial owner was declared "
                "as being sanctioned on the latest filing of the "
                "overseas entity"
            ),
            default=None,
        ),
    ]


class CorporateEntity(base.BaseModel):
    """A corporate entity person with significant control."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    notified_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description=("The date that Companies House was notified about this person with significant control.")
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["corporate-entity-person-with-significant-control"],
        pydantic.Field(description="The kind of resource."),
    ]

    name: typing.Annotated[
        str,
        pydantic.Field(description="Name of the person with significant control."),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]

    ceased_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date that Companies House was notified about the "
                "cessation of this person with significant control."
            ),
            default=None,
        ),
    ]

    address: typing.Annotated[
        PSCAddress | None,
        pydantic.Field(description="The address of the person with significant control."),
    ]

    identification: typing.Annotated[
        CorporateEntityIdent | None,
        pydantic.Field(
            description=("Identification details of the person with significant control."),
            default=None,
        ),
    ]

    natures_of_control: typing.Annotated[
        list[str],
        pydantic.Field(description=("Indicates the nature of control the person with significant control holds.")),
    ]


class CorporateEntityBeneficialOwner(base.BaseModel):
    """A corporate entity beneficial owner."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    kind: typing.Annotated[
        typing.Literal["corporate-entity-beneficial-owner"],
        pydantic.Field(description="The kind of resource."),
    ]

    notified_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=("The date that Companies House was notified about this beneficial owner."),
            default=None,
        ),
    ]

    ceased_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=("The date that Companies House was notified about the cessation of this beneficial owner."),
            default=None,
        ),
    ]

    name: typing.Annotated[
        str | None,
        pydantic.Field(description="Name of the beneficial owner.", default=None),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]

    address: typing.Annotated[
        BeneficialOwnerAddress | None,
        pydantic.Field(
            description="The address of the beneficial owner.",
            default=None,
        ),
    ]

    principal_office_address: typing.Annotated[
        BeneficialOwnerAddress | None,
        pydantic.Field(
            description=(
                "The principal/registered office address of a "
                "corporate-entity-beneficial-owner of a "
                "registered-overseas-entity."
            ),
            default=None,
        ),
    ]

    identification: typing.Annotated[
        BeneficialOwnerCorporateEntityIdent | None,
        pydantic.Field(
            description="Identification details of the beneficial owner.",
            default=None,
        ),
    ]

    natures_of_control: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description=("Indicates the nature of control the beneficial owner holds."),
            default=None,
        ),
    ]

    is_sanctioned: typing.Annotated[
        bool | None,
        pydantic.Field(
            description=(
                "Flag indicating if the beneficial owner was declared "
                "as being sanctioned on the latest filing of the "
                "overseas entity"
            ),
            default=None,
        ),
    ]


class LegalPerson(base.BaseModel):
    """A legal person with significant control."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    notified_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date that Companies House was notified about this person with significant control."
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["legal-person-person-with-significant-control"],
        pydantic.Field(description="The kind of resource."),
    ]

    name: typing.Annotated[
        str,
        pydantic.Field(description="Name of the person with significant control."),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]

    ceased_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date that Companies House was notified about the "
                "cessation of this person with significant control."
            ),
            default=None,
        ),
    ]

    address: typing.Annotated[
        PSCAddress | None,
        pydantic.Field(description="The address of the person with significant control."),
    ]

    identification: typing.Annotated[
        LegalPersonIdent | None,
        pydantic.Field(
            description="Identification details of the person with significant control.",
            default=None,
        ),
    ]

    natures_of_control: typing.Annotated[
        list[str],
        pydantic.Field(description="Indicates the nature of control the person with significant control holds."),
    ]


class LegalPersonBeneficialOwner(base.BaseModel):
    """A legal person beneficial owner."""

    etag: typing.Annotated[
        str,
        pydantic.Field(description="The ETag of the resource."),
    ]

    kind: typing.Annotated[
        typing.Literal["legal-person-beneficial-owner"],
        pydantic.Field(description="The kind of resource."),
    ]

    notified_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=("The date that Companies House was notified about this beneficial owner."),
            default=None,
        ),
    ]

    ceased_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=("The date that Companies House was notified about the cessation of this beneficial owner."),
            default=None,
        ),
    ]

    name: typing.Annotated[
        str | None,
        pydantic.Field(description="Name of the beneficial owner.", default=None),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(description="A set of URLs related to the resource, including self."),
    ]

    address: typing.Annotated[
        BeneficialOwnerAddress | None,
        pydantic.Field(
            description="The address of the beneficial owner.",
            default=None,
        ),
    ]

    principal_office_address: typing.Annotated[
        BeneficialOwnerAddress | None,
        pydantic.Field(
            description=(
                "The principal/registered office address of a "
                "legal-person-beneficial-owner of a "
                "registered-overseas-entity."
            ),
            default=None,
        ),
    ]

    identification: typing.Annotated[
        LegalPersonBeneficialOwnerIdent | None,
        pydantic.Field(
            description="Identification details of the beneficial owner.",
            default=None,
        ),
    ]

    natures_of_control: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description="Indicates the nature of control the beneficial owner holds.",
            default=None,
        ),
    ]

    is_sanctioned: typing.Annotated[
        bool | None,
        pydantic.Field(
            description=(
                "Flag indicating if the beneficial owner was declared "
                "as being sanctioned on the latest filing of the "
                "overseas entity"
            ),
            default=None,
        ),
    ]
