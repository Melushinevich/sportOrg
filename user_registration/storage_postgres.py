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
