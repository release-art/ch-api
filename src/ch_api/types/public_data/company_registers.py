"""Company registers models for Companies House API.

This module contains Pydantic models for the company registers endpoint,
which provides information about registers held at Companies House.

API Endpoint
-----
GET /company/{company_number}/registers

Returns information about registers held at Companies House for the company.

Registers
-----
Companies House maintains various registers that can be held at the company's
registered office or at Companies House. These registers include:
- Directors register
- Secretary register
- Members/shareholder register
- Charges register
- PSC register (Persons with Significant Control)
- And other statutory registers

Each register record indicates:
- Whether the register is held at Companies House or company's office
- Date the register status changed
- Location where the register is held

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/companyRegisters.json

Models in this Module
-----
- :class:`CompanyRegister` - Root register container
- :class:`Register` - Individual register information
- And other supporting models

Example Usage
-----
Fetch register information::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    registers = await client.get_company_registers("09370755")
    if registers and registers.registers:
        for register in registers.registers:
            print(f"Register: {register.register_type}")

See Also
--------
ch_api.Client.get_company_registers : Fetch register information
ch_api.types.public_data.company_profile : Company profile information
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared


class LinksItems(base.BaseModel):
    """Links for registered items."""

    filing: typing.Annotated[
        str,
        pydantic.Field(
            description="The URL of the transaction for the resource.",
        ),
    ]


class LinksDirectorsRegister(base.BaseModel):
    """Links for directors register."""

    directors_register: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The URL for the resource.",
            default=None,
        ),
    ]


class LinksSecretaryRegister(base.BaseModel):
    """Links for secretary register."""

    secretaries_register: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The URL for the resource.",
            default=None,
        ),
    ]


class LinksPersonsWithSignificantControlRegister(base.BaseModel):
    """Links for persons with significant control register."""

    persons_with_significant_control_register: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The URL for the resource.",
            default=None,
        ),
    ]


class LinksListUsualResidentialAddress(base.BaseModel):
    """Links for usual residential address register."""

    usual_residential_address: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The URL for the resource.",
            default=None,
        ),
    ]


class LinksListLLPUsualResidentialAddress(base.BaseModel):
    """Links for LLP usual residential address register."""

    llp_usual_residential_address: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The URL for the resource.",
            default=None,
        ),
    ]


class LinksListMembers(base.BaseModel):
    """Links for members register."""

    members: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The URL for the resource.",
            default=None,
        ),
    ]


class LinksListLLPMembers(base.BaseModel):
    """Links for LLP members register."""

    llp_members: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The URL for the resource.",
            default=None,
        ),
    ]


class RegisteredItems(base.BaseModel):
    """Registered item information."""

    moved_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date registered on",
        ),
    ]

    register_moved_to: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "public-register",
            "registered-office",
            "single-alternative-inspection-location",
            "unspecified-location",
        ),
        pydantic.Field(
            description="Location of registration",
        ),
    ]

    links: typing.Annotated[
        LinksItems,
        pydantic.Field(
            description="A set of URLs related to the resource.",
        ),
    ]


class RegisterListDirectors(base.BaseModel):
    """List of registered company directors."""

    register_type: typing.Annotated[
        str,
        field_types.RelaxedLiteral("directors"),
        pydantic.Field(
            description="The register type.",
        ),
    ]

    items: typing.Annotated[
        list[RegisteredItems],
        pydantic.Field(
            description="List of registered directors.",
        ),
    ]

    links: typing.Annotated[
        LinksDirectorsRegister | None,
        pydantic.Field(
            description="A set of URLs related to the resource.",
            default=None,
        ),
    ]


class RegisterListSecretaries(base.BaseModel):
    """List of registered company secretaries."""

    register_type: typing.Annotated[
        str,
        field_types.RelaxedLiteral("secretaries"),
        pydantic.Field(
            description="The register type.",
        ),
    ]

    items: typing.Annotated[
        list[RegisteredItems],
        pydantic.Field(
            description="List of registered secretaries.",
        ),
    ]

    links: typing.Annotated[
        LinksSecretaryRegister | None,
        pydantic.Field(
            description="A set of URLs related to the resource.",
            default=None,
        ),
    ]


class RegisterListPersonsWithSignificantControl(base.BaseModel):
    """List of registered company persons with significant control."""

    register_type: typing.Annotated[
        str,
        field_types.RelaxedLiteral("persons-with-significant-control"),
        pydantic.Field(
            description="The register type.",
        ),
    ]

    items: typing.Annotated[
        list[RegisteredItems],
        pydantic.Field(
            description="List of registered persons with significant control.",
        ),
    ]

    links: typing.Annotated[
        LinksPersonsWithSignificantControlRegister | None,
        pydantic.Field(
            description="A set of URLs related to the resource.",
            default=None,
        ),
    ]


class RegisterListUsualResidentialAddress(base.BaseModel):
    """List of register addresses."""

    register_type: typing.Annotated[
        str,
        field_types.RelaxedLiteral("usual-residential-address"),
        pydantic.Field(
            description="The register type.",
        ),
    ]

    items: typing.Annotated[
        list[RegisteredItems],
        pydantic.Field(
            description="List of registered addresses.",
        ),
    ]

    links: typing.Annotated[
        LinksListUsualResidentialAddress | None,
        pydantic.Field(
            description="A set of URLs related to the resource.",
            default=None,
        ),
    ]


class RegisterListLLPUsualResidentialAddress(base.BaseModel):
    """List of LLP register addresses."""

    register_type: typing.Annotated[
        str,
        field_types.RelaxedLiteral("llp-usual-residential-address"),
        pydantic.Field(
            description="The register type.",
        ),
    ]

    items: typing.Annotated[
        list[RegisteredItems],
        pydantic.Field(
            description="List of registered LLP addresses.",
        ),
    ]

    links: typing.Annotated[
        LinksListLLPUsualResidentialAddress | None,
        pydantic.Field(
            description="A set of URLs related to the resource.",
            default=None,
        ),
    ]


class RegisterListMembers(base.BaseModel):
    """List of registered company members."""

    register_type: typing.Annotated[
        str,
        field_types.RelaxedLiteral("members"),
        pydantic.Field(
            description="The register type.",
        ),
    ]

    items: typing.Annotated[
        list[RegisteredItems],
        pydantic.Field(
            description="List of registered members.",
        ),
    ]

    links: typing.Annotated[
        LinksListMembers | None,
        pydantic.Field(
            description="A set of URLs related to the resource.",
            default=None,
        ),
    ]


class RegisterListLLPMembers(base.BaseModel):
    """List of registered LLP members."""

    register_type: typing.Annotated[
        str,
        field_types.RelaxedLiteral("llp_members"),
        pydantic.Field(
            description="The register type.",
        ),
    ]

    items: typing.Annotated[
        list[RegisteredItems],
        pydantic.Field(
            description="List of registered LLP members.",
        ),
    ]

    links: typing.Annotated[
        LinksListLLPMembers | None,
        pydantic.Field(
            description="A set of URLs related to the resource.",
            default=None,
        ),
    ]


class Registers(base.BaseModel):
    """Registered company information."""

    directors: typing.Annotated[
        RegisterListDirectors | None,
        pydantic.Field(
            description="List of registered company directors.",
            default=None,
        ),
    ]

    secretaries: typing.Annotated[
        RegisterListSecretaries | None,
        pydantic.Field(
            description="List of registered company secretaries.",
            default=None,
        ),
    ]

    persons_with_significant_control: typing.Annotated[
        RegisterListPersonsWithSignificantControl | None,
        pydantic.Field(
            description="List of registered company persons with significant control.",
            default=None,
        ),
    ]

    usual_residential_address: typing.Annotated[
        RegisterListUsualResidentialAddress | None,
        pydantic.Field(
            description="List of register addresses.",
            default=None,
        ),
    ]

    llp_usual_residential_address: typing.Annotated[
        RegisterListLLPUsualResidentialAddress | None,
        pydantic.Field(
            description="List of register addresses.",
            default=None,
        ),
    ]

    members: typing.Annotated[
        RegisterListMembers | None,
        pydantic.Field(
            description="List of registered company members.",
            default=None,
        ),
    ]

    llp_members: typing.Annotated[
        RegisterListLLPMembers | None,
        pydantic.Field(
            description="List of registered llp members.",
            default=None,
        ),
    ]


class CompanyRegister(base.BaseModel):
    """Company registers information from Companies House."""

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="A set of URLs related to the resource, including self.",
        ),
    ]

    company_number: typing.Annotated[
        str,
        pydantic.Field(
            description="The number of the company.",
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["registers"],
        pydantic.Field(
            description="The kind of resource.",
        ),
    ]

    registers: typing.Annotated[
        Registers | None,
        pydantic.Field(
            description="company registers information.",
            default=None,
        ),
    ]

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The ETag of the resource.",
            default=None,
        ),
    ]
