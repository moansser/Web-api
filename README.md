# FastAPI Prices Demo

Итоговое задание: сервис котировок золота (XAU), серебра (XAG) и нефти (BRENT) с REST API, WebSocket-уведомлениями, фоновой загрузкой данных и публикацией событий в NATS.

## Запуск

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Документация по API

    Swagger UI: http://localhost:8000/docs
    WebSocket: ws://localhost:8000/ws/items
    Демостраница WS/NATS: http://localhost:8000/demo

## Пример работы NATS (publisher + subscriber)

1. Поднять NATS локально (по умолчанию `nats://localhost:4222`).
2. Запустить приложение (`uvicorn app.main:app --reload`).
3. Подписчик (python пример):
   ```python
   import asyncio, json
   from nats.aio.client import Client as NATS

   async def main():
       nc = NATS()
       await nc.connect("nats://localhost:4222")

       async def handler(msg):
           print("Received:", msg.subject, msg.data.decode())

       await nc.subscribe("prices.updates", cb=handler)
       print("listening on prices.updates")
       # удерживаем соединение
       await asyncio.Future()

   asyncio.run(main())
   ```
4. Паблишер: любые события приложения (POST/PATCH/DELETE /items или фоновая задача) публикуют JSON в `prices.updates`. Можно отправить вручную:
   ```python
   import asyncio, json
   from nats.aio.client import Client as NATS

   async def main():
       nc = NATS()
       await nc.connect("nats://localhost:4222")
       await nc.publish("prices.updates", json.dumps({"event": "test", "payload": 123}).encode())
       await nc.flush()
       await nc.close()

   asyncio.run(main())
   ```
    
## WebSocket

Подключение к `ws://localhost:8000/ws/items`.

<img width="1470" height="504" alt="image" src="https://github.com/user-attachments/assets/e3e9b719-3788-4809-85d2-c882bb9bb2a3" />

## Ссылка на отчет

    https://docs.google.com/document/d/16-G4UIoExsIhV06FjdfsOCHOiPqjCqls/edit?usp=sharing&ouid=111681029320580157118&rtpof=true&sd=true

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

