import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from .add_sport_critetia_window import AddSportCriteriaWindow
from .assets import asset_path
from .burger_menu import show_burger_menu
from .responses_window import ResponsesWindow
from .fonts import apply_app_fonts
from .ui_messages import apply_dialog_styles, show_error, show_info
from .team_view_window import TeamViewWindow
from .fonts import FONT_UI, title_font, ui_font
from .session import session
from .teams_service import load_coach_teams
from .api_client import ApiError
from .navigation import (
    ADD_SPORT,
    TRAINER_HOME,
    TRAINER_RESPONSES,
    leave_to,
    open_profile,
    open_screen,
    responses_id,
    team_view_id,
)


class TrainerSportsWindow(QMainWindow):
    sports_added = pyqtSignal(list)
    go_back = pyqtSignal()

    def __init__(self, trainer_name=" ", trainer_data=None):
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

        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(title_font(96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        trainer_label = QLabel("ТРЕНЕР")
        trainer_label.setFont(title_font(96))
        trainer_label.setStyleSheet("color: #6C769F;")
        top_layout.addWidget(trainer_label)

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
            QPushButton{
                background:#6C769F;
                border-radius:27px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        self.burger_button.clicked.connect(self.show_burger_menu)
        top_layout.addWidget(self.burger_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(30)

        list_title = QLabel("Команды")
        list_title.setFont(ui_font(20, QFont.Bold))
        list_title.setAlignment(Qt.AlignLeft)
        list_title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(list_title)

        self.sports_list_widget = QListWidget()
        self.sports_list_widget.setCursor(Qt.PointingHandCursor)
        self.sports_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 20px;
                font-size: 18px;
                font-family: "Roboto";
                padding: 15px;
                min-height: 300px;
                color: black;
            }
            QListWidget::item {
                background-color: white;
                padding: 15px 20px;
                border-radius: 15px;
                margin: 5px 0;
                color: black;
                font-style: italic;
            }
            QListWidget::item:hover {
                background-color: #E8E8E8;
            }
            QListWidget::item:selected {
                background-color: #6C769F;
                color: white;
            }
        """)
        self.sports_list_widget.itemDoubleClicked.connect(self.on_item_clicked)
        main_layout.addWidget(self.sports_list_widget)

        self.add_sport_button = QPushButton("ДОБАВИТЬ КОМАНДУ")
        self.add_sport_button.setFixedSize(690, 65)
        self.add_sport_button.setFont(ui_font(20))
        self.add_sport_button.setCursor(Qt.PointingHandCursor)
        self.add_sport_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F;
                color: white;
                border: none;
                border-radius: 30px;
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

        # Нижняя панель — только копирайт (кнопка поддержки убрана)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(ui_font(10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'responses': self.on_go_responses_all,
            'profile': self.on_go_profile,
        }
        show_burger_menu(self, self.burger_button, 'trainer', callbacks)

    def on_go_home(self):
        leave_to(TRAINER_HOME)

    def on_go_responses_all(self):
        open_screen(
            self,
            lambda: ResponsesWindow(
                team_name=None, sport_name="", parent=None, show_all=True
            ),
            screen_id=TRAINER_RESPONSES,
        )

    def on_go_profile(self):
        open_profile("trainer")

    def add_sport_to_list(self, team_name, sport_type, criteria, team_id=None):
        item_text = f"{team_name}\t{sport_type}"
        item = QListWidgetItem(item_text)
        item.setFont(ui_font(18, italic=True))
        item.setData(Qt.UserRole, {
            "team_id": team_id,
            "team_name": team_name,
            "sport_type": sport_type,
            "criteria": criteria,
        })
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.sports_list_widget.addItem(item)

    def load_teams(self) -> None:
        if not session.is_logged_in:
            return
        try:
            teams = load_coach_teams()
        except ApiError as exc:
            show_error(self, "Ошибка", str(exc))
            return

        self.sports_list_widget.clear()
        self.sports_with_criteria = []
        for team in teams:
            entry = {
                "team_id": team["team_id"],
                "team_name": team["team"],
                "sport_type": team["sport"],
                "criteria": [],
            }
            self.sports_with_criteria.append(entry)
            self.add_sport_to_list(
                entry["team_name"],
                entry["sport_type"],
                entry["criteria"],
                entry["team_id"],
            )

    def on_item_clicked(self, item):
        data = item.data(Qt.UserRole)
        if data:
            team_name = data["team_name"]
            open_screen(
                self,
                lambda tn=team_name: TeamViewWindow(team_name=tn, parent=None),
                screen_id=team_view_id(team_name),
            )

    def on_add_sport(self):
        existing_team_names = [item['team_name'] for item in self.sports_with_criteria]

        def _create_add_window():
            window = AddSportCriteriaWindow(existing_team_names, parent=None)
            window.sport_saved.connect(self.on_sport_saved)
            self.add_window = window
            return window

        window = open_screen(self, _create_add_window, screen_id=ADD_SPORT)
        window.update_existing_sports(existing_team_names)

    def on_sport_saved(self, team_name, sport_type, criteria, team_id):
        self.load_teams()
        show_info(
            self,
            "Успех",
            f"Команда '{team_name}' ({sport_type}) сохранена с {len(criteria)} критериями!",
        )
        leave_to(TRAINER_HOME)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_teams()
        if hasattr(self, 'add_window') and self.add_window:
            existing_names = [item['team_name'] for item in self.sports_with_criteria]
            self.add_window.update_existing_sports(existing_names)


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)

    apply_dialog_styles(app)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = TrainerSportsWindow(trainer_name="Иван Петров")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()