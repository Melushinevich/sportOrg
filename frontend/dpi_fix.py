"""
Масштаб Qt и размер окна приложения.

Соотношение сторон 4:3. Окно можно развернуть на весь экран, но не сжать ниже минимума.
Импортировать env-настройки ДО создания QApplication (см. run_frontend.py / main_app.py).
"""
from __future__ import annotations

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget

# Переменные окружения — до импорта PyQt5 в точках входа
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "0")
os.environ.setdefault("QT_SCALE_FACTOR", "1")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "0")
os.environ.setdefault("QT_SCREEN_SCALE_FACTORS", "1")

ASPECT_WIDTH = 4
ASPECT_HEIGHT = 3

# 1320×990 — 4:3; ширины хватает на кнопки ролей регистрации (381+153+381 + отступы).
MIN_WINDOW_WIDTH = 1320
MIN_WINDOW_HEIGHT = MIN_WINDOW_WIDTH * ASPECT_HEIGHT // ASPECT_WIDTH

DEFAULT_WINDOW_WIDTH = MIN_WINDOW_WIDTH
DEFAULT_WINDOW_HEIGHT = MIN_WINDOW_HEIGHT


def apply_dpi_fix(app: QApplication) -> None:
    """Вызвать сразу после создания QApplication."""
    _ = app


def setup_main_window(window: QWidget) -> None:
    """Главное окно приложения: стандартный размер + ограничение сжатия."""
    window.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    window.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    window.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
    window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


def setup_screen_widget(widget: QWidget) -> None:
    """Экран внутри QStackedWidget: заполняет доступное пространство."""
    widget.setMinimumSize(0, 0)
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    if isinstance(widget, QMainWindow):
        central = widget.centralWidget()
        if central is not None:
            central.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


def make_expanding(widget: QWidget) -> QWidget:
    """Виджет растягивается в layout (обычно таблица / список)."""
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    return widget
