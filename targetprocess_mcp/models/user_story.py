from dataclasses import dataclass


@dataclass
class UserStory:
    """TargetProcess User Story."""

    id: int
    name: str
    project: dict | None = None
    entity_state: dict | None = None
    assignee: dict | None = None
    feature: dict | None = None
    effort: float | None = None
