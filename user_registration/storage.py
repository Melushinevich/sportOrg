import sqlite3
import os

DB_FILE = 'users.db'


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("бд инициализирована")


def get_user_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def create_new_user(user_data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (email, password_hash, first_name, last_name, phone, city)
        VALUES(?, ?, ?, ?, ?, ?)''',
                   (
                       user_data('email'),
                       user_data('password_hash'),
                       user_data('first_name'),
                       user_data('last_name'),
                       user_data.get('phone', ''),
                       user_data.get('first_name', '')
                   ))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_all_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users
    ''')
    rows = cursor.fetchall()
    conn.close()

    return (dict(row) for row in rows)

