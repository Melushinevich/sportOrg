import json

import pytest

from tests.conftest import auth_header

COACH_H = None  # set in fixture


@pytest.fixture
def teams_mocks(monkeypatch):
    state = {
        "teams": [],
        "next_team_id": 1,
        "applications": [],
        "members": {},
    }

    def list_coach(_coach_id):
        return state["teams"]

    def create_team(_coach_id, sport, team, criteria=None):
        tid = state["next_team_id"]
        state["next_team_id"] += 1
        entry = {
            "team_id": tid,
            "team": team,
            "sport": sport,
            "criteria": [{"criterion_id": i + 1, "text": c, "sort_order": i} for i, c in enumerate(criteria or [])],
            "members": [],
        }
        state["teams"].append({"team_id": tid, "team": team, "sport": sport})
        state["members"][tid] = entry
        return tid

    def get_coach_detail(_coach_id, team_id):
        if team_id not in state["members"]:
            raise ValueError("Команда не найдена")
        return state["members"][team_id]

    def list_available(sport_name=None):
        rows = [
            {
                "team_id": t["team_id"],
                "team": t["team"],
                "sport": t["sport"],
                "coach_id": 1,
                "coach": "Coach Test",
                "criteria": state["members"][t["team_id"]]["criteria"],
            }
            for t in state["teams"]
        ]
        if sport_name:
            rows = [r for r in rows if r["sport"] == sport_name]
        return rows

    def get_available_detail(team_id):
        if team_id not in state["members"]:
            return None
        m = state["members"][team_id]
        return {
            "team_id": team_id,
            "team": m["team"],
            "sport": m["sport"],
            "coach_id": 1,
            "coach": "Coach Test",
            "criteria": m["criteria"],
        }

    def apply_to_team(team_id, athlete_user_id):
        if team_id not in state["members"]:
            raise ValueError("Команда не найдена")
        for a in state["applications"]:
            if a["team_id"] == team_id and a["athlete_user_id"] == athlete_user_id:
                raise ValueError("Заявка уже подана")
        aid = len(state["applications"]) + 1
        state["applications"].append(
            {"application_id": aid, "team_id": team_id, "athlete_user_id": athlete_user_id, "status": "pending"}
        )
        return aid

    def list_apps(athlete_user_id):
        return [a for a in state["applications"] if a["athlete_user_id"] == athlete_user_id]

    def list_athlete(_athlete_user_id):
        teams = []
        for tid, detail in state["members"].items():
            for m in detail["members"]:
                teams.append(
                    {
                        "member_id": m["member_id"],
                        "team_id": tid,
                        "team": detail["team"],
                        "sport": detail["sport"],
                        "coach_id": 1,
                        "coach": "Coach Test",
                    }
                )
        return teams

    def search_sportsmen(_q):
        return [{"athlete_user_id": 2, "full_name": "Athlete Test", "email": "a@t.com"}]

    def add_member(_coach_id, team_id, athlete_user_id):
        detail = get_coach_detail(_coach_id, team_id)
        mid = len(detail["members"]) + 1
        member = {
            "member_id": mid,
            "athlete_user_id": athlete_user_id,
            "full_name": "Athlete",
            "score": None,
            "qualities": [],
            "notes": "",
        }
        detail["members"].append(member)
        return mid

    def save_members(_coach_id, team_id, members):
        detail = get_coach_detail(_coach_id, team_id)
        return detail["members"]

    def remove_member(_coach_id, team_id, member_id):
        detail = get_coach_detail(_coach_id, team_id)
        before = len(detail["members"])
        detail["members"] = [m for m in detail["members"] if m["member_id"] != member_id]
        if len(detail["members"]) == before:
            raise ValueError("Участник не найден")

    def list_coach_applications(_coach_id, team_id=None, team_name=None, status="pending"):
        rows = []
        for app in state["applications"]:
            if status and app.get("status") != status:
                continue
            detail = state["members"].get(app["team_id"])
            if detail is None:
                continue
            if team_id is not None and app["team_id"] != team_id:
                continue
            if team_name and detail["team"] != team_name:
                continue
            rows.append(
                {
                    "application_id": app["application_id"],
                    "status": app["status"],
                    "team_id": app["team_id"],
                    "team": detail["team"],
                    "sport": detail["sport"],
                    "athlete_user_id": app["athlete_user_id"],
                    "full_name": "Athlete Test",
                    "email": "a@t.com",
                    "phone": "",
                    "skills": [{"name": "Скорость", "rating": 8}],
                }
            )
        return rows

    def accept_application(_coach_id, application_id):
        app = next((a for a in state["applications"] if a["application_id"] == application_id), None)
        if app is None:
            raise ValueError("Заявка не найдена")
        if app["status"] != "pending":
            raise ValueError("Заявка уже обработана")
        member_id = add_member(_coach_id, app["team_id"], app["athlete_user_id"])
        app["status"] = "accepted"
        detail = state["members"][app["team_id"]]
        return {
            "member_id": member_id,
            "application_id": application_id,
            "team_id": app["team_id"],
            "team": detail["team"],
            "sport": detail["sport"],
            "full_name": "Athlete Test",
            "email": "a@t.com",
            "phone": "",
            "skills": [{"name": "Скорость", "rating": 8}],
        }

    monkeypatch.setattr("sportorg.api.teams.list_coach_teams", list_coach)
    monkeypatch.setattr("sportorg.api.teams.create_team", create_team)
    monkeypatch.setattr("sportorg.api.teams.get_coach_team_detail", get_coach_detail)
    monkeypatch.setattr("sportorg.api.teams.list_available_teams", list_available)
    monkeypatch.setattr("sportorg.api.teams.get_available_team_detail", get_available_detail)
    monkeypatch.setattr("sportorg.api.teams.apply_to_team", apply_to_team)
    monkeypatch.setattr("sportorg.api.teams.list_my_team_applications", list_apps)
    monkeypatch.setattr("sportorg.api.teams.list_athlete_teams", list_athlete)
    monkeypatch.setattr("sportorg.api.teams.list_coach_applications", list_coach_applications)
    monkeypatch.setattr("sportorg.api.teams.accept_team_application", accept_application)
    monkeypatch.setattr("sportorg.api.teams.search_sportsmen", search_sportsmen)
    monkeypatch.setattr("sportorg.api.teams.add_team_member", add_member)
    monkeypatch.setattr("sportorg.api.teams.save_team_members", save_members)
    monkeypatch.setattr("sportorg.api.teams.remove_team_member", remove_member)
    return state


