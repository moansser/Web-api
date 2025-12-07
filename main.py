from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from database import init_db, get_db
from routers import tasks, websocket, task_generator
from background_tasks import background_task_manager
from routers.websocket import notify_clients

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    
    await init_db()
    logger.info("Database initialized")
    
    await background_task_manager.start(notify_callback=notify_clients)
    logger.info("Background task started")
    
    yield
    
    logger.info("Shutting down application...")
    await background_task_manager.stop()
    logger.info("Application stopped")


app = FastAPI(
    title="TODO API",
    description="REST API для управления задачами с WebSocket уведомлениями и фоновыми задачами",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(tasks.router)
app.include_router(websocket.router)
app.include_router(task_generator.router)


@app.get("/")
async def root():
    return {
        "message": "TODO API",
        "version": "1.0.0",
        "endpoints": {
            "tasks": "/tasks",
            "websocket": "/ws/tasks",
            "background_task": "/task-generator/run",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

