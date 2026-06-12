"""Встроенные шрифты: UrbanSlavic (заголовки) и Roboto (интерфейс)."""

from __future__ import annotations

from pathlib import Path

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication

_FONTS_DIR = Path(__file__).resolve().parent / "fonts"

FONT_FILES = (
    _FONTS_DIR / "UrbanSlavic.otf",
    _FONTS_DIR / "Roboto-Regular.ttf",
    _FONTS_DIR / "Roboto-Italic.ttf",
)

FONT_TITLE = "UrbanSlavic"
FONT_UI = "Roboto"

_loaded = False


def ensure_fonts_loaded() -> None:
    """Регистрирует .otf/.ttf из frontend/fonts/ в Qt (без установки в ОС)."""
    global _loaded, FONT_TITLE, FONT_UI
    if _loaded:
        return

    title_family: str | None = None
    ui_family: str | None = None

    for path in FONT_FILES:
        if not path.is_file():
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id < 0:
            continue
        for family in QFontDatabase.applicationFontFamilies(font_id):
            low = family.lower()
            if "urban" in low or "slavic" in low:
                title_family = family
            elif "roboto" in low:
                ui_family = family

    if title_family:
        FONT_TITLE = title_family
    if ui_family:
        FONT_UI = ui_family

    _loaded = True


def css_family(family: str) -> str:
    return f'"{family}"'


def ui_font(
    size: int,
    weight: int = QFont.Normal,
    *,
    italic: bool = False,
) -> QFont:
    ensure_fonts_loaded()
    font = QFont(FONT_UI, size, weight)
    font.setItalic(italic)
    return font


def title_font(size: int) -> QFont:
    ensure_fonts_loaded()
    return QFont(FONT_TITLE, size)


def apply_app_fonts(app: QApplication) -> None:
    ensure_fonts_loaded()
    app.setFont(ui_font(14))