def test_coach_catalog_endpoints(app_client, users_db, monkeypatch):
    ch = auth_header(1, "coach")
    monkeypatch.setattr(
        "sportorg.api.teams.list_sports",
        lambda: [{"sport_id": 1, "name": "Футбол"}, {"sport_id": 2, "name": "Бокс"}],
    )
    monkeypatch.setattr(
        "sportorg.api.teams.list_skills_catalog",
        lambda: [{"skill_id": 1, "name": "Скорость", "category": "physical"}],
    )

    rv = app_client.get("/api/v1/coach/sports", headers=ch)
    assert rv.status_code == 200
    assert len(rv.get_json()["sports"]) == 2

    rv2 = app_client.get("/api/v1/coach/skills-catalog", headers=ch)
    assert rv2.status_code == 200
    assert rv2.get_json()["skills"][0]["name"] == "Скорость"


def test_coach_list_and_create(app_client, users_db, teams_mocks):
    ch = auth_header(1, "coach")
    rv = app_client.get("/api/v1/coach/teams", headers=ch)
    assert rv.status_code == 200
    assert rv.get_json()["teams"] == []

    rv2 = app_client.post(
        "/api/v1/coach/teams",
        headers=ch,
        data=json.dumps({"sport": "Футбол", "team": "К1", "criteria": ["Скорость"]}),
        content_type="application/json",
    )
    assert rv2.status_code == 201
    assert rv2.get_json()["criteria"][0]["text"] == "Скорость"


def test_coach_create_validation(app_client, users_db, teams_mocks):
    ch = auth_header(1, "coach")
    rv = app_client.post("/api/v1/coach/teams", headers=ch, data="not-json")
    assert rv.status_code == 415

    rv2 = app_client.post(
        "/api/v1/coach/teams",
        headers=ch,
        data=json.dumps({"sport": "", "team": "X"}),
        content_type="application/json",
    )
    assert rv2.status_code == 400


def test_coach_team_detail_and_members(app_client, users_db, teams_mocks):
    ch = auth_header(1, "coach")
    tid = app_client.post(
        "/api/v1/coach/teams",
        headers=ch,
        data=json.dumps({"sport": "Баск", "team": "К2", "criteria": []}),
        content_type="application/json",
    ).get_json()["team_id"]

    rv = app_client.get(f"/api/v1/coach/teams/{tid}", headers=ch)
    assert rv.status_code == 200

    rv2 = app_client.post(
        f"/api/v1/coach/teams/{tid}/members",
        headers=ch,
        data=json.dumps({"athlete_user_id": 2}),
        content_type="application/json",
    )
    assert rv2.status_code == 201

    rv3 = app_client.put(
        f"/api/v1/coach/teams/{tid}/members",
        headers=ch,
        data=json.dumps({"members": [{"member_id": 1, "notes": "ok", "qualities": []}]}),
        content_type="application/json",
    )
    assert rv3.status_code == 200

    rv4 = app_client.delete(f"/api/v1/coach/teams/{tid}/members/1", headers=ch)
    assert rv4.status_code == 200

    rv5 = app_client.get("/api/v1/coach/sportsmen?search=test", headers=ch)
    assert rv5.status_code == 200
    assert rv5.get_json()["sportsmen"]


