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

```python
from ch_api import Client, api_settings

# Get API key at https://developer.company-information.service.gov.uk/
auth = api_settings.AuthSettings(api_key="your-api-key")
client = Client(credentials=auth)

# Get company profile
company = await client.get_company_profile("09370755")
print(f"{company.company_name} - {company.company_status}")

# Search companies
results = await client.search_companies("Apple")
async for company in results:
    print(company.title)

# Get officers
officers = await client.get_company_officers("09370755")
async for officer in officers:
    print(f"{officer.name} ({officer.officer_role})")

# Get persons with significant control
pscs = await client.get_company_pscs("09370755")
async for psc in pscs:
    print(f"{psc.name} - Control: {psc.natures_of_control}")
```

## Key Endpoints

- **Company**: `get_company_profile()`, `get_company_officers()`, `get_company_pscs()`, `get_company_charges()`, `get_company_filing_history()`
- **Search**: `search_companies()`, `search_officers()`, `search_disqualified_officers()`
- **Sandbox**: `create_test_company()` (TEST_API_SETTINGS only)

## Pagination

List endpoints return `MultipageList` with lazy-loading:

```python
results = await client.search_companies("tech")

# Lazy loading - pages fetched on demand
async for company in results:
    print(company.title)

# Or fetch all pages at once
await results.fetch_all_pages()
for company in results.local_items():
    print(company.title)
```

## Rate Limiting

The API allows 600 requests per 5 minutes. Use an async rate limiter:

```python
from asyncio_throttle import Throttler

throttler = Throttler(rate_limit=600, period=300)
client = Client(credentials=auth, limiter=throttler)
```

## Error Handling

```python
from ch_api.exc import NotFoundError, RateLimitError

try:
    company = await client.get_company_profile("invalid")
except NotFoundError:
    print("Company not found")
except RateLimitError:
    print("Rate limit exceeded")
```

## Advanced Usage

### Sandbox Environment

```python
client = Client(
    credentials=auth,
    settings=api_settings.TEST_API_SETTINGS
)
```

### Custom HTTP Session

```python
import httpx

session = httpx.AsyncClient(timeout=30.0)
client = Client(credentials=auth, api_session=session)
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


