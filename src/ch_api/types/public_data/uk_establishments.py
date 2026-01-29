"""UK establishments models for Companies House API.

This module contains Pydantic models for the UK establishments endpoint,
which provides information about UK branches of overseas companies.

API Endpoint
-----
GET /company/{company_number}/uk-establishments

Returns information about UK establishments for overseas companies.

UK Establishments
-----
Overseas companies operating in the UK must register their UK establishments
at Companies House. A UK establishment record includes:
- Establishment number
- Business name
- Registered office address in the UK
- Establishment status
- Date of registration
- Type of establishment
- Details of the overseas company
- Management and principal place of business

Overseas Company Operations
-----
UK establishments are required to provide:
- UK registered office address
- Details of persons authorized to manage UK business
- Contact information
- Details of the parent/overseas company
- Accounts and reports filed

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/companyUKEstablishments.json

Models in this Module
-----
- :class:`CompanyUKEstablishments` - Container for UK establishments
- :class:`UKEstablishment` - Individual UK establishment record
- And other supporting models

Example Usage
-----
Fetch UK establishments::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    establishments = await client.get_company_uk_establishments("09370755")
    for establishment in establishments.establishments or []:
        print(f"Establishment: {establishment.business_name}")
        print(f"Address: {establishment.registered_office.address_line_1}")

See Also
--------
ch_api.Client.get_company_uk_establishments : Fetch UK establishments
ch_api.types.public_data.company_profile : Company profile information
"""

import typing

import pydantic

from .. import base, shared


class CompanyEstablishmentDetails(base.BaseModel):
    """Details of a UK establishment company.

    This model represents a single UK establishment company record,
    including the company identification and status information.
    """

    company_number: typing.Annotated[
        str,
        pydantic.Field(description="The number of the company."),
    ]

    company_name: typing.Annotated[
        str,
        pydantic.Field(description="The name of the company."),
    ]

    company_status: typing.Annotated[
        str,
        pydantic.Field(description="Company status."),
    ]

    locality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The locality e.g London.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="Resources related to this company.",
        ),
    ]


class CompanyUKEstablishments(base.BaseModel):
    """List of UK establishment companies.

    This model represents the top-level response from the UK establishments
    API endpoint, containing pagination information and a list of establishment
    companies.
    """

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The ETag of the resource.",
            default=None,
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["ukestablishment-companies", "related-companies"] | None,
        pydantic.Field(
            description="UK Establishment companies.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="UK Establishment Resources related to this company.",
        ),
    ]

    items: typing.Annotated[
        typing.Sequence[CompanyEstablishmentDetails],
        pydantic.Field(
            description="List of UK Establishment companies.",
        ),
    ]
