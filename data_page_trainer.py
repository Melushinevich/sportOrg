import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from registr_window import SupportButton
from burger_menu import show_burger_menu


class CustomLineEdit(QLineEdit):
    def __init__(self, placeholder_text="", is_phone=False):
        super().__init__()
        self.placeholder_text = placeholder_text
        self.is_placeholder_active = True
        self.setText(placeholder_text)
        self.setAlignment(Qt.AlignCenter)

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

        self.focusInEvent = self.on_focus_in
        self.focusOutEvent = self.on_focus_out

    def on_focus_in(self, event):
        if self.is_placeholder_active:
            self.clear()
            self.is_placeholder_active = False
        super().focusInEvent(event)

    def on_focus_out(self, event):
        if not self.text():
            self.setText(self.placeholder_text)
            self.is_placeholder_active = True
        super().focusOutEvent(event)

    def get_real_text(self):
        return "" if self.is_placeholder_active else self.text()


class CustomComboBox(QComboBox):
    def __init__(self, placeholder="", items=None):
        super().__init__()
        items = items or []
        self.addItems(items)
        self.setEditable(True)

        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        self.lineEdit().setFont(QFont("Roboto Flex", 28, QFont.Thin))

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
                font-family: "Roboto Flex";
            }
        """)

        self.arrow_button = QPushButton("▼", self)
        self.arrow_button.setFixedSize(40, 40)
        self.arrow_button.setStyleSheet("""
            QPushButton{
                background:white;
                border:2px solid black;
                border-radius:20px;
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
        self.setWindowTitle("SPORTORG - Анкета тренера")
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
        title.setFont(QFont("UrbanSlavic", 96))
        title.setStyleSheet("color: black;")
        top.addWidget(title)

        top.addStretch()

        trainer = QLabel("ТРЕНЕР")
        trainer.setFont(QFont("UrbanSlavic", 96))
        trainer.setStyleSheet("color:#6C769F;")
        top.addWidget(trainer)

        self.burger = QPushButton(" ")
        self.burger.setIcon(QIcon("burger.png"))
        self.burger.setIconSize(QSize(30, 30))
        self.burger.setFixedSize(55, 55)
        self.burger.setStyleSheet("""
            QPushButton{
                background:#6C769F;
                color:white;
                border-radius:27px;
                font-size:24px;
            }
        """)
        self.burger.clicked.connect(self.show_burger_menu)
        top.addWidget(self.burger)

        main_layout.addLayout(top)
        main_layout.addSpacing(70)

        welcome = QLabel(
            "Привет! Я - твой виртуальный помощник по подбору команды,\n"
            "с которой вы победите в ваших соревнованиях!\n"
            "Пройдите регистрацию и выбирайте!"
        )
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(QFont("Roboto Flex", 26))
        welcome.setStyleSheet("color: black;")
        main_layout.addWidget(welcome)

        self.fio_input = CustomLineEdit("Фамилия Имя Отчество")
        self.fio_input.setFont(QFont("Roboto Flex", 96, QFont.Thin))
        main_layout.addWidget(self.fio_input)

        row2 = QHBoxLayout()

        self.birth_date = CustomDateEdit()
        self.birth_date.setFont(QFont("Roboto Flex", 96, QFont.Thin))

        self.gender_combo = CustomComboBox("Пол", ["Мужской", "Женский"])
        self.gender_combo.setFont(QFont("Roboto Flex", 96, QFont.Thin))

        row2.addWidget(self.birth_date)
        row2.addWidget(self.gender_combo)

        main_layout.addLayout(row2)

        row3 = QHBoxLayout()

        self.city_input = CustomLineEdit("Город проживания")
        self.phone_input = CustomLineEdit("Номер телефона")

        self.city_input.setFont(QFont("Roboto Flex", 96, QFont.Thin))
        self.phone_input.setFont(QFont("Roboto Flex", 96, QFont.Thin))

        row3.addWidget(self.city_input)
        row3.addWidget(self.phone_input)

        main_layout.addLayout(row3)

        main_layout.addStretch()

        self.save_button = QPushButton("СОХРАНИТЬ")
        self.save_button.setFixedSize(690, 91)
        self.save_button.setStyleSheet("""
            QPushButton{
                background:#6C769F;
                color:white;
                border-radius:40px;
                font-size:28px;
            }
        """)
        self.save_button.setFont(QFont("Roboto Flex", 48))
        self.save_button.clicked.connect(self.on_save)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_button)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'responses': self.on_go_responses,
            'profile': self.on_go_profile,
        }
        show_burger_menu(self, self.burger, 'trainer', callbacks)

    def on_go_home(self):
        from trainer_sport_window import TrainerSportsWindow
        self.home_window = TrainerSportsWindow(trainer_name="Тренер")
        self.home_window.show()
        self.close()

    def on_go_responses(self):
        from responses_window import ResponsesWindow
        self.responses_window = ResponsesWindow(
            team_name=None, sport_name="", parent=None, show_all=True
        )
        self.responses_window.show()
        self.hide()

    def on_go_profile(self):
        pass

    def on_save(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Сохранено")
        msg_box.setText("Ваши данные сохранены!")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


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

    window = ProfileWindow()
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()