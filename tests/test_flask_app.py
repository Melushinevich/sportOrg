import uuid

import pytest

import user_registration.storage as st
import user_registration.storage_sqlite as sb


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SPORTORG_DB_HOST", raising=False)
    monkeypatch.setattr(sb, "DB_FILE", str(tmp_path / "flask_users.db"))
    st._sqlite_mod = None
    st._postgres_mod = None

    from app import create_app

    return create_app(testing=True).test_client()


def test_register_page_renders(client):
    rv = client.get("/")
    assert rv.status_code == 200
    text = rv.get_data(as_text=True)
    assert "Регистрация" in text
    assert 'name="first_name"' in text


def test_register_post_success_flash(client):
    email = f"flask_{uuid.uuid4().hex[:8]}@test.local"
    rv = client.post(
        "/register",
        data={
            "first_name": "Тест",
            "last_name": "Клиент",
            "email": email,
            "password": "secret12",
            "password2": "secret12",
            "role": "coach",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert "Регистрация прошла успешно" in body
    assert "coach" in body
