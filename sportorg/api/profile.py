import logging
import re
from datetime import date

from flask import Blueprint, jsonify, request

from sportorg.auth.jwt import require_user_json
from sportorg.extensions import limiter
from user_registration.storage import get_user_profile, init_db, update_user_profile

log = logging.getLogger("sportorg.api.profile")

me_profile_bp = Blueprint("me_profile", __name__, url_prefix="/api/v1/me")

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _json_error(message: str, code: str, http_status: int):
    return jsonify({"error": message, "code": code}), http_status


def _parse_birth_date(raw) -> date | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip()
    if not s:
        return None
    if not _DATE_RE.match(s):
        raise ValueError("Дата рождения в формате ГГГГ-ММ-ДД")
    y, m, d = (int(x) for x in s.split("-"))
    return date(y, m, d)


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
        birth = _parse_birth_date(body.get("birth_date"))
    except ValueError as exc:
        return _json_error(str(exc), "invalid_birth_date", 400)

    payload = {
        "last_name": body.get("last_name"),
        "first_name": body.get("first_name"),
        "patronymic": body.get("patronymic"),
        "birth_date": birth,
        "phone": body.get("phone"),
        "city": body.get("city"),
    }

    try:
        profile = update_user_profile(user_id, payload)
    except ValueError as exc:
        return _json_error(str(exc), "validation_error", 400)
    except Exception:
        log.exception("profile update failed user_id=%s", user_id)
        return _json_error("Не удалось сохранить профиль", "server_error", 500)

    return _profile_response(profile)
