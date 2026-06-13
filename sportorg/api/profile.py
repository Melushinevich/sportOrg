import logging

from flask import Blueprint, jsonify, request

from sportorg.auth.jwt import require_user_json
from sportorg.extensions import limiter
from user_registration.birth_date import parse_iso_birth_date
from user_registration.storage import get_user_profile, init_db, update_user_profile

log = logging.getLogger("sportorg.api.profile")

me_profile_bp = Blueprint("me_profile", __name__, url_prefix="/api/v1/me")

_VALID_GENDERS = frozenset({"Мужской", "Женский"})


def _json_error(message: str, code: str, http_status: int):
    return jsonify({"error": message, "code": code}), http_status


def _parse_gender(raw) -> str | None:
    if raw is None or raw == "":
        return None
    value = str(raw).strip()
    if value not in _VALID_GENDERS:
        raise ValueError("Укажите пол: Мужской или Женский")
    return value


def _profile_response(profile: dict):
    return jsonify({"profile": profile})


@me_profile_bp.get("/profile")
@require_user_json
@limiter.limit("60 per minute")
def get_profile(user_id: int):
    init_db()
    profile = get_user_profile(user_id)
    if profile is None:
        return _json_error("Профиль не найден", "not_found", 404)
    return _profile_response(profile)


@me_profile_bp.put("/profile")
@require_user_json
@limiter.limit("30 per minute")
def put_profile(user_id: int):
    init_db()
    body = request.get_json(silent=True) or {}

    try:
        birth = parse_iso_birth_date(body.get("birth_date"))
    except ValueError as exc:
        return _json_error(str(exc), "invalid_birth_date", 400)

    try:
        gender = _parse_gender(body.get("gender"))
    except ValueError as exc:
        return _json_error(str(exc), "invalid_gender", 400)

    payload = {
        "last_name": body.get("last_name"),
        "first_name": body.get("first_name"),
        "patronymic": body.get("patronymic"),
        "birth_date": birth,
        "phone": body.get("phone"),
        "city": body.get("city"),
        "gender": gender,
    }

    try:
        profile = update_user_profile(user_id, payload)
    except ValueError as exc:
        msg = str(exc)
        msg_lower = msg.lower()
        if "пол" in msg_lower:
            code = "invalid_gender"
        elif any(
            token in msg_lower
            for token in ("дата рождения", "некорректная дата", "возраст", "год")
        ):
            code = "invalid_birth_date"
        else:
            code = "validation_error"
        return _json_error(msg, code, 400)
    except Exception:
        log.exception("profile update failed user_id=%s", user_id)
        return _json_error("Не удалось сохранить профиль", "server_error", 500)

    return _profile_response(profile)
