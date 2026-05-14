import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QRadioButton, QButtonGroup, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QMouseEvent, QIcon

from PyQt5.QtCore import pyqtSignal  # если еще не импортирован


class CustomLineEdit(QLineEdit):
    """Кастомное поле ввода с плейсхолдером по центру и радиусом скругления 40"""

    def __init__(self, placeholder_text="", is_password=False):
        super().__init__()
        self.placeholder_text = placeholder_text
        self.is_placeholder_active = True
        self.is_password = is_password

        # Устанавливаем текст-плейсхолдер
        self.setText(placeholder_text)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #D9D9D9;
                border: 2px solid black;
                border-radius: 40px;
                font-size: 40px;
                color: black;
            }
            QLineEdit:focus {
                border: 4px solid;
                border-radius: 40px;
            }
        """)
        self.setMinimumHeight(95)

        # Если это поле пароля, изначально не используем режим пароля (чтобы показать плейсхолдер)
        if self.is_password:
            self.setEchoMode(QLineEdit.Normal)

        # Подключаем события фокуса
        self.focusInEvent = self.on_focus_in
        self.focusOutEvent = self.on_focus_out

    def on_focus_in(self, event):
        if self.is_placeholder_active:
            self.clear()
            self.is_placeholder_active = False
            # При фокусе и если это поле пароля - включаем режим пароля
            if self.is_password:
                self.setEchoMode(QLineEdit.Password)
        super().focusInEvent(event)

    def on_focus_out(self, event):
        if not self.text():
            self.setText(self.placeholder_text)
            self.is_placeholder_active = True
            # Если это поле пароля и плейсхолдер активен - отключаем режим пароля
            if self.is_password:
                self.setEchoMode(QLineEdit.Normal)
        super().focusOutEvent(event)

    def get_real_text(self):
        """Возвращает реальный введенный текст (не плейсхолдер)"""
        if self.is_placeholder_active:
            return ""
        return self.text()


class CustomRadioButton(QPushButton):
    """Кастомная радио-кнопка без кружка, с радиусом скругления 40"""
    radio_clicked = pyqtSignal(str)

    def __init__(self, text, color="#FFA500"):  # Оранжевый по умолчанию
        super().__init__(text)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(381, 95)  # Фиксированный размер: ширина 381, высота 95
        self.default_color = color
        self.active_color = color  # Цвет когда кнопка выбрана
        self.inactive_color = "#D9D9D9"  # Серый когда не выбрана
        self.setFont(QFont("Roboto Flex", 14, QFont.Thin))
        self.update_style(False)
        self.clicked.connect(self.on_click)

    def update_style(self, checked):
        if checked:
            # Выбранное состояние - свой цвет (оранжевый/синий)
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.active_color};
                    border: 2px solid black;
                    border-radius: 40px;
                    color: white;
                    font-size: 40px;
                }}
                QPushButton:hover {{
                    background-color: {self.get_darker_color(self.active_color)};
                }}
            """)
        else:
            # Невыбранное состояние - серый
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.inactive_color};
                    border: 2px solid black;
                    border-radius: 40px;
                    color: black;
                    font-size: 40px;
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
        self.setIcon(QIcon("free-icon-support-8016461.png"))
        self.setIconSize(QSize(35, 35))
        self.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #EF8354;
            }
            QPushButton:pressed {
                background-color: #EF8354;
            }
        """)
        self.clicked.connect(self.on_click)

    def on_click(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Техподдержка")
        msg_box.setText(
            "Свяжитесь с нами:\n\n📧 Email: support@sportorg.ru\n📞 Телефон: +7 (999) 123-45-67\n💬 Telegram: @sportorg_support")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


class RegistrationWindow(QMainWindow):
    register_success = pyqtSignal(str, str, str)  # (role, email, password)
    go_to_start = pyqtSignal()  # Сигнал для возврата на стартовое окно

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SPORTORG")
        self.setFixedSize(1440, 1024)
        self.setup_ui()

    def setup_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной вертикальный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(200, 40, 200, 40)
        main_layout.setSpacing(20)

        # Заголовок SPORTORG
        title_label = QLabel("SPORTORG")
        title_font = QFont("UrbanSlavic", 128)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Подзаголовок "РЕГИСТРАЦИЯ"
        subtitle_label = QLabel("РЕГИСТРАЦИЯ")
        subtitle_font = QFont("Roboto Flex", 40)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: black;")
        main_layout.addWidget(subtitle_label)

        # Поле ПОЧТА
        self.email_input = CustomLineEdit("ПОЧТА", is_password=False)
        self.email_input.setFont(QFont("Roboto Flex", 128, QFont.Thin))
        main_layout.addWidget(self.email_input)

        # Поле ПАРОЛЬ
        self.password_input = CustomLineEdit("ПАРОЛЬ", is_password=True)
        self.password_input.setFont(QFont("Roboto Flex", 128, QFont.Thin))
        main_layout.addWidget(self.password_input)

        # Поле ПОДТВЕРЖДЕНИЕ ПАРОЛЯ
        self.confirm_password_input = CustomLineEdit("ПОДТВЕРДИТЕ ПАРОЛЬ", is_password=True)
        self.confirm_password_input.setFont(QFont("Roboto Flex", 128, QFont.Thin))
        main_layout.addWidget(self.confirm_password_input)

        # Блок выбора роли
        role_label = QLabel("ВЫБЕРИТЕ ВАШУ РОЛЬ")
        role_label.setFont(QFont("Roboto Flex", 40))
        role_label.setAlignment(Qt.AlignCenter)
        role_label.setStyleSheet("color: black; margin-top: 20px; margin-bottom: 5px;")
        main_layout.addWidget(role_label)

        # Горизонтальный layout для радио-кнопок
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(153)
        radio_layout.setAlignment(Qt.AlignCenter)

        self.role_sportsman = CustomRadioButton("СПОРТСМЕН", "#EF8354")
        self.role_trainer = CustomRadioButton("ТРЕНЕР", "#4F5D75")

        self.role_sportsman.radio_clicked.connect(lambda: self.on_role_selected("СПОРТСМЕН"))
        self.role_trainer.radio_clicked.connect(lambda: self.on_role_selected("ТРЕНЕР"))

        radio_layout.addWidget(self.role_sportsman)
        radio_layout.addWidget(self.role_trainer)

        main_layout.addLayout(radio_layout)

        # Добавляем растяжку
        main_layout.addStretch()

        # Кнопка ЗАРЕГИСТРИРОВАТЬСЯ
        self.register_button = QPushButton("ЗАРЕГИСТРИРОВАТЬСЯ")
        self.register_button.setMinimumHeight(91)
        self.register_button.setFont(QFont("Roboto Flex", 14))
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #2D3142;
                color: white;
                border: 2px solid black;
                border-radius: 40px;
                font-size: 40px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #40465E;
            }
            QPushButton:pressed {
                background-color: #2D3142;
            }
        """)
        self.register_button.clicked.connect(self.on_register)
        main_layout.addWidget(self.register_button)

        login_hint_layout = QHBoxLayout()
        login_hint_layout.setAlignment(Qt.AlignCenter)

        self.login_hint_button = QPushButton("Уже есть аккаунт? Войти")
        self.login_hint_button.setFont(QFont("Roboto Flex", 16))
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
        login_hint_layout.addWidget(self.login_hint_button)

        main_layout.addLayout(login_hint_layout)

        # Горизонтальный layout для нижней панели (инфо + кнопка поддержки)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Копирайт слева (растягивается, чтобы кнопка ушла вправо)
        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(QFont("Roboto Flex", 10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        # Кнопка техподдержки справа
        self.support_button = SupportButton()

        # Добавляем элементы в нижний layout
        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()  # Растяжка между копирайтом и кнопкой
        bottom_layout.addWidget(self.support_button)

        main_layout.addLayout(bottom_layout)

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
        if not email or email == "ПОЧТА":
            errors.append("Введите почту")
        elif '@' not in email:
            errors.append("Введите корректную почту")

        if not password or password == "ПАРОЛЬ":
            errors.append("Введите пароль")
        elif len(password) < 4:
            errors.append("Пароль должен содержать минимум 4 символа")

        if not confirm_password or confirm_password == "ПОДТВЕРДИТЕ ПАРОЛЬ":
            errors.append("Подтвердите пароль")
        elif password != confirm_password:
            errors.append("Пароли не совпадают")

        if not role:
            errors.append("Выберите вашу роль")

        if errors:
            self.show_error_message("\n".join(errors))
        else:
            self.show_success_message(f"Регистрация успешна!\nРоль: {role}\nПочта: {email}")

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Ошибка")
        msg_box.setText("Пожалуйста, исправьте следующие ошибки:")
        msg_box.setInformativeText(message)
        msg_box.setStyleSheet("color: black;")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_success_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Успех")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)

        # Ждем, пока пользователь нажмет OK
        msg_box.exec_()

        # Получаем данные перед очисткой
        email = self.email_input.get_real_text()
        password = self.password_input.get_real_text()
        role = self.get_selected_role()

        # Очищаем поля после успешной регистрации
        self.email_input.setText("ПОЧТА")
        self.email_input.is_placeholder_active = True
        self.password_input.setText("ПАРОЛЬ")
        self.password_input.is_placeholder_active = True
        self.password_input.setEchoMode(QLineEdit.Normal)
        self.confirm_password_input.setText("ПОДТВЕРДИТЕ ПАРОЛЬ")
        self.confirm_password_input.is_placeholder_active = True
        self.confirm_password_input.setEchoMode(QLineEdit.Normal)
        self.role_sportsman.setChecked(False)
        self.role_trainer.setChecked(False)

        # Отправляем сигнал с данными для перехода
        self.register_success.emit(role, email, password)


def main():
    app = QApplication(sys.argv)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = RegistrationWindow()
    window.show()


if __name__ == '__main__':
    main()