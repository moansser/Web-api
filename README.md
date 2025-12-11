# TODO API - FastAPI

Полноценный серверный backend на FastAPI с REST API, WebSocket и фоновыми задачами.

## Функциональность

### REST API для управления задачами

- `GET /tasks` - получить список всех задач
- `GET /tasks/{id}` - получить задачу по ID
- `POST /tasks` - создать новую задачу
- `PATCH /tasks/{id}` - частично обновить задачу
- `DELETE /tasks/{id}` - удалить задачу

### WebSocket

- `WS /ws/tasks` - WebSocket канал для уведомлений в реальном времени

### Фоновая задача

- Автоматически выполняется каждые 5 минут
- Получает данные с внешнего API (JSONPlaceholder)
- Наполняет базу данных новыми задачами
- `POST /task-generator/run` - принудительный запуск фоновой задачи

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск приложения

```bash
uvicorn main:app --reload
```

Приложение будет доступно по адресу: `http://localhost:8000`

### 3. Документация API

После запуска приложения доступна интерактивная документация:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Структура проекта

```
Web-api/
├── main.py                 # Главный файл приложения
├── database.py             # Настройка базы данных
├── models.py               # SQLAlchemy модели
├── schemas.py              # Pydantic схемы
├── background_tasks.py     # Фоновые задачи
├── routers/
│   ├── tasks.py           # REST API для задач
│   ├── websocket.py       # WebSocket endpoint
│   └── task_generator.py  # Endpoint для фоновой задачи
├── requirements.txt        # Зависимости
└── README.md              # Документация
```

## База данных

Используется SQLite с асинхронным драйвером `aiosqlite`. База данных создается автоматически при первом запуске в файле `tasks.db`.
