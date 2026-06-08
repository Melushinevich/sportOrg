import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

from sportOrg import dpi_fix
from start_window import StartWindow
from registr_window import RegistrationWindow
from login_window import LoginWindow
from data_page_sportsmen import ProfileWindow as SportsmanProfileWindow
from data_page_trainer import ProfileWindow as TrainerProfileWindow


class MainApplication(QStackedWidget):
    def __init__(self):
        super().__init__()

        # Создаем все окна
        self.start_window = StartWindow()
        self.registration_window = RegistrationWindow()
        self.login_window = LoginWindow()
        self.sportsman_window = SportsmanProfileWindow()
        self.trainer_window = TrainerProfileWindow()

        # Убираем стандартные заголовки у окон (для встраивания в QStackedWidget)
        self.start_window.setWindowFlags(Qt.Widget)
        self.registration_window.setWindowFlags(Qt.Widget)
        self.login_window.setWindowFlags(Qt.Widget)
        self.sportsman_window.setWindowFlags(Qt.Widget)
        self.trainer_window.setWindowFlags(Qt.Widget)

        # Добавляем окна в стек
        self.addWidget(self.start_window)  # индекс 0
        self.addWidget(self.registration_window)  # индекс 1
        self.addWidget(self.login_window)  # индекс 2
        self.addWidget(self.sportsman_window)  # индекс 3
        self.addWidget(self.trainer_window)  # индекс 4

        # Подключаем сигналы для переключения окон
        self.start_window.go_to_registration.connect(self.on_go_to_registration)
        self.start_window.go_to_login.connect(self.on_go_to_login)
        self.registration_window.register_success.connect(self.on_register_success)
        self.registration_window.go_to_start.connect(self.on_go_to_start)
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.go_to_start.connect(self.on_go_to_start)

        # Показываем стартовое окно
        self.setCurrentWidget(self.start_window)

    def on_go_to_registration(self):
        """Переход из стартового окна в окно регистрации"""
        self.setCurrentWidget(self.registration_window)
        print("Переход на окно регистрации")

    def on_go_to_login(self):
        """Переход из стартового окна в окно входа"""
        self.setCurrentWidget(self.login_window)
        self.login_window.clear_fields()
        print("Переход на окно входа")

    def on_go_to_start(self):
        """Возврат на стартовое окно"""
        self.setCurrentWidget(self.start_window)
        print("Возврат на стартовое окно")

    def on_register_success(self, role, email, password):
        """Переход из регистрации в анкету (спортсмен/тренер)"""
        if role == "СПОРТСМЕН":
            self.setCurrentWidget(self.sportsman_window)
            print(f"Переход на анкету спортсмена (email: {email})")
        elif role == "ТРЕНЕР":
            self.setCurrentWidget(self.trainer_window)
            print(f"Переход на анкету тренера (email: {email})")

    def on_login_success(self, email, role):
        """Переход после успешного входа"""
        if role == "СПОРТСМЕН":
            self.setCurrentWidget(self.sportsman_window)
            print(f"Успешный вход спортсмена: {email}")
        elif role == "ТРЕНЕР":
            self.setCurrentWidget(self.trainer_window)
            print(f"Успешный вход тренера: {email}")


def main():
    app = QApplication(sys.argv)

    dpi_fix.apply_dpi_fix(app)
    # Устанавливаем белый фон
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = MainApplication()
    window.setWindowTitle("SPORTORG")
    window.setFixedSize(1440, 1024)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()