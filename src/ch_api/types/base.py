"""Base Pydantic model for Companies House API types.

This module provides the foundation for all data models used to represent
Companies House API responses. It extends Pydantic's BaseModel with custom
validation logic to handle field name normalization and compatibility with
various API response formats.

See Also:
    - :mod:`ch_api.types`: Other type definitions
    - https://docs.pydantic.dev/latest/ : Pydantic documentation
"""

import typing

import pydantic

from . import settings


class BaseModel(pydantic.BaseModel):
    """Base Pydantic model for all Companies House API response types.

    This class extends Pydantic's BaseModel with custom validation to normalize
    field names and handle API-specific response patterns. All data models
    representing Companies House API responses should inherit from this class.

    Configuration
    ---------------
    - **Extra fields**: Handling is controlled by :data:`settings.model_validate_extra`
    - **Field validation**: Automatic normalization of field names to lowercase

    Features
    --------
    - Automatic field name normalization (lowercase)
    - Filtering of deprecated/unused fields marked with ``[notinuse]``
    - Flexible handling of extra fields not defined in the model
    - Full Pydantic validation and serialization support

    Example
    -------
    Creating a custom model for API responses::

        from ch_api.types.base import BaseModel
        import pydantic

        class CompanyInfo(BaseModel):
            company_number: str
            company_name: str
            status: str = pydantic.Field(..., description="Company status")

    The model will automatically normalize field names from API responses::

        # API returns mixed case field names
        data = {
            "CompanyNumber": "09370755",
            "CompanyName": "Example Corp",
            "Status": "active"
        }

        company = CompanyInfo.model_validate(data)
        # Field names are automatically normalized to lowercase

    Note
    ----
    This base model handles common API response patterns but all field names
    should be defined using lowercase with underscores in your model definitions.

    See Also
    --------
    pydantic.BaseModel : The parent Pydantic BaseModel
    settings.model_validate_extra : Configuration for extra field handling
    """

    model_config = pydantic.ConfigDict(
        extra=settings.model_validate_extra,
    )

    @classmethod
    def model_validate(cls, data: typing.Any) -> "BaseModel":
        """Validate and create model instance from API response data.

        This method extends Pydantic's validation to handle Companies House API
        response patterns including field name normalization and filtering of
        deprecated/unused fields.

        The method performs the following transformations:

        1. **Field name normalization**: Converts all field names to lowercase
        2. **Whitespace trimming**: Removes leading/trailing whitespace from field names
        3. **Deprecated field filtering**: Removes fields marked as ``[notinuse]``

        Parameters
        ----------
        data : Any
            Raw data from API response, typically a dictionary with field names
            that may use mixed case (e.g., ``CompanyName``, ``company_number``).

            Also supports non-dict data, which is passed directly to Pydantic's
            validation without modification.

        Returns
        -------
        BaseModel
            A validated model instance with normalized field names and
            deprecated fields removed.

        Example
        -------
        Validate API response with mixed-case field names::

            from ch_api.types.company_profile import CompanyProfile

            api_response = {
                "CompanyNumber": "09370755",
                "CompanyName": "Example Company",
                "CompanyStatus": "active",
                "OldField[notinuse]": "deprecated value"
            }

            company = CompanyProfile.model_validate(api_response)
            # Field names normalized, unused fields filtered

        Note
        ----
        This method is automatically called by Pydantic when deserializing
        JSON or dict data into the model. You typically don't need to call
        this method directly unless you're doing custom serialization/deserialization.

        See Also
        --------
        pydantic.BaseModel.model_validate : Parent Pydantic validation method
        """
        if isinstance(data, dict):
            updated_data = {}
            for key, value in data.items():
                if isinstance(key, str):
                    key = key.lower().strip()
                    if "[notinuse]" in key:
                        # Skip fields that are marked as not in use
                        continue
                updated_data[key] = value
            data = updated_data
        return super().model_validate(data)
