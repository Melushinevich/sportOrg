"""Прочие модули: integrations, notifications, app factory."""

import os

import pytest


def test_verification_stub(caplog):
    from sportorg.notifications.verification_stub import log_verification_stub

    with caplog.at_level("INFO"):
        log_verification_stub("user@test.local", 1)
    assert any("user@test.local" in r.message for r in caplog.records)


def test_remote_database_register(monkeypatch):
    monkeypatch.setattr("sportorg.integrations.remote_database.init_db", lambda: None)

    def fake_register(data):
        return {"success": True, "user_id": 7, "email": data["email"], "role": "sportsman"}

    monkeypatch.setattr("sportorg.integrations.remote_database._register_user", fake_register)

    from sportorg.integrations.remote_database import RemoteDatabase

    monkeypatch.setenv("SPORTORG_DB_HOST", "192.168.1.80")
    db = RemoteDatabase()
    ok, msg, uid = db.register_user(
        "a@b.com", "pass", "Last", "First", role="sportsman"
    )
    assert ok is True
    assert uid == 7


def test_remote_database_duplicate(monkeypatch):
    monkeypatch.setattr("sportorg.integrations.remote_database.init_db", lambda: None)
    monkeypatch.setattr(
        "sportorg.integrations.remote_database._register_user",
        lambda _d: {"success": False, "code": "email_already_exists", "error": "dup"},
    )
    from sportorg.integrations.remote_database import RemoteDatabase

    db = RemoteDatabase()
    ok, msg, uid = db.register_user("a@b.com", "p", "L", "F")
    assert ok is False
    assert uid is None


def test_create_app_testing():
    from sportorg.app import create_app

    app = create_app(testing=True)
    assert app.config["TESTING"] is True


def test_ensure_postgres_env_default(monkeypatch):
    from sportorg.app import _ensure_postgres_env

    for key in (
        "DATABASE_URL",
        "SPORTORG_DB_HOST",
        "SPORTORG_DB_PORT",
        "SPORTORG_DB_NAME",
        "SPORTORG_DB_USER",
        "SPORTORG_DB_PASSWORD",
    ):
        monkeypatch.delenv(key, raising=False)
    _ensure_postgres_env()
    assert os.environ.get("SPORTORG_DB_HOST") == "192.168.1.80"
