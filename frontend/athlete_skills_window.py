import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox,
    QInputDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from .assets import asset_path
from .burger_menu import show_burger_menu
from .help_window import HelpWindow
from .navigation import (
    ATHLETE_HOME,
    ATHLETE_TEAMS,
    open_profile,
    open_screen,
    leave_to,
)
from .fonts import apply_app_fonts, ui_family_css, qss_ui_font
from .ui_messages import apply_dialog_styles, show_error, show_info, show_warning
from .fonts import FONT_UI, title_font, ui_font
from .api_client import ApiError
from .athlete_skills_service import load_skills_page, save_my_skills
from .profile_service import athlete_display_name
from .session import session


class AthleteSkillsWindow(QMainWindow):
    # ЗАДАЧА 3: "ЯРОСЛАВЛЬ" → "СПОРТСМЕН"
    def __init__(self, athlete_name="СПОРТСМЕН", parent=None):
        super().__init__(parent)
        self.athlete_name = athlete_name
        self.available_skills: list[str] = []
        self.setWindowTitle("SPORTORG - Мои скиллы")
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(25)

        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(title_font(96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        athlete_label = QLabel(self.athlete_name)
        athlete_label.setFont(title_font(96))
        athlete_label.setStyleSheet("color: #EF8354;")
        self.athlete_name_label = athlete_label
        top_layout.addWidget(athlete_label)

        self.burger_button = QPushButton()
        self.burger_button.setFixedSize(55, 55)

        # Создаём layout для кнопки
        button_layout = QHBoxLayout(self.burger_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignCenter)

        # Создаём QLabel с иконкой
        icon_label = QLabel()
        pixmap = QPixmap(asset_path("burger.png")).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        button_layout.addWidget(icon_label)
        self.burger_button.setStyleSheet("""
            QPushButton {
                background: #EF8354;
                border-radius: 27px;
            }
            QPushButton:hover {
                background-color: #D6754B;
            }
        """)
        self.burger_button.clicked.connect(self.show_burger_menu)
        top_layout.addWidget(self.burger_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(30)

        list_title = QLabel("Навыки")
        list_title.setFont(ui_font(20, QFont.Bold))
        list_title.setAlignment(Qt.AlignLeft)
        list_title.setStyleSheet("color: black; margin-bottom: 5px;")
        main_layout.addWidget(list_title)

        skills_container = QWidget()
        skills_container.setStyleSheet("""
            QWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 0px;
            }
        """)
        skills_container_layout = QVBoxLayout(skills_container)
        skills_container_layout.setContentsMargins(15, 15, 15, 15)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Навык", "Оценка по 10 б шкале"])
        self.table.setRowCount(0)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.table.verticalHeader().setDefaultSectionSize(70)

        self.table.setStyleSheet(qss_ui_font("""
            QTableWidget {
                background-color: white;
                border: 2px solid;
                border-radius: 0px;
                font-family: __UI_FONT__;
                color: black;
                selection-background-color: #EF8354;
                selection-color: white;
                gridline-color: #B0B0B0;
            }
            QTableWidget::item {
                padding: 10px;
                color: black;
                border: 1px solid #B0B0B0;
            }
            QHeaderView::section {
                background-color: #C8C8C8;
                color: black;
                border: 1px solid #B0B0B0;
                border-radius: 0px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                font-family: __UI_FONT__;
            }
            QTableCornerButton::section {
                background-color: #C8C8C8;
                border: 1px solid #B0B0B0;
                border-radius: 0px;
            }
            QScrollBar:vertical {
                background: #D9D9D9;
                width: 12px;
                border-radius: 0px;
            }
            QScrollBar::handle:vertical {
                background: #EF8354;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #D6754B;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """))

        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.verticalHeader().setVisible(False)
        self._update_table_height()

        skills_container_layout.addWidget(self.table, 1)

        self.add_skill_button = QPushButton("ДОБАВИТЬ НАВЫК")
        self.add_skill_button.setFixedSize(690, 65)
        self.add_skill_button.setFont(ui_font(20))
        self.add_skill_button.setCursor(Qt.PointingHandCursor)
        self.add_skill_button.setStyleSheet("""
            QPushButton {
                background-color: #EF8354;
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 22px;
            }
            QPushButton:hover {
                background-color: #D6754B;
            }
        """)
        self.add_skill_button.clicked.connect(self.on_add_skill)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 8, 0, 0)
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_skill_button)
        btn_layout.addStretch()
        skills_container_layout.addLayout(btn_layout)

        main_layout.addWidget(skills_container, 1)

        save_layout = QHBoxLayout()
        save_layout.setAlignment(Qt.AlignCenter)

        self.save_button = QPushButton("СОХРАНИТЬ")
        self.save_button.setFixedSize(400, 65)
        self.save_button.setFont(ui_font(20))
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9;
                color: black;
                border: 2px solid #B0B0B0;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #C0C0C0;
            }
        """)
        self.save_button.clicked.connect(self.on_save)

        save_layout.addWidget(self.save_button)
        main_layout.addLayout(save_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        info_label = QLabel("© 2026 SPORTORG | Все права защищены")
        info_label.setFont(ui_font(10))
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("color: gray;")

        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'available_teams': self.on_go_available_teams,
            'my_skills': lambda: None,
            'profile': self.on_go_profile,
            'help': self.on_go_help,
        }
        show_burger_menu(self, self.burger_button, 'athlete', callbacks)

    def _update_table_height(self) -> None:
        header_height = self.table.horizontalHeader().height() or 45
        row_height = self.table.verticalHeader().defaultSectionSize()
        rows = max(self.table.rowCount(), 1)
        frame = self.table.frameWidth() * 2
        content_height = header_height + rows * row_height + frame + 2
        self.table.setMinimumHeight(min(content_height, 400))
        self.table.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded if content_height > 400 else Qt.ScrollBarAlwaysOff
        )

    def on_go_home(self):
        leave_to(ATHLETE_HOME)

    def on_go_available_teams(self):
        from .athlete_available_teams import AthleteAvailableTeamsWindow

        name = athlete_display_name()

        def _refresh(widget) -> None:
            if hasattr(widget, "set_athlete_name"):
                widget.set_athlete_name(name)

        open_screen(
            self,
            lambda: AthleteAvailableTeamsWindow(athlete_name=name),
            screen_id=ATHLETE_TEAMS,
            refresh=_refresh,
        )

    def on_go_profile(self):
        open_profile("athlete")

    def on_go_help(self):
        self.help_window = HelpWindow(user_type='athlete', parent=self)
        self.help_window.show()

    def set_athlete_name(self, name: str) -> None:
        self.athlete_name = (name or "СПОРТСМЕН").strip() or "СПОРТСМЕН"
        if hasattr(self, "athlete_name_label"):
            self.athlete_name_label.setText(self.athlete_name)

    def showEvent(self, event):
        super().showEvent(event)
        self.set_athlete_name(athlete_display_name())
        self.load_skills_data()

    def load_skills_data(self) -> None:
        if not session.is_logged_in:
            return
        try:
            skills, self.available_skills = load_skills_page()
        except ApiError as exc:
            show_error(self, "Ошибка", str(exc))
            return
        self.populate_table(skills)

    def populate_table(self, skills: list[dict]) -> None:
        self.table.setRowCount(0)
        for skill in skills:
            row = self.table.rowCount()
            self.table.insertRow(row)

            name = skill.get("name") or ""
            skill_item = QTableWidgetItem(name)
            skill_item.setFont(ui_font(16))
            skill_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, skill_item)

            rating = skill.get("rating")
            rating_text = str(rating) if rating is not None else ""
            rating_item = QTableWidgetItem(rating_text)
            rating_item.setFont(ui_font(16))
            rating_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, rating_item)

        self._update_table_height()

    def _rating_at_row(self, row: int) -> str:
        widget = self.table.cellWidget(row, 1)
        if isinstance(widget, QComboBox):
            text = widget.currentText()
            return "" if text == "—" else text
        item = self.table.item(row, 1)
        return item.text() if item else ""

    def on_cell_clicked(self, row, column):
        if column != 1:
            return

        existing_widget = self.table.cellWidget(row, column)
        if existing_widget and isinstance(existing_widget, QComboBox):
            return

        combo = QComboBox()
        combo.addItem("—")
        for i in range(1, 11):
            combo.addItem(str(i))

        combo.setFont(ui_font(16))
        combo.setStyleSheet("""
            QComboBox {
                background-color: #D9D9D9;
                border: none;
                border-radius: 15px;
                padding: 5px 10px;
                min-height: 30px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
                background-color: white;
                selection-background-color: #EF8354;
                selection-color: white;
            }
        """)

        current_text = self.table.item(row, column).text() if self.table.item(row, column) else ""
        if current_text:
            combo.setCurrentText(current_text)

        combo.currentTextChanged.connect(lambda text, r=row: self.on_rating_changed(r, text))

        self.table.setCellWidget(row, column, combo)
        combo.showPopup()

    def on_rating_changed(self, row, text):
        if text == "—":
            text = ""

        item = self.table.item(row, 1)
        if item:
            item.setText(text)

        self.table.removeCellWidget(row, 1)

    def on_add_skill(self):
        if not self.available_skills:
            show_warning(self, "Внимание", "Справочник навыков пуст или не загружен.")
            return

        skill, ok = QInputDialog.getItem(
            self,
            "Выбор навыка",
            "Выберите навык для добавления:",
            self.available_skills,
        )

        if ok and skill:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.text() == skill:
                    show_warning(self, "Внимание", f"Навык '{skill}' уже добавлен!")
                    return

            row = self.table.rowCount()
            self.table.insertRow(row)

            skill_item = QTableWidgetItem(skill)
            skill_item.setFont(ui_font(16))
            skill_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, skill_item)

            rating_item = QTableWidgetItem("")
            rating_item.setFont(ui_font(16))
            rating_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, rating_item)

            self._update_table_height()

    def on_save(self):
        if self.table.rowCount() == 0:
            show_warning(self, "Внимание", "Добавьте хотя бы один навык!")
            return

        skills_data = []
        for row in range(self.table.rowCount()):
            skill = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            rating = self._rating_at_row(row)
            if not skill:
                continue
            if rating:
                try:
                    value = int(rating)
                except ValueError:
                    show_warning(
                        self,
                        "Внимание",
                        f"Оценка для «{skill}» должна быть числом от 1 до 10.",
                    )
                    return
                if value < 1 or value > 10:
                    show_warning(
                        self,
                        "Внимание",
                        f"Оценка для «{skill}» должна быть от 1 до 10.",
                    )
                    return
            skills_data.append({"name": skill, "rating": rating or None})

        if not skills_data:
            show_warning(self, "Внимание", "Добавьте хотя бы один навык!")
            return

        try:
            saved = save_my_skills(skills=skills_data)
        except ApiError as exc:
            show_error(self, "Ошибка", str(exc))
            return

        self.populate_table(saved)
        show_info(
            self,
            "Сохранено",
            f"Ваши навыки сохранены! ({len(saved)} навыков)",
        )


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)

    apply_dialog_styles(app)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    # ЗАДАЧА 3: "ЯРОСЛАВЛЬ" → "СПОРТСМЕН"
    window = AthleteSkillsWindow(athlete_name="СПОРТСМЕН")
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()