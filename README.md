# Companies House API Python Client

A comprehensive, asynchronous Python client for the Companies House API, providing real-time access to UK company information including profiles, officers, charges, filing history, and persons with significant control.

## Features

- Full async/await support using httpx
- Automatic pagination handling for large result sets
- Type-safe Pydantic models for all API responses
- Support for all Companies House API endpoints
- Optional rate limiting support
- Comprehensive error handling
- Production-ready and well-tested

## Supported Data

The client provides access to:

- Company profiles and status information
- Registered office addresses
- Director and officer information
- Officer appointment history
- Persons with Significant Control (PSC)
- Charges over company assets
- Filing history and documents
- Financial accounts information
- Exemptions from filing
- Insolvency proceedings
- Disqualified officers
- UK branch establishments

## Installation

Install from PyPI:

```bash
pip install ch-api
```

Or install from source:

```bash
git clone https://github.com/release-art/ch-api.git
cd ch-api
pip install -e .
```

## Requirements

- Python 3.11 or later
- httpx >= 0.28.1
- pydantic >= 2.12.5

## Quick Start

### 1. Get an API Key

Register at the Companies House Developer Portal to obtain your API key:
https://developer.company-information.service.gov.uk/

### 2. Create a Client

```python
from ch_api import Client, api_settings

# Create authentication settings
auth = api_settings.AuthSettings(api_key="your-api-key")

# Create the client (uses production API by default)
client = Client(credentials=auth)
```

### 3. Fetch Company Information

```python
# Get company profile
company = await client.get_company_profile("09370755")
print(f"Company: {company.company_name}")
print(f"Status: {company.company_status}")
print(f"Type: {company.company_type}")

# Get registered office address
address = await client.registered_office_address("09370755")
print(f"Address: {address.address_line_1}")
print(f"Postcode: {address.postal_code}")
```

### 4. Search for Companies

```python
# Simple search
results = await client.search_companies("Apple")
print(f"Total results: {len(results)}")

# Iterate through results (pages fetched automatically)
async for company in results:
    print(f"{company.title} ({company.company_number})")

# Access specific results by index
if len(results) > 0:
    first = results[0]
    print(f"First result: {first.title}")
```

### 5. Get Company Officers

```python
# Get list of officers
officers = await client.get_officer_list("09370755")

# Iterate through officers
async for officer in officers:
    print(f"{officer.name}")
    print(f"  Appointed: {officer.appointed_on}")
    print(f"  Role: {officer.officer_role}")

# Filter by officer type
directors = await client.get_officer_list(
    "09370755",
    only_type="directors"
)
```

### 6. Get Filing History

```python
# Get all filing history
filings = await client.get_company_filing_history("09370755")

# Iterate through filings
async for filing in filings:
    print(f"{filing.type} - {filing.date}")

# Filter by category
accounts = await client.get_company_filing_history(
    "09370755",
    categories=("accounts", "annual-return")
)
```

### 7. Get Charges

```python
# Get all charges
charges = await client.get_company_charges("09370755")

for charge in charges.items or []:
    print(f"Charge {charge.charge_number}")
    print(f"  Type: {charge.charge_code}")
    print(f"  Date: {charge.created_on}")

# Get specific charge details
details = await client.get_company_charge_details("09370755", "charge-id")
```

### 8. Get Persons with Significant Control

```python
# Get PSC list
psc_list = await client.get_company_psc_list("09370755")

# Iterate through PSCs
async for psc in psc_list.items:
    print(f"{psc.name}")
    print(f"  Nature of control: {psc.nature_of_control}")

# Get specific PSC details
psc = await client.get_company_individual_psc("09370755", "psc-id")
```

## Advanced Usage

### Using Different Environments

Switch between production and sandbox environments:

```python
from ch_api import Client, api_settings

auth = api_settings.AuthSettings(api_key="your-api-key")

# Production (default)
client = Client(credentials=auth, settings=api_settings.LIVE_API_SETTINGS)

# Sandbox for testing
client = Client(credentials=auth, settings=api_settings.TEST_API_SETTINGS)
```

### Rate Limiting

Control API request rate with asyncio-throttle or similar:

```python
from ch_api import Client, api_settings
import asyncio_throttle

auth = api_settings.AuthSettings(api_key="your-api-key")

# Create rate limiter (max 2 requests per second)
limiter = asyncio_throttle.AsyncThrottle(max_rate=2, time_period=1.0)

# Create client with rate limiter
client = Client(
    credentials=auth,
    api_limiter=lambda: limiter
)
```

### Advanced Company Search

Perform advanced searches with multiple filters:

