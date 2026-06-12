"""Сопоставление пола: UI (рус.) ↔ БД (male/female)."""

GENDER_UI_TO_DB = {
    "Мужской": "male",
    "Женский": "female",
}

GENDER_DB_TO_UI = {db: ui for ui, db in GENDER_UI_TO_DB.items()}

VALID_GENDER_UI = frozenset(GENDER_UI_TO_DB)
VALID_GENDER_DB = frozenset(GENDER_UI_TO_DB.values())


def gender_ui_to_db(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    text = str(value).strip()
    if text in GENDER_UI_TO_DB:
        return GENDER_UI_TO_DB[text]
    if text in VALID_GENDER_DB:
        return text
    raise ValueError("Укажите пол: Мужской или Женский")


def gender_db_to_ui(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    text = str(value).strip()
    return GENDER_DB_TO_UI.get(text, text)
