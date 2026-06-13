"""Проверка и разбор даты рождения."""

from __future__ import annotations

import re
from datetime import date

_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DMY_RE = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")

MIN_BIRTH_YEAR = 1900
MAX_AGE_YEARS = 120


def _validate_date_bounds(value: date) -> None:
    today = date.today()
    if value > today:
        raise ValueError("Дата рождения не может быть в будущем")
    if value.year < MIN_BIRTH_YEAR:
        raise ValueError(f"Укажите год не раньше {MIN_BIRTH_YEAR}")
    age = today.year - value.year - (
        (today.month, today.day) < (value.month, value.day)
    )
    if age > MAX_AGE_YEARS:
        raise ValueError(f"Возраст не может превышать {MAX_AGE_YEARS} лет")


def parse_iso_birth_date(raw) -> date | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip()
    if not s:
        return None
    if not _ISO_RE.match(s):
        raise ValueError("Дата рождения в формате ГГГГ-ММ-ДД")
    y, m, d = (int(x) for x in s.split("-"))
    try:
        value = date(y, m, d)
    except ValueError as exc:
        raise ValueError("Некорректная дата рождения") from exc
    _validate_date_bounds(value)
    return value


def parse_dmy_birth_date(raw) -> date | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip()
    if not s:
        return None
    match = _DMY_RE.match(s)
    if not match:
        raise ValueError("Дата рождения в формате ДД.ММ.ГГГГ")
    day, month, year = (int(x) for x in match.groups())
    try:
        value = date(year, month, day)
    except ValueError as exc:
        raise ValueError("Некорректная дата рождения") from exc
    _validate_date_bounds(value)
    return value


def require_dmy_birth_date(raw) -> date:
    if raw is None or not str(raw).strip():
        raise ValueError("Укажите дату рождения")
    value = parse_dmy_birth_date(raw)
    if value is None:
        raise ValueError("Укажите дату рождения")
    return value


def iso_from_dmy_text(text: str) -> str | None:
    value = require_dmy_birth_date(text)
    return value.isoformat()


def dmy_from_iso(iso: str | None) -> str:
    if not iso:
        return ""
    value = parse_iso_birth_date(iso)
    if value is None:
        return ""
    return value.strftime("%d.%m.%Y")
