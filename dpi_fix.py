"""
Отключает HiDPI-масштабирование Qt, чтобы окно и элементы
всегда имели строго фиксированный размер в пикселях.
Должен быть импортирован ДО создания QApplication.
"""
import os

# Переменные окружения — должны быть установлены ДО импорта PyQt5
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
os.environ['QT_SCALE_FACTOR'] = '1'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
os.environ['QT_SCREEN_SCALE_FACTORS'] = '1'

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


def apply_dpi_fix(app: QApplication):
    """Вызвать сразу после создания QApplication"""
    # Отключаем автоматическое масштабирование
    app.setAttribute(Qt.AA_EnableHighDpiScaling, False)
    # Используем 96 DPI как базовое (стандарт Windows)
    app.setAttribute(Qt.AA_Use96Dpi, True)