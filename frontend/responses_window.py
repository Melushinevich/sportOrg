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
from .ui_messages import apply_dialog_styles


class ResponsesWindow(QMainWindow):
    def __init__(self, team_name=None, sport_name="", parent=None, show_all=False):
        super().__init__(parent)
        self.team_name = team_name
        self.sport_name = sport_name
        self.show_all = show_all

        self.all_participants = [
            {
                "name": "Иванов Иван Петрович", "sport": "Футбол", "team": "Команда 1", "accepted": True,
                "email": "ivanov@example.com",
                "phone": "+7 (999) 123-45-67",
                "skills": ["Скорость", "Дриблинг", "Удар", "Тактическое мышление", "Командная работа"],
                "response_details": {
                    "experience": "5 лет", "achievements": "Чемпион области 2024",
                    "position": "Нападающий", "motivation": "Хочу развиваться в профессиональном спорте",
                    "availability": "Пн, Ср, Пт 18:00-20:00"
                }
            },
            {
                "name": "Петров Алексей Сергеевич", "sport": "Футбол", "team": "Команда 1", "accepted": False,
                "email": "petrov@example.com",
                "phone": "+7 (999) 234-56-78",
                "skills": ["Выносливость", "Пас", "Позиционная игра", "Дисциплина"],
                "response_details": {
                    "experience": "2 года", "achievements": "Участник городских соревнований",
                    "position": "Защитник", "motivation": "Люблю командные игры",
                    "availability": "Вт, Чт 19:00-21:00"
                }
            },
            {
                "name": "Сидорова Мария Андреевна", "sport": "Баскетбол", "team": "Команда 2", "accepted": True,
                "email": "sidorova@example.com",
                "phone": "+7 (999) 345-67-89",
                "skills": ["Скорость", "Выносливость", "Лидерство", "Мотивация"],
                "response_details": {
                    "experience": "7 лет", "achievements": "МС по баскетболу",
                    "position": "Разыгрывающий", "motivation": "Готовлюсь к профессиональной карьере",
                    "availability": "Ежедневно 17:00-19:00"
                }
            },
            {
                "name": "Козлов Дмитрий Владимирович", "sport": "Баскетбол", "team": "Команда 2", "accepted": False,
                "email": "kozlov@example.com",
                "phone": "+7 (999) 456-78-90",
                "skills": ["Реакция", "Координация", "Стрессоустойчивость"],
                "response_details": {
                    "experience": "1 год", "achievements": "Новичок",
                    "position": "Центровой", "motivation": "Хочу научиться играть в команде",
                    "availability": "Сб, Вс 10:00-12:00"
                }
            },
        ]

        title = "Все отклики" if show_all else f"Отклики — {team_name}"
        self.setWindowTitle(f"SPORTORG - {title}")
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

        if not self.show_all:
            trainer_label = QLabel("ТРЕНЕР")
            trainer_label.setFont(QFont("Arial", 80))
            trainer_label.setStyleSheet("color: #6C769F;")
            top_layout.addWidget(trainer_label)
        else:
            user_label = QLabel("ЯРОСЛАВЛЬ")
            user_label.setFont(QFont("Arial", 80))
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
        list_title.setFont(QFont("Helvetica Neue", 20, QFont.Bold))
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

        if self.show_all:
            participants = self.all_participants
        else:
            participants = [p for p in self.all_participants if p["team"] == self.team_name]

        self.table.setRowCount(len(participants))

        for row, participant in enumerate(participants):
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
<b>Команда:</b> {participant['team']}<br>
<b>Опыт:</b> {details['experience']}<br>
<b>Достижения:</b> {details['achievements']}<br>
<b>Позиция:</b> {details['position']}<br>
<b>Мотивация:</b> {details['motivation']}<br>
<b>Доступность:</b> {details['availability']}<br><br>
<b>Навыки:</b><br>{skills_text}
            """

            name_item = QTableWidgetItem(participant["name"])
            name_item.setFont(QFont("Helvetica Neue", 14, QFont.Bold))
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setToolTip(tooltip_text)
            self.table.setItem(row, 1, name_item)

            sport_item = QTableWidgetItem(participant["sport"])
            sport_item.setFont(QFont("Helvetica Neue", 14))
            sport_item.setTextAlignment(Qt.AlignCenter)
            sport_item.setToolTip(tooltip_text)
            self.table.setItem(row, 2, sport_item)

            if self.show_all:
                team_item = QTableWidgetItem(participant["team"])
                team_item.setFont(QFont("Helvetica Neue", 14))
                team_item.setTextAlignment(Qt.AlignCenter)
                team_item.setToolTip(tooltip_text)
                self.table.setItem(row, 3, team_item)

                skills_display = ", ".join(participant.get("skills", []))
                skills_item = QTableWidgetItem(skills_display)
                skills_item.setFont(QFont("Helvetica Neue", 13))
                skills_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                skills_item.setToolTip(tooltip_text)
                self.table.setItem(row, 4, skills_item)
            else:
                skills_display = ", ".join(participant.get("skills", []))
                skills_item = QTableWidgetItem(skills_display)
                skills_item.setFont(QFont("Helvetica Neue", 13))
                skills_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                skills_item.setToolTip(tooltip_text)
                self.table.setItem(row, 3, skills_item)

        header = self.table.horizontalHeader()
        if self.show_all:
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.Stretch)
        else:
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.table.verticalHeader().setDefaultSectionSize(50)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #F5F5F5;
                border: 2px solid #6C769F;
                gridline-color: #DDDDDD;
                font-family: 'Helvetica Neue';
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
            QTableWidget::item:hover { background-color: #D0D4E6; }
            QTableWidget::item:selected { background-color: #6C769F; color: white; }
            QHeaderView::section {
                background-color: #6C769F;
                color: white;
                border: none;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Helvetica Neue';
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
                padding: 12px; font-family: 'Helvetica Neue'; font-size: 13px;
                max-width: 400px;
            }
        """)

        main_layout.addWidget(self.table)
        main_layout.addSpacing(30)

        confirm_layout = QHBoxLayout()
        confirm_layout.setAlignment(Qt.AlignCenter)

        self.confirm_button = QPushButton("ПОДТВЕРДИТЬ ВЫБОР")
        self.confirm_button.setFixedSize(300, 55)
        self.confirm_button.setFont(QFont("Helvetica Neue", 18, QFont.Bold))
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

        main_layout.addStretch()

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
        if self.show_all:
            return
        self.all_responses_window = ResponsesWindow(
            team_name=None, sport_name="", parent=None, show_all=True
        )
        self.all_responses_window.show()
        self.close()

    def on_go_profile(self):
        from .data_page_trainer import ProfileWindow
        self.profile_window = ProfileWindow()
        self.profile_window.show()
        self.close()

    def on_go_help(self):
        from .help_window import HelpWindow
        self.help_window = HelpWindow(user_type='trainer', parent=self)
        self.help_window.show()

    def on_confirm(self):
        accepted_players = self.get_accepted_players()

        if not accepted_players:
            self.close()
            return

        if not self.show_all:
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
                    player_sport = self.table.item(row, 2).text() if self.table.item(row, 2) else ""

                    if self.show_all:
                        player_team = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
                        player_skills_text = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
                    else:
                        player_team = self.team_name
                        player_skills_text = self.table.item(row, 3).text() if self.table.item(row, 3) else ""

                    player_skills = [s.strip() for s in player_skills_text.split(",") if
                                     s.strip()] if player_skills_text else []

                    participant_data = next(
                        (p for p in self.all_participants
                         if p.get('name') == player_name and p.get('team') == player_team),
                        {}
                    )

                    player_data = {
                        "name": player_name,
                        "sport": player_sport,
                        "team": player_team,
                        "skills": player_skills,
                        "email": participant_data.get("email", ""),
                        "phone": participant_data.get("phone", "")
                    }
                    accepted.append(player_data)
        return accepted

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

    window = ResponsesWindow(team_name=None, sport_name="Футбол", show_all=True)
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()