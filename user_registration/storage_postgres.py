import os
from typing import Any
from urllib.parse import quote_plus

import psycopg
from psycopg.rows import dict_row


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    host = os.environ.get("SPORTORG_DB_HOST")
    if not host:
        raise RuntimeError(
            "Задайте DATABASE_URL или SPORTORG_DB_HOST (и при необходимости "
            "SPORTORG_DB_PORT, SPORTORG_DB_NAME, SPORTORG_DB_USER, SPORTORG_DB_PASSWORD)."
        )
    port = int(os.environ.get("SPORTORG_DB_PORT", "5500"))
    name = os.environ.get("SPORTORG_DB_NAME", "postgres")
    user = os.environ.get("SPORTORG_DB_USER", "postgres")
    password = os.environ.get("SPORTORG_DB_PASSWORD", "12345678")
    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{quote_plus(name)}"
    )


def get_db_connection() -> psycopg.Connection[dict[str, Any]]:
    return psycopg.connect(_database_url(), row_factory=dict_row)


def init_db() -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    last_name VARCHAR(100) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    patronymic VARCHAR(100),
                    birth_date DATE,
                    phone VARCHAR(20),
                    city VARCHAR(100),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_profiles_last_name ON profiles(last_name)")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS athlete_skills (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(200) NOT NULL DEFAULT '',
                    rating INTEGER,
                    sort_order INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_athlete_skills_user ON athlete_skills(user_id)"
            )
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.email, u.password_hash, u.role, u.created_at,
                       p.last_name, p.first_name, p.patronymic,
                       p.birth_date, p.phone, p.city
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.email = %s
                LIMIT 1
                """,
                (email,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def create_new_user(user_data: dict) -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, password_hash, role)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    user_data.get("email"),
                    user_data.get("password_hash"),
                    user_data.get("role", "sportsman"),
                ),
            )
            user_id = cur.fetchone()["id"]

            cur.execute(
                """
                INSERT INTO profiles (user_id, last_name, first_name, patronymic,
                                      birth_date, phone, city)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    user_data.get("last_name"),
                    user_data.get("first_name"),
                    user_data.get("patronymic") or None,
                    user_data.get("birth_date") or None,
                    user_data.get("phone") or None,
                    user_data.get("city") or None,
                ),
            )
        conn.commit()
        return int(user_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_all_users():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.email, u.password_hash, u.role, u.created_at,
                       p.last_name, p.first_name, p.patronymic,
                       p.birth_date, p.phone, p.city
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                ORDER BY u.id
                """
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.email, u.password_hash, u.role, u.created_at,
                       p.last_name, p.first_name, p.patronymic,
                       p.birth_date, p.phone, p.city
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.id = %s
                LIMIT 1
                """,
                (user_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def list_athlete_skills(user_id: int) -> list[dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_id, name, rating, sort_order
                FROM athlete_skills
                WHERE user_id = %s
                ORDER BY sort_order ASC, id ASC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def add_athlete_skill(user_id: int, name: str = "") -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(sort_order), -1) + 1 AS next_sort FROM athlete_skills WHERE user_id = %s",
                (user_id,),
            )
            sort_order = int(cur.fetchone()["next_sort"])
            cur.execute(
                """
                INSERT INTO athlete_skills (user_id, name, rating, sort_order)
                VALUES (%s, %s, NULL, %s)
                RETURNING id
                """,
                (user_id, name.strip(), sort_order),
            )
            new_id = cur.fetchone()["id"]
        conn.commit()
        return int(new_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def replace_athlete_skills(user_id: int, skills: list[dict[str, Any]]) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM athlete_skills WHERE user_id = %s", (user_id,))
            for i, s in enumerate(skills):
                name = (s.get("name") or "").strip()
                rating = s.get("rating", None)
                if rating is not None:
                    rating = int(rating)
                cur.execute(
                    """
                    INSERT INTO athlete_skills (user_id, name, rating, sort_order)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, name, rating, i),
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
