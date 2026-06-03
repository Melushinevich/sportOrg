import logging

from flask import Blueprint, jsonify, request

from sportorg.auth.jwt import require_coach_json, require_sportsman_json
from sportorg.extensions import limiter
from user_registration.storage import (
    apply_to_team,
    create_team,
    init_db,
    list_available_teams,
    list_my_team_applications,
)

log = logging.getLogger("sportorg.api.teams")

bp = Blueprint("teams", __name__, url_prefix="/api/v1")


def _json_error(message: str, code: str, http_status: int):
    return jsonify({"error": message, "code": code}), http_status


@bp.post("/coach/teams")
@require_coach_json
@limiter.limit("30 per minute")
def coach_create_team(user_id: int):
    """
    Тренер создаёт открытую команду (заявку на набор).
    Тело: { "sport": "Футбол", "team": "Команда 1" }
    """
    init_db()
    if not request.is_json:
        return _json_error("Ожидается JSON", "invalid_content_type", 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_error("Тело запроса должно быть JSON-объектом", "invalid_json", 400)

    sport = (data.get("sport") or "").strip()
    team = (data.get("team") or "").strip()
    if not sport:
        return _json_error("Поле sport обязательно", "invalid_input", 400)
    if not team:
        return _json_error("Поле team обязательно", "invalid_input", 400)

    try:
        team_id = create_team(user_id, sport, team)
    except ValueError as exc:
        return _json_error(str(exc), "invalid_input", 400)
    except Exception as exc:  # noqa: BLE001
        log.exception("coach_create_team_fail coach_id=%s", user_id)
        return _json_error(str(exc), "storage_error", 503)

    log.info("coach_create_team_ok coach_id=%s team_id=%s", user_id, team_id)
    return jsonify({"team_id": team_id, "sport": sport, "team": team}), 201


@bp.get("/available-teams")
@require_sportsman_json
@limiter.limit("120 per minute")
def available_teams(user_id: int):
    """
    Спортсмен видит открытые команды (заявки тренеров).
    Query: ?sport=Футбол (опционально)
    """
    init_db()
    sport = request.args.get("sport")
    rows = list_available_teams(sport_name=sport)
    return jsonify({"teams": rows}), 200


@bp.post("/teams/<int:team_id>/apply")
@require_sportsman_json
@limiter.limit("60 per minute")
def apply_team(team_id: int, user_id: int):
    """Спортсмен подаёт заявку в команду."""
    init_db()
    try:
        app_id = apply_to_team(team_id=team_id, athlete_user_id=user_id)
    except ValueError as exc:
        msg = str(exc)
        code = "invalid_input"
        status = 400
        if "уже подана" in msg.lower():
            code = "already_applied"
            status = 409
        return _json_error(msg, code, status)
    except Exception as exc:  # noqa: BLE001
        log.exception("apply_team_fail team_id=%s athlete_id=%s", team_id, user_id)
        return _json_error(str(exc), "storage_error", 503)

    log.info("apply_team_ok team_id=%s athlete_id=%s app_id=%s", team_id, user_id, app_id)
    return jsonify({"application_id": app_id, "team_id": team_id, "status": "pending"}), 201


@bp.get("/me/applications")
@require_sportsman_json
@limiter.limit("120 per minute")
def my_applications(user_id: int):
    """Страница 'Команды': заявки спортсмена (в какие команды подал)."""
    init_db()
    rows = list_my_team_applications(user_id)
    return jsonify({"applications": rows}), 200

