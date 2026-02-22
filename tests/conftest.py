"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class BaseTestCase:
    """Base test class with common configuration."""

    BASE_URL = "https://test.tpondemand.com"
    BASE_API_URL = "https://test.tpondemand.com/api/v1"
    TEST_TOKEN = "test-token"


class ConfigMixin:
    """Mixin for configuration mocking."""

    def create_mock_config(
        self,
        targetprocess_url: str = "https://test.tpondemand.com",
        targetprocess_token: str = "test-token",
        api_base: str = "https://test.tpondemand.com/api/v1",
        vpn_required: bool = False,
        vpn_check_hosts: list[str] | None = None,
    ) -> MagicMock:
        """Create a mock config object."""
        mock_cfg = MagicMock()
        mock_cfg.targetprocess_url = targetprocess_url
        mock_cfg.targetprocess_token = targetprocess_token
        mock_cfg.api_base = api_base
        mock_cfg.vpn_required = vpn_required
        mock_cfg.vpn_check_hosts = vpn_check_hosts or []
        return mock_cfg

    def mock_config(self, **kwargs) -> patch:
        """Create a context manager for patching config."""
        mock_cfg = self.create_mock_config(**kwargs)
        return patch("targetprocess_mcp.config.config", mock_cfg)


@pytest.fixture
def mock_config():
    """Mock configuration for client tests."""
    mock_cfg = MagicMock()
    mock_cfg.targetprocess_url = "https://test.tpondemand.com"
    mock_cfg.targetprocess_token = "test-token"
    mock_cfg.api_base = "https://test.tpondemand.com/api/v1"
    mock_cfg.vpn_required = False

    with patch("targetprocess_mcp.config.config", mock_cfg):
        with patch("targetprocess_mcp.config.check_vpn", return_value=True):
            yield


@pytest.fixture
def client(mock_config):
    """Create test client."""
    from targetprocess_mcp.client import TargetProcessClient

    return TargetProcessClient(base_url="https://test.tpondemand.com/api/v1", token="test-token")
