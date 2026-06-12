import os
from typing import Any
from urllib.parse import quote_plus

import psycopg
from psycopg.rows import dict_row

from user_registration.profile_gender import gender_db_to_ui, gender_ui_to_db


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
    return psycopg.connect(
        _database_url(),
        row_factory=dict_row,
        connect_timeout=int(os.environ.get("SPORTORG_DB_CONNECT_TIMEOUT", "10")),
    )


def init_db() -> None:
    """Проверка доступности БД. Схему не создаём — она настраивается отдельно."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
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
                       p.birth_date, p.phone, p.city, p.gender
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
                                      birth_date, phone, city, gender)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    (user_data.get("last_name") or "").strip(),
                    (user_data.get("first_name") or "").strip(),
                    user_data.get("patronymic") or None,
                    user_data.get("birth_date") or None,
                    user_data.get("phone") or None,
                    user_data.get("city") or None,
                    user_data.get("gender") or None,
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
                       p.birth_date, p.phone, p.city, p.gender
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
                       p.birth_date, p.phone, p.city, p.gender
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


def _profile_row_to_dict(row: dict) -> dict:
    birth = row.get("birth_date")
    if birth is not None and hasattr(birth, "isoformat"):
        birth = birth.isoformat()
    return {
        "user_id": row["id"],
        "email": row.get("email"),
        "role": row.get("role"),
        "last_name": row.get("last_name"),
        "first_name": row.get("first_name"),
        "patronymic": row.get("patronymic"),
        "birth_date": birth,
        "phone": row.get("phone"),
        "city": row.get("city"),
        "gender": gender_db_to_ui(row.get("gender")),
    }


def get_user_profile(user_id: int) -> dict | None:
    row = get_user_by_id(user_id)
    if row is None:
        return None
    return _profile_row_to_dict(row)


def update_user_profile(user_id: int, data: dict) -> dict:
    last_name = (data.get("last_name") or "").strip()
    first_name = (data.get("first_name") or "").strip()
    if not last_name or not first_name:
        raise ValueError("Фамилия и имя обязательны")

    patronymic = (data.get("patronymic") or "").strip() or None
    birth_date = data.get("birth_date") or None
    phone = (data.get("phone") or "").strip() or None
    city = (data.get("city") or "").strip() or None
    gender = gender_ui_to_db(data.get("gender"))

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE profiles
                SET last_name = %s,
                    first_name = %s,
                    patronymic = %s,
                    birth_date = %s,
                    phone = %s,
                    city = %s,
                    gender = %s,
                    updated_at = NOW()
                WHERE user_id = %s
                RETURNING user_id
                """,
                (
                    last_name,
                    first_name,
                    patronymic,
                    birth_date,
                    phone,
                    city,
                    gender,
                    user_id,
                ),
            )
            if cur.fetchone() is None:
                raise ValueError("Профиль не найден")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    profile = get_user_profile(user_id)
    if profile is None:
        raise ValueError("Профиль не найден")
    return profile


def _get_or_create_skill_id(cur, name: str) -> int:
    n = (name or "").strip()
    if not n:
        raise ValueError("Название скилла обязательно")
    cur.execute(
        """
        INSERT INTO skills (name, category)
        VALUES (%s, 'custom')
        ON CONFLICT (name) DO NOTHING
        RETURNING id
        """,
        (n,),
    )
    row = cur.fetchone()
    if row and row.get("id") is not None:
        return int(row["id"])
    cur.execute("SELECT id FROM skills WHERE name = %s LIMIT 1", (n,))
    row2 = cur.fetchone()
    if not row2:
        raise RuntimeError("Не удалось создать скилл в справочнике")
    return int(row2["id"])


def _sportsman_skill_row(row: dict[str, Any], sort_order: int) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "user_id": int(row["user_id"]),
        "name": row.get("name") or "",
        "rating": row.get("self_rating"),
        "sort_order": sort_order,
        "skill_id": int(row["skill_id"]),
    }


