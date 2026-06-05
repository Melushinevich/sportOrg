"""Слой хранения: только PostgreSQL (см. storage_postgres)."""

from user_registration.storage_postgres import (
    add_athlete_skill,
    apply_to_team,
    create_new_user,
    create_team,
    ensure_sport,
    get_all_users,
    get_db_connection,
    get_user_by_email,
    get_user_by_id,
    init_db,
    list_available_teams,
    list_athlete_skills,
    list_my_team_applications,
    replace_athlete_skills,
)

__all__ = (
    "add_athlete_skill",
    "apply_to_team",
    "create_new_user",
    "create_team",
    "ensure_sport",
    "get_all_users",
    "get_db_connection",
    "get_user_by_email",
    "get_user_by_id",
    "init_db",
    "list_available_teams",
    "list_athlete_skills",
    "list_my_team_applications",
    "replace_athlete_skills",
)
