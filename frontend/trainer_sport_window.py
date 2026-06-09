import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from .add_sport_critetia_window import AddSportCriteriaWindow
from .assets import asset_path
from .burger_menu import show_burger_menu
from .data_page_trainer import ProfileWindow as TrainerProfileWindow
from .responses_window import ResponsesWindow
from .team_view_window import TeamViewWindow


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
        title_label.setFont(QFont("Arial", 96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        trainer_label = QLabel("ТРЕНЕР")
        trainer_label.setFont(QFont("Arial", 96))
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
        list_title.setFont(QFont("Helvetica Neue", 20, QFont.Bold))
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
                font-family: 'Helvetica Neue';
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
        self.add_sport_button.setFont(QFont("Helvetica Neue", 20))
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
        pass

    def on_go_responses_all(self):
        self.all_responses_window = ResponsesWindow(
            team_name=None, sport_name="", parent=None, show_all=True
        )
        self.all_responses_window.show()
        self.hide()

    def on_go_profile(self):
        self.profile_window = TrainerProfileWindow(parent=self)
        self.profile_window.show()
        self.hide()

    def add_sport_to_list(self, team_name, sport_type, criteria):
        item_text = f"{team_name}\t{sport_type}"
        item = QListWidgetItem(item_text)
        item.setFont(QFont("Helvetica Neue", 18, QFont.StyleItalic))
        item.setData(Qt.UserRole, {
            "team_name": team_name,
            "sport_type": sport_type,
            "criteria": criteria
        })
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.sports_list_widget.addItem(item)

    def on_item_clicked(self, item):
        data = item.data(Qt.UserRole)
        if data:
            team_name = data["team_name"]
            self.team_view_window = TeamViewWindow(team_name=team_name, parent=self)
            self.team_view_window.show()
            self.hide()

    def on_add_sport(self):
        existing_team_names = [item['team_name'] for item in self.sports_with_criteria]
        self.add_window = AddSportCriteriaWindow(existing_team_names, self)
        self.add_window.sport_saved.connect(self.on_sport_saved)
        self.add_window.show()
        self.hide()

    def on_sport_saved(self, team_name, sport_type, criteria):
        self.sports_with_criteria.append({
            "team_name": team_name,
            "sport_type": sport_type,
            "criteria": criteria
        })
        self.add_sport_to_list(team_name, sport_type, criteria)

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Успех")
        msg_box.setText(f"Команда '{team_name}' ({sport_type}) добавлена с {len(criteria)} критериями!")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

        self.show()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'add_window') and self.add_window:
            existing_names = [item['team_name'] for item in self.sports_with_criteria]
            self.add_window.update_existing_sports(existing_names)


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

    window = TrainerSportsWindow(trainer_name="Иван Петров")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()