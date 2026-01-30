"""Unit tests for API client initialization and credential handling."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from ch_api import api, api_settings, exc


class TestClientInitialization:
    """Test Client.__init__ with various credential types."""

    def test_init_with_auth_settings(self):
        """Test initialization with AuthSettings credentials."""
        auth = api_settings.AuthSettings(api_key="test-key-123")
        client = api.Client(credentials=auth)

        assert client._api_session is not None
        assert isinstance(client._api_session, httpx.AsyncClient)
        assert client._api_limiter == api._noop_limiter
        assert client._settings == api_settings.LIVE_API_SETTINGS

    def test_init_with_auth_settings_and_custom_settings(self):
        """Test initialization with AuthSettings and custom API settings."""
        auth = api_settings.AuthSettings(api_key="test-key-456")
        custom_settings = api_settings.TEST_API_SETTINGS

        client = api.Client(credentials=auth, settings=custom_settings)

        assert client._api_session is not None
        assert client._settings == custom_settings

    def test_init_with_httpx_client(self):
        """Test initialization with pre-configured httpx.AsyncClient."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        client = api.Client(credentials=mock_client)

        assert client._api_session == mock_client
        assert client._api_limiter == api._noop_limiter

    @pytest.mark.asyncio
    @pytest.mark.parametrize("owns_session", [True, False])
    async def test_init_with_httpx_client_and_owns_session(self, mocker, owns_session):
        mock_client = MagicMock(spec=httpx.AsyncClient)
        if owns_session:
            auth = api_settings.AuthSettings(api_key="test-key-456")
        else:
            auth = mock_client

        mocker.patch.object(httpx.AsyncClient, "__init__", return_value=None)
        mock_aclose = mocker.patch.object(httpx.AsyncClient, "aclose", new_callable=AsyncMock)

        async with api.Client(auth):
            pass

        if owns_session:
            # owns session => create the AsyncClient by itself
            mock_aclose.assert_called_once()
        else:
            mock_client.aclose.assert_not_called()
            mock_aclose.assert_not_called()

    def test_init_with_custom_api_limiter(self):
        """Test initialization with custom API limiter."""
        auth = api_settings.AuthSettings(api_key="test-key")

        async def custom_limiter():
            yield

        client = api.Client(credentials=auth, api_limiter=custom_limiter)

        assert client._api_limiter == custom_limiter

    def test_init_with_invalid_credentials_type(self):
        """Test initialization fails with invalid credential type."""
        with pytest.raises(ValueError) as exc_info:
            api.Client(credentials="invalid-string")

        assert "credentials must be either" in str(exc_info.value)
        assert "got str instead" in str(exc_info.value)

    def test_init_with_invalid_credentials_tuple(self):
        """Test initialization fails when credentials are a tuple."""
        with pytest.raises(ValueError) as exc_info:
            api.Client(credentials=("username", "password"))

        assert "credentials must be either" in str(exc_info.value)

    def test_init_with_invalid_credentials_dict(self):
        """Test initialization fails when credentials are a dict."""
        with pytest.raises(ValueError) as exc_info:
            api.Client(credentials={"api_key": "test"})

        assert "credentials must be either" in str(exc_info.value)

    def test_init_with_none_credentials(self):
        """Test initialization fails when credentials are None."""
        with pytest.raises(ValueError) as exc_info:
            api.Client(credentials=None)

        assert "credentials must be either" in str(exc_info.value)


class TestExecuteRequestMethod:
    """Test Client._execute_request method."""

    @pytest.mark.asyncio
    async def test_execute_request_with_valid_response(self):
        """Test _execute_request with valid response and expected model."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create mock response
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b'{"key": "value"}'
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None

        # Create mock request
        mock_request = MagicMock(spec=httpx.Request)

        # Mock the session
        client._api_session.send = AsyncMock(return_value=mock_response)

        # Mock a simple model for testing
        mock_model = MagicMock()
        mock_model.model_validate.return_value = {"validated": "data"}

        result = await client._execute_request(mock_request, mock_model)

        assert result == {"validated": "data"}
        mock_response.raise_for_status.assert_called_once()
        client._api_session.send.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_execute_request_with_no_expected_output(self):
        """Test _execute_request when no response body is expected."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create mock response
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 204
        mock_response.raise_for_status.return_value = None

        # Create mock request
        mock_request = MagicMock(spec=httpx.Request)

        # Mock the session
        client._api_session.send = AsyncMock(return_value=mock_response)

        result = await client._execute_request(mock_request, None)

        assert result is None

    @pytest.mark.asyncio
    async def test_execute_request_with_no_content_status_and_expected_output(self):
        """Test _execute_request raises error on NO_CONTENT status when output expected."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create mock response with NO_CONTENT status
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 204  # httpx.codes.NO_CONTENT
        mock_response.raise_for_status.return_value = None

        # Create mock request
        mock_request = MagicMock(spec=httpx.Request)

        # Mock the session
        client._api_session.send = AsyncMock(return_value=mock_response)

        # Mock a model that expects data
        mock_model = MagicMock()

        with pytest.raises(exc.UnexpectedApiResponseError) as exc_info:
            await client._execute_request(mock_request, mock_model)

        assert "Expected response body but got status code 204" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_request_with_empty_content(self):
        """Test _execute_request raises error on empty content when output expected."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create mock response with empty content
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b""
        mock_response.raise_for_status.return_value = None

        # Create mock request
        mock_request = MagicMock(spec=httpx.Request)

        # Mock the session
        client._api_session.send = AsyncMock(return_value=mock_response)

        # Mock a model that expects data
        mock_model = MagicMock()

        with pytest.raises(exc.UnexpectedApiResponseError) as exc_info:
            await client._execute_request(mock_request, mock_model)

        assert "Expected response body but got empty content" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_request_with_http_error(self):
        """Test _execute_request propagates HTTP errors."""
        auth = api_settings.AuthSettings(api_key="test-key")
        client = api.Client(credentials=auth)

        # Create mock response that raises on raise_for_status
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=mock_response
        )

        # Create mock request
        mock_request = MagicMock(spec=httpx.Request)

        # Mock the session
        client._api_session.send = AsyncMock(return_value=mock_response)

        with pytest.raises(httpx.HTTPStatusError):
            await client._execute_request(mock_request, None)


class TestNoopLimiter:
    """Test the _noop_limiter context manager."""

    @pytest.mark.asyncio
    async def test_noop_limiter_yields_none(self):
        """Test that _noop_limiter is a valid async context manager."""
        async with api._noop_limiter() as result:
            assert result is None
