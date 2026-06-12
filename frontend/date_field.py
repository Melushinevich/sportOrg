"""Поле даты рождения: placeholder ДД.ММ.ГГГГ и маска ввода."""

from __future__ import annotations

import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit

from .form_styles import PLACEHOLDER_QSS

_DATE_DMY = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
_INPUT_MASK = "00.00.0000"


class CustomDateLineEdit(QLineEdit):
    PLACEHOLDER = "ДД.ММ.ГГГГ"

    def __init__(self) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setPlaceholderText(self.PLACEHOLDER)
        self._masked = False
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

    def focusInEvent(self, event) -> None:
        if not self._masked:
            self.setInputMask(_INPUT_MASK)
            self._masked = True
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        super().focusOutEvent(event)
        if not self.is_complete():
            self._clear_mask()

    def _clear_mask(self) -> None:
        self.setInputMask("")
        self.clear()
        self._masked = False

    def get_real_text(self) -> str:
        return self.text().replace("_", "").strip()

    def is_complete(self) -> bool:
        return bool(_DATE_DMY.match(self.get_real_text()))

    def is_empty(self) -> bool:
        digits = self.get_real_text().replace(".", "")
        return not digits

    def clear_date(self) -> None:
        self._clear_mask()

    def set_dmy_text(self, dmy: str) -> None:
        text = (dmy or "").strip()
        if not text:
            self.clear_date()
            return
        self.setInputMask(_INPUT_MASK)
        self._masked = True
        self.setText(text)
