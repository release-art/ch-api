import pytest
import pathlib

@pytest.fixture
def test_resources_path() -> pathlib.Path:
    out = pathlib.Path(__file__).parent / "resources" / 'tests'
    assert out.is_dir(), f"Test resources path does not exist: {out}"
    return out.resolve()