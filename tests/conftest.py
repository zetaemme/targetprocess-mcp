import os
import pytest

os.environ["TARGETPROCESS_URL"] = "https://test.tpondemand.com"
os.environ["TARGETPROCESS_TOKEN"] = "test-token"


@pytest.fixture(autouse=True)
def mock_config():
    """Mock configuration for tests."""
    import importlib
    import targetprocess_mcp.config

    importlib.reload(targetprocess_mcp.config)
    yield
