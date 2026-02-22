"""Tests for configuration."""

import pytest
from unittest.mock import MagicMock, patch

from tests.conftest import BaseTestCase, ConfigMixin


class TestVPNCheck(BaseTestCase, ConfigMixin):
    """Tests for VPN check functionality."""

    def test_check_vpn_not_required(self):
        """Test VPN check when not required."""
        mock_cfg = self.create_mock_config(vpn_required=False)

        with patch("targetprocess_mcp.config.config", mock_cfg):
            from targetprocess_mcp.config import check_vpn

            assert check_vpn() is True

    def test_check_vpn_no_hosts(self):
        """Test VPN check with no hosts configured."""
        mock_cfg = self.create_mock_config(vpn_required=True, vpn_check_hosts=[])

        with patch("targetprocess_mcp.config.config", mock_cfg):
            from targetprocess_mcp.config import check_vpn

            assert check_vpn() is True


class TestLoadConfig(BaseTestCase):
    """Tests for configuration loading."""

    def test_load_config_missing_file(self):
        """Test config loading when file doesn't exist."""
        with patch("targetprocess_mcp.config.CONFIG_DIR") as mock_dir:
            mock_dir.exists.return_value = False
            from targetprocess_mcp.config import load_config

            result = load_config()
            assert result == {}


class TestConfig(BaseTestCase, ConfigMixin):
    """Tests for _Config class."""

    def test_targetprocess_url_from_env(self):
        """Test URL from environment variable."""
        with patch("targetprocess_mcp.config.load_config", return_value={}):
            with patch.dict(
                "targetprocess_mcp.config.os.environ", {"TARGETPROCESS_URL": "https://env.com"}
            ):
                from targetprocess_mcp.config import config

                assert config.targetprocess_url == "https://env.com"

    def test_targetprocess_url_from_config(self):
        """Test URL from config file when env not set."""
        with patch(
            "targetprocess_mcp.config.load_config", return_value={"URL": "https://config.com"}
        ):
            with patch.dict("targetprocess_mcp.config.os.environ", {}, clear=True):
                from targetprocess_mcp.config import config

                assert config.targetprocess_url == "https://config.com"

    def test_vpn_required_from_env(self):
        """Test VPN_REQUIRED from environment variable."""
        with patch("targetprocess_mcp.config.load_config", return_value={}):
            with patch.dict(
                "targetprocess_mcp.config.os.environ", {"TARGETPROCESS_VPN_REQUIRED": "true"}
            ):
                from targetprocess_mcp.config import config

                assert config.vpn_required is True

    def test_vpn_required_from_config(self):
        """Test VPN_REQUIRED from config when env not set."""
        with patch("targetprocess_mcp.config.load_config", return_value={"VPN_REQUIRED": True}):
            with patch.dict("targetprocess_mcp.config.os.environ", {}, clear=True):
                from targetprocess_mcp.config import config

                assert config.vpn_required is True
