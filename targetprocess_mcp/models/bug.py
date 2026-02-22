from dataclasses import dataclass


@dataclass
class Bug:
    """TargetProcess Bug."""

    id: int
    name: str
    project: dict | None = None
    entity_state: dict | None = None
    assignee: dict | None = None
    priority: dict | None = None
    severity: dict | None = None
