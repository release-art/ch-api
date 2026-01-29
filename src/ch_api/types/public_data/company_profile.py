"""Company profile and status models for Companies House API.

This module contains Pydantic models for the company profile endpoint,
which provides comprehensive information about UK limited companies including
registration details, financial information, company status, and exemptions.

API Endpoint
-----
GET /company/{company_number}

Returns detailed company profile information for the specified company number.

Documentation
-----
Full API documentation:
    https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-\
specifications/swagger-2.0/spec/companyProfile.json

Reference Guide:
    https://developer-specs.company-information.service.gov.uk/guides/\
gettingStarted

Models in this Module
-----
- :class:`CompanyProfile` - Complete company profile with all details
- :class:`AccountingReferenceDate` - Accounting reference date (ARD) information
- :class:`LastAccounts` - Details of the last filed company accounts
- :class:`NextAccounts` - Due date for next accounts filing
- :class:`Accounts` - Financial filing information container
- :class:`AnnualReturnLastMadeUpTo` - Last annual return filing date
- :class:`ConfirmationStatement` - Confirmation statement filing information
- :class:`PartialDataUnavailableAnnualReturn` - Partial data indicator for annual return
- :class:`PartialDataUnavailableConfirmationStatement` - Partial data indicator for CS
- And other supporting models

Company Status
-----
The ``company_status`` field uses standardized enumeration values:
    - ``active`` - Company is operating normally
    - ``dissolved`` - Company has been dissolved
    - ``liquidation`` - Company is in liquidation
    - ``administration`` - Company is in administration
    - ``insolvency-proceedings`` - Company involved in insolvency proceedings

See enumeration mappings:
    https://github.com/companieshouse/api-enumerations

Example Usage
-----
Fetch a company profile::

    from ch_api import Client, api_settings

    auth = api_settings.AuthSettings(api_key="your-key")
    client = Client(credentials=auth)

    profile = await client.get_company_profile("09370755")
    print(f"Company: {profile.company_name}")
    print(f"Status: {profile.company_status}")
    print(f"Incorporation: {profile.date_of_creation}")

See Also
--------
ch_api.Client.get_company_profile : Fetch company profile
ch_api.Client.registered_office_address : Get registered address
ch_api.types.public_data.search : Search for companies
"""

import datetime
import typing

import pydantic

from .. import base, field_types, shared


class AccountingReferenceDate(base.BaseModel):
    """Accounting Reference Date (ARD) for a company."""

    day: typing.Annotated[
        int,
        pydantic.Field(
            description="The Accounting Reference Date (ARD) day.",
        ),
    ]

    month: typing.Annotated[
        int,
        pydantic.Field(
            description="The Accounting Reference Date (ARD) month.",
        ),
    ]


class LastAccounts(base.BaseModel):
    """The last company accounts filed."""

    made_up_to: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="Deprecated. Please use accounts.last_accounts.period_end_on",
        ),
    ]

    period_end_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The last day of the most recently filed accounting period.",
            default=None,
        ),
    ]

    period_start_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The first day of the most recently filed accounting period.",
            default=None,
        ),
    ]

    type: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "null",
            "full",
            "small",
            "medium",
            "group",
            "dormant",
            "interim",
            "initial",
            "total-exemption-full",
            "total-exemption-small",
            "partial-exemption",
            "audit-exemption-subsidiary",
            "filing-exemption-subsidiary",
            "micro-entity",
            "no-accounts-type-available",
            "audited-abridged",
            "unaudited-abridged",
        ),
        pydantic.Field(
            description=(
                "The type of the last company accounts filed. "
                "For enumeration descriptions see `account_type` section "
                "in the enumeration mappings."
            ),
        ),
    ]


class NextAccounts(base.BaseModel):
    """The next company accounts to be filed."""

    due_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the next company accounts are due",
            default=None,
        ),
    ]

    overdue: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Flag indicating if the company accounts are overdue.",
            default=None,
        ),
    ]

    period_end_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The last day of the next accounting period to be filed.",
            default=None,
        ),
    ]

    period_start_on: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The first day of the next accounting period to be filed.",
            default=None,
        ),
    ]


