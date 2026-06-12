"""Юнит-тесты registration.py (моки storage)."""

import uuid

import pytest

from user_registration import registration


@pytest.fixture
def storage_mock(monkeypatch):
    store = {"by_email": {}, "next_id": 1}

    def get_user_by_email(email):
        return store["by_email"].get(email)

    def create_new_user(data):
        uid = store["next_id"]
        store["next_id"] += 1
        row = {**data, "id": uid}
        store["by_email"][data["email"]] = row
        return uid

    monkeypatch.setattr(registration, "get_user_by_email", get_user_by_email)
    monkeypatch.setattr(registration, "create_new_user", create_new_user)
    return store


def test_validate_email_and_password():
    assert registration.validate_email("a@b.c")[0] is True
    assert registration.validate_email("bad")[0] is False
    assert registration.validate_password("123456", "123456")[0] is True
    assert registration.validate_password("123456", "654321")[0] is False
    assert registration.validate_password("12", "12")[0] is False


def test_validate_role_and_required_fields():
    assert registration.validate_role("coach")[0] is True
    assert registration.validate_role("admin")[0] is False
    assert registration.validate_required_fields("", "Last", "e@t.com")[0] is False
    assert registration.validate_required_fields("First", "", "e@t.com")[0] is True


def test_register_without_names(storage_mock):
    email = f"n_{uuid.uuid4().hex[:8]}@test.local"
    out = registration.register_user(
        {
            "email": email,
            "password": "secret12",
            "password2": "secret12",
            "role": "coach",
        }
    )
    assert out["success"] is True
    row = storage_mock["by_email"][email]
    assert row.get("first_name") is None
    assert row.get("last_name") is None


def test_hash_password_deterministic():
    assert registration.hash_password("secret12") == registration.hash_password("secret12")


def test_register_success(storage_mock):
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


def test_register_duplicate_email(storage_mock):
    email = f"d_{uuid.uuid4().hex[:8]}@test.local"
    payload = {
        "first_name": "A",
        "last_name": "B",
        "email": email,
        "password": "secret12",
        "password2": "secret12",
    }
    assert registration.register_user(payload)["success"] is True
    second = registration.register_user(payload)
    assert second["success"] is False
    assert second["code"] == "email_already_exists"


def test_register_storage_error(monkeypatch):
    monkeypatch.setattr(registration, "get_user_by_email", lambda _e: None)

    def boom(_data):
        raise RuntimeError("db down")

    monkeypatch.setattr(registration, "create_new_user", boom)
    out = registration.register_user(
        {
            "first_name": "A",
            "last_name": "B",
            "email": "x@y.z",
            "password": "secret12",
            "password2": "secret12",
        }
    )
    assert out["code"] == "storage_error"


def test_login_success_and_wrong_password(storage_mock):
    email = f"l_{uuid.uuid4().hex[:8]}@test.local"
    registration.register_user(
        {
            "first_name": "L",
            "last_name": "G",
            "email": email,
            "password": "mypass1",
            "password2": "mypass1",
            "role": "coach",
        }
    )
    ok, data = registration.login_user(email, "mypass1")
    assert ok is True
    assert "password_hash" not in data

    ok2, msg = registration.login_user(email, "wrong")
    assert ok2 is False
    assert isinstance(msg, str)


def test_login_empty_credentials():
    ok, msg = registration.login_user("", "")
    assert ok is False


def test_register_invalid_input_paths():
    assert registration.register_user({})["code"] == "invalid_input"
    bad_email = registration.register_user(
        {
            "first_name": "A",
            "last_name": "B",
            "email": "bad",
            "password": "secret12",
            "password2": "secret12",
        }
    )
    assert bad_email["code"] == "invalid_input"
    bad_role = registration.register_user(
        {
            "first_name": "A",
            "last_name": "B",
            "email": "ok@t.com",
            "password": "secret12",
            "password2": "secret12",
            "role": "admin",
        }
    )
    assert bad_role["code"] == "invalid_input"
