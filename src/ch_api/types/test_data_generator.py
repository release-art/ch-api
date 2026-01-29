"""Models for test data generation in Companies House API."""

import typing

import pydantic

from . import base


class FilingHistoryResolution(base.BaseModel):
    """Resolution details for filing history."""

    category: typing.Annotated[
        typing.Literal[
            "auditors",
            "capital",
            "change-of-name",
            "incorporation",
            "insolvency",
            "liquidation",
            "miscellaneous",
            "other",
            "resolution",
        ],
        pydantic.Field(
            description=("Resolutions category for resolutions type (e.g., `incorporation`, `resolutions`)")
        ),
    ]
    description: typing.Annotated[
        typing.Literal[
            "elective-resolution",
            "extraordinary-resolution",
            "extraordinary-resolution-acquisition",
            "extraordinary-resolution-adopt-memorandum",
            "extraordinary-resolution-alteration-memorandum",
            "extraordinary-resolution-capitalisation",
            "extraordinary-resolution-exemption",
            "extraordinary-resolution-increase-capital",
            "extraordinary-resolution-memorandum",
            "extraordinary-resolution-purchase-number-shares",
            "extraordinary-resolution-purchase-shares",
            "extraordinary-resolution-reduction-capital",
            "extraordinary-resolution-removal-pre-emption",
            "extraordinary-resolution-securities",
            "extraordinary-resolution-varying-share-rights",
            "liquidation-special-resolution-to-wind-up-northern-ireland",
            "liquidation-voluntary-extraordinary-resolution-to-wind-up",
            "liquidation-voluntary-extraordinary-resolution-to-wind-up-with-case-start-date",
            "liquidation-voluntary-extraordinary-to-wind-up-with-case-start-date",
            "liquidation-voluntary-special-resolution-to-wind-up",
            "liquidation-voluntary-special-resolution-to-wind-up-case-start-date",
            "ordinary-resolution",
            "ordinary-resolution-acquisition",
            "ordinary-resolution-adopt-memorandum",
            "ordinary-resolution-alteration-memorandum",
            "ordinary-resolution-capitalisation",
            "ordinary-resolution-decrease-capital",
            "ordinary-resolution-exemption",
            "ordinary-resolution-increase-capital",
            "ordinary-resolution-memorandum",
            "ordinary-resolution-purchase-number-shares",
            "ordinary-resolution-purchase-shares",
            "ordinary-resolution-redeem-shares",
            "ordinary-resolution-reduction-capital",
            "ordinary-resolution-removal-pre-emption",
            "ordinary-resolution-securities",
            "ordindary-resolution-varying-share-rights",
            "resolution",
            "resolution-acquisition",
            "resolution-adopt-articles",
            "resolution-adopt-memorandum-and-articles",
            "resolution-alteration-articles",
            "resolution-alteration-memorandum",
            "resolution-alteration-memorandum-and-articles",
            "resolution-capitalisation",
            "resolution-change-of-name",
            "resolution-decrease-capital",
            "resolution-exemption",
            "resolution-increase-capital",
            "resolution-memorandum-and-articles",
            "resolution-purchase-number-shares",
            "resolution-purchase-shares",
            "resolution-re-registration",
            "resolution-redeem-shares",
            "resolution-reduction-capital",
            "resolution-removal-pre-emption",
            "resolution-securities",
            "resolution-varying-share-rights",
            "special-resolution",
            "special-resolution-acquisition",
            "special-resolution-adopt-memorandum",
            "special-resolution-alteration-memorandum",
            "special-resolution-capitalisation",
            "special-resolution-decrease-capital",
            "special-resolution-exemption",
            "special-resolution-increase-capital",
            "special-resolution-memorandum",
            "special-resolution-purchase-number-shares",
            "special-resolution-purchase-shares",
            "special-resolution-re-registration",
            "special-resolution-redeem-shares",
            "special-resolution-reduction-capital",
            "special-resolution-removal-pre-emption",
            "special-resolution-securities",
            "special-resolution-varying-share-rights",
            "written-resolution",
            "written-resolution-acquisition",
            "written-resolution-adopt-memorandum",
            "written-resolution-alteration-memorandum",
            "written-resolution-capitalisation",
            "written-resolution-decrease-capital",
            "written-resolution-exemption",
            "written-resolution-increase-capital",
            "written-resolution-memorandum",
            "written-resolution-purchase-number-shares",
            "written-resolution-purchase-shares",
            "written-resolution-re-registration",
            "written-resolution-reduction-capital",
            "written-resolution-removal-pre-emption",
            "written-resolution-securities",
            "written-resolution-varying-share-rights",
        ],
        pydantic.Field(
            description=(
                "Description for resolutions type (e.g., `resolution-re-registration`, `incorporation-company`)"
            )
        ),
    ]
    subcategory: typing.Annotated[
        typing.Literal["resolution", "voluntary"],
        pydantic.Field(description=("Sub category for resolutions type (e.g., `resolution`, `incorporation`)")),
    ]
    type: typing.Annotated[
        typing.Literal[
            "(W)ELRES",
            "ELRES",
            "ERES01",
            "ERES03",
            "ERES04",
            "ERES06",
            "ERES07",
            "ERES08",
            "ERES09",
            "ERES10",
            "ERES11",
            "ERES12",
            "ERES13",
            "ERES14",
            "LRES(NI)",
            "LRESC(NI)",
            "LRESEX",
            "LRESM(NI)",
            "LRESSP",
            "ORES01",
            "ORES03",
            "ORES04",
            "ORES05",
            "ORES06",
            "ORES07",
            "ORES08",
            "ORES09",
            "ORES10",
            "ORES11",
            "ORES12",
            "ORES13",
            "ORES14",
            "ORES16",
            "RES(ECS)",
            "RES(NI)",
            "RES01",
            "RES02",
            "RES03",
            "RES04",
            "RES05",
            "RES06",
            "RES07",
            "RES08",
            "RES09",
            "RES10",
            "RES11",
            "RES12",
            "RES13",
            "RES14",
            "RES15",
            "RES16",
            "RESMISC",
            "SRES01",
            "SRES02",
            "SRES03",
            "SRES04",
            "SRES05",
            "SRES06",
            "SRES07",
            "SRES08",
            "SRES09",
            "SRES10",
            "SRES11",
            "SRES12",
            "SRES13",
            "SRES14",
            "SRES16",
            "WRES01",
            "WRES02",
            "WRES03",
            "WRES04",
            "WRES05",
            "WRES06",
            "WRES07",
            "WRES08",
            "WRES09",
            "WRES10",
            "WRES11",
            "WRES12",
            "WRES13",
            "WRES14",
        ],
        pydantic.Field(description="Type for the resolutions type (e.g., `RES02`, `RES04`)"),
    ]


