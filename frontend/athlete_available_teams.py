import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from .assets import asset_path
from .burger_menu import show_burger_menu
from .help_window import HelpWindow
from .ui_messages import apply_dialog_styles, ask_yes_no, show_info, show_warning


class AthleteAvailableTeamsWindow(QMainWindow):
    # ЗАДАЧА 3: "ЯРОСЛАВЛЬ" → "СПОРТСМЕН"
    def __init__(self, athlete_name="СПОРТСМЕН", parent=None):
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

        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(QFont("Arial", 96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        athlete_label = QLabel("СПОРТСМЕН")
        athlete_label.setFont(QFont("Arial", 96))
        athlete_label.setStyleSheet("color: #EF8354;")
        top_layout.addWidget(athlete_label)

        top_layout.addStretch()

        city_label = QLabel(self.athlete_name)
        city_label.setFont(QFont("Arial", 96))
        city_label.setStyleSheet("color: black;")
        top_layout.addWidget(city_label)

        self.burger_button = QPushButton()
        self.burger_button.setFixedSize(55, 55)

        # Создаём layout для кнопки
        button_layout = QHBoxLayout(self.burger_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignCenter)

        # Создаём QLabel с иконкой
        icon_label = QLabel()
        pixmap = QPixmap(asset_path("burger.png")).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        button_layout.addWidget(icon_label)
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

        list_title = QLabel("Доступные команды")
        list_title.setFont(QFont("Helvetica Neue", 20, QFont.Bold))
        list_title.setAlignment(Qt.AlignLeft)
        list_title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(list_title)

        table_container = QWidget()
        table_container.setStyleSheet("""
            QWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 0px;
            }
        """)
        table_container_layout = QVBoxLayout(table_container)
        table_container_layout.setContentsMargins(15, 15, 15, 15)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Вид спорта", "Команда", "Тренер"])
        self.table.setRowCount(0)

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
            sport_item.setFont(QFont("Helvetica Neue", 16))
            sport_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, sport_item)

            team_item = QTableWidgetItem(team["team"])
            team_item.setFont(QFont("Helvetica Neue", 16))
            team_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, team_item)

            trainer_item = QTableWidgetItem(team["trainer"])
            trainer_item.setFont(QFont("Helvetica Neue", 16))
            trainer_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, trainer_item)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.verticalHeader().setDefaultSectionSize(60)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #6C769F;
                border-radius: 0px;
                font-family: 'Helvetica Neue';
                color: black;
                selection-background-color: #EF8354;
                selection-color: white;
                gridline-color: #B0B0B0;
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
                font-family: 'Helvetica Neue';
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

        table_container_layout.addWidget(self.table)
        main_layout.addWidget(table_container)

        self.apply_button = QPushButton("ПОДАТЬ ЗАЯВКУ")
        self.apply_button.setFixedSize(400, 65)
        self.apply_button.setFont(QFont("Helvetica Neue", 20))
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

        # ЗАДАЧА 4: Убрана кнопка поддержки
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(QFont("Helvetica Neue", 10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'available_teams': lambda: None,
            'my_skills': self.on_go_my_skills,
            'profile': self.on_go_profile,
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'athlete', callbacks)

    def on_go_home(self):
        from .athlete_main_window import AthleteMainWindow
        self.home_window = AthleteMainWindow(athlete_name=self.athlete_name)
        self.home_window.show()
        self.close()

    def on_go_my_skills(self):
        from .athlete_skills_window import AthleteSkillsWindow
        self.skills_window = AthleteSkillsWindow(athlete_name=self.athlete_name)
        self.skills_window.show()
        self.hide()

    def on_go_profile(self):
        from .data_page_sportsmen import ProfileWindow
        self.profile_window = ProfileWindow()
        self.profile_window.show()
        self.hide()

    def on_go_help(self):
        self.help_window = HelpWindow(user_type='athlete', parent=self)
        self.help_window.show()

    def on_apply(self):
        selected_items = self.table.selectedItems()

        if not selected_items:
            show_warning(
                self,
                "Внимание",
                "Выберите команду для подачи заявки!",
                informative="Кликните по строке в таблице, чтобы выбрать команду.",
            )
            return

        row = selected_items[0].row()
        sport = self.table.item(row, 0).text()
        team = self.table.item(row, 1).text()
        trainer = self.table.item(row, 2).text()

        if ask_yes_no(
            self,
            "Подтверждение заявки",
            f"Подать заявку в команду '{team}' ({sport})?",
            informative=(
                f"Тренер: {trainer}\n"
                "После отправки заявки тренер рассмотрит вашу кандидатуру."
            ),
            default_no=False,
        ):
            show_info(
                self,
                "Заявка отправлена",
                f"Заявка в '{team}' успешно отправлена!",
                informative="Тренер получит уведомление и свяжется с вами.",
            )


def main():
    app = QApplication(sys.argv)
    apply_dialog_styles(app)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    # ЗАДАЧА 3: "ЯРОСЛАВЛЬ" → "СПОРТСМЕН"
    window = AthleteAvailableTeamsWindow(athlete_name="СПОРТСМЕН")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()