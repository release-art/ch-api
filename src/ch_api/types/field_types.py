"""Custom Pydantic field types for Companies House API models.

This module provides specialized field types for handling Companies House API
response data, including relaxed literal validation and undocumented nullable fields.

These custom types allow the client to be more forgiving of API responses while
still providing useful warnings when unexpected values are encountered.

See Also:
    - https://docs.pydantic.dev/latest/concepts/json_schema/
    - https://docs.pydantic.dev/latest/api/annotated/
"""

import logging
import typing

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

logger = logging.getLogger(__name__)

T = typing.TypeVar("T")

#: Type alias for fields that may be null but this is not documented in the official API.
#:
#: This is used to mark fields that the API sometimes returns as ``null`` even though
#: the documentation doesn't explicitly state they are nullable. Using this type
#: signals to developers that the field might be ``None`` in practice.
#:
#: Example:
#:     .. code-block:: python
#:
#:         from ch_api.types import field_types
#:         import pydantic
#:
#:         class CompanyProfile(BaseModel):
#:             company_number: str
#:             company_name: str
#:             # This field may sometimes be null despite not being documented as optional
#:             dissolution_date: field_types.UndocumentedNullable[str] = None
UndocumentedNullable = typing.Optional[T]


def RelaxedLiteral(*expected_values: str):
    """Create a relaxed literal type that accepts any string but logs unexpected values.

    This custom Pydantic type implements a "relaxed" literal validation that allows any
    string value while logging a warning when an unexpected value is encountered. This
    approach makes the client more resilient to API changes where new enumeration values
    are added before the client is updated.

    The type is especially useful for Companies House API fields that represent
    enumerated types (e.g., company status, company type) which may be extended
    with new values by the API without prior notice.

    Parameters
    ----------
    *expected_values : str
        Variable-length list of expected string values. When a value outside this set
        is received, a warning is logged but validation succeeds.

    Returns
    -------
    type
        A Pydantic-compatible type that validates string fields with relaxed constraints.

    Features
    --------
    - **Forward compatibility**: Accepts new values from API not yet known to client
    - **Informative warnings**: Logs when unexpected values are encountered
    - **Nullable support**: Automatically allows ``None`` for optional fields
    - **Type safety**: Integrates seamlessly with Pydantic validation

    Example
    -------
    Define a model with relaxed literal fields for enumerated types::

        from ch_api.types.base import BaseModel
        from ch_api.types import field_types
        import pydantic
        import typing

        class CompanyProfile(BaseModel):
            # Strict company statuses (for example purposes)
            company_status: typing.Annotated[
                str,
                field_types.RelaxedLiteral(
                    "active",
                    "dissolved",
                    "liquidation",
                    "administration"
                )
            ] = pydantic.Field(..., description="Company status")

            # Optional field with relaxed validation
            company_type: typing.Annotated[
                str | None,
                field_types.RelaxedLiteral(
                    "private-unlimited",
                    "ltd",
                    "plc"
                )
            ] = pydantic.Field(default=None, description="Company type")

        # Accepts known values without warning
        profile = CompanyProfile.model_validate({
            "company_status": "active",
            "company_type": "ltd"
        })

        # Accepts new values from API update, logs warning
        profile = CompanyProfile.model_validate({
            "company_status": "administration",  # Known
            "company_type": "new-type-added-by-api"  # Unknown - logs warning
        })

        # Works with None values
        profile = CompanyProfile.model_validate({
            "company_status": "active",
            "company_type": None  # OK - field is optional
        })

    Benefits for Companies House API
    --------------------------------
    The Companies House API's enumeration types (documented at
    https://github.com/companieshouse/api-enumerations) are periodically extended
    with new values. This type allows the client to:

    1. Continue functioning when new enumeration values are introduced
    2. Alert developers to new values via logging (useful for testing/staging)
    3. Avoid breaking changes when the API evolves

    Without relaxed literals, a new enumeration value from the API would cause
    a Pydantic validation error, potentially breaking all client code.

    Note
    ----
    - Warnings are logged using the ``logging`` module at ``WARNING`` level
    - The actual string value is always available in the model, even if unexpected
    - This type should be used sparingly; strict literals are preferred when possible
    - Consider filing issues if new enumeration values need documentation

    See Also
    --------
    UndocumentedNullable : For fields that may be null but documentation doesn't indicate
    https://github.com/companieshouse/api-enumerations : API enumeration definitions
    https://docs.pydantic.dev/latest/concepts/json_schema/ : Pydantic validation
    """

    class _RelaxedLiteral:
        """Internal class implementing the relaxed literal validation logic."""

        _expected_values = set(expected_values)

        @classmethod
        def __get_pydantic_core_schema__(
            cls, source_type: typing.Any, handler: GetCoreSchemaHandler
        ) -> core_schema.CoreSchema:
            """Create the Pydantic core schema for relaxed literal validation.

            Parameters
            ----------
            source_type : Any
                The source type being validated (used by Pydantic)

            handler : GetCoreSchemaHandler
                Pydantic's schema handler

            Returns
            -------
            core_schema.CoreSchema
                The validation schema for this type
            """

            def validate_and_log(value: typing.Any, info: core_schema.ValidationInfo) -> typing.Any:
                """Validate value and log warnings for unexpected strings.

                Parameters
                ----------
                value : Any
                    The value to validate

                info : core_schema.ValidationInfo
                    Pydantic validation context information

                Returns
                -------
                Any
                    The validated value (passed through unchanged)
                """
                # Allow None to pass through without validation
                if value is None:
                    return value

                # Convert to string and validate
                str_value = str(value)
                if str_value not in cls._expected_values:
                    # Build field path for logging
                    field_name = "unknown field"
                    if hasattr(info, "field_name") and info.field_name:
                        field_name = info.field_name

                    logger.warning(
                        f"Field '{field_name}': Unexpected value '{str_value}'. "
                        f"Expected one of: {', '.join(sorted(cls._expected_values))}"
                    )
                return str_value

            return core_schema.with_info_after_validator_function(
                validate_and_log,
                core_schema.union_schema(
                    [
                        core_schema.none_schema(),
                        core_schema.str_schema(),
                    ]
                ),
            )

    return _RelaxedLiteral