class AccountsInformation(base.BaseModel):
    """Company accounts information."""

    accounting_reference_date: typing.Annotated[
        AccountingReferenceDate | None,
        pydantic.Field(
            description="The Accounting Reference Date (ARD) of the company.",
            default=None,
        ),
    ]

    last_accounts: typing.Annotated[
        LastAccounts | None,
        pydantic.Field(
            description="The last company accounts filed.",
            default=None,
        ),
    ]

    next_due: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="Deprecated. Please use accounts.next_accounts.due_on",
            default=None,
        ),
    ]

    next_made_up_to: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="Deprecated. Please use accounts.next_accounts.period_end_on",
        ),
    ]

    overdue: typing.Annotated[
        bool,
        pydantic.Field(
            description="Deprecated. Please use accounts.next_accounts.overdue",
        ),
    ]

    next_accounts: typing.Annotated[
        NextAccounts | None,
        pydantic.Field(
            description="The next company accounts filed.",
            default=None,
        ),
    ]


class AnnualReturnInformation(base.BaseModel):
    """Annual return information for a company."""

    last_made_up_to: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date the last annual return was made up to.",
            default=None,
        ),
    ]

    next_due: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date the next annual return is due. This member will only be returned "
                "if a confirmation statement has not been filed and the date is before 28th July 2016, "
                "otherwise refer to `confirmation_statement.next_due`"
            ),
            default=None,
        ),
    ]

    next_made_up_to: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date the next annual return should be made up to. This member will only be returned "
                "if a confirmation statement has not been filed and the date is before 30th July 2016, "
                "otherwise refer to `confirmation_statement.next_made_up_to`"
            ),
            default=None,
        ),
    ]

    overdue: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Flag indicating if the annual return is overdue.",
            default=None,
        ),
    ]


class ConfirmationStatementInformation(base.BaseModel):
    """Confirmation statement information for a company."""

    last_made_up_to: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date to which the company last made a confirmation statement.",
            default=None,
        ),
    ]

    next_due: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date by which the next confimation statement must be received.",
        ),
    ]

    next_made_up_to: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date to which the company must next make a confirmation statement.",
        ),
    ]

    overdue: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Flag indicating if the confirmation statement is overdue",
            default=None,
        ),
    ]


class PreviousCompanyNames(base.BaseModel):
    """Previous name for a company."""

    name: typing.Annotated[
        str,
        pydantic.Field(
            description="The previous company name",
        ),
    ]

    effective_from: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date from which the company name was effective.",
        ),
    ]

    ceased_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date on which the company name ceased.",
        ),
    ]


class CorporateAnnotation(base.BaseModel):
    """Corporate annotation for a company."""

    created_on: typing.Annotated[
        datetime.date,
        pydantic.Field(
            description="The date on which the corporate annotation was created.",
        ),
    ]

    description: typing.Annotated[
        str | None,
        pydantic.Field(
            description=('The details of a corporate annotation which has a corporate_annotation.type of "other".'),
            default=None,
        ),
    ]

    type: typing.Annotated[
        str,
        pydantic.Field(
            description=(
                "The type of corporate annotation. "
                "For enumeration descriptions see `corporate_annotation_type` section in the enumeration mappings."
            ),
        ),
    ]


class AccountPeriodFrom(base.BaseModel):
    """Account period start date."""

    day: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Day on which accounting period starts under parent law.",
            default=None,
        ),
    ]

    month: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Month in which accounting period starts under parent law.",
            default=None,
        ),
    ]


class AccountPeriodTo(base.BaseModel):
    """Account period end date."""

    day: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Day on which accounting period ends under parent law.",
            default=None,
        ),
    ]

    month: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Month in which accounting period ends under parent law.",
            default=None,
        ),
    ]


class FileWithin(base.BaseModel):
    """Time period within which accounts must be filed."""

    months: typing.Annotated[
        int | None,
        pydantic.Field(
            description="Number of months within which to file.",
            default=None,
        ),
    ]


class AccountInformation(base.BaseModel):
    """Foreign company account information."""

    account_period_from: typing.Annotated[
        AccountPeriodFrom | None,
        pydantic.Field(
            description="Date account period starts under parent law.",
            default=None,
        ),
    ]

    account_period_to: typing.Annotated[
        AccountPeriodTo | None,
        pydantic.Field(
            description="Date account period ends under parent law.",
            default=None,
        ),
    ]

    must_file_within: typing.Annotated[
        FileWithin | None,
        pydantic.Field(
            description="Time allowed from period end for disclosure of accounts under parent law.",
            default=None,
        ),
    ]


