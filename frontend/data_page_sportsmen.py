import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from .assets import asset_path
from .burger_menu import show_burger_menu
from .help_window import HelpWindow
from .navigation import open_screen


class CustomLineEdit(QLineEdit):
    def __init__(self, placeholder_text="", is_phone=False):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setPlaceholderText(placeholder_text)
        self.setStyleSheet("""
            QLineEdit{
                background:#D9D9D9;
                border:2px solid black;
                border-radius:30px;
                font-size:25px;
                color: black;
                min-height:70px;
            }
        """)

    def get_real_text(self):
        return self.text().strip()


class CustomComboBox(QComboBox):
    def __init__(self, placeholder="", items=None):
        if items is None:
            items = []
        super().__init__()
        self.addItems(items)
        self.setEditable(True)

        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        self.lineEdit().setFont(QFont("Helvetica Neue", 28, QFont.Thin))

        self.setCurrentText(placeholder)

        self.setStyleSheet("""
            QComboBox{
                background:#D9D9D9;
                border:2px solid black;
                border-radius:30px;
                font-size:24px;
                min-height:70px;
                color: black;
                padding-right:55px;
            }
            QComboBox::drop-down{
                border:none;
                width:0px;
            }
            QComboBox QAbstractItemView{
                font-size:24px;
                font-family: "Helvetica Neue";
            }
        """)

        self.arrow_button = QPushButton("▼", self)
        self.arrow_button.setFixedSize(40, 40)
        self.arrow_button.setStyleSheet("""
            QPushButton{
                background:white;
                border:2px solid black;
                border-radius:20px;
                color: black;
                font-size:18px;
            }
        """)
        self.arrow_button.clicked.connect(self.showPopup)

    def resizeEvent(self, event):
        self.arrow_button.move(self.width() - 50, (self.height() - 40) // 2)
        super().resizeEvent(event)


class CustomDateEdit(QDateEdit):
    def __init__(self):
        super().__init__()
        self.setDate(QDate.currentDate())
        self.setDisplayFormat("dd.MM.yyyy")
        self.setCalendarPopup(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)

        self.setStyleSheet("""
            QDateEdit{
                background:#D9D9D9;
                border:2px solid black;
                border-radius:30px;
                font-size:25px;
                color: black;
                min-height:70px;
            }
            QDateEdit::drop-down{
                border:none;
                width:0px;
            }
        """)

    def mousePressEvent(self, event):
        self.showCalendarPopup()
        super().mousePressEvent(event)


class ProfileWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SPORTORG - Анкета")
        self.setFixedSize(1440, 1024)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(25)

        top = QHBoxLayout()

        title = QLabel("SPORTORG")
        title.setFont(QFont("Arial", 96))
        title.setStyleSheet("color: black;")
        top.addWidget(title)

        top.addStretch()

        trainer = QLabel("СПОРТСМЕН")
        trainer.setFont(QFont("Arial", 96))
        trainer.setStyleSheet("color:#EF8354;")
        top.addWidget(trainer)

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
                background:#EF8354;
                color:white;
                border-radius:27px;
                font-size:24px;
            }
        """)
        self.burger_button.clicked.connect(self.show_burger_menu)
        top.addWidget(self.burger_button)

        main_layout.addLayout(top)
        main_layout.addSpacing(70)

        welcome = QLabel(
            "Привет! Я - твой виртуальный помощник по подбору команды, в которой ты с удовольствием займешься тем видом "
            "спорта, который тебе по душе! "
            "\nПройди регистрацию и выбирай! "
        )
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(QFont("Helvetica Neue", 20))
        welcome.setStyleSheet("color: black;")
        main_layout.addWidget(welcome)

        self.fio_input = CustomLineEdit("Фамилия Имя Отчество")
        self.fio_input.setFont(QFont("Helvetica Neue", 25))
        main_layout.addWidget(self.fio_input)

        row2 = QHBoxLayout()

        self.birth_date = CustomDateEdit()
        self.birth_date.setFont(QFont("Helvetica Neue", 25))

        self.gender_combo = CustomComboBox("Пол", ["Мужской", "Женский"])
        self.gender_combo.setFont(QFont("Helvetica Neue", 25))

        row2.addWidget(self.birth_date)
        row2.addWidget(self.gender_combo)

        main_layout.addLayout(row2)

        row3 = QHBoxLayout()

        self.city_input = CustomLineEdit("Город проживания")
        self.phone_input = CustomLineEdit("Номер телефона")

        self.city_input.setFont(QFont("Helvetica Neue", 25))
        self.phone_input.setFont(QFont("Helvetica Neue", 25))

        row3.addWidget(self.city_input)
        row3.addWidget(self.phone_input)

        main_layout.addLayout(row3)

        main_layout.addStretch()

        self.save_button = QPushButton("СОХРАНИТЬ")
        self.save_button.setFixedSize(690, 91)
        self.save_button.setStyleSheet("""
            QPushButton{
                background:#EF8354;
                color:white;
                border-radius:40px;
                font-size:28px;
            }
        """)
        self.save_button.setFont(QFont("Helvetica Neue", 48))
        self.save_button.clicked.connect(self.on_save)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_button)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'available_teams': self.on_go_available_teams,
            'my_skills': self.on_go_my_skills,
            'profile': lambda: None,
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'athlete', callbacks)

    def on_go_home(self):
        from .athlete_main_window import AthleteMainWindow

        self.home_window = open_screen(self, AthleteMainWindow)

    def on_go_available_teams(self):
        from .athlete_available_teams import AthleteAvailableTeamsWindow

        self.available_window = open_screen(self, AthleteAvailableTeamsWindow)

    def on_go_my_skills(self):
        from .athlete_skills_window import AthleteSkillsWindow

        self.skills_window = open_screen(self, AthleteSkillsWindow)

    def on_go_help(self):
        self.help_window = HelpWindow(user_type='athlete', parent=self)
        self.help_window.show()

    def on_save(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Сохранено")
        msg_box.setText("Ваши данные сохранены!")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


def main():
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = ProfileWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()