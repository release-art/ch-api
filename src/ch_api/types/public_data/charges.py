"""Charges (security interests) models for Companies House API.

This module contains Pydantic models for the company charges endpoint,
which provides information about charges (security interests/mortgages) over
company assets.

API Endpoints
-----
GET /company/{company_number}/charges - List all charges
GET /company/{company_number}/charges/{charge_id} - Get charge details

Charge Information
-----
A charge represents a legal security interest over company assets, such as:
- Mortgages or loans secured by property
- Pledges of company assets
- Floating charges over business assets

Each charge record includes:
- Charge number and date created
- Charge status (satisfied, pending, released, etc.)
- Classification (legal mortgage, floating charge, etc.)
- Amount secured
- Persons entitled to the charge
- Related assets
- Satisfaction details if applicable

Charge Status
-----
Possible charge statuses:
- ``satisfied`` - Charge has been fully repaid
- ``outstanding`` - Charge is still active
- ``partially-satisfied`` - Part of charge has been satisfied
- ``released`` - Charge has been released
- ``pending`` - Charge pending satisfaction

See enumeration mappings for complete status definitions:
    https://github.com/companieshouse/api-enumerations

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/charges.json

Models in this Module
-----
- :class:`ChargeList` - Paginated list of charges
- :class:`ChargeDetails` - Detailed charge information
- :class:`ChargeSummary` - Summary of a charge
- :class:`ClassificationDesc` - Charge type classification
- :class:`PersonsEntitled` - Details of charge beneficiaries
- And other supporting models

Example Usage
-----
Fetch all charges for a company::

    >>> from ch_api import Client, api_settings
    >>> auth = api_settings.AuthSettings(api_key="your-key")
    >>> client = Client(credentials=auth)
    ...
    >>> charges = await client.get_company_charges("09370755")
    >>> for charge in charges.items or []:
    ...     print(f"Charge {charge.charge_number}: {charge.charge_code}")

Get detailed charge information::

    >>> details = await client.get_company_charge_details(
    ...     "09370755",
    ...     "charge_id_123"
    ... )
    >>> print(f"Status: {details.status}")
    Status: ...
    >>> print(f"Created: {details.created_on}")
    Created: ...

See Also
--------
ch_api.Client.get_company_charges : Fetch all charges
ch_api.Client.get_company_charge_details : Get charge details
ch_api.types.public_data.company_profile : Company profile information
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared


class ClassificationDesc(base.BaseModel):
    """Classification information for a charge."""

    type: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "charge-description",
            "nature-of-charge",
        ),
        pydantic.Field(
            description=(
                "The type of charge classication. "
                "For enumeration descriptions see `classificationDesc` section in the enumeration mappings."
            ),
        ),
    ]

    description: typing.Annotated[
        str,
        pydantic.Field(
            description="Details of the charge classification",
        ),
    ]


class ParticularDesc(base.BaseModel):
    """Details of charge or undertaking."""

    type: typing.Annotated[
        field_types.UndocumentedNullable[str],
        field_types.RelaxedLiteral(
            "short-particulars",
            "charged-property-description",
            "charged-property-or-undertaking-description",
            "brief-description",
        ),
        pydantic.Field(
            description=(
                "The type of charge particulars. "
                "For enumeration descriptions see `particular-description` section in the enumeration mappings."
            ),
            default=None,
        ),
    ]

    description: typing.Annotated[
        field_types.UndocumentedNullable[str],
        pydantic.Field(
            description="Details of charge particulars",
            default=None,
        ),
    ]

    contains_floating_charge: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="The charge contains a floating charge",
            default=None,
        ),
    ]

    contains_fixed_charge: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="The charge contains a fixed charge",
            default=None,
        ),
    ]

    floating_charge_covers_all: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="The floating charge covers all the property or undertaking or the company",
            default=None,
        ),
    ]

    contains_negative_pledge: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="The charge contains a negative pledge",
            default=None,
        ),
    ]

    chargor_acting_as_bare_trustee: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="The chargor is acting as a bare trustee for the property",
            default=None,
        ),
    ]


class SecuredDetailsDesc(base.BaseModel):
    """Information about what is secured against this charge."""

    type: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "amount-secured",
            "obligations-secured",
        ),
        pydantic.Field(
            description=(
                "The type of secured details. "
                "For enumeration descriptions see `secured-details-description` section in the enumeration mappings."
            ),
        ),
    ]

    description: typing.Annotated[
        str,
        pydantic.Field(
            description="Details of the amount or obligation secured by the charge",
        ),
    ]


class AlterationsDesc(base.BaseModel):
    """Information about alterations for Scottish companies."""

    has_alterations_to_order: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="The charge has alterations to order",
            default=None,
        ),
    ]

    has_alterations_to_prohibitions: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="The charge has alterations to prohibitions",
            default=None,
        ),
    ]

    has_alterations_to_provisions: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="The charge has provisions restricting the creation of further charges",
            default=None,
        ),
    ]


class PersonsEntitled(base.BaseModel):
    """Person entitled to the charge."""

    name: typing.Annotated[
        str,
        pydantic.Field(
            description="The name of the person entitled.",
        ),
    ]


class Transactions(base.BaseModel):
    """Transaction that has been filed for the charge."""

    filing_type: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Filing type which created, updated or satisfied the charge",
            default=None,
        ),
    ]

    delivered_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the filing was submitted to Companies House",
            default=None,
        ),
    ]

    insolvency_case_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The insolvency case related to this filing",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="The resources related to this filing",
            default=None,
        ),
    ]


class InsolvencyCases(base.BaseModel):
    """Insolvency case related to the charge."""

    case_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The number of this insolvency case",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="The resources related to this insolvency case",
            default=None,
        ),
    ]


class ChargeDetails(base.BaseModel):
    """Individual charge information for company."""

    etag: typing.Annotated[
        str,
        pydantic.Field(
            description="The ETag of the resource.",
        ),
    ]

    id: typing.Annotated[
        field_types.UndocumentedNullable[str],
        pydantic.Field(
            description="The id of the charge",
            default=None,
        ),
    ]

    status: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "outstanding",
            "fully-satisfied",
            "part-satisfied",
            "satisfied",
        ),
        pydantic.Field(
            description=(
                "The status of the charge. "
                "For enumeration descriptions see `status` section in the enumeration mappings."
            ),
        ),
    ]

    classification: typing.Annotated[
        ClassificationDesc,
        pydantic.Field(
            description="Classification information",
        ),
    ]

    charge_number: typing.Annotated[
        int,
        pydantic.Field(
            description="The charge number is used to reference an individual charge",
        ),
    ]

    charge_code: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The charge code is a replacement of the mortgage description",
            default=None,
        ),
    ]

    assests_ceased_released: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "property-ceased-to-belong",
            "part-property-release-and-ceased-to-belong",
            "part-property-released",
            "part-property-ceased-to-belong",
            "whole-property-released",
            "multiple-filings",
            "whole-property-released-and-ceased-to-belong",
        ),
        pydantic.Field(
            description=(
                "Cease/release information about the charge. "
                "For enumeration descriptions see `assets-ceased-released` section in the enumeration mappings."
            ),
            default=None,
        ),
    ]

    acquired_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the property or undertaking was acquired on",
            default=None,
        ),
    ]

    delivered_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the charge was submitted to Companies House",
            default=None,
        ),
    ]

    resolved_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the issue was resolved on",
            default=None,
        ),
    ]

    covering_instrument_date: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date by which the series of debentures were created",
            default=None,
        ),
    ]

    created_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the charge was created",
            default=None,
        ),
    ]

    satisfied_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the charge was satisfied",
            default=None,
        ),
    ]

    particulars: typing.Annotated[
        ParticularDesc | None,
        pydantic.Field(
            description="Details of charge or undertaking",
            default=None,
        ),
    ]

    secured_details: typing.Annotated[
        SecuredDetailsDesc | None,
        pydantic.Field(
            description="Information about what is secured against this charge",
            default=None,
        ),
    ]

    scottish_alterations: typing.Annotated[
        AlterationsDesc | None,
        pydantic.Field(
            description="Information about alterations for Scottish companies",
            default=None,
        ),
    ]

    more_than_four_persons_entitled: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Charge has more than four person entitled",
            default=None,
        ),
    ]

    persons_entitled: typing.Annotated[
        list[PersonsEntitled] | None,
        pydantic.Field(
            description="People that are entitled to the charge",
            default=None,
        ),
    ]

    transactions: typing.Annotated[
        list[Transactions] | None,
        pydantic.Field(
            description="Transactions that have been filed for the charge.",
            default=None,
        ),
    ]

    insolvency_cases: typing.Annotated[
        list[InsolvencyCases] | None,
        pydantic.Field(
            description="Transactions that have been filed for the charge.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="The resources related to this charge",
            default=None,
        ),
    ]


class ChargeList(base.BaseModel):
    """List of charges for a company."""

    etag: typing.Annotated[
        str,
        pydantic.Field(
            description="The ETag of the resource.",
        ),
    ]

    items: typing.Annotated[
        list[ChargeDetails],
        pydantic.Field(
            description="List of charges",
        ),
    ]

    total_count: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Total number of charges returned by the API (filtering applies).",
            default=None,
        ),
    ]

    unfiletered_count: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Number of satisfied charges",
            default=None,
        ),
    ]

    satisfied_count: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Number of satisfied charges",
            default=None,
        ),
    ]

    part_satisfied_count: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Number of satisfied charges",
            default=None,
        ),
    ]
