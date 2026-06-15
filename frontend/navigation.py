"""Все экраны внутри одного QStackedWidget — без отдельных окон ОС."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStackedWidget, QWidget

from . import dpi_fix

T = TypeVar("T", bound=QWidget)

# Идентификаторы экранов в главном стеке
START = "start"
REGISTRATION = "registration"
LOGIN = "login"
SPORTSMAN_PROFILE = "sportsman_profile"
TRAINER_PROFILE = "trainer_profile"
ATHLETE_HOME = "athlete_home"
TRAINER_HOME = "trainer_home"
ATHLETE_TEAMS = "athlete_teams"
ATHLETE_SKILLS = "athlete_skills"
TRAINER_RESPONSES = "trainer_responses"
ADD_SPORT = "add_sport"
FINAL_TEAM = "final_team"


def leave_to(screen_id: str) -> bool:
    """Перейти на экран; True — если работаем внутри главного стека."""
    return navigate(screen_id) is not None


def responses_id(team_name: str | None = None) -> str:
    if team_name:
        return f"responses:{team_name}"
    return TRAINER_RESPONSES


class AppNavigator:
    def __init__(self, stack: QStackedWidget) -> None:
        self.stack = stack
        self._screens: dict[str, QWidget] = {}

    def register(self, screen_id: str, widget: QWidget) -> None:
        self._screens[screen_id] = widget

    def open(
        self,
        screen_id: str,
        factory: Callable[[], T] | None = None,
    ) -> T | QWidget:
        if screen_id not in self._screens:
            if factory is None:
                raise KeyError(f"Экран не найден: {screen_id}")
            widget = factory()
            widget.setWindowFlags(Qt.Widget)
            dpi_fix.setup_screen_widget(widget)
            self._screens[screen_id] = widget
            self.stack.addWidget(widget)
        self.stack.setCurrentWidget(self._screens[screen_id])
        return self._screens[screen_id]

    def clear_user_screens(self) -> None:
        """Удалить кэш экранов после выхода / смены пользователя."""
        protected = {
            START,
            REGISTRATION,
            LOGIN,
            SPORTSMAN_PROFILE,
            TRAINER_PROFILE,
        }
        for screen_id in list(self._screens.keys()):
            if screen_id in protected:
                continue
            widget = self._screens.pop(screen_id)
            self.stack.removeWidget(widget)
            widget.deleteLater()


_navigator: AppNavigator | None = None


def bind_navigator(stack: QStackedWidget) -> AppNavigator:
    global _navigator
    _navigator = AppNavigator(stack)
    return _navigator


def get_navigator() -> AppNavigator | None:
    return _navigator


def reset_user_screens() -> None:
    """Сбросить кэш экранов главной, команд, навыков и т.д."""
    nav = _navigator
    if nav is not None:
        nav.clear_user_screens()


def open_screen(
    from_widget: QWidget,
    factory: Callable[[], T],
    *,
    screen_id: str,
    refresh: Callable[[QWidget], None] | None = None,
) -> T | QWidget:
    """Показать экран в главном стеке или открыть отдельное окно (режим __main__)."""
    nav = _navigator
    if nav is not None:
        widget = nav.open(screen_id, factory)
        if refresh is not None:
            refresh(widget)
        return widget

    window = factory()
    from_widget.hide()
    window.show()
    return window


def navigate(screen_id: str) -> QWidget | None:
    """Переключиться на уже зарегистрированный экран."""
    nav = _navigator
    if nav is None:
        return None
    return nav.open(screen_id)


def open_profile(user_type: str) -> None:
    """Анкета спортсмена или тренера в том же окне."""
    key = SPORTSMAN_PROFILE if user_type == "athlete" else TRAINER_PROFILE
    navigate(key)


def team_view_id(team_name: str) -> str:
    return f"team_view:{team_name}"


def final_team_id(team_name: str) -> str:
    return f"final_team:{team_name}"
