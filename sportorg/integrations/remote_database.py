import os

from user_registration.registration import login_user as _login_user
from user_registration.registration import register_user as _register_user
from user_registration.storage import get_all_users, init_db


class RemoteDatabase:
    def __init__(self):
        self.connection_params = {
            "host": os.getenv("SPORTORG_DB_HOST", "192.168.1.80"),
            "port": int(os.getenv("SPORTORG_DB_PORT", "5500")),
            "database": os.getenv("SPORTORG_DB_NAME", "postgres"),
            "user": os.getenv("SPORTORG_DB_USER", "postgres"),
            "password": os.getenv("SPORTORG_DB_PASSWORD", "12345678"),
        }

        if not os.environ.get("DATABASE_URL"):
            os.environ.setdefault("SPORTORG_DB_HOST", self.connection_params["host"])
            os.environ.setdefault(
                "SPORTORG_DB_PORT", str(self.connection_params["port"])
            )
            os.environ.setdefault("SPORTORG_DB_NAME", self.connection_params["database"])
            os.environ.setdefault("SPORTORG_DB_USER", self.connection_params["user"])
            os.environ.setdefault(
                "SPORTORG_DB_PASSWORD", self.connection_params["password"]
            )

        self.init_database()

    def init_database(self) -> None:
        init_db()

    def register_user(
        self,
        email,
        password,
        last_name,
        first_name,
        role="sportsman",
        patronymic=None,
        birth_date=None,
        phone=None,
        city=None,
    ):
        result = _register_user(
            {
                "email": email or "",
                "password": password or "",
                "password2": password or "",
                "first_name": first_name or "",
                "last_name": last_name or "",
                "role": role or "sportsman",
                "patronymic": patronymic,
                "birth_date": birth_date,
                "phone": phone,
                "city": city,
            }
        )

        if result.get("success"):
            rid = result["user_id"]
            r = result.get("role", role)
            role_text = "тренер" if r == "coach" else "спортсмен"
            return True, f"{role_text} {last_name} {first_name} успешно зарегистрирован!", rid

        err = result.get("error", "Ошибка регистрации")
        if result.get("code") == "email_already_exists":
            return False, "Пользователь с таким email уже существует", None
        return False, err, None

    def login_user(self, email, password):
        return _login_user(email, password)

    def get_all_users(self):
        return get_all_users()
