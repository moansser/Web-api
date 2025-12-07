from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database import get_db
from background_tasks import background_task_manager
from routers.websocket import notify_clients

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/task-generator", tags=["task-generator"])


@router.post("/run")
async def run_background_task(db: AsyncSession = Depends(get_db)):
    try:
        await background_task_manager.run_once(db, notify_callback=notify_clients)
        
        return {
            "status": "success",
            "message": "Background task executed successfully"
        }
    except Exception as e:
        logger.error(f"Error running background task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running background task: {str(e)}"
        )

