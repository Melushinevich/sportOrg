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


class TeamViewWindow(QMainWindow):
    def __init__(self, team_name="Команда 1", parent=None):
        super().__init__(parent)
        self.team_name = team_name
        self.setWindowTitle(f"SPORTORG - {team_name}")
        self.setFixedSize(1440, 1024)
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
        title_label.setFont(QFont("Arial", 80))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        sport_label = QLabel(self.team_name)
        sport_label.setFont(QFont("Arial", 80))
        sport_label.setStyleSheet("color: black;")
        sport_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(sport_label)

        top_layout.addStretch()

        trainer_label = QLabel("ТРЕНЕР")
        trainer_label.setFont(QFont("Arial", 80))
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

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 0px;
                gridline-color: #B0B0B0;
                font-family: 'Helvetica Neue';
                color: black;
                selection-background-color: #6C769F;
                selection-color: white;
                min-height: 450px;
            }
            QTableWidget::item { padding: 10px; color: black; }
            QHeaderView::section {
                background-color: #C8C8C8; color: black;
                border: 1px solid #B0B0B0; border-radius: 0px;
                padding: 12px; font-size: 16px; font-weight: bold;
                font-family: 'Helvetica Neue';
            }
            QTableCornerButton::section {
                background-color: #C8C8C8;
                border: 1px solid #B0B0B0;
                border-radius: 0px;
            }
        """)

        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        main_layout.addWidget(self.table)
        main_layout.addSpacing(30)

        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(15)
        action_buttons_layout.setAlignment(Qt.AlignCenter)

        self.add_player_button = QPushButton("ДОБАВИТЬ УЧАСТНИКА")
        self.add_player_button.setFixedSize(260, 55)
        self.add_player_button.setFont(QFont("Helvetica Neue", 16))
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
        self.remove_player_button.setFont(QFont("Helvetica Neue", 16))
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
        self.form_button.setFont(QFont("Helvetica Neue", 20))
        self.form_button.setCursor(Qt.PointingHandCursor)
        self.form_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F; color: white;
                border: none; border-radius: 40px; font-size: 22px;
            }
            QPushButton:hover { background-color: #5A6385; }
        """)
        self.form_button.clicked.connect(self.on_form_team)
        btn_layout.addWidget(self.form_button)

        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

        # Нижняя панель — только копирайт (кнопка поддержки убрана)
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
            'responses': self.on_go_responses_all,
            'profile': self.on_go_profile,
        }
        show_burger_menu(self, self.burger_button, 'trainer', callbacks)

    def on_go_home(self):
        if hasattr(self, 'menu') and self.menu:
            self.menu.close()
        parent = self.parent()
        while parent:
            from .trainer_sport_window import TrainerSportsWindow
            if isinstance(parent, TrainerSportsWindow):
                parent.show()
                self.close()
                return
            parent = parent.parent()

    def on_go_responses_all(self):
        if hasattr(self, 'menu') and self.menu:
            self.menu.close()
        self.all_responses_window = ResponsesWindow(
            team_name=None, sport_name="", parent=None, show_all=True
        )
        self.all_responses_window.show()
        self.hide()

    def on_go_profile(self):
        if hasattr(self, 'menu') and self.menu:
            self.menu.close()
        from .data_page_trainer import ProfileWindow
        self.profile_window = ProfileWindow()
        self.profile_window.show()
        self.hide()

    def add_players_to_table(self, players):
        for player in players:
            player_name = player.get("name", "")
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
            name_item.setFont(QFont("Helvetica Neue", 14, QFont.Bold))
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            percent_item = QTableWidgetItem("")
            percent_item.setFont(QFont("Helvetica Neue", 14, QFont.Bold))
            percent_item.setTextAlignment(Qt.AlignCenter)
            percent_item.setFlags(percent_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, percent_item)

            skills = player.get("skills", [])
            email = player.get("email", "")
            phone = player.get("phone", "")

            self.players_data[player_name] = {
                "skills": skills,
                "ratings": {},
                "email": email,
                "phone": phone
            }

            qualities_item = QTableWidgetItem(self.format_skills_display(skills, {}))
            qualities_item.setFont(QFont("Helvetica Neue", 14))
            qualities_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            qualities_item.setFlags(qualities_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, qualities_item)

            notes_item = QTableWidgetItem("")
            notes_item.setFont(QFont("Helvetica Neue", 14))
            notes_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 3, notes_item)

    def format_skills_display(self, skills, ratings):
        if not skills:
            return ""
        parts = []
        for skill in skills:
            if skill in ratings:
                parts.append(f"{skill} ({ratings[skill]})")
            else:
                parts.append(skill)
        return ", ".join(parts)

    def calculate_average_rating(self, player_name):
        if player_name not in self.players_data:
            return None
        ratings = self.players_data[player_name]["ratings"]
        if not ratings:
            return None
        average = sum(ratings.values()) / len(ratings)
        return round(average, 1)

    def update_average_rating(self, row, player_name):
        average = self.calculate_average_rating(player_name)
        percent_item = self.table.item(row, 1)
        if percent_item:
            if average is not None:
                percent_item.setText(f"{average}")
            else:
                percent_item.setText("")

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
            skills = player_data["skills"]
            ratings = player_data["ratings"]

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

                qualities_item = self.table.item(row, 2)
                if qualities_item:
                    qualities_item.setText(self.format_skills_display(skills, new_ratings))

                self.update_average_rating(row, player_name)

    def on_add_player(self):
        self.responses_window = ResponsesWindow(
            team_name=self.team_name, sport_name="", parent=self, show_all=False
        )
        self.responses_window.show()
        self.hide()

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
                if name in self.players_data:
                    del self.players_data[name]
                self.table.removeRow(row)

        except Exception as e:
            show_error(self, "Ошибка", f"Не удалось удалить участника:\n{e}")

    def on_form_team(self):
        if self.table.rowCount() == 0:
            show_warning(self, "Внимание", "Сначала добавьте хотя бы одного участника!")
            return

        players = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            if not name:
                continue
            notes = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
            ratings = self.players_data.get(name, {}).get("ratings", {})
            average = self.calculate_average_rating(name)
            players.append({
                "name": name,
                "notes": notes,
                "ratings": ratings,
                "average": average
            })

        self.final_window = FinalTeamWindow(
            team_name=self.team_name, players=players, parent=self
        )
        self.final_window.show()
        self.hide()

    def closeEvent(self, event):
        if self.parent():
            self.parent().show()
        event.accept()


def main():
    app = QApplication(sys.argv)
    apply_dialog_styles(app)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = TeamViewWindow(team_name="Команда 1")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()