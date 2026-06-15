"""Общие фикстуры: Flask-клиент и моки БД (без реального Postgres)."""

from __future__ import annotations

import importlib
import os

# До импорта Qt: headless и единый биндинг (приложение на PyQt5, не PySide6).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYTEST_QT_API", "pyqt5")

import pytest

from sportorg.auth.jwt import issue_access_token

INIT_DB_MODULES = (
    "sportorg.api.public",
    "sportorg.api.teams",
    "sportorg.api.athlete_skills",
    "sportorg.api.profile",
)


@pytest.fixture
def noop_init_db(monkeypatch):
    """Тесты API работают с моками storage, без реального Postgres."""
    for name in INIT_DB_MODULES:
        mod = importlib.import_module(name)
        monkeypatch.setattr(mod, "init_db", lambda: None)


@pytest.fixture
def app_client(noop_init_db):
    from app import create_app

    return create_app(testing=True).test_client()


@pytest.fixture
def users_db(monkeypatch):
    """Пользователи для JWT-декораторов."""
    users = {
        1: {"id": 1, "role": "coach", "email": "coach@test.local"},
        2: {"id": 2, "role": "sportsman", "email": "athlete@test.local"},
    }
    monkeypatch.setattr(
        "user_registration.storage.get_user_by_id",
        lambda uid: users.get(int(uid)),
    )
    return users


def auth_header(user_id: int, role: str) -> dict[str, str]:
    token = issue_access_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}


class _FakeCursor:
    def execute(self, *_args, **_kwargs):
        return None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _FakeConn:
    def cursor(self):
        return _FakeCursor()

    def close(self):
        return None


@pytest.fixture
def mock_db_connected(monkeypatch):
    monkeypatch.setattr("sportorg.api.public.get_db_connection", lambda: _FakeConn())


@pytest.fixture
def coach_session():
    """Сессия тренера для service-тестов frontend."""
    from frontend.session import session

    session.user_id = 1
    session.email = "coach@test.local"
    session.role_api = "coach"
    session.role_ui = "ТРЕНЕР"
    session.access_token = "test-coach-token"
    yield session
    session.clear()


@pytest.fixture
def athlete_session():
    """Сессия спортсмена для service-тестов frontend."""
    from frontend.session import session

    session.user_id = 2
    session.email = "athlete@test.local"
    session.role_api = "sportsman"
    session.role_ui = "СПОРТСМЕН"
    session.access_token = "athlete-token"
    yield session
    session.clear()


@pytest.fixture
def no_qt_dialogs(monkeypatch):
    """Не показывать модальные диалоги в smoke-тестах PyQt."""
    monkeypatch.setattr("frontend.ui_messages.show_info", lambda *a, **k: None)
    monkeypatch.setattr("frontend.ui_messages.show_error", lambda *a, **k: None)
    monkeypatch.setattr("frontend.ui_messages.show_warning", lambda *a, **k: None)
    monkeypatch.setattr("frontend.ui_messages.ask_yes_no", lambda *a, **k: True)
    monkeypatch.setattr(
        "frontend.ui_messages.ask_skills_before_apply",
        lambda *a, **k: "continue",
    )
