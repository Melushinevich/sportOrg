import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from .assets import asset_path
from .burger_menu import show_burger_menu
from .help_window import HelpWindow
from .navigation import (
    ATHLETE_SKILLS,
    ATHLETE_TEAMS,
    open_profile,
    open_screen,
)
from .fonts import apply_app_fonts, ui_family_css, qss_ui_font
from .ui_messages import apply_dialog_styles, show_error
from .profile_service import athlete_display_name
from .athlete_teams_service import load_my_teams
from .api_client import ApiError
from .fonts import FONT_UI, title_font, ui_font
from .session import session


class AthleteMainWindow(QMainWindow):
    # ЗАДАЧА 3: "ЯРОСЛАВЛЬ" → "СПОРТСМЕН"
    def __init__(self, athlete_name="СПОРТСМЕН", parent=None):
        super().__init__(parent)
        self.athlete_name = athlete_name
        self.setWindowTitle("SPORTORG - Мои команды")
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

        top_layout.addStretch()

        athlete_label = QLabel(self.athlete_name)
        athlete_label.setFont(title_font(96))
        athlete_label.setStyleSheet("color: #EF8354;")
        self.athlete_name_label = athlete_label
        top_layout.addWidget(athlete_label)

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

        list_title = QLabel("Мои команды")
        list_title.setFont(ui_font(20, QFont.Bold))
        list_title.setAlignment(Qt.AlignLeft)
        list_title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(list_title)

        teams_container = QWidget()
        teams_container.setStyleSheet("""
            QWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 20px;
            }
        """)
        teams_container_layout = QVBoxLayout(teams_container)
        teams_container_layout.setContentsMargins(15, 15, 15, 15)
        teams_container_layout.setSpacing(10)

        self.teams_list = QListWidget()
        self.teams_list.setCursor(Qt.PointingHandCursor)
        self.teams_list.setStyleSheet(qss_ui_font("""
            QListWidget {
                background-color: transparent;
                border: none;
                font-size: 20px;
                font-family: __UI_FONT__;
                padding: 5px;
                min-height: 250px;
                color: black;
            }
            QListWidget::item {
                background-color: white;
                padding: 20px;
                border-radius: 15px;
                margin: 8px 0;
                color: black;
                font-style: italic;
                text-align: center;
            }
            QListWidget::item:hover { 
                background-color: #E8E8E8;
            }
            QListWidget::item:selected {
                background-color: #EF8354;
                color: white;
            }
        """))

        teams_container_layout.addWidget(self.teams_list, 1)
        main_layout.addWidget(teams_container, 1)

        self.apply_button = QPushButton("ПОДАТЬ ЗАЯВКУ В КОМАНДУ")
        self.apply_button.setFixedSize(690, 65)
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

    def load_my_teams(self) -> None:
        if not session.is_logged_in:
            return
        try:
            teams = load_my_teams()
        except ApiError as exc:
            show_error(self, "Ошибка", str(exc))
            return

        self.teams_list.clear()
        if not teams:
            empty = QListWidgetItem("Вы ещё пока не добавились ни в одну команду")
            empty.setFont(ui_font(18, italic=True))
            empty.setTextAlignment(Qt.AlignCenter)
            empty.setFlags(Qt.NoItemFlags)
            self.teams_list.addItem(empty)
            return

        for team in teams:
            item_text = f"{team['team']} — {team['sport']}"
            item = QListWidgetItem(item_text)
            item.setFont(ui_font(20, italic=True))
            item.setTextAlignment(Qt.AlignCenter)
            item.setData(Qt.UserRole, team)
            self.teams_list.addItem(item)

    def showEvent(self, event):
        super().showEvent(event)
        self.set_athlete_name(athlete_display_name())
        self.load_my_teams()

    def show_burger_menu(self):
        callbacks = {
            'home': lambda: None,
            'available_teams': self.on_go_available_teams,
            'my_skills': self.on_go_my_skills,
            'profile': self.on_go_profile,
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'athlete', callbacks)

    def on_go_available_teams(self):
        from .athlete_available_teams import AthleteAvailableTeamsWindow

        name = athlete_display_name()

        def _refresh(widget) -> None:
            if hasattr(widget, "set_athlete_name"):
                widget.set_athlete_name(name)

        open_screen(
            self,
            lambda: AthleteAvailableTeamsWindow(athlete_name=name),
            screen_id=ATHLETE_TEAMS,
            refresh=_refresh,
        )

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
        self.on_go_available_teams()


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)
    apply_dialog_styles(app)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    # ЗАДАЧА 3: "ЯРОСЛАВЛЬ" → "СПОРТСМЕН"
    window = AthleteMainWindow(athlete_name="СПОРТСМЕН")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()