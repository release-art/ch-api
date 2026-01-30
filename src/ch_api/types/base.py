"""Base Pydantic model for Companies House API types.

Extends Pydantic's BaseModel with field name normalization for API responses.

See Also:
    https://docs.pydantic.dev/latest/
"""

import typing

import pydantic

from . import settings


class BaseModel(pydantic.BaseModel):
    """Base Pydantic model for Companies House API responses.

    Automatically normalizes field names to lowercase for consistency.
    Inherits from this class for all API response models.
    """

    model_config = pydantic.ConfigDict(
        extra=settings.model_validate_extra,
    )

    @classmethod
    def model_validate(  # type: ignore[override]
        cls, data: typing.Any, **kwargs: typing.Any
    ) -> "BaseModel":
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
