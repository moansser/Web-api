# FastAPI Prices Service

Сервис для получения и отслеживания реальных цен на золото (XAU), серебро (XAG) и нефть Brent (BRENT) с использованием REST API, WebSocket-уведомлений, фоновой загрузки данных и публикацией событий в NATS.

## Возможности

- Получение реальных цен из Yahoo Finance API
- REST API для доступа к данным
- WebSocket для real-time уведомлений
- Фоновая задача автоматического обновления цен
- Публикация событий в NATS
- SQLite база данных для хранения истории цен


## Инструкция по запуску

### 1. Создание виртуального окружения
```bash
python -m venv venv
```
### 2. Активация виртуального окружения
**macOS/Linux:**
```bash
source venv/bin/activate
```
**Windows:**
```bash
venv\Scripts\activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Запуск NATS сервера
Откройте новый терминал и запустите NATS сервер:
```bash
nats-server
```
NATS сервер будет доступен по адресу `nats://localhost:4222` (по умолчанию).
**Примечание:** Если порт 4222 занят, можно найти и остановить процесс:
```bash
lsof -i :4222
kill <PID>
```

### 5. Запуск приложения
В терминале с активированным виртуальным окружением:
```bash
uvicorn app.main:app --reload
```
Приложение будет доступно по адресу `http://localhost:8000`

### 6. Проверка работы
- Откройте браузер и перейдите на `http://localhost:8000/docs` для просмотра Swagger UI
- Или откройте `http://localhost:8000/demo` для демонстрации WebSocket и NATS

## API Документация

После запуска приложения доступны следующие эндпоинты:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **WebSocket:** ws://localhost:8000/ws/items
- **Демо страница:** http://localhost:8000/demo

### Основные эндпоинты
- `GET /items/` - Получить список всех цен
- `GET /items/?symbol=XAU` - Получить цены по символу
- `GET /items/{item_id}` - Получить цену по ID
- `POST /tasks/run` - Запустить задачу получения цен вручную

## Использование NATS

### Подписка на события
Пример подписчика на события цен:
```python
import asyncio
import json
from nats.aio.client import Client as NATS

async def main():
    nc = NATS()
    await nc.connect("nats://localhost:4222")

    async def handler(msg):
        data = json.loads(msg.data.decode())
        print(f"Received: {msg.subject}")
        print(f"Data: {data}")

    await nc.subscribe("prices.updates", cb=handler)
    print("Listening on prices.updates...")
    await asyncio.Future()

asyncio.run(main())
```

### Публикация событий
Приложение автоматически публикует события при обновлении цен. Также можно публиковать вручную:
```python
import asyncio
import json
from nats.aio.client import Client as NATS

async def main():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    await nc.publish(
        "prices.updates",
        json.dumps({"event": "test", "items": []}).encode()
    )
    await nc.flush()
    await nc.close()

asyncio.run(main())
```

## WebSocket

Для подключения к WebSocket используйте:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/items');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## Структура проекта

```
Web-api-proj/
├── app/
│   ├── api/           # REST API эндпоинты
│   ├── config.py      # Настройки приложения
│   ├── db/            # Настройки базы данных
│   ├── main.py        # Точка входа приложения
│   ├── models/        # SQLAlchemy модели
│   ├── nats/          # NATS клиент
│   ├── schemas/       # Pydantic схемы
│   ├── services/      # Бизнес-логика
│   ├── static/        # Статические файлы
│   ├── tasks/         # Фоновые задачи
│   └── ws/            # WebSocket менеджер
├── app.db             # SQLite база данных (создается автоматически)
├── requirements.txt   # Зависимости Python
└── README.md          # Документация
```