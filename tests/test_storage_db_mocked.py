"""storage_postgres: ключевые функции с моком соединения."""

from unittest.mock import MagicMock

import pytest

from user_registration import storage_postgres as sp


def _mock_conn(monkeypatch, *, fetchone=None, fetchall=None, rowcount=1):
    cur = MagicMock()
    cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = fetchall if fetchall is not None else []
    cur.rowcount = rowcount
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)

    conn = MagicMock()
    conn.cursor.return_value = cur
    conn.__enter__ = lambda s: s
    conn.__exit__ = MagicMock(return_value=False)

    monkeypatch.setattr(sp, "get_db_connection", lambda: conn)
    return cur, conn


def test_get_user_by_email_found(monkeypatch):
    row = {"id": 1, "email": "a@b.com", "role": "sportsman", "password_hash": "h"}
    _mock_conn(monkeypatch, fetchone=row)
    user = sp.get_user_by_email("a@b.com")
    assert user["id"] == 1


def test_get_user_by_email_missing(monkeypatch):
    _mock_conn(monkeypatch, fetchone=None)
    assert sp.get_user_by_email("none@b.com") is None


def test_get_user_by_id(monkeypatch):
    _mock_conn(monkeypatch, fetchone={"id": 2, "email": "x@y.z", "role": "coach"})
    assert sp.get_user_by_id(2)["role"] == "coach"


def test_list_athlete_skills(monkeypatch):
    _mock_conn(
        monkeypatch,
        fetchall=[
            {"id": 1, "user_id": 2, "skill_id": 10, "self_rating": 8, "name": "Скорость"},
        ],
    )
    rows = sp.list_athlete_skills(2)
    assert rows[0]["name"] == "Скорость"
    assert rows[0]["rating"] == 8
    assert rows[0]["skill_id"] == 10


def test_get_or_create_skill_id_existing(monkeypatch):
    cur, _conn = _mock_conn(monkeypatch)
    cur.fetchone.side_effect = [None, {"id": 7}]
    assert sp._get_or_create_skill_id(cur, "Сила") == 7


def test_add_athlete_skill(monkeypatch):
    cur, _conn = _mock_conn(monkeypatch)
    cur.fetchone.side_effect = [{"id": 3}, {"id": 5}]
    new_id = sp.add_athlete_skill(2, "Сила")
    assert new_id == 5


def test_replace_athlete_skills(monkeypatch):
    cur, _conn = _mock_conn(monkeypatch)
    cur.fetchone.return_value = {"id": 1}
    sp.replace_athlete_skills(2, [{"name": "A", "rating": 7}])


def test_ensure_sport_insert(monkeypatch):
    cur, conn = _mock_conn(monkeypatch)
    cur.fetchone.side_effect = [{"id": 3}]
    sid = sp.ensure_sport("Футбол")
    assert sid == 3
    conn.commit.assert_called()


def test_ensure_sport_existing(monkeypatch):
    cur, _conn = _mock_conn(monkeypatch)
    cur.fetchone.side_effect = [None, {"id": 9}]
    assert sp.ensure_sport("Баскетбол") == 9


def test_list_coach_teams(monkeypatch):
    _mock_conn(monkeypatch, fetchall=[{"team_id": 1, "team": "К1", "sport": "Футбол"}])
    rows = sp.list_coach_teams(1)
    assert rows[0]["team"] == "К1"


def test_list_available_teams(monkeypatch):
    _mock_conn(
        monkeypatch,
        fetchall=[
            {
                "team_id": 1,
                "sport": "Футбол",
                "team": "К1",
                "coach_id": 1,
                "coach_first_name": "Иван",
                "coach_last_name": "Иванов",
            }
        ],
    )
    monkeypatch.setattr(sp, "_fetch_team_criteria", lambda _cur, _tid: [])
    rows = sp.list_available_teams()
    assert rows[0]["coach"] == "Иванов Иван"


def test_apply_to_team_success(monkeypatch):
    cur, conn = _mock_conn(monkeypatch)
    cur.fetchone.side_effect = [{"?column?": 1}, {"id": 10}]
    app_id = sp.apply_to_team(1, 2)
    assert app_id == 10
    conn.commit.assert_called()