```python
import datetime

results = await client.advanced_company_search(
    company_name_includes="Technology",
    company_name_excludes="Holdings",
    company_status="active",
    company_type="private-unlimited",
    location="England",
    sic_codes=["62012"],
    incorporated_from=datetime.date(2020, 1, 1),
    max_results=100
)

async for company in results:
    print(f"{company.company_name}")
```

### Alphabetical Search

Browse companies alphabetically:

```python
results = await client.alphabetical_companies_search(
    query="BBC",
    page_size=20
)

async for company in results:
    print(f"{company.title}")
```

### Dissolved Company Search

Search for dissolved or historical companies:

```python
results = await client.search_dissolved_companies(
    query="Enron",
    search_type="best-match"
)

async for company in results:
    print(f"{company.title}")
    print(f"  Dissolved: {company.date_of_dissolution}")
```

### Prefetch All Pages

For better performance with bulk operations, prefetch all pages:

```python
results = await client.search_companies("Technology")

# Fetch all pages at once
await results.fetch_all_pages()

# Access all items without further API calls
for item in results.local_items():
    process(item)
```

## API Reference

### Client Methods

#### Company Information

- `get_company_profile(company_number)` - Get company profile
- `registered_office_address(company_number)` - Get registered office address
- `get_company_registers(company_number)` - Get company registers information

#### Officers

- `get_officer_list(company_number, only_type=None, order_by=None)` - Get officers list
- `get_officer_appointment(company_number, appointment_id)` - Get officer appointment details
- `get_officer_appointments(officer_id)` - Get officer's appointments across companies
- `get_corporate_officer_disqualification(officer_id)` - Get corporate disqualification
- `get_natural_officer_disqualification(officer_id)` - Get natural person disqualification

#### Persons with Significant Control

- `get_company_psc_list(company_number)` - Get PSC list
- `get_company_psc_statements(company_number)` - Get PSC statements
- `get_company_individual_psc(company_number, psc_id)` - Get individual PSC
- `get_company_corporate_psc(company_number, psc_id)` - Get corporate PSC
- `get_company_legal_person_psc(company_number, psc_id)` - Get legal person PSC
- Additional PSC-related methods for beneficial owners and super-secure PSCs

#### Financial & Legal

- `get_company_charges(company_number)` - Get all charges
- `get_company_charge_details(company_number, charge_id)` - Get charge details
- `get_company_filing_history(company_number, categories=None)` - Get filing history
- `get_filing_history_item(company_number, filing_id)` - Get filing details
- `get_company_exemptions(company_number)` - Get exemptions
- `get_company_insolvency(company_number)` - Get insolvency information

#### Search

- `search(query)` - General search (companies and officers)
- `search_companies(query)` - Search companies
- `search_officers(query)` - Search officers
- `search_disqualified_officers(query)` - Search disqualified officers
- `advanced_company_search(...)` - Advanced search with filters
- `alphabetical_companies_search(query)` - Alphabetical search
- `search_dissolved_companies(query)` - Search dissolved companies

#### Other

- `get_company_uk_establishments(company_number)` - Get UK branch establishments
- `create_test_company(company)` - Create test company (sandbox only)

### Response Types

All API endpoints return Pydantic models providing:

- Type validation
- IDE autocomplete support
- Easy serialization/deserialization
- Helpful error messages

For detailed information about response types, see the [types documentation](src/ch_api/types/).

## Error Handling

The client defines custom exceptions:

```python
from ch_api import exc

try:
    profile = await client.get_company_profile("invalid-number")
except exc.UnexpectedApiResponseError as e:
    print(f"API response was unexpected: {e}")
except exc.CompaniesHouseApiError as e:
    print(f"API error occurred: {e}")
```

## Configuration

### Authentication Settings

```python
from ch_api.api_settings import AuthSettings

auth = AuthSettings(api_key="your-api-key")
```

### API Settings

```python
from ch_api.api_settings import LIVE_API_SETTINGS, TEST_API_SETTINGS

# Production (default)
settings = LIVE_API_SETTINGS

# Sandbox
settings = TEST_API_SETTINGS
```

## Async/Await Pattern

All client methods are asynchronous and must be called with `await`:

```python
import asyncio

async def main():
    client = Client(credentials=auth)
    
    # Use await for async methods
    profile = await client.get_company_profile("09370755")
    print(profile.company_name)
    
    # Use async for for paginated results
    results = await client.search_companies("Apple")
    async for company in results:
        print(company.title)

# Run the async function
asyncio.run(main())
```

## Pagination

List and search endpoints return `MultipageList` objects that provide:

