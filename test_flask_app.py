import uuid
import pytest
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent  # поднимаемся из tests/ в корень
sys.path.insert(0, str(project_root))


@pytest.fixture
def client(tmp_path):

    from user_registration.app import create_app

    app = create_app(testing=True)


    templates_path = project_root / "templates"
    if templates_path.exists():
        app.template_folder = str(templates_path)

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Отключаем CSRF для тестов

    # Создаем клиент
    client = app.test_client()


    with app.app_context():

        from user_registration import storage
        if hasattr(storage, 'init_db'):
            storage.init_db()

    yield client


def test_register_page_renders_black_box(client):
    """
    Тест: Проверяем, что страница регистрации открывается
    """
    response = client.get("/")

    assert response.status_code == 200

    html_text = response.get_data(as_text=True)
    assert "Регистрация" in html_text
    assert 'name="first_name"' in html_text


def test_register_post_success_black_box(client):
    """
    Тест: Проверяем, что регистрация работает
    """
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/register",
        data={
            "first_name": "Вася",
            "last_name": "Ложкин",
            "email": unique_email,
            "password": "123456789",
            "password2": "123456789",
            "role": "coach",
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    response_text = response.get_data(as_text=True)
    assert "Регистрация прошла успешно" in response_text
    assert "coach" in response_text


def test_register_post_password_mismatch_black_box(client):
    """
    Тест: Проверяем, что при разных паролях регистрация не проходит
    """
    response = client.post(
        "/register",
        data={
            "first_name": "Вася",
            "last_name": "Ложкин",
            "email": "test@example.com",
            "password": "123456789",
            "password2": "1234567890",
            "role": "coach",
        },
        follow_redirects=True
    )

    response_text = response.get_data(as_text=True)
    assert "Пароли не совпадают" in response_text or "ошибка" in response_text.lower()


def test_register_post_duplicate_email_black_box(client):
    """
    Тест: Проверяем, что email уже занят и регистрация не проходит
    """
    same_email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"

    # Первая регистрация (успешная)
    first_response = client.post(
        "/register",
        data={
            "first_name": "Вася",
            "last_name": "Ложкин",
            "email": same_email,
            "password": "123456789",
            "password2": "123456789",
            "role": "athlete",
        },
        follow_redirects=True
    )
    assert first_response.status_code == 200

    # Вторая регистрация (с тем же email) - должна выдать ошибку
    second_response = client.post(
        "/register",
        data={
            "first_name": "Брат",
            "last_name": "Ложкин",
            "email": same_email,
            "password": "123456789",
            "password2": "123456789",
            "role": "athlete",
        },
        follow_redirects=True
    )

    second_text = second_response.get_data(as_text=True)
    assert second_response.status_code == 200
    assert "Регистрация прошла успешно" not in second_text


def test_register_post_missing_fields_black_box(client):
    """
    Тест: Проверяем заполнение обязательных полей
    """
    response = client.post(
        "/register",
        data={
            "last_name": "Ложкин",
            "email": "test@example.com",
            "password": "123456789",
            "password2": "123456789",
            "role": "coach",
        },
        follow_redirects=True
    )

    response_text = response.get_data(as_text=True)
    assert "Регистрация прошла успешно" not in response_text