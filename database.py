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

            # 1. Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Таблица 'users' создана")

            # 2. Таблица профилей
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
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            print("Таблица 'profiles' создана")

            # 3. Таблица навыков (справочник)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    description TEXT
                )
            ''')
            print("Таблица 'skills' создана")

            # 4. Таблица навыков спортсмена (самооценка)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sportsman_skills (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    skill_id INTEGER NOT NULL,
                    self_rating INTEGER DEFAULT 5,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
                    UNIQUE(user_id, skill_id)
                )
            ''')
            print("Таблица 'sportsman_skills' создана")

            # 5. Таблица требований тренера
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS coach_requirements(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    skill_id INTEGER NOT NULL,
                    importance INTEGER DEFAULT 5,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
                    UNIQUE(user_id, skill_id)
                )
            ''')
            print("Таблица 'coach_requirements' создана")

            # 6. Таблица видов спорта (справочник)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sports (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Таблица 'sports' создана")

            # 7. Таблица требований к видам спорта
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

            # 8. Таблица команд
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    coach_user_id INTEGER NOT NULL,
                    sport_id INTEGER,
                    members_count INTEGER NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (coach_user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (sport_id) REFERENCES sports(id) ON DELETE SET NULL
                )
            ''')
            print("Таблица 'teams' создана")

            # 9. Таблица участников команд
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_members (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER NOT NULL,
                    athlete_user_id INTEGER NOT NULL,
                    notes TEXT,
                    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    FOREIGN KEY (athlete_user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(team_id, athlete_user_id)
                )
            ''')
            print("Таблица 'team_members' создана")

            # 10. Таблица оценок тренера
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS coach_assessments (
                    id SERIAL PRIMARY KEY,
                    coach_id INTEGER NOT NULL,
                    sportsman_id INTEGER NOT NULL,
                    skill_id INTEGER NOT NULL,
                    rating INTEGER DEFAULT 5,
                    comment TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (coach_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (sportsman_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
                    UNIQUE(coach_id, sportsman_id, skill_id)
                )
            ''')
            print("Таблица 'coach_assessments' создана")

            # 11. Таблица заявок на вступление в команду
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_applications (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER NOT NULL,
                    athlete_user_id INTEGER NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    FOREIGN KEY (athlete_user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(team_id, athlete_user_id)
                )
            ''')
            print("Таблица 'team_applications' создана")

            # 12. Таблица критериев отбора в команду
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_criteria (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER NOT NULL,
                    text VARCHAR(300) NOT NULL DEFAULT '',
                    sort_order INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
                )
            ''')
            print("Таблица 'team_criteria' создана")

            print("\nВсе 12 таблиц созданы")

            # Индексы
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_profiles_last_name ON profiles(last_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sportsman_skills_user ON sportsman_skills(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_coach_requirements_user ON coach_requirements(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sports_name ON sports(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sport_requirements_sport ON sport_requirements(sport_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_teams_coach_user ON teams(coach_user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_teams_sport ON teams(sport_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_members_athlete ON team_members(athlete_user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_coach_assessments_coach ON coach_assessments(coach_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_coach_assessments_sportsman ON coach_assessments(sportsman_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_applications_team ON team_applications(team_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_applications_athlete ON team_applications(athlete_user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_applications_status ON team_applications(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_criteria_team ON team_criteria(team_id)')

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
            ('Сила', 'physical', 'Физическая мощь'),
            ('Бросок', 'game', 'Точность броска'),
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
            ('Футбол', 'Командная игра с мячом'),
            ('Баскетбол', 'Командная игра с мячом в кольцо'),
            ('Хоккей', 'Командная игра с шайбой'),
            ('Настольный теннис', 'Индивидуальная игра с ракеткой'),
            ('Большой теннис', 'Индивидуальная игра с ракеткой'),
            ('Биатлон', 'Лыжная гонка с элементами стрельбы'),
            ('Волейбол', 'Командная игра с мячом через сетку'),
            ('Регби', 'Контактная командная игра'),
            ('Бокс', 'Единоборство'),
            ('Лёгкая атлетика (спринт)', 'Бег на короткие дистанции'),
            ('Лёгкая атлетика (стайер)', 'Бег на длинные дистанции'),
            ('Спортивная гимнастика', 'Гимнастические упражнения'),
            ('Плавание', 'Преодоление дистанций вплавь'),
            ('Велоспорт', 'Велосипедные гонки'),
            ('VR', 'Спорт в виртуальной реальности'),
            ('Туристическая эстафета', 'Командное прохождение эстафеты'),
            ('Взятие города Ж/М', 'Командная игра с кубом и мячом'),
            ('Русская лапта', 'Командная игра с битой и мячом'),
            ('Ярославская лапта', 'Разновидность русской лапты'),
            ('Тайский футбол', 'Футбол с элементами через сетку'),
            ('Бочча', 'Игра на точность'),
            ('Корнхолл', 'Метание мешочков'),
            ('Бигбол', 'Игра с большим мячом через сетку'),
            ('Классик', 'Альтернатива керлингу'),
            ('Ринго', 'Метание резинового кольца'),
            ('Лазертаг', 'Командная игра с лазерным оружием'),
            ('Дневной дозор', 'Командная игра-квест по городу'),
            ('Командный интенсив', 'Соревнования на физическую активность'),
        ]

        for name, desc in sports:
            cursor.execute('''
                INSERT INTO sports (name, description)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING
            ''', (name, desc))

        print(f"Добавлено видов спорта: {len(sports)}")

    # =========================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
    # =========================================================

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
                return True, f"{role_text} {last_name} {first_name} успешно зарегистрирован", user_id

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

    # =========================================================
    # МЕТОДЫ ДЛЯ НАВЫКОВ СПОРТСМЕНА (самооценка)
    # =========================================================

    def add_sportsman_skill(self, user_id, skill_name, self_rating=5):
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

    # =========================================================
    # МЕТОДЫ ДЛЯ ТРЕБОВАНИЙ ТРЕНЕРА
    # =========================================================

    def add_coach_requirement(self, user_id, skill_name, importance=5):
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

    # =========================================================
    # МЕТОДЫ ДЛЯ ОЦЕНОК ТРЕНЕРА
    # =========================================================

    def add_coach_assessment(self, coach_id, sportsman_id, skill_name, rating, comment=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT role FROM users WHERE id = %s", (coach_id,))
            user = cursor.fetchone()
            if not user or user['role'] != 'coach':
                return False, "Только тренер может оценивать"

            cursor.execute("SELECT id FROM skills WHERE name = %s", (skill_name,))
            skill = cursor.fetchone()
            if not skill:
                return False, f"Навык '{skill_name}' не найден"

            if rating < 1 or rating > 10:
                return False, "Оценка должна быть от 1 до 10"

            cursor.execute('''
                INSERT INTO coach_assessments (coach_id, sportsman_id, skill_id, rating, comment)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (coach_id, sportsman_id, skill_id) 
                DO UPDATE SET rating = %s, comment = %s, updated_at = CURRENT_TIMESTAMP
            ''', (coach_id, sportsman_id, skill['id'], rating, comment, rating, comment))

            return True, f"Оценка '{skill_name}' = {rating}/10"

    def get_sportsman_assessments(self, sportsman_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ca.*, s.name as skill_name, 
                       u.first_name as coach_first_name, u.last_name as coach_last_name
                FROM coach_assessments ca
                JOIN skills s ON ca.skill_id = s.id
                JOIN users u ON ca.coach_id = u.id
                WHERE ca.sportsman_id = %s
                ORDER BY ca.created_at DESC
            ''', (sportsman_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_coach_assessments(self, coach_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ca.*, s.name as skill_name,
                       p.first_name as sportsman_first_name, p.last_name as sportsman_last_name
                FROM coach_assessments ca
                JOIN skills s ON ca.skill_id = s.id
                JOIN profiles p ON ca.sportsman_id = p.user_id
                WHERE ca.coach_id = %s
                ORDER BY ca.created_at DESC
            ''', (coach_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_average_rating_for_sportsman(self, sportsman_id, skill_name=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if skill_name:
                cursor.execute('''
                    SELECT AVG(ca.rating) as avg_rating
                    FROM coach_assessments ca
                    JOIN skills s ON ca.skill_id = s.id
                    WHERE ca.sportsman_id = %s AND s.name = %s
                ''', (sportsman_id, skill_name))
                return cursor.fetchone()['avg_rating'] if cursor.fetchone() else None
            else:
                cursor.execute('''
                    SELECT s.name, AVG(ca.rating) as avg_rating
                    FROM coach_assessments ca
                    JOIN skills s ON ca.skill_id = s.id
                    WHERE ca.sportsman_id = %s
                    GROUP BY s.name
                    ORDER BY s.name
                ''', (sportsman_id,))
                return [dict(row) for row in cursor.fetchall()]

    # =========================================================
    # МЕТОДЫ ДЛЯ СПРАВОЧНИКОВ
    # =========================================================

    def get_all_skills(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM skills ORDER BY category, name')
            return [dict(row) for row in cursor.fetchall()]

    def get_skills_by_category(self, category):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM skills WHERE category = %s ORDER BY name', (category,))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_sports(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sports ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С КОМАНДАМИ
    # =========================================================

    def create_team(self, name, coach_user_id, sport_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT role FROM users WHERE id = %s", (coach_user_id,))
            user = cursor.fetchone()
            if not user or user['role'] != 'coach':
                return False, "Только тренер может создать команду", None

            cursor.execute('''
                INSERT INTO teams (name, coach_user_id, sport_id, members_count)
                VALUES (%s, %s, %s, 1)
                RETURNING id
            ''', (name, coach_user_id, sport_id))

            team_id = cursor.fetchone()['id']

            cursor.execute('''
                INSERT INTO team_members (team_id, athlete_user_id)
                VALUES (%s, %s)
            ''', (team_id, coach_user_id))

            return True, f"Команда '{name}' создана", team_id

    def add_member_to_team(self, team_id, athlete_user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute('''
                    INSERT INTO team_members (team_id, athlete_user_id, notes)
                    VALUES (%s, %s, NULL)
                ''', (team_id, athlete_user_id))

                cursor.execute('''
                    UPDATE teams SET members_count = members_count + 1
                    WHERE id = %s
                ''', (team_id,))

                return True, "Игрок добавлен в команду"
            except Exception as e:
                return False, f"Ошибка: {e}"

    def remove_member_from_team(self, team_id, athlete_user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute('''
                    DELETE FROM team_members 
                    WHERE team_id = %s AND athlete_user_id = %s
                ''', (team_id, athlete_user_id))

                cursor.execute('''
                    UPDATE teams SET members_count = members_count - 1
                    WHERE id = %s
                ''', (team_id,))

                return True, "Игрок удален из команды"
            except Exception as e:
                return False, f"Ошибка: {e}"

    def get_team_members(self, team_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, p.first_name, p.last_name, tm.notes, tm.joined_at
                FROM team_members tm
                JOIN users u ON tm.athlete_user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE tm.team_id = %s
                ORDER BY p.last_name
            ''', (team_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_member_notes(self, team_id, athlete_user_id, notes):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE team_members 
                SET notes = %s
                WHERE team_id = %s AND athlete_user_id = %s
            ''', (notes, team_id, athlete_user_id))
            return True, "Заметки обновлены"

    def get_team_by_id(self, team_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, s.name as sport_name,
                       u.first_name as coach_first_name, u.last_name as coach_last_name
                FROM teams t
                LEFT JOIN sports s ON t.sport_id = s.id
                LEFT JOIN users u ON t.coach_user_id = u.id
                WHERE t.id = %s
            ''', (team_id,))
            return dict(cursor.fetchone()) if cursor.fetchone() else None

    def get_all_teams(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, s.name as sport_name,
                       (SELECT COUNT(*) FROM team_members WHERE team_id = t.id) as member_count
                FROM teams t
                LEFT JOIN sports s ON t.sport_id = s.id
                ORDER BY t.created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_coach_teams(self, coach_user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, s.name as sport_name,
                       (SELECT COUNT(*) FROM team_members WHERE team_id = t.id) as member_count
                FROM teams t
                LEFT JOIN sports s ON t.sport_id = s.id
                WHERE t.coach_user_id = %s
                ORDER BY t.created_at DESC
            ''', (coach_user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_teams_by_sport(self, sport_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, s.name as sport_name,
                       (SELECT COUNT(*) FROM team_members WHERE team_id = t.id) as member_count
                FROM teams t
                LEFT JOIN sports s ON t.sport_id = s.id
                WHERE t.sport_id = %s
                ORDER BY t.created_at DESC
            ''', (sport_id,))
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================
    # МЕТОДЫ ДЛЯ ЗАЯВОК В КОМАНДУ
    # =========================================================

    def create_application(self, team_id, athlete_user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT role FROM users WHERE id = %s", (athlete_user_id,))
            user = cursor.fetchone()
            if not user or user['role'] != 'sportsman':
                return False, "Только спортсмен может подать заявку"

            try:
                cursor.execute('''
                    INSERT INTO team_applications (team_id, athlete_user_id, status)
                    VALUES (%s, %s, 'pending')
                ''', (team_id, athlete_user_id))
                return True, "Заявка подана"
            except Exception as e:
                return False, f"Ошибка: {e}"

    def update_application_status(self, team_id, athlete_user_id, status, coach_user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT role FROM users WHERE id = %s", (coach_user_id,))
            user = cursor.fetchone()
            if not user or user['role'] != 'coach':
                return False, "Только тренер может менять статус заявки"

            if status not in ['approved', 'rejected']:
                return False, "Статус должен быть 'approved' или 'rejected'"

            cursor.execute('''
                UPDATE team_applications 
                SET status = %s
                WHERE team_id = %s AND athlete_user_id = %s
            ''', (status, team_id, athlete_user_id))

            if status == 'approved':
                self.add_member_to_team(team_id, athlete_user_id)

            return True, f"Заявка {status}"

    def get_team_applications(self, team_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ta.*, u.email, p.first_name, p.last_name, p.city
                FROM team_applications ta
                JOIN users u ON ta.athlete_user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE ta.team_id = %s
                ORDER BY ta.created_at DESC
            ''', (team_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_user_applications(self, athlete_user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ta.*, t.name as team_name
                FROM team_applications ta
                JOIN teams t ON ta.team_id = t.id
                WHERE ta.athlete_user_id = %s
                ORDER BY ta.created_at DESC
            ''', (athlete_user_id,))
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================
    # МЕТОДЫ ДЛЯ КРИТЕРИЕВ КОМАНДЫ
    # =========================================================

    def add_team_criterion(self, team_id, text, sort_order=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO team_criteria (team_id, text, sort_order)
                VALUES (%s, %s, %s)
                RETURNING id
            ''', (team_id, text, sort_order))
            return True, "Критерий добавлен", cursor.fetchone()['id']

    def get_team_criteria(self, team_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM team_criteria
                WHERE team_id = %s
                ORDER BY sort_order, id
            ''', (team_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_team_criterion(self, criterion_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM team_criteria WHERE id = %s', (criterion_id,))
            return True, "Критерий удален"

    # =========================================================
    # МЕТОДЫ ДЛЯ ПОИСКА И СООТВЕТСТВИЯ
    # =========================================================

    def find_matching_sportsmen(self, coach_id):
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

    # =========================================================
    # СТАТИСТИКА
    # =========================================================

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

            cursor.execute('SELECT COUNT(*) FROM teams')
            teams_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM team_members')
            team_members_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM coach_assessments')
            coach_assessments_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM team_applications')
            team_applications_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) FROM team_criteria')
            team_criteria_count = cursor.fetchone()['count']

            return {
                'total_users': total_users,
                'sportsmen': sportsmen,
                'coaches': coaches,
                'profiles_completed': profiles_count,
                'skills_assigned': skills_assigned,
                'coach_requirements': requirements_count,
                'total_sports': sports_count,
                'total_skills': skills_count,
                'total_teams': teams_count,
                'total_team_members': team_members_count,
                'coach_assessments': coach_assessments_count,
                'team_applications': team_applications_count,
                'team_criteria': team_criteria_count
            }


if __name__ == '__main__':
    print("=" * 50)
    print("ПОДКЛЮЧЕНИЕ К POSTGRESQL")
    print("=" * 50)

    db = Database()

    print("\nИТОГОВАЯ СТАТИСТИКА:")
    stats = db.get_stats()
    print(f"   Всего пользователей: {stats['total_users']}")
    print(f"   Спортсменов: {stats['sportsmen']}")
    print(f"   Тренеров: {stats['coaches']}")
    print(f"   Заполненных профилей: {stats['profiles_completed']}")
    print(f"   Всего навыков в системе: {stats['total_skills']}")
    print(f"   Всего видов спорта: {stats['total_sports']}")
    print(f"   Назначено навыков (самооценка): {stats['skills_assigned']}")
    print(f"   Требований тренеров: {stats['coach_requirements']}")
    print(f"   Команд: {stats['total_teams']}")
    print(f"   Участников команд: {stats['total_team_members']}")
    print(f"   Оценок тренеров: {stats['coach_assessments']}")
    print(f"   Заявок в команды: {stats['team_applications']}")
    print(f"   Критериев команд: {stats['team_criteria']}")

    print("\nБаза данных готова к работе")