# AI Coding Agent Instructions for ch-api

## Project Overview

**ch-api** is an async-first Python client for the Companies House API providing real-time UK company data. It's a production-ready library with full type safety (Pydantic models), automatic pagination handling, and comprehensive error management.

**Key Stack:**
- Python 3.11+ with async/await (httpx for HTTP)
- Pydantic v2 for validation and type safety
- PDM for package management and testing
- Fully async API with no blocking operations

## Architecture

### Core Components

1. **[src/ch_api/api.py](src/ch_api/api.py)** - Main `Client` class
   - Async-first design: all methods are `async def`
   - Handles HTTP session management, auth, rate limiting, pagination
   - ~1300 lines covering all Companies House API endpoints
   - Returns `MultipageList` for list endpoints (lazy-loaded pagination)

2. **[src/ch_api/types/](src/ch_api/types/)** - Pydantic models hierarchy
   - `base.py`: Custom `BaseModel` with automatic field name normalization (API returns mixed case)
   - `compound_api_types/`: Complex nested data structures (officers, PSC, filing history)
   - `pagination/`: `MultipageList` generic container for paginated responses
   - Field types validate API response formats (e.g., dates, company numbers)

3. **[src/ch_api/types/pagination/paginated_list.py](src/ch_api/types/pagination/paginated_list.py)** - `MultipageList` class
   - Generic lazy-loading list for paginated API responses
   - Supports: `len()`, `[index]`, `async for`, slicing
   - Automatic page fetching with `asyncio.Lock` for thread safety
   - Key methods: `async __aiter__`, `__getitem__`, `fetch_all_pages()`
   - Example: `async for company in results:` only fetches pages on demand

4. **[src/ch_api/api_settings.py](src/ch_api/api_settings.py)** - Configuration
   - `AuthSettings(api_key)`: Authentication credentials
   - `ApiSettings`: Endpoint URLs for LIVE/TEST environments
   - Sandbox support for development with test data generator

### Data Flow

```
Client method → MultipageList(fetch_page_callback) → 
  _async_init() [fetch first page] → 
  lazy_load on access/iteration → 
  Pydantic validation → typed model instances
```

## Critical Patterns

### Async/Await Requirements
- **All API calls are async**: Never call `client.get_*()` without `await`
- **Pagination is async**: `async for company in results:` not `for`
- **Error handling**: Use try/except with async context managers
- Use `asyncio.run()` for scripts or `async with` for clients

### Pydantic Model Customization
- Inherit from `ch_api.types.base.BaseModel`, not `pydantic.BaseModel`
- Custom `model_validate()` normalizes field names to lowercase (API inconsistency)
- Models in `types/` define all API response structures; don't create ad-hoc dicts

### Pagination
- **MultipageList** is generic: `MultipageList[Officer]`, `MultipageList[Company]`
- Lazy by default: pages only fetch when accessed
- Call `await results.fetch_all_pages()` for bulk processing to fetch upfront
- Access: `results[0]` for first item, `results[10:20]` for slice, `len(results)` for total
- **Example pattern:**
  ```python
  results = await client.search_companies("Apple")
  print(len(results))  # Fetches first page automatically
  async for company in results:
      print(company.title)  # Loads next page when needed
  ```

### Field Name Normalization
- API returns mixed-case fields: `{"CompanyName": "...", "company_number": "..."}`
- `BaseModel.model_validate()` automatically normalizes to lowercase
- Model definitions use snake_case: `company_name`, `company_number`
- Never manually case-convert; trust the base model

## Development Workflows

### Helper Scripts in bin/

All development utilities are in `bin/` directory:

**bin/run.sh** - Wrapper that injects API keys via 1Password
- Fetches `CH_API_KEY` from 1Password vault automatically
- Use this as prefix: `bin/run.sh <any-command>`
- Example: `bin/run.sh pdm run pytest`
- Eliminates need to manually manage API keys

