import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Task
from datetime import datetime
import logging
from database import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def fetch_external_tasks() -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://jsonplaceholder.typicode.com/todos")
            response.raise_for_status()
            data = response.json()
            
            tasks = []
            for item in data[:5]:
                tasks.append({
                    "title": item.get("title", "Untitled Task"),
                    "description": f"Task from external API (User ID: {item.get('userId', 'N/A')})",
                    "completed": item.get("completed", False)
                })
            
            logger.info(f"Fetched {len(tasks)} tasks from external API")
            return tasks
    except Exception as e:
        logger.error(f"Error fetching external tasks: {e}")
        return []


async def populate_database_from_external(db: AsyncSession, notify_callback=None):
    try:
        external_tasks = await fetch_external_tasks()
        
        if not external_tasks:
            logger.warning("No tasks fetched from external API")
            if notify_callback:
                await notify_callback(
                    message_type="background_task",
                    message="No tasks fetched from external API",
                    data={"status": "warning", "created_count": 0}
                )
            return 0
        
        created_count = 0
        for task_data in external_tasks:
            result = await db.execute(
                select(Task).where(Task.title == task_data["title"])
            )
            existing_task = result.scalar_one_or_none()
            
            if not existing_task:
                new_task = Task(
                    title=task_data["title"],
                    description=task_data.get("description"),
                    completed=task_data.get("completed", False)
                )
                db.add(new_task)
                created_count += 1
        
        await db.commit()
        logger.info(f"Created {created_count} new tasks from external API")
        
        if notify_callback and created_count > 0:
            await notify_callback(
                message_type="background_task",
                message=f"Created {created_count} new tasks from external API",
                data={"status": "success", "created_count": created_count}
            )
        
        return created_count
    except Exception as e:
        await db.rollback()
        logger.error(f"Error populating database: {e}")
        if notify_callback:
            await notify_callback(
                message_type="background_task",
                message="Background task failed",
                data={"status": "error", "error": str(e)}
            )
        raise


class BackgroundTaskManager:
    def __init__(self):
        self.is_running = False
        self.task = None
        self.interval = 300
    
    async def start(self, notify_callback=None):
        if self.is_running:
            logger.warning("Background task is already running")
            return
        
        self.is_running = True
        logger.info("Starting background task")
        
        async def periodic_task():
            while self.is_running:
                try:
                    async with AsyncSessionLocal() as db:
                        await populate_database_from_external(db, notify_callback)
                except Exception as e:
                    logger.error(f"Error in periodic task: {e}")
                
                await asyncio.sleep(self.interval)
        
        self.task = asyncio.create_task(periodic_task())
    
    async def stop(self):
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Background task stopped")
    
    async def run_once(self, db: AsyncSession = None, notify_callback=None):
        logger.info("Running background task manually")
        if db is None:
            async with AsyncSessionLocal() as session:
                await populate_database_from_external(session, notify_callback)
        else:
            await populate_database_from_external(db, notify_callback)


background_task_manager = BackgroundTaskManager()

