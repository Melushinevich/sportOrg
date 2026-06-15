"""Тесты frontend/athlete_skills_service.py."""

from frontend.athlete_skills_service import (
    has_filled_skills,
    load_skills_page,
    save_my_skills,
)


class _FakeAthleteApi:
    def __init__(self):
        self.saved_payload = None

    def get_my_skills(self, **kwargs):
        return {
            "skills": [
                {"id": 1, "name": "Скорость", "rating": 8},
                {"id": 2, "name": "Пас", "rating": None},
            ],
            "catalog": [{"name": "Пас"}, {"name": "Скорость"}, {"name": "Удар"}],
        }

    def list_athlete_skills_catalog(self, **kwargs):
        raise AssertionError("catalog already in get_my_skills response")

    def save_my_skills(self, **kwargs):
        self.saved_payload = kwargs["skills"]
        return {
            "skills": [
                {"id": 1, "name": "Скорость", "rating": 9},
            ]
        }


def test_load_skills_page_parses_catalog(athlete_session):
    skills, catalog = load_skills_page(api=_FakeAthleteApi())
    assert [s["name"] for s in skills] == ["Скорость", "Пас"]
    assert catalog == ["Пас", "Скорость", "Удар"]


def test_has_filled_skills():
    assert not has_filled_skills([])
    assert not has_filled_skills([{"name": "Пас", "rating": None}])
    assert has_filled_skills([{"name": "Скорость", "rating": 8}])


def test_save_my_skills_normalizes_payload(athlete_session):
    api = _FakeAthleteApi()
    result = save_my_skills(
        skills=[
            {"name": "Скорость", "rating": 9},
            {"name": "  ", "rating": 5},
            {"skill": "Удар", "rating": "—"},
        ],
        api=api,
    )
    assert api.saved_payload == [
        {"name": "Скорость", "rating": 9},
        {"name": "Удар", "rating": None},
    ]
    assert result == [{"id": 1, "name": "Скорость", "rating": 9}]
