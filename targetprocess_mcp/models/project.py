from dataclasses import dataclass


@dataclass
class Project:
    """TargetProcess Project."""

    id: int
    name: str
    description: str | None = None
    process: dict | None = None
