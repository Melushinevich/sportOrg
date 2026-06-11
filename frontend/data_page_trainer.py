import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from .assets import asset_path
from .burger_menu import show_burger_menu
from .help_window import HelpWindow
from .api_client import ApiError
from .navigation import open_screen
from .profile_service import (
    apply_profile_to_trainer_form,
    iso_from_dmy_text,
    load_profile,
    save_profile,
)
from .ui_messages import show_error, show_info


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
            QLineEdit::placeholder {
                color: #555555;
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
                font-size:18px;
            }
        """)
        self.arrow_button.clicked.connect(self.showPopup)

    def resizeEvent(self, event):
        self.arrow_button.move(self.width() - 50, (self.height() - 40) // 2)
        super().resizeEvent(event)


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
        title.setFont(QFont("Arial", 96))
        title.setStyleSheet("color: black;")
        top.addWidget(title)

        top.addStretch()

        trainer = QLabel("ТРЕНЕР")
        trainer.setFont(QFont("Arial", 96))
        trainer.setStyleSheet("color:#6C769F;")
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
                background:#6C769F;
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
            "Привет! Я - твой виртуальный помощник по подбору команды,\n"
            "с которой вы победите в ваших соревнованиях!\n"
            "Пройдите регистрацию и выбирайте!"
        )
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(QFont("Helvetica Neue", 26))
        welcome.setStyleSheet("color: black;")
        main_layout.addWidget(welcome)

        self.fio_input = CustomLineEdit("Фамилия Имя Отчество")
        self.fio_input.setFont(QFont("Helvetica Neue", 25))
        main_layout.addWidget(self.fio_input)

        row2 = QHBoxLayout()

        # ЗАДАЧА 1: Замена CustomDateEdit на CustomLineEdit("Дата рождения")
        self.birth_date = CustomLineEdit("Дата рождения")
        self.birth_date.setFont(QFont("Helvetica Neue", 25))

        self.gender_combo = CustomComboBox("Пол", ["Мужской", "Женский"])
        self.gender_combo.setFont(QFont("Helvetica Neue", 28, QFont.Thin))

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
                background:#6C769F;
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
            'responses': self.on_go_responses,
            'profile': lambda: None,
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'trainer', callbacks)

    def on_go_home(self):
        from .trainer_sport_window import TrainerSportsWindow

        self.home_window = open_screen(
            self, lambda: TrainerSportsWindow(trainer_name="Тренер")
        )

    def on_go_responses(self):
        from .responses_window import ResponsesWindow

        self.responses_window = open_screen(
            self,
            lambda: ResponsesWindow(
                team_name=None, sport_name="", parent=None, show_all=True
            ),
        )

    def on_go_help(self):
        self.help_window = HelpWindow(user_type='trainer', parent=self)
        self.help_window.show()

    def load_profile(self):
        profile = load_profile()
        if profile:
            apply_profile_to_trainer_form(self, profile)

    def on_save(self):
        fio = self.fio_input.get_real_text()
        city = self.city_input.get_real_text()
        phone = self.phone_input.get_real_text()

        try:
            birth_date = iso_from_dmy_text(self.birth_date.get_real_text())
            save_profile(
                fio=fio,
                birth_date=birth_date,
                city=city,
                phone=phone,
            )
        except ValueError as exc:
            show_error(self, "Ошибка", str(exc))
            return
        except ApiError as exc:
            show_error(self, "Ошибка", str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            show_error(self, "Ошибка", f"Ошибка сохранения: {exc}")
            return

        show_info(self, "Сохранено", "Ваши данные сохранены!")


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