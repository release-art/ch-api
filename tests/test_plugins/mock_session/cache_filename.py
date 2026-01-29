"""Convert session request params to cache filename used in tests."""

import hashlib
import json
import logging
import pathlib
import re
import typing
from urllib.parse import parse_qs, urlparse

import httpx

logger = logging.getLogger(__name__)
G_CUR_TEST_PREFIX: typing.Optional[pathlib.PurePath] = None


def make(request: httpx.Request) -> pathlib.PurePath:  # noqa: C901
    """Generate a cache filename based on the request parameters.

    Creates human-readable cache filenames by:
    - Using the last URL path segment as a directory name
    - Creating descriptive filenames based on request parameters
    - Adding a hash suffix for uniqueness

    Parameters
    ----------
    request : httpx.Request
        The HTTP request object.

    Returns
    -------
    pathlib.PurePath
        Path to the cache file with directory structure.
    """
    # Parse the URL to extract components
    parsed_url = urlparse(str(request.url))
    path_parts = [part for part in parsed_url.path.split("/") if part]

    # Use the last path segment as directory name, or 'root' if no path
    name_parts = []
    if path_parts:
        for part in reversed(path_parts):
            if not part.isdigit():
                name_parts.insert(0, part)
                if len(name_parts) >= 2:
                    break

    if not name_parts:
        name_parts.append("root")

    name_prefix = "_".join(name_parts).lower()

    # Clean directory name (remove special characters)
    name_prefix = re.sub(r"[^\w\-_]", "_", name_prefix)

    # Build human-readable filename components
    filename_parts = [name_prefix]

    # Add method
    filename_parts.append(request.method.lower())

    content_size = len(request.content) if request.content else 0
    filename_parts.append(f"data_{content_size}")

    # Add query parameters if present
    query_params = parse_qs(parsed_url.query)
    if query_params:
        for key, values in sorted(query_params.items()):
            if values:
                # Clean parameter values for filename safety
                clean_value = re.sub(r"[^\w\-_]", "_", str(values[0]))[:20]  # Limit length
                filename_parts.append(f"{key}_{clean_value}")

    # Create base filename
    if filename_parts:
        base_filename = "_".join(filename_parts)
    else:
        base_filename = "request"

    # Create a hash for uniqueness (shorter than before, but still unique)
    cache_key_data = {
        "url": str(request.url),
        "method": request.method,
    }
    cache_key = json.dumps(cache_key_data, sort_keys=True)
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()[:8]  # Use first 8 chars

    # Combine into final filename
    final_filename = f"{base_filename}_{cache_hash}.json"

    assert G_CUR_TEST_PREFIX is not None, "G_CUR_TEST_PREFIX must be set before calling make()"
    out = G_CUR_TEST_PREFIX / final_filename
    logger.info(f"Generated cache filename: {out}")
    return out
