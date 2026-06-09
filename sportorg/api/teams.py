import logging

from flask import Blueprint, jsonify, request

from sportorg.auth.jwt import require_coach_json, require_sportsman_json
from sportorg.extensions import limiter
from user_registration.storage import (
    add_team_member,
    apply_to_team,
    create_team,
    get_available_team_detail,
    get_coach_team_detail,
    init_db,
    list_available_teams,
    list_coach_teams,
    list_my_team_applications,
    remove_team_member,
    save_team_members,
    search_sportsmen,
)

log = logging.getLogger("sportorg.api.teams")

bp = Blueprint("teams", __name__, url_prefix="/api/v1")


def _json_error(message: str, code: str, http_status: int):
    return jsonify({"error": message, "code": code}), http_status


def _value_error_response(exc: ValueError):
    msg = str(exc)
    code = "invalid_input"
    status = 400
    if msg == "Команда не найдена":
        status = 404
        code = "not_found"
    elif "уже в составе" in msg.lower():
        status = 409
        code = "already_member"
    elif "не найден" in msg.lower():
        status = 404
        code = "not_found"
    return _json_error(msg, code, status)


@bp.get("/coach/teams")
@require_coach_json
@limiter.limit("120 per minute")
def coach_list_teams(user_id: int):
    """Страница «Команды»: список команд тренера (слева название, справа вид)."""
    init_db()
    teams = list_coach_teams(user_id)
    return jsonify({"teams": teams}), 200


