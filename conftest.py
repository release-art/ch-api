"""This is a very top-level conftest.py (applies to all tests, including doctests)."""

import asyncio
import inspect
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
    out = pathlib.Path(__file__).parent / "tests" / "resources" / "doctests"
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


@pytest.fixture(autouse=True)
def add_np(doctest_namespace, request):
    async def run_async_func_impl(func, kwargs):
        # raise Exception(kwargs)
        return await func(**kwargs)
    
    def run_async_func(func):
        """Run async function with pytest fixtures auto-injected based on parameters."""
        sig = inspect.signature(func)
        kwargs = {}
        for param_name in sig.parameters:
            actual_fixture_name = {
                # Substitute long fixture names with shorter param names
                # for doctests
                'client': 'live_env_test_client',
            }.get(param_name, param_name)
            kwargs[param_name] = request.getfixturevalue(actual_fixture_name)

        coro = run_async_func_impl(func, kwargs)
        try:
            # Reuse the current event loop if available
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(coro)
        except RuntimeError:
            # No running loop, create a new one
            return asyncio.run(coro, debug=True)
    
    doctest_namespace["run_async_func"] = run_async_func
