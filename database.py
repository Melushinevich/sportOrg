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
        """Контекстный менеджер для работы с БД"""
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

            # 1. Таблица users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 2. Таблица profiles
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

            print("Таблицы созданы")

            # Индексы для быстрого поиска
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_profiles_last_name ON profiles(last_name)')


    def register_user(self, email, password, last_name, first_name, role='sportsman',
                      patronymic=None, birth_date=None, phone=None, city=None):
        # Проверка данных
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

        # Хешируем пароль
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # 1. Создаем пользователя в таблице users
                cursor.execute('''
                    INSERT INTO users (email, password_hash, role)
                    VALUES (%s, %s, %s)
                    RETURNING id
                ''', (email, password_hash, role))
                user_id = cursor.fetchone()['id']

                # 2. Создаем профиль в таблице profiles
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
        """Авторизация пользователя с получением данных профиля"""
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
        """Получить всех пользователей с их профилями"""
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
        """Получить пользователя по ID с его профилем"""
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
        """Получить пользователя по email с его профилем"""
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
        """Обновить профиль пользователя"""
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
        """Изменить роль пользователя"""
        if new_role not in ['sportsman', 'coach']:
            return False, "Роль должна быть sportsman или coach"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET role = %s WHERE id = %s
            ''', (new_role, user_id))
            return True, f"Роль изменена на {new_role}"

    def delete_user(self, user_id):
        """Удалить пользователя (каскадно удалится и профиль)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            return cursor.rowcount > 0

    def get_coaches(self):
        """Получить всех тренеров"""
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
        """Получить всех спортсменов"""
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

    def get_stats(self):
        """Статистика"""
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

            return {
                'total_users': total_users,
                'sportsmen': sportsmen,
                'coaches': coaches,
                'profiles_completed': profiles_count
            }


if __name__ == '__main__':
    print("ПОДКЛЮЧЕНИЕ К POSTGRESQL")

    db = Database()

    # 1. Регистрация спортсмена
    print("\n1. РЕГИСТРАЦИЯ СПОРТСМЕНА:")
    success, msg, user_id = db.register_user(
        email="ivan@mail.ru",
        password="123456",
        last_name="Петров",
        first_name="Иван",
        role="sportsman",
        patronymic="Иванович",
        birth_date="1995-05-15",
        phone="+7 (999) 123-45-67",
        city="Москва"
    )
    print(f"   {msg}")

    # 2. Регистрация тренера
    print("\n2. РЕГИСТРАЦИЯ ТРЕНЕРА:")
    success, msg, user_id = db.register_user(
        email="alex@mail.ru",
        password="123456",
        last_name="Смирнов",
        first_name="Алексей",
        role="coach",
        patronymic="Сергеевич",
        birth_date="1980-10-20",
        phone="+7 (999) 888-77-66",
        city="Санкт-Петербург"
    )
    print(f"   {msg}")

    # 3. Авторизация
    print("\n3. АВТОРИЗАЦИЯ:")
    success, user = db.login_user("ivan@mail.ru", "123456")
    if success:
        print(f"   Вход выполнен!")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   Роль: {user['role']}")
        print(f"   Имя: {user['last_name']} {user['first_name']}")
        print(f"   Город: {user['city']}")
    else:
        print(f" {user}")

    # 4. Все пользователи
    print("\n4. ВСЕ ПОЛЬЗОВАТЕЛИ:")
    for user in db.get_all_users():
        role_icon = "Тренер" if user['role'] == 'coach' else "🏃 Спортсмен"
        name = f"{user['last_name']} {user['first_name']}" if user['last_name'] else user['email']
        print(f"   {role_icon}: {name} - {user['email']}")

    # 5. Только тренеры
    print("\n5. СПИСОК ТРЕНЕРОВ:")
    for coach in db.get_coaches():
        print(f"   {coach['last_name']} {coach['first_name']} - {coach['email']}")

    # 6. Статистика
    print("\n6. СТАТИСТИКА:")
    stats = db.get_stats()
    print(f"   Всего пользователей: {stats['total_users']}")
    print(f"   Спортсменов: {stats['sportsmen']}")
    print(f"   Тренеров: {stats['coaches']}")
    print(f"   Заполненных профилей: {stats['profiles_completed']}")

    print("ГОТОВО!")
