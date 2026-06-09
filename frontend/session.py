"""Текущий пользователь после входа (токен для API)."""

from dataclasses import dataclass


@dataclass
class UserSession:
    user_id: int | None = None
    email: str | None = None
    role_api: str | None = None
    role_ui: str | None = None
    access_token: str | None = None

    def clear(self) -> None:
        self.user_id = None
        self.email = None
        self.role_api = None
        self.role_ui = None
        self.access_token = None

    @property
    def is_logged_in(self) -> bool:
        return self.access_token is not None


session = UserSession()
