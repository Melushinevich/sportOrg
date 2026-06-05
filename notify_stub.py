"""
Заглушка «подтверждение email»: без SMTP и без токенов в БД.
В проде сюда подключают очередь писем и хранение одноразового токена.
"""

import logging
import os
import secrets

log = logging.getLogger("sportorg.notify")


def log_verification_stub(email: str, user_id: int) -> None:
    token = secrets.token_urlsafe(24)
    base = os.environ.get("PUBLIC_APP_URL", "http://127.0.0.1:5000").rstrip("/")
    fake_link = f"{base}/verify-email?token={token}&user_id={user_id}"
    log.info(
        "verification_stub email=%s user_id=%s link=%s",
        email,
        user_id,
        fake_link,
    )
    