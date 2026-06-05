import json
import uuid

import pytest

from tests.conftest import _apply_default_db_env


@pytest.fixture
def api_client(postgres_db):
    _apply_default_db_env()
    from app import create_app

    return create_app(testing=True).test_client()


def test_health(api_client):
    rv = api_client.get("/api/v1/health")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "ok"
    assert data["storage"] == "postgres"
    assert data.get("db") == "connected"


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
    body = rv.get_json()
    user = body["user"]
    assert user["email"] == email
    assert "password_hash" not in user
    assert "access_token" in body and body["access_token"]
    assert body.get("token_type") == "Bearer"


def test_register_requires_json(api_client):
    rv = api_client.post("/api/v1/register", data="not json")
    assert rv.status_code == 415
