"""TargetProcess API client."""

from typing import Any, Literal

import httpx

from .config import check_vpn

_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    """Get or create the shared HTTP client singleton."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=20,
                keepalive_expiry=30.0,
            ),
        )
    return _client


async def close_http_client() -> None:
    """Close the HTTP client (call on shutdown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


class TargetProcessClient:
    """Async client for TargetProcess REST API."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _build_params(self, **kwargs: Any) -> dict[str, Any]:
        """Build query parameters, excluding None values."""
        return {k: v for k, v in kwargs.items() if v is not None}

    def _build_where(self, *conditions: str) -> str | None:
        """Build OData WHERE clause from conditions."""
        return " and ".join(conditions) or None

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make HTTP request to TargetProcess API."""
        if not check_vpn():
            raise RuntimeError("VPN connection required. Please connect to VPN.")

        url = f"{self.base_url}/{endpoint}?token={self.token}"
        params = self._build_params(**kwargs.get("params", {}))

        client = get_http_client()
        response = await client.request(
            method,
            url,
            params=params if params else None,
        )
        response.raise_for_status()
        return response.json()

    async def get(
        self,
        endpoint: str,
        include: str | None = None,
        where: str | None = None,
        take: int = 100,
        skip: int | None = None,
        order_by: str | None = None,
    ) -> list[dict[str, Any]]:
        """Generic GET request with TargetProcess query parameters."""
        params = self._build_params(
            include=include,
            where=where,
            take=take,
            skip=skip,
            orderby=order_by,
        )
        data = await self._request("GET", endpoint, params=params)

        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("Items", [data])
        return [data]

    async def get_projects(self, take: int = 100) -> list[dict[str, Any]]:
        """Get all projects (id + name only for quick reference)."""
        return await self.get("Projects", include="Name", take=take)

    async def search(
        self,
        query: str,
        entity_type: str | None = None,
        project_id: int | None = None,
        take: int = 20,
    ) -> list[dict[str, Any]]:
        """Search entities by name."""
        conditions = [f"(Name.Contains('{query}'))"]
        if project_id:
            conditions.append(f"(Project.Id eq {project_id})")

        endpoint = entity_type if entity_type else "UserStories"
        return await self.get(
            endpoint,
            include="Project,EntityState",
            where=self._build_where(*conditions),
            take=take,
        )

    async def get_user_stories(
        self,
        project_id: int | None = None,
        feature_id: int | None = None,
        assignee_id: int | None = None,
        state: str | None = None,
        take: int = 100,
    ) -> list[dict[str, Any]]:
        """Get user stories."""
        conditions = []
        if project_id:
            conditions.append(f"(Project.Id eq {project_id})")
        if feature_id:
            conditions.append(f"(Feature.Id eq {feature_id})")
        if assignee_id:
            conditions.append(f"(Assignable.Assignee.Id eq {assignee_id})")
        if state:
            conditions.append(f"(EntityState.Name eq '{state}')")

        return await self.get(
            "UserStories",
            include="Project,EntityState,Assignee,Feature",
            where=self._build_where(*conditions),
            take=take,
        )

    async def get_bugs(
        self,
        project_id: int | None = None,
        assignee_id: int | None = None,
        state: str | None = None,
        severity: str | None = None,
        take: int = 100,
    ) -> list[dict[str, Any]]:
        """Get bugs."""
        conditions = []
        if project_id:
            conditions.append(f"(Project.Id eq {project_id})")
        if assignee_id:
            conditions.append(f"(Assignee.Id eq {assignee_id})")
        if state:
            conditions.append(f"(EntityState.Name eq '{state}')")
        if severity:
            conditions.append(f"(Severity.Name eq '{severity}')")

        return await self.get(
            "Bugs",
            include="Project,EntityState,Assignee,Priority,Severity",
            where=self._build_where(*conditions),
            take=take,
        )

    async def get_features(
        self,
        project_id: int | None = None,
        state: str | None = None,
        take: int = 100,
    ) -> list[dict[str, Any]]:
        """Get features."""
        conditions = []
        if project_id:
            conditions.append(f"(Project.Id eq {project_id})")
        if state:
            conditions.append(f"(EntityState.Name eq '{state}')")

        return await self.get(
            "Features",
            include="Project,EntityState",
            where=self._build_where(*conditions),
            take=take,
        )

    async def get_sprints(
        self,
        project_id: int | None = None,
        take: int = 50,
    ) -> list[dict[str, Any]]:
        """Get sprints/releases for a project."""
        where = f"(Project.Id eq {project_id})" if project_id else None
        return await self.get(
            "Releases",
            include="Project,Iteration",
            where=where,
            take=take,
        )


async def get_client() -> TargetProcessClient:
    """Factory function to create a new client instance."""
    from . import config as config_module

    if not config_module.TARGETPROCESS_URL or not config_module.TARGETPROCESS_TOKEN:
        raise RuntimeError(
            "TargetProcess not configured. Run: configure(url='https://yourcompany.tpondemand.com', token='your-api-token')"
        )

    return TargetProcessClient(
        base_url=config_module.API_BASE,
        token=config_module.TARGETPROCESS_TOKEN,
    )
