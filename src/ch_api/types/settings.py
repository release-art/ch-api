"""Global type settings for Companies House API models.

This module provides centralized configuration for Pydantic model behavior
across all API response types.

Global Settings
-----
These settings control how Pydantic models handle extra fields (fields in API
responses that don't have corresponding model properties).

Configuration Options:
    - ``'allow'`` - Accept and store extra fields (most permissive)
    - ``'ignore'`` - Accept but discard extra fields (recommended for production)
    - ``'forbid'`` - Reject responses with extra fields (useful for development)

Strategy
-----
**Development**: Use ``'forbid'`` to catch API changes and new fields that
the client library hasn't been updated to handle yet.

**Production**: Use ``'ignore'`` to be resilient to API changes. The client
will continue working even if the API adds new fields or changes response
structures slightly.

**Debugging**: Use ``'allow'`` to inspect what extra fields the API returns
for debugging purposes.

Example
-------
The setting controls model behavior::

    # With 'ignore' (current setting)
    profile = CompanyProfile.model_validate(api_response)
    # Extra fields in api_response are silently ignored

    # With 'forbid'
    try:
        profile = CompanyProfile.model_validate(api_response)
    except pydantic.ValidationError:
        # API returned a field we don't know about
        print("API may have changed")

See Also
--------
pydantic.ConfigDict : Pydantic configuration documentation
ch_api.types.base.BaseModel : Uses this setting in model_config
"""

import typing

#: Global Pydantic model configuration for extra field handling.
#:
#: Controls how models handle fields in API responses that don't match
#: declared model fields:
#:
#: - ``'allow'``: Accept and store extra fields
#: - ``'ignore'``: Accept but discard extra fields
#: - ``'forbid'``: Reject responses with extra fields
#:
#: Currently set to ``'ignore'`` to be production-safe while discarding
#: unknown fields gracefully.
#:
#: Adjust this setting to debug API changes:
#: - For development: Use ``'forbid'`` to catch API schema changes
#: - For production: Use ``'ignore'`` for resilience
#: - For inspection: Use ``'allow'`` to see what extra fields exist
#:
#: See Also:
#:     https://docs.pydantic.dev/latest/api/config/
model_validate_extra: typing.Literal["allow", "ignore", "forbid"] = "ignore"
