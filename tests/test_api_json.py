import json
import uuid

import pytest

import user_registration.storage as st
import user_registration.storage_sqlite as sb


@pytest.fixture
def api_client(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SPORTORG_DB_HOST", raising=False)
    monkeypatch.setattr(sb, "DB_FILE", str(tmp_path / "api_users.db"))
    st._sqlite_mod = None
    st._postgres_mod = None

    from app import create_app

    app = create_app(testing=True)
    return app.test_client()


def test_health(api_client):
    rv = api_client.get("/api/v1/health")
    assert rv.status_code == 200
    assert rv.get_json() == {"status": "ok"}


def test_register_json_201(api_client):
    email = f"api_{uuid.uuid4().hex[:8]}@test.local"
    rv = api_client.post(
        "/api/v1/register",
        data=json.dumps(
            {
                "first_name": "Api",
                "last_name": "User",
                "email": email,
                "password": "secret12",
                "password2": "secret12",
                "role": "sportsman",
            }
        ),
        content_type="application/json",
    )
    assert rv.status_code == 201
    data = rv.get_json()
    assert data["email"] == email
    assert data["role"] == "sportsman"
    assert isinstance(data["user_id"], int)


def test_register_duplicate_409(api_client):
    email = f"d_{uuid.uuid4().hex[:8]}@test.local"
    body = {
        "first_name": "A",
        "last_name": "B",
        "email": email,
        "password": "secret12",
        "password2": "secret12",
    }
    assert api_client.post(
        "/api/v1/register",
        data=json.dumps(body),
        content_type="application/json",
    ).status_code == 201
    rv2 = api_client.post(
        "/api/v1/register",
        data=json.dumps(body),
        content_type="application/json",
    )
    assert rv2.status_code == 409
    assert rv2.get_json()["code"] == "email_already_exists"


def test_login_json_200(api_client):
    email = f"login_{uuid.uuid4().hex[:8]}@test.local"
    api_client.post(
        "/api/v1/register",
        data=json.dumps(
            {
                "first_name": "L",
                "last_name": "G",
                "email": email,
                "password": "mypass1",
                "password2": "mypass1",
            }
        ),
        content_type="application/json",
    )
    rv = api_client.post(
        "/api/v1/login",
        data=json.dumps({"email": email, "password": "mypass1"}),
        content_type="application/json",
    )
    assert rv.status_code == 200
    user = rv.get_json()["user"]
    assert user["email"] == email
    assert "password_hash" not in user


def test_register_requires_json(api_client):
    rv = api_client.post("/api/v1/register", data="not json")
    assert rv.status_code == 415
