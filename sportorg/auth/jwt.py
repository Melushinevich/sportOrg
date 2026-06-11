import os
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any

import jwt
from flask import jsonify, request

DEFAULT_SECRET = "dev-jwt-secret-change-in-production"
ALGO = "HS256"
TTL_HOURS = int(os.environ.get("JWT_TTL_HOURS", "168"))


def jwt_secret() -> str:
    return os.environ.get("JWT_SECRET_KEY", DEFAULT_SECRET)


def issue_access_token(user_id: int, role: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=TTL_HOURS),
    }
    return jwt.encode(payload, jwt_secret(), algorithm=ALGO)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, jwt_secret(), algorithms=[ALGO])
    except jwt.PyJWTError:
        return None


def bearer_token() -> str | None:
    h = request.headers.get("Authorization", "")
    if h.lower().startswith("bearer "):
        return h[7:].strip() or None
    return None


def require_sportsman_json(f):
    """JWT обязателен; роль sportsman; иначе 401/403 JSON."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        from user_registration.storage import get_user_by_id

        raw = bearer_token()
        if not raw:
            return jsonify({"error": "Нужен заголовок Authorization: Bearer <token>", "code": "unauthorized"}), 401
        data = decode_access_token(raw)
        if not data:
            return jsonify({"error": "Недействительный или просроченный токен", "code": "invalid_token"}), 401
        try:
            uid = int(data["sub"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Недействительный токен", "code": "invalid_token"}), 401

        user = get_user_by_id(uid)
        if user is None:
            return jsonify({"error": "Пользователь не найден", "code": "not_found"}), 401
        if (user.get("role") or "").lower() != "sportsman":
            return jsonify({"error": "Скиллы доступны только спортсмену", "code": "forbidden_role"}), 403

        return f(user_id=uid, *args, **kwargs)

    return wrapped


def require_coach_json(f):
    """JWT обязателен; роль coach; иначе 401/403 JSON."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        from user_registration.storage import get_user_by_id

        raw = bearer_token()
        if not raw:
            return jsonify({"error": "Нужен заголовок Authorization: Bearer <token>", "code": "unauthorized"}), 401
        data = decode_access_token(raw)
        if not data:
            return jsonify({"error": "Недействительный или просроченный токен", "code": "invalid_token"}), 401
        try:
            uid = int(data["sub"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Недействительный токен", "code": "invalid_token"}), 401

        user = get_user_by_id(uid)
        if user is None:
            return jsonify({"error": "Пользователь не найден", "code": "not_found"}), 401
        if (user.get("role") or "").lower() != "coach":
            return jsonify({"error": "Доступно только тренеру", "code": "forbidden_role"}), 403

        return f(user_id=uid, *args, **kwargs)

    return wrapped


def require_user_json(f):
    """JWT обязателен; роль sportsman или coach."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        from user_registration.storage import get_user_by_id

        raw = bearer_token()
        if not raw:
            return jsonify({"error": "Нужен заголовок Authorization: Bearer <token>", "code": "unauthorized"}), 401
        data = decode_access_token(raw)
        if not data:
            return jsonify({"error": "Недействительный или просроченный токен", "code": "invalid_token"}), 401
        try:
            uid = int(data["sub"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Недействительный токен", "code": "invalid_token"}), 401

        user = get_user_by_id(uid)
        if user is None:
            return jsonify({"error": "Пользователь не найден", "code": "not_found"}), 401
        role = (user.get("role") or "").lower()
        if role not in ("sportsman", "coach"):
            return jsonify({"error": "Недопустимая роль", "code": "forbidden_role"}), 403

        return f(user_id=uid, *args, **kwargs)

    return wrapped
