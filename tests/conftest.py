import os

import pytest

from user_registration.storage import get_db_connection, init_db


def _apply_default_db_env() -> None:
    if os.environ.get("DATABASE_URL"):
        return
    os.environ.setdefault("SPORTORG_DB_HOST", "192.168.1.73")
    os.environ.setdefault("SPORTORG_DB_PORT", "5500")
    os.environ.setdefault("SPORTORG_DB_NAME", "postgres")
    os.environ.setdefault("SPORTORG_DB_USER", "postgres")
    os.environ.setdefault("SPORTORG_DB_PASSWORD", "12345678")


@pytest.fixture(scope="session")
def postgres_db():
    """Проверка доступности PostgreSQL; пропуск тестов, если БД недоступна."""
    _apply_default_db_env()
    try:
        init_db()
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        finally:
            conn.close()
    except Exception as exc:
        pytest.skip(f"PostgreSQL недоступен: {exc}")
    yield
