import logging

from flask import Blueprint, jsonify, request

from sportorg.auth.jwt import require_sportsman_json
from sportorg.extensions import limiter
from user_registration.storage import (
    add_athlete_skill,
    init_db,
    list_athlete_skills,
    replace_athlete_skills,
)

log = logging.getLogger("sportorg.api.skills")

me_bp = Blueprint("me", __name__, url_prefix="/api/v1/me")

MAX_SKILLS = 100
MAX_NAME_LEN = 200


def _json_error(message: str, code: str, http_status: int):
    return jsonify({"error": message, "code": code}), http_status


def _validate_rating(rating) -> tuple[bool, str | None]:
    if rating is None:
        return True, None
    try:
        v = int(rating)
    except (TypeError, ValueError):
        return False, "Оценка должна быть числом или null"
    if v < 1 or v > 10:
        return False, "Оценка по 10-балльной шкале: от 1 до 10 или пусто"
    return True, None


@me_bp.get("/skills")
@require_sportsman_json
@limiter.limit("60 per minute")
def get_skills(user_id: int):
    init_db()
    rows = list_athlete_skills(user_id)
    return jsonify({"skills": rows}), 200


@me_bp.post("/skills")
@require_sportsman_json
@limiter.limit("30 per minute")
def post_skill(user_id: int):
    init_db()
    if not request.is_json:
        return _json_error("Ожидается JSON", "invalid_content_type", 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_error("Тело запроса должно быть JSON-объектом", "invalid_json", 400)

    name = (data.get("name") or "").strip()
    if len(name) > MAX_NAME_LEN:
        return _json_error("Слишком длинное название скилла", "invalid_input", 400)

    current = list_athlete_skills(user_id)
    if len(current) >= MAX_SKILLS:
        return _json_error(f"Не больше {MAX_SKILLS} скиллов", "limit_exceeded", 400)

    new_id = add_athlete_skill(user_id, name)
    log.info("skill_added user_id=%s skill_id=%s", user_id, new_id)
    return jsonify({"id": new_id, "name": name, "rating": None, "sort_order": len(current)}), 201


@me_bp.put("/skills")
@require_sportsman_json
@limiter.limit("30 per minute")
def put_skills(user_id: int):
    init_db()
    if not request.is_json:
        return _json_error("Ожидается JSON", "invalid_content_type", 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_error("Тело запроса должно быть JSON-объектом", "invalid_json", 400)

    skills = data.get("skills")
    if not isinstance(skills, list):
        return _json_error("Нужно поле skills — массив объектов", "invalid_json", 400)
    if len(skills) > MAX_SKILLS:
        return _json_error(f"Не больше {MAX_SKILLS} скиллов", "invalid_input", 400)

    cleaned = []
    for i, item in enumerate(skills):
        if not isinstance(item, dict):
            return _json_error(f"skills[{i}] должен быть объектом", "invalid_input", 400)
        name = (item.get("name") or "").strip()
        if len(name) > MAX_NAME_LEN:
            return _json_error(f"Слишком длинное название в skills[{i}]", "invalid_input", 400)
        rating = item.get("rating", None)
        if rating == "":
            rating = None
        ok, err = _validate_rating(rating)
        if not ok:
            return _json_error(err or "Неверная оценка", "invalid_input", 400)
        cleaned.append({"name": name, "rating": rating})

    try:
        replace_athlete_skills(user_id, cleaned)
    except Exception as exc:  # noqa: BLE001
        log.exception("skill_save_fail user_id=%s", user_id)
        return _json_error(str(exc), "storage_error", 503)

    log.info("skills_saved user_id=%s count=%s", user_id, len(cleaned))
    rows = list_athlete_skills(user_id)
    return jsonify({"skills": rows}), 200
