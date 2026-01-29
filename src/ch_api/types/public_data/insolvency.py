"""Insolvency and administration information models for Companies House API.

This module contains Pydantic models for the company insolvency endpoint,
which provides information about insolvency proceedings and administration.

API Endpoint
-----
GET /company/{company_number}/insolvency

Returns insolvency information for companies in liquidation or administration.

Insolvency Information
-----
Companies in insolvency proceedings provide details about:
- Insolvency cases and dates
- Court cases associated with insolvency
- Practitioner details and contact information
- Case types (administration, liquidation, etc.)
- Dates of various proceedings

This data is required for companies with company status indicating insolvency.

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/insolvency.json

Models in this Module
-----
- :class:`CompanyInsolvency` - Root insolvency container
- :class:`Case` - Individual insolvency case
- :class:`PractitionerDetails` - Insolvency practitioner information
- And other supporting models

Example Usage
-----
Fetch insolvency information::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    insolvency = await client.get_company_insolvency("09370755")
    for case in insolvency.cases or []:
        print(f"Case: {case.case_type} - {case.case_number}")

See Also
--------
ch_api.Client.get_company_insolvency : Fetch insolvency information
ch_api.types.public_data.company_profile : Company profile information
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared


class PractitionerAddress(base.BaseModel):
    """Address of a practitioner."""

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
            description="The country.",
            default=None,
        ),
    ]


class Practitioners(base.BaseModel):
    """Practitioner information for an insolvency case."""

    name: typing.Annotated[
        str,
        pydantic.Field(
            description="The name of the practitioner.",
        ),
    ]

    address: typing.Annotated[
        PractitionerAddress,
        pydantic.Field(
            description="The practitioners' address.",
        ),
    ]

    appointed_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the practitioner was appointed on.",
            default=None,
        ),
    ]

    ceased_to_act_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the practitioner ceased to act for the case.",
            default=None,
        ),
    ]

    role: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "final-liquidator",
            "receiver",
            "receiver-manager",
            "proposed-liquidator",
            "provisional-liquidator",
            "administrative-receiver",
            "practitioner",
            "interim-liquidator",
        ),
        pydantic.Field(
            description="The type of role.",
            default=None,
        ),
    ]


class CaseDates(base.BaseModel):
    """Date information for an insolvency case."""

    type: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "instrumented-on",
            "administration-started-on",
            "administration-discharged-on",
            "administration-ended-on",
            "concluded-winding-up-on",
            "petitioned-on",
            "ordered-to-wind-up-on",
            "due-to-be-dissolved-on",
            "case-end-on",
            "wound-up-on",
            "voluntary-arrangement-started-on",
            "voluntary-arrangement-ended-on",
            "moratorium-started-on",
            "moratorium-ended-on",
            "declaration-solvent-on",
        ),
        pydantic.Field(
            description=(
                "Describes what date is represented by the associated `date` element. "
                "For enumeration descriptions see `insolvency_case_date_type` section in the enumeration mappings."
            ),
        ),
    ]

    date: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The case date, described by `date_type`.",
        ),
    ]


class Case(base.BaseModel):
    """Individual insolvency case."""

    type: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "compulsory-liquidation",
            "creditors-voluntary-liquidation",
            "members-voluntary-liquidation",
            "in-administration",
            "corporate-voluntary-arrangement",
            "corporate-voluntary-arrangement-moratorium",
            "administration-order",
            "receiver-manager",
            "administrative-receiver",
            "receivership",
            "foreign-insolvency",
            "moratorium",
        ),
        pydantic.Field(
            description=(
                "The type of case. "
                "For enumeration descriptions see `insolvency_case_type` section in the enumeration mappings."
            ),
        ),
    ]

    dates: typing.Annotated[
        list[CaseDates],
        pydantic.Field(
            description="The dates specific to the case.",
        ),
    ]

    practitioners: typing.Annotated[
        list[Practitioners],
        pydantic.Field(
            description="The practitioners for the case.",
        ),
    ]

    notes: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description="The dates specific to the case.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="The practitioners for the case.",
            default=None,
        ),
    ]

    number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The case number.",
            default=None,
        ),
    ]


class CompanyInsolvency(base.BaseModel):
    """Company insolvency information."""

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The ETag of the resource.",
            default=None,
        ),
    ]

    cases: typing.Annotated[
        list[Case],
        pydantic.Field(
            description="List of insolvency cases.",
        ),
    ]

    status: typing.Annotated[
        list[
            typing.Annotated[
                str,
                field_types.RelaxedLiteral(
                    "administration-order",
                    "administrative-receiver",
                    "in-administration",
                    "liquidation",
                    "live-receiver-manager-on-at-least-one-charge",
                    "receivership",
                    "receiver-manager",
                    "voluntary-arrangement",
                    "voluntary-arrangement-receivership",
                ),
            ]
        ]
        | None,
        pydantic.Field(
            description="Company insolvency status details",
            default=None,
        ),
    ]
