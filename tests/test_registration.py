import uuid

import pytest

from user_registration import registration


@pytest.mark.usefixtures("postgres_db")
def test_register_success():
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


@pytest.mark.usefixtures("postgres_db")
def test_register_duplicate_email():
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


@pytest.mark.usefixtures("postgres_db")
def test_login_success():
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


@pytest.mark.usefixtures("postgres_db")
def test_login_wrong_password():
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
