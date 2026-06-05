import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from burger_menu import show_burger_menu
from help_window import HelpWindow


class AthleteMainWindow(QMainWindow):
    def __init__(self, athlete_name="ЯРОСЛАВЛЬ", parent=None):
        super().__init__(parent)
        self.athlete_name = athlete_name
        self.setWindowTitle("SPORTORG - Мои команды")
        self.setFixedSize(1440, 1024)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(25)

        # === Верхняя панель ===
        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(QFont("UrbanSlavic", 96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        athlete_label = QLabel(self.athlete_name)
        athlete_label.setFont(QFont("UrbanSlavic", 96))
        athlete_label.setStyleSheet("color: #EF8354;")
        top_layout.addWidget(athlete_label)

        self.burger_button = QPushButton(" ")
        self.burger_button.setIcon(QIcon("burger.png"))
        self.burger_button.setIconSize(QSize(30, 30))
        self.burger_button.setFixedSize(55, 55)
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

        # === Заголовок "Мои команды" ===
        list_title = QLabel("Мои команды")
        list_title.setFont(QFont("Roboto Flex", 20, QFont.Bold))
        list_title.setAlignment(Qt.AlignLeft)
        list_title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(list_title)

        # === Контейнер со списком команд ===
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

        # Скроллируемый список команд (где спортсмен уже принят)
        self.teams_list = QListWidget()
        self.teams_list.setCursor(Qt.PointingHandCursor)
        self.teams_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                font-size: 20px;
                font-family: 'Roboto Flex';
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
        """)

        # Демо-данные: команды, где спортсмен уже принят
        my_teams = [
            {"name": "Команда 1", "sport": "Футбол", "status": "Принят"},
            {"name": "Команда 3", "sport": "Волейбол", "status": "Принят"},
        ]

        for team in my_teams:
            item_text = f"{team['name']} — {team['sport']}"
            item = QListWidgetItem(item_text)
            item.setFont(QFont("Roboto Flex", 20, QFont.StyleItalic))
            item.setTextAlignment(Qt.AlignCenter)
            item.setData(Qt.UserRole, team)
            self.teams_list.addItem(item)

        teams_container_layout.addWidget(self.teams_list)
        main_layout.addWidget(teams_container)

        # === Кнопка "ПОДАТЬ ЗАЯВКУ В КОМАНДУ" ===
        self.apply_button = QPushButton("ПОДАТЬ ЗАЯВКУ В КОМАНДУ")
        self.apply_button.setFixedSize(690, 65)
        self.apply_button.setFont(QFont("Roboto Flex", 20))
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

        main_layout.addStretch()

        # === Нижняя панель ===
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(QFont("Roboto Flex", 10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        self.support_button = QPushButton(" ")
        try:
            self.support_button.setIcon(QIcon("headphones.png"))
            self.support_button.setIconSize(QSize(35, 35))
        except Exception:
            self.support_button.setText("🎧")
            self.support_button.setFont(QFont("Roboto Flex", 28))

        self.support_button.setFixedSize(65, 65)
        self.support_button.setCursor(Qt.PointingHandCursor)
        self.support_button.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                border-radius: 32px;
                border: none;
            }
            QPushButton:hover {
                background-color: #D6754B;
            }
        """)

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.support_button)

        main_layout.addLayout(bottom_layout)

    def show_burger_menu(self):
        callbacks = {
            'home': lambda: None,  # Уже на главной
            'available_teams': self.on_go_available_teams,
            'my_skills': self.on_go_my_skills,
            'profile': self.on_go_profile,
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'athlete', callbacks)

    def on_go_available_teams(self):
        """Переход на окно доступных команд"""
        from athlete_available_teams import AthleteAvailableTeamsWindow
        self.available_window = AthleteAvailableTeamsWindow(athlete_name=self.athlete_name)
        self.available_window.show()
        self.hide()

    def on_go_my_skills(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Мои скиллы")
        msg_box.setText("Раздел 'Мои скиллы' находится в разработке")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def on_go_profile(self):
        from data_page_sportsmen import ProfileWindow
        self.profile_window = ProfileWindow()
        self.profile_window.show()
        self.hide()

    def on_go_help(self):
        self.help_window = HelpWindow(user_type='athlete', parent=self)
        self.help_window.show()

    def on_apply(self):
        """Открыть окно доступных команд для подачи заявки"""
        from athlete_available_teams import AthleteAvailableTeamsWindow
        self.available_window = AthleteAvailableTeamsWindow(athlete_name=self.athlete_name)
        self.available_window.show()
        self.hide()


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMessageBox { background-color: white; }
        QMessageBox QLabel { color: black; background-color: transparent; }
        QMessageBox QPushButton {
            background-color: #EF8354; color: white; border: none;
            border-radius: 15px; padding: 8px 20px; min-width: 80px;
            font-family: 'Roboto Flex'; font-size: 14px;
        }
        QMessageBox QPushButton:hover { background-color: #D6754B; }
    """)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = AthleteMainWindow(athlete_name="ЯРОСЛАВЛЬ")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()