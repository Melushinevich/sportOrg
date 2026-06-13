import json

import pytest

from tests.conftest import auth_header


@pytest.fixture
def skills_mocks(monkeypatch):
    state = {"skills": []}

    def list_skills(_uid):
        return list(state["skills"])

    def add_skill(_uid, name=""):
        sid = len(state["skills"]) + 1
        state["skills"].append({"id": sid, "name": name, "rating": None, "sort_order": len(state["skills"])})
        return sid

    def replace(_uid, items):
        state["skills"] = [
            {"id": i + 1, "name": s["name"], "rating": s.get("rating"), "sort_order": i}
            for i, s in enumerate(items)
        ]

    monkeypatch.setattr("sportorg.api.athlete_skills.list_athlete_skills", list_skills)
    monkeypatch.setattr("sportorg.api.athlete_skills.list_skills_catalog", lambda: [])
    monkeypatch.setattr("sportorg.api.athlete_skills.add_athlete_skill", add_skill)
    monkeypatch.setattr("sportorg.api.athlete_skills.replace_athlete_skills", replace)
    return state


def test_skills_get_empty(app_client, users_db, skills_mocks):
    rv = app_client.get("/api/v1/me/skills", headers=auth_header(2, "sportsman"))
    assert rv.status_code == 200
    assert rv.get_json() == {"skills": [], "catalog": []}


def test_skills_add_and_save(app_client, users_db, skills_mocks):
    h = auth_header(2, "sportsman")
    r1 = app_client.post(
        "/api/v1/me/skills",
        headers=h,
        data=json.dumps({"name": "Скилл 1"}),
        content_type="application/json",
    )
    assert r1.status_code == 201

    r2 = app_client.put(
        "/api/v1/me/skills",
        headers=h,
        data=json.dumps({"skills": [{"name": "Скилл 1", "rating": 8}, {"name": "Скилл 2"}]}),
        content_type="application/json",
    )
    assert r2.status_code == 200
    assert len(r2.get_json()["skills"]) == 2


def test_skills_rating_invalid(app_client, users_db, skills_mocks):
    rv = app_client.put(
        "/api/v1/me/skills",
        headers=auth_header(2, "sportsman"),
        data=json.dumps({"skills": [{"name": "X", "rating": 11}]}),
        content_type="application/json",
    )
    assert rv.status_code == 400


def test_skills_not_json(app_client, users_db, skills_mocks):
    rv = app_client.post("/api/v1/me/skills", headers=auth_header(2, "sportsman"), data="x")
    assert rv.status_code == 415


def test_skills_invalid_skills_array(app_client, users_db, skills_mocks):
    rv = app_client.put(
        "/api/v1/me/skills",
        headers=auth_header(2, "sportsman"),
        data=json.dumps({"skills": "bad"}),
        content_type="application/json",
    )
    assert rv.status_code == 400


def test_skills_storage_error(app_client, users_db, monkeypatch):
    monkeypatch.setattr("sportorg.api.athlete_skills.list_athlete_skills", lambda _u: [])
    monkeypatch.setattr(
        "sportorg.api.athlete_skills.replace_athlete_skills",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("fail")),
    )
    rv = app_client.put(
        "/api/v1/me/skills",
        headers=auth_header(2, "sportsman"),
        data=json.dumps({"skills": [{"name": "A", "rating": 5}]}),
        content_type="application/json",
    )
    assert rv.status_code == 503
