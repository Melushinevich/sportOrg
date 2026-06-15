"""Тесты format_application_skills (страница «Отклики»)."""

from frontend.application_skills import format_application_skills


def test_format_application_skills_with_ratings():
    display, tooltip = format_application_skills(
        [
            {"name": "Скорость", "rating": 8},
            {"name": "Выносливость", "rating": 6},
        ]
    )
    assert display == "Скорость, Выносливость"
    assert "Скорость — 8/10" in tooltip
    assert "Выносливость — 6/10" in tooltip
    assert "<br>" in tooltip


def test_format_application_skills_without_rating():
    display, tooltip = format_application_skills([{"name": "Пас", "rating": None}])
    assert display == "Пас"
    assert "Пас — без оценки" in tooltip


def test_format_application_skills_legacy_strings():
    display, tooltip = format_application_skills(["Скорость", "  ", "Удар"])
    assert display == "Скорость, Удар"
    assert tooltip == "• Скорость<br>• Удар"


def test_format_application_skills_empty():
    assert format_application_skills([]) == ("", "—")
    assert format_application_skills([{"name": ""}]) == ("", "—")
