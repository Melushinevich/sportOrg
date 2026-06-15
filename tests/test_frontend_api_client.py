"""Тесты frontend/api_client.py с моком HTTP."""

from __future__ import annotations

import io
import json
from urllib.error import HTTPError, URLError

import pytest

from frontend.api_client import ApiError, ROLE_API_TO_UI, ROLE_UI_TO_API, SportOrgApi


class _FakeResponse:
    def __init__(self, status: int, payload: dict | list) -> None:
        self.status = status
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def _mock_urlopen(monkeypatch, handler):
    monkeypatch.setattr("frontend.api_client.urllib.request.urlopen", handler)


def test_role_maps():
    assert ROLE_UI_TO_API["ТРЕНЕР"] == "coach"
    assert ROLE_API_TO_UI["sportsman"] == "СПОРТСМЕН"


def test_api_error_str():
    err = ApiError("msg", code="x", status=400)
    assert str(err) == "msg"
    assert err.code == "x"


def test_health_and_login(monkeypatch):
    calls: list[tuple[str, str]] = []

    def handler(req, timeout=15):
        calls.append((req.method, req.full_url))
        if req.full_url.endswith("/api/v1/health"):
            return _FakeResponse(200, {"status": "ok"})
        if req.full_url.endswith("/api/v1/login"):
            return _FakeResponse(200, {"access_token": "tok", "user_id": 1})
        raise AssertionError(req.full_url)

    _mock_urlopen(monkeypatch, handler)
    api = SportOrgApi(base_url="http://api.test")
    assert api.health()["status"] == "ok"
    data = api.login(email="a@b.c", password="secret")
    assert data["access_token"] == "tok"
    assert ("POST", "http://api.test/api/v1/login") in calls


def test_register_success(monkeypatch):
    def handler(req, timeout=15):
        body = json.loads(req.data.decode())
        assert body["role"] == "coach"
        return _FakeResponse(201, {"user_id": 5})

    _mock_urlopen(monkeypatch, handler)
    data = SportOrgApi("http://api.test").register(
        email="c@t.com",
        password="123456",
        password2="123456",
        role_ui="ТРЕНЕР",
    )
    assert data["user_id"] == 5


def test_register_invalid_role():
    with pytest.raises(ApiError, match="роль"):
        SportOrgApi("http://api.test").register(
            email="a@b.c",
            password="123456",
            password2="123456",
            role_ui="ADMIN",
        )


def test_http_error_parsed(monkeypatch):
    def handler(req, timeout=15):
        payload = json.dumps({"error": "Нет доступа", "code": "forbidden"}).encode()
        raise HTTPError(
            req.full_url,
            403,
            "Forbidden",
            hdrs=None,
            fp=io.BytesIO(payload),
        )

    _mock_urlopen(monkeypatch, handler)
    with pytest.raises(ApiError) as exc:
        SportOrgApi("http://api.test").get_profile(token="t")
    assert exc.value.code == "forbidden"
    assert exc.value.status == 403


def test_connection_error(monkeypatch):
    def handler(req, timeout=15):
        raise URLError("connection refused")

    _mock_urlopen(monkeypatch, handler)
    with pytest.raises(ApiError) as exc:
        SportOrgApi("http://api.test").list_coach_teams(token="t")
    assert exc.value.code == "connection_error"


@pytest.mark.parametrize(
    "method_name,path_suffix,status,response_key",
    [
        ("get_profile", "/api/v1/me/profile", 200, "profile"),
        ("get_my_skills", "/api/v1/me/skills", 200, "skills"),
        ("list_coach_teams", "/api/v1/coach/teams", 200, "teams"),
        ("list_my_teams", "/api/v1/me/teams", 200, "teams"),
    ],
)
def test_get_endpoints_ok(monkeypatch, method_name, path_suffix, status, response_key):
    payload = {response_key: []}

    def handler(req, timeout=15):
        assert path_suffix in req.full_url
        assert req.get_header("Authorization") == "Bearer tok"
        return _FakeResponse(status, payload)

    _mock_urlopen(monkeypatch, handler)
    api = SportOrgApi("http://api.test")
    result = getattr(api, method_name)(token="tok")
    assert response_key in result or result == payload


def test_list_coach_applications_builds_query(monkeypatch):
    seen_url = {}

    def handler(req, timeout=15):
        seen_url["url"] = req.full_url
        return _FakeResponse(200, {"applications": []})

    _mock_urlopen(monkeypatch, handler)
    SportOrgApi("http://api.test").list_coach_applications(
        token="t",
        team_id=3,
        team_name='Команда "А"',
        status="pending",
    )
    url = seen_url["url"]
    assert "team_id=3" in url
    assert "status=pending" in url
    assert "team=" in url


def test_apply_to_team_requires_201(monkeypatch):
    def handler(req, timeout=15):
        return _FakeResponse(200, {"error": "bad", "code": "x"})

    _mock_urlopen(monkeypatch, handler)
    with pytest.raises(ApiError):
        SportOrgApi("http://api.test").apply_to_team(token="t", team_id=1)
