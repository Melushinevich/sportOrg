import importlib
import os
from typing import Any

__all__ = (
    "add_athlete_skill",
    "create_new_user",
    "get_all_users",
    "get_db_connection",
    "get_user_by_email",
    "get_user_by_id",
    "init_db",
    "list_athlete_skills",
    "replace_athlete_skills",
)


def _use_postgres() -> bool:
    return bool(os.environ.get("DATABASE_URL") or os.environ.get("SPORTORG_DB_HOST"))


_sqlite_mod: Any = None
_postgres_mod: Any = None


def _backend():
    """Выбор бэкенда на каждый вызов (удобно после выставления SPORTORG_* / DATABASE_URL)."""
    global _sqlite_mod, _postgres_mod
    if _use_postgres():
        if _postgres_mod is None:
            _postgres_mod = importlib.import_module(".storage_postgres", __package__)
        return _postgres_mod
    if _sqlite_mod is None:
        _sqlite_mod = importlib.import_module(".storage_sqlite", __package__)
    return _sqlite_mod


def get_db_connection():
    return _backend().get_db_connection()


def init_db():
    return _backend().init_db()


def get_user_by_email(email: str):
    return _backend().get_user_by_email(email)


def create_new_user(user_data: dict) -> int:
    return _backend().create_new_user(user_data)


def get_all_users():
    return _backend().get_all_users()


def get_user_by_id(user_id: int):
    return _backend().get_user_by_id(user_id)


def list_athlete_skills(user_id: int):
    return _backend().list_athlete_skills(user_id)


def add_athlete_skill(user_id: int, name: str = "") -> int:
    return _backend().add_athlete_skill(user_id, name)


def replace_athlete_skills(user_id: int, skills: list[dict[str, Any]]) -> None:
    return _backend().replace_athlete_skills(user_id, skills)
