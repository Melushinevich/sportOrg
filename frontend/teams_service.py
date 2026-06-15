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


def load_coach_applications(
    *,
    team_id: int | None = None,
    team_name: str | None = None,
    status: str = "pending",
    api: SportOrgApi | None = None,
) -> list[dict[str, Any]]:
    client = api or _api()
    data = client.list_coach_applications(
        token=_require_token(),
        team_id=team_id,
        team_name=team_name,
        status=status,
    )
    return [
        {
            "application_id": int(a["application_id"]),
            "team_id": int(a["team_id"]),
            "team": a.get("team") or "",
            "sport": a.get("sport") or "",
            "athlete_user_id": int(a["athlete_user_id"]),
            "full_name": a.get("full_name") or "",
            "email": a.get("email") or "",
            "phone": a.get("phone") or "",
            "skills": a.get("skills") or [],
            "status": a.get("status") or "",
        }
        for a in (data.get("applications") or [])
        if a.get("application_id") is not None
    ]


def accept_coach_application(
    *,
    application_id: int,
    api: SportOrgApi | None = None,
) -> dict[str, Any]:
    client = api or _api()
    data = client.accept_coach_application(
        token=_require_token(),
        application_id=application_id,
    )
    return {
        "member_id": int(data["member_id"]),
        "application_id": int(data["application_id"]),
        "team_id": int(data["team_id"]),
        "team": data.get("team") or "",
        "sport": data.get("sport") or "",
        "full_name": data.get("full_name") or "",
        "email": data.get("email") or "",
        "phone": data.get("phone") or "",
        "skills": data.get("skills") or [],
    }


def load_coach_team(
    *,
    team_id: int,
    api: SportOrgApi | None = None,
) -> dict[str, Any]:
    client = api or _api()
    data = client.get_coach_team(token=_require_token(), team_id=team_id)
    members: list[dict[str, Any]] = []
    for m in data.get("members") or []:
        if m.get("member_id") is None:
            continue
        qualities = m.get("qualities") or []
        skill_names = [q.get("name") or "" for q in qualities if q.get("name")]
        ratings = {
            q["name"]: int(q["rating"])
            for q in qualities
            if q.get("name") and q.get("rating") is not None
        }
        score = m.get("score")
        athlete_score = m.get("athlete_score")
        members.append(
            {
                "member_id": int(m["member_id"]),
                "athlete_user_id": m.get("athlete_user_id"),
                "name": m.get("full_name") or "",
                "skills": skill_names,
                "ratings": ratings,
                "qualities": qualities,
                "score": score,
                "athlete_score": athlete_score,
                "notes": m.get("notes") or "",
                "email": "",
                "phone": "",
            }
        )
    return {
        "team_id": int(data["team_id"]),
        "team": data.get("team") or "",
        "sport": data.get("sport") or "",
        "criteria": [
            {
                "criterion_id": int(c["criterion_id"]),
                "text": c.get("text") or "",
                "sort_order": int(c.get("sort_order") or 0),
            }
            for c in (data.get("criteria") or [])
            if c.get("criterion_id") is not None
        ],
        "members": members,
    }


def average_rating(ratings: dict[str, int] | None) -> float | None:
    if not ratings:
        return None
    return round(sum(ratings.values()) / len(ratings), 1)


def success_percent(
    *,
    score: float | None = None,
    ratings: dict[str, int] | None = None,
) -> float | None:
    """%-усп.: среднее по coach_assessments (изначально копия sportsman_skills)."""
    if score is not None:
        return score
    return average_rating(ratings)


def build_member_save_payload(
    *,
    member_id: int,
    notes: str,
    qualities: list[dict[str, Any]],
    ratings_by_name: dict[str, int] | None,
) -> dict[str, Any]:
    payload_qualities: list[dict[str, Any]] = []
    for quality in qualities:
        name = (quality.get("name") or "").strip()
        if not name:
            continue
        if name not in (ratings_by_name or {}):
            continue
        rating = (ratings_by_name or {}).get(name)
        if rating in ("", "—", None):
            continue
        entry: dict[str, Any] = {"name": name, "rating": int(rating)}
        skill_id = quality.get("skill_id")
        if skill_id is not None:
            entry["skill_id"] = int(skill_id)
        quality_id = quality.get("quality_id")
        if quality_id is not None:
            entry["quality_id"] = int(quality_id)
        payload_qualities.append(entry)
    return {
        "member_id": int(member_id),
        "notes": (notes or "").strip(),
        "qualities": payload_qualities,
    }


def save_team_members(
    *,
    team_id: int,
    members: list[dict[str, Any]],
    api: SportOrgApi | None = None,
) -> list[dict[str, Any]]:
    client = api or _api()
    data = client.save_coach_team_members(
        token=_require_token(),
        team_id=team_id,
        members=members,
    )
    saved: list[dict[str, Any]] = []
    for m in data.get("members") or []:
        if m.get("member_id") is None:
            continue
        qualities = m.get("qualities") or []
        ratings = {
            q["name"]: int(q["rating"])
            for q in qualities
            if q.get("name") and q.get("rating") is not None
        }
        saved.append(
            {
                "member_id": int(m["member_id"]),
                "name": m.get("full_name") or "",
                "ratings": ratings,
                "score": m.get("score"),
                "athlete_score": m.get("athlete_score"),
                "notes": m.get("notes") or "",
                "qualities": qualities,
            }
        )
    return saved


def remove_team_member(
    *,
    team_id: int,
    member_id: int,
    api: SportOrgApi | None = None,
) -> None:
    client = api or _api()
    client.remove_coach_team_member(
        token=_require_token(),
        team_id=team_id,
        member_id=member_id,
    )
