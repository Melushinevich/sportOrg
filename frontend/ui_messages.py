"""Единый стиль QMessageBox и QInputDialog — читаемый текст на всех экранах."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from .fonts import ensure_fonts_loaded, ui_family_css, ui_font, qss_ui_font

SKILLS_DIALOG_BUTTON_STYLE = """
QPushButton {
    background-color: #555555;
    color: white;
    border: none;
    border-radius: 15px;
    padding: 10px 18px;
    min-width: 120px;
    font-size: 14px;
}
QPushButton:hover { background-color: #333333; }
QPushButton:default { background-color: #444444; }
"""


def message_box_style() -> str:
    ensure_fonts_loaded()
    return qss_ui_font("""
QMessageBox {{ background-color: white; color: black; }}
QMessageBox QLabel {{ color: black; background-color: transparent; }}
QMessageBox QPushButton {{
    background-color: #555555;
    color: white;
    border: none;
    border-radius: 15px;
    padding: 8px 20px;
    min-width: 80px;
    font-family: __UI_FONT__;
    font-size: 14px;
}}
QMessageBox QPushButton:hover {{ background-color: #333333; }}
""")


def _message_box_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    return palette


def input_dialog_style() -> str:
    ensure_fonts_loaded()
    return """
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
    ensure_fonts_loaded()
    app.setStyleSheet((app.styleSheet() or "") + message_box_style() + input_dialog_style())


def style_message_box(box: QMessageBox) -> None:
    box.setStyleSheet(message_box_style())
    palette = _message_box_palette()
    box.setPalette(palette)
    box.setAutoFillBackground(True)
    for label in box.findChildren(QLabel):
        label.setPalette(palette)
        label.setStyleSheet("color: black; background-color: transparent;")


class _SkillsBeforeApplyDialog(QDialog):
    """Компактное предупреждение перед заявкой в команду."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        text: str,
        primary_label: str,
    ) -> None:
        super().__init__(parent)
        self._result = "cancel"
        self.setWindowTitle("Предупреждение")
        self.setModal(True)
        self.setWindowFlags(
            (self.windowFlags() | Qt.WindowCloseButtonHint) & ~Qt.WindowContextHelpButtonHint
        )
        self.setFixedWidth(390)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(16)

        content = QHBoxLayout()
        content.setSpacing(14)

        icon_label = QLabel()
        icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        icon_label.setPixmap(icon.pixmap(44, 44))
        icon_label.setFixedSize(44, 44)
        content.addWidget(icon_label, 0, Qt.AlignTop)

        message = QLabel(text)
        message.setWordWrap(True)
        message.setFont(ui_font(14))
        message.setStyleSheet("color: black; background: transparent;")
        message.setMaximumWidth(270)
        content.addWidget(message, 1)

        root.addLayout(content)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch()

        continue_btn = QPushButton("Продолжить")
        primary_btn = QPushButton(primary_label)
        for btn in (continue_btn, primary_btn):
            btn.setFont(ui_font(14))
            btn.setStyleSheet(SKILLS_DIALOG_BUTTON_STYLE)
            btn.setCursor(Qt.PointingHandCursor)

        continue_btn.clicked.connect(lambda: self._finish("continue"))
        primary_btn.clicked.connect(lambda: self._finish("fill_skills"))
        continue_btn.setDefault(True)
        continue_btn.setAutoDefault(True)

        buttons.addWidget(continue_btn)
        buttons.addWidget(primary_btn)
        root.addLayout(buttons)

    def _finish(self, action: str) -> None:
        self._result = action
        self.accept()

    def reject(self) -> None:
        self._result = "cancel"
        super().reject()

    def result_action(self) -> str:
        return self._result


def show_info(
    parent: QWidget | None,
    title: str,
    message: str,
    *,
    informative: str | None = None,
) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(message)
    if informative:
        box.setInformativeText(informative)
    style_message_box(box)
    box.exec_()


def show_error(
    parent: QWidget | None,
    title: str,
    message: str,
    *,
    informative: str | None = None,
) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle(title)
    box.setText(message)
    if informative:
        box.setInformativeText(informative)
    style_message_box(box)
    box.exec_()


def show_warning(
    parent: QWidget | None,
    title: str,
    message: str,
    *,
    informative: str | None = None,
) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Warning)
    box.setWindowTitle(title)
    box.setText(message)
    if informative:
        box.setInformativeText(informative)
    style_message_box(box)
    box.exec_()


def ask_yes_no(
    parent: QWidget | None,
    title: str,
    message: str,
    *,
    informative: str | None = None,
    default_no: bool = False,
) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(message)
    if informative:
        box.setInformativeText(informative)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    box.setDefaultButton(QMessageBox.No if default_no else QMessageBox.Yes)
    style_message_box(box)
    return box.exec_() == QMessageBox.Yes


def ask_skills_before_apply(
    parent: QWidget | None,
    *,
    skills_filled: bool,
) -> str:
    """Предупреждение перед заявкой. Возвращает fill_skills | continue | cancel."""
    if skills_filled:
        text = "Не забудьте обновить свои навыки, если вы стали сильнее💪"
        primary_label = "Обновить навыки"
    else:
        text = "Заполните свои навыки, так тренер сможет лучше оценить Вас"
        primary_label = "Заполнить навыки"

    dialog = _SkillsBeforeApplyDialog(
        parent,
        text=text,
        primary_label=primary_label,
    )
    dialog.exec_()
    return dialog.result_action()
