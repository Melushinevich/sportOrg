"""Тесты user_registration/profile_gender.py."""

import pytest

from user_registration.profile_gender import gender_db_to_ui, gender_ui_to_db


def test_gender_ui_to_db():
    assert gender_ui_to_db("Мужской") == "male"
    assert gender_ui_to_db("female") == "female"
    assert gender_ui_to_db(None) is None
    assert gender_ui_to_db("  ") is None


def test_gender_ui_to_db_invalid():
    with pytest.raises(ValueError, match="пол"):
        gender_ui_to_db("Другое")


def test_gender_db_to_ui():
    assert gender_db_to_ui("male") == "Мужской"
    assert gender_db_to_ui("female") == "Женский"
    assert gender_db_to_ui(None) is None
