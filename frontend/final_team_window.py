import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from .assets import asset_path
from .burger_menu import show_burger_menu
from .help_window import HelpWindow


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
        title_label.setFont(QFont("Arial", 80))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        final_label = QLabel(f"ИТОГ - {self.team_name}")
        final_label.setFont(QFont("Arial", 80))
        final_label.setStyleSheet("color: black;")
        final_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(final_label)

        top_layout.addStretch()

        trainer_label = QLabel("ТРЕНЕР")
        trainer_label.setFont(QFont("Arial", 80))
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

        font_italic = QFont("Helvetica Neue", 16)
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
                font-family: 'Helvetica Neue';
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
                font-family: 'Helvetica Neue';
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
        self.back_button.setFont(QFont("Helvetica Neue", 20))
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
        self.save_button.setFont(QFont("Helvetica Neue", 20))
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
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'trainer', callbacks)

    def on_go_home(self):
        parent = self.parent()
        while parent:
            from .trainer_sport_window import TrainerSportsWindow
            if isinstance(parent, TrainerSportsWindow):
                parent.show()
                self.close()
                return
            parent = parent.parent()

    def on_go_responses_all(self):
        from .responses_window import ResponsesWindow
        self.all_responses_window = ResponsesWindow(
            team_name=None, sport_name="", parent=None, show_all=True
        )
        self.all_responses_window.show()
        self.hide()

    def on_go_profile(self):
        from .data_page_trainer import ProfileWindow
        self.profile_window = ProfileWindow()
        self.profile_window.show()
        self.hide()

    def on_go_help(self):
        self.help_window = HelpWindow(user_type='trainer', parent=self)
        self.help_window.show()

    def on_back(self):
        if self.parent():
            self.parent().show()
        self.close()

    def on_save(self):
        if self.table.rowCount() == 0:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Внимание")
            msg_box.setText("Таблица пуста!")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
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

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Сохранено")
        msg_box.setText(f"Итоговый состав '{self.team_name}' сохранён! ({len(final_data)} чел.)")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

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
            font-family: 'Helvetica Neue'; font-size: 14px;
        }
        QMessageBox QPushButton:hover { background-color: #5A6385; }
    """)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    demo_players = [{"name": "ФИО", "notes": "Вася лох"}]
    window = FinalTeamWindow(team_name="ВИД 1", players=demo_players)
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()