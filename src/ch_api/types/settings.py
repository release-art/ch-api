"""Global type settings for Companies House API models.

Controls how Pydantic models handle extra fields in API responses:
- ``'allow'`` - Accept and store extra fields (debugging)
- ``'ignore'`` - Accept but discard extra fields (production, default)
- ``'forbid'`` - Reject responses with extra fields (development)
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
