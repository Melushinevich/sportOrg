import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QComboBox, QLineEdit,
    QInputDialog
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from . import dpi_fix
from .assets import asset_path
from .burger_menu import show_burger_menu
from .registr_window import SupportButton
from .fonts import apply_app_fonts
from .ui_messages import apply_dialog_styles, ask_yes_no, show_error as display_error
from .fonts import FONT_UI, title_font, ui_font
from .api_client import ApiError
from .session import session
from .teams_service import (
    create_coach_team,
    criteria_texts,
    load_skills_catalog,
    load_sports_catalog,
)
from .navigation import (
    TRAINER_HOME,
    TRAINER_RESPONSES,
    get_navigator,
    leave_to,
    open_profile,
    open_screen,
)


class CustomComboBox(QComboBox):
    """Кастомный ComboBox со стрелкой-кнопкой"""

    def __init__(self, placeholder="", items=None):
        if items is None:
            items = []
        self._placeholder = placeholder
        super().__init__()
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        font_combo = ui_font(28)
        font_combo.setItalic(True)
        self.lineEdit().setFont(font_combo)

        self.setStyleSheet("""
            QComboBox {
                background-color: #D9D9D9;
                border: none;
                border-radius: 30px;
                padding: 15px 60px 15px 30px;
                min-height: 70px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
                width: 0px;
            }
            QComboBox QAbstractItemView {
                font-size: 20px;
                font-family: "Roboto";
                color: black;
                background-color: white;
                selection-background-color: #6C769F;
                selection-color: white;
                border: 2px solid #6C769F;
                border-radius: 15px;
            }
        """)

        # Кнопка-стрелка
        self.arrow_button = QPushButton("▼", self)
        self.arrow_button.setFixedSize(40, 40)
        self.arrow_button.setStyleSheet("""
            QPushButton {
                background: white;
                border: 2px solid black;
                border-radius: 20px;
                font-size: 18px;
                color: black;
            }
        """)
        self.arrow_button.clicked.connect(self.showPopup)
        self.reload_items(items)

    def reload_items(self, items: list[str]) -> None:
        self.clear()
        if items:
            self.addItems(items)
        self.setCurrentIndex(-1)
        self.setCurrentText(self._placeholder)

    def resizeEvent(self, event):
        """Позиционируем стрелку при изменении размера"""
        if hasattr(self, 'arrow_button'):
            x = self.width() - 50
            y = (self.height() - 40) // 2
            self.arrow_button.move(x, y)
        super().resizeEvent(event)


