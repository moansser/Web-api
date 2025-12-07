# TODO API - FastAPI Backend

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

Или через Python:

```bash
python main.py
```

Приложение будет доступно по адресу: `http://localhost:8000`

### 3. Документация API

После запуска приложения доступна интерактивная документация:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Использование

### REST API примеры

#### Создать задачу

```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новая задача",
    "description": "Описание задачи",
    "completed": false
  }'
```

#### Получить все задачи

```bash
curl "http://localhost:8000/tasks"
```

#### Обновить задачу

```bash
curl -X PATCH "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

#### Удалить задачу

```bash
curl -X DELETE "http://localhost:8000/tasks/1"
```

### WebSocket пример

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tasks');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onopen = () => {
  console.log('Connected to WebSocket');
  ws.send(JSON.stringify({ type: 'ping' }));
};
```

### Принудительный запуск фоновой задачи

```bash
curl -X POST "http://localhost:8000/task-generator/run"
```

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

## Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **aiosqlite** - асинхронный драйвер для SQLite
- **httpx** - асинхронный HTTP клиент
- **Pydantic** - валидация данных
- **WebSocket** - двусторонняя связь в реальном времени

## База данных

Используется SQLite с асинхронным драйвером `aiosqlite`. База данных создается автоматически при первом запуске в файле `tasks.db`.