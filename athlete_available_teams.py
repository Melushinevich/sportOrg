import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from burger_menu import show_burger_menu
from help_window import HelpWindow


class AthleteAvailableTeamsWindow(QMainWindow):
    def __init__(self, athlete_name="ЯРОСЛАВЛЬ", parent=None):
        super().__init__(parent)
        self.athlete_name = athlete_name
        self.setWindowTitle("SPORTORG - Доступные команды")
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

        athlete_label = QLabel("СПОРТСМЕН")
        athlete_label.setFont(QFont("UrbanSlavic", 96))
        athlete_label.setStyleSheet("color: #EF8354;")
        top_layout.addWidget(athlete_label)

        top_layout.addStretch()

        city_label = QLabel(self.athlete_name)
        city_label.setFont(QFont("UrbanSlavic", 96))
        city_label.setStyleSheet("color: black;")
        top_layout.addWidget(city_label)

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

        # === Заголовок "Доступные команды" ===
        list_title = QLabel("Доступные команды")
        list_title.setFont(QFont("Roboto Flex", 20, QFont.Bold))
        list_title.setAlignment(Qt.AlignLeft)
        list_title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(list_title)

        # === Контейнер с таблицей ===
        table_container = QWidget()
        table_container.setStyleSheet("""
            QWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 20px;
            }
        """)
        table_container_layout = QVBoxLayout(table_container)
        table_container_layout.setContentsMargins(15, 15, 15, 15)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Вид спорта", "Команда", "Тренер"])
        self.table.setRowCount(0)

        # Демо-данные
        demo_teams = [
            {"sport": "Футбол", "team": "Команда 1", "trainer": "Иванов И.И."},
            {"sport": "Баскетбол", "team": "Команда 2", "trainer": "Петров П.П."},
            {"sport": "Волейбол", "team": "Команда 3", "trainer": "Сидоров С.С."},
            {"sport": "Хоккей", "team": "Команда 4", "trainer": "Козлов К.К."},
            {"sport": "Теннис", "team": "Команда 5", "trainer": "Новиков Н.Н."},
        ]

        self.table.setRowCount(len(demo_teams))
        for row, team in enumerate(demo_teams):
            sport_item = QTableWidgetItem(team["sport"])
            sport_item.setFont(QFont("Roboto Flex", 16))
            sport_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, sport_item)

            team_item = QTableWidgetItem(team["team"])
            team_item.setFont(QFont("Roboto Flex", 16))
            team_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, team_item)

            trainer_item = QTableWidgetItem(team["trainer"])
            trainer_item.setFont(QFont("Roboto Flex", 16))
            trainer_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, trainer_item)

        # Настройка заголовков
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.verticalHeader().setDefaultSectionSize(60)

        # Стили таблицы
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 15px;
                font-family: 'Roboto Flex';
                color: black;
                selection-background-color: #EF8354;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 10px;
                color: black;
            }
            QHeaderView::section {
                background-color: #C8C8C8;
                color: black;
                border: 1px solid #B0B0B0;
                border-radius: 15px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Roboto Flex';
            }
            QScrollBar:vertical {
                background: #D9D9D9;
                width: 12px;
                border-radius: 6px;
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

        table_container_layout.addWidget(self.table)
        main_layout.addWidget(table_container)

        # === Кнопка "ПОДАТЬ ЗАЯВКУ" ===
        self.apply_button = QPushButton("ПОДАТЬ ЗАЯВКУ")
        self.apply_button.setFixedSize(400, 65)
        self.apply_button.setFont(QFont("Roboto Flex", 20))
        self.apply_button.setCursor(Qt.PointingHandCursor)
        self.apply_button.setStyleSheet("""
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
        self.apply_button.clicked.connect(self.on_apply)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.apply_button)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

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
            self.support_button.setText("🎧")
            self.support_button.setFont(QFont("Roboto Flex", 28))

        self.support_button.setFixedSize(65, 65)
        self.support_button.setCursor(Qt.PointingHandCursor)
        self.support_button.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                border-radius: 32px;
                border: none;
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
            'available_teams': lambda: None,  # Уже на этой странице
            'my_skills': self.on_go_my_skills,
            'profile': self.on_go_profile,
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'athlete', callbacks)

    def on_go_home(self):
        """Переход на главную - мои команды"""
        from athlete_main_window import AthleteMainWindow
        self.home_window = AthleteMainWindow(athlete_name=self.athlete_name)
        self.home_window.show()
        self.close()

    def on_go_my_skills(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Мои скиллы")
        msg_box.setText("Раздел 'Мои скиллы' находится в разработке")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def on_go_profile(self):
        from data_page_sportsmen import ProfileWindow
        self.profile_window = ProfileWindow()
        self.profile_window.show()
        self.hide()

    def on_go_help(self):
        self.help_window = HelpWindow(user_type='athlete', parent=self)
        self.help_window.show()

    def on_apply(self):
        """Обработка кнопки подачи заявки"""
        selected_items = self.table.selectedItems()

        if not selected_items:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Внимание")
            msg_box.setText("Выберите команду для подачи заявки!")
            msg_box.setInformativeText("Кликните по строке в таблице, чтобы выбрать команду.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            return

        # Получаем данные выбранной строки
        row = selected_items[0].row()
        sport = self.table.item(row, 0).text()
        team = self.table.item(row, 1).text()
        trainer = self.table.item(row, 2).text()

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Подтверждение заявки")
        msg_box.setText(f"Подать заявку в команду '{team}' ({sport})?")
        msg_box.setInformativeText(f"Тренер: {trainer}\nПосле отправки заявки тренер рассмотрит вашу кандидатуру.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            success_msg = QMessageBox(self)
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setWindowTitle("Заявка отправлена")
            success_msg.setText(f"Заявка в '{team}' успешно отправлена!")
            success_msg.setInformativeText("Тренер получит уведомление и свяжется с вами.")
            success_msg.setStandardButtons(QMessageBox.Ok)
            success_msg.exec_()


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMessageBox { background-color: white; }
        QMessageBox QLabel { color: black; background-color: transparent; }
        QMessageBox QPushButton {
            background-color: #EF8354; color: white; border: none;
            border-radius: 15px; padding: 8px 20px; min-width: 80px;
            font-family: 'Roboto Flex'; font-size: 14px;
        }
        QMessageBox QPushButton:hover { background-color: #D6754B; }
    """)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = AthleteAvailableTeamsWindow(athlete_name="ЯРОСЛАВЛЬ")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()