"""Переходы между экранами без «пустого» главного окна."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget

T = TypeVar("T", bound=QMainWindow)


def _root_stack(widget: QWidget) -> QStackedWidget | None:
    root = widget.window()
    return root if isinstance(root, QStackedWidget) else None


def open_screen(from_widget: QWidget, factory: Callable[[], T]) -> T:
    """
    Открыть полноэкранное окно.
    Если вызов из MainApplication (QStackedWidget), не скрываем текущую
    страницу стека — иначе пользователь видит пустое окно.
    """
    window = factory()
    if _root_stack(from_widget) is not None:
        window.show()
        return window

    from_widget.hide()
    window.show()
    return window
