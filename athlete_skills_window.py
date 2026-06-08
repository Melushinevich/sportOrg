import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,
    QInputDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from burger_menu import show_burger_menu
from help_window import HelpWindow

AVAILABLE_SKILLS = [
    "Скорость", "Выносливость", "Сила", "Гибкость", "Координация", "Реакция",
    "Дриблинг", "Пас", "Удар", "Игра головой", "Техника ведения мяча",
    "Тактическое мышление", "Позиционная игра", "Чтение игры",
    "Стрессоустойчивость", "Мотивация", "Лидерство", "Дисциплина", "Командная работа",
]


class AthleteSkillsWindow(QMainWindow):
    def __init__(self, athlete_name="ЯРОСЛАВЛЬ", parent=None):
        super().__init__(parent)
        self.athlete_name = athlete_name
        self.setWindowTitle("SPORTORG - Мои скиллы")
        self.setFixedSize(1440, 1024)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(25)

        # === Верхняя панель ===
        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(QFont("UrbanSlavic", 96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        athlete_label = QLabel(self.athlete_name)
        athlete_label.setFont(QFont("UrbanSlavic", 96))
        athlete_label.setStyleSheet("color: #EF8354;")
        top_layout.addWidget(athlete_label)

        self.burger_button = QPushButton(" ")
        self.burger_button.setIcon(QIcon("burger.png"))
        self.burger_button.setIconSize(QSize(30, 30))
        self.burger_button.setFixedSize(55, 55)
        self.burger_button.setStyleSheet("""
            QPushButton {
                background: #EF8354;
                border-radius: 27px;
            }
            QPushButton:hover {
                background-color: #D6754B;
            }
        """)
        self.burger_button.clicked.connect(self.show_burger_menu)
        top_layout.addWidget(self.burger_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(30)

        # === Заголовок "Скиллы" ===
        list_title = QLabel("Скиллы")
        list_title.setFont(QFont("Roboto Flex", 20, QFont.Bold))
        list_title.setAlignment(Qt.AlignLeft)
        list_title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(list_title)

        # === Контейнер с таблицей ===
        skills_container = QWidget()
        skills_container.setStyleSheet("""
            QWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 0px;
            }
        """)
        skills_container_layout = QVBoxLayout(skills_container)
        skills_container_layout.setContentsMargins(15, 15, 15, 15)

        # Таблица скиллов
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Скилл", "Оценка по 10 б шкале"])
        self.table.setRowCount(0)

        # Настройка заголовков
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Увеличенная высота строк
        self.table.verticalHeader().setDefaultSectionSize(70)

        # Стили таблицы - ПРЯМОУГОЛЬНАЯ, без закруглений
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #6C769F;
                border-radius: 0px;
                font-family: 'Roboto Flex';
                color: black;
                selection-background-color: #EF8354;
                selection-color: white;
                gridline-color: #B0B0B0;
                min-height: 500px;
            }
            QTableWidget::item {
                padding: 10px;
                color: black;
                border: 1px solid #B0B0B0;
            }
            QHeaderView::section {
                background-color: #C8C8C8;
                color: black;
                border: 1px solid #B0B0B0;
                border-radius: 0px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Roboto Flex';
            }
            QTableCornerButton::section {
                background-color: #C8C8C8;
                border: 1px solid #B0B0B0;
                border-radius: 0px;
            }
            QScrollBar:vertical {
                background: #D9D9D9;
                width: 12px;
                border-radius: 0px;
            }
            QScrollBar::handle:vertical {
                background: #EF8354;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #D6754B;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Обработчик клика по таблице
        self.table.cellClicked.connect(self.on_cell_clicked)

        skills_container_layout.addWidget(self.table)

        # === Кнопка "ДОБАВИТЬ СКИЛЛ" внутри контейнера ===
        self.add_skill_button = QPushButton("ДОБАВИТЬ СКИЛЛ")
        self.add_skill_button.setFixedSize(690, 65)
        self.add_skill_button.setFont(QFont("Roboto Flex", 20))
        self.add_skill_button.setCursor(Qt.PointingHandCursor)
        # ИСПРАВЛЕНО: color: white; (убрал color: black; в конце)
        self.add_skill_button.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 22px;
            }
            QPushButton:hover {
                background-color: #D6754B;
            }
        """)
        self.add_skill_button.clicked.connect(self.on_add_skill)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_skill_button)
        btn_layout.addStretch()
        skills_container_layout.addLayout(btn_layout)

        main_layout.addWidget(skills_container)

        # === Кнопка "СОХРАНИТЬ" ===
        save_layout = QHBoxLayout()
        save_layout.setAlignment(Qt.AlignCenter)

        self.save_button = QPushButton("СОХРАНИТЬ")
        self.save_button.setFixedSize(400, 65)
        self.save_button.setFont(QFont("Roboto Flex", 20))
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9;
                color: black;
                border: 2px solid #B0B0B0;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #C0C0C0;
            }
        """)
        self.save_button.clicked.connect(self.on_save)

        save_layout.addWidget(self.save_button)
        main_layout.addLayout(save_layout)

        main_layout.addStretch()

        # === Нижняя панель ===
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(QFont("Roboto Flex", 10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        self.support_button = QPushButton(" ")
        try:
            self.support_button.setIcon(QIcon("headphones.png"))
            self.support_button.setIconSize(QSize(35, 35))
        except Exception:
            self.support_button.setText("")
            self.support_button.setFont(QFont("Roboto Flex", 28))

        self.support_button.setFixedSize(65, 65)
        self.support_button.setCursor(Qt.PointingHandCursor)
        self.support_button.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                border-radius: 32px;
                border: none;
                color: white; /* ИСПРАВЛЕНО: белый текст на кнопке поддержки */
            }
            QPushButton:hover {
                background-color: #D6754B;
            }
        """)

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.support_button)

        main_layout.addLayout(bottom_layout)

    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'available_teams': self.on_go_available_teams,
            'my_skills': lambda: None,
            'profile': self.on_go_profile,
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'athlete', callbacks)

    def on_go_home(self):
        from athlete_main_window import AthleteMainWindow
        self.home_window = AthleteMainWindow(athlete_name=self.athlete_name)
        self.home_window.show()
        self.close()

    def on_go_available_teams(self):
        from athlete_available_teams import AthleteAvailableTeamsWindow
        self.available_window = AthleteAvailableTeamsWindow(athlete_name=self.athlete_name)
        self.available_window.show()
        self.hide()

    def on_go_profile(self):
        from data_page_sportsmen import ProfileWindow
        self.profile_window = ProfileWindow()
        self.profile_window.show()
        self.hide()

    def on_go_help(self):
        self.help_window = HelpWindow(user_type='athlete', parent=self)
        self.help_window.show()

    def on_cell_clicked(self, row, column):
        """При клике на ячейку оценки (колонка 1) — показываем combobox"""
        if column != 1:
            return

        # Проверяем, есть ли уже combobox в этой ячейке
        existing_widget = self.table.cellWidget(row, column)
        if existing_widget and isinstance(existing_widget, QComboBox):
            return

        # Создаём combobox с оценками 1-10
        combo = QComboBox()
        combo.addItem("—")
        for i in range(1, 11):
            combo.addItem(str(i))

        combo.setFont(QFont("Roboto Flex", 16))
        combo.setStyleSheet("""
            QComboBox {
                background-color: #D9D9D9;
                border: none;
                border-radius: 15px;
                padding: 5px 10px;
                min-height: 30px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
                background-color: white;
                selection-background-color: #EF8354;
                selection-color: white;
            }
        """)

        # Устанавливаем текущее значение если есть
        current_text = self.table.item(row, column).text() if self.table.item(row, column) else ""
        if current_text:
            combo.setCurrentText(current_text)

        # При изменении значения — обновляем ячейку
        combo.currentTextChanged.connect(lambda text, r=row: self.on_rating_changed(r, text))

        # Вставляем combobox в ячейку
        self.table.setCellWidget(row, column, combo)

        # Открываем список сразу
        combo.showPopup()

    def on_rating_changed(self, row, text):
        """Сохраняем выбранную оценку в ячейку"""
        if text == "—":
            text = ""

        item = self.table.item(row, 1)
        if item:
            item.setText(text)

        # Убираем combobox после выбора
        self.table.removeCellWidget(row, 1)

    def on_add_skill(self):
        """Добавить новый навык из списка"""
        skill, ok = QInputDialog.getItem(
            self,
            "Выбор навыка",
            "Выберите навык для добавления:",
            AVAILABLE_SKILLS
        )

        if ok and skill:
            # Проверяем, нет ли уже такого навыка
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.text() == skill:
                    msg_box = QMessageBox(self)
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setWindowTitle("Внимание")
                    msg_box.setText(f"Навык '{skill}' уже добавлен!")
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    msg_box.exec_()
                    return

            # Добавляем новую строку
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Название навыка
            skill_item = QTableWidgetItem(skill)
            skill_item.setFont(QFont("Roboto Flex", 16))
            skill_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, skill_item)

            # Оценка (пустая)
            rating_item = QTableWidgetItem("")
            rating_item.setFont(QFont("Roboto Flex", 16))
            rating_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, rating_item)

    def on_save(self):
        """Сохранить скиллы"""
        if self.table.rowCount() == 0:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Внимание")
            msg_box.setText("Добавьте хотя бы один навык!")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            return

        # Собираем данные
        skills_data = []
        for row in range(self.table.rowCount()):
            skill = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            rating = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            if skill:
                skills_data.append({"skill": skill, "rating": rating})

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Сохранено")
        msg_box.setText(f"Ваши навыки сохранены! ({len(skills_data)} навыков)")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


def main():
    app = QApplication(sys.argv)

    # ИСПРАВЛЕНО: Стили для диалоговых окон
    # 1. Текст сообщений (QLabel) теперь явно черный.
    # 2. Текст кнопок (QPushButton) внутри диалогов теперь белый (был конфликт цветов).
    app.setStyleSheet("""
        QMessageBox { 
            background-color: white; 
        }
        QMessageBox QLabel { 
            color: black; 
            background-color: transparent; 
        }
        QMessageBox QPushButton {
            background-color: #EF8354; 
            color: white; 
            border: none;
            border-radius: 15px; 
            padding: 8px 20px; 
            min-width: 80px;
            font-family: 'Roboto Flex'; 
            font-size: 14px;
        }
        QMessageBox QPushButton:hover { 
            background-color: #D6754B; 
        }
        QInputDialog { 
            background-color: white; 
        }
        QInputDialog QLabel { 
            color: black; 
            background-color: transparent; 
        }
        QInputDialog QComboBox {
            background-color: #D9D9D9; 
            color: black;
            border: 1px solid #B0B0B0; 
            border-radius: 10px; 
            padding: 5px;
        }
        QInputDialog QPushButton {
            background-color: #EF8354; 
            color: white; 
            border: none;
            border-radius: 15px; 
            padding: 8px 20px; 
            min-width: 80px;
            font-family: 'Roboto Flex';
        }
        QInputDialog QPushButton:hover { 
            background-color: #D6754B; 
        }
    """)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = AthleteSkillsWindow(athlete_name="ЯРОСЛАВЛЬ")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()