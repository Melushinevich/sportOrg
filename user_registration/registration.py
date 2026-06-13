import hashlib

from user_registration.birth_date import parse_iso_birth_date
from .storage import create_new_user, get_user_by_email

VALID_ROLES = frozenset({"sportsman", "coach"})


def validate_email(email: str):
    if "@" not in email:
        return False, "email должен содержать @"
    if len(email) < 5:
        return False, "email должен содержать больше 5 символов"
    return True, ""


def validate_password(password: str, password2: str):
    if password != password2:
        return False, "Пароли не совпадают, попробуйте снова"
    if len(password) < 6:
        return False, "Пароль слишком короткий"
    return True, ""


def validate_empty_str(first_name, last_name, email):
    """При регистрации нужен только email; ФИО заполняется в анкете."""
    _ = first_name, last_name
    if not email or not email.strip():
        return False, "Email обязателен"
    return True, ""


validate_required_fields = validate_empty_str


def validate_role(role: str) -> tuple[bool, str]:
    if not role or not str(role).strip():
        return False, "Укажите роль"
    r = str(role).strip().lower()
    if r not in VALID_ROLES:
        return False, "Роль должна быть sportsman или coach"
    return True, ""


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(request: dict) -> dict:

    valid, error = validate_required_fields(
        request.get("first_name", ""),
        request.get("last_name", ""),
        request.get("email", ""),
    )
    if not valid:
        return {"success": False, "error": error, "code": "invalid_input"}

    valid, error = validate_email(request["email"])
    if not valid:
        return {"success": False, "error": error, "code": "invalid_input"}

    valid, error = validate_password(request["password"], request["password2"])
    if not valid:
        return {"success": False, "error": error, "code": "invalid_input"}

    role = request.get("role", "sportsman")
    valid, error = validate_role(role)
    if not valid:
        return {"success": False, "error": error, "code": "invalid_input"}

    existing_user = get_user_by_email(request["email"])
    if existing_user is not None:
        return {
            "success": False,
            "error": "Email уже зарегистрирован",
            "code": "email_already_exists",
        }

    password_hash = hash_password(request["password"])

    first_name = (request.get("first_name") or "").strip() or None
    last_name = (request.get("last_name") or "").strip() or None

    birth_date = None
    raw_birth = request.get("birth_date")
    if raw_birth not in (None, ""):
        try:
            birth_date = parse_iso_birth_date(raw_birth)
        except ValueError as exc:
            return {"success": False, "error": str(exc), "code": "invalid_birth_date"}

    user_data = {
        "email": request["email"],
        "password_hash": password_hash,
        "role": str(role).strip().lower(),
        "first_name": first_name,
        "last_name": last_name,
        "patronymic": request.get("patronymic") or None,
        "birth_date": birth_date,
        "phone": request.get("phone") or None,
        "city": request.get("city") or None,
    }

    try:
        user_id = create_new_user(user_data)
    except Exception as exc:  # noqa: BLE001 — пробрасываем как ответ API
        return {
            "success": False,
            "error": str(exc),
            "code": "storage_error",
        }

    return {
        "success": True,
        "user_id": user_id,
        "email": request["email"],
        "role": user_data["role"],
    }


def login_user(email: str, password: str):
    """
    Проверка email + пароля. Совместимо с прежним RemoteDatabase.login_user:
    (True, dict_пользователя) или (False, сообщение).
    Поле password_hash в словаре не возвращается.
    """
    if not email or not password:
        return False, "Неверный email или пароль"

    row = get_user_by_email(email.strip())
    if row is None:
        return False, "Неверный email или пароль"

    if row.get("password_hash") != hash_password(password):
        return False, "Неверный email или пароль"

    safe = {k: v for k, v in row.items() if k != "password_hash"}
    return True, safe
