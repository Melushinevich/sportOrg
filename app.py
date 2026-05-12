"""
Веб: форма регистрации + JSON API (/api/v1).

  export FLASK_APP=app.py
  flask run

Переменные: FLASK_SECRET_KEY, LOG_LEVEL, DISABLE_RATE_LIMIT=1, PUBLIC_APP_URL (для заглушки ссылки в логе).
"""

import logging
import os
import sys

from flask import Flask, flash, redirect, render_template, request, url_for

from flask_limiter.constants import ConfigVars

from api_routes import bp as api_bp
from extensions import limiter
from user_registration.registration import register_user
from user_registration.storage import init_db


def configure_logging() -> None:
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format=fmt, stream=sys.stderr)
    root.setLevel(level)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def create_app(testing: bool = False) -> Flask:
    configure_logging()
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")
    app.config["TESTING"] = testing
    disable_rl = os.environ.get("DISABLE_RATE_LIMIT", "").lower() in ("1", "true", "yes")
    app.config[ConfigVars.ENABLED] = not testing and not disable_rl

    limiter.init_app(app)
    app.register_blueprint(api_bp)

    @app.post("/register")
    @limiter.limit("30 per minute")
    def register_submit():
        init_db()
        form = request.form
        result = register_user(
            {
                "first_name": form.get("first_name", ""),
                "last_name": form.get("last_name", ""),
                "email": form.get("email", ""),
                "password": form.get("password", ""),
                "password2": form.get("password2", ""),
                "role": form.get("role") or "sportsman",
                "patronymic": form.get("patronymic") or None,
                "birth_date": form.get("birth_date") or None,
                "phone": form.get("phone") or None,
                "city": form.get("city") or None,
            }
        )
        if result.get("success"):
            flash(
                f"Регистрация прошла успешно. ID: {result['user_id']}, роль: {result['role']}.",
                "success",
            )
            return redirect(url_for("register_form"))
        flash(result.get("error", "Ошибка"), "error")
        return redirect(url_for("register_form"))

    @app.get("/")
    @app.get("/register")
    def register_form():
        init_db()
        return render_template("register.html")

    @app.after_request
    def log_request(response):
        app.logger.info(
            "%s %s -> %s",
            request.method,
            request.path,
            response.status_code,
        )
        return response

    return app


app = create_app()
