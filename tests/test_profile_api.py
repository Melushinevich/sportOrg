import json

import pytest

from tests.conftest import auth_header


@pytest.fixture
def profile_mocks(monkeypatch):
    state = {
        2: {
            "user_id": 2,
            "email": "athlete@test.local",
            "role": "sportsman",
            "last_name": None,
            "first_name": None,
            "patronymic": None,
            "birth_date": None,
            "phone": None,
            "city": None,
            "gender": None,
        },
        1: {
            "user_id": 1,
            "email": "coach@test.local",
            "role": "coach",
            "last_name": None,
            "first_name": None,
            "patronymic": None,
            "birth_date": None,
            "phone": None,
            "city": None,
            "gender": None,
        },
    }

    def get_profile(uid):
        return state.get(int(uid))

    def update_profile(uid, data):
        row = state[int(uid)]
        row.update(
            {
                "last_name": data["last_name"],
                "first_name": data["first_name"],
                "patronymic": data.get("patronymic"),
                "birth_date": data.get("birth_date").isoformat()
                if data.get("birth_date") is not None
                else None,
                "phone": data.get("phone"),
                "city": data.get("city"),
                "gender": data.get("gender"),
            }
        )
        return dict(row)

    monkeypatch.setattr("sportorg.api.profile.get_user_profile", get_profile)
    monkeypatch.setattr("sportorg.api.profile.update_user_profile", update_profile)
    return state


def test_profile_get_sportsman(app_client, users_db, profile_mocks):
    rv = app_client.get("/api/v1/me/profile", headers=auth_header(2, "sportsman"))
    assert rv.status_code == 200
    body = rv.get_json()
    assert body["profile"]["email"] == "athlete@test.local"


def test_profile_put_sportsman(app_client, users_db, profile_mocks):
    h = auth_header(2, "sportsman")
    rv = app_client.put(
        "/api/v1/me/profile",
        headers=h,
        data=json.dumps(
            {
                "last_name": "Иванов",
                "first_name": "Иван",
                "patronymic": "Иванович",
                "birth_date": "2000-05-15",
                "city": "Москва",
                "phone": "+79990001122",
                "gender": "Мужской",
            }
        ),
        content_type="application/json",
    )
    assert rv.status_code == 200
    profile = rv.get_json()["profile"]
    assert profile["last_name"] == "Иванов"
    assert profile["city"] == "Москва"
    assert profile["gender"] == "Мужской"


def test_profile_put_coach(app_client, users_db, profile_mocks):
    rv = app_client.put(
        "/api/v1/me/profile",
        headers=auth_header(1, "coach"),
        data=json.dumps({"last_name": "Петров", "first_name": "Пётр"}),
        content_type="application/json",
    )
    assert rv.status_code == 200
    assert rv.get_json()["profile"]["last_name"] == "Петров"


def test_profile_unauthorized(app_client, users_db, profile_mocks):
    rv = app_client.get("/api/v1/me/profile")
    assert rv.status_code == 401


def test_profile_invalid_birth_date(app_client, users_db, profile_mocks):
    rv = app_client.put(
        "/api/v1/me/profile",
        headers=auth_header(2, "sportsman"),
        data=json.dumps(
            {"last_name": "Иванов", "first_name": "Иван", "birth_date": "15.05.2000"}
        ),
        content_type="application/json",
    )
    assert rv.status_code == 400
    assert rv.get_json()["code"] == "invalid_birth_date"


def test_profile_future_birth_date(app_client, users_db, profile_mocks):
    rv = app_client.put(
        "/api/v1/me/profile",
        headers=auth_header(2, "sportsman"),
        data=json.dumps(
            {
                "last_name": "Иванов",
                "first_name": "Иван",
                "birth_date": "2099-01-01",
            }
        ),
        content_type="application/json",
    )
    assert rv.status_code == 400
    assert rv.get_json()["code"] == "invalid_birth_date"


def test_profile_invalid_gender(app_client, users_db, profile_mocks):
    rv = app_client.put(
        "/api/v1/me/profile",
        headers=auth_header(2, "sportsman"),
        data=json.dumps(
            {
                "last_name": "Иванов",
                "first_name": "Иван",
                "gender": "Other",
            }
        ),
        content_type="application/json",
    )
    assert rv.status_code == 400
    assert rv.get_json()["code"] == "invalid_gender"