def test_apply_to_team_closed(monkeypatch):
    _mock_conn(monkeypatch, fetchone=None)
    with pytest.raises(ValueError, match="не найдена"):
        sp.apply_to_team(99, 2)


def test_list_my_team_applications(monkeypatch):
    _mock_conn(
        monkeypatch,
        fetchall=[
            {
                "application_id": 1,
                "status": "pending",
                "created_at": None,
                "team_id": 1,
                "team": "К1",
                "sport": "Футбол",
                "coach_id": 1,
                "coach_first_name": "A",
                "coach_last_name": "B",
            }
        ],
    )
    apps = sp.list_my_team_applications(2)
    assert apps[0]["status"] == "pending"


def test_search_sportsmen(monkeypatch):
    _mock_conn(
        monkeypatch,
        fetchall=[
            {
                "athlete_user_id": 2,
                "last_name": "Петров",
                "first_name": "Пётр",
                "patronymic": None,
                "email": "p@t.com",
            }
        ],
    )
    rows = sp.search_sportsmen("Петр")
    assert rows[0]["full_name"] == "Петров Пётр"


def test_get_all_users(monkeypatch):
    _mock_conn(monkeypatch, fetchall=[{"id": 1, "email": "a@b.com"}])
    assert len(sp.get_all_users()) == 1


def test_fetch_athlete_skills_with_ratings(monkeypatch):
    cur, _conn = _mock_conn(
        monkeypatch,
        fetchall=[{"name": "Скорость", "rating": 8}, {"name": "Пас", "rating": None}],
    )
    rows = sp._fetch_athlete_skills_with_ratings(cur, 2)
    assert rows == [{"name": "Скорость", "rating": 8}, {"name": "Пас", "rating": None}]


def test_list_coach_applications(monkeypatch):
    app_row = {
        "application_id": 5,
        "status": "pending",
        "created_at": None,
        "athlete_user_id": 2,
        "team_id": 1,
        "team": "Dream",
        "sport": "Футбол",
        "email": "a@b.com",
        "last_name": "Иванов",
        "first_name": "Иван",
        "patronymic": None,
        "phone": "+7",
    }
    cur, _conn = _mock_conn(monkeypatch)
    cur.fetchall.side_effect = [[app_row], [{"name": "Скорость", "rating": 7}]]
    rows = sp.list_coach_applications(1, status="pending")
    assert rows[0]["full_name"] == "Иванов Иван"
    assert rows[0]["skills"][0]["rating"] == 7


def test_get_coach_team_detail(monkeypatch):
    cur, conn = _mock_conn(monkeypatch)
    cur.fetchone.return_value = {"team_id": 1, "team": "Dream", "sport": "Футбол"}
    monkeypatch.setattr(
        sp,
        "_fetch_team_members",
        lambda _c, _t, _coach: [
            {
                "member_id": 10,
                "athlete_user_id": 2,
                "full_name": "A B",
                "score": 8.0,
                "athlete_score": 7.5,
                "qualities": [],
                "notes": "",
            }
        ],
    )
    monkeypatch.setattr(sp, "_fetch_team_criteria", lambda _c, _t: [])
    detail = sp.get_coach_team_detail(1, 1)
    assert detail["team"] == "Dream"
    assert detail["members"][0]["full_name"] == "A B"
    conn.commit.assert_called()


def test_validate_quality_rating():
    assert sp._validate_quality_rating(None) is None
    assert sp._validate_quality_rating(5) == 5
    with pytest.raises(ValueError, match="1 до 10"):
        sp._validate_quality_rating(11)


def test_remove_team_member(monkeypatch):
    cur, conn = _mock_conn(monkeypatch, rowcount=1)
    cur.fetchone.return_value = {"team_id": 1, "team": "T", "sport": "S"}
    sp.remove_team_member(1, 1, 5)
    conn.commit.assert_called()


def test_compute_member_score():
    qualities = [{"rating": 8}, {"rating": 6}, {"rating": None}]
    assert sp._compute_member_score(qualities) == 7.0
    assert sp._compute_member_score([]) is None
