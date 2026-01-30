"""Advanced company search models for Companies House API.

This module contains Pydantic models for advanced company search endpoints,
including advanced search, alphabetical search, and dissolved company search.

API Endpoints
-----
GET /advanced-search/companies - Advanced search with filters
GET /alphabetical-search/companies - Alphabetical search by company name
GET /dissolved-search/companies - Search for dissolved companies

Search Types
-----
The module supports multiple search strategies:

1. **Advanced Search**: Filter by multiple criteria
   - Company name (includes/excludes)
   - Company status
   - Company type and subtype
   - Incorporation and dissolution dates
   - Location/SIC codes
   - Maximum results control

2. **Alphabetical Search**: Browse by company name
   - Cursor-based pagination using company name
   - Search above/below a specific name
   - Useful for company directory listings

3. **Dissolved Company Search**: Find historical companies
   - Search by company name
   - Filter by previous names
   - Best-match or alphabetical ordering

Advanced Search Parameters
-----
Detailed filters available:
- ``company_name_includes`` - Company name must contain
- ``company_name_excludes`` - Exclude companies with name containing
- ``company_status`` - Active, dissolved, liquidation, administration
- ``company_type`` - Private, public, LLP, etc.
- ``dissolved_from``/``dissolved_to`` - Dissolution date range
- ``incorporated_from``/``incorporated_to`` - Incorporation date range
- ``location`` - Geographic filter
- ``sic_codes`` - Standard Industry Classification codes
- ``max_results`` - Limit result count (1-5000)

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/search-companies.json

Models in this Module
-----
- :class:`AdvancedSearchResult` - Advanced search results container
- :class:`AdvancedCompany` - Individual company result from advanced search
- :class:`AlphabeticalCompanySearchResult` - Alphabetical search results
- :class:`AlphabeticalCompany` - Company result from alphabetical search
- :class:`DissolvedCompany` - Result from dissolved company search
- :class:`GenericSearchResult` - Generic paginated search result container
- And other supporting models

Search Result Structure
-----
Each search type returns results with:
- Company number
- Company name
- Company status
- Incorporation date
- Dissolution date (if applicable)
- Registered office address
- Links to full company profile
- Match highlights for display

Pagination
-----
All searches are paginated. Use the client's search methods which handle
pagination automatically through MultipageList interface.

Example Usage
-----
Advanced company search::

    >>> async def search_companies_example(client):
    ...     results = await client.advanced_company_search(
    ...         company_name_includes="Apple"
    ...     )
    ...     return len(results.items) if results.items else 0
    >>> count = await run_async_func(search_companies_example)  # doctest: +SKIP

Alphabetical search::

    >>> async def alphabetical_search_example(client):
    ...     results = await client.alphabetical_companies_search("BBC")
    ...     count = 0
    ...     async for company in results:
    ...         count += 1
    ...         if count >= 1:
    ...             break
    ...     return count
    >>> count = await run_async_func(alphabetical_search_example)  # doctest: +SKIP

Dissolved company search::

    >>> async def dissolved_search_example(client):
    ...     dissolved = await client.search_dissolved_companies("Enron")
    ...     count = 0
    ...     async for company in dissolved:
    ...         count += 1
    ...         if count >= 1:
    ...             break
    ...     return count
    >>> count = await run_async_func(dissolved_search_example)  # doctest: +SKIP

See Also
--------
ch_api.Client.advanced_company_search : Perform advanced search
ch_api.Client.alphabetical_companies_search : Alphabetical search
ch_api.Client.search_dissolved_companies : Dissolved company search
ch_api.types.public_data.search : Simple company search
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared

T = typing.TypeVar("T", bound=base.BaseModel)


class PreviousCompanyName(base.BaseModel):
    """Previous company name."""

    company_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The company number of the dissolved company",
            default=None,
        ),
    ]

    ceased_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date that the company ceased being known under the company name",
            default=None,
        ),
    ]

    effective_from: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date that the company started being known under the company name",
            default=None,
        ),
    ]

    name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The previous name of the company",
            default=None,
        ),
    ]


class DissolvedCompanyRegisteredOfficeAddress(base.BaseModel):
    """Registered Office Address for dissolved companies.

    This will only appear if there are ROA details in the company record.
    """

    address_line_1: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The first line of the address e.g Crown Way",
            default=None,
        ),
    ]

    address_line_2: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The second line of the address",
            default=None,
        ),
    ]

    locality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The town associated to the ROA e.g Cardiff",
            default=None,
        ),
    ]

    postal_code: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The postal code e.g CF14 3UZ",
            default=None,
        ),
    ]


class AdvancedCompanyRegisteredOfficeAddress(base.BaseModel):
    """Registered Office Address for advanced search results.

    This will only appear if there are ROA details in the company record.
    """

    address_line_1: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The first line of the address e.g Crown Way",
            default=None,
        ),
    ]

    address_line_2: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The second line of the address",
            default=None,
        ),
    ]

    locality: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The town associated to the ROA e.g Cardiff",
            default=None,
        ),
    ]

    postal_code: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The postal code e.g CF14 3UZ",
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
        ),
        pydantic.Field(
            description="The country.",
            default=None,
        ),
    ]


class DissolvedCompany(base.BaseModel):
    """Dissolved company search result."""

    company_name: typing.Annotated[
        str,
        pydantic.Field(
            description="The company name associated with the dissolved company",
        ),
    ]

    company_number: typing.Annotated[
        str,
        pydantic.Field(
            description="The company number of the dissolved company",
        ),
    ]

    date_of_cessation: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date that the company was dissolved",
        ),
    ]

    date_of_creation: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date that the company was incorporated",
        ),
    ]

    company_status: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The status of the company",
            default=None,
        ),
    ]

    ordered_alpha_key_with_id: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The alphakey with it's id associated with the dissolved company",
            default=None,
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["search-results#dissolved-company", "searchresults#dissolved-company"],
        pydantic.Field(
            description="The type of search result",
        ),
    ]

    registered_office_address: typing.Annotated[
        DissolvedCompanyRegisteredOfficeAddress | None,
        pydantic.Field(
            default=None,
        ),
    ]

    previous_company_names: typing.Annotated[
        list[PreviousCompanyName] | None,
        pydantic.Field(
            default=None,
        ),
    ]

    matched_previous_company_name: typing.Annotated[
        PreviousCompanyName | None,
        pydantic.Field(
            default=None,
        ),
    ]


class AlphabeticalCompany(base.BaseModel):
    """Alphabetical company search result."""

    company_name: typing.Annotated[
        str,
        pydantic.Field(
            description="The company name associated with the company",
        ),
    ]

    company_number: typing.Annotated[
        str,
        pydantic.Field(
            description="The company number of the company",
        ),
    ]

    company_status: typing.Annotated[
        str,
        pydantic.Field(
            description="The status of the company",
        ),
    ]

    company_type: typing.Annotated[
        str,
        pydantic.Field(
            description="The type of company associated with the company",
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="The link to the company",
        ),
    ]

    ordered_alpha_key_with_id: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The alphakey with it's id associated with the company",
            default=None,
        ),
    ]

    kind: typing.Annotated[
        typing.Literal[
            "search-results#alphabetical-search",
            "search-results#company",
            "searchresults#alphabetical-search",
            "searchresults#company",
        ],
        pydantic.Field(
            description="The type of search result",
            default=None,
        ),
    ]


class AdvancedCompany(base.BaseModel):
    """Advanced company search result."""

    company_name: typing.Annotated[
        str,
        pydantic.Field(
            description="The company name associated with the company",
        ),
    ]

    company_number: typing.Annotated[
        str,
        pydantic.Field(
            description="The company number of the company",
        ),
    ]

    company_status: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "active",
            "dissolved",
            "open",
            "closed",
            "converted-closed",
            "receivership",
            "administration",
            "liquidation",
            "insolvency-proceedings",
            "voluntary-arrangement",
            "registered",
            "removed",
        ),
        pydantic.Field(
            description=(
                "The status of the company. "
                "For enumeration descriptions see `company_status` section in the enumeration mappings."
            ),
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
            "protected-cell-company",
            "assurance-company",
            "oversea-company",
            "eeig",
            "icvc-securities",
            "icvc-warrant",
            "icvc-umbrella",
            "registered-society-non-jurisdictional",
            "industrial-and-provident-society",
            "northern-ireland",
            "northern-ireland-other",
            "royal-charter",
            "investment-company-with-variable-capital",
            "unregistered-company",
            "llp",
            "other",
            "european-public-limited-liability-company-se",
            "uk-establishment",
            "scottish-partnership",
            "charitable-incorporated-organisation",
            "scottish-charitable-incorporated-organisation",
            "further-education-or-sixth-form-college-corporation",
            "registered-overseas-entity",
        ),
        pydantic.Field(
            description=(
                "The type of the company. "
                "For enumeration descriptions see `company_type` section in the enumeration mappings."
            ),
        ),
    ]

    date_of_creation: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date that the company was incorporated",
        ),
    ]

    kind: typing.Annotated[
        typing.Literal["search-results#company"],
        pydantic.Field(
            description="The type of search result",
        ),
    ]

    company_subtype: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "community-interest-company",
            "private-fund-limited-partnership",
        ),
        pydantic.Field(
            description=(
                "The subtype of the company. "
                "For enumeration descriptions see `company_subtype` section in the enumeration mappings."
            ),
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="The link to the company",
            default=None,
        ),
    ]

    date_of_cessation: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date that the company was dissolved",
            default=None,
        ),
    ]

    registered_office_address: typing.Annotated[
        AdvancedCompanyRegisteredOfficeAddress | None,
        pydantic.Field(
            default=None,
        ),
    ]

    sic_codes: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description="SIC codes for this company",
            default=None,
        ),
    ]


# class DissolvedCompanySearch(base.BaseModel):
#     """List of dissolved companies."""

#     etag: typing.Annotated[
#         str | None,
#         pydantic.Field(
#             default=None,
#         ),
#     ]

#     items: typing.Annotated[
#         list[DissolvedCompany] | None,
#         pydantic.Field(
#             default=None,
#         ),
#     ]

#     kind: typing.Annotated[
#         typing.Literal[
#             "search#alphabetical-dissolved",
#             "search#dissolved",
#             "search#previous-name-dissolved",
#         ]
#         | None,
#         pydantic.Field(
#             default=None,
#         ),
#     ]

#     top_hit: typing.Annotated[
#         DissolvedCompany | None,
#         pydantic.Field(
#             description="The best matching company in dissolved search results",
#             default=None,
#         ),
#     ]

#     hits: typing.Annotated[
#         str | None,
#         pydantic.Field(
#             description="The number of hits returned on a best-match or previous-company-names search",
#             default=None,
#         ),
#     ]


class AlphabeticalCompanySearchResult(base.BaseModel, typing.Generic[T]):
    """List of companies from alphabetical search."""

    items: typing.Annotated[
        list[T] | None,
        pydantic.Field(
            default=None,
        ),
    ]

    kind: typing.Annotated[
        typing.Literal[
            "search#alphabetical-search",
            "search#enhanced-search",
            "search#alphabetical-dissolved",
            "search#dissolved",
            "search#previous-name-dissolved",
        ]
        | None,
        pydantic.Field(
            default=None,
        ),
    ]

    top_hit: typing.Annotated[
        T | None,
        pydantic.Field(
            description="The best matching company in alphabetical search results",
            default=None,
        ),
    ]


class GenericSearchResult(base.BaseModel, typing.Generic[T]):
    """Disqualified officer search results."""

    kind: typing.Annotated[
        typing.Literal[
            "officer-list", "search#all", "search#companies", "search#officers", "search#disqualified-officers"
        ],
        pydantic.Field(
            description="The type of response returned.",
        ),
    ]

    total_results: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of further search results available for the current search.",
        ),
    ]

    start_index: typing.Annotated[
        int,
        pydantic.Field(
            description="The index into the entire result set that this result page starts.",
        ),
    ]

    items_per_page: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of search items returned per page.",
        ),
    ]

    items: typing.Annotated[
        list[T] | None,
        pydantic.Field(
            description="The results of the completed search.",
            default=None,
        ),
    ]

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The ETag of the resource",
            default=None,
        ),
    ]


class AdvancedSearchResult(base.BaseModel, typing.Generic[T]):
    """Disqualified officer search results."""

    kind: typing.Annotated[
        typing.Literal["search#advanced-search"],
        pydantic.Field(
            description="The type of response returned.",
        ),
    ]

    items: typing.Annotated[
        list[T] | None,
        pydantic.Field(
            description="The results of the completed search.",
            default=None,
        ),
    ]

    hits: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of matches found using advanced search",
        ),
    ]

    top_hit: typing.Annotated[
        T | None,
        pydantic.Field(
            description="The best matching item in the search results",
            default=None,
        ),
    ]

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The ETag of the resource",
            default=None,
        ),
    ]
