import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from registr_window import SupportButton
from responses_window import ResponsesWindow
from final_team_window import FinalTeamWindow
from burger_menu import BurgerMenu, show_burger_menu


class TeamViewWindow(QMainWindow):
    def __init__(self, team_name="Команда 1", parent=None):
        super().__init__(parent)
        self.team_name = team_name
        self.setWindowTitle(f"SPORTORG - {team_name}")
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
        title_label.setFont(QFont("UrbanSlavic", 80))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        sport_label = QLabel(self.team_name)
        sport_label.setFont(QFont("UrbanSlavic", 80))
        sport_label.setStyleSheet("color: black;")
        sport_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(sport_label)

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
        self.burger_button.clicked.connect(self.show_burger_menu)
        top_layout.addWidget(self.burger_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(30)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ФИО", "%-усп.", "КАЧЕСТВА", "ЗАМЕТКИ"])
        self.table.setRowCount(0)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
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
                font-family: 'Roboto Flex';
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
                font-family: 'Roboto Flex';
            }
            QTableCornerButton::section {
                background-color: #C8C8C8;
                border: 1px solid #B0B0B0;
                border-radius: 0px;
            }
        """)

        main_layout.addWidget(self.table)
        main_layout.addSpacing(30)

        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(15)
        action_buttons_layout.setAlignment(Qt.AlignCenter)

        self.add_player_button = QPushButton("ДОБАВИТЬ УЧАСТНИКА")
        self.add_player_button.setFixedSize(260, 55)
        self.add_player_button.setFont(QFont("Roboto Flex", 16))
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
        self.remove_player_button.setFont(QFont("Roboto Flex", 16))
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
        self.form_button.setFont(QFont("Roboto Flex", 20))
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

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(QFont("Roboto Flex", 10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        self.support_button = SupportButton()

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.support_button)

        main_layout.addLayout(bottom_layout)

    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'responses': self.on_go_responses_all,
            'profile': self.on_go_profile,
        }
        show_burger_menu(self, self.burger_button, 'trainer', callbacks)

    def on_go_home(self):
        if self.menu:
            self.menu.close()
        parent = self.parent()
        while parent:
            from trainer_sport_window import TrainerSportsWindow
            if isinstance(parent, TrainerSportsWindow):
                parent.show()
                self.close()
                return
            parent = parent.parent()

    def on_go_responses_all(self):
        if self.menu:
            self.menu.close()
        self.all_responses_window = ResponsesWindow(
            team_name=None, sport_name="", parent=None, show_all=True
        )
        self.all_responses_window.show()
        self.hide()

    def on_go_profile(self):
        if self.menu:
            self.menu.close()
        from data_page_trainer import ProfileWindow
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
            name_item.setFont(QFont("Roboto Flex", 14, QFont.Bold))
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            percent_item = QTableWidgetItem("")
            percent_item.setFont(QFont("Roboto Flex", 14))
            percent_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, percent_item)

            skills = player.get("skills", [])
            skills_text = ", ".join(skills) if skills else ""
            qualities_item = QTableWidgetItem(skills_text)
            qualities_item.setFont(QFont("Roboto Flex", 14))
            qualities_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            qualities_item.setFlags(qualities_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, qualities_item)

            notes_item = QTableWidgetItem("")
            notes_item.setFont(QFont("Roboto Flex", 14))
            notes_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 3, notes_item)

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
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Внимание")
                msg_box.setText("Выберите участника для удаления!")
                msg_box.setInformativeText("Кликните по любой ячейке строки спортсмена.")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec_()
                return

            name_item = self.table.item(row, 0)
            name = name_item.text() if name_item else f"строка {row + 1}"

            reply = QMessageBox.question(
                self, "Подтверждение удаления",
                f"Удалить участника '{name}'?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.table.removeRow(row)

        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText(f"Не удалось удалить участника:\n{str(e)}")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

    def on_form_team(self):
        if self.table.rowCount() == 0:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Внимание")
            msg_box.setText("Сначала добавьте хотя бы одного участника!")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            return

        players = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            if not name:
                continue
            notes = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
            players.append({"name": name, "notes": notes})

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

    app.setStyleSheet("""
        QMessageBox { background-color: white; }
        QMessageBox QLabel { color: black; background-color: transparent; }
        QMessageBox QPushButton {
            background-color: #6C769F; color: white; border: none;
            border-radius: 15px; padding: 8px 20px; min-width: 80px;
            font-family: 'Roboto Flex'; font-size: 14px;
        }
        QMessageBox QPushButton:hover { background-color: #5A6385; }
    """)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = TeamViewWindow(team_name="Команда 1")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()