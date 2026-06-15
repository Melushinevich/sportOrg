"""Поле телефона: +7-XXX-XXX-XX-XX, не более 11 цифр."""

from __future__ import annotations

import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit

from .form_styles import PLACEHOLDER_QSS

PHONE_EXAMPLE = "+7-980-651-57-80"
PHONE_MAX_DIGITS = 11
_PHONE_GROUP_SIZES = (3, 3, 2, 2)


def phone_digits(value: str | None) -> str:
    """Только цифры, максимум 11."""
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return ""
    if digits[0] == "8":
        digits = "7" + digits[1:]
    if digits[0] != "7":
        digits = "7" + digits
    return digits[:PHONE_MAX_DIGITS]


def format_phone_display(value: str | None) -> str:
    """Формат отображения: +7-980-651-57-80."""
    digits = phone_digits(value)
    if not digits:
        return ""
    body = digits[1:]
    chunks: list[str] = []
    pos = 0
    for size in _PHONE_GROUP_SIZES:
        if pos >= len(body):
            break
        chunks.append(body[pos : pos + size])
        pos += size
    if not chunks:
        return "+7"
    return "+7-" + "-".join(chunks)


def is_phone_complete(value: str | None) -> bool:
    return len(phone_digits(value)) == PHONE_MAX_DIGITS


class CustomPhoneLineEdit(QLineEdit):
    PLACEHOLDER = PHONE_EXAMPLE

    def __init__(self) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setPlaceholderText(self.PLACEHOLDER)
        self._updating = False
        self.setStyleSheet(
            """
            QLineEdit {
                background: #D9D9D9;
                border: 2px solid black;
                border-radius: 30px;
                font-size: 25px;
                color: black;
                min-height: 70px;
            }
            """
            + PLACEHOLDER_QSS
        )
        self.textChanged.connect(self._format_as_typed)

    def _format_as_typed(self, _text: str) -> None:
        if self._updating:
            return
        formatted = format_phone_display(self.text())
        if formatted == self.text():
            return
        self._updating = True
        self.setText(formatted)
        self.setCursorPosition(len(formatted))
        self._updating = False

    def get_real_text(self) -> str:
        return format_phone_display(self.text())

    def digits(self) -> str:
        return phone_digits(self.text())

    def is_complete(self) -> bool:
        return is_phone_complete(self.text())

    def is_empty(self) -> bool:
        return not phone_digits(self.text())

    def clear_phone(self) -> None:
        self._updating = True
        self.clear()
        self._updating = False

    def set_phone_text(self, value: str | None) -> None:
        text = format_phone_display(value)
        self._updating = True
        if text:
            self.setText(text)
        else:
            self.clear()
        self._updating = False
