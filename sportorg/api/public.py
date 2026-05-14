import logging

from flask import Blueprint, jsonify, request

from sportorg.auth.jwt import issue_access_token
from sportorg.extensions import limiter
from sportorg.notifications.verification_stub import log_verification_stub
from user_registration.registration import login_user, register_user
from user_registration.storage import init_db

log = logging.getLogger("sportorg.api")

bp = Blueprint("api", __name__, url_prefix="/api/v1")


def _json_error(message: str, code: str, http_status: int):
    body = {"error": message, "code": code}
    return jsonify(body), http_status


@bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@bp.post("/register")
@limiter.limit("15 per minute")
def api_register():
    init_db()
    if not request.is_json:
        return _json_error("Ожидается JSON (Content-Type: application/json)", "invalid_content_type", 415)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_error("Тело запроса должно быть JSON-объектом", "invalid_json", 400)

    result = register_user(
        {
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "email": data.get("email", ""),
            "password": data.get("password", ""),
            "password2": data.get("password2", data.get("password", "")),
            "role": data.get("role") or "sportsman",
            "patronymic": data.get("patronymic"),
            "birth_date": data.get("birth_date"),
            "phone": data.get("phone"),
            "city": data.get("city"),
        }
    )

    if result.get("success"):
        uid = result["user_id"]
        log.info(
            "register_ok user_id=%s email=%s role=%s",
            uid,
            result.get("email"),
            result.get("role"),
        )
        log_verification_stub(result["email"], uid)
        return (
            jsonify(
                {
                    "user_id": uid,
                    "email": result["email"],
                    "role": result["role"],
                }
            ),
            201,
        )

    err = result.get("error", "Ошибка")
    c = result.get("code", "unknown")
    log.warning("register_fail code=%s email=%s", c, data.get("email"))

    status_map = {
        "invalid_input": 400,
        "email_already_exists": 409,
        "storage_error": 503,
    }
    return _json_error(err, c, status_map.get(c, 400))


@bp.post("/login")
@limiter.limit("30 per minute")
def api_login():
    init_db()
    if not request.is_json:
        return _json_error("Ожидается JSON", "invalid_content_type", 415)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_error("Тело запроса должно быть JSON-объектом", "invalid_json", 400)

    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    ok, payload = login_user(email, password)
    if ok:
        log.info("login_ok email=%s user_id=%s", email, payload.get("id"))
        token = issue_access_token(int(payload["id"]), str(payload.get("role", "")))
        return jsonify({"user": payload, "access_token": token, "token_type": "Bearer"}), 200

    log.warning("login_fail email=%s", email)
    return _json_error(str(payload), "unauthorized", 401)
