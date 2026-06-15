"""Скиллы спортсмена: загрузка, сохранение, справочник."""

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


def _parse_skills(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": int(s["id"]),
            "name": s.get("name") or "",
            "rating": s.get("rating"),
        }
        for s in (data.get("skills") or [])
        if s.get("id") is not None
    ]


def _parse_catalog(data: dict[str, Any]) -> list[str]:
    names = [s.get("name") or "" for s in (data.get("catalog") or [])]
    return sorted({name for name in names if name})


def load_skills_page(
    api: SportOrgApi | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Скиллы спортсмена и справочник одним запросом GET /me/skills."""
    client = api or _api()
    data = client.get_my_skills(token=_require_token())
    skills = _parse_skills(data)
    catalog = _parse_catalog(data)
    if catalog:
        return skills, catalog

    try:
        catalog_data = client.list_athlete_skills_catalog(token=_require_token())
        catalog = _parse_catalog(catalog_data)
    except ApiError:
        catalog = sorted({s["name"] for s in skills if s.get("name")})
    return skills, catalog


def load_my_skills(api: SportOrgApi | None = None) -> list[dict[str, Any]]:
    skills, _catalog = load_skills_page(api=api)
    return skills


def has_filled_skills(skills: list[dict[str, Any]] | None) -> bool:
    """Хотя бы один навык с самооценкой."""
    return any(s.get("rating") is not None for s in (skills or []))


def save_my_skills(
    *,
    skills: list[dict[str, Any]],
    api: SportOrgApi | None = None,
) -> list[dict[str, Any]]:
    client = api or _api()
    payload = []
    for item in skills:
        name = (item.get("name") or item.get("skill") or "").strip()
        if not name:
            continue
        rating = item.get("rating")
        if rating in ("", "—", None):
            rating = None
        else:
            rating = int(rating)
        payload.append({"name": name, "rating": rating})

    data = client.save_my_skills(token=_require_token(), skills=payload)
    return _parse_skills(data)