- **Lazy loading**: Pages fetched only when accessed
- **Length checking**: `len(results)` returns total count
- **Indexing**: `results[0]` fetches items on demand
- **Async iteration**: `async for item in results`
- **All-at-once**: `await results.fetch_all_pages()`

```python
results = await client.search_companies("Apple")

# Check total without loading all pages
total = len(results)

# Iterate (loads pages as needed)
async for company in results:
    print(company.title)

# Access by index
first = results[0]

# Prefetch all
await results.fetch_all_pages()
for company in results.local_items():
    print(company.title)
```

## API Rate Limiting

The Companies House API enforces rate limits. Consider using a rate limiter:

```bash
pip install asyncio-throttle
```

```python
import asyncio_throttle

limiter = asyncio_throttle.AsyncThrottle(max_rate=5, time_period=1.0)
client = Client(credentials=auth, api_limiter=lambda: limiter)
```

## Performance Tips

1. Use prefetching for bulk operations:
   ```python
   await results.fetch_all_pages()
   ```

2. Filter results server-side when possible:
   ```python
   # Better: filter via parameters
   await client.get_officer_list("09370755", only_type="directors")
   ```

3. Use appropriate page sizes for your use case

4. Reuse client instances to maintain connection pooling

5. Consider using a rate limiter to avoid hitting API limits

## Testing

For development and testing, use the sandbox API:

```python
from ch_api import api_settings

auth = api_settings.AuthSettings(api_key="your-sandbox-key")
client = Client(credentials=auth, settings=api_settings.TEST_API_SETTINGS)

# Test data can be created in the sandbox
# See API documentation for details
```

## Project Structure

```
src/ch_api/
├── __init__.py              # Package entry point
├── api.py                   # Main Client class
├── api_settings.py          # Configuration classes
├── exc.py                   # Exception types
└── types/                   # Type definitions
    ├── base.py              # Base Pydantic model
    ├── field_types.py       # Custom field types
    ├── shared.py            # Shared types
    ├── settings.py          # Global configuration
    ├── pagination/          # Pagination types
    ├── public_data/         # API response models
    │   ├── company_profile.py
    │   ├── search.py
    │   ├── company_officers.py
    │   ├── charges.py
    │   ├── filing_history.py
    │   ├── psc.py
    │   └── ...
    └── compound_api_types/  # Complex wrappers
```

## Documentation

- Complete API reference with docstrings: `src/ch_api/`
- Type documentation: `src/ch_api/types/`
- Companies House API: https://developer-specs.company-information.service.gov.uk/
- API Swagger specs: https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/swagger.json

## Common Patterns

### Fetch and Process All Companies in a List

```python
results = await client.search_companies("Technology")
await results.fetch_all_pages()

for company in results.local_items():
    profile = await client.get_company_profile(company.company_number)
    print(f"{profile.company_name}: {profile.company_status}")
```

### Monitor Company Changes

```python
async def check_company_status(company_number, interval_hours=24):
    import asyncio
    
    client = Client(credentials=auth)
    
    while True:
        profile = await client.get_company_profile(company_number)
        print(f"Status: {profile.company_status}")
        
        await asyncio.sleep(interval_hours * 3600)
```

### Export Company Data

```python
import json

company = await client.get_company_profile("09370755")

# Pydantic models serialize to dict/JSON easily
company_dict = company.model_dump()
company_json = company.model_dump_json()

print(json.dumps(company_dict, indent=2))
```

## Troubleshooting

### Authentication Error

Ensure your API key is correct:
```python
auth = api_settings.AuthSettings(api_key="your-correct-key")
```

### Rate Limit Error

Implement rate limiting:
```python
from ch_api import Client, api_settings
import asyncio_throttle

limiter = asyncio_throttle.AsyncThrottle(max_rate=2, time_period=1.0)
client = Client(credentials=auth, api_limiter=lambda: limiter)
```

### No Results Found

Check company number format (8 alphanumeric characters):
```python
profile = await client.get_company_profile("09370755")  # Correct format
```

### Timeout Errors

Use a custom httpx.AsyncClient with timeout settings:
```python
import httpx
from ch_api import Client, api_settings

auth = api_settings.AuthSettings(api_key="your-key")
http_client = httpx.AsyncClient(timeout=30.0)
client = Client(credentials=http_client)
```

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code follows project style
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:

- GitHub Issues: https://github.com/yourusername/ch-api/issues
- Companies House API Support: https://developer-specs.company-information.service.gov.uk/
- Companies House Developer Forum: https://forum.aws.chdev.org/

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## Related Projects

- [Companies House API Enumerations](https://github.com/companieshouse/api-enumerations)
- Official API Documentation: https://developer-specs.company-information.service.gov.uk/
- Companies House: https://www.companieshouse.gov.uk/

