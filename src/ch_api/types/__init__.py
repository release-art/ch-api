"""Type definitions for Companies House API responses.

This package contains all Pydantic models representing Companies House API
response structures. Models are organized by API endpoint and data category.

Module Organization
-----
- :mod:`base` - Base model with common configurations
- :mod:`field_types` - Custom Pydantic field types
- :mod:`shared` - Shared types used across multiple models
- :mod:`settings` - Global type configuration
- :mod:`public_data` - Models for public data endpoints
- :mod:`compound_api_types` - Complex wrapper types
- :mod:`pagination` - Pagination support types
- :mod:`test_data_generator` - Test data generator models

Public Data Endpoints
-----
All Companies House API endpoints are represented in the ``public_data`` package:

**Company Information**
- :mod:`public_data.company_profile` - Company profiles
- :mod:`public_data.registered_office` - Registered office address

**Officers & Management**
- :mod:`public_data.company_officers` - Officers and directors
- :mod:`public_data.officer_appointments` - Officer appointment details
- :mod:`public_data.officer_changes` - Officer change history

**Ownership & Control**
- :mod:`public_data.psc` - Persons with Significant Control

**Financial & Legal**
- :mod:`public_data.charges` - Charges over assets
- :mod:`public_data.filing_history` - Filing history and documents
- :mod:`public_data.exemptions` - Exemptions from filing
- :mod:`public_data.insolvency` - Insolvency information

**Searches**
- :mod:`public_data.search` - General search results
- :mod:`public_data.search_companies` - Advanced company search

**Other**
- :mod:`public_data.company_registers` - Registers held at Companies House
- :mod:`public_data.disqualifications` - Officer disqualifications
- :mod:`public_data.uk_establishments` - UK branches of overseas companies

Pagination
-----
Search and list endpoints return paginated results via:
- :mod:`pagination.paginated_list` - MultipageList for lazy-loaded results
- :mod:`pagination.types` - Pagination type definitions

Custom Field Types
-----
Special field types for API data:
- :class:`field_types.UndocumentedNullable` - Fields that may be null unexpectedly
- :class:`field_types.RelaxedLiteral` - Enumeration values with forward compatibility

Example Usage
-----
Access API response types::

    from ch_api import types

    # Company profile
    profile: types.public_data.company_profile.CompanyProfile

    # Officers
    officers: types.public_data.company_officers.OfficerSummary

    # Search results
    results: types.pagination.paginated_list.MultipageList[
        types.public_data.search.CompanySearchItem
    ]

See Also
--------
ch_api.Client : API client using these types
ch_api.api_settings : Settings for API communication
https://developer-specs.company-information.service.gov.uk/ : API documentation
"""

from . import (
    base,
    compound_api_types,
    field_types,
    pagination,
    public_data,
    settings,
    shared,
    test_data_generator,
)
