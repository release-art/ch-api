"""Officer disqualification models for Companies House API.

This module contains Pydantic models for the disqualified officers endpoints,
which provide information about directors disqualified from acting as company officers.

API Endpoints
-----
GET /disqualified-officers/natural/{officer_id} - Get natural person disqualification
GET /disqualified-officers/corporate/{officer_id} - Get corporate officer disqualification

Disqualifications
-----
Disqualified officers are individuals or companies prohibited from managing
companies under the Company Directors Disqualification Act 1986. Disqualifications
may result from:
- Criminal convictions
- Fraudulent trading
- Breach of company law
- Unfitness to manage companies
- Voluntary agreements

Each disqualification record includes:
- Disqualification dates (from and to)
- Reason for disqualification
- Court case details
- Competency indicator

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/disqualifications.json

Models in this Module
-----
- :class:`NaturalDisqualification` - Disqualification for natural persons
- :class:`CorporateDisqualification` - Disqualification for corporate officers
- And other supporting models

Example Usage
-----
Fetch disqualification information for a natural person::

    >>> from ch_api import Client, api_settings
    >>> auth = api_settings.AuthSettings(api_key="your-key")
    >>> client = Client(credentials=auth)
    ...
    >>> disqualification = await client.get_natural_officer_disqualification("officer_id")
    >>> print(f"Disqualified: {disqualification.disqualified_from}")
    Disqualified: ...
    >>> print(f"Until: {disqualification.disqualified_until}")
    Until: ...

Get corporate officer disqualification::

    >>> disqualification = await client.get_corporate_officer_disqualification("officer_id")

See Also
--------
ch_api.Client.get_natural_officer_disqualification : Get natural person disqualification
ch_api.Client.get_corporate_officer_disqualification : Get corporate disqualification
ch_api.types.public_data.company_officers : Officer information
"""

import datetime
import typing

import pydantic

from .. import base, shared


class Address(base.BaseModel):
    """Address of the disqualified officer."""

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


class Reason(base.BaseModel):
    """Reason for the disqualification."""

    description_identifier: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "An enumeration type that provides the description for the reason of disqualification. "
                "For enumeration descriptions see `description_identifier` section in the "
                "[enumeration mappings](https://github.com/companieshouse/api-enumerations/blob/master/disqualified_officer_descriptions.yml)"
            ),
        ),
    ]

    act: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "An enumeration type that provides the law under which the disqualification was made. "
                "For enumeration descriptions see `act` section in the "
                "[enumeration mappings](https://github.com/companieshouse/api-enumerations/blob/master/disqualified_officer_descriptions.yml)"
            ),
        ),
    ]

    article: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The article of the act under which the disqualification was made. "
                "Only applicable if `reason.act` is `company-directors-disqualification-northern-ireland-order-2002`."
            ),
            default=None,
        ),
    ]

    section: typing.Annotated[
        str | None,
        pydantic.Field(
            description=(
                "The section of the act under which the disqualification was made. "
                "Only applicable if `reason.act` is `company-directors-disqualification-act-1986` or "
                "`sanctions-anti-money-laundering-act-2018` or `sanctions-counter-terrorism-regulations-2019`."
            ),
            default=None,
        ),
    ]


class LastVariation(base.BaseModel):
    """Latest variation made to the disqualification."""

    varied_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the variation was made against the disqualification.",
            default=None,
        ),
    ]

    case_identifier: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The case identifier of the variation.",
            default=None,
        ),
    ]

    court_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The name of the court that handled the variation case.",
            default=None,
        ),
    ]


