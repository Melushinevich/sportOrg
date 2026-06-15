import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from . import dpi_fix
from .assets import asset_path
from .burger_menu import show_burger_menu
from .final_team_window import FinalTeamWindow
from .fonts import apply_app_fonts, title_font, ui_font, ui_family_css, qss_ui_font
from .player_contact_dialog import PlayerContactDialog
from .responses_window import ResponsesWindow
from .skill_rating_dialog import SkillsRatingDialog
from .ui_messages import (
    apply_dialog_styles,
    ask_yes_no,
    show_error,
    show_info,
    show_warning,
)
from .navigation import (
    FINAL_TEAM,
    TRAINER_HOME,
    TRAINER_RESPONSES,
    leave_to,
    open_profile,
    open_screen,
    responses_id,
)
from .api_client import ApiError
from .session import session
from .teams_service import (
    build_member_save_payload,
    load_coach_team,
    remove_team_member,
    save_team_members,
    success_percent,
)
from .team_display import format_skills_display


class TeamViewWindow(QMainWindow):
    def __init__(self, team_name="Команда 1", team_id: int | None = None, parent=None):
        super().__init__(parent)
        self.team_name = team_name
        self.team_id = team_id
        self.setWindowTitle(f"SPORTORG - {team_name}")
        self.players_data = {}
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

        top_layout.addStretch()

        sport_label = QLabel(self.team_name)
        sport_label.setFont(title_font(80))
        sport_label.setStyleSheet("color: black;")
        sport_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(sport_label)

        top_layout.addStretch()

        trainer_label = QLabel("ТРЕНЕР")
        trainer_label.setFont(title_font(80))
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
            QPushButton:hover { background-color: #5A6385; }
        """)
        self.burger_button.clicked.connect(self.show_burger_menu)
        top_layout.addWidget(self.burger_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(30)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ФИО", "Балл", "КАЧЕСТВА", "ЗАМЕТКИ"])
        self.table.setRowCount(0)

        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.table.verticalHeader().setDefaultSectionSize(50)

        self.table.setStyleSheet(qss_ui_font("""
            QTableWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 0px;
                gridline-color: #B0B0B0;
                font-family: __UI_FONT__;
                color: black;
                selection-background-color: #6C769F;
                selection-color: white;
            }
            QTableWidget::item { padding: 10px; color: black; }
            QHeaderView::section {
                background-color: #C8C8C8; color: black;
                border: 1px solid #B0B0B0; border-radius: 0px;
                padding: 12px; font-size: 16px; font-weight: bold;
                font-family: __UI_FONT__;
            }
            QTableCornerButton::section {
                background-color: #C8C8C8;
                border: 1px solid #B0B0B0;
                border-radius: 0px;
            }
        """))

        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        main_layout.addWidget(self.table, 1)
        main_layout.addSpacing(30)

        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(15)
        action_buttons_layout.setAlignment(Qt.AlignCenter)

        self.add_player_button = QPushButton("ДОБАВИТЬ УЧАСТНИКА")
        self.add_player_button.setFixedSize(260, 55)
        self.add_player_button.setFont(ui_font(16))
        self.add_player_button.setCursor(Qt.PointingHandCursor)
        self.add_player_button.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9; color: black;
                border: none; border-radius: 25px;
            }
            QPushButton:hover { background-color: #C0C0C0; }
        """)
        self.add_player_button.clicked.connect(self.on_add_player)
        action_buttons_layout.addWidget(self.add_player_button)

        self.remove_player_button = QPushButton("УДАЛИТЬ УЧАСТНИКА")
        self.remove_player_button.setFixedSize(260, 55)
        self.remove_player_button.setFont(ui_font(16))
        self.remove_player_button.setCursor(Qt.PointingHandCursor)
        self.remove_player_button.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9; color: black;
                border: none; border-radius: 25px;
            }
            QPushButton:hover { background-color: #C0C0C0; }
        """)
        self.remove_player_button.clicked.connect(self.on_remove_player)
        action_buttons_layout.addWidget(self.remove_player_button)

        main_layout.addLayout(action_buttons_layout)
        main_layout.addSpacing(40)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        self.form_button = QPushButton("СФОРМИРОВАТЬ СОСТАВ")
        self.form_button.setFixedSize(400, 65)
        self.form_button.setFont(ui_font(20))
        self.form_button.setCursor(Qt.PointingHandCursor)
        self.form_button.setStyleSheet("""
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
        self.form_button.clicked.connect(self.on_form_team)
        btn_layout.addWidget(self.form_button)

        main_layout.addLayout(btn_layout)

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
        if hasattr(self, 'menu') and self.menu:
            self.menu.close()
        leave_to(TRAINER_HOME)

    def on_go_responses_all(self):
        if hasattr(self, 'menu') and self.menu:
            self.menu.close()
        open_screen(
            self,
            lambda: ResponsesWindow(
                team_name=None, sport_name="", parent=None, show_all=True
            ),
            screen_id=TRAINER_RESPONSES,
        )

    def on_go_profile(self):
        if hasattr(self, 'menu') and self.menu:
            self.menu.close()
        open_profile("trainer")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_team_roster()

    def load_team_roster(self) -> None:
        if not self.team_id or not session.is_logged_in:
            return
        try:
            detail = load_coach_team(team_id=self.team_id)
        except ApiError as exc:
            show_error(self, "Ошибка", str(exc))
            return
        self.set_roster(detail.get("members") or [])

    def set_roster(self, members: list[dict]) -> None:
        self.table.setRowCount(0)
        self.players_data.clear()
        players = [
            {
                "member_id": m.get("member_id"),
                "name": m.get("name") or "",
                "skills": m.get("skills") or [],
                "ratings": m.get("ratings") or {},
                "qualities": m.get("qualities") or [],
                "email": m.get("email") or "",
                "phone": m.get("phone") or "",
                "score": m.get("score"),
                "notes": m.get("notes") or "",
            }
            for m in members
        ]
        self._fill_table(players)

    def add_players_to_table(self, players):
        self._fill_table(players)

    def _fill_table(self, players):
        for player in players:
            player_name = player.get("name", "")
            if not player_name:
                continue
            is_duplicate = False
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0) and self.table.item(row, 0).text() == player_name:
                    is_duplicate = True
                    break
            if is_duplicate:
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(player_name)
            name_item.setFont(ui_font(14, QFont.Bold))
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            skills = player.get("skills", [])
            if player.get("qualities"):
                skills = [
                    q.get("name") or ""
                    for q in player.get("qualities") or []
                    if q.get("name")
                ] or skills
            ratings = player.get("ratings") or {}
            email = player.get("email", "")
            phone = player.get("phone", "")

            score = success_percent(
                score=player.get("score"),
                ratings=ratings,
            )
            score_text = str(score) if score is not None else ""
            percent_item = QTableWidgetItem(score_text)
            percent_item.setFont(ui_font(14, QFont.Bold))
            percent_item.setTextAlignment(Qt.AlignCenter)
            percent_item.setFlags(percent_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, percent_item)

            self.players_data[player_name] = {
                "member_id": player.get("member_id"),
                "skills": skills,
                "ratings": dict(ratings),
                "qualities": list(player.get("qualities") or []),
                "score": player.get("score"),
                "email": email,
                "phone": phone,
            }

            qualities_item = QTableWidgetItem(format_skills_display(skills, ratings))
            qualities_item.setFont(ui_font(14))
            qualities_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            qualities_item.setFlags(qualities_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, qualities_item)

            notes_item = QTableWidgetItem(player.get("notes") or "")
            notes_item.setFont(ui_font(14))
            notes_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 3, notes_item)

    def _player_success_percent(self, player_name: str) -> float | None:
        if player_name not in self.players_data:
            return None
        data = self.players_data[player_name]
        return success_percent(
            score=data.get("score"),
            ratings=data.get("ratings") or {},
        )

    def update_success_display(self, row: int, player_name: str) -> None:
        percent = self._player_success_percent(player_name)
        percent_item = self.table.item(row, 1)
        if percent_item:
            percent_item.setText(str(percent) if percent is not None else "")

    def _member_payload_for_row(self, row: int) -> dict | None:
        name_item = self.table.item(row, 0)
        if not name_item:
            return None
        player_name = name_item.text()
        data = self.players_data.get(player_name)
        if not data or not data.get("member_id"):
            return None
        notes_item = self.table.item(row, 3)
        notes = notes_item.text() if notes_item else ""
        qualities = data.get("qualities") or []
        ratings_for_save = data.get("ratings") or {}
        return build_member_save_payload(
            member_id=int(data["member_id"]),
            notes=notes,
            qualities=qualities,
            ratings_by_name=ratings_for_save,
        )

    def _apply_member_save_result(self, row: int, player_name: str, saved: dict) -> None:
        data = self.players_data.get(player_name)
        if not data:
            return
        data["ratings"] = saved.get("ratings") or data.get("ratings") or {}
        data["qualities"] = saved.get("qualities") or data.get("qualities") or []
        data["score"] = saved.get("score")
        data["skills"] = [
            q.get("name") or ""
            for q in data.get("qualities") or []
            if q.get("name")
        ] or data.get("skills") or []

        qualities_item = self.table.item(row, 2)
        if qualities_item:
            qualities_item.setText(
                format_skills_display(
                    data.get("skills") or list(data["ratings"].keys()),
                    data["ratings"],
                )
            )
        self.update_success_display(row, player_name)

    def _save_member_row(self, row: int) -> None:
        if not self.team_id:
            return
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        player_name = name_item.text()
        payload = self._member_payload_for_row(row)
        if payload is None:
            return
        saved_list = save_team_members(team_id=self.team_id, members=[payload])
        if saved_list:
            match = next(
                (s for s in saved_list if s.get("name") == player_name),
                saved_list[0],
            )
            self._apply_member_save_result(row, player_name, match)

    def calculate_average_rating(self, player_name):
        return self._player_success_percent(player_name)

    def update_average_rating(self, row, player_name):
        self.update_success_display(row, player_name)

    def on_cell_double_clicked(self, row, column):
        player_name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
        if not player_name or player_name not in self.players_data:
            return

        player_data = self.players_data[player_name]

        if column == 0:
            email = player_data.get("email", "")
            phone = player_data.get("phone", "")
            dialog = PlayerContactDialog(player_name, email, phone, self)
            dialog.exec_()

        elif column == 2:
            qualities = player_data.get("qualities") or []
            skills = [
                q.get("name") or ""
                for q in qualities
                if q.get("name")
            ] or player_data.get("skills") or []
            ratings = player_data.get("ratings") or {}

            if not skills:
                show_info(
                    self,
                    "Нет навыков",
                    f"У игрока '{player_name}' нет указанных навыков.",
                )
                return

            dialog = SkillsRatingDialog(player_name, skills, ratings, self)
            if dialog.exec_() == SkillsRatingDialog.Accepted:
                new_ratings = dialog.get_ratings()
                self.players_data[player_name]["ratings"] = new_ratings
                if new_ratings:
                    self.players_data[player_name]["score"] = round(
                        sum(new_ratings.values()) / len(new_ratings), 1
                    )

                qualities_item = self.table.item(row, 2)
                if qualities_item:
                    qualities_item.setText(format_skills_display(skills, new_ratings))

                self.update_success_display(row, player_name)
                try:
                    self._save_member_row(row)
                except ApiError as exc:
                    show_error(self, "Ошибка", str(exc))
                    return

    def on_add_player(self):
        def _create_responses():
            window = ResponsesWindow(
                team_name=self.team_name,
                sport_name="",
                parent=None,
                show_all=False,
                team_id=self.team_id,
            )
            window._team_view = self
            return window

        window = open_screen(
            self,
            _create_responses,
            screen_id=responses_id(self.team_name),
        )
        window._team_view = self

    def on_remove_player(self):
        try:
            row = self.table.currentRow()
            if row < 0 or row >= self.table.rowCount():
                show_warning(
                    self,
                    "Внимание",
                    "Выберите участника для удаления!",
                    informative="Двойной клик по строке для выделения, затем нажмите 'Удалить'.",
                )
                return

            name_item = self.table.item(row, 0)
            name = name_item.text() if name_item else f"строка {row + 1}"

            if ask_yes_no(self, "Подтверждение удаления", f"Удалить участника '{name}'?"):
                player_data = self.players_data.get(name, {})
                member_id = player_data.get("member_id")
                if self.team_id and member_id:
                    try:
                        remove_team_member(
                            team_id=self.team_id,
                            member_id=int(member_id),
                        )
                    except ApiError as exc:
                        show_error(self, "Ошибка", str(exc))
                        return
                elif self.team_id and not member_id:
                    show_error(
                        self,
                        "Ошибка",
                        "Не удалось определить участника в базе. Обновите состав команды.",
                    )
                    return

                if name in self.players_data:
                    del self.players_data[name]
                self.table.removeRow(row)

        except Exception as e:
            show_error(self, "Ошибка", f"Не удалось удалить участника:\n{e}")

    def on_form_team(self):
        if self.table.rowCount() == 0:
            show_warning(self, "Внимание", "Сначала добавьте хотя бы одного участника!")
            return

        if not self.team_id:
            show_warning(self, "Внимание", "Не удалось определить команду.")
            return

        members_payload = []
        for row in range(self.table.rowCount()):
            payload = self._member_payload_for_row(row)
            if payload is not None:
                members_payload.append(payload)

        try:
            if members_payload:
                save_team_members(team_id=self.team_id, members=members_payload)
        except ApiError as exc:
            show_error(self, "Ошибка", str(exc))
            return

        players = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            if not name:
                continue
            notes = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
            data = self.players_data.get(name, {})
            percent = self._player_success_percent(name)
            players.append({
                "member_id": data.get("member_id"),
                "name": name,
                "notes": notes,
                "ratings": data.get("ratings") or {},
                "qualities": data.get("qualities") or [],
                "average": percent,
                "percent": percent,
            })

        players.sort(
            key=lambda p: (
                p.get("average") is None,
                -(p.get("average") or 0),
                p.get("name") or "",
            )
        )

        def _create_final():
            window = FinalTeamWindow(
                team_name=self.team_name,
                team_id=self.team_id,
                players=players,
                parent=None,
            )
            window._team_view = self
            return window

        window = open_screen(
            self,
            _create_final,
            screen_id=FINAL_TEAM,
        )
        window.set_team_data(self.team_name, players, team_id=self.team_id)

    def closeEvent(self, event):
        leave_to(TRAINER_HOME)
        event.accept()


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)
    apply_dialog_styles(app)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = TeamViewWindow(team_name="Команда 1")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()