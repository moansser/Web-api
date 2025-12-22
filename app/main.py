import asyncio
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse, HTMLResponse
from starlette.websockets import WebSocketDisconnect

from app.api import items as items_router
from app.api import tasks as tasks_router
from app.db.session import Base, engine
from app.nats.client import connect_nats, disconnect_nats
from app.tasks.fetch_prices import fetch_prices_loop
from app.ws.connections import manager

logger = logging.getLogger("app")

app = FastAPI(title="Prices Parser Demo")

app.include_router(items_router.router, prefix="/items", tags=["items"])
app.include_router(tasks_router.router, prefix="/tasks", tags=["tasks"])

background_task: Optional[asyncio.Task] = None
BASE_DIR = Path(__file__).resolve().parent


@app.on_event("startup")
async def startup_event() -> None:
    global background_task

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    nats = await connect_nats()
    if nats is None:
        logger.warning("NATS is NOT connected (check nats-server and NATS_URL).")
    else:
        logger.info("NATS connected successfully.")

    background_task = asyncio.create_task(fetch_prices_loop())
    logger.info("Background task started: fetch_prices_loop")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global background_task

    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
        logger.info("Background task stopped")

    await disconnect_nats()


@app.get("/demo", response_class=HTMLResponse, include_in_schema=False)
async def demo_page():
    return FileResponse(BASE_DIR / "static" / "demo.html")


@app.websocket("/ws/items")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)