class FilingHistoryItem(base.BaseModel):
    """Filing history item for test company generation."""

    type: typing.Annotated[
        str,
        pydantic.Field(description="The type of the filing history"),
    ]
    category: typing.Annotated[
        typing.Literal[
            "accounts",
            "address",
            "annotation",
            "annual-return",
            "auditors",
            "capital",
            "certificate",
            "change-of-constitution",
            "change-of-name",
            "confirmation-statement",
            "court-order",
            "dissolution",
            "document-replacement",
            "gazette",
            "historical",
            "incorporation",
            "insolvency",
            "liquidation",
            "miscellaneous",
            "mortgage",
            "officer",
            "officers",
            "other",
            "persons-with-significant-control",
            "reregistration",
            "resolution",
            "restoration",
            "return",
            "social-landlord",
        ],
        pydantic.Field(description="The category of the filing history"),
    ]
    description: typing.Annotated[
        str,
        pydantic.Field(description="The description of the filing history"),
    ]
    sub_category: typing.Annotated[
        typing.Literal[
            "annual-return",
            "confirmation-statement",
            "full",
            "partial",
            "short",
            "acquire",
            "administration",
            "alter",
            "appointments",
            "certificate",
            "change",
            "compulsory",
            "court-order",
            "create",
            "debenture",
            "document-replacement",
            "investment-company",
            "mortgage",
            "notifications",
            "officers",
            "other",
            "receiver",
            "register",
            "release-cease",
            "resolution",
            "satisfy",
            "social-landlord",
            "statements",
            "termination",
            "transfer",
            "trustee",
            "voluntary",
            "voluntary-arrangement",
            "voluntary-arrangement-moratoria",
        ],
        pydantic.Field(description="The sub category of the filing history"),
    ]
    resolutions: typing.Annotated[
        list[FilingHistoryResolution] | None,
        pydantic.Field(
            description=(
                "The resolutions associated with the filing history. Maximum of 20 resolutions can be specified"
            ),
            max_length=20,
            default=None,
        ),
    ]


class RegisterItem(base.BaseModel):
    """Register information for test company generation."""

    register_type: typing.Annotated[
        typing.Literal[
            "members",
            "directors",
            "secretaries",
            "psc",
            "charges",
            "allotments",
            "debentures",
            "persons-with-significant-control",
            "usual-residential-address",
            "llp-members",
            "llp-usual-residential-address",
        ],
        pydantic.Field(description="The type of the register"),
    ]
    register_moved_to: typing.Annotated[
        typing.Literal[
            "public-register",
            "registered-office",
            "single-alternative-inspection-location",
            "unspecified-location",
        ],
        pydantic.Field(description="Where the register has been moved to"),
    ]


