import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QRadioButton, QButtonGroup, QSizePolicy,
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QMouseEvent, QIcon, QFontMetrics

from PyQt5.QtCore import pyqtSignal  # если еще не импортирован

from . import dpi_fix
from .fonts import apply_app_fonts
from .api_client import ROLE_API_TO_UI, ApiError, SportOrgApi
from .session import session
from .support_link import open_support_link
from .ui_messages import show_error, show_info
from .assets import asset_path
from .fonts import FONT_UI, title_font, ui_font
from .form_styles import PLACEHOLDER_QSS


class CustomLineEdit(QLineEdit):
    """Поле ввода с серым placeholder (исчезает при клике/вводе)."""

    def __init__(self, placeholder_text="", is_password=False, height=91, radius=40):
        super().__init__()
        self.is_password = is_password
        self.setAlignment(Qt.AlignCenter)
        self.setPlaceholderText(placeholder_text)
        self.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: #D9D9D9;
                border: 2px solid black;
                border-radius: {radius}px;
                padding: 0px 30px;
                color: black;
            }}
            QLineEdit:focus {{
                border: 2px solid black;
                border-radius: {radius}px;
            }}
            """
            + PLACEHOLDER_QSS
        )
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if is_password:
            self.setEchoMode(QLineEdit.Password)

    def get_real_text(self):
        return self.text().strip()


class CustomRadioButton(QPushButton):
    """Кастомная радио-кнопка без кружка, с радиусом скругления 40"""
    radio_clicked = pyqtSignal(str)

    def __init__(self, text, color="#FFA500", width=381, height=95, font_size=40, radius=40):
        super().__init__(text)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(width, height)
        self._font_size = font_size
        self._radius = radius
        self.default_color = color
        self.active_color = color  # Цвет когда кнопка выбрана
        self.inactive_color = "#D9D9D9"  # Серый когда не выбрана
        self.setFont(ui_font(14, QFont.Thin))
        self.update_style(False)
        self.clicked.connect(self.on_click)

    def update_style(self, checked):
        if checked:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.active_color};
                    border: 2px solid black;
                    border-radius: {self._radius}px;
                    color: white;
                    font-size: {self._font_size}px;
                }}
                QPushButton:hover {{
                    background-color: {self.get_darker_color(self.active_color)};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.inactive_color};
                    border: 2px solid black;
                    border-radius: {self._radius}px;
                    color: black;
                    font-size: {self._font_size}px;
                }}
                QPushButton:hover {{
                    background-color: #c0c0c0;
                }}
            """)

    def get_darker_color(self, color):
        """Возвращает более темный оттенок для эффекта наведения"""
        if color == "#EF8354":  # Оранжевый
            return "#D6754B"
        elif color == "#4F5D75":  # Синий
            return "#3E485B"
        return "#696969"

    def on_click(self):
        self.radio_clicked.emit(self.text())

    def setChecked(self, checked):
        super().setChecked(checked)
        self.update_style(checked)


