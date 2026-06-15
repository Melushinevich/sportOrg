"""Тесты frontend/team_display.py и dpi/assets."""

from frontend.assets import asset_path
from frontend.phone_field import (
    PHONE_EXAMPLE,
    CustomPhoneLineEdit,
    format_phone_display,
    is_phone_complete,
    phone_digits,
)
from frontend.dpi_fix import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    make_expanding,
    setup_main_window,
    setup_screen_widget,
)
from frontend.team_display import format_skills_display


def test_format_skills_display():
    assert format_skills_display([], {}) == ""
    assert format_skills_display(["Пас"], {}) == "Пас"
    assert format_skills_display(["Скорость", "Пас"], {"Скорость": 8}) == "Скорость (8), Пас"


def test_asset_path():
    path = asset_path("burger.png")
    assert path.endswith("burger.png")
    assert "frontend" in path


def test_dpi_constants():
    from frontend.dpi_fix import MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH

    assert DEFAULT_WINDOW_WIDTH == 1320
    assert DEFAULT_WINDOW_HEIGHT == 990
    assert MIN_WINDOW_WIDTH == 1320
    assert MIN_WINDOW_HEIGHT == 990
    assert MIN_WINDOW_WIDTH * 3 == MIN_WINDOW_HEIGHT * 4


def test_dpi_widget_setup(qtbot, qapp):
    from PyQt5.QtWidgets import QMainWindow, QTableWidget, QWidget

    window = QMainWindow()
    qtbot.addWidget(window)
    setup_main_window(window)
    assert window.minimumWidth() == 1320
    assert window.minimumHeight() == 990

    screen = QWidget()
    setup_screen_widget(screen)
    table = make_expanding(QTableWidget())
    assert table is not None


def test_phone_formatting():
    assert PHONE_EXAMPLE == "+7-980-651-57-80"
    assert format_phone_display("79806515780") == "+7-980-651-57-80"
    assert format_phone_display("89806515780") == "+7-980-651-57-80"
    assert format_phone_display("9806515780") == "+7-980-651-57-80"
    assert format_phone_display("79806515780999") == "+7-980-651-57-80"
    assert phone_digits("+7-980-651") == "7980651"
    assert is_phone_complete("+7-980-651-57-80")
    assert not is_phone_complete("+7-980-651")


def test_phone_field_widget(qtbot, qapp):
    field = CustomPhoneLineEdit()
    qtbot.addWidget(field)
    assert field.placeholderText() == PHONE_EXAMPLE
    field.set_phone_text("79806515780")
    assert field.get_real_text() == "+7-980-651-57-80"
    assert field.is_complete()
    field.clear_phone()
    assert field.is_empty()
