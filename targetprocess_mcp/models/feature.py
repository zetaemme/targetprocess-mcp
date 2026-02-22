from dataclasses import dataclass


@dataclass
class Feature:
    """TargetProcess Feature."""

    id: int
    name: str
    project: dict | None = None
    entity_state: dict | None = None
