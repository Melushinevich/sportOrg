from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication
)
from PyQt5.QtCore import Qt, QSize, QEvent
import os

from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

from .assets import asset_path
from .fonts import FONT_UI, title_font, ui_font

MENU_CONFIGS = {
    'trainer': {
        'burger_color': '#6C769F',
        'burger_hover': '#5A6385',
        'items': [
            ('Главная', 'home'),
            ('Отклики спортсменов', 'responses'),
            ('Профиль', 'profile'),
            ('Справка', 'help'),
        ],
    },
    'athlete': {
        'burger_color': '#EF8354',
        'burger_hover': '#D6754B',
        'items': [
            ('Главная', 'home'),
            ('Доступные команды', 'available_teams'),
            ('Мои скиллы', 'my_skills'),
            ('Профиль', 'profile'),
            ('Справка', 'help'),
        ],
    },
}


class BurgerMenu(QFrame):
    def __init__(self, parent=None, user_type='trainer', callbacks=None):
        super().__init__(parent)
        self.user_type = user_type
        self.callbacks = callbacks or {}
        self.config = MENU_CONFIGS.get(user_type, MENU_CONFIGS['trainer'])

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#F5F5F5"))
        self.setPalette(palette)

        self.setup_ui()
        self.hide()

    def setup_ui(self):
        self.setFixedSize(420, 900)

        self.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 15px;
            }
            QLabel {
                background: transparent;
            }
            QPushButton {
                background: transparent;
                border: none;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(0)

        # Шапка
        header_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(title_font(60))
        title_label.setStyleSheet("color: black; background: transparent;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Разделитель
        separator = QFrame()
        separator.setFixedHeight(3)
        burger_color = self.config['burger_color']
        separator.setStyleSheet(f"background-color: {burger_color};")
        main_layout.addWidget(separator)

        main_layout.addSpacing(30)

        # Пункты меню
        self.menu_buttons = []
        for label, action in self.config['items']:
            button = QPushButton(label)
            font = ui_font(22)
            font.setItalic(True)
            button.setFont(font)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: black;
                    border: none;
                    text-align: left;
                    padding: 10px;
                }
                QPushButton:hover {
                    color: #6C769F;
                    background: transparent;
                }
            """)

            if action == 'help':
                button.clicked.connect(self._make_help_handler())
            else:
                callback = self.callbacks.get(action)
                if callback:
                    button.clicked.connect(self._make_handler(callback))

            self.menu_buttons.append(button)
            main_layout.addWidget(button)

        main_layout.addStretch()

        # Кнопка поддержки — ИКОНКА ПО ЦЕНТРУ через QLabel + QPixmap
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addSpacing(15)

        self.support_button = QPushButton()
        self.support_button.setFixedSize(65, 65)
        self.support_button.setCursor(Qt.PointingHandCursor)
        self.support_button.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                border-radius: 32px;
                border: none;
            }
            QPushButton:hover {
                background-color: #D6754B;
            }
        """)

        # Создаём layout для кнопки
        button_layout = QHBoxLayout(self.support_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignCenter)

        # Ищем файл иконки
        icon_path = None
        for name in ["free-icon-support-8016461.png", "support.png", "headphones.png"]:
            path = asset_path(name)
            if os.path.exists(path):
                icon_path = path
                break

        # Создаём QLabel с иконкой
        icon_label = QLabel()
        if icon_path:
            pixmap = QPixmap(icon_path)
            # Масштабируем иконку до 30x30
            pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            # Fallback на эмодзи
            icon_label.setText("🎧")
            icon_label.setFont(ui_font(28))
            icon_label.setStyleSheet("color: white;")

        button_layout.addWidget(icon_label)

        bottom_layout.addWidget(self.support_button)

        main_layout.addLayout(bottom_layout)

    def _make_handler(self, callback):
        def handler():
            self.hide()
            callback()

        return handler

    def _make_help_handler(self):
        def handler():
            self.hide()
            from .help_window import HelpWindow
            parent_window = self.parent()
            help_win = HelpWindow(user_type=self.user_type, parent=parent_window)
            help_win.show()

        return handler


def show_burger_menu(window, burger_button, user_type, callbacks):
    if not hasattr(window, 'burger_menu') or window.burger_menu is None:
        window.burger_menu = BurgerMenu(
            parent=window,
            user_type=user_type,
            callbacks=callbacks,
        )
        window.installEventFilter(window.burger_menu)
    else:
        window.burger_menu.callbacks = callbacks
        window.burger_menu.user_type = user_type
        window.burger_menu.config = MENU_CONFIGS.get(user_type, MENU_CONFIGS['trainer'])

        if window.burger_menu.isVisible():
            window.burger_menu.hide()
            return

    btn_pos = burger_button.pos()

    x = btn_pos.x() - 420 + 20
    y = btn_pos.y() + 60

    x = max(10, min(x, window.width() - 420 - 10))
    y = max(10, min(y, window.height() - 900 - 10))

    window.burger_menu.move(x, y)
    window.burger_menu.raise_()
    window.burger_menu.show()


def _outside_click_filter(menu_self, obj, event):
    if event.type() == QEvent.MouseButtonPress:
        pos = event.globalPos()
        if not menu_self.geometry().contains(menu_self.mapFromGlobal(pos)):
            menu_self.hide()
            return True
    return False


BurgerMenu.eventFilter = lambda self, obj, event: _outside_click_filter(self, obj, event)