# Companies House API Python Client

[![CI](https://github.com/release-art/ch-api/actions/workflows/ci.yml/badge.svg)](https://github.com/release-art/ch-api/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/ch-api?logo=python&color=41bb13)](https://pypi.org/project/ch-api)

Async Python client for the Companies House API with type-safe Pydantic models, automatic pagination, and comprehensive error handling.

## Features

- Async-first with `httpx`
- Type-safe Pydantic models  
- Automatic pagination handling
- Optional rate limiting
- 98%+ test coverage

## Installation

```bash
pip install ch-api
```

## Quick Start

Example of getting company information:

    >>> async def get_company_example(client):
    ...     company = await client.get_company_profile("09370755")
    ...     return company is not None
    >>> run_async_func(get_company_example)
    True

## Key Endpoints

- **Company**: `get_company_profile()`, `get_officer_list()`, `get_company_psc_list()`, `get_company_charges()`, `get_company_filing_history()`
- **Search**: `search_companies()`, `search_officers()`, `search_disqualified_officers()`
- **Sandbox**: `create_test_company()` (TEST_API_SETTINGS only)

## Pagination

List endpoints return `MultipageList` with lazy-loading:

    >>> async def search_example(client):
    ...     results = await client.search_companies("tech")
    ...     count = 0
    ...     async for company in results:
    ...         count += 1
    ...         if count >= 1:
    ...             break
    ...     return count >= 1
    >>> run_async_func(search_example)
    True

## Rate Limiting

The API allows 600 requests per 5 minutes. Use an async rate limiter:

```python doctest
>>> from asyncio_throttle import Throttler  # doctest: +SKIP
```

## Error Handling

```python doctest
>>> import httpx  # doctest: +SKIP
```

## Advanced Usage

### Sandbox Environment

```python doctest
>>> from ch_api import Client, api_settings  # doctest: +SKIP
```

### Custom HTTP Session

```python doctest
>>> import httpx  # doctest: +SKIP
```

## Requirements

- Python 3.11+
- httpx >= 0.28.1
- pydantic >= 2.12.5

## Documentation

- [Full API Docs](https://docs.release.art/ch-api/)
- [API Overview](docs/sources/api-overview.rst)
- [Usage Guide](docs/sources/usage.rst)
- [Contributing](docs/sources/contributing.rst)

## License

[MIT License](LICENSE) - See LICENSE file for details

## Contributing

Please see [CONTRIBUTING](docs/sources/contributing.rst) for development guidelines.


