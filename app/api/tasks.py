from fastapi import APIRouter, status

from app.tasks.fetch_prices import fetch_prices_once

router = APIRouter()


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def run_task_once():
    items = await fetch_prices_once()
    return {"status": "ok", "items": items}

