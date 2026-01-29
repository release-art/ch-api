"""Exceptions for the Companies House API client.

This module defines custom exception classes raised by the API client when
errors occur during API communication or response processing.

Exception Hierarchy
-------------------
All exceptions inherit from :exc:`CompaniesHouseApiError`, which inherits from
the built-in :exc:`Exception`. This allows catching all Companies House API
errors with a single except clause::

    try:
        profile = await client.get_company_profile("invalid-number")
    except ch_api.exc.CompaniesHouseApiError as e:
        print(f"API error: {e}")

See Also:
    https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
"""

__all__ = [
    "CompaniesHouseApiError",
    "UnexpectedApiResponseError",
]


class CompaniesHouseApiError(Exception):
    """Base exception for Companies House API errors.

    This is the parent class for all exceptions raised by the Companies House API
    client. Catch this exception to handle any API-related errors in a generic manner.

    Example
    -------
    Handle any API error::

        try:
            company = await client.get_company_profile("12345678")
        except CompaniesHouseApiError as e:
            logger.error(f"Failed to fetch company: {e}")

    See Also
    --------
    UnexpectedApiResponseError : Specific error for malformed API responses
    """


class UnexpectedApiResponseError(CompaniesHouseApiError):
    """Exception raised when the API response is not as expected.

    This error indicates that the Companies House API returned a response that
    could not be properly parsed or validated. Common causes include:

    - Missing expected response body
    - Empty response when body was expected
    - Malformed JSON response
    - Response structure doesn't match expected Pydantic model
    - HTTP status code conflicts with expected response type

    Attributes
    ----------
    message : str
        Description of what was unexpected about the response.

    Example
    -------
    Handle unexpected response errors::

        try:
            company = await client.get_company_profile("09370755")
        except UnexpectedApiResponseError as e:
            logger.error(f"Unexpected API response: {e}")
            # May indicate API version mismatch or API changes

    Note
    ----
    This exception is typically raised when the API response structure has
    changed unexpectedly, possibly due to an API upgrade or regression.
    If you encounter this error frequently, check the Companies House API
    documentation for any announced changes.

    See Also
    --------
    CompaniesHouseApiError : Base exception class
    """
