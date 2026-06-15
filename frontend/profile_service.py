"""Загрузка и сохранение анкеты через API /api/v1/me/profile."""

from __future__ import annotations

from user_registration.birth_date import dmy_from_iso, iso_from_dmy_text
from .api_client import ApiError, SportOrgApi
from .session import session

GENDER_VALUES = frozenset({"Мужской", "Женский"})


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


def iso_from_qdate(qdate) -> str | None:
    if qdate is None or not qdate.isValid():
        return None
    return qdate.toString("yyyy-MM-dd")


def is_profile_complete(profile: dict | None) -> bool:
    """Анкета заполнена: ФИО, дата рождения, город и телефон."""
    if not profile:
        return False

    last = (profile.get("last_name") or "").strip()
    first = (profile.get("first_name") or "").strip()
    if not last or not first:
        return False

    if not profile.get("birth_date"):
        return False
    if not (profile.get("city") or "").strip():
        return False
    if not (profile.get("phone") or "").strip():
        return False
    gender = (profile.get("gender") or "").strip()
    if gender not in GENDER_VALUES:
        return False
    return True


def gender_from_combo(combo) -> str | None:
    text = (combo.currentText() or "").strip()
    if text in GENDER_VALUES:
        return text
    if hasattr(combo, "lineEdit"):
        text = (combo.lineEdit().text() or "").strip()
        if text in GENDER_VALUES:
            return text
    return None


def apply_gender_to_combo(combo, gender: str | None) -> None:
    value = (gender or "").strip()
    if value in GENDER_VALUES:
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
            return
        if hasattr(combo, "lineEdit"):
            combo.lineEdit().setText(value)
        return
    if hasattr(combo, "lineEdit"):
        combo.lineEdit().clear()
    combo.setCurrentIndex(-1)


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


def athlete_display_name(profile: dict | None = None) -> str:
    """Имя спортсмена для шапки экранов."""
    if profile is None:
        profile = load_profile()
    if profile:
        name = format_fio(profile).strip()
        if name:
            return name
    return "СПОРТСМЕН"


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
    gender: str | None = None,
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
        gender=gender,
    )
    profile = data.get("profile")
    if not profile:
        raise ApiError("Пустой ответ сервера", code="empty_response")
    return profile


def apply_profile_to_sportsman_form(window, profile: dict) -> None:
    fio = format_fio(profile)
    window.fio_input.setText(fio) if fio else window.fio_input.clear()

    birth = dmy_from_iso(profile.get("birth_date"))
    if birth:
        window.birth_date.set_dmy_text(birth)
    elif hasattr(window.birth_date, "clear_date"):
        window.birth_date.clear_date()
    else:
        window.birth_date.clear()

    if profile.get("city"):
        window.city_input.setText(profile["city"])
    else:
        window.city_input.clear()
    if profile.get("phone"):
        if hasattr(window.phone_input, "set_phone_text"):
            window.phone_input.set_phone_text(profile["phone"])
        else:
            window.phone_input.setText(profile["phone"])
    else:
        if hasattr(window.phone_input, "clear_phone"):
            window.phone_input.clear_phone()
        else:
            window.phone_input.clear()

    apply_gender_to_combo(window.gender_combo, profile.get("gender"))


def apply_profile_to_trainer_form(window, profile: dict) -> None:
    fio = format_fio(profile)
    window.fio_input.setText(fio) if fio else window.fio_input.clear()

    birth = dmy_from_iso(profile.get("birth_date"))
    if birth:
        window.birth_date.set_dmy_text(birth)
    elif hasattr(window.birth_date, "clear_date"):
        window.birth_date.clear_date()
    else:
        window.birth_date.clear()

    if profile.get("city"):
        window.city_input.setText(profile["city"])
    else:
        window.city_input.clear()
    if profile.get("phone"):
        if hasattr(window.phone_input, "set_phone_text"):
            window.phone_input.set_phone_text(profile["phone"])
        else:
            window.phone_input.setText(profile["phone"])
    else:
        if hasattr(window.phone_input, "clear_phone"):
            window.phone_input.clear_phone()
        else:
            window.phone_input.clear()

    apply_gender_to_combo(window.gender_combo, profile.get("gender"))
