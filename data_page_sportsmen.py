import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon


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
    def __init__(self, placeholder="", items=[]):
        super().__init__()

        self.addItems(items)
        self.setEditable(True)

        # Поле ввода
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)

        # ВОТ ТУТ главное исправление:
        self.lineEdit().setFont(QFont("Roboto Flex", 28, QFont.Thin))

        self.setCurrentText(placeholder)

        self.setStyleSheet("""
            QComboBox{
                background:#D9D9D9;
                border:2px solid black;
                border-radius:30px;
                font-size:24px;
                min-height:70px;
                padding-right:55px;
            }

            QComboBox::drop-down{
                border:none;
                width:0px;
            }

            QComboBox QAbstractItemView{
                font-size:24px;
                font-family:"Roboto Flex";
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
    def __init__(self):
        super().__init__()
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
        title.setFont(QFont("UrbanSlavic", 96))
        top.addWidget(title)

        top.addStretch()

        trainer = QLabel("СПОРТСМЕН")
        trainer.setFont(QFont("UrbanSlavic", 96))
        trainer.setStyleSheet("color:#EF8354;")
        top.addWidget(trainer)

        self.burger = QPushButton("")
        self.burger.setIcon(QIcon("burger.png"))
        self.burger.setIconSize(QSize(30, 30))
        self.burger.setFixedSize(55, 55)
        self.burger.setStyleSheet("""
            QPushButton{
                background:#EF8354;
                color:white;
                border-radius:27px;
                font-size:24px;
            }
        """)
        top.addWidget(self.burger)

        main_layout.addLayout(top)
        main_layout.addSpacing(70)

        welcome = QLabel(
            "Привет! Я-твой виртуальный помощник по подбору команды, в которой ты с удовольствием займешься тем видом"
            "спорта, который тебе по душе!"
            "\nПройди регистрацию и выбирай!"
        )
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(QFont("Roboto Flex", 20))
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
                background:#EF8354;
                color:white;
                border-radius:40px;
                font-size:28px;
            }
        """)
        self.save_button.setFont(QFont("Roboto Flex", 48))

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_button)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)


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