from dataclasses import dataclass


@dataclass
class Task:
    """TargetProcess Task."""

    id: int
    name: str
    entity_state: dict | None = None
    assignee: dict | None = None
