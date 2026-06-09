from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SkillsRatingDialog(QDialog):
    def __init__(self, player_name, skills, ratings=None, parent=None):
        super().__init__(parent)
        self.player_name = player_name
        self.skills = skills
        self.ratings = ratings or {}
        self.setWindowTitle(f"Оценка навыков — {player_name}")
        self.setFixedSize(600, 700)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Заголовок
        title = QLabel(f"Оцените навыки игрока: {self.player_name}")
        title.setFont(QFont("Helvetica Neue", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: black;")
        main_layout.addWidget(title)

        # Скроллируемая область для навыков
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #6C769F;
                border-radius: 15px;
                background-color: #F5F5F5;
                color: black;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)

        self.rating_combos = {}
        for skill in self.skills:
            row = QHBoxLayout()

            skill_label = QLabel(skill)
            skill_label.setFont(QFont("Helvetica Neue", 16))
            skill_label.setStyleSheet("color: black;")
            skill_label.setFixedWidth(250)
            row.addWidget(skill_label)

            combo = QComboBox()
            combo.addItems(["—", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
            combo.setFont(QFont("Helvetica Neue", 16))
            combo.setFixedSize(100, 40)

            # Устанавливаем текущую оценку если есть
            if skill in self.ratings:
                combo.setCurrentText(str(self.ratings[skill]))

            combo.setStyleSheet("""
                QComboBox {
                    background-color: #D9D9D9;
                    border: none;
                    border-radius: 20px;
                    padding: 5px 15px;
                    color: black;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 30px;
                    color: black;
                }
                QComboBox QAbstractItemView {
                    font-size: 14px;
                    background-color: white;
                    selection-background-color: #6C769F;
                    selection-color: white;
                    color: black;
                }
            """)
            row.addWidget(combo)
            row.addStretch()

            self.rating_combos[skill] = combo
            scroll_layout.addLayout(row)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        cancel_button = QPushButton("ОТМЕНА")
        cancel_button.setFixedSize(200, 50)
        cancel_button.setFont(QFont("Helvetica Neue", 16))
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9;
                color: black;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover { background-color: #C0C0C0; }
        """)
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("СОХРАНИТЬ")
        save_button.setFixedSize(200, 50)
        save_button.setFont(QFont("Helvetica Neue", 16))
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F;
                color: white;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover { background-color: #5A6385; }
        """)
        save_button.clicked.connect(self.on_save)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

    def on_save(self):
        """Собираем оценки и закрываем диалог"""
        self.ratings = {}
        for skill, combo in self.rating_combos.items():
            value = combo.currentText()
            if value != "—":
                self.ratings[skill] = int(value)
        self.accept()

    def get_ratings(self):
        return self.ratings