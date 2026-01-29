"""Compound API type wrappers for complex Companies House API responses.

This package contains custom wrapper classes for complex API responses that
require additional processing or composition beyond simple Pydantic models.

These types are typically returned by client methods that wrap multiple API
endpoints or transform standard responses for easier consumption.

For example:
- Search results with custom pagination handling
- Officer appointment lists with aggregation
- PSC lists with special filtering

See Also
--------
ch_api.types.public_data : Base Pydantic models for individual endpoints
ch_api.types.pagination : Pagination support
"""

from . import public_data
