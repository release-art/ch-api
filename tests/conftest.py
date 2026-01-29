import os
import pathlib
from base64 import b64encode

import pytest
import pytest_asyncio

import ch_api

pytest_plugins = [
    "tests.test_plugins.mock_session",
]


@pytest.fixture
def test_api_key():
    return os.getenv("CH_API_KEY", "mock-test-key")


@pytest.fixture(autouse=True)
def _raise_on_extra_settings_override():
    """Fixture to override the global model settings to 'forbid' during tests."""
    orig_value = ch_api.types.base.BaseModel.model_config["extra"]
    ch_api.types.base.BaseModel.model_config["extra"] = "forbid"
    yield
    ch_api.types.base.BaseModel.model_config["extra"] = orig_value


@pytest.fixture
def test_resources_path() -> pathlib.Path:
    out = pathlib.Path(__file__).parent / "resources"
    assert out.is_dir(), f"Test resources path does not exist: {out}"
    return out.resolve()


@pytest_asyncio.fixture
async def live_env_test_client(test_api_key, test_resources_path, caching_session_subclass):
    userpass = b":".join((test_api_key.encode("ascii"), b""))
    token = b64encode(userpass).decode()
    async with caching_session_subclass(
        headers={
            "ACCEPT": "application/json",
            "Authorization": f"Basic {token}",
        },
        cache_dir=test_resources_path,
        cache_mode="fetch_missing",
    ) as api_session:
        yield ch_api.api.Client(
            credentials=api_session,
            settings=ch_api.api_settings.LIVE_API_SETTINGS,
        )
