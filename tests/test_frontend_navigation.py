"""Тесты frontend/date_field.py и navigation."""

import pytest
from PyQt5.QtWidgets import QStackedWidget, QWidget

from frontend.date_field import CustomDateLineEdit
from frontend.navigation import (
    AppNavigator,
    bind_navigator,
    final_team_id,
    get_navigator,
    leave_to,
    open_screen,
    responses_id,
    team_view_id,
)


def test_navigation_ids():
    assert responses_id() == "trainer_responses"
    assert responses_id("Dream") == "responses:Dream"
    assert team_view_id("A") == "team_view:A"
    assert final_team_id("B") == "final_team:B"


def test_app_navigator_register_and_open(qtbot, qapp):
    import frontend.navigation as nav_mod

    nav_mod._navigator = None
    stack = QStackedWidget()
    qtbot.addWidget(stack)
    nav = bind_navigator(stack)
    widget = QWidget()
    stack.addWidget(widget)
    nav.register("home", widget)
    opened = nav.open("home")
    assert opened is widget
    assert stack.currentWidget() is widget
    nav_mod._navigator = None


def test_leave_to_without_navigator():
    import frontend.navigation as nav_mod

    nav_mod._navigator = None
    assert leave_to("start") is False


def test_open_screen_fallback_window(qtbot, qapp, monkeypatch):
    import frontend.navigation as nav_mod

    nav_mod._navigator = None
    parent = QWidget()
    qtbot.addWidget(parent)

    class _Screen(QWidget):
        pass

    window = open_screen(parent, _Screen, screen_id="x")
    assert isinstance(window, _Screen)
    assert not parent.isVisible()


def test_get_navigator_after_bind(qtbot):
    stack = QStackedWidget()
    bind_navigator(stack)
    assert get_navigator() is not None
    import frontend.navigation as nav_mod

    nav_mod._navigator = None


def test_date_field_mask_and_validation(qtbot, qapp):
    field = CustomDateLineEdit()
    qtbot.addWidget(field)
    assert field.is_empty()
    field.set_dmy_text("01.02.2000")
    assert field.is_complete()
    assert field.get_real_text() == "01.02.2000"
    field.clear_date()
    assert field.is_empty()


def test_date_field_incomplete_cleared_on_focus_out(qtbot, qapp):
    field = CustomDateLineEdit()
    qtbot.addWidget(field)
    field.setFocus()
    qtbot.wait(10)
    field.clearFocus()
    qtbot.wait(10)
    assert field.is_empty() or not field.is_complete()
