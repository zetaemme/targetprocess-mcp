"""Tests for TargetProcessClient."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from targetprocess_mcp.client import TargetProcessClient, get_client


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


class TestBuildWhere:
    """Tests for _build_where helper."""

    def test_single_condition(self, client):
        """Test WHERE clause building with single condition."""
        where = client._build_where("(Project.Id eq 5)")
        assert where == "(Project.Id eq 5)"

    def test_multiple_conditions(self, client):
        """Test WHERE clause building with multiple conditions."""
        where = client._build_where("(Project.Id eq 5)", "(State eq 'Open')")
        assert "and" in where
        assert "Project.Id eq 5" in where
        assert "State eq 'Open'" in where

    def test_empty_conditions(self, client):
        """Test WHERE clause with no conditions."""
        where = client._build_where()
        assert where is None


class TestConditionsFromFilters:
    """Tests for _conditions_from_filters helper."""

    def test_single_filter(self):
        """Test single filter condition."""
        client = TargetProcessClient("https://test.com", "token")
        conditions = client._conditions_from_filters(project_id=5)
        assert len(conditions) == 1
        assert "Project.Id eq 5" in conditions[0]

    def test_multiple_filters(self):
        """Test multiple filter conditions."""
        client = TargetProcessClient("https://test.com", "token")
        conditions = client._conditions_from_filters(
            project_id=5, state="Open", severity="Critical"
        )
        assert len(conditions) == 3

    def test_none_values_skipped(self):
        """Test that None values are skipped."""
        client = TargetProcessClient("https://test.com", "token")
        conditions = client._conditions_from_filters(project_id=5, state=None)
        assert len(conditions) == 1

    def test_unknown_filters_skipped(self):
        """Test that unknown filters are skipped."""
        client = TargetProcessClient("https://test.com", "token")
        conditions = client._conditions_from_filters(unknown_field=123)
        assert len(conditions) == 0


class TestBuildParams:
    """Tests for _build_params helper."""

    def test_excludes_none_values(self):
        """Test that None values are excluded."""
        client = TargetProcessClient("https://test.com", "token")
        params = client._build_params(name="test", value=None)
        assert "name" in params
        assert "value" not in params

    def test_keeps_falsy_values(self):
        """Test that falsy values (0, False) are kept."""
        client = TargetProcessClient("https://test.com", "token")
        params = client._build_params(count=0, active=False)
        assert params["count"] == 0
        assert params["active"] is False


class TestGetResponse:
    """Tests for get method response handling."""

    @pytest.mark.asyncio
    async def test_response_as_list(self):
        """Test response when API returns a list."""
        client = TargetProcessClient("https://test.com", "token")
        with patch("targetprocess_mcp.client.get_http_client") as mock_http:
            mock_response = MagicMock()
            mock_response.json.return_value = [{"id": 1}, {"id": 2}]
            mock_response.raise_for_status = MagicMock()
            mock_http.return_value.request = AsyncMock(return_value=mock_response)

            result = await client.get("Projects")
            assert result == [{"id": 1}, {"id": 2}]

    @pytest.mark.asyncio
    async def test_response_as_dict_with_items(self):
        """Test response when API returns dict with Items."""
        client = TargetProcessClient("https://test.com", "token")
        with patch("targetprocess_mcp.client.get_http_client") as mock_http:
            mock_response = MagicMock()
            mock_response.json.return_value = {"Items": [{"id": 1}, {"id": 2}]}
            mock_response.raise_for_status = MagicMock()
            mock_http.return_value.request = AsyncMock(return_value=mock_response)

            result = await client.get("Projects")
            assert result == [{"id": 1}, {"id": 2}]

    @pytest.mark.asyncio
    async def test_response_as_single_dict(self):
        """Test response when API returns single dict."""
        client = TargetProcessClient("https://test.com", "token")
        with patch("targetprocess_mcp.client.get_http_client") as mock_http:
            mock_response = MagicMock()
            mock_response.json.return_value = {"id": 1, "name": "Test"}
            mock_response.raise_for_status = MagicMock()
            mock_http.return_value.request = AsyncMock(return_value=mock_response)

            result = await client.get("Projects")
            assert result == [{"id": 1, "name": "Test"}]


class TestGetClient:
    """Tests for get_client factory function."""

    @pytest.mark.asyncio
    async def test_get_client_not_configured(self):
        """Test get_client raises when not configured."""
        mock_cfg = MagicMock()
        mock_cfg.targetprocess_url = ""
        mock_cfg.targetprocess_token = ""

        with patch("targetprocess_mcp.config.config", mock_cfg):
            with pytest.raises(RuntimeError, match="not configured"):
                await get_client()

    @pytest.mark.asyncio
    async def test_get_client_configured(self):
        """Test get_client returns client when configured."""
        mock_cfg = MagicMock()
        mock_cfg.targetprocess_url = "https://test.com"
        mock_cfg.targetprocess_token = "token"
        mock_cfg.api_base = "https://test.com/api/v1"

        with patch("targetprocess_mcp.config.config", mock_cfg):
            client = await get_client()
            assert client.base_url == "https://test.com/api/v1"
            assert client.token == "token"
