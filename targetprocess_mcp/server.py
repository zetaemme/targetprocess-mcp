"""FastMCP server for TargetProcess integration."""

from fastmcp import FastMCP

from .client import get_client

mcp = FastMCP("TargetProcess")


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
