"""Тесты frontend/athlete_teams_service.py."""

import pytest

from frontend.api_client import ApiError
from frontend.athlete_teams_service import apply_to_team, load_available_teams, load_my_teams


class _FakeAthleteTeamsApi:
    def list_my_teams(self, **kwargs):
        return {
            "teams": [
                {
                    "member_id": 1,
                    "team_id": 2,
                    "team": "Dream",
                    "sport": "Футбол",
                    "coach": "Иванов",
                }
            ]
        }

    def list_available_teams(self, **kwargs):
        assert kwargs.get("sport") == "Футбол"
        return {
            "teams": [
                {
                    "team_id": 3,
                    "team": "Stars",
                    "sport": "Футбол",
                    "coach": "",
                }
            ]
        }

    def apply_to_team(self, **kwargs):
        return {"application_id": 9, "status": "pending"}


def test_load_my_teams(athlete_session):
    rows = load_my_teams(api=_FakeAthleteTeamsApi())
    assert rows[0]["team"] == "Dream"
    assert rows[0]["coach"] == "Иванов"


def test_load_available_teams_default_coach(athlete_session):
    rows = load_available_teams(sport="Футбол", api=_FakeAthleteTeamsApi())
    assert rows[0]["coach"] == "—"


def test_apply_to_team(athlete_session):
    result = apply_to_team(team_id=3, api=_FakeAthleteTeamsApi())
    assert result["application_id"] == 9


def test_load_my_teams_requires_token():
    from frontend.session import session

    session.clear()
    with pytest.raises(ApiError):
        load_my_teams(api=_FakeAthleteTeamsApi())
