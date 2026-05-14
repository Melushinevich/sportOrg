import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

from registr_window import SupportButton

# Доступные виды спорта
AVAILABLE_SPORTS = ["Футбол", "Баскетбол", "Волейбол", "Теннис", "Плавание",
                    "Легкая атлетика", "Хоккей", "Бокс", "Самбо", "Гимнастика"]

# Доступные критерии
AVAILABLE_CRITERIA = [
    "Скорость", "Выносливость", "Сила", "Техника", "Тактика",
    "Координация", "Гибкость", "Реакция", "Командная работа",
    "Лидерство", "Дисциплина", "Стрессоустойчивость", "Мотивация"
]


class AddSportCriteriaWindow(QMainWindow):
    sport_saved = pyqtSignal(str, list)

    def __init__(self, existing_sports=None, parent=None):
        super().__init__(parent)
        self.existing_sports = existing_sports or []
        self.selected_criteria = []
        self.setWindowTitle("SPORTORG - Добавление вида спорта")
        self.setFixedSize(1440, 1024)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(200, 60, 200, 60)
        main_layout.setSpacing(20)

        # Верхняя панель
        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(QFont("UrbanSlavic", 96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        add_label = QLabel("ДОБАВЛЕНИЕ")
        add_label.setFont(QFont("UrbanSlavic", 96))
        add_label.setStyleSheet("color: #6C769F;")
        top_layout.addWidget(add_label)

        # Кнопка назад
        self.back_button = QPushButton("←")
        self.back_button.setFixedSize(55, 55)
        self.back_button.setFont(QFont("Roboto Flex", 30))
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton{
                background:#6C769F;
                color: white;
                border-radius:27px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        self.back_button.clicked.connect(self.on_back)
        top_layout.addWidget(self.back_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(40)

        # Заголовок
        title = QLabel("Добавление вида спорта")
        title.setFont(QFont("Roboto Flex", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: black; margin-bottom: 20px;")
        main_layout.addWidget(title)

        # Выбор вида спорта
        sport_label = QLabel("Выберите вид спорта:")
        sport_label.setFont(QFont("Roboto Flex", 18, QFont.Bold))
        sport_label.setStyleSheet("color: black;")
        main_layout.addWidget(sport_label)

        self.sport_combo = QComboBox()
        self.sport_combo.addItems(AVAILABLE_SPORTS)
        self.sport_combo.setFont(QFont("Roboto Flex", 18))
        self.sport_combo.setStyleSheet("""
            QComboBox {
                background-color: #D9D9D9;
                border: 2px solid black;
                border-radius: 25px;
                padding: 8px;
                min-height: 45px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
                width: 35px;
            }
            QComboBox QAbstractItemView {
                font-size: 16px;
                color: black;
                background-color: white;
                selection-background-color: #6C769F;
                selection-color: white;
            }
        """)
        main_layout.addWidget(self.sport_combo)

        main_layout.addSpacing(15)

        # Выбор критериев
        criteria_label = QLabel("Выберите критерии оценки:")
        criteria_label.setFont(QFont("Roboto Flex", 18, QFont.Bold))
        criteria_label.setStyleSheet("color: black;")
        main_layout.addWidget(criteria_label)

        # Выпадающий список для добавления критериев
        criteria_add_layout = QHBoxLayout()
        criteria_add_layout.setSpacing(15)

        self.criteria_combo = QComboBox()
        self.criteria_combo.addItems(AVAILABLE_CRITERIA)
        self.criteria_combo.setFont(QFont("Roboto Flex", 16))
        self.criteria_combo.setStyleSheet("""
            QComboBox {
                background-color: #D9D9D9;
                border: 2px solid black;
                border-radius: 25px;
                padding: 8px;
                min-height: 45px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
                width: 35px;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
                color: black;
                background-color: white;
                selection-background-color: #6C769F;
                selection-color: white;
            }
        """)

        self.add_criteria_button = QPushButton("+ Добавить критерий")
        self.add_criteria_button.setFixedSize(180, 45)
        self.add_criteria_button.setFont(QFont("Roboto Flex", 15))
        self.add_criteria_button.setCursor(Qt.PointingHandCursor)
        self.add_criteria_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F;
                color: white;
                border: 2px solid black;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        self.add_criteria_button.clicked.connect(self.on_add_criteria)

        criteria_add_layout.addWidget(self.criteria_combo)
        criteria_add_layout.addWidget(self.add_criteria_button)
        main_layout.addLayout(criteria_add_layout)

        main_layout.addSpacing(10)

        # Список выбранных критериев
        selected_label = QLabel("Выбранные критерии:")
        selected_label.setFont(QFont("Roboto Flex", 16, QFont.Bold))
        selected_label.setStyleSheet("color: black;")
        main_layout.addWidget(selected_label)

        self.criteria_list_widget = QListWidget()
        self.criteria_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #F5F5F5;
                border: 2px solid #6C769F;
                border-radius: 15px;
                font-size: 16px;
                font-family: 'Roboto Flex';
                padding: 10px;
                min-height: 200px;
                max-height: 200px;
                color: black;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #DDDDDD;
                color: black;
            }
            QListWidget::item:selected {
                background-color: #6C769F;
                color: white;
            }
        """)
        main_layout.addWidget(self.criteria_list_widget)

        # Кнопка удаления критерия
        self.remove_criteria_button = QPushButton("- Удалить выбранный критерий")
        self.remove_criteria_button.setFixedSize(220, 45)
        self.remove_criteria_button.setFont(QFont("Roboto Flex", 15))
        self.remove_criteria_button.setCursor(Qt.PointingHandCursor)
        self.remove_criteria_button.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                color: white;
                border: 2px solid black;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: #D6754B;
            }
        """)
        self.remove_criteria_button.clicked.connect(self.on_remove_criteria)

        remove_layout = QHBoxLayout()
        remove_layout.addStretch()
        remove_layout.addWidget(self.remove_criteria_button)
        remove_layout.addStretch()
        main_layout.addLayout(remove_layout)

        main_layout.addStretch()

        # Кнопки Сохранить и Отмена
        save_buttons_layout = QHBoxLayout()
        save_buttons_layout.setSpacing(30)
        save_buttons_layout.setAlignment(Qt.AlignCenter)

        self.save_button = QPushButton("СОХРАНИТЬ")
        self.save_button.setFixedSize(250, 60)
        self.save_button.setFont(QFont("Roboto Flex", 18, QFont.Bold))
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2D3142;
                color: white;
                border: 2px solid black;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #40465E;
            }
        """)
        self.save_button.clicked.connect(self.on_save)

        self.cancel_button = QPushButton("ОТМЕНА")
        self.cancel_button.setFixedSize(250, 60)
        self.cancel_button.setFont(QFont("Roboto Flex", 18, QFont.Bold))
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9;
                color: black;
                border: 2px solid black;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #C0C0C0;
            }
        """)
        self.cancel_button.clicked.connect(self.on_back)

        save_buttons_layout.addWidget(self.save_button)
        save_buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(save_buttons_layout)

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

    def update_existing_sports(self, existing_sports):
        self.existing_sports = existing_sports

    def on_add_criteria(self):
        criteria = self.criteria_combo.currentText()
        if criteria not in self.selected_criteria:
            self.selected_criteria.append(criteria)
            item = QListWidgetItem(criteria)
            item.setTextAlignment(Qt.AlignCenter)
            self.criteria_list_widget.addItem(item)
        else:
            self.show_error(f"Критерий '{criteria}' уже добавлен!")

    def on_remove_criteria(self):
        current_item = self.criteria_list_widget.currentItem()
        if current_item:
            criteria = current_item.text()
            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить критерий '{criteria}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.selected_criteria.remove(criteria)
                row = self.criteria_list_widget.row(current_item)
                self.criteria_list_widget.takeItem(row)
        else:
            self.show_error("Пожалуйста, выберите критерий для удаления!")

    def on_save(self):
        sport = self.sport_combo.currentText()

        if sport in self.existing_sports:
            reply = QMessageBox.question(
                self,
                "Вид спорта уже добавлен",
                f"Вид спорта '{sport}' уже был добавлен ранее. Заменить?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        if not self.selected_criteria:
            reply = QMessageBox.question(
                self,
                "Нет критериев",
                "Вы не выбрали ни одного критерия. Продолжить?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        self.sport_saved.emit(sport, self.selected_criteria.copy())
        self.close()

    def on_back(self):
        self.close()

    def show_error(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Ошибка")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def closeEvent(self, event):
        if self.parent():
            self.parent().show()
        event.accept()


def main():
    app = QApplication(sys.argv)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = AddSportCriteriaWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()