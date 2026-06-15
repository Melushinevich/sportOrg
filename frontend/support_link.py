"""Ссылка на техподдержку SPORTORG."""

from __future__ import annotations

SUPPORT_URL = "https://vk.ru/id1114617582"


def open_support_link(parent=None) -> bool:
    from PyQt5.QtCore import QUrl
    from PyQt5.QtGui import QDesktopServices

    opened = QDesktopServices.openUrl(QUrl(SUPPORT_URL))
    if not opened and parent is not None:
        from .ui_messages import show_warning

        show_warning(
            parent,
            "Техподдержка",
            "Не удалось открыть ссылку в браузере.\n\n"
            f"Откройте вручную:\n{SUPPORT_URL}",
        )
    return opened
