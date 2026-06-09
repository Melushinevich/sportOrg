"""JWT и декораторы авторизации."""

import jwt as pyjwt
import pytest

from sportorg.auth.jwt import (
    decode_access_token,
    issue_access_token,
    jwt_secret,
    require_coach_json,
    require_sportsman_json,
)


def test_issue_and_decode_token():
    token = issue_access_token(42, "sportsman")
    data = decode_access_token(token)
    assert data is not None
    assert data["sub"] == "42"
    assert data["role"] == "sportsman"


def test_decode_invalid_token():
    assert decode_access_token("not.a.token") is None


def test_jwt_secret_from_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    token = issue_access_token(1, "coach")
    assert decode_access_token(token) is not None
    assert jwt_secret() == "test-secret"


def test_require_sportsman_json_401_no_header(app_client):
    rv = app_client.get("/api/v1/me/skills")
    assert rv.status_code == 401
    assert rv.get_json()["code"] == "unauthorized"


def test_require_sportsman_json_403_coach(app_client, users_db):
    from tests.conftest import auth_header

    rv = app_client.get("/api/v1/me/skills", headers=auth_header(1, "coach"))
    assert rv.status_code == 403


def test_require_coach_json_403_sportsman(app_client, users_db):
    from tests.conftest import auth_header

    rv = app_client.get("/api/v1/coach/teams", headers=auth_header(2, "sportsman"))
    assert rv.status_code == 403


def test_require_invalid_token(app_client, users_db):
    rv = app_client.get(
        "/api/v1/coach/teams",
        headers={"Authorization": "Bearer bad.token.here"},
    )
    assert rv.status_code == 401


def test_require_unknown_user(app_client, monkeypatch):
    monkeypatch.setattr("user_registration.storage.get_user_by_id", lambda _uid: None)
    token = issue_access_token(99, "coach")
    rv = app_client.get(
        "/api/v1/coach/teams",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rv.status_code == 401
    assert rv.get_json()["code"] == "not_found"


def test_expired_token(app_client, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", jwt_secret())
    payload = {"sub": "2", "role": "sportsman", "iat": 0, "exp": 1}
    token = pyjwt.encode(payload, jwt_secret(), algorithm="HS256")
    rv = app_client.get(
        "/api/v1/me/skills",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rv.status_code == 401
