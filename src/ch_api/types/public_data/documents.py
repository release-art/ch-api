"""Document API models for Companies House.

This module contains Pydantic models for the Companies House Document API,
which provides access to document metadata and download URLs for filed documents.

The Document API runs on a separate host from the main Companies House API:
    ``document-api.company-information.service.gov.uk``

API Endpoints
-----
GET /document/{document_id}         - Fetch document metadata
GET /document/{document_id}/content - Fetch document (returns redirect to download URL)

Document Resources
-----
Each document may be available in multiple formats. The ``resources`` field
maps MIME type strings to :class:`ResourceContent` objects describing each format:

- ``application/pdf`` - PDF document
- ``application/json`` - Machine-readable JSON
- ``application/xml`` - XML format
- ``application/xhtml+xml`` - XHTML format
- ``application/zip`` - ZIP archive
- ``text/csv`` - CSV data

Not all content types are available for all documents. Inspect ``resources``
to determine which types are available before requesting document content.

Fetching a document
-----
1. Call :meth:`~ch_api.Client.get_document_metadata` to retrieve metadata and
   inspect ``resources`` for available content types.
2. Call :meth:`~ch_api.Client.get_document_url` with the desired MIME type to
   obtain a pre-signed download URL (valid for a short time).
3. Fetch the URL directly with any HTTP client.

Documentation
-----
https://developer-specs.company-information.service.gov.uk/document-api.company-information.service.gov.uk-specifications/swagger-2.0/spec/swagger.json
"""

import datetime
import typing

import pydantic

from .. import base, shared


class ResourceContent(base.BaseModel):
    """Metadata for a single document format / content type.

    Describes the size and optional timestamps for one available representation
    of a document (e.g. the PDF version or the JSON version).
    """

    content_length: typing.Annotated[
        int,
        pydantic.Field(
            description="The size of the document in bytes when returned as this content type.",
        ),
    ]

    created_at: typing.Annotated[
        datetime.datetime | None,
        pydantic.Field(
            default=None,
            description="The date and time this content type was first created.",
        ),
    ]

    updated_at: typing.Annotated[
        datetime.datetime | None,
        pydantic.Field(
            default=None,
            description="The date and time this content type was last updated.",
        ),
    ]


class DocumentLinks(shared.LinksSection):
    """Links associated with a document metadata response.

    Inherits ``self`` (and any other arbitrary links) from
    :class:`~ch_api.types.shared.LinksSection`.  The ``document`` field is
    declared explicitly so IDEs and type checkers can see it.
    """

    document: typing.Annotated[
        str | None,
        pydantic.Field(
            default=None,
            description="Link to the document content endpoint.",
        ),
    ]


class DocumentMetadata(base.BaseModel):
    """Metadata for a filed document returned by the Companies House Document API.

    Returned by :meth:`~ch_api.Client.get_document_metadata`.  Use the
    ``resources`` mapping to discover which content types are available, then
    pass the desired MIME type to :meth:`~ch_api.Client.get_document_url`.

    Example
    -------
    Check which formats a document is available in::

        meta = await client.get_document_metadata("L_X0y9bwYnkyEMwLe3TNQUfmBpMG0FIj0tLzr5b5s2o")
        if meta:
            print(meta.company_number, meta.pages)
            for mime_type, resource in (meta.resources or {}).items():
                print(f"  {mime_type}: {resource.content_length} bytes")
    """

    etag: typing.Annotated[
        str,
        pydantic.Field(
            description="The ETag of the resource.",
        ),
    ]

    id: typing.Annotated[
        str | None,
        pydantic.Field(
            default=None,
            description="The document ID (not always returned by the API).",
        ),
    ]

    company_number: typing.Annotated[
        str,
        pydantic.Field(
            description="The company number the document belongs to.",
        ),
    ]

    created_at: typing.Annotated[
        datetime.datetime,
        pydantic.Field(
            description="The date and time the document was first created.",
        ),
    ]

    updated_at: typing.Annotated[
        datetime.datetime | None,
        pydantic.Field(
            default=None,
            description="The date and time the document was last updated.",
        ),
    ]

    pages: typing.Annotated[
        int | None,
        pydantic.Field(
            default=None,
            description="The document page count.",
        ),
    ]

    barcode: typing.Annotated[
        str | None,
        pydantic.Field(
            default=None,
            description="The barcode identifier for this document.",
        ),
    ]

    filename: typing.Annotated[
        str | None,
        pydantic.Field(
            default=None,
            description="The filename of this document.",
        ),
    ]

    category: typing.Annotated[
        str | None,
        pydantic.Field(
            default=None,
            description="The filing category this document belongs to (e.g. 'annual-returns').",
        ),
    ]

    significant_date: typing.Annotated[
        datetime.datetime | None,
        pydantic.Field(
            default=None,
            description="A significant date associated with this document, if applicable.",
        ),
    ]

    significant_date_type: typing.Annotated[
        str | None,
        pydantic.Field(
            default=None,
            description="The type of significant date.",
        ),
    ]

    links: typing.Annotated[
        DocumentLinks | None,
        pydantic.Field(
            default=None,
            description=(
                "Links to other resources associated with this document. "
                "Typically includes ``self`` (metadata URL) and ``document`` (content URL)."
            ),
        ),
    ]

    resources: typing.Annotated[
        dict[str, ResourceContent] | None,
        pydantic.Field(
            default=None,
            description=(
                "Available content types for this document, keyed by MIME type. "
                "Common types: application/pdf, application/json, application/xml, "
                "application/xhtml+xml, application/zip, text/csv."
            ),
        ),
    ]
