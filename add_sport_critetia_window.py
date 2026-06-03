import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QComboBox, QLineEdit,
    QInputDialog
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from registr_window import SupportButton
from burger_menu import show_burger_menu  # <-- Добавлен импорт

AVAILABLE_SPORTS = ["Футбол", "Баскетбол", "Волейбол", "Теннис", "Плавание",
                    "Легкая атлетика", "Хоккей", "Бокс", "Самбо", "Гимнастика"]

ATHLETE_SKILLS_STUB = [
    "Скорость", "Выносливость", "Сила", "Гибкость", "Координация", "Реакция",
    "Дриблинг", "Пас", "Удар", "Игра головой", "Техника ведения мяча",
    "Тактическое мышление", "Позиционная игра", "Чтение игры",
    "Стрессоустойчивость", "Мотивация", "Лидерство", "Дисциплина", "Командная работа",
]

AVAILABLE_CRITERIA = ATHLETE_SKILLS_STUB


class AddSportCriteriaWindow(QMainWindow):
    sport_saved = pyqtSignal(str, list)

    def __init__(self, existing_sports=None, parent=None):
        super().__init__(parent)
        self.existing_sports = existing_sports or []
        self.selected_criteria = []
        self.setWindowTitle("SPORTORG - Добавление команды")
        self.setFixedSize(1440, 1024)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(100, 40, 100, 40)
        main_layout.setSpacing(15)

        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(QFont("UrbanSlavic", 80))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        trainer_label = QLabel("ТРЕНЕР")
        trainer_label.setFont(QFont("UrbanSlavic", 80))
        trainer_label.setStyleSheet("color: #6C769F;")
        top_layout.addWidget(trainer_label)

        self.burger_button = QPushButton(" ")
        self.burger_button.setIcon(QIcon("burger.png"))
        self.burger_button.setIconSize(QSize(30, 30))
        self.burger_button.setFixedSize(55, 55)
        self.burger_button.setStyleSheet("""
            QPushButton{
                background:#6C769F;
                border-radius:27px;
            }
            QPushButton:hover { background-color: #5A6385; }
        """)
        # ВАЖНО: подключаем бургер-кнопку к функции открытия менюшки
        self.burger_button.clicked.connect(self.show_burger_menu)
        top_layout.addWidget(self.burger_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(20)

        self.team_name_input = QLineEdit()
        self.team_name_input.setPlaceholderText("Название команды")
        font_input = QFont("Roboto Flex", 16)
        font_input.setItalic(True)
        self.team_name_input.setFont(font_input)
        self.team_name_input.setAlignment(Qt.AlignCenter)
        self.team_name_input.setStyleSheet("""
            QLineEdit {
                background-color: #D9D9D9;
                border: none;
                border-radius: 20px;
                padding: 10px;
                min-height: 45px;
                color: black;
            }
            QLineEdit::placeholder { color: #555555; }
        """)
        main_layout.addWidget(self.team_name_input)

        main_layout.addSpacing(10)

        self.sport_combo = QComboBox()
        self.sport_combo.addItem("Вид")
        self.sport_combo.addItems(AVAILABLE_SPORTS)
        font_combo = QFont("Roboto Flex", 16)
        font_combo.setItalic(True)
        self.sport_combo.setFont(font_combo)
        self.sport_combo.setStyleSheet("""
            QComboBox {
                background-color: #D9D9D9;
                border: none;
                border-radius: 20px;
                padding: 6px 20px;
                min-height: 45px;
                color: black;
            }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView {
                font-size: 14px; color: black;
                background-color: white;
                selection-background-color: #6C769F;
                selection-color: white;
            }
        """)
        main_layout.addWidget(self.sport_combo)

        main_layout.addSpacing(15)

        criteria_label = QLabel("Критерии")
        font_crit = QFont("Roboto Flex", 16)
        font_crit.setItalic(True)
        criteria_label.setFont(font_crit)
        criteria_label.setStyleSheet("color: black;")
        main_layout.addWidget(criteria_label)

        criteria_container = QWidget()
        criteria_container.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border: 2px solid #6C769F;
                border-radius: 20px;
            }
        """)
        criteria_container_layout = QVBoxLayout(criteria_container)
        criteria_container_layout.setContentsMargins(10, 10, 10, 10)
        criteria_container_layout.setSpacing(8)

        self.criteria_list_widget = QListWidget()
        self.criteria_list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                font-size: 14px;
                font-family: 'Roboto Flex';
                padding: 5px;
                min-height: 200px;
                max-height: 200px;
                color: black;
            }
            QListWidget::item {
                padding: 10px;
                background-color: white;
                border-radius: 12px;
                margin: 3px 0;
                color: black;
            }
            QListWidget::item:selected {
                background-color: #6C769F;
                color: white;
            }
        """)
        criteria_container_layout.addWidget(self.criteria_list_widget)

        self.add_criteria_button = QPushButton("ДОБАВИТЬ КРИТЕРИЙ")
        self.add_criteria_button.setFont(QFont("Roboto Flex", 14))
        self.add_criteria_button.setCursor(Qt.PointingHandCursor)
        self.add_criteria_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #5A6385; }
        """)
        self.add_criteria_button.clicked.connect(self.on_add_criteria)
        criteria_container_layout.addWidget(self.add_criteria_button)

        main_layout.addWidget(criteria_container)
        main_layout.addStretch()

        save_layout = QHBoxLayout()
        save_layout.setAlignment(Qt.AlignCenter)

        self.save_button = QPushButton("СОХРАНИТЬ")
        self.save_button.setFixedSize(200, 50)
        self.save_button.setFont(QFont("Roboto Flex", 16, QFont.Bold))
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9;
                color: black;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover { background-color: #C0C0C0; }
        """)
        self.save_button.clicked.connect(self.on_save)

        save_layout.addWidget(self.save_button)
        main_layout.addLayout(save_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 15, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(QFont("Roboto Flex", 9))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        self.support_button = SupportButton()

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.support_button)

        main_layout.addLayout(bottom_layout)

    # ВАЖНО: добавляем метод для открытия менюшки
    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'responses': self.on_go_responses_all,
            'profile': self.on_go_profile,
        }
        show_burger_menu(self, self.burger_button, 'trainer', callbacks)

    def on_go_home(self):
        # Возврат на главную тренера
        from trainer_sport_window import TrainerSportsWindow
        parent = self.parent()
        if parent and isinstance(parent, TrainerSportsWindow):
            parent.show()
        self.close()

    def on_go_responses_all(self):
        # Переход на все отклики
        from responses_window import ResponsesWindow
        self.responses_window = ResponsesWindow(
            team_name=None, sport_name="", parent=None, show_all=True
        )
        self.responses_window.show()
        self.hide()

    def on_go_profile(self):
        # Переход в профиль тренера
        from data_page_trainer import ProfileWindow
        self.profile_window = ProfileWindow(parent=self)
        self.profile_window.show()
        self.hide()

    def update_existing_sports(self, existing_sports):
        self.existing_sports = existing_sports

    def on_add_criteria(self):
        criteria, ok = QInputDialog.getItem(
            self, "Выбор критерия", "Выберите навык спортсмена:", AVAILABLE_CRITERIA
        )
        if ok and criteria:
            if criteria not in self.selected_criteria:
                self.selected_criteria.append(criteria)
                item = QListWidgetItem(criteria)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(QFont("Roboto Flex", 14))
                self.criteria_list_widget.addItem(item)
            else:
                self.show_error(f"Навык '{criteria}' уже добавлен!")

    def on_save(self):
        team_name = self.team_name_input.text().strip()
        sport = self.sport_combo.currentText()

        if not team_name:
            self.show_error("Введите название команды!")
            return

        if sport == "Вид":
            self.show_error("Выберите вид спорта!")
            return

        if sport in self.existing_sports:
            reply = QMessageBox.question(
                self, "Команда уже добавлена",
                f"Команда '{team_name}' уже была добавлена ранее. Заменить?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        if not self.selected_criteria:
            reply = QMessageBox.question(
                self, "Нет критериев",
                "Вы не выбрали ни одного навыка. Продолжить?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        self.sport_saved.emit(team_name, self.selected_criteria.copy())
        self.close()

    def show_error(self, message):
        msg_box = QMessageBox(self)
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

    app.setStyleSheet("""
        QMessageBox { background-color: white; }
        QMessageBox QLabel { color: black; background-color: transparent; }
        QMessageBox QPushButton {
            background-color: #6C769F; color: white; border: none;
            border-radius: 15px; padding: 8px 20px; min-width: 80px;
            font-family: 'Roboto Flex'; font-size: 14px;
        }
        QMessageBox QPushButton:hover { background-color: #5A6385; }
        QInputDialog { background-color: white; }
        QInputDialog QLabel { color: black; background-color: transparent; }
        QInputDialog QComboBox {
            background-color: #D9D9D9; color: black;
            border: 1px solid #B0B0B0; border-radius: 10px; padding: 5px;
        }
        QInputDialog QPushButton {
            background-color: #6C769F; color: white; border: none;
            border-radius: 15px; padding: 8px 20px; min-width: 80px;
            font-family: 'Roboto Flex';
        }
        QInputDialog QPushButton:hover { background-color: #5A6385; }
    """)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = AddSportCriteriaWindow()
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()