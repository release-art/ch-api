"""Public data models for the Companies House API.

This package contains Pydantic models for all public data returned by the
Companies House API, organized by API endpoint and data category.

API Endpoints
-----
The Companies House API provides read-only access to public company information
through numerous endpoints:

- **Company Information**: Profile, status, registered address
- **Officers & Management**: Officers, appointments, officer changes
- **Ownership & Control**: Persons with Significant Control (PSC), statements
- **Financial**: Charges, exemptions, insolvency information
- **Documents**: Filing history
- **Search**: Full-text search across company names, officers, etc.
- **Registers**: Registers held at Companies House
- **Overseas**: UK establishments for overseas companies

Module Organization
-----
Each module corresponds to a Companies House API endpoint:

- :mod:`company_profile` - Company profiles and status information
- :mod:`company_officers` - Officers and director information
- :mod:`officer_appointments` - Detailed officer appointment records
- :mod:`officer_changes` - Historical officer changes
- :mod:`psc` - Persons with Significant Control data
- :mod:`charges` - Charges over company assets
- :mod:`filing_history` - Historical filings and documents
- :mod:`insolvency` - Insolvency and administration data
- :mod:`exemptions` - Exemptions from filing requirements
- :mod:`disqualifications` - Officer disqualifications
- :mod:`company_registers` - Registers held at Companies House
- :mod:`registered_office` - Registered office address
- :mod:`uk_establishments` - UK branches of overseas companies
- :mod:`search` - Search results (companies, officers, disqualified officers)
- :mod:`search_companies` - Advanced company search results

API Documentation
-----
Full API documentation and schema specifications are available at:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/swagger.json

Rate Limiting
-----
The Companies House API enforces rate limits. See developer guidelines for details:
    https://developer-specs.company-information.service.gov.uk/guides/rateLimiting

Enumeration Types
-----
Many API fields use enumeration types (standardized values). The complete mapping
of enumeration values is available on GitHub:
    https://github.com/companieshouse/api-enumerations

See Also
--------
ch_api.Client : The main API client for querying these endpoints
ch_api.types : All type definitions
"""

"""Pydantic models for all Companies House API public data endpoints.

This package contains data models for every endpoint in the Companies House API,
organized by functional category. All models use Pydantic for validation and
inherit from the base model with common configurations.

Endpoint Categories
-------------------

**Company Information**
- :mod:`company_profile` - Company profiles and status
- :mod:`registered_office` - Registered office addresses
- :mod:`company_registers` - Registers held at Companies House

**Officers & Management**
- :mod:`company_officers` - Officers and directors
- :mod:`officer_appointments` - Officer appointment details
- :mod:`officer_changes` - Officer change history

**Ownership & Control**
- :mod:`psc` - Persons with Significant Control (PSC)

**Financial & Legal Documents**
- :mod:`charges` - Charges over company assets
- :mod:`filing_history` - Filing history and documents
- :mod:`exemptions` - Exemptions from filing requirements
- :mod:`insolvency` - Insolvency proceedings

**Search Results**
- :mod:`search` - General search results (companies & officers)
- :mod:`search_companies` - Advanced search, alphabetical search, dissolved search

**Other**
- :mod:`disqualifications` - Officer disqualifications
- :mod:`uk_establishments` - UK branches of overseas companies

Model Organization
-------------------
Each module contains:
- Main container model (e.g., ``CompanyProfile``, ``ChargeList``)
- Component models used by the container
- Shared types (dates, links, addresses, etc.)

Example
-------
Access models for a specific endpoint::

    from ch_api import types

    # Company profile models
    profile: types.public_data.company_profile.CompanyProfile
    accounts: types.public_data.company_profile.Accounts

    # Officer models
    officer: types.public_data.company_officers.OfficerSummary
    changes: types.public_data.officer_changes.Officer

    # Search results
    result: types.public_data.search.CompanySearchItem

API Response Structure
---------------------
Typical API responses are structured as:

1. **Container model**: Root response object
2. **Item models**: Individual records (officers, charges, etc.)
3. **Component models**: Shared structures (addresses, dates, links)
4. **Links section**: Related resource URLs

Type Validation
---------------
All models perform automatic validation:
- Field name normalization (lowercase, whitespace trimmed)
- Type validation and coercion
- Deprecated field filtering
- Optional field handling

Configuration
--------------
Models are configured via ``model_config`` to:
- Allow or ignore extra fields (see :mod:`settings`)
- Inherit from BaseModel for common behavior
- Support field aliases and validation

Advanced Features
------------------
- **Relaxed Literals**: Enumeration fields accept new values with warnings
- **Undocumented Nullables**: Fields marked as sometimes null
- **Custom Validators**: Per-field validation logic
- **Links**: Automatic linking to related resources

See Also
--------
:mod:`base` : Base model configuration
:mod:`field_types` : Custom field types
:mod:`shared` : Shared component types
:mod:`settings` : Global configuration

Documentation
--------------
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/swagger.json
"""

from . import (
    charges,
    company_officers,
    company_profile,
    company_registers,
    disqualifications,
    exemptions,
    filing_history,
    insolvency,
    officer_appointments,
    officer_changes,
    psc,
    registered_office,
    search,
    search_companies,
    uk_establishments,
)
