import json
import uuid

import pytest

from tests.conftest import _apply_default_db_env


@pytest.fixture
def skills_client(postgres_db):
    _apply_default_db_env()
    from app import create_app

    return create_app(testing=True).test_client()


def _register_sportsman(client, email: str):
    r = client.post(
        "/api/v1/register",
        data=json.dumps(
            {
                "first_name": "Спорт",
                "last_name": "Смен",
                "email": email,
                "password": "secret12",
                "password2": "secret12",
                "role": "sportsman",
            }
        ),
        content_type="application/json",
    )
    assert r.status_code == 201


def _token(client, email: str, password: str) -> str:
    r = client.post(
        "/api/v1/login",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json",
    )
    assert r.status_code == 200
    return r.get_json()["access_token"]


def test_skills_get_empty(skills_client):
    email = f"sk_{uuid.uuid4().hex[:8]}@test.local"
    _register_sportsman(skills_client, email)
    tok = _token(skills_client, email, "secret12")
    rv = skills_client.get(
        "/api/v1/me/skills",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert rv.status_code == 200
    assert rv.get_json() == {"skills": []}


def test_skills_add_and_save(skills_client):
    email = f"sk2_{uuid.uuid4().hex[:8]}@test.local"
    _register_sportsman(skills_client, email)
    tok = _token(skills_client, email, "secret12")

    r1 = skills_client.post(
        "/api/v1/me/skills",
        headers={"Authorization": f"Bearer {tok}"},
        data=json.dumps({"name": "Скилл 1"}),
        content_type="application/json",
    )
    assert r1.status_code == 201
    assert r1.get_json()["name"] == "Скилл 1"
    assert r1.get_json()["rating"] is None

    r2 = skills_client.put(
        "/api/v1/me/skills",
        headers={"Authorization": f"Bearer {tok}"},
        data=json.dumps(
            {
                "skills": [
                    {"name": "Скилл 1", "rating": 8},
                    {"name": "Скилл 2", "rating": None},
                ]
            }
        ),
        content_type="application/json",
    )
    assert r2.status_code == 200
    skills = r2.get_json()["skills"]
    assert len(skills) == 2
    assert skills[0]["name"] == "Скилл 1" and skills[0]["rating"] == 8
    assert skills[1]["name"] == "Скилл 2" and skills[1]["rating"] is None


def test_skills_rating_invalid(skills_client):
    email = f"sk3_{uuid.uuid4().hex[:8]}@test.local"
    _register_sportsman(skills_client, email)
    tok = _token(skills_client, email, "secret12")
    rv = skills_client.put(
        "/api/v1/me/skills",
        headers={"Authorization": f"Bearer {tok}"},
        data=json.dumps({"skills": [{"name": "X", "rating": 11}]}),
        content_type="application/json",
    )
    assert rv.status_code == 400
    assert rv.get_json()["code"] == "invalid_input"


def test_skills_coach_forbidden(skills_client):
    email = f"coach_{uuid.uuid4().hex[:8]}@test.local"
    r = skills_client.post(
        "/api/v1/register",
        data=json.dumps(
            {
                "first_name": "Трен",
                "last_name": "Ер",
                "email": email,
                "password": "secret12",
                "password2": "secret12",
                "role": "coach",
            }
        ),
        content_type="application/json",
    )
    assert r.status_code == 201
    tok = _token(skills_client, email, "secret12")
    rv = skills_client.get(
        "/api/v1/me/skills",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert rv.status_code == 403
