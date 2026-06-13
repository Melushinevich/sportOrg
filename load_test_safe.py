import time
from database import Database

db = Database()


def print_section(title):
    print(f" {title}")


def test_select_all_users():
    """
    Тест 1: Получаем всех пользователей
    Проверяем, как быстро БД отдаёт все записи
    """
    print_section("ТЕСТ 1: ВЫБОРКА ВСЕХ ПОЛЬЗОВАТЕЛЕЙ")

    start = time.time()
    users = db.get_all_users()
    elapsed = time.time() - start

    print(f"Найдено пользователей: {len(users)}")
    print(f"Время выполнения: {elapsed:.4f} сек")

    # Оцениваем результат
    if elapsed < 0.1:
        print("Вердикт: быстро, всё отлично")
    elif elapsed < 0.5:
        print("Вердикт: нормально, но можно быстрее")
    else:
        print("Вердикт: медленно, надо оптимизировать")

    return elapsed


def test_select_by_id():
    """
    Тест 2: Поиск пользователя по ID
    Здесь должен использоваться PRIMARY KEY индекс
    """
    print_section("ТЕСТ 2: ПОИСК ПО ID (первичный ключ)")

    # Сначала получим хотя бы одного пользователя
    users = db.get_all_users()
    if not users:
        print("Ошибка: в базе нет пользователей для теста")
        return None

    user_id = users[0]['id']

    start = time.time()
    user = db.get_user_by_id(user_id)
    elapsed = time.time() - start

    print(f"Ищем пользователя с ID = {user_id}")
    print(f"Время выполнения: {elapsed:.4f} сек")

    if elapsed < 0.01:
        print("Вердикт: отлично, индекс работает")
    elif elapsed < 0.05:
        print("Вердикт: нормально")
    else:
        print("Вердикт: медленно, возможно индекс не используется")

    return elapsed


def test_select_by_email():
    """
    Тест 3: Поиск пользователя по email
    Здесь должен использоваться UNIQUE индекс
    """
    print_section("ТЕСТ 3: ПОИСК ПО EMAIL (уникальный индекс)")

    users = db.get_all_users()
    if not users:
        print("Ошибка: в базе нет пользователей для теста")
        return None

    email = users[0]['email']

    start = time.time()
    user = db.get_user_by_email(email)
    elapsed = time.time() - start

    print(f"Ищем пользователя с email = {email}")
    print(f"Время выполнения: {elapsed:.4f} сек")

    if elapsed < 0.01:
        print("Вердикт: отлично")
    elif elapsed < 0.05:
        print("Вердикт: нормально")
    else:
        print("Вердикт: медленно")

    return elapsed


def test_join_query():
    """
    Тест 4: JOIN запрос
    Объединяем таблицы users и profiles
    """
    print_section("ТЕСТ 4: ОБЪЕДИНЕНИЕ ТАБЛИЦ (JOIN)")

    with db.get_connection() as conn:
        cursor = conn.cursor()

        start = time.time()
        cursor.execute("""
            SELECT u.id, u.email, u.role, p.last_name, p.first_name, p.city
            FROM users u
            LEFT JOIN profiles p ON u.id = p.user_id
            LIMIT 100
        """)
        results = cursor.fetchall()
        elapsed = time.time() - start

    print(f"Получено записей: {len(results)}")
    print(f"Время выполнения: {elapsed:.4f} сек")

    if elapsed < 0.05:
        print("Вердикт: отлично")
    elif elapsed < 0.2:
        print("Вердикт: нормально")
    else:
        print("Вердикт: медленно")

    return elapsed


def test_aggregation_query():
    """
    Тест 5: Группировка и подсчёт
    Считаем сколько пользователей с каждой ролью
    """
    print_section("ТЕСТ 5: ГРУППИРОВКА ДАННЫХ (GROUP BY)")

    with db.get_connection() as conn:
        cursor = conn.cursor()

        start = time.time()
        cursor.execute("""
            SELECT role, COUNT(*) as count
            FROM users
            GROUP BY role
        """)
        results = cursor.fetchall()
        elapsed = time.time() - start

    print(f"  Результатов: {len(results)}")
    for row in results:
        print(f"    {row['role']}: {row['count']} человек")
    print(f"  Время выполнения: {elapsed:.4f} сек")

    return elapsed


def test_search_like():
    """
    Тест 6: Поиск по шаблону LIKE
    Такие запросы обычно медленные, если нет специального индекса
    """
    print_section("ТЕСТ 6: ПОИСК ПО ШАБЛОНУ (LIKE)")

    with db.get_connection() as conn:
        cursor = conn.cursor()

        start = time.time()
        cursor.execute("""
            SELECT last_name, first_name FROM profiles 
            WHERE last_name LIKE '%ов%'
            LIMIT 50
        """)
        results = cursor.fetchall()
        elapsed = time.time() - start

    print(f"Найдено записей: {len(results)}")
    print(f"Время выполнения: {elapsed:.4f} сек")

    if elapsed < 0.1:
        print("Вердикт: отлично")
    elif elapsed < 0.3:
        print("Вердикт: нормально")
    else:
        print("Вердикт: медленно, возможно нужен индекс")

    return elapsed


