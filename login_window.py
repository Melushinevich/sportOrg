import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

from registr_window import CustomLineEdit, SupportButton
from sportOrg import dpi_fix


class LoginWindow(QMainWindow):
    # Сигнал для успешного входа
    login_success = pyqtSignal(str, str)  # (email, role)
    # Сигнал для возврата на стартовое окно
    go_to_start = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SPORTORG - Вход")
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

        # Подзаголовок "АВТОРИЗАЦИЯ"
        subtitle_label = QLabel("АВТОРИЗАЦИЯ")
        subtitle_font = QFont("Roboto Flex", 40)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: black;")
        main_layout.addWidget(subtitle_label)

        # Отступ
        main_layout.addSpacing(40)

        # Поле ПОЧТА
        self.email_input = CustomLineEdit("ПОЧТА", is_password=False)
        self.email_input.setFont(QFont("Roboto Flex", 128, QFont.Thin))
        main_layout.addWidget(self.email_input)

        # Поле ПАРОЛЬ
        self.password_input = CustomLineEdit("ПАРОЛЬ", is_password=True)
        self.password_input.setFont(QFont("Roboto Flex", 128, QFont.Thin))
        main_layout.addWidget(self.password_input)

        # Добавляем растяжку
        main_layout.addStretch()

        # Кнопка ВОЙТИ
        self.login_button = QPushButton("ВОЙТИ")
        self.login_button.setMinimumHeight(91)
        self.login_button.setFont(QFont("Roboto Flex", 14))
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
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
                background-color: #1D212F;
            }
        """)
        self.login_button.clicked.connect(self.on_login)
        main_layout.addWidget(self.login_button)

        # Кнопка "Нет аккаунта? Зарегистрироваться"
        register_hint_layout = QHBoxLayout()
        register_hint_layout.setAlignment(Qt.AlignCenter)

        self.register_hint_button = QPushButton("Нет аккаунта? Зарегистрироваться")
        self.register_hint_button.setFont(QFont("Roboto Flex", 16))
        self.register_hint_button.setCursor(Qt.PointingHandCursor)
        self.register_hint_button.setStyleSheet("""
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
        self.register_hint_button.clicked.connect(self.on_register_clicked)
        register_hint_layout.addWidget(self.register_hint_button)

        main_layout.addLayout(register_hint_layout)

        # Нижняя панель с копирайтом и кнопкой поддержки
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        # Копирайт слева
        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(QFont("Roboto Flex", 10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        # Кнопка техподдержки
        self.support_button = SupportButton()

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.support_button)

        main_layout.addLayout(bottom_layout)

    def on_login(self):
        """Обработка нажатия на кнопку ВОЙТИ"""
        email = self.email_input.get_real_text()
        password = self.password_input.get_real_text()

        errors = []
        if not email or email == "ПОЧТА":
            errors.append("Введите почту")
        elif '@' not in email:
            errors.append("Введите корректную почту")

        if not password or password == "ПАРОЛЬ":
            errors.append("Введите пароль")
        elif len(password) < 4:
            errors.append("Пароль должен содержать минимум 4 символа")

        if errors:
            self.show_error_message("\n".join(errors))
        else:
            # Здесь будет реальная проверка credentials в базе данных
            # Пока сделаем заглушку - проверяем по коду
            self.authenticate_user(email, password)

    def authenticate_user(self, email, password):
        """Аутентификация пользователя (заглушка - потом подключим БД)"""
        # TODO: Заменить на реальную проверку в базе данных

        # Для теста: admin@test.com / 1234 - спортсмен
        if email == "admin@test.com" and password == "1234":
            self.show_success_message("Добро пожаловать!", "СПОРТСМЕН")
            self.login_success.emit(email, "СПОРТСМЕН")
        # Для теста: trainer@test.com / 1234 - тренер
        elif email == "trainer@test.com" and password == "1234":
            self.show_success_message("Добро пожаловать!", "ТРЕНЕР")
            self.login_success.emit(email, "ТРЕНЕР")
        else:
            self.show_error_message("Неверная почта или пароль")

    def show_error_message(self, message):
        """Показать сообщение об ошибке"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Ошибка входа")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_success_message(self, message, role):
        """Показать сообщение об успешном входе"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Успешный вход")
        msg_box.setText(f"{message}\nРоль: {role}")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def on_register_clicked(self):
        """Переход на окно регистрации"""
        self.go_to_start.emit()

    def clear_fields(self):
        """Очистить поля ввода"""
        self.email_input.setText("ПОЧТА")
        self.email_input.is_placeholder_active = True
        self.password_input.setText("ПАРОЛЬ")
        self.password_input.is_placeholder_active = True
        self.password_input.setEchoMode(QLineEdit.Normal)


def main():
    app = QApplication(sys.argv)
    dpi_fix.apply_dpi_fix(app)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()