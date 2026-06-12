"""Общие стили полей ввода (полупрозрачный placeholder)."""

PLACEHOLDER_QSS = """
QLineEdit::placeholder {
    color: rgba(0, 0, 0, 0.42);
    font-style: italic;
}
"""

COMBO_PLACEHOLDER_QSS = """
QComboBox QLineEdit::placeholder {
    color: rgba(0, 0, 0, 0.42);
    font-style: italic;
}
"""
