"""Company exemptions models for Companies House API.

This module contains Pydantic models for the company exemptions endpoint,
which provides information about exemptions from filing requirements.

API Endpoint
-----
GET /company/{company_number}/exemptions

Returns information about exemptions from filing requirements for a company.

Exemptions
-----
Certain companies may be exempt from filing certain documents at Companies House.
Exemptions may apply to:
- Accounts and reports filing
- Confirmation statement filing
- Director service address information
- Audit exemptions
- Other regulatory exemptions

Each exemption record includes:
- Type of exemption
- Status (granted, revoked, etc.)
- Date granted
- Expiry date if applicable

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/exemptions.json

Models in this Module
-----
- :class:`CompanyExemptions` - Root exemptions container
- :class:`Exemption` - Individual exemption record
- And other supporting models

Example Usage
-----
Fetch exemption information::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    exemptions = await client.get_company_exemptions("09370755")
    for exemption in exemptions.exemptions or []:
        print(f"Exemption: {exemption.exemption_type}")

See Also
--------
ch_api.Client.get_company_exemptions : Fetch exemption information
ch_api.types.public_data.company_profile : Company profile information
"""

import datetime
import typing

import pydantic

from .. import base, shared


class ExemptionItem(base.BaseModel):
    """Individual exemption period."""

    exempt_from: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="Exemption valid from.",
        ),
    ]

    exempt_to: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="Exemption valid to.",
            default=None,
        ),
    ]


class PscExemptAsTradingOnRegulatedMarketItem(base.BaseModel):
    """PSC exempt as trading on regulated market exemption."""

    exemption_type: typing.Annotated[
        typing.Literal["psc-exempt-as-trading-on-regulated-market"],
        pydantic.Field(
            description="The exemption type.",
        ),
    ]

    items: typing.Annotated[
        list[ExemptionItem],
        pydantic.Field(
            description="List of dates",
        ),
    ]


class PscExemptAsSharesAdmittedOnMarketItem(base.BaseModel):
    """PSC exempt as shares admitted on market exemption."""

    exemption_type: typing.Annotated[
        typing.Literal["psc-exempt-as-shares-admitted-on-market"],
        pydantic.Field(
            description="The exemption type.",
        ),
    ]

    items: typing.Annotated[
        list[ExemptionItem],
        pydantic.Field(
            description="List of dates",
        ),
    ]


class PscExemptAsTradingOnUkRegulatedMarketItem(base.BaseModel):
    """PSC exempt as trading on UK regulated market exemption."""

    exemption_type: typing.Annotated[
        typing.Literal["psc-exempt-as-trading-on-uk-regulated-market"],
        pydantic.Field(
            description="The exemption type.",
        ),
    ]

    items: typing.Annotated[
        list[ExemptionItem],
        pydantic.Field(
            description="List of dates",
        ),
    ]


class PscExemptAsTradingOnEuRegulatedMarketItem(base.BaseModel):
    """PSC exempt as trading on EU regulated market exemption."""

    exemption_type: typing.Annotated[
        typing.Literal["psc-exempt-as-trading-on-eu-regulated-market"],
        pydantic.Field(
            description="The exemption type.",
        ),
    ]

    items: typing.Annotated[
        list[ExemptionItem],
        pydantic.Field(
            description="List of dates",
        ),
    ]


class DisclosureTransparencyRulesChapterFiveAppliesItem(base.BaseModel):
    """Disclosure transparency rules chapter five applies exemption."""

    exemption_type: typing.Annotated[
        typing.Literal["disclosure-transparency-rules-chapter-five-applies"],
        pydantic.Field(
            description="The exemption type.",
        ),
    ]

    items: typing.Annotated[
        list[ExemptionItem],
        pydantic.Field(
            description="List of exemption periods.",
        ),
    ]


class Exemptions(base.BaseModel):
    """Exemptions information."""

    psc_exempt_as_trading_on_regulated_market: typing.Annotated[
        PscExemptAsTradingOnRegulatedMarketItem | None,
        pydantic.Field(
            description=(
                "If present the company has been or is exempt from keeping a PSC register, "
                "as it has voting shares admitted to trading on a regulated market other than the UK."
            ),
            default=None,
        ),
    ]

    psc_exempt_as_shares_admitted_on_market: typing.Annotated[
        PscExemptAsSharesAdmittedOnMarketItem | None,
        pydantic.Field(
            description=(
                "If present the company has been or is exempt from keeping a PSC register, "
                "as it has voting shares admitted to trading on a market listed in the "
                "Register of People with Significant Control Regulations 2016."
            ),
            default=None,
        ),
    ]

    psc_exempt_as_trading_on_uk_regulated_market: typing.Annotated[
        PscExemptAsTradingOnUkRegulatedMarketItem | None,
        pydantic.Field(
            description=(
                "If present the company has been or is exempt from keeping a PSC register, "
                "as it has voting shares admitted to trading on a UK regulated market."
            ),
            default=None,
        ),
    ]

    psc_exempt_as_trading_on_eu_regulated_market: typing.Annotated[
        PscExemptAsTradingOnEuRegulatedMarketItem | None,
        pydantic.Field(
            description=(
                "If present the company has been or is exempt from keeping a PSC register, "
                "as it has voting shares admitted to trading on an EU regulated market."
            ),
            default=None,
        ),
    ]

    disclosure_transparency_rules_chapter_five_applies: typing.Annotated[
        DisclosureTransparencyRulesChapterFiveAppliesItem | None,
        pydantic.Field(
            description=(
                "If present the company has been or is exempt from keeping a PSC register, "
                "because it is a DTR issuer and the shares are admitted to trading on a regulated market."
            ),
            default=None,
        ),
    ]


class CompanyExemptions(base.BaseModel):
    """Company exemptions information."""

    kind: typing.Annotated[
        typing.Literal["exemptions"],
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

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="A set of URLs related to the resource, including self.",
        ),
    ]

    exemptions: typing.Annotated[
        Exemptions,
        pydantic.Field(
            description="Company exemptions information.",
        ),
    ]