def list_athlete_skills(user_id: int) -> list[dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ss.id, ss.user_id, ss.skill_id, ss.self_rating, s.name
                FROM sportsman_skills ss
                JOIN skills s ON s.id = ss.skill_id
                WHERE ss.user_id = %s
                ORDER BY ss.id ASC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            return [_sportsman_skill_row(dict(r), i) for i, r in enumerate(rows)]
    finally:
        conn.close()


def add_athlete_skill(user_id: int, name: str = "") -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            skill_id = _get_or_create_skill_id(cur, name)
            cur.execute(
                """
                INSERT INTO sportsman_skills (user_id, skill_id, self_rating)
                VALUES (%s, %s, NULL)
                RETURNING id
                """,
                (user_id, skill_id),
            )
            new_id = cur.fetchone()["id"]
        conn.commit()
        return int(new_id)
    except psycopg.errors.UniqueViolation as exc:  # type: ignore[attr-defined]
        conn.rollback()
        raise ValueError("Такой скилл уже добавлен") from exc
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def replace_athlete_skills(user_id: int, skills: list[dict[str, Any]]) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sportsman_skills WHERE user_id = %s", (user_id,))
            for s in skills:
                name = (s.get("name") or "").strip()
                rating = s.get("rating", None)
                if rating is not None:
                    rating = int(rating)
                skill_id = _get_or_create_skill_id(cur, name)
                cur.execute(
                    """
                    INSERT INTO sportsman_skills (user_id, skill_id, self_rating)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, skill_id, rating),
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_sports() -> list[dict[str, Any]]:
    """Справочник видов спорта из таблицы sports."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id AS sport_id, name
                FROM sports
                ORDER BY name ASC
                """
            )
            return [
                {"sport_id": int(r["sport_id"]), "name": r.get("name") or ""}
                for r in cur.fetchall()
            ]
    finally:
        conn.close()


def list_skills_catalog() -> list[dict[str, Any]]:
    """Справочник навыков/критериев из таблицы skills."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id AS skill_id, name, category
                FROM skills
                ORDER BY name ASC
                """
            )
            return [
                {
                    "skill_id": int(r["skill_id"]),
                    "name": r.get("name") or "",
                    "category": r.get("category"),
                }
                for r in cur.fetchall()
            ]
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
                INSERT INTO teams (sport_id, name, coach_user_id, members_count)
                VALUES (%s, %s, %s, 0)
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
                WHERE t.id = %s
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
                    WHERE s.name = %s
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


def list_athlete_teams(athlete_user_id: int) -> list[dict[str, Any]]:
    """Команды, в состав которых спортсмена принял тренер (team_members)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m.id AS member_id,
                    t.id AS team_id,
                    t.name AS team,
                    s.name AS sport,
                    u.id AS coach_id,
                    p.first_name AS coach_first_name,
                    p.last_name AS coach_last_name
                FROM team_members m
                JOIN teams t ON t.id = m.team_id
                JOIN sports s ON s.id = t.sport_id
                JOIN users u ON u.id = t.coach_user_id
                LEFT JOIN profiles p ON p.user_id = u.id
                WHERE m.athlete_user_id = %s
                ORDER BY m.id DESC
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
                        "member_id": int(r["member_id"]),
                        "team_id": int(r["team_id"]),
                        "team": r.get("team") or "",
                        "sport": r.get("sport") or "",
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
                "SELECT 1 FROM teams WHERE id = %s LIMIT 1",
                (team_id,),
            )
            if cur.fetchone() is None:
                raise ValueError("Команда не найдена")
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


def _fetch_member_qualities(
    cur,
    coach_user_id: int,
    athlete_user_id: int,
) -> list[dict[str, Any]]:
    """Качества участника — оценки тренера из coach_assessments + справочник skills."""
    cur.execute(
        """
        SELECT ca.id AS quality_id, ca.skill_id, s.name, ca.rating
        FROM coach_assessments ca
        JOIN skills s ON s.id = ca.skill_id
        WHERE ca.coach_id = %s AND ca.sportsman_id = %s
        ORDER BY ca.id ASC
        """,
        (coach_user_id, athlete_user_id),
    )
    return [
        {
            "quality_id": int(r["quality_id"]),
            "skill_id": int(r["skill_id"]),
            "name": r.get("name") or "",
            "rating": r.get("rating"),
            "sort_order": i,
        }
        for i, r in enumerate(cur.fetchall())
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


def _seed_coach_assessments_from_athlete(
    cur,
    coach_user_id: int,
    athlete_user_id: int,
) -> None:
    """При добавлении в состав копируем самооценки спортсмена в coach_assessments."""
    cur.execute(
        """
        INSERT INTO coach_assessments (coach_id, sportsman_id, skill_id, rating)
        SELECT %s, %s, ss.skill_id, ss.self_rating
        FROM sportsman_skills ss
        WHERE ss.user_id = %s
          AND NOT EXISTS (
              SELECT 1 FROM coach_assessments ca
              WHERE ca.coach_id = %s
                AND ca.sportsman_id = %s
                AND ca.skill_id = ss.skill_id
          )
        """,
        (coach_user_id, athlete_user_id, athlete_user_id, coach_user_id, athlete_user_id),
    )


def _fetch_team_members(cur, team_id: int, coach_user_id: int) -> list[dict[str, Any]]:
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
        athlete_user_id = int(row["athlete_user_id"])
        qualities = _fetch_member_qualities(cur, coach_user_id, athlete_user_id)
        out.append(_member_row_to_dict(row, qualities))
    return out


def _require_coach_team(cur, coach_user_id: int, team_id: int) -> dict[str, Any]:
    cur.execute(
        """
        SELECT t.id AS team_id, t.name AS team, s.name AS sport
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
            members = _fetch_team_members(cur, team_id, coach_user_id)
            criteria = _fetch_team_criteria(cur, team_id)
        return {
            "team_id": int(team["team_id"]),
            "team": team["team"],
            "sport": team["sport"],
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
            _seed_coach_assessments_from_athlete(cur, coach_user_id, athlete_user_id)
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
                    """
                    SELECT athlete_user_id
                    FROM team_members
                    WHERE id = %s AND team_id = %s
                    LIMIT 1
                    """,
                    (member_id, team_id),
                )
                member_row = cur.fetchone()
                if member_row is None:
                    raise ValueError(f"Участник member_id={member_id} не найден в команде")
                athlete_user_id = int(member_row["athlete_user_id"])

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
                    cur.execute(
                        """
                        UPDATE coach_assessments
                        SET rating = %s, updated_at = NOW()
                        WHERE id = %s
                          AND coach_id = %s
                          AND sportsman_id = %s
                        """,
                        (rating, int(quality_id), coach_user_id, athlete_user_id),
                    )
                    if cur.rowcount == 0:
                        raise ValueError(
                            f"Оценка quality_id={quality_id} не найдена у участника {member_id}"
                        )

            saved = _fetch_team_members(cur, team_id, coach_user_id)
        conn.commit()
        return saved
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
