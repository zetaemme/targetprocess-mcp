"""FastMCP server for TargetProcess integration."""

import subprocess
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.middleware.caching import ResponseCachingMiddleware

from . import config as config_module
from .client import get_client

mcp = FastMCP("TargetProcess")
mcp.add_middleware(ResponseCachingMiddleware())

KEYCHAIN_SERVICE = "targetprocess-mcp"
CONFIG_DIR = Path.home() / ".config" / "targetprocess-mcp"


def store_in_keychain(account: str, password: str) -> bool:
    """Store password in macOS Keychain."""
    try:
        subprocess.run(
            ["security", "delete-generic-password", "-s", KEYCHAIN_SERVICE, "-a", account],
            capture_output=True,
        )
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-s",
                KEYCHAIN_SERVICE,
                "-a",
                account,
                "-w",
                password,
            ],
            capture_output=True,
            check=True,
        )
        return True
    except Exception:
        return False


def save_config(
    url: str, vpn_required: bool = False, vpn_check_hosts: list[str] | None = None
) -> None:
    """Save configuration to TOML file."""
    import sys

    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_data = {"URL": url.rstrip("/")}
    if vpn_required:
        config_data["VPN_REQUIRED"] = True
        if vpn_check_hosts:
            config_data["VPN_CHECK_HOSTS"] = vpn_check_hosts

    config_file = CONFIG_DIR / "config.toml"
    with open(config_file, "wb") as f:
        tomllib.dump(config_data, f)


@mcp.tool()
async def configure(
    url: str,
    token: str,
    vpn_required: bool = False,
    vpn_check_hosts: str | None = None,
) -> str:
    """Configure TargetProcess MCP with your credentials.

    Run this first to set up your TargetProcess URL and API token.

    Args:
        url: TargetProcess URL (e.g., https://yourcompany.tpondemand.com)
        token: API token from TargetProcess Settings > API
        vpn_required: Whether VPN is required to access TargetProcess
        vpn_check_hosts: Comma-separated list of hosts to check VPN connectivity

    Returns:
        Success or error message
    """
    if not url:
        return "Error: URL is required"
    if not token:
        return "Error: Token is required"

    save_config(url, vpn_required, vpn_check_hosts.split(",") if vpn_check_hosts else None)

    if store_in_keychain("api-token", token):
        return "Configuration saved successfully!\n\nTo add to Claude Code, run:\n  /mcp add targetprocess -- python -m targetprocess_mcp.server"
    else:
        return "Configuration saved but failed to store token in keychain"


@mcp.tool()
async def get_status() -> dict:
    """Check if TargetProcess MCP is configured and connected."""
    try:
        if not config_module.config.targetprocess_url:
            return {"configured": False, "message": "Not configured. Run configure tool first."}
        if not config_module.config.targetprocess_token:
            return {"configured": False, "message": "Token not found. Run configure tool first."}

        return {
            "configured": True,
            "url": config_module.config.targetprocess_url,
            "vpn_required": config_module.config.vpn_required,
        }
    except Exception as e:
        return {"configured": False, "message": str(e)}


@mcp.tool()
async def get_projects(take: int = 100) -> list[dict]:
    """Get all projects (id + name) for quick reference.

    Use this to find project IDs before querying specific entities.

    Args:
        take: Maximum number of projects to return (default 100)

    Returns:
        List of projects with id and name
    """
    client = await get_client()
    return await client.get_projects(take=take)


@mcp.tool()
async def search(
    query: str,
    entity_type: str | None = None,
    project_id: int | None = None,
    take: int = 20,
) -> list[dict]:
    """Search entities by name.

    Quick way to find user stories, bugs, or features by partial name match.

    Args:
        query: Search term (matches entity name, case-insensitive)
        entity_type: Filter by type - UserStory, Bug, Feature, or Task
        project_id: Filter by project ID
        take: Maximum results to return (default 20)

    Returns:
        List of matching entities
    """
    client = await get_client()
    return await client.search(query, entity_type, project_id, take)


@mcp.tool()
async def get_user_stories(
    project_id: int | None = None,
    feature_id: int | None = None,
    assignee_id: int | None = None,
    state: str | None = None,
    take: int = 100,
) -> list[dict]:
    """Get user stories from TargetProcess.

    Args:
        project_id: Filter by project ID
        feature_id: Filter by feature ID
        assignee_id: Filter by assignee user ID
        state: Filter by state name (e.g., "Open", "In Progress", "Done", "QA")
        take: Maximum results (default 100)

    Returns:
        List of user stories with project, state, assignee, and feature info
    """
    client = await get_client()
    return await client.get_user_stories(
        project_id=project_id,
        feature_id=feature_id,
        assignee_id=assignee_id,
        state=state,
        take=take,
    )


@mcp.tool()
async def get_bugs(
    project_id: int | None = None,
    assignee_id: int | None = None,
    state: str | None = None,
    severity: str | None = None,
    take: int = 100,
) -> list[dict]:
    """Get bugs from TargetProcess.

    Args:
        project_id: Filter by project ID
        assignee_id: Filter by assignee user ID
        state: Filter by state (e.g., "Open", "In Progress", "Done", "Resolved")
        severity: Filter by severity (e.g., "Critical", "Major", "Minor")
        take: Maximum results (default 100)

    Returns:
        List of bugs with project, state, assignee, priority, and severity info
    """
    client = await get_client()
    return await client.get_bugs(
        project_id=project_id,
        assignee_id=assignee_id,
        state=state,
        severity=severity,
        take=take,
    )


@mcp.tool()
async def get_features(
    project_id: int | None = None,
    state: str | None = None,
    take: int = 100,
) -> list[dict]:
    """Get features from TargetProcess.

    Args:
        project_id: Filter by project ID
        state: Filter by state (e.g., "Proposed", "In Progress", "Completed")
        take: Maximum results (default 100)

    Returns:
        List of features with project and state info
    """
    client = await get_client()
    return await client.get_features(project_id=project_id, state=state, take=take)


@mcp.tool()
async def get_sprints(
    project_id: int | None = None,
    take: int = 50,
) -> list[dict]:
    """Get sprints/releases from TargetProcess.

    Args:
        project_id: Filter by project ID
        take: Maximum results (default 50)

    Returns:
        List of releases/sprints with project and iteration info
    """
    client = await get_client()
    return await client.get_sprints(project_id=project_id, take=take)


def run():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    run()
