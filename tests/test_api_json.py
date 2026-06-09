import json
import uuid

import pytest

from user_registration import registration


def test_health_connected(app_client, mock_db_connected):
    rv = app_client.get("/api/v1/health")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "ok"
    assert data["db"] == "connected"


def test_health_degraded(app_client, monkeypatch):
    def fail_conn():
        raise OSError("no db")

    monkeypatch.setattr("sportorg.api.public.get_db_connection", fail_conn)
    rv = app_client.get("/api/v1/health")
    data = rv.get_json()
    assert data["status"] == "degraded"
    assert data["db"] == "error"


def test_index_route(app_client):
    rv = app_client.get("/")
    assert rv.status_code == 200
    assert rv.get_json()["service"] == "SportOrg API"


def test_register_json_201(app_client, monkeypatch):
    email = f"api_{uuid.uuid4().hex[:8]}@test.local"

    def fake_register(_req):
        return {"success": True, "user_id": 10, "email": email, "role": "sportsman"}

    monkeypatch.setattr("sportorg.api.public.register_user", fake_register)
    rv = app_client.post(
        "/api/v1/register",
        data=json.dumps(
            {
                "first_name": "Api",
                "last_name": "User",
                "email": email,
                "password": "secret12",
                "password2": "secret12",
            }
        ),
        content_type="application/json",
    )
    assert rv.status_code == 201
    assert rv.get_json()["user_id"] == 10


def test_register_duplicate_409(app_client, monkeypatch):
    def dup(_req):
        return {"success": False, "error": "dup", "code": "email_already_exists"}

    monkeypatch.setattr("sportorg.api.public.register_user", dup)
    rv = app_client.post(
        "/api/v1/register",
        data=json.dumps(
            {
                "first_name": "A",
                "last_name": "B",
                "email": "d@test.local",
                "password": "secret12",
                "password2": "secret12",
            }
        ),
        content_type="application/json",
    )
    assert rv.status_code == 409


def test_login_json_200(app_client, monkeypatch):
    def fake_login(_email, _password):
        return True, {"id": 5, "email": "u@t.com", "role": "sportsman"}

    monkeypatch.setattr("sportorg.api.public.login_user", fake_login)
    rv = app_client.post(
        "/api/v1/login",
        data=json.dumps({"email": "u@t.com", "password": "secret12"}),
        content_type="application/json",
    )
    assert rv.status_code == 200
    body = rv.get_json()
    assert body.get("access_token")
    assert body.get("token_type") == "Bearer"


def test_login_fail_401(app_client, monkeypatch):
    monkeypatch.setattr("sportorg.api.public.login_user", lambda *_: (False, "bad"))
    rv = app_client.post(
        "/api/v1/login",
        data=json.dumps({"email": "u@t.com", "password": "x"}),
        content_type="application/json",
    )
    assert rv.status_code == 401


def test_register_requires_json(app_client):
    rv = app_client.post("/api/v1/register", data="not json")
    assert rv.status_code == 415


def test_register_invalid_json_body(app_client):
    rv = app_client.post(
        "/api/v1/register",
        data=json.dumps([]),
        content_type="application/json",
    )
    assert rv.status_code == 400
