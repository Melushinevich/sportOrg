"""
HTTP API (JSON): регистрация, логин, скиллы спортсмена.

  export FLASK_APP=app:create_app
  flask run

Переменные: FLASK_SECRET_KEY, LOG_LEVEL, DISABLE_RATE_LIMIT, JWT_SECRET_KEY, PUBLIC_APP_URL.
PostgreSQL: SPORTORG_DB_HOST (по умолчанию 192.168.1.73), SPORTORG_DB_PORT (5500), SPORTORG_DB_NAME,
SPORTORG_DB_USER, SPORTORG_DB_PASSWORD — или DATABASE_URL.
"""

import logging
import os
import sys

from flask import Flask, jsonify, request

from flask_limiter.constants import ConfigVars

from sportorg.api.athlete_skills import me_bp
from sportorg.api.public import bp as api_bp
from sportorg.api.teams import bp as teams_bp
from sportorg.extensions import limiter


def configure_logging() -> None:
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format=fmt, stream=sys.stderr)
    root.setLevel(level)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def _ensure_postgres_env() -> None:
    """Параметры PostgreSQL по умолчанию (192.168.1.73:5500), если не заданы в окружении."""
    if os.environ.get("DATABASE_URL"):
        return
    os.environ.setdefault("SPORTORG_DB_HOST", "192.168.1.73")
    os.environ.setdefault("SPORTORG_DB_PORT", "5500")
    os.environ.setdefault("SPORTORG_DB_NAME", "postgres")
    os.environ.setdefault("SPORTORG_DB_USER", "postgres")
    os.environ.setdefault("SPORTORG_DB_PASSWORD", "12345678")


def create_app(testing: bool = False) -> Flask:
    configure_logging()
    _ensure_postgres_env()
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")
    app.config["TESTING"] = testing
    disable_rl = os.environ.get("DISABLE_RATE_LIMIT", "").lower() in ("1", "true", "yes")
    app.config[ConfigVars.ENABLED] = not testing and not disable_rl

    limiter.init_app(app)
    app.register_blueprint(api_bp)
    app.register_blueprint(me_bp)
    app.register_blueprint(teams_bp)

    @app.get("/favicon.ico")
    def favicon():
        return "", 204

    @app.get("/")
    def index():
        """Подсказка: бэкенд только JSON API, без HTML-форм."""
        return jsonify(
            {
                "service": "SportOrg API",
                "docs_hint": "Используйте /api/v1/... с Content-Type: application/json",
                "endpoints": {
                    "health": "GET /api/v1/health",
                    "register": "POST /api/v1/register",
                    "login": "POST /api/v1/login",
                    "skills": "GET|POST|PUT /api/v1/me/skills (Bearer, sportsman)",
                    "available_teams": "GET /api/v1/available-teams?sport=... (Bearer, sportsman)",
                    "apply": "POST /api/v1/teams/<team_id>/apply (Bearer, sportsman)",
                    "my_applications": "GET /api/v1/me/applications (Bearer, sportsman)",
                    "coach_teams": "GET|POST /api/v1/coach/teams (Bearer, coach)",
                    "coach_team_detail": "GET /api/v1/coach/teams/<id> (Bearer, coach)",
                    "coach_team_members": "POST|PUT|DELETE /api/v1/coach/teams/<id>/members (Bearer, coach)",
                    "coach_finalize_roster": "POST /api/v1/coach/teams/<id>/finalize (Bearer, coach)",
                    "coach_search_sportsmen": "GET /api/v1/coach/sportsmen?search=... (Bearer, coach)",
                },
            }
        )

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
