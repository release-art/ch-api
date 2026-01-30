"""API settings and authentication configuration for Companies House API client.

This module provides configuration classes for API endpoints and authentication
credentials for the Companies House API client.

The Companies House provides two API environments:

- **Live API**: For production use with real company data
- **Test/Sandbox API**: For development and testing with test data

Authentication:
    All API calls require an API key obtained from the Companies House Developer Portal.
    Register your application at: https://developer.company-information.service.gov.uk/

Example:
    Configure the client with live API settings::

        >>> from ch_api import api_settings
        >>> auth = api_settings.AuthSettings(api_key="your-api-key")
        >>> # Uses LIVE_API_SETTINGS by default

    Use sandbox for testing::

        >>> from ch_api import api_settings
        >>> auth = api_settings.AuthSettings(api_key="your-test-key")
        >>> # client = Client(credentials=auth, settings=api_settings.TEST_API_SETTINGS)

See Also:
    - https://developer-specs.company-information.service.gov.uk/guides/authorisation
    - https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
"""

import dataclasses

__all__ = [
    "AuthSettings",
    "ApiSettings",
    "LIVE_API_SETTINGS",
    "TEST_API_SETTINGS",
]


@dataclasses.dataclass(frozen=True, kw_only=True)
class AuthSettings:
    """API key authentication credentials for Companies House API.

    The API key serves as your unique identifier and authentication token
    for all API requests. Treat it as a sensitive credential.

    Attributes
    ----------
    api_key : str
        Your Companies House API key obtained from the Developer Portal.
        Used for HTTP Basic Authentication (as the username, with empty password).

    Example
    -------
    Create authentication settings::

        auth = AuthSettings(api_key="your-api-key-here")

    Note
    ----
    - API keys can be obtained from https://developer.company-information.service.gov.uk/
    - Never commit API keys to version control
    - Use environment variables or secure credential management for production

    See Also
    --------
    https://developer-specs.company-information.service.gov.uk/guides/authorisation
    """

    api_key: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class ApiSettings:
    """Configuration for Companies House API endpoints and environments.

    This dataclass contains the URLs for different API environments and services.
    Use ``LIVE_API_SETTINGS`` for production or ``TEST_API_SETTINGS`` for
    sandbox testing.

    Attributes
    ----------
    api_url : str
        Base URL for the main Companies House API endpoint.
        - Production: ``https://api.company-information.service.gov.uk``
        - Sandbox: ``https://api-sandbox.company-information.service.gov.uk``

    identity_url : str
        Base URL for the identity/authentication service.
        - Production: ``https://identity.company-information.service.gov.uk``
        - Sandbox: ``https://identity-sandbox.company-information.service.gov.uk``

    test_data_generator_url : str, optional
        Base URL for the Test Data Generator API (sandbox only).
        - Production: ``None`` (not available)
        - Sandbox: ``https://test-data-sandbox.company-information.service.gov.uk``

        This service allows creating mock companies for testing in the sandbox environment.

    Example
    -------
    Use predefined settings::

        from ch_api import Client, api_settings

        # Production settings (default)
        client = Client(
            credentials=auth,
            settings=api_settings.LIVE_API_SETTINGS
        )

        # Sandbox settings for testing
        client = Client(
            credentials=test_auth,
            settings=api_settings.TEST_API_SETTINGS
        )

    See Also
    --------
    LIVE_API_SETTINGS : Production API configuration
    TEST_API_SETTINGS : Sandbox API configuration
    """

    api_url: str
    identity_url: str
    test_data_generator_url: str | None = None


#: Production API settings for live company data.
#:
#: Use this for accessing real, up-to-date company information.
#: Requires a valid production API key from Companies House.
#:
#: API Base: https://api.company-information.service.gov.uk
#:
#: See Also:
#:     https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
LIVE_API_SETTINGS = ApiSettings(
    api_url="https://api.company-information.service.gov.uk",
    identity_url="https://identity.company-information.service.gov.uk",
)

#: Sandbox/test API settings for development and testing.
#:
#: Use this environment with test API keys to develop and test your application
#: without affecting production data. The sandbox includes the Test Data Generator
#: service for creating mock companies.
#:
#: API Base: https://api-sandbox.company-information.service.gov.uk
#: Test Data Generator: https://test-data-sandbox.company-information.service.gov.uk
#:
#: Note:
#:     Test companies created in the sandbox are temporary and not available
#:     in the production API.
#:
#: See Also:
#:     https://developer-specs.company-information.service.gov.uk/guides/gettingStarted
TEST_API_SETTINGS = ApiSettings(
    api_url="https://api-sandbox.company-information.service.gov.uk",
    identity_url="https://identity-sandbox.company-information.service.gov.uk",
    test_data_generator_url="https://test-data-sandbox.company-information.service.gov.uk",
)
