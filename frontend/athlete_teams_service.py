"""Команды спортсмена: мои команды, доступные команды, заявки."""

from __future__ import annotations

from typing import Any

from .api_client import ApiError, SportOrgApi
from .session import session


def _api() -> SportOrgApi:
    return SportOrgApi()


def _require_token() -> str:
    token = session.access_token
    if not token:
        raise ApiError("Войдите в аккаунт спортсмена", code="unauthorized")
    return token


def load_my_teams(api: SportOrgApi | None = None) -> list[dict[str, Any]]:
    client = api or _api()
    data = client.list_my_teams(token=_require_token())
    return [
        {
            "member_id": int(t["member_id"]),
            "team_id": int(t["team_id"]),
            "team": t.get("team") or "",
            "sport": t.get("sport") or "",
            "coach": t.get("coach") or "",
        }
        for t in (data.get("teams") or [])
        if t.get("team_id") is not None
    ]


def load_available_teams(
    *,
    sport: str | None = None,
    api: SportOrgApi | None = None,
) -> list[dict[str, Any]]:
    client = api or _api()
    data = client.list_available_teams(token=_require_token(), sport=sport)
    return [
        {
            "team_id": int(t["team_id"]),
            "team": t.get("team") or "",
            "sport": t.get("sport") or "",
            "coach": t.get("coach") or "—",
        }
        for t in (data.get("teams") or [])
        if t.get("team_id") is not None
    ]


def apply_to_team(*, team_id: int, api: SportOrgApi | None = None) -> dict[str, Any]:
    client = api or _api()
    return client.apply_to_team(token=_require_token(), team_id=team_id)
