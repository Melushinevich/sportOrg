"""Тесты frontend/profile_service.py (без Qt-форм)."""

import pytest

from frontend.profile_service import (
    athlete_display_name,
    format_fio,
    is_profile_complete,
    parse_fio,
)


def test_parse_fio_two_and_three_parts():
    assert parse_fio("Иванов Иван") == ("Иванов", "Иван", None)
    assert parse_fio("  Петров  Пётр  Сергеевич ") == ("Петров", "Пётр", "Сергеевич")


def test_parse_fio_invalid():
    with pytest.raises(ValueError, match="ФИО"):
        parse_fio("")
    with pytest.raises(ValueError, match="фамилию"):
        parse_fio("Один")


def test_athlete_display_name():
    assert athlete_display_name({"last_name": "Aboba", "first_name": "aa"}) == "Aboba aa"
    assert athlete_display_name({}) == "СПОРТСМЕН"
    assert athlete_display_name(None) == "СПОРТСМЕН"


def test_format_fio():
    assert (
        format_fio(
            {
                "last_name": "Иванов",
                "first_name": "Иван",
                "patronymic": "Иванович",
            }
        )
        == "Иванов Иван Иванович"
    )
    assert format_fio({"last_name": "A", "first_name": "B"}) == "A B"


@pytest.mark.parametrize(
    "profile,expected",
    [
        (None, False),
        ({}, False),
        (
            {
                "last_name": "A",
                "first_name": "B",
                "birth_date": "2000-01-01",
                "city": "Москва",
                "phone": "+7",
                "gender": "Мужской",
            },
            True,
        ),
        (
            {
                "last_name": "A",
                "first_name": "B",
                "birth_date": "2000-01-01",
                "city": "Москва",
                "phone": "+7",
                "gender": "Другое",
            },
            False,
        ),
        (
            {
                "last_name": "A",
                "first_name": "",
                "birth_date": "2000-01-01",
                "city": "Москва",
                "phone": "+7",
                "gender": "Женский",
            },
            False,
        ),
    ],
)
def test_is_profile_complete(profile, expected):
    assert is_profile_complete(profile) is expected


class _FakeProfileApi:
    def get_profile(self, **kwargs):
        return {
            "profile": {
                "last_name": "Иванов",
                "first_name": "Иван",
                "birth_date": "2000-01-01",
                "city": "Москва",
                "phone": "+7",
                "gender": "Мужской",
            }
        }

    def update_profile(self, **kwargs):
        return {
            "profile": {
                "last_name": kwargs["last_name"],
                "first_name": kwargs["first_name"],
                "patronymic": kwargs.get("patronymic"),
                "birth_date": kwargs.get("birth_date"),
                "city": kwargs.get("city"),
                "phone": kwargs.get("phone"),
                "gender": kwargs.get("gender"),
            }
        }


def test_load_profile(monkeypatch, athlete_session):
    from frontend.profile_service import load_profile
    from frontend.session import session

    session.access_token = "tok"
    profile = load_profile(api=_FakeProfileApi())
    assert profile["last_name"] == "Иванов"


def test_save_profile(monkeypatch, athlete_session):
    from frontend.profile_service import save_profile
    from frontend.session import session

    session.access_token = "tok"
    profile = save_profile(
        fio="Иванов Иван Иванович",
        birth_date="2000-01-01",
        city="Москва",
        phone="+7999",
        gender="Мужской",
        api=_FakeProfileApi(),
    )
    assert profile["first_name"] == "Иван"
    assert is_profile_complete(profile)


def test_load_profile_not_logged_in():
    from frontend.profile_service import load_profile
    from frontend.session import session

    session.clear()
    assert load_profile(api=_FakeProfileApi()) is None
