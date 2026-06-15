"""Форматирование навыков заявки для таблицы и tooltip (без Qt)."""

from __future__ import annotations


def format_application_skills(skills: list) -> tuple[str, str]:
    """Имена для колонки и HTML для tooltip (самооценки из sportsman_skills)."""
    names: list[str] = []
    tooltip_lines: list[str] = []
    for item in skills or []:
        if isinstance(item, dict):
            name = (item.get("name") or "").strip()
            if not name:
                continue
            names.append(name)
            rating = item.get("rating")
            if rating is not None:
                tooltip_lines.append(f"• {name} — {rating}/10")
            else:
                tooltip_lines.append(f"• {name} — без оценки")
        elif isinstance(item, str) and item.strip():
            names.append(item.strip())
            tooltip_lines.append(f"• {item.strip()}")
    display = ", ".join(names)
    tooltip = "<br>".join(tooltip_lines) if tooltip_lines else "—"
    return display, tooltip
