from datetime import date, timedelta

import pytest

from user_registration.birth_date import (
    dmy_from_iso,
    iso_from_dmy_text,
    parse_dmy_birth_date,
    parse_iso_birth_date,
    require_dmy_birth_date,
)


def test_parse_iso_valid():
    assert parse_iso_birth_date("2000-05-15") == date(2000, 5, 15)


def test_parse_iso_invalid_format():
    with pytest.raises(ValueError, match="ГГГГ-ММ-ДД"):
        parse_iso_birth_date("15.05.2000")


def test_parse_iso_invalid_calendar():
    with pytest.raises(ValueError, match="Некорректная дата"):
        parse_iso_birth_date("2000-02-31")


def test_parse_iso_future():
    future = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValueError, match="будущем"):
        parse_iso_birth_date(future)


def test_parse_dmy_valid():
    assert parse_dmy_birth_date("15.05.2000") == date(2000, 5, 15)


def test_parse_dmy_invalid_format():
    with pytest.raises(ValueError, match="ДД.ММ.ГГГГ"):
        parse_dmy_birth_date("2000-05-15")


def test_require_dmy_empty():
    with pytest.raises(ValueError, match="Укажите дату рождения"):
        require_dmy_birth_date("")


def test_iso_from_dmy_text():
    assert iso_from_dmy_text("15.05.2000") == "2000-05-15"


def test_dmy_from_iso():
    assert dmy_from_iso("2000-05-15") == "15.05.2000"
    assert dmy_from_iso(None) == ""
