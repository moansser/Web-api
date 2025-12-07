# Быстрый старт

## Установка

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # На macOS/Linux
# или
venv\Scripts\activate  # На Windows

# Установите зависимости
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn main:app --reload
```

Или:

```bash
python main.py
```

## Проверка работы

1. Откройте браузер: http://localhost:8000/docs
2. Протестируйте API через Swagger UI
3. Для WebSocket используйте любой WebSocket клиент:
   - Подключитесь к: `ws://localhost:8000/ws/tasks`
   - Отправьте: `{"type": "ping"}`

## Примеры запросов

### Создать задачу
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Моя задача", "description": "Описание", "completed": false}'
```

### Получить все задачи
```bash
curl "http://localhost:8000/tasks"
```

### Запустить фоновую задачу
```bash
curl -X POST "http://localhost:8000/task-generator/run"
```

