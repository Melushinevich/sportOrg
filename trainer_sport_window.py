import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

from registr_window import SupportButton
from add_sport_critetia_window import AddSportCriteriaWindow


class TrainerSportsWindow(QMainWindow):
    sports_added = pyqtSignal(list)
    go_back = pyqtSignal()  # сигнал для возврата

    def __init__(self, trainer_name="", trainer_data=None):
        super().__init__()
        self.trainer_name = trainer_name
        self.trainer_data = trainer_data or {}
        self.sports_with_criteria = []
        self.setWindowTitle("SPORTORG - Виды спорта")
        self.setFixedSize(1440, 1024)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(25)

        # Верхняя панель
        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(QFont("UrbanSlavic", 96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        sports_label = QLabel("ВИДЫ")
        sports_label.setFont(QFont("UrbanSlavic", 96))
        sports_label.setStyleSheet("color: #6C769F;")
        top_layout.addWidget(sports_label)

        self.burger_button = QPushButton("")
        self.burger_button.setIcon(QIcon("burger.png"))
        self.burger_button.setIconSize(QSize(30, 30))
        self.burger_button.setFixedSize(55, 55)
        self.burger_button.setStyleSheet("""
            QPushButton{
                background:#6C769F;
                border-radius:27px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        top_layout.addWidget(self.burger_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(50)

        # Приветствие
        welcome_label = QLabel(f"Здравствуйте, {self.trainer_name}! \n Добавьте виды спорта, которые вы преподаете")
        welcome_font = QFont("Roboto Flex", 32)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #6C769F; margin-bottom: 10px;")
        main_layout.addWidget(welcome_label)

        # Заголовок списка
        list_title = QLabel("Ваши виды спорта и критерии оценки:")
        list_title.setFont(QFont("Roboto Flex", 20, QFont.Bold))
        list_title.setAlignment(Qt.AlignCenter)
        list_title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(list_title)

        # Список видов спорта
        self.sports_list_widget = QListWidget()
        self.sports_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #F5F5F5;
                border: 2px solid #6C769F;
                border-radius: 20px;
                font-size: 18px;
                font-family: 'Roboto Flex';
                padding: 15px;
                min-height: 300px;
                color: black;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #DDDDDD;
                color: black;
            }
        """)
        main_layout.addWidget(self.sports_list_widget)

        # Кнопка ДОБАВИТЬ ВИД
        self.add_sport_button = QPushButton("+ ДОБАВИТЬ ВИД")
        self.add_sport_button.setFixedSize(400, 65)
        self.add_sport_button.setFont(QFont("Roboto Flex", 20))
        self.add_sport_button.setCursor(Qt.PointingHandCursor)
        self.add_sport_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F;
                color: white;
                border: 2px solid black;
                border-radius: 40px;
                font-size: 22px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        self.add_sport_button.clicked.connect(self.on_add_sport)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_sport_button)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        main_layout.addStretch()

        # Нижняя панель
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(QFont("Roboto Flex", 10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        self.support_button = SupportButton()

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.support_button)

        main_layout.addLayout(bottom_layout)

    def add_sport_to_list(self, sport_name, criteria):
        """Добавить вид спорта в список"""
        criteria_text = " • ".join(criteria) if criteria else "Критерии не выбраны"
        item_text = f"🏆 {sport_name}\n📋 Критерии: {criteria_text}"

        item = QListWidgetItem(item_text)
        item.setFont(QFont("Roboto Flex", 16))
        item.setData(Qt.UserRole, {"sport": sport_name, "criteria": criteria})
        self.sports_list_widget.addItem(item)

    def on_add_sport(self):
        """Переход на окно добавления вида спорта"""
        existing_sport_names = [item['sport'] for item in self.sports_with_criteria]
        self.add_window = AddSportCriteriaWindow(existing_sport_names, self)
        self.add_window.sport_saved.connect(self.on_sport_saved)
        self.add_window.show()
        self.hide()  # скрываем текущее окно

    def on_sport_saved(self, sport, criteria):
        """Сохранение вида спорта с критериями и возврат"""
        self.sports_with_criteria.append({
            "sport": sport,
            "criteria": criteria
        })
        self.add_sport_to_list(sport, criteria)

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Успех")
        msg_box.setText(f"Вид спорта '{sport}' добавлен с {len(criteria)} критериями!")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

        # Возвращаемся к окну тренера
        self.show()

    def showEvent(self, event):
        """При показе окна обновляем список существующих видов спорта"""
        super().showEvent(event)
        # Если есть окно добавления, обновляем его existing_sports
        if hasattr(self, 'add_window') and self.add_window:
            existing_names = [item['sport'] for item in self.sports_with_criteria]
            self.add_window.update_existing_sports(existing_names)


def main():
    app = QApplication(sys.argv)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = TrainerSportsWindow(trainer_name="Иван Петров")
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()