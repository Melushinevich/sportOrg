import os
import sqlite3
from typing import Any


# хранить БД рядом с этим модулем, чтобы путь был стабильным
DB_FILE = os.path.join(os.path.dirname(__file__), "users.db")


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None


def _sqlite_schema_incompatible(conn: sqlite3.Connection) -> bool:
    """Старая однотабличная схема или users без role — CREATE IF NOT EXISTS не обновит колонки."""
    if not _table_exists(conn, "users"):
        return False
    ucols = _table_columns(conn, "users")
    need_users = {"email", "password_hash", "role", "created_at"}
    if not need_users <= ucols:
        return True
    if not _table_exists(conn, "profiles"):
        return True
    pcols = _table_columns(conn, "profiles")
    need_profiles = {"user_id", "last_name", "first_name"}
    return not need_profiles <= pcols


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    if _sqlite_schema_incompatible(conn):
        cursor.execute("DROP TABLE IF EXISTS athlete_skills")
        cursor.execute("DROP TABLE IF EXISTS profiles")
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        print("бд sqlite: несовместимая схема — таблицы пересозданы (данные старых users сброшены)")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            patronymic TEXT,
            birth_date TEXT,
            phone TEXT,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_last_name ON profiles(last_name)")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS athlete_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            rating INTEGER,
            sort_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_athlete_skills_user ON athlete_skills(user_id)"
    )

    conn.commit()
    conn.close()
    print("бд инициализирована (sqlite)")


def _row_to_user_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "email": row["email"],
        "password_hash": row["password_hash"],
        "role": row["role"],
        "created_at": row["created_at"],
        "last_name": row["last_name"],
        "first_name": row["first_name"],
        "patronymic": row["patronymic"],
        "birth_date": row["birth_date"],
        "phone": row["phone"],
        "city": row["city"],
    }


def get_user_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT u.id, u.email, u.password_hash, u.role, u.created_at,
               p.last_name, p.first_name, p.patronymic,
               p.birth_date, p.phone, p.city
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE u.email = ?
        LIMIT 1
        """,
        (email,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return _row_to_user_dict(row)
    return None


def create_new_user(user_data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, role)
            VALUES (?, ?, ?)
            """,
            (
                user_data.get("email"),
                user_data.get("password_hash"),
                user_data.get("role", "sportsman"),
            ),
        )
        user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO profiles (user_id, last_name, first_name, patronymic,
                                  birth_date, phone, city)
            VALUES (?, ?, ?, ?, ?, ?, ?)
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


def get_all_users() -> list[dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.id, u.email, u.password_hash, u.role, u.created_at,
               p.last_name, p.first_name, p.patronymic,
               p.birth_date, p.phone, p.city
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        ORDER BY u.id
        """
    )
    rows = cursor.fetchall()
    conn.close()

    return [_row_to_user_dict(row) for row in rows]


def get_user_by_id(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.id, u.email, u.password_hash, u.role, u.created_at,
               p.last_name, p.first_name, p.patronymic,
               p.birth_date, p.phone, p.city
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE u.id = ?
        LIMIT 1
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return _row_to_user_dict(row) if row else None


def list_athlete_skills(user_id: int) -> list[dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, rating, sort_order
        FROM athlete_skills
        WHERE user_id = ?
        ORDER BY sort_order ASC, id ASC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "rating": r["rating"],
            "sort_order": r["sort_order"],
        }
        for r in rows
    ]


def add_athlete_skill(user_id: int, name: str = "") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 FROM athlete_skills WHERE user_id = ?",
            (user_id,),
        )
        sort_order = int(cursor.fetchone()[0])
        cursor.execute(
            """
            INSERT INTO athlete_skills (user_id, name, rating, sort_order)
            VALUES (?, ?, NULL, ?)
            """,
            (user_id, name.strip(), sort_order),
        )
        new_id = cursor.lastrowid
        conn.commit()
        return int(new_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def replace_athlete_skills(user_id: int, skills: list[dict[str, Any]]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM athlete_skills WHERE user_id = ?", (user_id,))
        for i, s in enumerate(skills):
            name = (s.get("name") or "").strip()
            rating = s.get("rating", None)
            if rating is not None:
                rating = int(rating)
            cursor.execute(
                """
                INSERT INTO athlete_skills (user_id, name, rating, sort_order)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, name, rating, i),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
