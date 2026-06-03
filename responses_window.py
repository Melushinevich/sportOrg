import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from registr_window import SupportButton


class ResponsesWindow(QMainWindow):
    def __init__(self, team_name="Команда 1", sport_name="", parent=None):
        super().__init__(parent)
        self.team_name = team_name
        self.sport_name = sport_name
        self.setWindowTitle("SPORTORG - Отклики участников")
        self.setFixedSize(1440, 1024)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(25)

        # Верхняя панель
        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(QFont("UrbanSlavic", 80))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        trainer_label = QLabel("ТРЕНЕР")
        trainer_label.setFont(QFont("UrbanSlavic", 80))
        trainer_label.setStyleSheet("color: #6C769F;")
        top_layout.addWidget(trainer_label)

        top_layout.addStretch()

        user_label = QLabel("ЯРОСЛАВЛЬ")
        user_label.setFont(QFont("UrbanSlavic", 80))
        user_label.setStyleSheet("color: black;")
        top_layout.addWidget(user_label)

        self.burger_button = QPushButton(" ")
        self.burger_button.setIcon(QIcon("burger.png"))
        self.burger_button.setIconSize(QSize(30, 30))
        self.burger_button.setFixedSize(55, 55)
        self.burger_button.setStyleSheet("""
            QPushButton{
                background:#6C769F;
                border-radius:27px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        top_layout.addWidget(self.burger_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(30)

        list_title = QLabel("Отклики участников")
        list_title.setFont(QFont("Roboto Flex", 20, QFont.Bold))
        list_title.setAlignment(Qt.AlignLeft)
        list_title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(list_title)

        # Таблица откликов
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["✓", "ФИО", "Вид спорта", "Команда"])

        demo_participants = [
            {
                "name": "Иванов Иван Петрович", "sport": "Футбол", "team": "Команда 1", "accepted": True,
                "response_details": {
                    "experience": "5 лет", "achievements": "Чемпион области 2024",
                    "position": "Нападающий", "motivation": "Хочу развиваться в профессиональном спорте",
                    "availability": "Пн, Ср, Пт 18:00-20:00",
                    "skills": ["Скорость", "Дриблинг", "Удар", "Тактическое мышление", "Командная работа"]
                }
            },
            {
                "name": "Петров Алексей Сергеевич", "sport": "Футбол", "team": "Команда 1", "accepted": False,
                "response_details": {
                    "experience": "2 года", "achievements": "Участник городских соревнований",
                    "position": "Защитник", "motivation": "Люблю командные игры",
                    "availability": "Вт, Чт 19:00-21:00",
                    "skills": ["Выносливость", "Пас", "Позиционная игра", "Дисциплина"]
                }
            },
            {
                "name": "Сидорова Мария Андреевна", "sport": "Футбол", "team": "Команда 1", "accepted": True,
                "response_details": {
                    "experience": "7 лет", "achievements": "МС по футболу, призёр чемпионата России",
                    "position": "Полузащитник", "motivation": "Готовлюсь к профессиональной карьере",
                    "availability": "Ежедневно 17:00-19:00",
                    "skills": ["Скорость", "Выносливость", "Техника ведения мяча", "Чтение игры", "Лидерство", "Мотивация"]
                }
            },
            {
                "name": "Козлов Дмитрий Владимирович", "sport": "Футбол", "team": "Команда 1", "accepted": False,
                "response_details": {
                    "experience": "1 год", "achievements": "Новичок",
                    "position": "Вратарь", "motivation": "Хочу научиться играть в команде",
                    "availability": "Сб, Вс 10:00-12:00",
                    "skills": ["Реакция", "Координация", "Стрессоустойчивость"]
                }
            },
        ]

        self.table.setRowCount(len(demo_participants))

        for row, participant in enumerate(demo_participants):
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox = QCheckBox()
            checkbox.setChecked(participant["accepted"])
            checkbox.setStyleSheet("""
                QCheckBox { spacing: 0px; }
                QCheckBox::indicator {
                    width: 20px; height: 20px;
                    border: 2px solid #6C769F; border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #6C769F;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgNEw0LjUgNy41TDExIDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
                }
                QCheckBox::indicator:hover { border-color: #4A5568; }
            """)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, checkbox_widget)

            details = participant["response_details"]
            skills_text = "<br>".join([f"• {skill}" for skill in details.get("skills", [])])
            tooltip_text = f"""
<b>{participant['name']}</b><br><br>
<b>Опыт:</b> {details['experience']}<br>
<b>Достижения:</b> {details['achievements']}<br>
<b>Позиция:</b> {details['position']}<br>
<b>Мотивация:</b> {details['motivation']}<br>
<b>Доступность:</b> {details['availability']}<br><br>
<b>Навыки:</b><br>{skills_text}
            """

            name_item = QTableWidgetItem(participant["name"])
            name_item.setFont(QFont("Roboto Flex", 14, QFont.Bold))
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setToolTip(tooltip_text)
            self.table.setItem(row, 1, name_item)

            sport_item = QTableWidgetItem(participant["sport"])
            sport_item.setFont(QFont("Roboto Flex", 14))
            sport_item.setTextAlignment(Qt.AlignCenter)
            sport_item.setToolTip(tooltip_text)
            self.table.setItem(row, 2, sport_item)

            team_item = QTableWidgetItem(participant["team"])
            team_item.setFont(QFont("Roboto Flex", 14))
            team_item.setTextAlignment(Qt.AlignCenter)
            team_item.setToolTip(tooltip_text)
            self.table.setItem(row, 3, team_item)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.table.verticalHeader().setDefaultSectionSize(50)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #F5F5F5;
                border: 2px solid #6C769F;
                gridline-color: #DDDDDD;
                font-family: 'Roboto Flex';
                color: black;
                selection-background-color: #6C769F;
                selection-color: white;
                min-height: 450px;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px;
                color: black;
                border: none;
                background-color: transparent;
            }
            QTableWidget::item:hover {
                background-color: #D0D4E6;
            }
            QTableWidget::item:selected {
                background-color: #6C769F;
                color: white;
            }
            QHeaderView::section {
                background-color: #6C769F;
                color: white;
                border: none;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Roboto Flex';
            }
            QTableCornerButton::section {
                background-color: #6C769F;
                border: none;
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #6C769F;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5A6385;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QToolTip {
                background-color: white;
                color: black;
                border: 2px solid #6C769F;
                border-radius: 10px;
                padding: 12px;
                font-family: 'Roboto Flex';
                font-size: 13px;
                max-width: 400px;
            }
        """)

        main_layout.addWidget(self.table)
        main_layout.addSpacing(30)

        confirm_layout = QHBoxLayout()
        confirm_layout.setAlignment(Qt.AlignCenter)

        self.confirm_button = QPushButton("ПОДТВЕРДИТЬ ВЫБОР")
        self.confirm_button.setFixedSize(300, 55)
        self.confirm_button.setFont(QFont("Roboto Flex", 18, QFont.Bold))
        self.confirm_button.setCursor(Qt.PointingHandCursor)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F;
                color: white;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        self.confirm_button.clicked.connect(self.on_confirm)
        confirm_layout.addWidget(self.confirm_button)

        main_layout.addLayout(confirm_layout)
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

    def on_confirm(self):
        accepted_players = self.get_accepted_players()

        if not accepted_players:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Внимание")
            msg_box.setText("Выберите хотя бы одного участника галочкой для добавления в состав!")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            return

        if self.parent() and hasattr(self.parent(), 'add_players_to_table'):
            self.parent().add_players_to_table(accepted_players)

        self.close()

    def get_accepted_players(self):
        accepted = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    player_name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                    player_skills = []
                    for demo in self._get_demo_participants():
                        if demo["name"] == player_name:
                            player_skills = demo["response_details"].get("skills", [])
                            break

                    player_data = {
                        "name": player_name,
                        "sport": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                        "team": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                        "skills": player_skills
                    }
                    accepted.append(player_data)
        return accepted

    def _get_demo_participants(self):
        return [
            {"name": "Иванов Иван Петрович", "response_details": {"skills": ["Скорость", "Дриблинг", "Удар", "Тактическое мышление", "Командная работа"]}},
            {"name": "Петров Алексей Сергеевич", "response_details": {"skills": ["Выносливость", "Пас", "Позиционная игра", "Дисциплина"]}},
            {"name": "Сидорова Мария Андреевна", "response_details": {"skills": ["Скорость", "Выносливость", "Техника ведения мяча", "Чтение игры", "Лидерство", "Мотивация"]}},
            {"name": "Козлов Дмитрий Владимирович", "response_details": {"skills": ["Реакция", "Координация", "Стрессоустойчивость"]}},
        ]

    def closeEvent(self, event):
        if self.parent():
            self.parent().show()
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Глобальный стиль для диалогов
    app.setStyleSheet("""
        QMessageBox {
            background-color: white;
        }
        QMessageBox QLabel {
            color: black;
            background-color: transparent;
        }
        QMessageBox QPushButton {
            background-color: #6C769F;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 8px 20px;
            min-width: 80px;
            font-family: 'Roboto Flex';
            font-size: 14px;
        }
        QMessageBox QPushButton:hover {
            background-color: #5A6385;
        }
    """)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = ResponsesWindow(team_name="Команда 1", sport_name="Футбол")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()