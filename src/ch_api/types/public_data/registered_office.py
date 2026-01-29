"""Registered office address models for Companies House API.

This module contains Pydantic models for the registered office address endpoint,
which provides the official address at which a company is registered.

API Endpoint
-----
GET /company/{company_number}/registered-office-address

Returns the registered office address for the specified company.

Registered Office Address
-----
The registered office is the official address where a company is registered
at Companies House. This is the address where:
- Official documents are delivered
- Statutory notices are served
- The company records are kept

Each company must have a registered office address. The address format includes:
- Address lines (1 and 2)
- Locality/City
- Postal code
- Country
- Region (for Northern Ireland)
- Postal address (if different)
- Previous addresses (historical data)

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/companyAddress.json

Models in this Module
-----
- :class:`RegisteredOfficeAddress` - The registered office address
- :class:`Address` - Address structure with components
- And other supporting address models

Example Usage
-----
Fetch registered office address::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    address = await client.registered_office_address("09370755")
    print(f"Address: {address.address_line_1}")
    print(f"City: {address.locality}")
    print(f"Postcode: {address.postal_code}")

See Also
--------
ch_api.Client.registered_office_address : Fetch registered office address
ch_api.types.public_data.company_profile : Company profile information
"""

import typing

import pydantic

from .. import base, field_types, shared


class RegisteredOfficeAddress(base.BaseModel):
    """Registered office address for a company.

    This model represents the registered office address of a company,
    including all required and optional address fields.
    """

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The ETag of the resource.",
            default=None,
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["registered-office-address"] | None,
        pydantic.Field(
            description="The type of resource.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="Links to the related resources",
            default=None,
        ),
    ]

    premises: typing.Annotated[
        field_types.UndocumentedNullable[str],
        pydantic.Field(
            description="The property name or number.",
            default=None,
        ),
    ]

    address_line_1: typing.Annotated[
        str,
        pydantic.Field(description="The first line of the address."),
    ]

    address_line_2: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The second line of the address.",
            default=None,
        ),
    ]

    locality: typing.Annotated[
        str,
        pydantic.Field(description="The locality e.g London."),
    ]

    region: typing.Annotated[
        str | None,
        pydantic.Field(description="The region e.g Surrey.", default=None),
    ]

    postal_code: typing.Annotated[
        str,
        pydantic.Field(description="The postal code e.g CF14 3UZ."),
    ]

    country: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "England",
            "Wales",
            "Scotland",
            "Northern Ireland",
            "Great Britain",
            "United Kingdom",
            "Not specified",
        ),
        pydantic.Field(description="The country."),
    ]

    accept_appropriate_office_address_statement: typing.Annotated[
        field_types.UndocumentedNullable[bool],
        pydantic.Field(
            description=(
                "Setting this to true confirms that the new registered office "
                "address is an appropriate address as outlined in section 86(2) "
                "of the Companies Act 2006."
            ),
            default=None,
        ),
    ]


class RegisteredOfficeAddressChange(RegisteredOfficeAddress):
    """Request to change a company's registered office address.

    Inherits all fields from RegisteredOfficeAddress and adds additional
    fields required for the change request, including the reference etag
    for optimistic locking.
    """

    reference_etag: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "The latest etag read from the current ROA API resource "
                "(`/company/{company_number}/registered-office-address`) on the "
                "public register. If this reference etag does not match the "
                "current register the request will be rejected."
            )
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="Links to the related resources",
            default=None,
        ),
    ]