**bin/test.sh** - Test runner with coverage
- Wraps `bin/run.sh pdm run pytest` with API key injection
- Runs full test suite with coverage reports (xml, html, terminal)
- Pass pytest args: `bin/test.sh tests/unit/test_api_client.py -v`
- Coverage config in `pyproject.toml`: target >85%

**bin/autoformat.sh** - Code formatter and linter
- Runs `ruff format` then `ruff check --fix` on src/ and tests/
- Config in `pyproject.toml`: target-version=py313, 120-char lines
- Always run before committing to ensure code quality

### Testing
```bash
# Run all tests with coverage (recommended)
bin/test.sh

# Run specific test file or directory
bin/test.sh tests/unit/test_api_client.py
bin/test.sh tests/integration/

# Run with pytest options
bin/test.sh -v -k "test_search"

# Manual pytest (needs API key set)
export CH_API_KEY="your-key"
pdm run pytest
```
**Test structure:** `tests/unit/` for mocked, `tests/integration/` for live API calls
**Fixtures:** `tests/conftest.py` provides shared fixtures

### Code Quality
```bash
# Format and lint (always use this)
bin/autoformat.sh

# Check without fixing
pdm run ruff check src tests
```

### Running Commands with API Keys
```bash
# Use bin/run.sh to auto-inject API keys from 1Password
bin/run.sh python my_script.py
bin/run.sh pdm run <command>

# Or set manually for one-off commands
export CH_API_KEY="your-api-key"
```

## Common Modifications

### Adding a New API Endpoint
1. Add Pydantic model in `src/ch_api/types/compound_api_types/` or `public_data/`
2. Create async method in `Client` that returns typed model or `MultipageList[Model]`
3. Use internal `_fetch_model()` or `_fetch_paginated_list()` helpers
4. Add unit test mocking httpx response, integration test with sandbox API

### Extending Pagination Types
- Subclass `MultipageList[T]` or create wrapper in `types/compound_api_types/public_data/pagination.py`
- `_PaginatedEntityInitCls` shows pattern for custom item conversion
- Always implement `async_init()` for deferred initialization

### Modifying Type Models
- Update Pydantic field definitions in appropriate `types/` module
- Run `pdm run pytest` to validate against real API fixtures
- Field name normalization handles API inconsistencies; don't add custom validators unless necessary

## Key Files Reference

| File | Purpose |
|------|---------|
| [src/ch_api/api.py](src/ch_api/api.py) | Main Client class (1300+ lines) |
| [src/ch_api/types/base.py](src/ch_api/types/base.py) | BaseModel with auto field normalization |
| [src/ch_api/types/pagination/paginated_list.py](src/ch_api/types/pagination/paginated_list.py) | MultipageList generic container |
| [src/ch_api/types/compound_api_types/](src/ch_api/types/compound_api_types/) | Complex nested types (officers, PSC, etc.) |
| [src/ch_api/api_settings.py](src/ch_api/api_settings.py) | Auth + endpoint configuration |
| [src/ch_api/exc.py](src/ch_api/exc.py) | Custom exception hierarchy |
| [tests/unit/test_api_client.py](tests/unit/test_api_client.py) | Core client tests |
| [tests/integration/](tests/integration/) | Live sandbox API tests |

## Integration Points

- **Authentication**: HTTP Basic Auth via `AuthSettings.api_key`
- **Rate Limiting**: Optional `limiter` parameter in `Client.__init__()` (not built-in)
- **Environments**: LIVE_API_SETTINGS (production) vs TEST_API_SETTINGS (sandbox)
- **Test Data Generator**: Sandbox-only endpoint for creating mock companies

## Non-Obvious Conventions

1. **All list endpoints return MultipageList, not plain lists** - even single-page results
2. **Async initialization is deferred** - `MultipageList` requires `await _async_init()` before use
3. **Field names auto-normalize in model_validate()** - API inconsistency workaround, don't replicate
4. **Negative indexing not supported** - `results[-1]` raises IndexError; use `results[len(results)-1]`
5. **Settings are frozen dataclasses** - immutable by design for thread safety
6. **No context manager for Client** - session management is manual; call `client._api_session.aclose()`
