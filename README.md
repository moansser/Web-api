# FastAPI Prices Demo

Итоговое задание: сервис котировок золота (XAU), серебра (XAG) и нефти (BRENT) с REST API, WebSocket-уведомлениями, фоновой загрузкой данных и публикацией событий в NATS.

## Запуск

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## WebSocket

Подключение к `ws://localhost:8000/ws/items`.

## Структура

- `app/api` — REST эндпоинты
- `app/ws` — менеджер WebSocket-подключений
- `app/services` — бизнес-логика и работа с БД
- `app/tasks` — фоновые задачи парсинга
- `app/db` — настройки БД
- `app/models` — SQLAlchemy модели
- `app/nats` — клиент NATS
- `app/schemas` — Pydantic-схемы
- `app/config.py` — настройки приложения

