from dataclasses import dataclass


@dataclass
class User:
    """TargetProcess User."""

    id: int
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    login: str = ""
    is_active: bool = True

    @property
    def full_name(self) -> str:
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.login