class Disqualification(base.BaseModel):
    """Disqualification information."""

    case_identifier: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The case identifier of the disqualification.",
            default=None,
        ),
    ]

    address: typing.Annotated[
        Address,
        pydantic.Field(
            description="The address of the disqualified officer as provided by the disqualifying authority.",
        ),
    ]

    company_names: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description="The companies in which the misconduct took place.",
            default=None,
        ),
    ]

    court_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The name of the court that handled the disqualification case.",
            default=None,
        ),
    ]

    disqualification_type: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "An enumeration type that provides the disqualifying authority that handled the disqualification case. "
                "For enumeration descriptions see `disqualification_type` section in the "
                "[enumeration mappings](https://github.com/companieshouse/api-enumerations/blob/master/disqualified_officer_descriptions.yml)"
            ),
        ),
    ]

    disqualified_from: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date that the disqualification starts.",
        ),
    ]

    disqualified_until: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date that the disqualification ends.",
        ),
    ]

    heard_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the disqualification hearing was on.",
            default=None,
        ),
    ]

    undertaken_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the disqualification undertaking was agreed on.",
            default=None,
        ),
    ]

    last_variation: typing.Annotated[
        list[LastVariation] | None,
        pydantic.Field(
            description="The latest variation made to the disqualification.",
            default=None,
        ),
    ]

    reason: typing.Annotated[
        Reason,
        pydantic.Field(
            description="The reason for the disqualification.",
        ),
    ]


class PermissionToAct(base.BaseModel):
    """Permission to act that has been granted for the disqualified officer."""

    company_names: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description="The companies for which the disqualified officer has permission to act.",
            default=None,
        ),
    ]

    court_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The name of the court that granted the permission to act.",
            default=None,
        ),
    ]

    expires_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date that the permission ends.",
        ),
    ]

    granted_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date that the permission starts.",
        ),
    ]


class NaturalDisqualification(base.BaseModel):
    """Natural officer's disqualifications."""

    kind: typing.Annotated[
        typing.Literal["natural-disqualification"],
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
            description="Links to other resources associated with this officer disqualification resource.",
        ),
    ]

    surname: typing.Annotated[
        str,
        pydantic.Field(
            description="The surname of the disqualified officer.",
        ),
    ]

    forename: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The forename of the disqualified officer.",
            default=None,
        ),
    ]

    other_forenames: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The other forenames of the disqualified officer.",
            default=None,
        ),
    ]

    title: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The title of the disqualified officer.",
            default=None,
        ),
    ]

    honours: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The honours that the disqualified officer has.",
            default=None,
        ),
    ]

    nationality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The nationality of the disqualified officer.",
            default=None,
        ),
    ]

    date_of_birth: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The disqualified officer's date of birth.",
            default=None,
        ),
    ]

    disqualifications: typing.Annotated[
        list[Disqualification],
        pydantic.Field(
            description="The officer's disqualifications.",
        ),
    ]

    permissions_to_act: typing.Annotated[
        list[PermissionToAct] | None,
        pydantic.Field(
            description="Permissions to act that have been granted for the disqualified officer.",
            default=None,
        ),
    ]

    person_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The disqualified officer's person number.",
            default=None,
        ),
    ]


class CorporateDisqualification(base.BaseModel):
    """Corporate officer's disqualifications."""

    kind: typing.Annotated[
        typing.Literal["corporate-disqualification"],
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
            description="Links to other resources associated with this officer disqualification resource.",
        ),
    ]

    name: typing.Annotated[
        str,
        pydantic.Field(
            description="The name of the disqualified officer.",
        ),
    ]

    company_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The registration number of the disqualified officer.",
            default=None,
        ),
    ]

    country_of_registration: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country in which the disqualified officer was registered.",
            default=None,
        ),
    ]

    disqualifications: typing.Annotated[
        list[Disqualification],
        pydantic.Field(
            description="The officer's disqualifications.",
        ),
    ]

    permissions_to_act: typing.Annotated[
        list[PermissionToAct] | None,
        pydantic.Field(
            description="Permissions that the disqualified officer has to act outside of their disqualification.",
            default=None,
        ),
    ]

    person_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The disqualified officer's person number.",
            default=None,
        ),
    ]
