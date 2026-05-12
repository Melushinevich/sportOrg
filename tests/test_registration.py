import uuid

import pytest

import user_registration.storage_sqlite as sqlite_backend
from user_registration import registration


@pytest.fixture
def isolated_sqlite(monkeypatch, tmp_path):
    """SQLite в временном файле, без Postgres в окружении."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SPORTORG_DB_HOST", raising=False)
    db_path = tmp_path / "test_users.db"
    monkeypatch.setattr(sqlite_backend, "DB_FILE", str(db_path))
    sqlite_backend.init_db()
    yield sqlite_backend


def test_register_success(isolated_sqlite, monkeypatch):
    monkeypatch.setattr(registration, "get_user_by_email", sqlite_backend.get_user_by_email)
    monkeypatch.setattr(registration, "create_new_user", sqlite_backend.create_new_user)

    email = f"u_{uuid.uuid4().hex[:8]}@test.local"
    out = registration.register_user(
        {
            "first_name": "Иван",
            "last_name": "Тестов",
            "email": email,
            "password": "secret12",
            "password2": "secret12",
            "role": "sportsman",
        }
    )
    assert out["success"] is True
    assert out["email"] == email
    assert out["role"] == "sportsman"
    assert isinstance(out["user_id"], int)


def test_register_duplicate_email(isolated_sqlite, monkeypatch):
    monkeypatch.setattr(registration, "get_user_by_email", sqlite_backend.get_user_by_email)
    monkeypatch.setattr(registration, "create_new_user", sqlite_backend.create_new_user)

    email = f"d_{uuid.uuid4().hex[:8]}@test.local"
    payload = {
        "first_name": "А",
        "last_name": "Б",
        "email": email,
        "password": "secret12",
        "password2": "secret12",
    }
    assert registration.register_user(payload)["success"] is True
    second = registration.register_user(payload)
    assert second["success"] is False
    assert second["code"] == "email_already_exists"


def test_login_success(isolated_sqlite, monkeypatch):
    monkeypatch.setattr(registration, "get_user_by_email", sqlite_backend.get_user_by_email)
    monkeypatch.setattr(registration, "create_new_user", sqlite_backend.create_new_user)

    email = f"l_{uuid.uuid4().hex[:8]}@test.local"
    registration.register_user(
        {
            "first_name": "Логин",
            "last_name": "Тест",
            "email": email,
            "password": "mypass1",
            "password2": "mypass1",
            "role": "coach",
        }
    )
    ok, data = registration.login_user(email, "mypass1")
    assert ok is True
    assert isinstance(data, dict)
    assert "password_hash" not in data
    assert data["email"] == email
    assert data["role"] == "coach"


def test_login_wrong_password(isolated_sqlite, monkeypatch):
    monkeypatch.setattr(registration, "get_user_by_email", sqlite_backend.get_user_by_email)
    monkeypatch.setattr(registration, "create_new_user", sqlite_backend.create_new_user)

    email = f"w_{uuid.uuid4().hex[:8]}@test.local"
    registration.register_user(
        {
            "first_name": "X",
            "last_name": "Y",
            "email": email,
            "password": "rightpass1",
            "password2": "rightpass1",
        }
    )
    ok, msg = registration.login_user(email, "wrongpass1")
    assert ok is False
    assert isinstance(msg, str)
