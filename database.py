import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import hashlib


class Database:
    def __init__(self):
        self.connection_params = {
            'host': 'localhost',
            'port': 5500,
            'database': 'postgres',
            'user': 'postgres',
            'password': '12345678'
        }
        self.init_database()

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(**self.connection_params, cursor_factory=RealDictCursor)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Таблица 'users' создана")

            # 2. ТАБЛИЦА ПРОФИЛЕЙ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL UNIQUE,
                    last_name VARCHAR(100) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    patronymic VARCHAR(100),
                    birth_date DATE,
                    phone VARCHAR(20),
                    city VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            print("Таблица 'profiles' создана")

            # 3. ТАБЛИЦА НАВЫКОВ (справочник)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    description TEXT
                )
            ''')
            print("Таблица 'skills' создана")

            # 4. ТАБЛИЦА НАВЫКОВ СПОРТСМЕНА
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sportsman_skills (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    skill_id INTEGER NOT NULL,
                    self_rating INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
                    UNIQUE(user_id, skill_id)
                )
            ''')
            print("Таблица 'sportsman_skills' создана")

            # 5. ТАБЛИЦА ТРЕБОВАНИЙ ТРЕНЕРА
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS coach_requirements(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    skill_id INTEGER NOT NULL,
                    importance INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
                    UNIQUE(user_id, skill_id)
                )
            ''')
            print("Таблица 'coach_requirements' создана")

            # 6. ТАБЛИЦА ВИДОВ СПОРТА (справочник)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sports (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Таблица 'sports' создана")

            # 7. ТАБЛИЦА ТРЕБОВАНИЙ К ВИДАМ СПОРТА
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sport_requirements (
                    id SERIAL PRIMARY KEY,
                    sport_id INTEGER NOT NULL,
                    skill_id INTEGER NOT NULL,
                    min_value INTEGER DEFAULT 5,
                    weight FLOAT DEFAULT 1.0,
                    FOREIGN KEY (sport_id) REFERENCES sports(id) ON DELETE CASCADE,
                    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
                    UNIQUE(sport_id, skill_id)
                )
            ''')
            print("Таблица 'sport_requirements' создана")

            # БЕЗОПАСНЫЕ ИНДЕКСЫ (только для существующих колонок)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_profiles_last_name ON profiles(last_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sportsman_skills_user ON sportsman_skills(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_coach_requirements_user ON coach_requirements(user_id)')

            # Индексы для новых таблиц (без проверок)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sports_name ON sports(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sport_requirements_sport ON sport_requirements(sport_id)')

            print("Индексы созданы")

            # Заполняем справочники
            self._insert_skills(cursor)
            self._insert_sports(cursor)

    def _insert_skills(self, cursor):
        """Заполнение справочника навыков"""
        skills = [
            ('Командность', 'team', 'Умение работать в команде'),
            ('Индивидуальность', 'team', 'Самостоятельность в решениях'),
            ('Ответственность', 'personal', 'Ответственное отношение'),
            ('Посещаемость', 'personal', 'Регулярность посещения'),
            ('Результативность', 'game', 'Эффективность в игре'),
            ('Стрессоустойчивость', 'psychological', 'Хладнокровие'),
            ('Бег', 'physical', 'Скорость бега'),
            ('Ловкость', 'physical', 'Координация движений'),
            ('Выносливость', 'physical', 'Длительная нагрузка'),
            ('Сообразительность', 'psychological', 'Тактическое мышление'),
            ('Идейность', 'personal', 'Понимание стратегии'),
            ('Командный игрок', 'team', 'Ориентация на команду'),
            ('Идейный', 'personal', 'Генерация идей'),
            ('Уравновешенность', 'personal', 'Эмоциональный контроль'),
            ('Опыт', 'personal', 'Игровой стаж'),
            ('Скорость', 'physical', 'Быстрота реакции'),
            ('Сила', 'physical', 'Физическая мощь'),
            ('Качество броска', 'game', 'Точность броска'),
            ('Пас мяча', 'game', 'Точность передачи'),
            ('Сильный бросок мяча', 'game', 'Мощность удара'),
            ('Наличие инвентаря', 'equipment', 'Наличие гаджетов'),
            ('Возможность участия', 'availability', 'Готовность участвовать'),
        ]

        for name, category, desc in skills:
            cursor.execute('''
                INSERT INTO skills (name, category, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            ''', (name, category, desc))

        print(f"Добавлено навыков: {len(skills)}")

    def _insert_sports(self, cursor):
        """Заполнение справочника видов спорта"""
        sports = [
            ('Футбол (полевой игрок)', 'Командная игра с мячом'),
            ('Баскетбол', 'Командная игра с мячом в кольцо'),
            ('Хоккей', 'Командная игра с шайбой'),
            ('Теннис (одиночный)', 'Индивидуальная игра с ракеткой'),
            ('Биатлон', 'Лыжная гонка со стрельбой'),
            ('Волейбол', 'Командная игра с мячом через сетку'),
            ('Регби', 'Контактная командная игра'),
            ('Бокс', 'Единоборство'),
            ('Лёгкая атлетика (спринт)', 'Бег на короткие дистанции'),
            ('Спортивная гимнастика', 'Гимнастические упражнения'),
            ('Плавание', 'Соревновательное плавание'),
            ('Велоспорт', 'Велосипедные гонки'),
            ('VR', 'Спорт в виртуальной реальности'),
            ('Туристическая эстафета', 'Веревочное соревнование'),
            ('Взятие города Ж/М', 'Командная игра с кубом и мячом'),
            ('Русская лапта', 'Командная игра с битой и теннисным мячом'),
            ('Ярославская лапта', 'Разновидность лапты'),
            ('Тайский футбол', 'Командная игра с элементами футбола через сетку'),
            ('Бочча', 'Игра на точность'),
            ('Корнхолл', 'Метание мешочков'),
            ('Бигбол', 'Игра с большим мячом через сетку'),
            ('Классик', 'Толкание дисков шваброй'),
            ('Ринго', 'Метание кольца через сетку'),
            ('Лазертаг', 'Командная игра с лазерным оружием'),
            ('Дневной дозор', 'Командная игра на местности'),
            ('Командный интенсив', 'Соревнования на физическую активность'),
        ]

        for name, desc in sports:
            cursor.execute('''
                INSERT INTO sports (name, description)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING
            ''', (name, desc))

        print(f"Добавлено видов спорта: {len(sports)}")

    # МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
    def register_user(self, email, password, last_name, first_name, role='sportsman',
                      patronymic=None, birth_date=None, phone=None, city=None):
        if not email or '@' not in email:
            return False, "Введите корректный email", None
        if not password or len(password) < 4:
            return False, "Пароль должен быть не менее 4 символов", None
        if not last_name or len(last_name) < 2:
            return False, "Введите фамилию", None
        if not first_name or len(first_name) < 2:
            return False, "Введите имя", None
        if role not in ['sportsman', 'coach']:
            return False, "Выберите роль: sportsman или coach", None

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (email, password_hash, role)
                    VALUES (%s, %s, %s)
                    RETURNING id
                ''', (email, password_hash, role))
                user_id = cursor.fetchone()['id']

                cursor.execute('''
                    INSERT INTO profiles (user_id, last_name, first_name, patronymic, 
                                         birth_date, phone, city)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (user_id, last_name, first_name, patronymic,
                      birth_date, phone, city))

                role_text = "тренер" if role == 'coach' else "спортсмен"
                return True, f"{role_text} {last_name} {first_name} успешно зарегистрирован!", user_id

            except psycopg2.IntegrityError as e:
                if 'email' in str(e):
                    return False, "Пользователь с таким email уже существует", None
                return False, f"Ошибка: {e}", None

    def login_user(self, email, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.role, u.created_at,
                       p.last_name, p.first_name, p.patronymic, 
                       p.birth_date, p.phone, p.city
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.email = %s AND u.password_hash = %s
            ''', (email, password_hash))

            user = cursor.fetchone()
            if user:
                return True, dict(user)
            return False, "Неверный email или пароль"

    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.role, u.created_at,
                       p.last_name, p.first_name, p.patronymic, 
                       p.birth_date, p.phone, p.city
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                ORDER BY u.id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_user_by_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.role, u.created_at,
                       p.last_name, p.first_name, p.patronymic, 
                       p.birth_date, p.phone, p.city
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.id = %s
            ''', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_email(self, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.role, u.created_at,
                       p.last_name, p.first_name, p.patronymic, 
                       p.birth_date, p.phone, p.city
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.email = %s
            ''', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_profile(self, user_id, **kwargs):
        allowed_fields = ['last_name', 'first_name', 'patronymic',
                          'birth_date', 'phone', 'city']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not updates:
            return False, "Нет данных для обновления"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [user_id]

            cursor.execute(f'''
                UPDATE profiles 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            ''', values)

            return True, "Профиль обновлен"

    def update_user_role(self, user_id, new_role):
        if new_role not in ['sportsman', 'coach']:
            return False, "Роль должна быть sportsman или coach"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET role = %s WHERE id = %s
            ''', (new_role, user_id))
            return True, f"Роль изменена на {new_role}"

    def delete_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            return cursor.rowcount > 0

    def get_coaches(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.created_at,
                       p.last_name, p.first_name, p.city, p.phone
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.role = 'coach'
                ORDER BY p.last_name
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_sportsmen(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.created_at,
                       p.last_name, p.first_name, p.city, p.phone
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.role = 'sportsman'
                ORDER BY p.last_name
            ''')
            return [dict(row) for row in cursor.fetchall()]

    # МЕТОДЫ ДЛЯ НАВЫКОВ СПОРТСМЕНА
    def add_sportsman_skill(self, user_id, skill_name, self_rating=5):
        """Спортсмен выбирает навык и оценивает себя (1-10)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM skills WHERE name = %s", (skill_name,))
            skill = cursor.fetchone()
            if not skill:
                return False, f"Навык '{skill_name}' не найден"

            if self_rating < 1 or self_rating > 10:
                return False, "Оценка должна быть от 1 до 10"

            cursor.execute('''
                INSERT INTO sportsman_skills (user_id, skill_id, self_rating)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, skill_id) 
                DO UPDATE SET self_rating = %s, updated_at = CURRENT_TIMESTAMP
            ''', (user_id, skill['id'], self_rating, self_rating))

            return True, f"Навык '{skill_name}' добавлен с оценкой {self_rating}/10"

    def get_sportsman_skills(self, user_id):
        """Получить все навыки спортсмена с его оценками"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.name, s.category, s.description, 
                       ss.self_rating, ss.created_at, ss.updated_at
                FROM sportsman_skills ss
                JOIN skills s ON ss.skill_id = s.id
                WHERE ss.user_id = %s
                ORDER BY ss.self_rating DESC, s.category
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_sportsman_skill_rating(self, user_id, skill_name, new_rating):
        """Спортсмен обновляет свою оценку по навыку"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM skills WHERE name = %s", (skill_name,))
            skill = cursor.fetchone()
            if not skill:
                return False, f"Навык '{skill_name}' не найден"

            if new_rating < 1 or new_rating > 10:
                return False, "Оценка должна быть от 1 до 10"

            cursor.execute('''
                UPDATE sportsman_skills 
                SET self_rating = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND skill_id = %s
            ''', (new_rating, user_id, skill['id']))

            if cursor.rowcount == 0:
                return False, f"Навык '{skill_name}' не найден у пользователя"

            return True, f"Оценка по навыку '{skill_name}' обновлена на {new_rating}/10"

    def delete_sportsman_skill(self, user_id, skill_name):
        """Спортсмен удаляет навык из своего профиля"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM skills WHERE name = %s", (skill_name,))
            skill = cursor.fetchone()
            if not skill:
                return False, f"Навык '{skill_name}' не найден"

            cursor.execute('''
                DELETE FROM sportsman_skills 
                WHERE user_id = %s AND skill_id = %s
            ''', (user_id, skill['id']))

            if cursor.rowcount == 0:
                return False, f"Навык '{skill_name}' не найден у пользователя"

            return True, f"Навык '{skill_name}' удален"

    def get_sportsman_profile_full(self, user_id):
        """Получить полный профиль спортсмена (личные данные + навыки)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT u.id, u.email, u.role, u.created_at,
                       p.last_name, p.first_name, p.patronymic, 
                       p.birth_date, p.phone, p.city
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.id = %s AND u.role = 'sportsman'
            ''', (user_id,))
            user = cursor.fetchone()

            if not user:
                return None

            result = dict(user)

            cursor.execute('''
                SELECT s.name, s.category, ss.self_rating, ss.updated_at
                FROM sportsman_skills ss
                JOIN skills s ON ss.skill_id = s.id
                WHERE ss.user_id = %s
                ORDER BY ss.self_rating DESC, s.category
            ''', (user_id,))
            result['skills'] = [dict(row) for row in cursor.fetchall()]

            return result

    #  МЕТОДЫ ДЛЯ ТРЕБОВАНИЙ ТРЕНЕРА
    def add_coach_requirement(self, user_id, skill_name, importance=5):
        """Тренер добавляет требование к спортсмену"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM skills WHERE name = %s", (skill_name,))
            skill = cursor.fetchone()
            if not skill:
                return False, f"Навык '{skill_name}' не найден"

            if importance < 1 or importance > 10:
                return False, "Важность должна быть от 1 до 10"

            cursor.execute('''
                INSERT INTO coach_requirements (user_id, skill_id, importance)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, skill_id) 
                DO UPDATE SET importance = %s, created_at = CURRENT_TIMESTAMP
            ''', (user_id, skill['id'], importance, importance))

            return True, f"Требование '{skill_name}' важность {importance}/10"

    def get_coach_requirements(self, user_id):
        """Получить требования тренера"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.name, s.category, cr.importance, cr.created_at
                FROM coach_requirements cr
                JOIN skills s ON cr.skill_id = s.id
                WHERE cr.user_id = %s
                ORDER BY cr.importance DESC, s.category
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_coach_requirement(self, user_id, skill_name):
        """Удалить требование тренера"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM skills WHERE name = %s", (skill_name,))
            skill = cursor.fetchone()
            if not skill:
                return False, f"Навык '{skill_name}' не найден"

            cursor.execute('''
                DELETE FROM coach_requirements 
                WHERE user_id = %s AND skill_id = %s
            ''', (user_id, skill['id']))

            return True, f"Требование '{skill_name}' удалено"

    def get_all_sports(self):
        """Получить все виды спорта"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sports ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]

    # МЕТОДЫ ДЛЯ СПРАВОЧНИКОВ
    def get_all_skills(self):
        """Получить все навыки из справочника"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM skills ORDER BY category, name')
            return [dict(row) for row in cursor.fetchall()]

    def get_skills_by_category(self, category):
        """Получить навыки по категории"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM skills WHERE category = %s ORDER BY name', (category,))
            return [dict(row) for row in cursor.fetchall()]

    # МЕТОДЫ ДЛЯ ПОИСКА И СООТВЕТСТВИЯ
    def find_matching_sportsmen(self, coach_id):
        """Найти спортсменов, подходящих под требования тренера"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT skill_id, importance
                FROM coach_requirements
                WHERE user_id = %s
            ''', (coach_id,))
            requirements = cursor.fetchall()

            if not requirements:
                return []

            cursor.execute('''
                SELECT u.id, p.first_name, p.last_name
                FROM users u
                JOIN profiles p ON u.id = p.user_id
                WHERE u.role = 'sportsman'
            ''')
            sportsmen = cursor.fetchall()

            results = []
            for sportsman in sportsmen:
                total_score = 0
                max_score = 0

                for req in requirements:
                    max_score += req['importance'] * 10

                    cursor.execute('''
                        SELECT self_rating FROM sportsman_skills 
                        WHERE user_id = %s AND skill_id = %s
                    ''', (sportsman['id'], req['skill_id']))
                    skill = cursor.fetchone()

                    if skill:
                        rating = skill['self_rating']
                        total_score += rating * req['importance']

                match_percent = (total_score / max_score * 100) if max_score > 0 else 0

                results.append({
                    'sportsman_id': sportsman['id'],
                    'first_name': sportsman['first_name'],
                    'last_name': sportsman['last_name'],
                    'match_percent': round(match_percent, 1)
                })

            results.sort(key=lambda x: x['match_percent'], reverse=True)
            return results

    def get_stats(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM users WHERE role = \'sportsman\'')
            sportsmen = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM users WHERE role = \'coach\'')
            coaches = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM profiles')
            profiles_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM sportsman_skills')
            skills_assigned = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM coach_requirements')
            requirements_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM sports')
            sports_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM skills')
            skills_count = cursor.fetchone()['count']

            return {
                'total_users': total_users,
                'sportsmen': sportsmen,
                'coaches': coaches,
                'profiles_completed': profiles_count,
                'skills_assigned': skills_assigned,
                'coach_requirements': requirements_count,
                'total_sports': sports_count,
                'total_skills': skills_count
            }


if __name__ == '__main__':
    db = Database()
    print("\n ИТОГОВАЯ СТАТИСТИКА:")
    stats = db.get_stats()
    print(f"   Всего пользователей: {stats['total_users']}")
    print(f"   Спортсменов: {stats['sportsmen']}")
    print(f"   Тренеров: {stats['coaches']}")
    print(f"   Заполненных профилей: {stats['profiles_completed']}")
    print(f"   Всего навыков в системе: {stats['total_skills']}")
    print(f"   Всего видов спорта: {stats['total_sports']}")
    print(f"   Назначено навыков: {stats['skills_assigned']}")
    print(f"   Требований тренеров: {stats['coach_requirements']}")
