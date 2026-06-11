"""Единый стиль QMessageBox и QInputDialog — читаемый текст на всех экранах."""

from __future__ import annotations

from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget

MESSAGE_BOX_STYLE = """
QMessageBox { background-color: white; }
QMessageBox QLabel { color: black; background-color: transparent; }
QMessageBox QPushButton {
    background-color: #555555;
    color: white;
    border: none;
    border-radius: 15px;
    padding: 8px 20px;
    min-width: 80px;
    font-family: 'Helvetica Neue';
    font-size: 14px;
}
QMessageBox QPushButton:hover { background-color: #333333; }
"""

INPUT_DIALOG_STYLE = """
QInputDialog { background-color: white; }
QInputDialog QLabel { color: black; background-color: transparent; }
QInputDialog QLineEdit, QInputDialog QComboBox {
    background-color: #D9D9D9;
    color: black;
    border: 1px solid #B0B0B0;
    border-radius: 10px;
    padding: 5px;
}
QInputDialog QPushButton {
    background-color: #555555;
    color: white;
    border: none;
    border-radius: 15px;
    padding: 8px 20px;
    min-width: 80px;
}
"""


def apply_dialog_styles(app: QApplication) -> None:
    """Глобальные стили диалогов — вызывать один раз после QApplication()."""
    app.setStyleSheet((app.styleSheet() or "") + MESSAGE_BOX_STYLE + INPUT_DIALOG_STYLE)


def style_message_box(box: QMessageBox) -> None:
    box.setStyleSheet(MESSAGE_BOX_STYLE)


def show_info(
    parent: QWidget | None,
    title: str,
    text: str,
    *,
    informative: str = "",
) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(text)
    if informative:
        box.setInformativeText(informative)
    style_message_box(box)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec_()


def show_error(
    parent: QWidget | None,
    title: str,
    text: str,
    *,
    informative: str = "",
) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle(title)
    box.setText(text or "Неизвестная ошибка")
    if informative:
        box.setInformativeText(informative)
    style_message_box(box)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec_()


def show_warning(
    parent: QWidget | None,
    title: str,
    text: str,
    *,
    informative: str = "",
) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Warning)
    box.setWindowTitle(title)
    box.setText(text)
    if informative:
        box.setInformativeText(informative)
    style_message_box(box)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec_()


def ask_yes_no(
    parent: QWidget | None,
    title: str,
    text: str,
    *,
    informative: str = "",
    default_no: bool = True,
) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(text)
    if informative:
        box.setInformativeText(informative)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    box.setDefaultButton(QMessageBox.No if default_no else QMessageBox.Yes)
    style_message_box(box)
    return box.exec_() == QMessageBox.Yes
