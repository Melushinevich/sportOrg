"""Тесты frontend/teams_service.py (логика без Qt)."""

import pytest

from frontend.api_client import ApiError
from frontend.teams_service import (
    average_rating,
    build_member_save_payload,
    criteria_texts,
    load_coach_applications,
    load_coach_team,
    success_percent,
)


def test_criteria_texts_mixed():
    assert criteria_texts(["  a  ", "", {"text": " b "}, {"text": ""}, 42]) == ["a", "b"]


def test_average_rating_and_success_percent():
    assert average_rating({}) is None
    assert average_rating({"a": 8, "b": 6}) == 7.0
    assert success_percent(score=9.2) == 9.2
    assert success_percent(ratings={"x": 10, "y": 8}) == 9.0


def test_build_member_save_payload_filters_and_maps():
    payload = build_member_save_payload(
        member_id=5,
        notes="  капитан  ",
        qualities=[
            {"name": "Скорость", "skill_id": 1},
            {"name": "Пас", "skill_id": 2},
            {"name": ""},
        ],
        ratings_by_name={"Скорость": 8, "Пас": "—"},
    )
    assert payload == {
        "member_id": 5,
        "notes": "капитан",
        "qualities": [{"name": "Скорость", "rating": 8, "skill_id": 1}],
    }


class _FakeCoachApi:
    def list_coach_applications(self, **kwargs):
        assert kwargs["token"] == "test-coach-token"
        assert kwargs["status"] == "pending"
        return {
            "applications": [
                {
                    "application_id": 10,
                    "team_id": 3,
                    "team": "Dream",
                    "sport": "Футбол",
                    "athlete_user_id": 7,
                    "full_name": "Иванов Иван",
                    "email": "i@test.local",
                    "phone": "+7",
                    "skills": [{"name": "Скорость", "rating": 8}],
                    "status": "pending",
                }
            ]
        }

    def get_coach_team(self, **kwargs):
        return {
            "team_id": 3,
            "team": "Dream",
            "sport": "Футбол",
            "criteria": [{"criterion_id": 1, "text": "Дисциплина", "sort_order": 0}],
            "members": [
                {
                    "member_id": 1,
                    "athlete_user_id": 7,
                    "full_name": "Иванов Иван",
                    "qualities": [{"name": "Скорость", "rating": 8, "skill_id": 1}],
                    "score": 8.0,
                    "athlete_score": 7.5,
                    "notes": "",
                }
            ],
        }


def test_load_coach_applications_maps_skills(coach_session):
    rows = load_coach_applications(api=_FakeCoachApi())
    assert len(rows) == 1
    assert rows[0]["skills"] == [{"name": "Скорость", "rating": 8}]


def test_load_coach_team_maps_qualities(coach_session):
    data = load_coach_team(team_id=3, api=_FakeCoachApi())
    assert data["team"] == "Dream"
    assert data["members"][0]["ratings"] == {"Скорость": 8}
    assert data["members"][0]["score"] == 8.0


def test_load_coach_applications_requires_token():
    from frontend.session import session

    session.clear()
    with pytest.raises(ApiError, match="Войдите"):
        load_coach_applications(api=_FakeCoachApi())


class _FullCoachApi(_FakeCoachApi):
    def list_sports_catalog(self, **kwargs):
        return {"sports": [{"sport_id": 1, "name": "Футбол"}]}

    def list_skills_catalog(self, **kwargs):
        return {"skills": [{"skill_id": 2, "name": "Скорость", "category": None}]}

    def list_coach_teams(self, **kwargs):
        return {"teams": [{"team_id": 1, "team": "Dream", "sport": "Футбол"}]}

    def create_coach_team(self, **kwargs):
        return {
            "team_id": 9,
            "team": kwargs["team"],
            "sport": kwargs["sport"],
            "criteria": [{"text": "Дисциплина"}],
        }

    def save_coach_team_members(self, **kwargs):
        return {
            "members": [
                {
                    "member_id": 1,
                    "full_name": "Иванов",
                    "qualities": [{"name": "Скорость", "rating": 9}],
                    "score": 9.0,
                    "notes": "ok",
                }
            ]
        }

    def accept_coach_application(self, **kwargs):
        return {
            "member_id": 2,
            "application_id": kwargs["application_id"],
            "team_id": 3,
            "team": "Dream",
            "sport": "Футбол",
            "full_name": "Петров",
            "email": "p@t.com",
            "phone": "",
            "skills": [],
        }


def test_load_catalogs_and_create_team(coach_session):
    from frontend.teams_service import (
        accept_coach_application,
        create_coach_team,
        load_coach_teams,
        load_skills_catalog,
        load_sports_catalog,
        save_team_members,
    )

    api = _FullCoachApi()
    sports = load_sports_catalog(api=api)
    assert sports[0]["name"] == "Футбол"
    skills = load_skills_catalog(api=api)
    assert skills[0]["skill_id"] == 2
    teams = load_coach_teams(api=api)
    assert teams[0]["team_id"] == 1
    created = create_coach_team(team="New", sport="Футбол", criteria=["A"], api=api)
    assert created["team_id"] == 9
    assert created["criteria"] == ["Дисциплина"]
    saved = save_team_members(
        team_id=3,
        members=[{"member_id": 1, "notes": "n", "qualities": [{"name": "Скорость", "rating": 9}]}],
        api=api,
    )
    assert saved[0]["score"] == 9.0
    accepted = accept_coach_application(application_id=10, api=api)
    assert accepted["member_id"] == 2


def test_remove_team_member(coach_session):
    from frontend.teams_service import remove_team_member

    class _Api:
        def remove_coach_team_member(self, **kwargs):
            assert kwargs["team_id"] == 3
            assert kwargs["member_id"] == 5
            return {"ok": True}

    remove_team_member(team_id=3, member_id=5, api=_Api())
