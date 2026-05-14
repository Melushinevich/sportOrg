import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

from registr_window import RegistrationWindow
from data_page_sportsmen import ProfileWindow as SportsmanProfileWindow
from data_page_trainer import ProfileWindow as TrainerProfileWindow


class MainApplication(QStackedWidget):
    def __init__(self):
        super().__init__()

        # Создаем все окна
        self.registration_window = RegistrationWindow()
        self.sportsman_window = SportsmanProfileWindow()
        self.trainer_window = TrainerProfileWindow()

        # Убираем стандартные заголовки у окон, так как они будут внутри QStackedWidget
        self.registration_window.setWindowFlags(Qt.Widget)
        self.sportsman_window.setWindowFlags(Qt.Widget)
        self.trainer_window.setWindowFlags(Qt.Widget)

        # Добавляем окна в стек
        self.addWidget(self.registration_window)  # индекс 0
        self.addWidget(self.sportsman_window)  # индекс 1
        self.addWidget(self.trainer_window)  # индекс 2

        # Подключаем сигналы для переключения окон
        self.registration_window.register_success.connect(self.on_register_success)

        # Показываем окно регистрации
        self.setCurrentWidget(self.registration_window)

    def on_register_success(self, role, email, password):
        """Обработка успешной регистрации"""
        if role == "СПОРТСМЕН":
            self.setCurrentWidget(self.sportsman_window)
            print(f"Переход на анкету спортсмена (email: {email})")
        elif role == "ТРЕНЕР":
            self.setCurrentWidget(self.trainer_window)
            print(f"Переход на анкету тренера (email: {email})")

    def go_to_registration(self):
        """Вернуться на регистрацию (можно добавить кнопку в профилях)"""
        self.setCurrentWidget(self.registration_window)


def main():
    app = QApplication(sys.argv)

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