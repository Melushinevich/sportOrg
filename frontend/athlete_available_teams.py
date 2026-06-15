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
from .navigation import (
    ATHLETE_HOME,
    ATHLETE_SKILLS,
    leave_to,
    open_profile,
    open_screen,
)
from .fonts import apply_app_fonts, ui_family_css, qss_ui_font
from .ui_messages import (
    apply_dialog_styles,
    ask_skills_before_apply,
    ask_yes_no,
    show_error,
    show_info,
    show_warning,
)
from .session import session
from .athlete_skills_service import has_filled_skills, load_my_skills
from .athlete_teams_service import apply_to_team, load_available_teams
from .profile_service import athlete_display_name
from .api_client import ApiError
from .fonts import FONT_UI, title_font, ui_font


class AthleteAvailableTeamsWindow(QMainWindow):
    # ЗАДАЧА 3: "ЯРОСЛАВЛЬ" → "СПОРТСМЕН"
    def __init__(self, athlete_name="СПОРТСМЕН", parent=None):
        super().__init__(parent)
        self.athlete_name = athlete_name
        self.setWindowTitle("SPORTORG - Доступные команды")
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(25)

        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(title_font(96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        athlete_label = QLabel("СПОРТСМЕН")
        athlete_label.setFont(title_font(96))
        athlete_label.setStyleSheet("color: #EF8354;")
        top_layout.addWidget(athlete_label)

        top_layout.addStretch()

        city_label = QLabel(self.athlete_name)
        city_label.setFont(title_font(96))
        city_label.setStyleSheet("color: black;")
        self.athlete_name_label = city_label
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
        list_title.setFont(ui_font(20, QFont.Bold))
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

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.verticalHeader().setDefaultSectionSize(60)

        self.table.setStyleSheet(qss_ui_font("""
            QTableWidget {
                background-color: white;
                border: 2px solid #6C769F;
                border-radius: 0px;
                font-family: __UI_FONT__;
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
                font-family: __UI_FONT__;
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
        """))

        table_container_layout.addWidget(self.table, 1)
        main_layout.addWidget(table_container, 1)

        self.apply_button = QPushButton("ПОДАТЬ ЗАЯВКУ")
        self.apply_button.setFixedSize(400, 65)
        self.apply_button.setFont(ui_font(20))
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

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(ui_font(10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def set_athlete_name(self, name: str) -> None:
        self.athlete_name = (name or "СПОРТСМЕН").strip() or "СПОРТСМЕН"
        if hasattr(self, "athlete_name_label"):
            self.athlete_name_label.setText(self.athlete_name)

    def load_available_teams(self) -> None:
        if not session.is_logged_in:
            return
        try:
            teams = load_available_teams()
        except ApiError as exc:
            show_error(self, "Ошибка", str(exc))
            return

        self.table.setRowCount(len(teams))
        for row, team in enumerate(teams):
            sport_item = QTableWidgetItem(team["sport"])
            sport_item.setFont(ui_font(16))
            sport_item.setTextAlignment(Qt.AlignCenter)
            sport_item.setFlags(sport_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, sport_item)

            team_item = QTableWidgetItem(team["team"])
            team_item.setFont(ui_font(16))
            team_item.setTextAlignment(Qt.AlignCenter)
            team_item.setData(Qt.UserRole, team["team_id"])
            team_item.setFlags(team_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, team_item)

            trainer_item = QTableWidgetItem(team["coach"])
            trainer_item.setFont(ui_font(16))
            trainer_item.setTextAlignment(Qt.AlignCenter)
            trainer_item.setFlags(trainer_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, trainer_item)

    def showEvent(self, event):
        super().showEvent(event)
        self.set_athlete_name(athlete_display_name())
        self.load_available_teams()

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
        leave_to(ATHLETE_HOME)

    def on_go_my_skills(self):
        from .athlete_skills_window import AthleteSkillsWindow

        name = athlete_display_name()

        def _refresh(widget) -> None:
            if hasattr(widget, "set_athlete_name"):
                widget.set_athlete_name(name)

        open_screen(
            self,
            lambda: AthleteSkillsWindow(athlete_name=name),
            screen_id=ATHLETE_SKILLS,
            refresh=_refresh,
        )

    def on_go_profile(self):
        open_profile("athlete")

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

        if self.table.rowCount() == 0:
            show_warning(self, "Внимание", "Нет доступных команд.")
            return

        row = selected_items[0].row()
        sport = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
        team = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        trainer = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
        team_item = self.table.item(row, 1)
        team_id = team_item.data(Qt.UserRole) if team_item else None

        if team_id is None:
            show_error(self, "Ошибка", "Не удалось определить команду.")
            return

        try:
            skills = load_my_skills()
        except ApiError:
            skills = []

        skills_choice = ask_skills_before_apply(
            self,
            skills_filled=has_filled_skills(skills),
        )
        if skills_choice == "fill_skills":
            self.on_go_my_skills()
            return
        if skills_choice != "continue":
            return

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
            try:
                apply_to_team(team_id=int(team_id))
            except ApiError as exc:
                show_error(self, "Ошибка", str(exc))
                return
            except Exception as exc:  # noqa: BLE001
                show_error(self, "Ошибка", f"Не удалось отправить заявку: {exc}")
                return

            show_info(
                self,
                "Заявка отправлена",
                f"Заявка в '{team}' успешно отправлена!",
                informative="Тренер получит уведомление и свяжется с вами.",
            )


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)
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