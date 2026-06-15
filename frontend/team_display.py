"""Форматирование навыков в таблице состава (без Qt)."""

from __future__ import annotations


def format_skills_display(skills: list, ratings: dict) -> str:
    if not skills:
        return ""
    parts: list[str] = []
    for skill in skills:
        if skill in ratings:
            parts.append(f"{skill} ({ratings[skill]})")
        else:
            parts.append(str(skill))
    return ", ".join(parts)
