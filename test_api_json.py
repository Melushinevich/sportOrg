import json
import uuid
import sys
import os
import pytest

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def api_client():
    """Создаёт тестовый клиент для API (чёрный ящик)"""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SPORTORG_DB_HOST", raising=False)

    # Импортируем из правильного места
    from user_registration.app import create_app
    app = create_app(testing=True)
    return app.test_client()


@pytest.fixture
def authenticated_client(api_client):
    """Создаёт авторизованного тестового клиента"""
    email = f"auth_user_{uuid.uuid4().hex[:8]}@example.com"

    # Регистрация
    response = api_client.post(
        "/api/v1/register",
        data=json.dumps({
            "first_name": "Вася",
            "last_name": "Коров",
            "email": email,
            "password": "123456789",
            "password2": "123456789",
            "role": "sportsman"
        }),
        content_type="application/json"
    )

    # Проверяем, что регистрация прошла успешно
    assert response.status_code == 201, f"Registration failed: {response.get_data(as_text=True)}"

    # Логин
    login_response = api_client.post(
        "/api/v1/login",
        data=json.dumps({
            "email": email,
            "password": "123456789"
        }),
        content_type="application/json"
    )

    assert login_response.status_code == 200, f"Login failed: {login_response.get_data(as_text=True)}"

    return api_client


def test_health_endpoint_returns_ok(api_client):
    """
    Тест: эндпоинт /api/v1/health работает и возвращает {'status': 'ok'}
    """
    response = api_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_successful_user_registration(api_client):
    """
    Тест: успешная регистрации пользователя
    """
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"

    response = api_client.post(
        "/api/v1/register",
        data=json.dumps({
            "first_name": "Брат",
            "last_name": "Ложкин",
            "email": email,
            "password": "1234567890",
            "password2": "1234567890",
            "role": "sportsman"
        }),
        content_type="application/json"
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["email"] == email
    assert data["role"] == "sportsman"
    assert "user_id" in data
    assert isinstance(data["user_id"], int)


def test_cannot_register_with_same_email_twice(api_client):
    """
    Тест: нельзя зарегистрироваться с одинаковым email дважды
    """
    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
    user_data = {
        "first_name": "Вася",
        "last_name": "Ложкин",
        "email": email,
        "password": "123456789",
        "password2": "123456789",
        "role": "sportsman"
    }

    response1 = api_client.post(
        "/api/v1/register",
        data=json.dumps(user_data),
        content_type="application/json"
    )
    assert response1.status_code == 201

    response2 = api_client.post(
        "/api/v1/register",
        data=json.dumps(user_data),
        content_type="application/json"
    )
    assert response2.status_code == 409
    error_data = response2.get_json()
    assert error_data["code"] == "email_already_exists"


def test_successful_user_login(api_client):
    """
    Тест успешного входа пользователя
    """
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"

    api_client.post(
        "/api/v1/register",
        data=json.dumps({
            "first_name": "Вася",
            "last_name": "Ложкин",
            "email": email,
            "password": "123456789",
            "password2": "123456789",
            "role": "sportsman"
        }),
        content_type="application/json"
    )

    response = api_client.post(
        "/api/v1/login",
        data=json.dumps({
            "email": email,
            "password": "123456789"
        }),
        content_type="application/json"
    )

    assert response.status_code == 200
    user_data = response.get_json()["user"]
    assert user_data["email"] == email
    assert "password_hash" not in user_data


def test_login_fails_with_wrong_password(api_client):
    """
    Тест: вход с неверным паролем, должен вернуть ошибку
    """
    email = f"wrongpass_{uuid.uuid4().hex[:8]}@example.com"

    api_client.post(
        "/api/v1/register",
        data=json.dumps({
            "first_name": "Вася",
            "last_name": "Ложкин",
            "email": email,
            "password": "123456789",
            "password2": "123456789",
            "role": "sportsman"
        }),
        content_type="application/json"
    )

    response = api_client.post(
        "/api/v1/login",
        data=json.dumps({
            "email": email,
            "password": "987654321"
        }),
        content_type="application/json"
    )

    assert response.status_code == 401


def test_register_rejects_non_json_request(api_client):
    """
    Тест: регистрация требует JSON-формат
    """
    response = api_client.post(
        "/api/v1/register",
        data="это не json",
        content_type="text/plain"
    )
    assert response.status_code == 415


def test_register_rejects_missing_fields(api_client):
    """
    Тест: регистрация требует обязательные поля
    """
    response = api_client.post(
        "/api/v1/register",
        data=json.dumps({
            "email": "vasya@example.com",
            "password": "123456789"
        }),
        content_type="application/json"
    )

    assert response.status_code == 400


def test_users_can_have_different_roles(api_client):
    """
    Тест: пользователи могут регистрироваться с разными ролями
    """
    roles = ["sportsman", "coach"]

    for role in roles:
        email = f"{role}_{uuid.uuid4().hex[:8]}@example.com"
        response = api_client.post(
            "/api/v1/register",
            data=json.dumps({
                "first_name": "Вася",
                "last_name": "Ложкин",
                "email": email,
                "password": "123456789",
                "password2": "123456789",
                "role": role
            }),
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["role"] == role


def test_team_creation_requires_auth(api_client):
    """
    Тест: создание команды требует авторизации
    """
    response = api_client.post(
        "/api/v1/teams",
        data=json.dumps({
            "name": "ИВТ",
            "sport_type": "Ринго"
        }),
        content_type="application/json"
    )

    assert response.status_code == 401


def test_get_teams_list_works(api_client):
    """
    Тест: получение списка команд работает
    """
    response = api_client.get("/api/v1/teams?page=1&per_page=5")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "pagination" in data


def test_application_requires_auth(api_client):
    """
    Тест: подача заявки требует авторизации
    """
    response = api_client.post(
        "/api/v1/applications",
        data=json.dumps({
            "team_ids": [1],
            "comment": "Тест"
        }),
        content_type="application/json"
    )

    assert response.status_code == 401


def test_application_rejects_empty_team_list(authenticated_client):
    """
    Тест: заявка с пустым списком команд возвращает ошибку 400
    """
    response = authenticated_client.post(
        "/api/v1/applications",
        data=json.dumps({
            "team_ids": [],
            "comment": "Тестовая заявка"
        }),
        content_type="application/json"
    )

    assert response.status_code == 400
    error_data = response.get_json()
    assert "error" in error_data

#
# def test_application_accepts_valid_team_list(authenticated_client):
#     """Тест: заявка с непустым списком команд принимается"""
#     pytest.skip("Для этого теста нужно создать реальную команду в БД")