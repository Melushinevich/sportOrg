"""Шрифты с fallback для macOS (без Roboto Flex / UrbanSlavic)."""

from PyQt5.QtGui import QFont

FONT_TITLE = "Arial"
FONT_UI = "Helvetica Neue"


def ui_font(size: int, weight: int = QFont.Normal, *, italic: bool = False) -> QFont:
    font = QFont(FONT_UI, size, weight)
    font.setItalic(italic)
    return font


def title_font(size: int) -> QFont:
    return QFont(FONT_TITLE, size, QFont.Bold)
