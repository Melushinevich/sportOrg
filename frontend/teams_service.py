"""Команды тренера: список и создание через /api/v1/coach/teams."""

from __future__ import annotations

from typing import Any

from .api_client import ApiError, SportOrgApi
from .session import session


def _api() -> SportOrgApi:
    return SportOrgApi()


def _require_token() -> str:
    token = session.access_token
    if not token:
        raise ApiError("Войдите в аккаунт тренера", code="unauthorized")
    return token


def criteria_texts(raw: list[Any] | None) -> list[str]:
    result: list[str] = []
    for item in raw or []:
        if isinstance(item, str):
            text = item.strip()
        elif isinstance(item, dict):
            text = (item.get("text") or "").strip()
        else:
            continue
        if text:
            result.append(text)
    return result


def load_sports_catalog(api: SportOrgApi | None = None) -> list[dict[str, Any]]:
    client = api or _api()
    data = client.list_sports_catalog(token=_require_token())
    return [
        {"sport_id": int(s["sport_id"]), "name": s.get("name") or ""}
        for s in (data.get("sports") or [])
        if s.get("sport_id") is not None
    ]


def load_skills_catalog(api: SportOrgApi | None = None) -> list[dict[str, Any]]:
    client = api or _api()
    data = client.list_skills_catalog(token=_require_token())
    return [
        {
            "skill_id": int(s["skill_id"]),
            "name": s.get("name") or "",
            "category": s.get("category"),
        }
        for s in (data.get("skills") or [])
        if s.get("skill_id") is not None
    ]


def load_coach_teams(api: SportOrgApi | None = None) -> list[dict[str, Any]]:
    client = api or _api()
    data = client.list_coach_teams(token=_require_token())
    teams = data.get("teams") or []
    return [
        {
            "team_id": int(t["team_id"]),
            "team": t.get("team") or "",
            "sport": t.get("sport") or "",
        }
        for t in teams
        if t.get("team_id") is not None
    ]


def create_coach_team(
    *,
    team: str,
    sport: str,
    criteria: list[str] | None = None,
    api: SportOrgApi | None = None,
) -> dict[str, Any]:
    client = api or _api()
    data = client.create_coach_team(
        token=_require_token(),
        sport=sport,
        team=team,
        criteria=criteria or [],
    )
    return {
        "team_id": int(data["team_id"]),
        "team": data.get("team") or team,
        "sport": data.get("sport") or sport,
        "criteria": criteria_texts(data.get("criteria")),
    }
