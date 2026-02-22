from dataclasses import dataclass


@dataclass
class Release:
    """TargetProcess Release/Sprint."""

    id: int
    name: str
    project: dict | None = None
    iteration: dict | None = None
    start_date: str | None = None
    end_date: str | None = None
