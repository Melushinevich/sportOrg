"""HTTP-клиент для SportOrg API."""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    _env = Path(__file__).resolve().parents[1] / ".env"
    if _env.is_file():
        load_dotenv(_env, override=True)
except ImportError:
    pass

ROLE_UI_TO_API = {
    "СПОРТСМЕН": "sportsman",
    "ТРЕНЕР": "coach",
}

ROLE_API_TO_UI = {
    "sportsman": "СПОРТСМЕН",
    "coach": "ТРЕНЕР",
}


@dataclass
class ApiError(Exception):
    message: str
    code: str = "unknown"
    status: int = 0

    def __str__(self) -> str:
        return self.message


class SportOrgApi:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (
            base_url or os.environ.get("SPORTORG_API_URL") or "http://127.0.0.1:5000"
        ).rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> tuple[int, dict[str, Any]]:
        url = f"{self.base_url}{path}"
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
                payload = json.loads(raw) if raw else {}
                return resp.status, payload
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                payload = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                payload = {"error": raw or exc.reason}
            message = payload.get("error") or exc.reason or "Ошибка сервера"
            code = payload.get("code", "http_error")
            raise ApiError(message, code=code, status=exc.code) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise ApiError(
                    "Сервер API не отвечает (таймаут). Запустите: flask --app app run "
                    "(на Mac, если порт 5000 занят: flask --app app run --port 5001)",
                    code="timeout",
                ) from exc
            raise ApiError(
                "Не удалось подключиться к API. Запустите сервер: flask --app app run",
                code="connection_error",
            ) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise ApiError(
                "Сервер API не отвечает (таймаут). Проверьте, что Flask запущен, "
                "и SPORTORG_API_URL в .env указывает на правильный порт.",
                code="timeout",
            ) from exc

    def health(self) -> dict[str, Any]:
        _, data = self._request("GET", "/api/v1/health")
        return data

    def register(
        self,
        *,
        email: str,
        password: str,
        password2: str,
        role_ui: str,
        first_name: str = "Пользователь",
        last_name: str = "Новый",
    ) -> dict[str, Any]:
        role = ROLE_UI_TO_API.get(role_ui)
        if not role:
            raise ApiError("Неизвестная роль", code="invalid_input")

        status, data = self._request(
            "POST",
            "/api/v1/register",
            body={
                "email": email.strip(),
                "password": password,
                "password2": password2,
                "role": role,
                "first_name": first_name.strip() or "Пользователь",
                "last_name": last_name.strip() or "Новый",
            },
        )
        if status != 201:
            raise ApiError(
                data.get("error", "Ошибка регистрации"),
                code=data.get("code", "unknown"),
                status=status,
            )
        return data

    def login(self, *, email: str, password: str) -> dict[str, Any]:
        status, data = self._request(
            "POST",
            "/api/v1/login",
            body={"email": email.strip(), "password": password},
        )
        if status != 200:
            raise ApiError(
                data.get("error", "Неверная почта или пароль"),
                code=data.get("code", "unauthorized"),
                status=status,
            )
        return data