class AddSportCriteriaWindow(QMainWindow):
    sport_saved = pyqtSignal(str, str, list, int)

    def __init__(self, existing_sports=None, parent=None):
        super().__init__(parent)
        self.existing_sports = existing_sports or []
        self.available_sports: list[str] = []
        self.available_criteria: list[str] = []
        self.selected_criteria = []
        self.setWindowTitle("SPORTORG - Добавление команды")
        self.setFixedSize(1440, 1024)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(20)

        # === Верхняя панель ===
        top_layout = QHBoxLayout()

        title_label = QLabel("SPORTORG")
        title_label.setFont(title_font(96))
        title_label.setStyleSheet("color: black;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        trainer_label = QLabel("ТРЕНЕР")
        trainer_label.setFont(title_font(96))
        trainer_label.setStyleSheet("color: #6C769F;")
        top_layout.addWidget(trainer_label)

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
                background: #6C769F;
                border-radius: 27px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        self.burger_button.clicked.connect(self.show_burger_menu)
        top_layout.addWidget(self.burger_button)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(40)

        # === Поле "Название команды" ===
        self.team_name_input = QLineEdit()
        self.team_name_input.setPlaceholderText("Название команды")
        font_input = ui_font(28)
        font_input.setItalic(True)
        self.team_name_input.setFont(font_input)
        self.team_name_input.setAlignment(Qt.AlignCenter)
        self.team_name_input.setFixedHeight(70)
        self.team_name_input.setStyleSheet("""
            QLineEdit {
                background-color: #D9D9D9;
                border: none;
                border-radius: 30px;
                padding: 15px 30px;
                color: black;
            }
            QLineEdit::placeholder {
                color: #555555;
            }
        """)
        main_layout.addWidget(self.team_name_input)

        # === Поле "Вид" (кастомный combobox со стрелкой) ===
        self.sport_combo = CustomComboBox("Вид", [])
        main_layout.addWidget(self.sport_combo)

        # === Заголовок "Критерии" ===
        criteria_label = QLabel("Критерии")
        font_crit = ui_font(28)
        font_crit.setItalic(True)
        criteria_label.setFont(font_crit)
        criteria_label.setStyleSheet("color: black;")
        criteria_label.setFixedHeight(40)
        main_layout.addWidget(criteria_label)

        # === Контейнер с критериями ===
        criteria_container = QWidget()
        criteria_container.setStyleSheet("""
            QWidget {
                background-color: #D9D9D9;
                border: 2px solid #6C769F;
                border-radius: 20px;
            }
        """)
        criteria_container_layout = QVBoxLayout(criteria_container)
        criteria_container_layout.setContentsMargins(15, 15, 15, 15)
        criteria_container_layout.setSpacing(10)

        self.criteria_list_widget = QListWidget()
        self.criteria_list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                font-size: 20px;
                font-family: "Roboto";
                padding: 5px;
                min-height: 250px;
                color: black;
            }
            QListWidget::item {
                background-color: white;
                padding: 15px;
                border-radius: 15px;
                margin: 5px 0;
                color: black;
                text-align: center;
            }
            QListWidget::item:selected {
                background-color: #6C769F;
                color: white;
            }
        """)
        criteria_container_layout.addWidget(self.criteria_list_widget)

        self.add_criteria_button = QPushButton("ДОБАВИТЬ КРИТЕРИЙ")
        self.add_criteria_button.setFont(ui_font(20))
        self.add_criteria_button.setCursor(Qt.PointingHandCursor)
        self.add_criteria_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F;
                color: white;
                border: none;
                border-radius: 30px;
                padding: 15px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        self.add_criteria_button.clicked.connect(self.on_add_criteria)
        criteria_container_layout.addWidget(self.add_criteria_button)

        main_layout.addWidget(criteria_container)

        # === Кнопка "СОХРАНИТЬ" ===
        save_layout = QHBoxLayout()
        save_layout.setAlignment(Qt.AlignCenter)

        self.save_button = QPushButton("СОХРАНИТЬ")
        self.save_button.setFixedSize(400, 70)
        self.save_button.setFont(ui_font(22))
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

        main_layout.addStretch()

    def show_burger_menu(self):
        callbacks = {
            'home': self.on_go_home,
            'responses': self.on_go_responses_all,
            'profile': self.on_go_profile,
        }
        show_burger_menu(self, self.burger_button, 'trainer', callbacks)

    def on_go_home(self):
        leave_to(TRAINER_HOME)

    def on_go_responses_all(self):
        from .responses_window import ResponsesWindow

        open_screen(
            self,
            lambda: ResponsesWindow(
                team_name=None, sport_name="", parent=None, show_all=True
            ),
            screen_id=TRAINER_RESPONSES,
        )

    def on_go_profile(self):
        open_profile("trainer")

    def update_existing_sports(self, existing_sports):
        self.existing_sports = existing_sports or []
        self.load_catalog()
        self.reset_form()

    def load_catalog(self) -> None:
        if not session.is_logged_in:
            return
        try:
            sports = load_sports_catalog()
            skills = load_skills_catalog()
        except ApiError as exc:
            self.show_error(str(exc))
            return

        self.available_sports = [row["name"] for row in sports if row.get("name")]
        self.available_criteria = [row["name"] for row in skills if row.get("name")]
        self.sport_combo.reload_items(self.available_sports)

    def reset_form(self):
        self.team_name_input.clear()
        self.sport_combo.reload_items(self.available_sports)
        self.selected_criteria.clear()
        self.criteria_list_widget.clear()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_catalog()

    def on_add_criteria(self):
        if not self.available_criteria:
            self.show_error("Список критериев пуст. Проверьте подключение к API.")
            return
        criteria, ok = QInputDialog.getItem(
            self,
            "Выбор критерия",
            "Выберите навык спортсмена:",
            self.available_criteria,
        )
        if ok and criteria:
            if criteria not in self.selected_criteria:
                self.selected_criteria.append(criteria)
                item = QListWidgetItem(criteria)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(ui_font(20))
                self.criteria_list_widget.addItem(item)
            else:
                self.show_error(f"Навык '{criteria}' уже добавлен!")

    def on_save(self):
        team_name = self.team_name_input.text().strip()
        sport = self.sport_combo.currentText()

        if not team_name:
            self.show_error("Введите название команды!")
            return

        if sport == "Вид" or sport not in self.available_sports:
            self.show_error("Выберите вид спорта!")
            return

        if team_name in self.existing_sports:
            if not ask_yes_no(
                self,
                "Команда уже добавлена",
                f"Команда '{team_name}' уже была добавлена ранее. Создать ещё одну?",
            ):
                return

        if not self.selected_criteria:
            if not ask_yes_no(
                self,
                "Нет критериев",
                "Вы не выбрали ни одного навыка. Продолжить?",
            ):
                return

        self.save_button.setEnabled(False)
        try:
            created = create_coach_team(
                team=team_name,
                sport=sport,
                criteria=self.selected_criteria.copy(),
            )
        except ApiError as exc:
            self.show_error(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            self.show_error(f"Ошибка сохранения: {exc}")
            return
        finally:
            self.save_button.setEnabled(True)

        criteria = criteria_texts(created.get("criteria")) or self.selected_criteria.copy()
        team_id = int(created["team_id"])
        self.sport_saved.emit(team_name, sport, criteria, team_id)
        if not leave_to(TRAINER_HOME):
            self.close()

    def show_error(self, message):
        display_error(self, "Ошибка", message)

    def closeEvent(self, event):
        if get_navigator() is None and self.parent():
            self.parent().show()
        elif get_navigator() is not None:
            leave_to(TRAINER_HOME)
        event.accept()


def main():
    app = QApplication(sys.argv)
    apply_app_fonts(app)
    dpi_fix.apply_dpi_fix(app)

    apply_dialog_styles(app)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    app.setPalette(palette)

    window = AddSportCriteriaWindow()
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()