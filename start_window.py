import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

# Импортируем SupportButton из registr_window
from registr_window import SupportButton


class StartWindow(QMainWindow):
    # Сигнал для перехода в окно регистрации
    go_to_registration = pyqtSignal()
    # Сигнал для перехода в окно входа (если понадобится)
    go_to_login = pyqtSignal()

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
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(25)

        # Заголовок SPORTORG
        title_label = QLabel("SPORTORG")
        title_font = QFont("UrbanSlavic", 120)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: black; margin-top: 50px;")
        main_layout.addWidget(title_label)

        # Отступ
        main_layout.addSpacing(80)

        # Приветственный текст
        welcome_label = QLabel(
            "Привет! Я - твой виртуальный помощник по подбору команды\n"
            "Для продолжения зарегистрируйтесь или войдите в аккаунт"
        )
        welcome_font = QFont("Roboto Flex", 26)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: black;")
        main_layout.addWidget(welcome_label)

        # Отступ
        main_layout.addSpacing(100)

        # Горизонтальный layout для кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(100)
        buttons_layout.setAlignment(Qt.AlignCenter)

        # Кнопка РЕГИСТРАЦИЯ
        self.register_button = QPushButton("РЕГИСТРАЦИЯ")
        self.register_button.setFixedSize(400, 100)
        self.register_button.setFont(QFont("Roboto Flex", 32))
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                color: white;
                border: 2px solid black;
                border-radius: 50px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D6754B;
            }
            QPushButton:pressed {
                background-color: #C0653F;
            }
        """)
        self.register_button.clicked.connect(self.on_register_clicked)

        # Кнопка ВХОД
        self.login_button = QPushButton("ВХОД")
        self.login_button.setFixedSize(400, 100)
        self.login_button.setFont(QFont("Roboto Flex", 32))
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2D3142;
                color: white;
                border: 2px solid black;
                border-radius: 50px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #40465E;
            }
            QPushButton:pressed {
                background-color: #1D212F;
            }
        """)
        self.login_button.clicked.connect(self.on_login_clicked)

        buttons_layout.addWidget(self.register_button)
        buttons_layout.addWidget(self.login_button)

        # Добавляем layout с кнопками в основной
        main_layout.addLayout(buttons_layout)

        # Добавляем растяжку
        main_layout.addStretch()

        # Нижняя панель с копирайтом и кнопкой поддержки
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)

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

    def on_register_clicked(self):
        """Обработчик нажатия на кнопку регистрации"""
        self.go_to_registration.emit()

    def on_login_clicked(self):
        """Обработчик нажатия на кнопку входа"""
        self.go_to_login.emit()


def main():
    app = QApplication(sys.argv)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = StartWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()