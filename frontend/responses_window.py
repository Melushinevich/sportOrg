import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from .assets import asset_path
from .burger_menu import show_burger_menu
from .fonts import apply_app_fonts, ui_family_css, qss_ui_font
from .ui_messages import apply_dialog_styles, show_error, show_info
from .session import session
from .teams_service import accept_coach_application, load_coach_applications
from .application_skills import format_application_skills
from .api_client import ApiError
from .fonts import FONT_UI, title_font, ui_font
from .navigation import (
    TRAINER_HOME,
    TRAINER_RESPONSES,
    get_navigator,
    leave_to,
    open_profile,
    open_screen,
    responses_id,
    team_view_id,
)


class ResponsesWindow(QMainWindow):
    def __init__(
        self,
        team_name=None,
        sport_name="",
        parent=None,
        show_all=False,
        team_id: int | None = None,
    ):
        super().__init__(parent)
        self.team_name = team_name
        self.team_id = team_id
        self.sport_name = sport_name
        self.show_all = show_all
        self.all_participants: list[dict] = []

        title = "Все отклики" if show_all else f"Отклики — {team_name}"
        self.setWindowTitle(f"SPORTORG - {title}")
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(25)

        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(title_font(80))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        if not self.show_all:
            trainer_label = QLabel("ТРЕНЕР")
            trainer_label.setFont(title_font(80))
            trainer_label.setStyleSheet("color: #6C769F;")
            top_layout.addWidget(trainer_label)
        else:
            user_label = QLabel("ЯРОСЛАВЛЬ")
            user_label.setFont(title_font(80))
            user_label.setStyleSheet("color: black;")
            top_layout.addWidget(user_label)

        top_layout.addStretch()

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

        if self.show_all:
            list_title = QLabel("Все отклики спортсменов")
        else:
            list_title = QLabel(f"Отклики — {self.team_name}")
        list_title.setFont(ui_font(20, QFont.Bold))
        list_title.setAlignment(Qt.AlignLeft)
        list_title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(list_title)

        self.table = QTableWidget()
        if self.show_all:
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["✓", "ФИО", "Вид спорта", "Команда", "Навыки"])
        else:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["✓", "ФИО", "Вид спорта", "Навыки"])

        self.populate_table([])

        header = self.table.horizontalHeader()
        if self.show_all:
            header.setSectionResizeMode(0, QHeaderView.Fixed)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.Stretch)
            self.table.setColumnWidth(0, 58)
        else:
            header.setSectionResizeMode(0, QHeaderView.Fixed)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.Stretch)
            self.table.setColumnWidth(0, 58)

        self.table.verticalHeader().setDefaultSectionSize(50)

        self.table.setStyleSheet(qss_ui_font("""
            QTableWidget {
                background-color: #F5F5F5;
                border: 2px solid #6C769F;
                gridline-color: #DDDDDD;
                font-family: __UI_FONT__;
                color: black;
                selection-background-color: #6C769F;
                selection-color: white;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px;
                color: black;
                border: none;
                background-color: transparent;
            }
            QTableWidget::item:hover { background-color: #D0D4E6; }
            QTableWidget::item:selected { background-color: #6C769F; color: white; }
            QHeaderView::section {
                background-color: #6C769F;
                color: white;
                border: none;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                font-family: __UI_FONT__;
            }
            QTableCornerButton::section {
                background-color: #6C769F;
                border: none;
            }
            QScrollBar:vertical {
                background: #F5F5F5; width: 12px; margin: 0px; border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #6C769F; min-height: 30px; border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background: #5A6385; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QToolTip {
                background-color: white; color: black;
                border: 2px solid #6C769F; border-radius: 10px;
                padding: 12px; font-family: __UI_FONT__; font-size: 13px;
                max-width: 400px;
            }
        """))

        main_layout.addWidget(self.table, 1)
        main_layout.addSpacing(30)

        confirm_layout = QHBoxLayout()
        confirm_layout.setAlignment(Qt.AlignCenter)

        self.confirm_button = QPushButton("ПОДТВЕРДИТЬ ВЫБОР")
        self.confirm_button.setFixedSize(300, 55)
        self.confirm_button.setFont(ui_font(18, QFont.Bold))
        self.confirm_button.setCursor(Qt.PointingHandCursor)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F; color: white;
                border: none; border-radius: 25px;
            }
            QPushButton:hover { background-color: #5A6385; }
        """)
        self.confirm_button.clicked.connect(self.on_confirm)
        confirm_layout.addWidget(self.confirm_button)
        main_layout.addLayout(confirm_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(ui_font(10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def _create_row_checkbox(self) -> tuple[QWidget, QCheckBox]:
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        checkbox = QCheckBox()
        checkbox.setText("")
        checkbox.setChecked(False)
        checkbox.setFocusPolicy(Qt.NoFocus)
        checkbox.setFixedSize(20, 20)
        checkbox.setStyleSheet("""
            QCheckBox {
                margin: 0;
                padding: 0;
                spacing: 0;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #6C769F;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #6C769F;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgNEw0LjUgNy41TDExIDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
            }
            QCheckBox::indicator:hover { border-color: #4A5568; }
        """)

        layout.addStretch(1)
        layout.addWidget(checkbox, 0, Qt.AlignCenter)
        layout.addStretch(1)
        return wrapper, checkbox

    def populate_table(self, participants: list[dict]) -> None:
        self.table.setRowCount(len(participants))

        for row, participant in enumerate(participants):
            checkbox_widget, _checkbox = self._create_row_checkbox()
            self.table.setCellWidget(row, 0, checkbox_widget)

            name = participant.get("full_name") or participant.get("name") or "—"
            sport = participant.get("sport") or ""
            team = participant.get("team") or ""
            skills = participant.get("skills") or []
            skills_display, skills_tooltip = format_application_skills(skills)
            tooltip_text = (
                f"<b>{name}</b><br><br>"
                f"<b>Команда:</b> {team}<br>"
                f"<b>Вид спорта:</b> {sport}<br>"
                f"<b>Email:</b> {participant.get('email') or '—'}<br>"
                f"<b>Телефон:</b> {participant.get('phone') or '—'}<br><br>"
                f"<b>Самооценка (навыки):</b><br>{skills_tooltip}"
            )

            name_item = QTableWidgetItem(name)
            name_item.setFont(ui_font(14, QFont.Bold))
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setToolTip(tooltip_text)
            name_item.setData(Qt.UserRole, participant.get("application_id"))
            self.table.setItem(row, 1, name_item)

            sport_item = QTableWidgetItem(sport)
            sport_item.setFont(ui_font(14))
            sport_item.setTextAlignment(Qt.AlignCenter)
            sport_item.setToolTip(tooltip_text)
            self.table.setItem(row, 2, sport_item)

            if self.show_all:
                team_item = QTableWidgetItem(team)
                team_item.setFont(ui_font(14))
                team_item.setTextAlignment(Qt.AlignCenter)
                team_item.setToolTip(tooltip_text)
                self.table.setItem(row, 3, team_item)

                skills_item = QTableWidgetItem(skills_display)
                skills_item.setFont(ui_font(13))
                skills_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                skills_item.setToolTip(tooltip_text)
                self.table.setItem(row, 4, skills_item)
            else:
                skills_item = QTableWidgetItem(skills_display)
                skills_item.setFont(ui_font(13))
                skills_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                skills_item.setToolTip(tooltip_text)
                self.table.setItem(row, 3, skills_item)

    def load_applications(self) -> None:
        if not session.is_logged_in:
            return
        try:
            applications = load_coach_applications(
                team_id=self.team_id,
                team_name=None if self.team_id else self.team_name,
                status="pending",
            )
        except ApiError as exc:
            show_error(self, "Ошибка", str(exc))
            return

        self.all_participants = applications
        self.populate_table(applications)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_applications()

    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'responses': self.on_go_responses_all,
            'profile': self.on_go_profile,
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'trainer', callbacks)

    def on_go_home(self):
        leave_to(TRAINER_HOME)

    def on_go_responses_all(self):
        if self.show_all:
            return
        open_screen(
            self,
            lambda: ResponsesWindow(
                team_name=None, sport_name="", parent=None, show_all=True
            ),
            screen_id=TRAINER_RESPONSES,
        )

    def on_go_profile(self):
        open_profile("trainer")

    def on_go_help(self):
        from .help_window import HelpWindow
        self.help_window = HelpWindow(user_type='trainer', parent=self)
        self.help_window.show()

    def _return_from_responses(self) -> None:
        if get_navigator() is not None:
            if not self.show_all and hasattr(self, "_team_view") and self._team_view:
                leave_to(team_view_id(self.team_name))
            else:
                leave_to(TRAINER_HOME)
            return
        if self.parent():
            self.parent().show()
        self.close()

    def on_confirm(self):
        application_ids = self.get_selected_application_ids()

        if not application_ids:
            self._return_from_responses()
            return

        accepted_players = []
        for app_id in application_ids:
            try:
                result = accept_coach_application(application_id=app_id)
            except ApiError as exc:
                show_error(self, "Ошибка", str(exc))
                return
            except Exception as exc:  # noqa: BLE001
                show_error(self, "Ошибка", f"Не удалось принять заявку: {exc}")
                return
            accepted_players.append(
                {
                    "name": result.get("full_name") or "",
                    "sport": result.get("sport") or "",
                    "team": result.get("team") or "",
                    "skills": result.get("skills") or [],
                    "email": result.get("email") or "",
                    "phone": result.get("phone") or "",
                }
            )

        if accepted_players:
            show_info(
                self,
                "Готово",
                f"Принято заявок: {len(accepted_players)}",
            )

        if not self.show_all:
            team_view = getattr(self, "_team_view", None)
            if team_view and hasattr(team_view, "load_team_roster"):
                team_view.load_team_roster()

        self._return_from_responses()

    def get_selected_application_ids(self) -> list[int]:
        selected: list[int] = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if not checkbox_widget:
                continue
            checkbox = checkbox_widget.findChild(QCheckBox)
            if not checkbox or not checkbox.isChecked():
                continue
            name_item = self.table.item(row, 1)
            app_id = name_item.data(Qt.UserRole) if name_item else None
            if app_id is not None:
                selected.append(int(app_id))
        return selected

    def closeEvent(self, event):
        if get_navigator() is None and self.parent():
            self.parent().show()
        event.accept()


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)

    apply_dialog_styles(app)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = ResponsesWindow(team_name=None, sport_name="Футбол", show_all=True)
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()