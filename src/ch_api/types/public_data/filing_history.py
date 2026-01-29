"""Filing history models for Companies House API.

This module contains Pydantic models for the company filing history endpoint,
which provides a chronological record of all documents filed at Companies House
for a company.

API Endpoints
-----
GET /company/{company_number}/filing-history - List filing history
GET /company/{company_number}/filing-history/{transaction_id} - Get filing details

Filing History
-----
Filing history includes all official documents submitted to Companies House:
- Annual accounts and reports
- Confirmation statements
- Resolutions and special notices
- Officer appointments and resignations
- Address changes
- Charges and mortgage registrations
- Company name changes
- Capital alterations
- Miscellaneous company filings

Each filing record contains:
- Transaction ID and filing date
- Type of filing (categorized)
- Original description from Companies House
- Effective date of filing
- Action date (when it took effect)
- Paper/electronically filed indicator
- Links to filed documents

Filing Categories
-----
Filings are organized into categories:
- ``accounts`` - Annual accounts and financial reports
- ``address`` - Address change notices
- ``annual-return`` - Annual return filings
- ``capital`` - Capital alterations
- ``change-of-name`` - Company name changes
- ``incorporation`` - Incorporation documents
- ``liquidation`` - Liquidation documents
- ``miscellaneous`` - Other miscellaneous filings
- ``mortgage`` - Charge/mortgage registrations
- ``officers`` - Officer-related filings
- ``resolution`` - Board resolutions

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/filingHistory.json

Models in this Module
-----
- :class:`FilingHistoryList` - Paginated list of filings
- :class:`FilingHistoryItem` - Individual filing record
- :class:`Annotation` - Filing annotations
- :class:`ActionDate` - Filing action date information
- And other supporting models

Example Usage
-----
Fetch filing history for a company::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    filings = await client.get_company_filing_history("09370755")
    async for filing in filings:
        print(f"{filing.type}: {filing.date}")

Filter by filing category::

    accounts = await client.get_company_filing_history(
        "09370755",
        categories=("accounts", "annual-return")
    )

Get specific filing details::

    filing = await client.get_filing_history_item(
        "09370755",
        "filing_id_123"
    )
    print(f"Filing: {filing.description}")
    print(f"Date: {filing.date}")

See Also
--------
ch_api.Client.get_company_filing_history : Fetch filing history
ch_api.Client.get_filing_history_item : Get specific filing
ch_api.types.public_data.company_profile : Company profile information
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared


class Annotation(base.BaseModel):
    """Annotation for a filing."""

    date: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date the annotation was added.",
        ),
    ]

    description: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "A description of the annotation. "
                "For enumeration descriptions see `description` section in the enumeration mappings."
            ),
        ),
    ]

    annotation: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The annotation text.",
            default=None,
        ),
    ]


class AssociatedFiling(base.BaseModel):
    """Associated filing information."""

    date: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date the associated filing was processed.",
        ),
    ]

    description: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "A description of the associated filing. "
                "For enumeration descriptions see `description` section in the enumeration mappings."
            ),
        ),
    ]

    type: typing.Annotated[
        str,
        pydantic.Field(
            description="The type of the associated filing.",
        ),
    ]


class Resolution(base.BaseModel):
    """Resolution information for a filing."""

    category: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "miscellaneous",
            "change-of-name",
        ),
        pydantic.Field(
            description="The category of the resolution filed.",
        ),
    ]

    description: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "A description of the associated filing. "
                "For enumeration descriptions see `description` section in the enumeration mappings."
            ),
        ),
    ]

    receive_date: typing.Annotated[
        field_types.UndocumentedNullable[datetime.date],
        pydantic.Field(
            description="The date the resolution was processed.",
            default=None,
        ),
    ]

    subcategory: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "resolution",
        ),
        pydantic.Field(
            description="The sub-category of the document filed.",
        ),
    ]

    type: typing.Annotated[
        str,
        pydantic.Field(
            description="The type of the associated filing.",
        ),
    ]

    document_id: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The document id of the resolution.",
            default=None,
        ),
    ]


class FilingHistoryItem(base.BaseModel):
    """Individual filing history item."""

    transaction_id: typing.Annotated[
        str,
        pydantic.Field(
            description="The transaction ID of the filing.",
        ),
    ]

    category: typing.Annotated[
        str,
        field_types.RelaxedLiteral(
            "accounts",
            "address",
            "annual-return",
            "capital",
            "change-of-name",
            "incorporation",
            "liquidation",
            "miscellaneous",
            "mortgage",
            "officers",
            "resolution",
            "confirmation-statement",
        ),
        pydantic.Field(
            description="The category of the document filed.",
        ),
    ]

    date: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date the filing was processed.",
        ),
    ]

    description: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "A description of the filing. "
                "For enumeration descriptions see `description` section in the enumeration mappings."
            ),
        ),
    ]

    type: typing.Annotated[
        str,
        pydantic.Field(
            description="The type of filing.",
        ),
    ]

    annotations: typing.Annotated[
        list[Annotation] | None,
        pydantic.Field(
            description="Annotations for the filing",
            default=None,
        ),
    ]

    associated_filings: typing.Annotated[
        list[AssociatedFiling] | None,
        pydantic.Field(
            description="Any filings associated with the current item",
            default=None,
        ),
    ]

    barcode: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The barcode of the document.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection | None,
        pydantic.Field(
            description="Links to other resources associated with this filing history item.",
            default=None,
        ),
    ]

    pages: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Number of pages within the PDF document (links.document_metadata)",
            default=None,
        ),
    ]

    paper_filed: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="If true, indicates this is a paper filing.",
            default=None,
        ),
    ]

    resolutions: typing.Annotated[
        list[Resolution] | None,
        pydantic.Field(
            description="Resolutions for the filing",
            default=None,
        ),
    ]

    subcategory: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "resolution",
            "certificate",
        ),
        pydantic.Field(
            description="The sub-category of the document filed.",
            default=None,
        ),
    ]


class FilingHistoryList(base.BaseModel):
    """Filing history list for a company."""

    etag: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The ETag of the resource.",
            default=None,
        ),
    ]

    items: typing.Annotated[
        list[FilingHistoryItem],
        pydantic.Field(
            description="The filing history items.",
        ),
    ]

    items_per_page: typing.Annotated[
        int,
        pydantic.Field(
            description="The number of filing history items returned per page.",
        ),
    ]

    kind: typing.Annotated[
        field_types.UndocumentedNullable[typing.Literal["filing-history"]],
        pydantic.Field(
            description="Indicates this resource is a filing history.",
            default=None,
        ),
    ]

    start_index: typing.Annotated[
        int,
        pydantic.Field(
            description="The index into the entire result set that this result page starts.",
        ),
    ]

    total_count: typing.Annotated[
        int,
        pydantic.Field(
            description="The total number of filing history items for this company.",
        ),
    ]

    filing_history_status: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "filing-history-available",
        ),
        pydantic.Field(
            description="The status of this filing history.",
            default=None,
        ),
    ]
