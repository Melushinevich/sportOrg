import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from .assets import asset_path
from .burger_menu import show_burger_menu
from .help_window import HelpWindow
from .fonts import apply_app_fonts
from .ui_messages import apply_dialog_styles, show_info, show_warning
from .fonts import FONT_UI, title_font, ui_font
from .navigation import (
    TRAINER_HOME,
    TRAINER_RESPONSES,
    leave_to,
    open_profile,
    open_screen,
    team_view_id,
)


class FinalTeamWindow(QMainWindow):
    def __init__(self, team_name="Команда 1", players=None, parent=None):
        super().__init__(parent)
        self.team_name = team_name
        self.players = players or []
        self.setWindowTitle(f"SPORTORG - Итог {team_name}")
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
        title_label.setFont(title_font(80))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        final_label = QLabel(f"ИТОГ - {self.team_name}")
        final_label.setFont(title_font(80))
        final_label.setStyleSheet("color: black;")
        final_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(final_label)

        top_layout.addStretch()

        trainer_label = QLabel("ТРЕНЕР")
        trainer_label.setFont(title_font(80))
        trainer_label.setStyleSheet("color: #6C769F;")
        top_layout.addWidget(trainer_label)

        self.burger_button = QPushButton(" ")
        self.burger_button.setIcon(QIcon(asset_path("burger.png")))
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ФИО", "%-усп.", "ЗАМЕТКИ"])

        self.table.setRowCount(max(len(self.players), 1))

        font_italic = ui_font(16)
        font_italic.setItalic(True)

        for row, player in enumerate(self.players):
            name_item = QTableWidgetItem(player.get("name", ""))
            name_item.setFont(font_italic)
            name_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, name_item)

            percent_item = QTableWidgetItem("")
            percent_item.setFont(font_italic)
            percent_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, percent_item)

            notes_item = QTableWidgetItem(player.get("notes", ""))
            notes_item.setFont(font_italic)
            notes_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, notes_item)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.verticalHeader().setDefaultSectionSize(45)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 15px;
                gridline-color: #B0B0B0;
                font-family: "Roboto";
                color: black;
                selection-background-color: #6C769F;
                selection-color: white;
                min-height: 450px;
            }
            QTableWidget::item {
                padding: 8px; color: black;
                background-color: transparent;
            }
            QHeaderView::section {
                background-color: #C8C8C8; color: black;
                border: 1px solid #B0B0B0; border-radius: 0px;
                padding: 10px; font-size: 16px; font-weight: bold;
                font-family: "Roboto";
            }
            QTableCornerButton::section {
                background-color: #C8C8C8;
                border: 1px solid #B0B0B0;
            }
        """)

        main_layout.addWidget(self.table)
        main_layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(40)
        buttons_layout.setContentsMargins(20, 0, 20, 20)

        self.back_button = QPushButton("ВЕРНУТЬСЯ")
        self.back_button.setFixedSize(380, 60)
        self.back_button.setFont(ui_font(20))
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F; color: white;
                border: none; border-radius: 30px;
            }
            QPushButton:hover { background-color: #5A6385; }
        """)
        self.back_button.clicked.connect(self.on_back)

        self.save_button = QPushButton("СОХРАНИТЬ")
        self.save_button.setFixedSize(380, 60)
        self.save_button.setFont(ui_font(20))
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F; color: white;
                border: none; border-radius: 30px;
            }
            QPushButton:hover { background-color: #5A6385; }
        """)
        self.save_button.clicked.connect(self.on_save)

        buttons_layout.addWidget(self.back_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)

        # ЗАДАЧА 4: Убрана кнопка поддержки
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(ui_font(10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def set_team_data(self, team_name: str, players: list) -> None:
        self.team_name = team_name
        self.players = players or []
        self.setWindowTitle(f"SPORTORG - Итог {team_name}")
        self.table.setRowCount(max(len(self.players), 1))

        font_italic = ui_font(16)
        font_italic.setItalic(True)

        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.table.setItem(row, col, None)

        for row, player in enumerate(self.players):
            name_item = QTableWidgetItem(player.get("name", ""))
            name_item.setFont(font_italic)
            name_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, name_item)

            percent_item = QTableWidgetItem("")
            percent_item.setFont(font_italic)
            percent_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, percent_item)

            notes_item = QTableWidgetItem(player.get("notes", ""))
            notes_item.setFont(font_italic)
            notes_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, notes_item)

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
        from .responses_window import ResponsesWindow

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
        self.help_window = HelpWindow(user_type='trainer', parent=self)
        self.help_window.show()

    def on_back(self):
        if hasattr(self, "_team_view") and self._team_view is not None:
            leave_to(team_view_id(self.team_name))
        elif not leave_to(TRAINER_HOME):
            if self.parent():
                self.parent().show()
            self.close()

    def on_save(self):
        if self.table.rowCount() == 0:
            show_warning(self, "Внимание", "Таблица пуста!")
            return

        final_data = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            if not name:
                continue
            percent = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            notes = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
            final_data.append({
                "name": name,
                "percent": percent,
                "notes": notes
            })

        show_info(
            self,
            "Сохранено",
            f"Итоговый состав '{self.team_name}' сохранён! ({len(final_data)} чел.)",
        )

    def closeEvent(self, event):
        self.on_back()
        event.accept()


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)

    apply_dialog_styles(app)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    demo_players = [{"name": "ФИО", "notes": "Вася лох"}]
    window = FinalTeamWindow(team_name="ВИД 1", players=demo_players)
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()