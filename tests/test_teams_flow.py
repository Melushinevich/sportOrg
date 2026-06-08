import json
import uuid

import pytest

from tests.conftest import _apply_default_db_env


@pytest.fixture
def client(postgres_db):
    _apply_default_db_env()
    from app import create_app

    return create_app(testing=True).test_client()


def _register(client, *, role: str, email: str):
    rv = client.post(
        "/api/v1/register",
        data=json.dumps(
            {
                "first_name": "A",
                "last_name": "B",
                "email": email,
                "password": "secret12",
                "password2": "secret12",
                "role": role,
            }
        ),
        content_type="application/json",
    )
    assert rv.status_code == 201


def _login_token(client, *, email: str) -> str:
    rv = client.post(
        "/api/v1/login",
        data=json.dumps({"email": email, "password": "secret12"}),
        content_type="application/json",
    )
    assert rv.status_code == 200
    body = rv.get_json()
    assert body.get("token_type") == "Bearer"
    return body["access_token"]


def test_coach_creates_team_and_athlete_applies_and_sees_applications(client):
    coach_email = f"coach_{uuid.uuid4().hex[:8]}@test.local"
    athlete_email = f"ath_{uuid.uuid4().hex[:8]}@test.local"

    _register(client, role="coach", email=coach_email)
    _register(client, role="sportsman", email=athlete_email)

    coach_token = _login_token(client, email=coach_email)
    athlete_token = _login_token(client, email=athlete_email)

    rv_team = client.post(
        "/api/v1/coach/teams",
        headers={"Authorization": f"Bearer {coach_token}"},
        data=json.dumps(
            {
                "sport": "Футбол",
                "team": "Команда 1",
                "criteria": ["Скорость", "Командная игра"],
            }
        ),
        content_type="application/json",
    )
    assert rv_team.status_code == 201
    body = rv_team.get_json()
    team_id = body["team_id"]
    assert len(body["criteria"]) == 2

    rv_list = client.get(
        "/api/v1/available-teams",
        headers={"Authorization": f"Bearer {athlete_token}"},
    )
    assert rv_list.status_code == 200
    teams = rv_list.get_json()["teams"]
    row = next(t for t in teams if t["team_id"] == team_id)
    assert row["sport"] == "Футбол"
    assert row["team"] == "Команда 1"
    assert row.get("coach")
    assert len(row["criteria"]) == 2
    assert row["criteria"][0]["text"] == "Скорость"

    rv_card = client.get(
        f"/api/v1/available-teams/{team_id}",
        headers={"Authorization": f"Bearer {athlete_token}"},
    )
    assert rv_card.status_code == 200
    assert len(rv_card.get_json()["criteria"]) == 2

    rv_list_filtered = client.get(
        "/api/v1/available-teams?sport=%D0%A4%D1%83%D1%82%D0%B1%D0%BE%D0%BB",
        headers={"Authorization": f"Bearer {athlete_token}"},
    )
    assert rv_list_filtered.status_code == 200
    teams_f = rv_list_filtered.get_json()["teams"]
    assert any(t["team_id"] == team_id for t in teams_f)

    rv_apply = client.post(
        f"/api/v1/teams/{team_id}/apply",
        headers={"Authorization": f"Bearer {athlete_token}"},
    )
    assert rv_apply.status_code == 201
    assert rv_apply.get_json()["status"] == "pending"

    rv_my = client.get(
        "/api/v1/me/applications",
        headers={"Authorization": f"Bearer {athlete_token}"},
    )
    assert rv_my.status_code == 200
    apps = rv_my.get_json()["applications"]
    assert any(a["team_id"] == team_id and a["status"] == "pending" for a in apps)

    rv_apply2 = client.post(
        f"/api/v1/teams/{team_id}/apply",
        headers={"Authorization": f"Bearer {athlete_token}"},
    )
    assert rv_apply2.status_code == 409
    assert rv_apply2.get_json()["code"] == "already_applied"


