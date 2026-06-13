import unittest
from database import Database


class TestSportDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Выполняется один раз перед всеми тестами"""
        cls.db = Database()
        print("\nПодключение к базе данных установлено")

    def setUp(self):
        """Выполняется перед каждым тестом - создаём тестовые данные"""
        import time
        self.test_email = f"test_{int(time.time() * 1000)}@test.ru"
        success, msg, user_id = self.db.register_user(
            email=self.test_email,
            password="123456",
            last_name="Тестов",
            first_name="Тест",
            role="sportsman",
            city="Москва"
        )
        self.test_user_id = user_id if success else None

    def tearDown(self):
        """Выполняется после каждого теста - удаляем тестовые данные"""
        if self.test_user_id:
            self.db.delete_user(self.test_user_id)

    # 1. ТЕСТЫ РЕГИСТРАЦИИ

    def test_register_user_success(self):
        """Тест: успешная регистрация пользователя"""
        import time
        email = f"new_{int(time.time() * 1000)}@test.ru"
        success, msg, user_id = self.db.register_user(
            email=email,
            password="123456",
            last_name="Новый",
            first_name="Пользователь",
            role="sportsman"
        )
        self.assertTrue(success)
        self.assertIsNotNone(user_id)
        if user_id:
            self.db.delete_user(user_id)

    def test_register_user_duplicate_email(self):
        """Тест: регистрация с существующим email - должна быть ошибка"""
        success, msg, user_id = self.db.register_user(
            email=self.test_email,
            password="123456",
            last_name="Дубль",
            first_name="Тест",
            role="sportsman"
        )
        self.assertFalse(success)
        self.assertIn("уже существует", msg)

    def test_register_user_invalid_role(self):
        """Тест: регистрация с неверной ролью - должна быть ошибка"""
        import time
        success, msg, user_id = self.db.register_user(
            email=f"invalid_{int(time.time() * 1000)}@test.ru",
            password="123456",
            last_name="Тест",
            first_name="Тест",
            role="admin"
        )
        self.assertFalse(success)

    def test_register_user_short_password(self):
        """Тест: регистрация с коротким паролем - должна быть ошибка"""
        import time
        success, msg, user_id = self.db.register_user(
            email=f"short_{int(time.time() * 1000)}@test.ru",
            password="123",
            last_name="Тест",
            first_name="Тест",
            role="sportsman"
        )
        self.assertFalse(success)

    # 2. ТЕСТЫ ВХОДА

    def test_login_success(self):
        """Тест: успешный вход"""
        success, user = self.db.login_user(self.test_email, "123456")
        self.assertTrue(success)
        self.assertEqual(user['email'], self.test_email)

    def test_login_wrong_password(self):
        """Тест: неверный пароль"""
        success, user = self.db.login_user(self.test_email, "wrongpassword")
        self.assertFalse(success)

    def test_login_wrong_email(self):
        """Тест: неверный email"""
        success, user = self.db.login_user("nonexistent@test.ru", "123456")
        self.assertFalse(success)

    # 3. ТЕСТЫ ПРОФИЛЯ

    def test_get_user_by_id(self):
        """Тест: получение пользователя по ID"""
        user = self.db.get_user_by_id(self.test_user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], self.test_email)

    def test_get_user_by_email(self):
        """Тест: получение пользователя по email"""
        user = self.db.get_user_by_email(self.test_email)
        self.assertIsNotNone(user)
        self.assertEqual(user['id'], self.test_user_id)

    def test_update_profile(self):
        """Тест: обновление профиля"""
        success, msg = self.db.update_profile(
            self.test_user_id,
            phone="+7 (999) 111-22-33",
            city="Санкт-Петербург"
        )
        self.assertTrue(success)

        user = self.db.get_user_by_id(self.test_user_id)
        self.assertEqual(user.get('city'), "Санкт-Петербург")

    # 4. ТЕСТЫ НАВЫКОВ

    def test_add_sportsman_skill_success(self):
        """Тест: успешное добавление навыка"""
        success, msg = self.db.add_sportsman_skill(self.test_user_id, "Бег", 8)
        self.assertTrue(success)

    def test_add_sportsman_skill_invalid_rating(self):
        """Тест: добавление навыка с неверной оценкой"""
        success, msg = self.db.add_sportsman_skill(self.test_user_id, "Бег", 15)
        self.assertFalse(success)

    def test_add_sportsman_skill_nonexistent(self):
        """Тест: добавление несуществующего навыка"""
        success, msg = self.db.add_sportsman_skill(self.test_user_id, "НесуществующийНавык", 8)
        self.assertFalse(success)

    def test_get_sportsman_skills(self):
        """Тест: получение навыков спортсмена"""
        self.db.add_sportsman_skill(self.test_user_id, "Бег", 8)
        self.db.add_sportsman_skill(self.test_user_id, "Сила", 7)
        skills = self.db.get_sportsman_skills(self.test_user_id)
        self.assertGreaterEqual(len(skills), 2)

    def test_update_sportsman_skill_rating(self):
        """Тест: обновление оценки навыка"""
        self.db.add_sportsman_skill(self.test_user_id, "Бег", 8)
        success, msg = self.db.update_sportsman_skill_rating(self.test_user_id, "Бег", 9)
        self.assertTrue(success)

    def test_delete_sportsman_skill(self):
        """Тест: удаление навыка"""
        self.db.add_sportsman_skill(self.test_user_id, "Бег", 8)
        success, msg = self.db.delete_sportsman_skill(self.test_user_id, "Бег")
        self.assertTrue(success)

    # 5. ТЕСТЫ КОМАНД

    def test_15_create_team_success(self):
        """Проверка: создание команды тренером"""
        print("\n[Тест] Создание команды")

        # Создаём тренера
        coach_email = f"coach_{int(time.time() * 1000)}@test.ru"
        success, msg, coach_id = self.db.register_user(
            email=coach_email,
            password="123456",
            last_name="Тренеров",
            first_name="Тренер",
            role="coach"
        )
        self.assertTrue(success, f"Не удалось создать тренера: {msg}")

        # Получаем ID любого вида спорта из базы
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM sports LIMIT 1")
            sport = cursor.fetchone()
            sport_id = sport['id'] if sport else None

        # Создаём команду
        success, msg, team_id = self.db.create_team(
            name="Тестовая команда",
            coach_user_id=coach_id,
            sport_id=sport_id
        )

        self.assertTrue(success, f"Не удалось создать команду: {msg}")
        print(f"  -> Создана команда: Тестовая команда (вид спорта ID: {sport_id})")

        # Чистим
        self.db.delete_user(coach_id)

    def test_create_team_not_coach(self):
        """Тест: создание команды не тренером - ошибка"""
        success, msg, team_id = self.db.create_team(
            name="ТестКоманда",
            coach_user_id=self.test_user_id
        )
        self.assertFalse(success)

    def test_add_member_to_team(self):
        """Тест: добавление спортсмена в команду"""
        import time
        coach_email = f"coach_{int(time.time() * 1000)}@test.ru"
        success, msg, coach_id = self.db.register_user(
            email=coach_email,
            password="123456",
            last_name="Тренеров",
            first_name="Тренер",
            role="coach"
        )
        self.assertTrue(success)

        success, msg, team_id = self.db.create_team(
            name="ТестКоманда",
            coach_user_id=coach_id
        )
        self.assertTrue(success)

        success, msg = self.db.add_member_to_team(team_id, self.test_user_id)
        self.assertTrue(success)

        self.db.delete_user(coach_id)

    # 6. ТЕСТЫ ЗАЯВОК

    def test_create_application(self):
        """Тест: подача заявки на вступление в команду"""
        import time
        coach_email = f"coach_{int(time.time() * 1000)}@test.ru"
        success, msg, coach_id = self.db.register_user(
            email=coach_email,
            password="123456",
            last_name="Тренеров",
            first_name="Тренер",
            role="coach"
        )
        self.assertTrue(success)

        success, msg, team_id = self.db.create_team(
            name="ТестКоманда",
            coach_user_id=coach_id
        )
        self.assertTrue(success)

        success, msg = self.db.create_application(team_id, self.test_user_id)
        self.assertTrue(success)

        self.db.delete_user(coach_id)

    # 7. ТЕСТЫ ОЦЕНОК ТРЕНЕРА

    def test_add_coach_assessment(self):
        """Тест: добавление оценки тренера"""
        import time
        coach_email = f"coach_{int(time.time() * 1000)}@test.ru"
        success, msg, coach_id = self.db.register_user(
            email=coach_email,
            password="123456",
            last_name="Тренеров",
            first_name="Тренер",
            role="coach"
        )
        self.assertTrue(success)

        success, msg = self.db.add_coach_assessment(
            coach_id=coach_id,
            sportsman_id=self.test_user_id,
            skill_name="Бег",
            rating=8
        )
        self.assertTrue(success)

        self.db.delete_user(coach_id)

    # 8. ТЕСТЫ ПОИСКА

    def test_get_all_users(self):
        """Тест: получение всех пользователей"""
        users = self.db.get_all_users()
        self.assertIsInstance(users, list)
        self.assertGreaterEqual(len(users), 1)

    def test_get_coaches(self):
        """Тест: получение всех тренеров"""
        coaches = self.db.get_coaches()
        self.assertIsInstance(coaches, list)

    def test_get_sportsmen(self):
        """Тест: получение всех спортсменов"""
        sportsmen = self.db.get_sportsmen()
        self.assertIsInstance(sportsmen, list)

    # 9. ТЕСТЫ СПРАВОЧНИКОВ

    def test_get_all_skills(self):
        """Тест: получение всех навыков"""
        skills = self.db.get_all_skills()
        self.assertIsInstance(skills, list)
        self.assertGreaterEqual(len(skills), 10)

    def test_get_all_sports(self):
        """Тест: получение всех видов спорта"""
        sports = self.db.get_all_sports()
        self.assertIsInstance(sports, list)
        self.assertGreaterEqual(len(sports), 10)

    # 10. ТЕСТЫ ОГРАНИЧЕНИЙ

    def test_foreign_key_constraint(self):
        """Тест: FOREIGN KEY - нельзя создать профиль без пользователя"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO profiles (user_id, last_name, first_name)
                    VALUES (99999, 'Тест', 'Тест')
                """)
                conn.commit()
                self.fail("Должна была быть ошибка FOREIGN KEY")
            except Exception as e:
                self.assertIn("foreign key", str(e).lower())


if __name__ == '__main__':
    import time

    unittest.main(verbosity=2)
