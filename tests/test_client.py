import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from targetprocess_mcp.server import mcp
from targetprocess_mcp.client import TargetProcessClient


@pytest.fixture
def mock_config():
    """Mock configuration."""
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
    return TargetProcessClient(base_url="https://test.tpondemand.com/api/v1", token="test-token")


class TestTargetProcessClient:
    """Tests for TargetProcessClient."""

    @pytest.mark.asyncio
    async def test_get_projects(self, client):
        """Test getting projects."""
        mock_response = [
            {"Id": 1, "Name": "Project 1"},
            {"Id": 2, "Name": "Project 2"},
        ]

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_projects()

            assert len(result) == 2
            assert result[0]["Name"] == "Project 1"
            mock_get.assert_called_once_with("Projects", include="Name", take=100)

    @pytest.mark.asyncio
    async def test_search(self, client):
        """Test search functionality."""
        mock_response = [
            {"Id": 1, "Name": "Login User Story", "EntityState": {"Name": "Open"}},
        ]

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.search("login")

            assert len(result) == 1
            assert "login" in result[0]["Name"].lower()
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_stories_with_filters(self, client):
        """Test getting user stories with filters."""
        mock_response = [
            {"Id": 1, "Name": "US 1", "Project": {"Id": 5}},
        ]

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_user_stories(
                project_id=5, state="In Progress", assignee_id=10
            )

            assert len(result) == 1
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_bugs_with_filters(self, client):
        """Test getting bugs with filters."""
        mock_response = [
            {"Id": 1, "Name": "Bug 1", "Severity": {"Name": "Critical"}},
        ]

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_bugs(project_id=5, severity="Critical")

            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_build_where_single_condition(self, client):
        """Test WHERE clause building with single condition."""
        where = client._build_where("(Project.Id eq 5)")
        assert where == "(Project.Id eq 5)"

    @pytest.mark.asyncio
    async def test_build_where_multiple_conditions(self, client):
        """Test WHERE clause building with multiple conditions."""
        where = client._build_where("(Project.Id eq 5)", "(State eq 'Open')")
        assert "and" in where
        assert "Project.Id eq 5" in where
        assert "State eq 'Open'" in where

    @pytest.mark.asyncio
    async def test_build_where_empty(self, client):
        """Test WHERE clause with no conditions."""
        where = client._build_where()
        assert where is None


class TestMCPServer:
    """Tests for MCP server tools using FastMCP Client."""

    @pytest.mark.asyncio
    async def test_mcp_server_starts(self):
        """Test that MCP server can be created."""
        assert mcp is not None
        assert mcp.name == "TargetProcess"


class TestVPNCheck:
    """Tests for VPN check functionality."""

    def test_check_vpn_not_required(self):
        """Test VPN check when not required."""
        mock_cfg = MagicMock()
        mock_cfg.vpn_required = False

        with patch("targetprocess_mcp.config.config", mock_cfg):
            from targetprocess_mcp.config import check_vpn

            assert check_vpn() is True

    def test_check_vpn_no_hosts(self):
        """Test VPN check with no hosts configured."""
        mock_cfg = MagicMock()
        mock_cfg.vpn_required = True
        mock_cfg.vpn_check_hosts = []

        with patch("targetprocess_mcp.config.config", mock_cfg):
            from targetprocess_mcp.config import check_vpn

            assert check_vpn() is True


class TestConfig:
    """Tests for configuration."""

    def test_load_config_missing(self):
        """Test config loading when file doesn't exist."""
        with patch("targetprocess_mcp.config.CONFIG_DIR") as mock_dir:
            mock_dir.exists.return_value = False
            from targetprocess_mcp.config import load_config

            result = load_config()
            assert result == {}