class AccountsRequired(base.BaseModel):
    """Accounting requirements for a foreign company."""

    foreign_account_type: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "accounting-requirements-of-originating-country-apply",
            "accounting-requirements-of-originating-country-do-not-apply",
        ),
        pydantic.Field(
            description=(
                "Type of accounting requirement that applies. "
                "For enumeration descriptions see `foreign_account_type` section in the enumeration mappings."
            ),
            default=None,
        ),
    ]

    terms_of_account_publication: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "accounts-publication-date-supplied-by-company",
            "accounting-publication-date-does-not-need-to-be-supplied-by-company",
            "accounting-reference-date-allocated-by-companies-house",
        ),
        pydantic.Field(
            description=(
                "Describes how the publication date is derived. "
                "For enumeration descriptions see `terms_of_account_publication` section in the enumeration mappings."
            ),
            default=None,
        ),
    ]


class OriginatingRegistry(base.BaseModel):
    """Information about the originating registry of a foreign company."""

    country: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Country in which company was incorporated.",
            default=None,
        ),
    ]

    name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Identity of register in country of incorporation.",
            default=None,
        ),
    ]


class ForeignCompanyDetails(base.BaseModel):
    """Foreign company details."""

    originating_registry: typing.Annotated[
        OriginatingRegistry | None,
        pydantic.Field(
            description="Company origin informations",
            default=None,
        ),
    ]

    registration_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Registration number in company of incorporation.",
            default=None,
        ),
    ]

    governed_by: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Law governing the company in country of incorporation.",
            default=None,
        ),
    ]

    company_type: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Legal form of the company in the country of incorporation.",
            default=None,
        ),
    ]

    is_a_credit_finance_institution: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Is it a financial or credit institution.",
            default=None,
        ),
    ]

    accounts: typing.Annotated[
        AccountInformation | None,
        pydantic.Field(
            description="Foreign company account information.",
            default=None,
        ),
    ]

    business_activity: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Type of business undertaken by the company.",
            default=None,
        ),
    ]

    accounting_requirement: typing.Annotated[
        AccountsRequired | None,
        pydantic.Field(
            description="Accounts requirement.",
            default=None,
        ),
    ]


class RegisteredOfficeAddress(base.BaseModel):
    """Registered office address for a company."""

    care_of: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The care of name.",
            default=None,
        ),
    ]

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
            description="The region e.g Surrey.",
            default=None,
        ),
    ]


class ServiceAddress(base.BaseModel):
    """Service address of a Registered overseas entity."""

    care_of: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The care of name.",
            default=None,
        ),
    ]

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
            description="The country e.g. United Kingdom.",
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

    region: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The region e.g Surrey.",
            default=None,
        ),
    ]


class BranchCompanyDetails(base.BaseModel):
    """UK branch of a foreign company."""

    business_activity: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Type of business undertaken by the UK establishment.",
            default=None,
        ),
    ]

    parent_company_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Parent company number.",
            default=None,
        ),
    ]

    parent_company_name: typing.Annotated[
        str | None,
        pydantic.Field(
            description="Parent company name.",
            default=None,
        ),
    ]


