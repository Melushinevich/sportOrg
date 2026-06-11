"""Загрузка и сохранение анкеты через API /api/v1/me/profile."""

from __future__ import annotations

import re

from PyQt5.QtCore import QDate

from .api_client import ApiError, SportOrgApi
from .session import session

_DATE_DMY = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")


def parse_fio(full_name: str) -> tuple[str, str, str | None]:
    name = (full_name or "").strip()
    if not name:
        raise ValueError("Введите ФИО")
    parts = name.split()
    if len(parts) < 2:
        raise ValueError(
            "Укажите фамилию и имя через пробел\n(например: Иванов Иван или Иванов Иван Иванович)"
        )
    patronymic = " ".join(parts[2:]) if len(parts) > 2 else None
    return parts[0], parts[1], patronymic


def iso_from_qdate(qdate: QDate) -> str | None:
    if qdate is None or not qdate.isValid():
        return None
    return qdate.toString("yyyy-MM-dd")


def iso_from_dmy_text(text: str) -> str | None:
    raw = (text or "").strip()
    if not raw:
        return None
    match = _DATE_DMY.match(raw)
    if not match:
        raise ValueError("Дата рождения в формате ДД.ММ.ГГГГ")
    day, month, year = match.groups()
    return f"{year}-{month}-{day}"


def dmy_from_iso(iso: str | None) -> str:
    if not iso:
        return ""
    parts = str(iso).split("-")
    if len(parts) != 3:
        return ""
    return f"{parts[2]}.{parts[1]}.{parts[0]}"


def format_fio(profile: dict) -> str:
    return " ".join(
        part
        for part in (
            profile.get("last_name"),
            profile.get("first_name"),
            profile.get("patronymic"),
        )
        if part
    )


def _api() -> SportOrgApi:
    return SportOrgApi()


def load_profile(api: SportOrgApi | None = None) -> dict | None:
    if not session.is_logged_in:
        return None
    client = api or _api()
    try:
        data = client.get_profile(token=session.access_token)
    except ApiError:
        return None
    return data.get("profile")


def save_profile(
    *,
    fio: str,
    birth_date: str | None,
    city: str,
    phone: str,
    api: SportOrgApi | None = None,
) -> dict:
    if not session.is_logged_in:
        raise ValueError("Сначала войдите в систему")

    last_name, first_name, patronymic = parse_fio(fio)
    city_val = (city or "").strip() or None
    phone_val = (phone or "").strip() or None

    client = api or _api()
    data = client.update_profile(
        token=session.access_token,
        last_name=last_name,
        first_name=first_name,
        patronymic=patronymic,
        birth_date=birth_date,
        city=city_val,
        phone=phone_val,
    )
    profile = data.get("profile")
    if not profile:
        raise ApiError("Пустой ответ сервера", code="empty_response")
    return profile


def apply_profile_to_sportsman_form(window, profile: dict) -> None:
    fio = format_fio(profile)
    if fio:
        window.fio_input.setText(fio)

    birth = profile.get("birth_date")
    if birth:
        parts = str(birth).split("-")
        if len(parts) == 3:
            window.birth_date.setDate(
                QDate(int(parts[0]), int(parts[1]), int(parts[2]))
            )

    if profile.get("city"):
        window.city_input.setText(profile["city"])
    if profile.get("phone"):
        window.phone_input.setText(profile["phone"])


def apply_profile_to_trainer_form(window, profile: dict) -> None:
    fio = format_fio(profile)
    if fio:
        window.fio_input.setText(fio)

    birth = dmy_from_iso(profile.get("birth_date"))
    if birth:
        window.birth_date.setText(birth)

    if profile.get("city"):
        window.city_input.setText(profile["city"])
    if profile.get("phone"):
        window.phone_input.setText(profile["phone"])
