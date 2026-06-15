"""Экспорт итогового состава команды в PDF."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

_FONT_NAME = "Inter"
_FONT_REGISTERED = False


def _ensure_font() -> str:
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return _FONT_NAME
    font_path = Path(__file__).resolve().parent / "fonts" / "Inter-Regular.ttf"
    if not font_path.is_file():
        raise FileNotFoundError(f"Шрифт не найден: {font_path}")
    pdfmetrics.registerFont(TTFont(_FONT_NAME, str(font_path)))
    _FONT_REGISTERED = True
    return _FONT_NAME


def default_pdf_filename(team_name: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", (team_name or "команда").strip())
    safe = re.sub(r"\s+", " ", safe) or "команда"
    return f"Итог_{safe}_{date.today().isoformat()}.pdf"


def export_final_team_pdf(
    path: str | Path,
    *,
    team_name: str,
    rows: list[dict[str, Any]],
) -> Path:
    """Сохраняет таблицу состава в PDF. rows: name, percent, notes."""
    output = Path(path)
    if output.suffix.lower() != ".pdf":
        output = output.with_suffix(".pdf")

    font = _ensure_font()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TeamTitle",
        parent=styles["Heading1"],
        fontName=font,
        fontSize=16,
        leading=20,
        spaceAfter=8,
    )
    meta_style = ParagraphStyle(
        "TeamMeta",
        parent=styles["Normal"],
        fontName=font,
        fontSize=10,
        textColor=colors.HexColor("#444444"),
        spaceAfter=12,
    )
    cell_style = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontName=font,
        fontSize=10,
        leading=12,
    )

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    story = [
        Paragraph("SPORTORG", title_style),
        Paragraph(f"Итоговый состав — {team_name or 'Команда'}", title_style),
        Paragraph(f"Дата формирования: {date.today().strftime('%d.%m.%Y')}", meta_style),
        Spacer(1, 4 * mm),
    ]

    table_data = [
        [
            Paragraph("<b>ФИО</b>", cell_style),
            Paragraph("<b>%-усп.</b>", cell_style),
            Paragraph("<b>Заметки</b>", cell_style),
        ]
    ]
    for row in rows:
        table_data.append(
            [
                Paragraph(_escape(row.get("name") or ""), cell_style),
                Paragraph(_escape(str(row.get("percent") or "")), cell_style),
                Paragraph(_escape(row.get("notes") or ""), cell_style),
            ]
        )

    table = Table(table_data, colWidths=[62 * mm, 24 * mm, 82 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C8C8C8")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#6C769F")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    return output


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