class SupportButton(QPushButton):
    """Кнопка техподдержки в виде круга с иконкой наушников"""

    def __init__(self):
        super().__init__()
        self.setFixedSize(60, 60)
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(QIcon(asset_path("free-icon-support-8016461.png")))
        self.setIconSize(QSize(35, 35))
        self.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                border-radius: 30px;
                color: black;
            }
            QPushButton:hover {
                background-color: #EF8354;
                color: black;
            }
            QPushButton:pressed {
                background-color: #EF8354;
                color: black;
            }
        """)
        self.clicked.connect(self.on_click)

    def on_click(self):
        open_support_link(self)


class RegistrationWindow(QMainWindow):
    register_success = pyqtSignal(str, str, str)  # (role, email, password)
    go_to_start = pyqtSignal()  # Сигнал для возврата на стартовое окно

    FIELD_HEIGHT = 70
    FIELD_GAP = 12
    FIELD_RADIUS = 30
    ROLE_LABEL_HEIGHT = 36
    ROLE_GAP = 8
    RADIO_WIDTH = 381
    RADIO_HEIGHT = 68
    RADIO_GAP = 153
    RADIO_FONT_SIZE = 28
    RADIO_RADIUS = 30

    def __init__(self):
        super().__init__()
        self.api = SportOrgApi()
        self.setWindowTitle("SPORTORG")
        self.setup_ui()

    def setup_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной вертикальный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(200, 40, 200, 20)
        main_layout.setSpacing(16)

        # Заголовок SPORTORG
        title_label = QLabel("SPORTORG")
        title_label_font = title_font(72)
        title_label.setFont(title_label_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: black;")
        title_label.setFixedHeight(78)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(title_label)

        # Подзаголовок "РЕГИСТРАЦИЯ"
        subtitle_label = QLabel("РЕГИСТРАЦИЯ")
        subtitle_font = ui_font(40)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: black;")
        subtitle_label.setFixedHeight(44)
        subtitle_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(16)

        fields_box = QWidget()
        fields_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fields_box.setFixedHeight(self.FIELD_HEIGHT * 3 + self.FIELD_GAP * 2)
        fields_layout = QVBoxLayout(fields_box)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(self.FIELD_GAP)

        self.email_input = CustomLineEdit(
            "ПОЧТА", is_password=False, height=self.FIELD_HEIGHT, radius=self.FIELD_RADIUS
        )
        self.email_input.setFont(ui_font(24))
        fields_layout.addWidget(self.email_input)

        self.password_input = CustomLineEdit(
            "ПАРОЛЬ", is_password=True, height=self.FIELD_HEIGHT, radius=self.FIELD_RADIUS
        )
        self.password_input.setFont(ui_font(24))
        fields_layout.addWidget(self.password_input)

        self.confirm_password_input = CustomLineEdit(
            "ПОДТВЕРДИТЕ ПАРОЛЬ",
            is_password=True,
            height=self.FIELD_HEIGHT,
            radius=self.FIELD_RADIUS,
        )
        self.confirm_password_input.setFont(ui_font(24))
        fields_layout.addWidget(self.confirm_password_input)

        main_layout.addWidget(fields_box)

        role_box = QWidget()
        role_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        role_box.setFixedHeight(
            self.ROLE_LABEL_HEIGHT + self.ROLE_GAP + self.RADIO_HEIGHT
        )
        role_layout = QVBoxLayout(role_box)
        role_layout.setContentsMargins(0, 0, 0, 0)
        role_layout.setSpacing(self.ROLE_GAP)

        role_label = QLabel("ВЫБЕРИТЕ ВАШУ РОЛЬ")
        role_label.setFont(ui_font(28))
        role_label.setAlignment(Qt.AlignCenter)
        role_label.setStyleSheet("color: black;")
        role_label.setFixedHeight(self.ROLE_LABEL_HEIGHT)
        role_layout.addWidget(role_label)

        radio_row = QHBoxLayout()
        radio_row.setContentsMargins(0, 0, 0, 0)
        radio_row.setSpacing(self.RADIO_GAP)
        radio_row.setAlignment(Qt.AlignCenter)

        self.role_sportsman = CustomRadioButton(
            "СПОРТСМЕН",
            "#EF8354",
            width=self.RADIO_WIDTH,
            height=self.RADIO_HEIGHT,
            font_size=self.RADIO_FONT_SIZE,
            radius=self.RADIO_RADIUS,
        )
        self.role_trainer = CustomRadioButton(
            "ТРЕНЕР",
            "#4F5D75",
            width=self.RADIO_WIDTH,
            height=self.RADIO_HEIGHT,
            font_size=self.RADIO_FONT_SIZE,
            radius=self.RADIO_RADIUS,
        )

        self.role_sportsman.radio_clicked.connect(lambda: self.on_role_selected("СПОРТСМЕН"))
        self.role_trainer.radio_clicked.connect(lambda: self.on_role_selected("ТРЕНЕР"))

        radio_row.addWidget(self.role_sportsman)
        radio_row.addWidget(self.role_trainer)
        role_layout.addLayout(radio_row)

        main_layout.addWidget(role_box)

        main_layout.addSpacing(12)

        actions_box = QWidget()
        actions_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        actions_box.setFixedHeight(self.FIELD_HEIGHT + 10 + 34)
        actions_layout = QVBoxLayout(actions_box)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)

        self.register_button = QPushButton("ЗАРЕГИСТРИРОВАТЬСЯ")
        self.register_button.setFixedHeight(self.FIELD_HEIGHT)
        self.register_button.setFont(ui_font(14))
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #2D3142;
                color: white;
                border: 2px solid black;
                border-radius: 30px;
                font-size: 28px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #40465E;
            }
            QPushButton:pressed {
                background-color: #2D3142;
            }
        """)
        self.register_button.clicked.connect(self.on_register)
        actions_layout.addWidget(self.register_button)

        self.login_hint_button = QPushButton("Уже есть аккаунт? Войти")
        self.login_hint_button.setFixedHeight(34)
        self.login_hint_button.setFont(ui_font(16))
        self.login_hint_button.setCursor(Qt.PointingHandCursor)
        self.login_hint_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #EF8354;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.login_hint_button.clicked.connect(self.on_login_clicked)
        actions_layout.addWidget(self.login_hint_button)

        main_layout.addWidget(actions_box)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 6, 0, 0)

        # Копирайт слева (растягивается, чтобы кнопка ушла вправо)
        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(ui_font(10))
        info_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        info_label.setStyleSheet("color: gray;")

        # Кнопка техподдержки справа
        self.support_button = SupportButton()

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.support_button, 0, Qt.AlignTop)

        main_layout.addLayout(bottom_layout)

        main_layout.addStretch()

    def on_role_selected(self, role):
        """Обработка выбора роли"""
        if role == "СПОРТСМЕН":
            self.role_sportsman.setChecked(True)
            self.role_trainer.setChecked(False)
        else:
            self.role_sportsman.setChecked(False)
            self.role_trainer.setChecked(True)

    def get_selected_role(self):
        """Возвращает выбранную роль"""
        if self.role_sportsman.isChecked():
            return "СПОРТСМЕН"
        elif self.role_trainer.isChecked():
            return "ТРЕНЕР"
        return None

    def on_login_clicked(self):
        """Переход на окно входа"""
        self.go_to_start.emit()

    def on_register(self):
        email = self.email_input.get_real_text()
        password = self.password_input.get_real_text()
        confirm_password = self.confirm_password_input.get_real_text()

        role = self.get_selected_role()

        errors = []
        if not email:
            errors.append("Введите почту")
        elif '@' not in email:
            errors.append("Введите корректную почту")

        if not password:
            errors.append("Введите пароль")
        elif len(password) < 6:
            errors.append("Пароль должен содержать минимум 6 символов")

        if not confirm_password:
            errors.append("Подтвердите пароль")
        elif password != confirm_password:
            errors.append("Пароли не совпадают")

        if not role:
            errors.append("Выберите вашу роль")

        if errors:
            self.show_error_message("\n".join(errors))
            return

        self.register_button.setEnabled(False)
        try:
            result = self.api.register(
                email=email,
                password=password,
                password2=confirm_password,
                role_ui=role,
            )
        except ApiError as exc:
            self.show_error_message(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            self.show_error_message(f"Ошибка регистрации: {exc}")
            return
        finally:
            self.register_button.setEnabled(True)

        try:
            login_result = self.api.login(email=email, password=password)
        except ApiError as exc:
            self.show_error_message(
                f"Регистрация прошла, но автоматический вход не удался: {exc}"
            )
            return
        except Exception as exc:  # noqa: BLE001
            self.show_error_message(f"Регистрация прошла, но вход не удался: {exc}")
            return

        user = login_result.get("user") or {}
        role_api = (user.get("role") or result.get("role") or "").lower()
        role_ui = ROLE_API_TO_UI.get(role_api) or role
        session.user_id = int(user.get("id") or result.get("user_id") or 0) or None
        session.email = user.get("email") or email
        session.role_api = role_api
        session.role_ui = role_ui
        session.access_token = login_result.get("access_token")

        role_label = "ТРЕНЕР" if role_api == "coach" else "СПОРТСМЕН"
        self.show_success_message(
            f"Регистрация успешна!\nРоль: {role_label}\nПочта: {email}"
        )

    def show_error_message(self, message):
        show_error(
            self,
            "Ошибка",
            "Пожалуйста, исправьте следующие ошибки:",
            informative=message,
        )

    def show_success_message(self, message):
        show_info(self, "Успех", message)

        # Получаем данные перед очисткой
        email = self.email_input.get_real_text()
        password = self.password_input.get_real_text()
        role = self.get_selected_role()

        self.email_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.role_sportsman.setChecked(False)
        self.role_trainer.setChecked(False)

        # Отправляем сигнал с данными для перехода
        self.register_success.emit(role, email, password)


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)
    dpi_fix.apply_dpi_fix(app)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = RegistrationWindow()
    window.show()


if __name__ == '__main__':
    main()