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
        data=json.dumps({"sport": "Футбол", "team": "Команда 1"}),
        content_type="application/json",
    )
    assert rv_team.status_code == 201
    team_id = rv_team.get_json()["team_id"]

    rv_list = client.get(
        "/api/v1/available-teams",
        headers={"Authorization": f"Bearer {athlete_token}"},
    )
    assert rv_list.status_code == 200
    teams = rv_list.get_json()["teams"]
    assert any(t["team_id"] == team_id and t["sport"] == "Футбол" for t in teams)

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
