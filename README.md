# SPORTORG

Десктоп-приложение (PyQt5) для подбора спортивных команд и REST API (Flask) с PostgreSQL.

- **Спортсмен:** регистрация, анкета, навыки, поиск команд, заявки в команды.
- **Тренер:** регистрация, анкета, создание команд и критериев, просмотр откликов, оценка участников, экспорт состава в PDF.

## Требования

- Python **3.10+**
- PostgreSQL (в проекте — общая БД, доступ по **Tailscale** или локальной сети)
- macOS / Linux / Windows (UI проверялся в первую очередь на macOS)

## Быстрый старт

### 1. Клонирование и окружение

```bash
git clone <url-репозитория>
cd SportOrg

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Переменные окружения

Скопируйте пример и отредактируйте под свою среду:

```bash
cp .env.example .env
```

| Переменная | Назначение |
|------------|------------|
| `SPORTORG_API_URL` | URL Flask API для десктоп-клиента (по умолчанию `http://127.0.0.1:5000`) |
| `SPORTORG_DB_HOST` | Хост PostgreSQL (Tailscale-имя или IP) |
| `SPORTORG_DB_PORT` | Порт PostgreSQL (по умолчанию `5500`) |
| `SPORTORG_DB_NAME` | Имя базы |
| `SPORTORG_DB_USER` | Пользователь БД |
| `SPORTORG_DB_PASSWORD` | Пароль БД |

Альтернатива — одна строка `DATABASE_URL=postgresql://user:pass@host:port/dbname`.

**Tailscale:** участники команды подключаются к одной БД по стабильному имени хоста в VPN (см. `.env.example`), без привязки к локальному IP.

**macOS:** порт `5000` часто занят AirPlay Receiver. Если API не стартует, в `.env` укажите:

```env
SPORTORG_API_URL=http://127.0.0.1:5001
```

и запускайте Flask на порту `5001` (см. ниже).

### 3. Запуск (рекомендуется)

API и десктоп одной командой — API поднимается первым, затем ждёт `/api/v1/health` и открывает UI:

```bash
python run_dev.py
```

### 4. Запуск по отдельности

**Только API:**

```bash
flask --app app run --host 127.0.0.1 --port 5000
```

Другой порт (например, на Mac):

```bash
flask --app app run --host 127.0.0.1 --port 5001
```

**Только десктоп** (API уже должен работать, `SPORTORG_API_URL` в `.env`):

```bash
python run_frontend.py
```

## Проверка API

```bash
curl http://127.0.0.1:5000/api/v1/health
```

Ожидается ответ `200` с JSON.

## Тесты

**Важно:** команды ниже — только из **корня репозитория** (там, где лежат `app.py`, `tests/` и `requirements.txt`).  
Если запускать из папки `sportorg/` или другой поддиректории, pytest напишет `collected 0 items`, покрытие будет **0%** — это не баг проекта, а неверная рабочая директория.

```bash
cd /path/to/SportOrg
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen python -m pytest
```

Удобная обёртка (всегда стартует из корня):

```bash
python run_tests.py
```

В `pytest.ini` заданы `pythonpath = .` и `qt_api = pyqt5` (приложение на PyQt5; без этого pytest-qt может подхватить PySide6 и упасть с `Abort trap`).

Общее покрытие кода проекта (`sportorg`, `user_registration`, `frontend`) — **не ниже 65%** (см. `pytest.ini`).

Для headless Qt (CI / без дисплея):

```bash
QT_QPA_PLATFORM=offscreen pytest
```

## Структура проекта

```
SportOrg/
├── app.py                 # точка входа Flask CLI
├── run_dev.py             # API + десктоп
├── run_frontend.py        # только PyQt5-клиент
├── run_tests.py           # pytest из корня (удобно, если cwd другой)
├── sportorg/              # Flask-приложение, JWT, blueprints API
├── user_registration/     # регистрация, storage PostgreSQL
├── frontend/              # PyQt5 UI, навигация, HTTP-клиент
├── tests/                 # pytest
└── .env.example           # шаблон переменных окружения
```

## Дополнительные переменные (опционально)

| Переменная | Назначение |
|------------|------------|
| `FLASK_SECRET_KEY` | секрет Flask-сессий |
| `JWT_SECRET_KEY` | подпись JWT-токенов |
| `JWT_TTL_HOURS` | время жизни токена (часы) |
| `DISABLE_RATE_LIMIT=1` | отключить rate limit (разработка) |
| `LOG_LEVEL=DEBUG` | уровень логов API |

## Типичные проблемы

1. **`API не ответил за 30 с`** — занят порт 5000 (Mac) или не запущен PostgreSQL / нет Tailscale.
2. **Ошибки входа / регистрации** — проверьте `.env`, доступность БД и `curl .../api/v1/health`.
3. **PyQt5 не установился** — убедитесь, что активировано venv и выполнен `pip install -r requirements.txt`.
4. **`collected 0 items`, coverage 0%** — вы не в корне репозитория; выполните `cd` туда, где есть `tests/`, или `python run_tests.py`.
5. **`ModuleNotFoundError: sportorg`** — то же: корень проекта не в `PYTHONPATH`; запускайте `python -m pytest` из корня.