def test_sportsman_available_and_apply(app_client, users_db, teams_mocks):
    ch = auth_header(1, "coach")
    sh = auth_header(2, "sportsman")
    tid = app_client.post(
        "/api/v1/coach/teams",
        headers=ch,
        data=json.dumps({"sport": "Футбол", "team": "К4", "criteria": ["Вынос"]}),
        content_type="application/json",
    ).get_json()["team_id"]

    rv = app_client.get("/api/v1/available-teams", headers=sh)
    assert rv.status_code == 200
    assert any(t["team_id"] == tid for t in rv.get_json()["teams"])

    rv2 = app_client.get(f"/api/v1/available-teams/{tid}", headers=sh)
    assert rv2.status_code == 200

    rv3 = app_client.post(f"/api/v1/teams/{tid}/apply", headers=sh)
    assert rv3.status_code == 201

    rv4 = app_client.get("/api/v1/me/applications", headers=sh)
    assert rv4.status_code == 200

    rv6 = app_client.get("/api/v1/me/teams", headers=sh)
    assert rv6.status_code == 200
    assert rv6.get_json()["teams"] == []

    rv5 = app_client.post(f"/api/v1/teams/{tid}/apply", headers=sh)
    assert rv5.status_code == 409


def test_coach_applications_list_and_accept(app_client, users_db, teams_mocks):
    ch = auth_header(1, "coach")
    sh = auth_header(2, "sportsman")
    tid = app_client.post(
        "/api/v1/coach/teams",
        headers=ch,
        data=json.dumps({"sport": "Футбол", "team": "К5", "criteria": ["Скорость"]}),
        content_type="application/json",
    ).get_json()["team_id"]

    app_client.post(f"/api/v1/teams/{tid}/apply", headers=sh)

    rv = app_client.get("/api/v1/coach/applications", headers=ch)
    assert rv.status_code == 200
    apps = rv.get_json()["applications"]
    assert len(apps) == 1
    app_id = apps[0]["application_id"]

    rv2 = app_client.post(f"/api/v1/coach/applications/{app_id}/accept", headers=ch)
    assert rv2.status_code == 200

    rv3 = app_client.get("/api/v1/coach/applications", headers=ch)
    assert rv3.get_json()["applications"] == []

    rv4 = app_client.get("/api/v1/me/teams", headers=sh)
    assert len(rv4.get_json()["teams"]) == 1


def test_available_team_not_found(app_client, users_db, teams_mocks):
    rv = app_client.get("/api/v1/available-teams/999", headers=auth_header(2, "sportsman"))
    assert rv.status_code == 404


def test_coach_create_storage_error(app_client, users_db, teams_mocks, monkeypatch):
    def boom(*_a, **_k):
        raise RuntimeError("db")

    monkeypatch.setattr("sportorg.api.teams.create_team", boom)
    rv = app_client.post(
        "/api/v1/coach/teams",
        headers=auth_header(1, "coach"),
        data=json.dumps({"sport": "X", "team": "Y"}),
        content_type="application/json",
    )
    assert rv.status_code == 503


def test_coach_add_member_validation(app_client, users_db, teams_mocks):
    ch = auth_header(1, "coach")
    tid = app_client.post(
        "/api/v1/coach/teams",
        headers=ch,
        data=json.dumps({"sport": "S", "team": "T"}),
        content_type="application/json",
    ).get_json()["team_id"]
    rv = app_client.post(f"/api/v1/coach/teams/{tid}/members", headers=ch, data="x")
    assert rv.status_code == 415


def test_coach_team_not_found(app_client, users_db, teams_mocks, monkeypatch):
    def raise_nf(*_a, **_k):
        raise ValueError("Команда не найдена")

    monkeypatch.setattr("sportorg.api.teams.get_coach_team_detail", raise_nf)
    rv = app_client.get("/api/v1/coach/teams/1", headers=auth_header(1, "coach"))
    assert rv.status_code == 404