@bp.post("/coach/teams")
@require_coach_json
@limiter.limit("30 per minute")
def coach_create_team(user_id: int):
    """
    Тренер создаёт команду (анкета: название, вид, критерии).
    Тело: {
      "sport": "Футбол",
      "team": "Команда 1",
      "criteria": ["Скорость", "Выносливость"]
    }
    """
    init_db()
    if not request.is_json:
        return _json_error("Ожидается JSON", "invalid_content_type", 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_error("Тело запроса должно быть JSON-объектом", "invalid_json", 400)

    sport = (data.get("sport") or "").strip()
    team = (data.get("team") or "").strip()
    criteria = data.get("criteria", [])
    if not sport:
        return _json_error("Поле sport обязательно", "invalid_input", 400)
    if not team:
        return _json_error("Поле team обязательно", "invalid_input", 400)
    if criteria is None:
        criteria = []
    if not isinstance(criteria, list):
        return _json_error("Поле criteria должно быть массивом строк", "invalid_input", 400)

    try:
        team_id = create_team(user_id, sport, team, criteria=criteria)
        detail = get_coach_team_detail(user_id, team_id)
    except ValueError as exc:
        return _json_error(str(exc), "invalid_input", 400)
    except Exception as exc:  # noqa: BLE001
        log.exception("coach_create_team_fail coach_id=%s", user_id)
        return _json_error(str(exc), "storage_error", 503)

    log.info("coach_create_team_ok coach_id=%s team_id=%s", user_id, team_id)
    return (
        jsonify(
            {
                "team_id": team_id,
                "sport": sport,
                "team": team,
                "criteria": detail.get("criteria", []),
            }
        ),
        201,
    )


@bp.get("/coach/teams/<int:team_id>")
@require_coach_json
@limiter.limit("120 per minute")
def coach_team_detail(team_id: int, user_id: int):
    """Страница команды: состав с ФИО, баллом, качествами и заметками."""
    init_db()
    try:
        detail = get_coach_team_detail(user_id, team_id)
    except ValueError as exc:
        return _value_error_response(exc)
    except Exception as exc:  # noqa: BLE001
        log.exception("coach_team_detail_fail coach_id=%s team_id=%s", user_id, team_id)
        return _json_error(str(exc), "storage_error", 503)
    return jsonify(detail), 200


@bp.get("/coach/sportsmen")
@require_coach_json
@limiter.limit("60 per minute")
def coach_search_sportsmen(user_id: int):
    """Поиск спортсменов для добавления в состав (?search=фамилия)."""
    init_db()
    query = request.args.get("search", "")
    rows = search_sportsmen(query)
    return jsonify({"sportsmen": rows}), 200


@bp.post("/coach/teams/<int:team_id>/members")
@require_coach_json
@limiter.limit("60 per minute")
def coach_add_member(team_id: int, user_id: int):
    """Добавить спортсмена в состав. Тело: { "athlete_user_id": 123 }"""
    init_db()
    if not request.is_json:
        return _json_error("Ожидается JSON", "invalid_content_type", 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_error("Тело запроса должно быть JSON-объектом", "invalid_json", 400)

    athlete_user_id = data.get("athlete_user_id")
    if athlete_user_id is None:
        return _json_error("Нужно поле athlete_user_id", "invalid_input", 400)
    try:
        athlete_user_id = int(athlete_user_id)
    except (TypeError, ValueError):
        return _json_error("athlete_user_id должен быть числом", "invalid_input", 400)

    try:
        member_id = add_team_member(user_id, team_id, athlete_user_id)
        detail = get_coach_team_detail(user_id, team_id)
    except ValueError as exc:
        return _value_error_response(exc)
    except Exception as exc:  # noqa: BLE001
        log.exception("coach_add_member_fail coach_id=%s team_id=%s", user_id, team_id)
        return _json_error(str(exc), "storage_error", 503)

    member = next((m for m in detail["members"] if m["member_id"] == member_id), None)
    log.info(
        "coach_add_member_ok coach_id=%s team_id=%s member_id=%s",
        user_id,
        team_id,
        member_id,
    )
    return jsonify({"member_id": member_id, "member": member}), 201


@bp.delete("/coach/teams/<int:team_id>/members/<int:member_id>")
@require_coach_json
@limiter.limit("60 per minute")
def coach_remove_member(team_id: int, member_id: int, user_id: int):
    """Удалить участника из состава."""
    init_db()
    try:
        remove_team_member(user_id, team_id, member_id)
    except ValueError as exc:
        return _value_error_response(exc)
    except Exception as exc:  # noqa: BLE001
        log.exception("coach_remove_member_fail coach_id=%s team_id=%s", user_id, team_id)
        return _json_error(str(exc), "storage_error", 503)
    return jsonify({"ok": True}), 200


@bp.put("/coach/teams/<int:team_id>/members")
@require_coach_json
@limiter.limit("30 per minute")
def coach_save_members(team_id: int, user_id: int):
    """
    Сохранить оценки качеств и заметки. Балл пересчитывается как среднее по качествам.
    Тело: {
      "members": [{
        "member_id": 1,
        "notes": "...",
        "qualities": [{ "quality_id": 1, "rating": 8 }, { "quality_id": 2, "rating": 9 }]
      }]
    }
    """
    init_db()
    if not request.is_json:
        return _json_error("Ожидается JSON", "invalid_content_type", 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_error("Тело запроса должно быть JSON-объектом", "invalid_json", 400)

    members = data.get("members")
    if not isinstance(members, list):
        return _json_error("Нужно поле members — массив объектов", "invalid_json", 400)

    try:
        saved = save_team_members(user_id, team_id, members)
    except ValueError as exc:
        return _value_error_response(exc)
    except Exception as exc:  # noqa: BLE001
        log.exception("coach_save_members_fail coach_id=%s team_id=%s", user_id, team_id)
        return _json_error(str(exc), "storage_error", 503)

    log.info("coach_save_members_ok coach_id=%s team_id=%s count=%s", user_id, team_id, len(saved))
    return jsonify({"members": saved}), 200


@bp.get("/available-teams")
@require_sportsman_json
@limiter.limit("120 per minute")
def available_teams(user_id: int):
    """
    Страница «Доступные виды»: вид спорта, команда, тренер, критерии.
    """
    init_db()
    sport = request.args.get("sport")
    rows = list_available_teams(sport_name=sport)
    return jsonify({"teams": rows}), 200


@bp.get("/available-teams/<int:team_id>")
@require_sportsman_json
@limiter.limit("120 per minute")
def available_team_detail(team_id: int, user_id: int):
    """Карточка команды перед откликом: критерии и данные тренера."""
    init_db()
    detail = get_available_team_detail(team_id)
    if detail is None:
        return _json_error("Команда не найдена", "not_found", 404)
    return jsonify(detail), 200


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
