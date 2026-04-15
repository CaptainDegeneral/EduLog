# EduLog

EduLog — это полнофункциональное веб-приложение для учёта занятий репетитора, построенное с использованием:

- **Backend**: FastAPI, SQLAlchemy 2.0 (async), SQLite, Pydantic v2, Alembic
- **Frontend**: Vue 3 Composition API, Vite, Tailwind CSS, Axios

## Архитектура

Backend реализует запрошенную многоуровневую структуру:

- `API` — транспортный уровень и маршрутизация
- `Services` — бизнес-логика и расчёты
- `Repositories` — доступ к данным без бизнес-логики
- `Models` — SQLAlchemy-сущности

Вычисляемые поля занятий не хранятся в базе данных:

- `duration_hours` — продолжительность в часах
- `total` — итоговая стоимость
- `debt` — задолженность

Точки расширения для масштабирования:

- `DATABASE_URL` уже поддерживает переключение с SQLite на PostgreSQL путём изменения строки подключения и асинхронного драйвера.
- Предусмотрен заглушка-эндпоинт авторизации `GET /api/auth/me`.
- Роутеры и сервисы легко масштабируются по `user_id` в будущем.
- Границы моделей `Subject` и `Lesson` позволяют расширять функционал для групповых занятий.

## Структура проекта

```text
backend/
  app/
    main.py
    core/
    models/
    schemas/
    repositories/
    services/
    api/
      routes/
    utils/
  alembic/
frontend/
  src/
    api/
    components/
    views/
    store/
    types/
```

## Настройка Backend

Требования:

- Python 3.11+

Шаги установки:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.sample .env
alembic upgrade head
python seed.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Документация и проверка работоспособности backend:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Healthcheck: `http://127.0.0.1:8000/health`

## Настройка Frontend

Требования:

- Node.js 20+

Шаги установки:

```bash
cd frontend
npm install
Copy-Item .env.sample .env
npm run dev
```

Запуск frontend-приложения:

- `http://127.0.0.1:5173`

## Переменные окружения

Можно использовать корневой файл `.env.sample` как справочный или сервис-специфичные файлы:

- `backend/.env.sample`
- `frontend/.env.sample`

Рекомендуемые значения для локальной разработки:

```env
APP_NAME=EduLog API
DEBUG=true
API_V1_PREFIX=/api
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite+aiosqlite:///./edulog.db
SQL_ECHO=false
AUTO_CREATE_TABLES=false
LOG_LEVEL=INFO
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Миграции

Alembic настроен в файле `backend/alembic.ini`.

Создание новой миграции:

```bash
cd backend
alembic revision -m "описание изменений"
```

Применение миграций:

```bash
cd backend
alembic upgrade head
```

Команды миграций для SQLite через Docker Compose:

```bash
# применить все миграции
docker compose run --rm backend alembic upgrade head

# создать новую миграцию
docker compose run --rm backend alembic revision -m "описание изменений"

# откатить миграцию на один шаг
docker compose run --rm backend alembic downgrade -1
```

## Начальные данные (Seed)

Скрипт заполнения базы данных:

```bash
cd backend
python seed.py
```

Скрипт создаёт начальные записи студентов, предметов и занятий, если база данных пуста.

## Эндпоинты API

### Студенты

- `GET /api/students` — получение списка студентов
- `POST /api/students` — создание нового студента
- `PUT /api/students/{id}` — обновление данных студента
- `DELETE /api/students/{id}` — удаление студента

### Предметы

- `GET /api/subjects` — получение списка предметов
- `POST /api/subjects` — создание нового предмета
- `PUT /api/subjects/{id}` — обновление данных предмета
- `DELETE /api/subjects/{id}` — удаление предмета

### Занятия

- `GET /api/lessons?date=YYYY-MM-DD&student_id=1&status=planned` — получение списка занятий с фильтрацией
- `POST /api/lessons` — создание нового занятия
- `PUT /api/lessons/{id}` — обновление данных занятия
- `DELETE /api/lessons/{id}` — удаление занятия

Валидации в сервисе занятий:

- `end_time > start_time` — время окончания должно быть позже времени начала
- `rate >= 0` — ставка не может быть отрицательной
- `prepayment_amount >= 0` — сумма предоплаты не может быть отрицательной
- Отсутствие пересекающихся не отменённых занятий для одного студента в одну дату

### Аналитика

- `GET /api/analytics/summary` — сводная аналитика
- `GET /api/analytics/by-student` — аналитика в разрезе студентов

## Примечания

- Поля `total_income`, `total_hours` и `total_debt` рассчитываются на основе не отменённых занятий.
- Поле `cancelled_count` учитывает отменённые занятия отдельно.
- Таблица занятий во frontend поддерживает фильтрацию, модальное окно создания и редактирование строк inline.