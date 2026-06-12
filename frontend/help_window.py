from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from .fonts import FONT_UI, title_font, ui_font


# Тексты справки для разных ролей
HELP_TEXTS = {
    'trainer': {
        'title': 'Справка для тренера',
        'content': """
<b>Добро пожаловать в SPORTORG!</b><br><br>

Этот раздел поможет вам разобраться в основных функциях приложения для тренера.<br><br>

<b> Главная страница</b><br>
Здесь отображается список ваших команд. Вы можете:<br>
• Добавить новую команду, нажав кнопку "ДОБАВИТЬ КОМАНДУ"<br>
• Открыть существующую команду двойным кликом по ней<br><br>

<b>➕ Добавление команды</b><br>
При создании команды необходимо:<br>
• Ввести название команды<br>
• Выбрать вид спорта из списка<br>
• Добавить критерии оценки навыков спортсменов<br><br>

<b>👥 Работа с составом</b><br>
В окне команды вы можете:<br>
• Добавить участников через кнопку "ДОБАВИТЬ УЧАСТНИКА"<br>
• Оценить навыки спортсмена двойным кликом по колонке "КАЧЕСТВА"<br>
• Удалить участника, выбрав строку и нажав "УДАЛИТЬ УЧАСТНИКА"<br>
• Сформировать итоговый состав кнопкой "СФОРМИРОВАТЬ СОСТАВ"<br><br>

<b>📊 Оценка навыков</b><br>
При двойном клике на навыки игрока открывается окно оценки, где вы можете поставить балл от 1 до 10 по каждому навыку. Средний балл рассчитывается автоматически.<br><br>

<b>📝 Отклики спортсменов</b><br>
В разделе "Отклики спортсменов" вы видите всех спортсменов, откликнувшихся на ваши команды. Вы можете фильтровать отклики по конкретной команде.<br><br>

<b>❓ Нужна помощь?</b><br>
Нажмите на кнопку поддержки (наушники) в правом нижнем углу, чтобы связаться с нами.
        """
    },
    'athlete': {
        'title': 'Справка для спортсмена',
        'content': """
<b>Добро пожаловать в SPORTORG!</b><br><br>

Этот раздел поможет вам разобраться в основных функциях приложения для спортсмена.<br><br>

<b>📝 Регистрация</b><br>
Заполните анкету, указав:<br>
• ФИО<br>
• Дату рождения и пол<br>
• Город проживания и номер телефона<br><br>

<b> Мои скиллы</b><br>
В разделе "Мои скиллы" вы можете указать свои навыки и качества. Это поможет тренерам лучше оценить вас при отборе в команду.<br><br>

<b>🏆 Доступные команды</b><br>
Здесь отображаются команды, которые ищут спортсменов. Вы можете:<br>
• Просмотреть информацию о команде<br>
• Откликнуться на интересующую вас команду<br>
• Указать мотивацию и доступное время для тренировок<br><br>

<b>📬 Отклики</b><br>
После отклика тренер рассмотрит вашу кандидатуру. Если вас выберут, вы получите уведомление.<br><br>

<b>💡 Советы</b><br>
• Указывайте все свои навыки честно — это поможет найти подходящую команду<br>
• Заполняйте мотивацию подробно — тренеры обращают на это внимание<br>
• Следите за статусом ваших откликов в личном кабинете<br><br>

<b> Нужна помощь?</b><br>
Нажмите на кнопку поддержки (наушники) в правом нижнем углу, чтобы связаться с нами.
        """
    }
}


class HelpWindow(QDialog):
    def __init__(self, user_type='trainer', parent=None):
        super().__init__(parent)
        self.user_type = user_type
        self.setWindowTitle("SPORTORG - Справка")
        self.setFixedSize(800, 700)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # Получаем текст справки для текущей роли
        help_data = HELP_TEXTS.get(self.user_type, HELP_TEXTS['trainer'])

        # Заголовок
        title = QLabel(help_data['title'])
        title.setFont(title_font(48))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: black;")
        main_layout.addWidget(title)

        # Разделитель
        separator = QWidget()
        separator.setFixedHeight(3)
        separator.setStyleSheet("background-color: #6C769F;")
        main_layout.addWidget(separator)

        # Скроллируемая область с текстом
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #6C769F;
                border-radius: 15px;
                background-color: #F5F5F5;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)

        content_label = QLabel(help_data["content"])
        content_label.setFont(ui_font(16))
        content_label.setTextFormat(Qt.RichText)
        content_label.setStyleSheet("color: black; background: transparent;")
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        content_layout.addWidget(content_label)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Кнопка закрытия
        close_button = QPushButton("ЗАКРЫТЬ")
        close_button.setFixedSize(300, 60)
        close_button.setFont(ui_font(20))
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6C769F;
                color: white;
                border: none;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #5A6385;
            }
        """)
        close_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)