def test_coach_teams_list_detail_and_roster(client):
    coach_email = f"coach2_{uuid.uuid4().hex[:8]}@test.local"
    athlete_email = f"ath2_{uuid.uuid4().hex[:8]}@test.local"

    _register(client, role="coach", email=coach_email)
    _register(client, role="sportsman", email=athlete_email)

    coach_token = _login_token(client, email=coach_email)
    athlete_token = _login_token(client, email=athlete_email)

    rv_create = client.post(
        "/api/v1/coach/teams",
        headers={"Authorization": f"Bearer {coach_token}"},
        data=json.dumps({"sport": "Баскетбол", "team": "Команда 2"}),
        content_type="application/json",
    )
    assert rv_create.status_code == 201
    team_id = rv_create.get_json()["team_id"]

    rv_list = client.get(
        "/api/v1/coach/teams",
        headers={"Authorization": f"Bearer {coach_token}"},
    )
    assert rv_list.status_code == 200
    teams = rv_list.get_json()["teams"]
    assert any(t["team_id"] == team_id and t["team"] == "Команда 2" and t["sport"] == "Баскетбол" for t in teams)

    rv_login_ath = client.post(
        "/api/v1/login",
        data=json.dumps({"email": athlete_email, "password": "secret12"}),
        content_type="application/json",
    )
    athlete_user_id = rv_login_ath.get_json()["user"]["id"]

    rv_skills = client.put(
        "/api/v1/me/skills",
        headers={"Authorization": f"Bearer {athlete_token}"},
        data=json.dumps(
            {
                "skills": [
                    {"name": "Скорость", "rating": 8},
                    {"name": "Выносливость", "rating": 10},
                ]
            }
        ),
        content_type="application/json",
    )
    assert rv_skills.status_code == 200

    rv_add = client.post(
        f"/api/v1/coach/teams/{team_id}/members",
        headers={"Authorization": f"Bearer {coach_token}"},
        data=json.dumps({"athlete_user_id": athlete_user_id}),
        content_type="application/json",
    )
    assert rv_add.status_code == 201
    member_id = rv_add.get_json()["member_id"]
    assert rv_add.get_json()["member"]["full_name"] == "B A"
    qualities = rv_add.get_json()["member"]["qualities"]
    assert len(qualities) == 2
    assert qualities[0]["name"] == "Скорость" and qualities[0]["rating"] == 8
    assert qualities[1]["name"] == "Выносливость" and qualities[1]["rating"] == 10
    assert rv_add.get_json()["member"]["score"] == 9.0

    q1, q2 = qualities[0]["quality_id"], qualities[1]["quality_id"]
    rv_save = client.put(
        f"/api/v1/coach/teams/{team_id}/members",
        headers={"Authorization": f"Bearer {coach_token}"},
        data=json.dumps(
            {
                "members": [
                    {
                        "member_id": member_id,
                        "notes": "Стабильно",
                        "qualities": [
                            {"quality_id": q1, "rating": 6},
                            {"quality_id": q2, "rating": 10},
                        ],
                    }
                ]
            }
        ),
        content_type="application/json",
    )
    assert rv_save.status_code == 200
    saved = rv_save.get_json()["members"][0]
    assert saved["score"] == 8.0
    assert saved["qualities"][0]["rating"] == 6
    assert saved["qualities"][1]["rating"] == 10
    assert saved["notes"] == "Стабильно"

    rv_finalize = client.post(
        f"/api/v1/coach/teams/{team_id}/finalize",
        headers={"Authorization": f"Bearer {coach_token}"},
    )
    assert rv_finalize.status_code == 200
    assert rv_finalize.get_json()["is_open"] is False

    rv_avail = client.get(
        "/api/v1/available-teams",
        headers={"Authorization": f"Bearer {athlete_token}"},
    )
    assert not any(t["team_id"] == team_id for t in rv_avail.get_json()["teams"])
