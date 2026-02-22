"""Tests for MCP server."""

import pytest

from targetprocess_mcp.server import mcp


class TestMCPServer:
    """Tests for MCP server."""

    @pytest.mark.asyncio
    async def test_server_exists(self):
        """Test that MCP server exists."""
        assert mcp is not None

    @pytest.mark.asyncio
    async def test_server_name(self):
        """Test MCP server has correct name."""
        assert mcp.name == "TargetProcess"

    @pytest.mark.asyncio
    async def test_has_tools(self):
        """Test MCP server has tools registered."""
        from fastmcp.client import Client

        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [t.name for t in tools]
            assert "configure" in tool_names
            assert "get_status" in tool_names
            assert "get_projects" in tool_names
            assert "search" in tool_names
