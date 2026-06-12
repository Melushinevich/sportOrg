import sys

from . import dpi_fix  # env для Qt — до импорта QApplication
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from .data_page_sportsmen import ProfileWindow as SportsmanProfileWindow
from .data_page_trainer import ProfileWindow as TrainerProfileWindow
from .login_window import LoginWindow
from .registr_window import RegistrationWindow
from .start_window import StartWindow
from .ui_messages import apply_dialog_styles
from .fonts import apply_app_fonts
from .profile_service import is_profile_complete, load_profile
from .navigation import (
    ATHLETE_HOME,
    LOGIN,
    REGISTRATION,
    SPORTSMAN_PROFILE,
    START,
    TRAINER_HOME,
    TRAINER_PROFILE,
    bind_navigator,
)


class MainApplication(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.start_window = StartWindow()
        self.registration_window = RegistrationWindow()
        self.login_window = LoginWindow()
        self.sportsman_window = SportsmanProfileWindow()
        self.trainer_window = TrainerProfileWindow()

        for w in (
            self.start_window,
            self.registration_window,
            self.login_window,
            self.sportsman_window,
            self.trainer_window,
        ):
            w.setWindowFlags(Qt.Widget)

        self.addWidget(self.start_window)
        self.addWidget(self.registration_window)
        self.addWidget(self.login_window)
        self.addWidget(self.sportsman_window)
        self.addWidget(self.trainer_window)

        nav = bind_navigator(self)
        nav.register(START, self.start_window)
        nav.register(REGISTRATION, self.registration_window)
        nav.register(LOGIN, self.login_window)
        nav.register(SPORTSMAN_PROFILE, self.sportsman_window)
        nav.register(TRAINER_PROFILE, self.trainer_window)

        self.start_window.go_to_registration.connect(self.on_go_to_registration)
        self.start_window.go_to_login.connect(self.on_go_to_login)
        self.registration_window.register_success.connect(self.on_register_success)
        self.registration_window.go_to_start.connect(self.on_go_to_start)
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.go_to_start.connect(self.on_go_to_start)

        nav.open(START)

    def on_go_to_registration(self):
        navigate_or(self, REGISTRATION)

    def on_go_to_login(self):
        navigate_or(self, LOGIN)
        self.login_window.clear_fields()

    def on_go_to_start(self):
        navigate_or(self, START)

    def on_register_success(self, role, email, password):
        if role == "СПОРТСМЕН":
            self.sportsman_window.load_profile()
            navigate_or(self, SPORTSMAN_PROFILE)
        elif role == "ТРЕНЕР":
            self.trainer_window.load_profile()
            navigate_or(self, TRAINER_PROFILE)

    def on_login_success(self, email, role):
        profile = load_profile()

        if role == "СПОРТСМЕН":
            self.sportsman_window.load_profile()
            if is_profile_complete(profile):
                self.sportsman_window._open_sportsman_home(profile)
            else:
                navigate_or(self, SPORTSMAN_PROFILE)
        elif role == "ТРЕНЕР":
            self.trainer_window.load_profile()
            if is_profile_complete(profile):
                self.trainer_window._open_trainer_home(profile)
            else:
                navigate_or(self, TRAINER_PROFILE)


def navigate_or(stack: QStackedWidget, screen_id: str) -> None:
    from .navigation import get_navigator

    nav = get_navigator()
    if nav:
        nav.open(screen_id)


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)

    dpi_fix.apply_dpi_fix(app)
    apply_dialog_styles(app)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = MainApplication()
    window.setWindowTitle("SPORTORG")
    window.setFixedSize(1440, 1024)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
