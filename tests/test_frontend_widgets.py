"""Smoke-тесты экранов PyQt (setup_ui + ключевые методы)."""

from __future__ import annotations

import pytest

from frontend.session import session


@pytest.fixture(autouse=True)
def _logged_in_coach():
    session.access_token = "coach-token"
    session.user_id = 1
    session.role_api = "coach"
    yield
    session.clear()


def test_team_view_roster(qtbot, no_qt_dialogs, monkeypatch):
    from frontend.team_view_window import TeamViewWindow

    window = TeamViewWindow(team_name="Dream", team_id=1)
    qtbot.addWidget(window)
    window.set_roster(
        [
            {
                "member_id": 1,
                "name": "Иванов Иван",
                "skills": ["Скорость"],
                "ratings": {"Скорость": 8},
                "qualities": [{"name": "Скорость", "rating": 8, "skill_id": 1}],
                "score": 8.0,
                "notes": "капитан",
            }
        ]
    )
    assert window.table.rowCount() == 1
    assert window.table.item(0, 0).text() == "Иванов Иван"


def test_responses_populate_table(qtbot, no_qt_dialogs):
    from frontend.responses_window import ResponsesWindow

    window = ResponsesWindow(show_all=True)
    qtbot.addWidget(window)
    window.populate_table(
        [
            {
                "application_id": 10,
                "full_name": "Петров Пётр",
                "sport": "Футбол",
                "team": "Dream",
                "email": "p@t.com",
                "phone": "+7",
                "skills": [{"name": "Пас", "rating": 7}],
            }
        ]
    )
    assert window.table.rowCount() == 1
    assert "Пас" in window.table.item(0, 4).text()


def test_responses_selected_ids(qtbot, no_qt_dialogs):
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QCheckBox

    from frontend.responses_window import ResponsesWindow

    window = ResponsesWindow(show_all=True)
    qtbot.addWidget(window)
    window.populate_table([{"application_id": 42, "full_name": "A", "sport": "S", "skills": []}])
    checkbox = window.table.cellWidget(0, 0).findChild(QCheckBox)
    checkbox.setChecked(True)
    assert window.get_selected_application_ids() == [42]


def test_help_window(qtbot):
    from frontend.help_window import HelpWindow

    window = HelpWindow(user_type="trainer")
    qtbot.addWidget(window)
    assert window.windowTitle()


def test_start_and_login_windows(qtbot):
    from frontend.login_window import LoginWindow
    from frontend.start_window import StartWindow

    start = StartWindow()
    qtbot.addWidget(start)
    assert start.windowTitle()

    login = LoginWindow()
    qtbot.addWidget(login)
    assert login.windowTitle()


def test_ui_messages_apply(qtbot, qapp):
    from frontend.ui_messages import apply_dialog_styles, style_message_box
    from PyQt5.QtWidgets import QMessageBox

    apply_dialog_styles(qapp)
    box = QMessageBox()
    style_message_box(box)
    assert "QMessageBox" in box.styleSheet()


def test_font_files_bundled():
    from frontend.fonts import FONT_FILES

    missing = [p.name for p in FONT_FILES if not p.is_file()]
    assert not missing, f"Missing font files: {missing}"


def test_fonts_helpers(qtbot, qapp):
    from frontend.fonts import (
        FONT_TITLE,
        FONT_UI,
        apply_app_fonts,
        css_family,
        ensure_fonts_loaded,
        title_font,
        ui_font,
    )

    apply_app_fonts(qapp)
    ensure_fonts_loaded()
    assert ui_font(12).pointSize() == 12
    assert title_font(20).pointSize() == 20
    assert css_family(FONT_UI).startswith('"')
    assert "inter" in FONT_UI.lower() or FONT_UI == "Inter"
    assert "urban" in FONT_TITLE.lower() or "slavic" in FONT_TITLE.lower()
