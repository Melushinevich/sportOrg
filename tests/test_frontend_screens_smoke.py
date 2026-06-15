"""Smoke-тесты: создание экранов и MainApplication."""

from __future__ import annotations

import pytest

from frontend.session import session


@pytest.fixture(autouse=True)
def _auth_session():
    session.access_token = "test-token"
    session.user_id = 1
    session.role_api = "coach"
    session.email = "u@test.local"
    yield
    session.clear()


@pytest.fixture(autouse=True)
def _mock_profile_load(monkeypatch):
    monkeypatch.setattr(
        "frontend.profile_service.load_profile",
        lambda *a, **k: {
            "last_name": "Иванов",
            "first_name": "Иван",
            "birth_date": "2000-01-01",
            "city": "Москва",
            "phone": "+7",
            "gender": "Мужской",
        },
    )


@pytest.fixture(autouse=True)
def _mock_team_lists(monkeypatch):
    monkeypatch.setattr("frontend.teams_service.load_coach_teams", lambda **k: [])
    monkeypatch.setattr("frontend.teams_service.load_coach_applications", lambda **k: [])
    monkeypatch.setattr("frontend.athlete_teams_service.load_my_teams", lambda **k: [])
    monkeypatch.setattr(
        "frontend.athlete_teams_service.load_available_teams",
        lambda **k: [],
    )
    monkeypatch.setattr(
        "frontend.athlete_skills_service.load_skills_page",
        lambda **k: ([], ["Скорость", "Пас"]),
    )


@pytest.fixture(autouse=True)
def _reset_navigator():
    import frontend.navigation as nav_mod

    nav_mod._navigator = None
    yield
    nav_mod._navigator = None


def test_main_application(qtbot, no_qt_dialogs):
    from frontend.main_app import MainApplication, navigate_or
    from frontend.navigation import LOGIN, START

    app = MainApplication()
    qtbot.addWidget(app)
    assert app.currentWidget() is app.start_window
    navigate_or(app, LOGIN)
    assert app.currentWidget() is app.login_window


def test_trainer_sports_window(qtbot, no_qt_dialogs):
    from frontend.trainer_sport_window import TrainerSportsWindow

    w = TrainerSportsWindow(trainer_name="Coach")
    qtbot.addWidget(w)
    assert "SPORTORG" in w.windowTitle()


def test_add_sport_criteria_window(qtbot, no_qt_dialogs, monkeypatch):
    from frontend.add_sport_critetia_window import AddSportCriteriaWindow

    monkeypatch.setattr("frontend.teams_service.load_sports_catalog", lambda **k: [{"sport_id": 1, "name": "Футбол"}])
    monkeypatch.setattr(
        "frontend.teams_service.load_skills_catalog",
        lambda **k: [{"skill_id": 1, "name": "Скорость", "category": None}],
    )
    w = AddSportCriteriaWindow()
    qtbot.addWidget(w)
    assert w.windowTitle()


def test_athlete_main_window(qtbot, no_qt_dialogs):
    from frontend.athlete_main_window import AthleteMainWindow

    w = AthleteMainWindow()
    qtbot.addWidget(w)
    w.load_my_teams()
    assert w.windowTitle()


def test_athlete_available_teams(qtbot, no_qt_dialogs):
    from frontend.athlete_available_teams import AthleteAvailableTeamsWindow

    w = AthleteAvailableTeamsWindow()
    qtbot.addWidget(w)
    w.load_available_teams()
    assert w.windowTitle()


def test_athlete_skills_window(qtbot, no_qt_dialogs):
    from frontend.athlete_skills_window import AthleteSkillsWindow

    w = AthleteSkillsWindow()
    qtbot.addWidget(w)
    w.load_skills_data()
    assert w.windowTitle()


def test_profile_windows(qtbot, no_qt_dialogs):
    from frontend.data_page_sportsmen import ProfileWindow as SportsmanProfile
    from frontend.data_page_trainer import ProfileWindow as TrainerProfile

    s = SportsmanProfile()
    qtbot.addWidget(s)
    s.load_profile()

    t = TrainerProfile()
    qtbot.addWidget(t)
    t.load_profile()


def test_final_team_window(qtbot, no_qt_dialogs):
    from frontend.final_team_window import FinalTeamWindow

    w = FinalTeamWindow(team_name="Dream", players=[])
    qtbot.addWidget(w)
    assert w.windowTitle()


def test_skill_rating_dialog(qtbot, no_qt_dialogs):
    from frontend.skill_rating_dialog import SkillsRatingDialog

    dlg = SkillsRatingDialog(
        player_name="Иванов",
        skills=["Скорость", "Пас"],
        ratings={"Скорость": 8},
        parent=None,
    )
    qtbot.addWidget(dlg)
    assert dlg.windowTitle()


def test_player_contact_dialog(qtbot, no_qt_dialogs):
    from frontend.player_contact_dialog import PlayerContactDialog

    dlg = PlayerContactDialog(
        player_name="Иванов",
        email="a@b.com",
        phone="+7",
        parent=None,
    )
    qtbot.addWidget(dlg)
    assert dlg.windowTitle()


def test_support_link_opens(qtbot, monkeypatch):
    from frontend.support_link import SUPPORT_URL, open_support_link

    monkeypatch.setattr(
        "PyQt5.QtGui.QDesktopServices.openUrl",
        staticmethod(lambda _url: True),
    )
    assert open_support_link() is True


def test_registr_window(qtbot, no_qt_dialogs):
    from frontend.registr_window import RegistrationWindow

    w = RegistrationWindow()
    qtbot.addWidget(w)
    assert w.windowTitle()