class CreateTestCompanyRequest(base.BaseModel):
    """Request body for creating a test company in Companies House.

    This model defines all available options for generating test company data,
    including company details, officers, PSCs, filing history, and registers.
    """

    jurisdiction: typing.Annotated[
        typing.Literal["england-wales", "scotland", "northern-ireland"],
        pydantic.Field(
            description=("The jurisdiction of the test company to generate. Defaults to `england-wales`"),
            default="england-wales",
        ),
    ]

    company_status: typing.Annotated[
        typing.Literal[
            "active",
            "administration",
            "closed",
            "converted-closed",
            "dissolved",
            "inactive",
            "insolvency-proceedings",
            "liquidation",
            "open",
            "receivership",
            "registered",
            "removed",
            "voluntary-arrangement",
        ],
        pydantic.Field(
            description=("The company_status of the test company to generate. Defaults to `active`"),
            default="active",
        ),
    ]

    company_type: typing.Annotated[
        typing.Literal[
            "assurance-company",
            "charitable-incorporated-organisation",
            "community-interest-company",
            "converted-or-closed",
            "eeig",
            "eeig-establishment",
            "european-public-limited-liability-company-se",
            "further-education-or-sixth-form-college-corporation",
            "icvc-securities",
            "icvc-umbrella",
            "icvc-warrant",
            "industrial-and-provident-society",
            "investment-company-with-variable-capital",
            "limited-partnership",
            "llp",
            "ltd",
            "northern-ireland",
            "northern-ireland-other",
            "old-public-company",
            "other",
            "oversea-company",
            "plc",
            "private-fund-limited-partnership",
            "private-limited-guarant-nsc",
            "private-limited-guarant-nsc-limited-exemption",
            "private-limited-shares-section-30-exemption",
            "private-unlimited",
            "private-unlimited-nsc",
            "protected-cell-company",
            "registered-overseas-entity",
            "registered-society-non-jurisdictional",
            "royal-charter",
            "scottish-charitable-incorporated-organisation",
            "scottish-partnership",
            "uk-establishment",
            "ukeig",
            "united-kingdom-societas",
            "unregistered-company",
        ],
        pydantic.Field(
            description=("The company type of the test company to generate. Defaults to `ltd`"),
            default="ltd",
        ),
    ]

    sub_type: typing.Annotated[
        typing.Literal[
            "community-interest-company",
            "private-fund-limited-partnership",
        ]
        | None,
        pydantic.Field(
            description=("The company sub type of the test company to generate. Defaults to `none`"),
            default=None,
        ),
    ]

    company_status_detail: typing.Annotated[
        typing.Literal[
            "active",
            "active-proposal-to-strike-off",
            "converted-closed",
            "converted-to-plc",
            "converted-to-uk-societas",
            "converted-to-ukeig",
            "dissolved",
            "petition-to-restore-dissolved",
            "transferred-from-uk",
            "transformed-to-se",
        ],
        pydantic.Field(
            description=("The company status detail of the test company to generate. Defaults to `active`"),
            default="active",
        ),
    ]

    filing_history: typing.Annotated[
        list[FilingHistoryItem] | None,
        pydantic.Field(
            description=(
                "The filing history of the test company to generate. "
                "Defaults to `none`. Maximum of 20 items can be specified."
            ),
            max_length=20,
            default=None,
        ),
    ]

    accounts_due_status: typing.Annotated[
        typing.Literal["overdue", "due-soon"],
        pydantic.Field(
            description=("The accounts due status of the test company to generate. Defaults to `overdue`"),
            default="overdue",
        ),
    ]

    registers: typing.Annotated[
        list[RegisterItem] | None,
        pydantic.Field(
            description=("The registers for the test company to generate. Maximum of 20 registers can be specified"),
            max_length=20,
            default=None,
        ),
    ]

    has_super_secure_pscs: typing.Annotated[
        bool | None,
        pydantic.Field(
            description=("Whether the test company has super secure PSCs. Defaults to not having super secure PSCs"),
            default=None,
        ),
    ]

    number_of_appointments: typing.Annotated[
        int,
        pydantic.Field(
            description=(
                "Total number of officers to create. Defaults to 1 (a director). "
                "If greater than 1, officers are created in this order: director, "
                "then secretary, then additional directors (unless officer_roles "
                "is specified). Maximum number of appointments are 20."
            ),
            ge=1,
            le=20,
            default=1,
        ),
    ]

    officer_roles: typing.Annotated[
        list[
            typing.Literal[
                "cic-manager",
                "corporate-director",
                "corporate-llp-designated-member",
                "corporate-llp-member",
                "corporate-manager-of-an-eeig",
                "corporate-managing-officer",
                "corporate-member-of-a-management-organ",
                "corporate-member-of-a-supervisory-organ",
                "corporate-member-of-an-administrative-organ",
                "corporate-nominee-director",
                "corporate-nominee-secretary",
                "corporate-secretary",
                "director",
                "general-partner-in-a-limited-partnership",
                "judicial-factor",
                "limited-partner-in-a-limited-partnership",
                "llp-designated-member",
                "llp-member",
                "manager-of-an-eeig",
                "managing-officer",
                "member-of-a-management-organ",
                "member-of-a-supervisory-organ",
                "member-of-an-administrative-organ",
                "nominee-director",
                "nominee-secretary",
                "person-authorised-to-accept",
                "person-authorised-to-represent",
                "person-authorised-to-represent-and-accept",
                "receiver-and-manager",
                "secretary",
            ]
        ]
        | None,
        pydantic.Field(
            description=(
                "List of strings. Specifies roles for the officers created. "
                "If the list is shorter than number_of_appointments, "
                "remaining officers default to directors. If ONLY this field "
                "is specified, only ONE officer is created (using the first "
                "role in the list)."
            ),
            default=None,
        ),
    ]

    number_of_pscs: typing.Annotated[
        int,
        pydantic.Field(
            description=(
                "Integer (Max: 20). The number of PSCs. This value is used as "
                "the default for active_statements if active_statements is not "
                "provided. Defaults to 0."
            ),
            ge=0,
            le=20,
            default=0,
        ),
    ]

    psc_type: typing.Annotated[
        typing.Literal[
            "individual",
            "corporate",
            "legal-person",
            "individual-bo",
            "corporate-bo",
        ],
        pydantic.Field(
            description="The type of PSC to create. Defaults to `individual`",
            default="individual",
        ),
    ]

    psc_active: typing.Annotated[
        bool,
        pydantic.Field(
            description=(
                "Boolean value to determine if the PSCs are active or ceased. "
                "To be used alongside PSC requests. Where a request is creating "
                "multiple PSCs, a false value here will set the first PSC to "
                "inactive. Defaults to true."
            ),
            default=True,
        ),
    ]

    withdrawn_statements: typing.Annotated[
        int,
        pydantic.Field(
            description=("Integer (Max: 20). Number of withdrawn PSC statements. Defaults to 0."),
            ge=0,
            le=20,
            default=0,
        ),
    ]

    active_statements: typing.Annotated[
        int | None,
        pydantic.Field(
            description=(
                "Integer (Max: 20). Number of active PSC statements. "
                "Defaults to number_of_psc or 0. This value is ignored and "
                "forced to 1 if has_super_secure_pscs is true."
            ),
            ge=0,
            le=20,
            default=None,
        ),
    ]

    has_uk_establishment: typing.Annotated[
        bool,
        pydantic.Field(
            description=(
                "Boolean value to determine if the oversea company has a UK "
                "establishment. Defaults to false. A `true` value will create "
                "an oversea company with a UK establishment. Used alongside "
                "`oversea-company` company type."
            ),
            default=False,
        ),
    ]

    registered_office_is_in_dispute: typing.Annotated[
        bool,
        pydantic.Field(
            description=("Boolean value to determine if the registered office is in dispute. Defaults to false."),
            default=False,
        ),
    ]

    undeliverable_registered_office_address: typing.Annotated[
        bool,
        pydantic.Field(
            description=(
                "Boolean value to indicate if a company's registered office "
                "address has been reported as undeliverable by the Royal Mail. "
                "Defaults to false."
            ),
            default=False,
        ),
    ]

    is_secure_officer: typing.Annotated[
        bool,
        pydantic.Field(
            description=(
                "Boolean value. If set to `true`, all company officers created "
                "by this request will have their `is_secure_officer` field set "
                "to `true`. Defaults to `false`."
            ),
            default=False,
        ),
    ]

    foreign_company_legal_form: typing.Annotated[
        bool,
        pydantic.Field(
            description=(
                "Boolean value to determine if a foreign company legal form is "
                "to be added. Defaults to false. If it is true, an auto "
                "generated text form will be added to the foreign company "
                "details."
            ),
            default=False,
        ),
    ]


class CreateTestCompanyResponse(base.BaseModel):
    """Response from creating a test company in Companies House.

    Contains the generated company details including the company number,
    URI for retrieving the company profile, and authorization code.
    """

    company_number: typing.Annotated[
        str,
        pydantic.Field(description="The company number generated"),
    ]

    company_uri: typing.Annotated[
        str,
        pydantic.Field(description="The URI to retrieve the generated company profile data"),
    ]

    auth_code: typing.Annotated[
        str,
        pydantic.Field(description="The company authorisation code generated"),
    ]


class DeleteTestCompanyRequestBody(base.BaseModel):
    """Request body for deleting a test company in Companies House.

    Requires the authorization code that was returned when the test company was created.
    """

    auth_code: typing.Annotated[
        str,
        pydantic.Field(description=("The company auth code returned when the test company was generated")),
    ]