def test_complex_query():
    """
    Тест 7: Сложный запрос с несколькими JOIN и агрегацией
    Проверяем, как БД справляется с тяжёлыми запросами
    """
    print_section("ТЕСТ 7: СЛОЖНЫЙ ЗАПРОС (JOIN + АГРЕГАЦИЯ)")

    with db.get_connection() as conn:
        cursor = conn.cursor()

        start = time.time()
        cursor.execute("""
            SELECT 
                u.email, 
                p.last_name, 
                p.first_name, 
                p.city,
                COUNT(ss.id) as skills_count,
                AVG(ss.self_rating) as avg_rating
            FROM users u
            LEFT JOIN profiles p ON u.id = p.user_id
            LEFT JOIN sportsman_skills ss ON u.id = ss.user_id
            WHERE u.role = 'sportsman'
            GROUP BY u.id, p.id
            ORDER BY avg_rating DESC NULLS LAST
            LIMIT 20
        """)
        results = cursor.fetchall()
        elapsed = time.time() - start

    print(f"Получено записей: {len(results)}")
    print(f"Время выполнения: {elapsed:.4f} сек")

    if elapsed < 0.1:
        print("Вердикт: отлично")
    elif elapsed < 0.3:
        print("Вердикт: нормально")
    else:
        print("Вердикт: медленно")

    return elapsed


def test_multiple_queries(num_queries=50):
    """
    Тест 8: Серия последовательных запросов
    Имитируем работу приложения, когда оно делает много запросов подряд
    """
    print_section(f"ТЕСТ 8: {num_queries} ПОСЛЕДОВАТЕЛЬНЫХ ЗАПРОСОВ")

    users = db.get_all_users()
    if not users:
        print("Ошибка: в базе нет пользователей для теста")
        return None

    print("Выполняем запросы: поиск по ID, по email, получение навыков...")

    start = time.time()
    for i in range(num_queries):
        # Чередуем разные типы запросов
        if i % 3 == 0:
            db.get_user_by_id(users[i % len(users)]['id'])
        elif i % 3 == 1:
            db.get_user_by_email(users[i % len(users)]['email'])
        else:
            db.get_sportsman_skills(users[i % len(users)]['id'])
    elapsed = time.time() - start

    print(f"Всего запросов: {num_queries}")
    print(f"Общее время: {elapsed:.4f} сек")
    print(f"Среднее время на запрос: {elapsed / num_queries:.4f} сек")

    return elapsed


def generate_report(results):
    """
    Формируем итоговый отчёт по всем тестам
    """
    print_section("ИТОГОВЫЙ ОТЧЁТ ПО НАГРУЗОЧНЫМ ТЕСТАМ")

    print("\n  Что проверяли и сколько времени заняло:")

    for name, value in results.items():
        if value is not None:
            if 'time' in name or 'elapsed' in name:
                print(f"    {name}: {value:.4f} сек")
            else:
                print(f"    {name}: {value}")

    # Анализируем результаты
    print(" Общий вывод:")

    slow_tests = 0
    for name, value in results.items():
        if 'time' in name and value is not None and value > 0.3:
            slow_tests += 1

    if slow_tests == 0:
        print("Отлично! Все запросы выполняются быстро.")
        print("База данных хорошо оптимизирована.")
    elif slow_tests <= 2:
        print("Хорошо, но некоторые запросы можно ускорить.")
        print("Рекомендую посмотреть на запросы с LIKE и сложные JOIN.")
    else:
        print("Внимание! Многие запросы работают медленно.")
        print("Рекомендации по оптимизации:")
        print("1. Добавить индексы на часто используемые поля")
        print("2. Переписать сложные JOIN запросы")
        print("3. Использовать EXPLAIN ANALYZE для анализа")


def run_all_tests():
    """
    Запускаем все тесты по порядку
    """
    print("ЗАПУСК НАГРУЗОЧНОГО ТЕСТИРОВАНИЯ")

    results = {}


    results['SELECT всех пользователей'] = test_select_all_users()
    results['SELECT по ID'] = test_select_by_id()
    results['SELECT по email'] = test_select_by_email()
    results['JOIN запрос'] = test_join_query()
    results['Агрегация GROUP BY'] = test_aggregation_query()
    results['Поиск LIKE'] = test_search_like()
    results['Сложный запрос'] = test_complex_query()
    results['Серия запросов'] = test_multiple_queries(50)

    generate_report(results)

    print("\n" + "=" * 60)
    print("     ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

    return results


if __name__ == '__main__':
    run_all_tests()
