from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class PlayerContactDialog(QDialog):
    def __init__(self, player_name, email="", phone="", parent=None):
        super().__init__(parent)
        self.player_name = player_name
        self.email = email
        self.phone = phone
        self.setWindowTitle(f"Контакты — {player_name}")
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # Заголовок с именем
        title = QLabel(self.player_name)
        title.setFont(QFont("Helvetica Neue", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: black;")
        main_layout.addWidget(title)

        # Разделитель
        separator = QLabel()
        separator.setStyleSheet("background-color: #6C769F; min-height: 3px; max-height: 3px;")
        main_layout.addWidget(separator)

        main_layout.addSpacing(20)

        # Email
        if self.email:
            email_layout = QHBoxLayout()

            email_icon = QLabel("📧")
            email_icon.setFont(QFont("Segoe UI", 24))
            email_icon.setFixedSize(40, 40)
            email_layout.addWidget(email_icon)

            email_label = QLabel(self.email)
            email_label.setFont(QFont("Helvetica Neue", 16))
            email_label.setStyleSheet("color: black; background: transparent;")
            email_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            email_layout.addWidget(email_label)

            email_layout.addStretch()
            main_layout.addLayout(email_layout)
            main_layout.addSpacing(15)

        # Телефон
        if self.phone:
            phone_layout = QHBoxLayout()

            phone_icon = QLabel("📱")
            phone_icon.setFont(QFont("Segoe UI", 24))
            phone_icon.setFixedSize(40, 40)
            phone_layout.addWidget(phone_icon)

            phone_label = QLabel(self.phone)
            phone_label.setFont(QFont("Helvetica Neue", 16))
            phone_label.setStyleSheet("color: black; background: transparent;")
            phone_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            phone_layout.addWidget(phone_label)

            phone_layout.addStretch()
            main_layout.addLayout(phone_layout)
            main_layout.addSpacing(15)

        # Если нет контактов
        if not self.email and not self.phone:
            no_contact_label = QLabel("Контактная информация не указана")
            no_contact_label.setFont(QFont("Helvetica Neue", 14))
            no_contact_label.setStyleSheet("color: gray;")
            no_contact_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(no_contact_label)
            main_layout.addSpacing(15)

        main_layout.addStretch()

        # Кнопка закрытия
        close_button = QPushButton("ЗАКРЫТЬ")
        close_button.setFixedSize(200, 50)
        close_button.setFont(QFont("Helvetica Neue", 16))
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F;
                color: white;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        close_button.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_button)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)