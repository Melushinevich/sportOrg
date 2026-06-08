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
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS team_members (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
                    athlete_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(team_id, athlete_user_id)
                );
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_team_members_athlete ON team_members(athlete_user_id)"
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS team_member_qualities (
                    id SERIAL PRIMARY KEY,
                    team_member_id INTEGER NOT NULL REFERENCES team_members(id) ON DELETE CASCADE,
                    name VARCHAR(200) NOT NULL DEFAULT '',
                    rating INTEGER,
                    sort_order INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_tmq_member ON team_member_qualities(team_member_id)"
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS team_criteria (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
                    text VARCHAR(300) NOT NULL DEFAULT '',
                    sort_order INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_team_criteria_team ON team_criteria(team_id)"
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


MAX_TEAM_CRITERIA = 20
MAX_CRITERION_LEN = 300


def _normalize_criteria(criteria: list[Any] | None) -> list[str]:
    if not criteria:
        return []
    if not isinstance(criteria, list):
        raise ValueError("criteria должен быть массивом строк")
    if len(criteria) > MAX_TEAM_CRITERIA:
        raise ValueError(f"Не больше {MAX_TEAM_CRITERIA} критериев")
    out: list[str] = []
    for i, item in enumerate(criteria):
        text = (str(item) if item is not None else "").strip()
        if not text:
            raise ValueError(f"criteria[{i}] не может быть пустым")
        if len(text) > MAX_CRITERION_LEN:
            raise ValueError(f"criteria[{i}]: не больше {MAX_CRITERION_LEN} символов")
        out.append(text)
    return out


def _insert_team_criteria(cur, team_id: int, criteria: list[str]) -> None:
    for i, text in enumerate(criteria):
        cur.execute(
            """
            INSERT INTO team_criteria (team_id, text, sort_order)
            VALUES (%s, %s, %s)
            """,
            (team_id, text, i),
        )


def _fetch_team_criteria(cur, team_id: int) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT id AS criterion_id, text, sort_order
        FROM team_criteria
        WHERE team_id = %s
        ORDER BY sort_order ASC, id ASC
        """,
        (team_id,),
    )
    return [
        {
            "criterion_id": int(r["criterion_id"]),
            "text": r.get("text") or "",
            "sort_order": int(r["sort_order"]),
        }
        for r in cur.fetchall()
    ]


def create_team(
    coach_user_id: int,
    sport_name: str,
    team_name: str,
    criteria: list[Any] | None = None,
) -> int:
    sport_id = ensure_sport(sport_name)
    tn = (team_name or "").strip()
    if not tn:
        raise ValueError("Название команды обязательно")
    crits = _normalize_criteria(criteria)
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
            team_id = int(row["id"])
            _insert_team_criteria(cur, team_id, crits)
        conn.commit()
        return team_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_available_team_detail(team_id: int) -> dict[str, Any] | None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    t.id AS team_id,
                    t.name AS team,
                    s.name AS sport,
                    u.id AS coach_id,
                    p.first_name AS coach_first_name,
                    p.last_name AS coach_last_name
                FROM teams t
                JOIN sports s ON s.id = t.sport_id
                JOIN users u ON u.id = t.coach_user_id
                LEFT JOIN profiles p ON p.user_id = u.id
                WHERE t.id = %s AND t.is_open = TRUE
                LIMIT 1
                """,
                (team_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            r = dict(row)
            coach_name = " ".join(
                x for x in [r.get("coach_last_name") or "", r.get("coach_first_name") or ""] if x
            ).strip()
            criteria = _fetch_team_criteria(cur, team_id)
        return {
            "team_id": int(r["team_id"]),
            "sport": r["sport"],
            "team": r["team"],
            "coach_id": int(r["coach_id"]),
            "coach": coach_name or None,
            "criteria": criteria,
        }
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
                row = dict(r)
                coach_name = " ".join(
                    x
                    for x in [row.get("coach_last_name") or "", row.get("coach_first_name") or ""]
                    if x
                ).strip()
                team_id = int(row["team_id"])
                out.append(
                    {
                        "team_id": team_id,
                        "sport": row["sport"],
                        "team": row["team"],
                        "coach_id": int(row["coach_id"]),
                        "coach": coach_name or None,
                        "criteria": _fetch_team_criteria(cur, team_id),
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


def _format_full_name(
    last_name: str | None,
    first_name: str | None,
    patronymic: str | None = None,
) -> str | None:
    parts = [last_name or "", first_name or "", patronymic or ""]
    name = " ".join(x for x in parts if x).strip()
    return name or None


def _compute_member_score(qualities: list[dict[str, Any]]) -> float | None:
    """Средний балл: сумма оценок качеств / количество качеств с оценкой."""
    rated = [int(q["rating"]) for q in qualities if q.get("rating") is not None]
    if not rated:
        return None
    return round(sum(rated) / len(rated), 1)


def _fetch_member_qualities(cur, member_id: int) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT id AS quality_id, name, rating, sort_order
        FROM team_member_qualities
        WHERE team_member_id = %s
        ORDER BY sort_order ASC, id ASC
        """,
        (member_id,),
    )
    return [
        {
            "quality_id": int(r["quality_id"]),
            "name": r.get("name") or "",
            "rating": r.get("rating"),
            "sort_order": int(r["sort_order"]),
        }
        for r in cur.fetchall()
    ]


def _member_row_to_dict(row: dict[str, Any], qualities: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "member_id": int(row["member_id"]),
        "athlete_user_id": int(row["athlete_user_id"]),
        "full_name": _format_full_name(
            row.get("last_name"),
            row.get("first_name"),
            row.get("patronymic"),
        ),
        "score": _compute_member_score(qualities),
        "qualities": qualities,
        "notes": row.get("notes") or "",
    }


def _seed_member_qualities_from_athlete(cur, member_id: int, athlete_user_id: int) -> None:
    cur.execute(
        """
        INSERT INTO team_member_qualities (team_member_id, name, rating, sort_order)
        SELECT %s, name, rating, sort_order
        FROM athlete_skills
        WHERE user_id = %s
        ORDER BY sort_order ASC, id ASC
        """,
        (member_id, athlete_user_id),
    )


def _fetch_team_members(cur, team_id: int) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT
            m.id AS member_id,
            m.athlete_user_id,
            m.notes,
            p.last_name,
            p.first_name,
            p.patronymic
        FROM team_members m
        JOIN users u ON u.id = m.athlete_user_id
        LEFT JOIN profiles p ON p.user_id = u.id
        WHERE m.team_id = %s
        ORDER BY m.id ASC
        """,
        (team_id,),
    )
    out: list[dict[str, Any]] = []
    for r in cur.fetchall():
        row = dict(r)
        member_id = int(row["member_id"])
        qualities = _fetch_member_qualities(cur, member_id)
        out.append(_member_row_to_dict(row, qualities))
    return out


def _require_coach_team(cur, coach_user_id: int, team_id: int) -> dict[str, Any]:
    cur.execute(
        """
        SELECT t.id AS team_id, t.name AS team, t.is_open, s.name AS sport
        FROM teams t
        JOIN sports s ON s.id = t.sport_id
        WHERE t.id = %s AND t.coach_user_id = %s
        LIMIT 1
        """,
        (team_id, coach_user_id),
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError("Команда не найдена")
    return dict(row)


def list_coach_teams(coach_user_id: int) -> list[dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT t.id AS team_id, t.name AS team, s.name AS sport
                FROM teams t
                JOIN sports s ON s.id = t.sport_id
                WHERE t.coach_user_id = %s
                ORDER BY t.id DESC
                """,
                (coach_user_id,),
            )
            rows = cur.fetchall()
            return [
                {
                    "team_id": int(r["team_id"]),
                    "team": r["team"],
                    "sport": r["sport"],
                }
                for r in rows
            ]
    finally:
        conn.close()


def get_coach_team_detail(coach_user_id: int, team_id: int) -> dict[str, Any]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            team = _require_coach_team(cur, coach_user_id, team_id)
            members = _fetch_team_members(cur, team_id)
            criteria = _fetch_team_criteria(cur, team_id)
        return {
            "team_id": int(team["team_id"]),
            "team": team["team"],
            "sport": team["sport"],
            "is_open": bool(team["is_open"]),
            "criteria": criteria,
            "members": members,
        }
    finally:
        conn.close()


def add_team_member(coach_user_id: int, team_id: int, athlete_user_id: int) -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            _require_coach_team(cur, coach_user_id, team_id)
            cur.execute(
                "SELECT role FROM users WHERE id = %s LIMIT 1",
                (athlete_user_id,),
            )
            athlete = cur.fetchone()
            if athlete is None:
                raise ValueError("Спортсмен не найден")
            if (athlete.get("role") or "").lower() != "sportsman":
                raise ValueError("В состав можно добавить только спортсмена")
            cur.execute(
                """
                INSERT INTO team_members (team_id, athlete_user_id)
                VALUES (%s, %s)
                RETURNING id
                """,
                (team_id, athlete_user_id),
            )
            row = cur.fetchone()
            member_id = int(row["id"])
            _seed_member_qualities_from_athlete(cur, member_id, athlete_user_id)
        conn.commit()
        return member_id
    except psycopg.errors.UniqueViolation as exc:  # type: ignore[attr-defined]
        conn.rollback()
        raise ValueError("Спортсмен уже в составе") from exc
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def remove_team_member(coach_user_id: int, team_id: int, member_id: int) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            _require_coach_team(cur, coach_user_id, team_id)
            cur.execute(
                """
                DELETE FROM team_members
                WHERE id = %s AND team_id = %s
                """,
                (member_id, team_id),
            )
            if cur.rowcount == 0:
                raise ValueError("Участник не найден")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _validate_quality_rating(rating: Any) -> int | None:
    if rating is None or rating == "":
        return None
    try:
        v = int(rating)
    except (TypeError, ValueError) as exc:
        raise ValueError("Оценка качества должна быть числом или null") from exc
    if v < 1 or v > 10:
        raise ValueError("Оценка качества: от 1 до 10 или пусто")
    return v


def save_team_members(
    coach_user_id: int,
    team_id: int,
    members: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            _require_coach_team(cur, coach_user_id, team_id)
            for i, item in enumerate(members):
                if not isinstance(item, dict):
                    raise ValueError(f"members[{i}] должен быть объектом")
                member_id = item.get("member_id")
                if member_id is None:
                    raise ValueError(f"members[{i}]: нужен member_id")
                member_id = int(member_id)
                cur.execute(
                    "SELECT 1 FROM team_members WHERE id = %s AND team_id = %s LIMIT 1",
                    (member_id, team_id),
                )
                if cur.fetchone() is None:
                    raise ValueError(f"Участник member_id={member_id} не найден в команде")

                notes = (item.get("notes") or "").strip()
                cur.execute(
                    "UPDATE team_members SET notes = %s WHERE id = %s AND team_id = %s",
                    (notes, member_id, team_id),
                )

                qualities = item.get("qualities")
                if qualities is None:
                    continue
                if not isinstance(qualities, list):
                    raise ValueError(f"members[{i}].qualities должен быть массивом")

                for j, q in enumerate(qualities):
                    if not isinstance(q, dict):
                        raise ValueError(f"members[{i}].qualities[{j}] должен быть объектом")
                    quality_id = q.get("quality_id")
                    if quality_id is None:
                        raise ValueError(f"members[{i}].qualities[{j}]: нужен quality_id")
                    rating = _validate_quality_rating(q.get("rating", None))
                    name = q.get("name")
                    if name is not None:
                        name = str(name).strip()
                        if len(name) > 200:
                            raise ValueError("Название качества: не больше 200 символов")
                        cur.execute(
                            """
                            UPDATE team_member_qualities
                            SET rating = %s, name = %s
                            WHERE id = %s AND team_member_id = %s
                            """,
                            (rating, name, int(quality_id), member_id),
                        )
                    else:
                        cur.execute(
                            """
                            UPDATE team_member_qualities
                            SET rating = %s
                            WHERE id = %s AND team_member_id = %s
                            """,
                            (rating, int(quality_id), member_id),
                        )
                    if cur.rowcount == 0:
                        raise ValueError(
                            f"Качество quality_id={quality_id} не найдено у участника {member_id}"
                        )

            saved = _fetch_team_members(cur, team_id)
        conn.commit()
        return saved
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def finalize_team_roster(coach_user_id: int, team_id: int) -> dict[str, Any]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            _require_coach_team(cur, coach_user_id, team_id)
            cur.execute(
                "UPDATE teams SET is_open = FALSE WHERE id = %s",
                (team_id,),
            )
            team = _require_coach_team(cur, coach_user_id, team_id)
            members = _fetch_team_members(cur, team_id)
        conn.commit()
        return {
            "team_id": int(team["team_id"]),
            "team": team["team"],
            "sport": team["sport"],
            "is_open": bool(team["is_open"]),
            "members": members,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def search_sportsmen(query: str, *, limit: int = 20) -> list[dict[str, Any]]:
    q = (query or "").strip()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if q:
                pattern = f"%{q}%"
                cur.execute(
                    """
                    SELECT u.id AS athlete_user_id, p.last_name, p.first_name, p.patronymic, u.email
                    FROM users u
                    LEFT JOIN profiles p ON p.user_id = u.id
                    WHERE u.role = 'sportsman'
                      AND (
                        u.email ILIKE %s
                        OR p.last_name ILIKE %s
                        OR p.first_name ILIKE %s
                        OR p.patronymic ILIKE %s
                      )
                    ORDER BY p.last_name, p.first_name, u.id
                    LIMIT %s
                    """,
                    (pattern, pattern, pattern, pattern, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT u.id AS athlete_user_id, p.last_name, p.first_name, p.patronymic, u.email
                    FROM users u
                    LEFT JOIN profiles p ON p.user_id = u.id
                    WHERE u.role = 'sportsman'
                    ORDER BY p.last_name, p.first_name, u.id
                    LIMIT %s
                    """,
                    (limit,),
                )
            rows = cur.fetchall()
            return [
                {
                    "athlete_user_id": int(r["athlete_user_id"]),
                    "full_name": _format_full_name(
                        r.get("last_name"),
                        r.get("first_name"),
                        r.get("patronymic"),
                    ),
                    "email": r.get("email"),
                }
                for r in rows
            ]
    finally:
        conn.close()
