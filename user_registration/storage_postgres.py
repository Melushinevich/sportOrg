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
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sports (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) UNIQUE NOT NULL
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sports_name ON sports(name)")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS teams (
                    id SERIAL PRIMARY KEY,
                    sport_id INTEGER NOT NULL REFERENCES sports(id) ON DELETE RESTRICT,
                    name VARCHAR(200) NOT NULL,
                    coach_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    is_open BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_teams_sport ON teams(sport_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_teams_open ON teams(is_open)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_teams_coach ON teams(coach_user_id)")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS team_applications (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
                    athlete_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(team_id, athlete_user_id)
                );
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_team_apps_athlete ON team_applications(athlete_user_id)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_team_apps_team ON team_applications(team_id)"
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


def ensure_sport(name: str) -> int:
    n = (name or "").strip()
    if not n:
        raise ValueError("Название вида спорта обязательно")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sports(name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """,
                (n,),
            )
            row = cur.fetchone()
            if row and row.get("id") is not None:
                conn.commit()
                return int(row["id"])

            cur.execute("SELECT id FROM sports WHERE name = %s LIMIT 1", (n,))
            row2 = cur.fetchone()
            if not row2:
                raise RuntimeError("Не удалось создать вид спорта")
        conn.commit()
        return int(row2["id"])
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_team(coach_user_id: int, sport_name: str, team_name: str) -> int:
    sport_id = ensure_sport(sport_name)
    tn = (team_name or "").strip()
    if not tn:
        raise ValueError("Название команды обязательно")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO teams (sport_id, name, coach_user_id, is_open)
                VALUES (%s, %s, %s, TRUE)
                RETURNING id
                """,
                (sport_id, tn, coach_user_id),
            )
            row = cur.fetchone()
        conn.commit()
        return int(row["id"])
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_available_teams(sport_name: str | None = None) -> list[dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if sport_name:
                cur.execute(
                    """
                    SELECT
                        t.id AS team_id,
                        s.name AS sport,
                        t.name AS team,
                        u.id AS coach_id,
                        p.first_name AS coach_first_name,
                        p.last_name AS coach_last_name
                    FROM teams t
                    JOIN sports s ON s.id = t.sport_id
                    JOIN users u ON u.id = t.coach_user_id
                    LEFT JOIN profiles p ON p.user_id = u.id
                    WHERE t.is_open = TRUE AND s.name = %s
                    ORDER BY s.name, t.id
                    """,
                    ((sport_name or "").strip(),),
                )
            else:
                cur.execute(
                    """
                    SELECT
                        t.id AS team_id,
                        s.name AS sport,
                        t.name AS team,
                        u.id AS coach_id,
                        p.first_name AS coach_first_name,
                        p.last_name AS coach_last_name
                    FROM teams t
                    JOIN sports s ON s.id = t.sport_id
                    JOIN users u ON u.id = t.coach_user_id
                    LEFT JOIN profiles p ON p.user_id = u.id
                    WHERE t.is_open = TRUE
                    ORDER BY s.name, t.id
                    """
                )
            rows = cur.fetchall()
            out: list[dict[str, Any]] = []
            for r in rows:
                coach_name = " ".join(
                    x
                    for x in [r.get("coach_last_name") or "", r.get("coach_first_name") or ""]
                    if x
                ).strip()
                out.append(
                    {
                        "team_id": int(r["team_id"]),
                        "sport": r["sport"],
                        "team": r["team"],
                        "coach_id": int(r["coach_id"]),
                        "coach": coach_name or None,
                    }
                )
            return out
    finally:
        conn.close()


def apply_to_team(team_id: int, athlete_user_id: int) -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM teams WHERE id = %s AND is_open = TRUE LIMIT 1",
                (team_id,),
            )
            if cur.fetchone() is None:
                raise ValueError("Команда не найдена или набор закрыт")
            cur.execute(
                """
                INSERT INTO team_applications (team_id, athlete_user_id, status)
                VALUES (%s, %s, 'pending')
                RETURNING id
                """,
                (team_id, athlete_user_id),
            )
            row = cur.fetchone()
        conn.commit()
        return int(row["id"])
    except psycopg.errors.UniqueViolation as exc:  # type: ignore[attr-defined]
        conn.rollback()
        raise ValueError("Заявка уже подана") from exc
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_my_team_applications(athlete_user_id: int) -> list[dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    a.id AS application_id,
                    a.status,
                    a.created_at,
                    t.id AS team_id,
                    t.name AS team,
                    s.name AS sport,
                    u.id AS coach_id,
                    p.first_name AS coach_first_name,
                    p.last_name AS coach_last_name
                FROM team_applications a
                JOIN teams t ON t.id = a.team_id
                JOIN sports s ON s.id = t.sport_id
                JOIN users u ON u.id = t.coach_user_id
                LEFT JOIN profiles p ON p.user_id = u.id
                WHERE a.athlete_user_id = %s
                ORDER BY a.created_at DESC, a.id DESC
                """,
                (athlete_user_id,),
            )
            rows = cur.fetchall()
            out: list[dict[str, Any]] = []
            for r in rows:
                coach_name = " ".join(
                    x
                    for x in [r.get("coach_last_name") or "", r.get("coach_first_name") or ""]
                    if x
                ).strip()
                out.append(
                    {
                        "application_id": int(r["application_id"]),
                        "status": r["status"],
                        "team_id": int(r["team_id"]),
                        "team": r["team"],
                        "sport": r["sport"],
                        "coach_id": int(r["coach_id"]),
                        "coach": coach_name or None,
                        "created_at": r["created_at"],
                    }
                )
            return out
    finally:
        conn.close()
