"""Search result models for Companies House API.

This module contains Pydantic models representing search results from the
Companies House API search endpoints, including searches for companies,
officers, and disqualified officers.

API Endpoints
-----
- GET /search - Search across all types (companies and officers)
- GET /search/companies - Search companies only
- GET /search/officers - Search officers only
- GET /search/disqualified-officers - Search disqualified officers

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/search.json

Models in this Module
-----
- :class:`CompanySearchItem` - Company search result
- :class:`OfficerSearchItem` - Officer search result
- :class:`DisqualifiedOfficerSearchItem` - Disqualified officer search result
- :class:`AnySearchResultT` - Union type for any search result
- :class:`RegisteredOfficeAddress` - Registered office address from search
- :class:`MatchesModel` - Character offsets of search term matches

Search Results
-----
Each search returns a paginated list of results with:
- Matched titles and snippets
- Character offsets showing where search terms matched
- Links to full detailed records
- Address information (for companies)
- Highlighted matches for display in UI

Match Highlighting
-----
The ``matches`` field contains character offsets (1-indexed) that mark where
the search terms appear in the title and snippet. Use these offsets to
highlight matching text in your user interface::

    matches = result.matches
    # matches.title = [0, 5, 15, 20]  # Pairs of start, end positions
    # Use these to highlight result.title[0:5] and result.title[15:20]

Example Usage
-----
Search for companies::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    # Simple search
    results = await client.search_companies("Apple")
    async for company in results:
        print(f"{company.title} ({company.company_number})")

    # Search all types
    results = await client.search("Barclays")
    async for result in results:
        print(f"{result.title}")

    # Search officers
    officers = await client.search_officers("Smith")
    async for officer in officers:
        print(f"{officer.title}")

Pagination
-----
Search results are automatically paginated. The client handles pagination
transparently through the :class:`ch_api.types.pagination.paginated_list.MultipageList` interface.

See Also
--------
ch_api.Client.search : Generic search
ch_api.Client.search_companies : Company search
ch_api.Client.search_officers : Officer search
ch_api.Client.search_disqualified_officers : Disqualified officer search
ch_api.types.pagination.paginated_list.MultipageList : Paginated results container

References
----------
- https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
- https://github.com/companieshouse/api-enumerations
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared


class MatchesModel(base.BaseModel):
    """Character offsets defining substrings that matched the search terms."""

    title: typing.Annotated[
        list[int] | None,
        pydantic.Field(
            description=(
                "An array of character offset into the `title` string. These always occur in pairs "
                "and define the start and end of substrings in the member `title` that matched the "
                "search terms. The first character of the string is index 1."
            ),
            default=None,
        ),
    ]

    snippet: typing.Annotated[
        list[int] | None,
        pydantic.Field(
            description=(
                "An array of character offset into the `snippet` string. These always occur in pairs "
                "and define the start and end of substrings in the member `snippet` that matched the "
                "search terms. The first character of the string is index 1."
            ),
            default=None,
        ),
    ]

    address_snippet: typing.Annotated[
        list[int] | None,
        pydantic.Field(
            description=(
                "An array of character offset into the `address_snippet` string. These always occur "
                "in pairs and define the start and end of substrings in the member `address_snippet` "
                "that matched the search terms."
            ),
            default=None,
        ),
    ]


class RegisteredOfficeAddress(base.BaseModel):
    """Registered office address for search results."""

    address_line_1: typing.Annotated[
        field_types.UndocumentedNullable[str],
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

    country: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "Wales",
            "England",
            "Scotland",
            "Great Britain",
            "Not specified",
            "United Kingdom",
            "Northern Ireland",
            "United States",
        ),
        pydantic.Field(
            description="The country.",
            default=None,
        ),
    ]

    locality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The locality e.g London.",
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
            description="The postal code e.g CF14 3UZ.",
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

    region: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The region e.g Surrey.",
            default=None,
        ),
    ]


class OfficerAddress(base.BaseModel):
    """Service address of an officer."""

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
            description="The country. For example UK.",
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


class DisqualifiedOfficerAddress(base.BaseModel):
    """Address of a disqualified officer."""

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

    country: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The country. For example UK.",
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


class OfficerDateOfBirth(base.BaseModel):
    """Date of birth for an officer."""

    month: typing.Annotated[
        int,
        pydantic.Field(
            description="The month the officer was born in.",
        ),
    ]

    year: typing.Annotated[
        int,
        pydantic.Field(
            description="The year the officer was born in.",
        ),
    ]


class CompanySearchItem(base.BaseModel):
    """Company search result item."""

    kind: typing.Annotated[
        typing.Literal["searchresults#company"],
        pydantic.Field(
            description="The type of search result.",
        ),
    ]

    title: typing.Annotated[
        str,
        pydantic.Field(
            description="The title of the search result.",
        ),
    ]

    address_snippet: typing.Annotated[
        field_types.UndocumentedNullable[str],
        pydantic.Field(
            description=(
                "A single line address. This will be the address that matched within the indexed "
                "document or the primary address otherwise (as returned by the `address` member)."
            ),
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="The URL of the search result.",
        ),
    ]

    company_number: typing.Annotated[
        str,
        pydantic.Field(
            description="The company registration / incorporation number of the company.",
        ),
    ]

    date_of_creation: typing.Annotated[
        field_types.UndocumentedNullable[datetime.date],
        pydantic.Field(
            description="The date the company was created.",
            default=None,
        ),
    ]

    company_type: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "private-unlimited",
            "ltd",
            "plc",
            "old-public-company",
            "private-limited-guarant-nsc-limited-exemption",
            "limited-partnership",
            "private-limited-guarant-nsc",
            "converted-or-closed",
            "private-unlimited-nsc",
            "private-limited-shares-section-30-exemption",
            "assurance-company",
            "oversea-company",
            "eeig",
            "icvc-securities",
            "icvc-warrant",
            "icvc-umbrella",
            "industrial-and-provident-society",
            "northern-ireland",
            "northern-ireland-other",
            "royal-charter",
            "investment-company-with-variable-capital",
            "unregistered-company",
            "llp",
            "other",
            "european-public-limited-liability-company-se",
            "registered-overseas-entity",
            "scottish-charitable-incorporated-organisation",
            "charitable-incorporated-organisation",
            "registered-society-non-jurisdictional",
            "uk-establishment",
        ),
        pydantic.Field(
            description="The company type.",
        ),
    ]

    company_status: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "active",
            "dissolved",
            "liquidation",
            "receivership",
            "administration",
            "voluntary-arrangement",
            "converted-closed",
            "insolvency-proceedings",
            "registered",
            "removed",
            "open",
        ),
        pydantic.Field(
            description="The company status.",
            default=None,
        ),
    ]

    address: typing.Annotated[
        RegisteredOfficeAddress,
        pydantic.Field(
            description="The address of the company's registered office.",
        ),
    ]

    description_identifier: typing.Annotated[
        list[
            typing.Annotated[
                str,
                field_types.RelaxedLiteral(
                    "incorporated-on",
                    "registered-on",
                    "formed-on",
                    "dissolved-on",
                    "converted-closed-on",
                    "closed-on",
                    "closed",
                    "first-uk-establishment-opened-on",
                    "opened-on",
                    "voluntary-arrangement",
                    "receivership",
                    "insolvency-proceedings",
                    "liquidation",
                    "administration",
                    "registered",
                    "removed",
                    "registered-externally",
                ),
            ]
        ]
        | None,
        pydantic.Field(
            description=(
                "An array of enumeration types that make up the search description. "
                "See search_descriptions_raw.yaml in api-enumerations"
            ),
            default=None,
        ),
    ]

    date_of_cessation: typing.Annotated[
        datetime.date | typing.Literal["Unknown"] | None,
        pydantic.Field(
            description="The date the company ended.",
            default=None,
        ),
    ]

    description: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The result description.",
            default=None,
        ),
    ]

    snippet: typing.Annotated[
        str | None,
        pydantic.Field(
            description=("Summary information for the result showing additional details that have matched."),
            default=None,
        ),
    ]

    matches: typing.Annotated[
        MatchesModel | None,
        pydantic.Field(
            description=(
                "A list of members and arrays of character offset defining substrings that matched the search terms."
            ),
            default=None,
        ),
    ]


class OfficerSearchItem(base.BaseModel):
    """Officer search result item."""

    kind: typing.Annotated[
        typing.Literal["searchresults#officer"],
        pydantic.Field(
            description="Describes the type of result returned.",
        ),
    ]

    appointment_count: typing.Annotated[
        int,
        pydantic.Field(
            description="The total number of appointments the officer has.",
        ),
    ]

    description: typing.Annotated[
        str,
        pydantic.Field(
            description="The result description.",
        ),
    ]

    title: typing.Annotated[
        str,
        pydantic.Field(
            description="The title of the search result.",
        ),
    ]

    address_snippet: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "A single line address. This will be the address that matched within the indexed "
                "document or the primary address otherwise (as returned by the `address` member)."
            ),
        ),
    ]

    address: typing.Annotated[
        field_types.UndocumentedNullable[OfficerAddress],
        pydantic.Field(
            description="The service address of the officer.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="The URL of the search result.",
            default=None,
        ),
    ]

    date_of_birth: typing.Annotated[
        OfficerDateOfBirth | None,
        pydantic.Field(
            description="The officer date of birth details.",
            default=None,
        ),
    ]

    description_identifiers: typing.Annotated[
        list[typing.Annotated[str, field_types.RelaxedLiteral("appointment-count", "born-on")]] | None,
        pydantic.Field(
            description=(
                "An array of enumeration types that make up the search description. "
                "See search_descriptions_raw.yaml in api-enumerations."
            ),
            default=None,
        ),
    ]

    snippet: typing.Annotated[
        str | None,
        pydantic.Field(
            description=("Summary information for the result showing additional details that have matched."),
            default=None,
        ),
    ]

    matches: typing.Annotated[
        MatchesModel | None,
        pydantic.Field(
            description=(
                "A list of members and arrays of character offset defining substrings that matched the search terms."
            ),
            default=None,
        ),
    ]


class DisqualifiedOfficerSearchItem(base.BaseModel):
    """Disqualified officer search result item."""

    kind: typing.Annotated[
        typing.Literal["searchresults#disqualified-officer"],
        pydantic.Field(
            description="Describes the type of result returned.",
        ),
    ]

    title: typing.Annotated[
        str,
        pydantic.Field(
            description="The title of the search result.",
        ),
    ]

    description: typing.Annotated[
        str,
        pydantic.Field(
            description="The result description.",
        ),
    ]

    address: typing.Annotated[
        DisqualifiedOfficerAddress,
        pydantic.Field(
            description="The address of the disqualified officer as provided by the disqualifying authority.",
        ),
    ]

    address_snippet: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "A single line address. This will be the address that matched within the indexed "
                "document or the primary address otherwise (as returned by the `address` member)."
            ),
        ),
    ]

    date_of_birth: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The disqualified officer's date of birth.",
            default=None,
        ),
    ]

    description_identifiers: typing.Annotated[
        list[typing.Annotated[str, field_types.RelaxedLiteral("born-on")]] | None,
        pydantic.Field(
            description=(
                "An array of enumeration types that make up the search description. "
                "See search_descriptions_raw.yaml in api-enumerations."
            ),
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="The URL of the search result.",
            default=None,
        ),
    ]

    snippet: typing.Annotated[
        str | None,
        pydantic.Field(
            description=("Summary information for the result showing additional details that have matched."),
            default=None,
        ),
    ]

    matches: typing.Annotated[
        MatchesModel | None,
        pydantic.Field(
            description=(
                "A list of members and arrays of character offset defining substrings that matched the search terms."
            ),
            default=None,
        ),
    ]


AnySearchResultT = typing.Annotated[
    typing.Union[
        CompanySearchItem,
        OfficerSearchItem,
        DisqualifiedOfficerSearchItem,
    ],
    pydantic.Field(discriminator="kind"),
]