class CompanyProfile(base.BaseModel):
    """Company profile information from Companies House."""

    accounts: typing.Annotated[
        AccountsInformation | None,
        pydantic.Field(
            description="Company accounts information.",
            default=None,
        ),
    ]

    annual_return: typing.Annotated[
        AnnualReturnInformation | None,
        pydantic.Field(
            description=(
                "Annual return information. This member is only returned if a confirmation statement has not be filed."
            ),
            default=None,
        ),
    ]

    can_file: typing.Annotated[
        bool,
        pydantic.Field(
            description="Flag indicating whether this company can file.",
        ),
    ]

    confirmation_statement: typing.Annotated[
        ConfirmationStatementInformation | None,
        pydantic.Field(
            description=(
                "Confirmation statement information (N.B. refers to the Annual Statement "
                "where type is registered-overseas-entity)"
            ),
            default=None,
        ),
    ]

    company_name: typing.Annotated[
        str,
        pydantic.Field(
            description="The name of the company.",
        ),
    ]

    jurisdiction: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "england-wales",
            "wales",
            "scotland",
            "northern-ireland",
            "european-union",
            "united-kingdom",
            "england",
            "noneu",
        ),
        pydantic.Field(
            description="The jurisdiction specifies the political body responsible for the company.",
            default=None,
        ),
    ]

    company_number: typing.Annotated[
        str,
        pydantic.Field(
            description="The number of the company.",
        ),
    ]

    date_of_creation: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date when the company was created.",
            default=None,
        ),
    ]

    date_of_cessation: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description=(
                "The date which the company was converted/closed, dissolved or removed. "
                "Please refer to company status to determine which."
            ),
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

    has_been_liquidated: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Deprecated. Please use links.insolvency",
            default=None,
        ),
    ]

    has_charges: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Deprecated. Please use links.charges",
            default=None,
        ),
    ]

    is_community_interest_company: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Deprecated. Please use subtype",
            default=None,
        ),
    ]

    subtype: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "community-interest-company",
            "private-fund-limited-partnership",
        ),
        pydantic.Field(
            description="The subtype of the company.",
            default=None,
        ),
    ]

    partial_data_available: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "full-data-available-from-financial-conduct-authority",
            "full-data-available-from-department-of-the-economy",
            "full-data-available-from-the-company",
        ),
        pydantic.Field(
            description=(
                "Returned if Companies House is not the primary source of data for this company. "
                "For enumeration descriptions see partial_data_available section in the enumeration mappings."
            ),
            default=None,
        ),
    ]

    external_registration_number: typing.Annotated[
        str | None,
        pydantic.Field(
            description="The number given by an external registration body.",
            default=None,
        ),
    ]

    foreign_company_details: typing.Annotated[
        ForeignCompanyDetails | None,
        pydantic.Field(
            description="Foreign company details.",
            default=None,
        ),
    ]

    last_full_members_list_date: typing.Annotated[
        datetime.date | None,
        pydantic.Field(
            description="The date of last full members list update.",
            default=None,
        ),
    ]

    registered_office_address: typing.Annotated[
        RegisteredOfficeAddress | None,
        pydantic.Field(
            description="The address of the company's registered office.",
            default=None,
        ),
    ]

    service_address: typing.Annotated[
        ServiceAddress | None,
        pydantic.Field(
            description="The correspondence address of a Registered overseas entity",
            default=None,
        ),
    ]

    has_super_secure_pscs: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Flag indicating whether the company has super secure persons with significant control.",
        ),
    ]

    super_secure_managing_officer_count: typing.Annotated[
        int | None,
        pydantic.Field(
            description="The total count of super secure managing officers for a `registered-overseas-entity`.",
            default=None,
        ),
    ]

    sic_codes: typing.Annotated[
        list[str] | None,
        pydantic.Field(
            description="SIC codes for this company.",
            default=None,
        ),
    ]

    previous_company_names: typing.Annotated[
        list[PreviousCompanyNames] | None,
        pydantic.Field(
            description="The previous names of this company.",
            default=None,
        ),
    ]

    corporate_annotation: typing.Annotated[
        list[CorporateAnnotation] | None,
        pydantic.Field(
            description=(
                "A corporate level message published by Companies House about a company, "
                "or situations affecting the company, or its information."
            ),
            default=None,
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
            "closed",
            "open",
        ),
        pydantic.Field(
            description=(
                "The status of the company. "
                "For enumeration descriptions see `company_status` section in the enumeration mappings."
            ),
            default=None,
        ),
    ]

    company_status_detail: typing.Annotated[
        str | None,
        field_types.RelaxedLiteral(
            "transferred-from-uk",
            "active-proposal-to-strike-off",
            "petition-to-restore-dissolved",
            "transformed-to-se",
            "converted-to-plc",
        ),
        pydantic.Field(
            description=(
                "Extra details about the status of the company. "
                "For enumeration descriptions see `company_status_detail` section in the enumeration mappings."
            ),
            default=None,
        ),
    ]

    type: typing.Annotated[
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

    has_insolvency_history: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Deprecated. Please use links.insolvency",
            default=None,
        ),
    ]

    undeliverable_registered_office_address: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Flag indicating whether post can be delivered to the registered office.",
            default=None,
        ),
    ]

    registered_office_is_in_dispute: typing.Annotated[
        bool | None,
        pydantic.Field(
            description="Flag indicating registered office address as been replaced.",
            default=None,
        ),
    ]

    branch_company_details: typing.Annotated[
        BranchCompanyDetails | None,
        pydantic.Field(
            description="UK branch of a foreign company.",
            default=None,
        ),
    ]

    links: typing.Annotated[
        shared.LinksSection,
        pydantic.Field(
            description="A set of URLs related to the resource, including self.",
        ),
    ]
