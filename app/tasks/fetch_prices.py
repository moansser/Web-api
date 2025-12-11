from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List

import httpx
from fastapi.encoders import jsonable_encoder

from app.config import get_settings
from app.db.session import AsyncSessionLocal
from app.nats.client import publish
from app.schemas.prices import PriceCreate, PriceRead
from app.services.prices_service import PricesService
from app.ws.connections import manager


async def _fetch_external_prices(api_url: str) -> Dict[str, float]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(api_url)
            response.raise_for_status()
            data = response.json()
            return {
                "XAU": float(data.get("XAU", data.get("xau", 1900.0))),
                "XAG": float(data.get("XAG", data.get("xag", 22.0))),
                "BRENT": float(data.get("BRENT", data.get("brent", 80.0))),
            }
    except Exception:
        return {"XAU": 1900.0, "XAG": 22.0, "BRENT": 80.0}


async def fetch_prices_once() -> List[dict[str, Any]]:
    """Single run: fetch, store, publish, and broadcast prices."""
    settings = get_settings()
    raw_prices = await _fetch_external_prices(settings.EXTERNAL_API_URL)
    now = datetime.utcnow()
    payloads = [
        PriceCreate(symbol=symbol, price=price, currency="USD", source=settings.EXTERNAL_API_URL, fetched_at=now)
        for symbol, price in raw_prices.items()
    ]

    async with AsyncSessionLocal() as session:
        service = PricesService(session)
        stored = await service.upsert_prices(payloads)

    items = [PriceRead.from_orm(p).dict() for p in stored]
    message = jsonable_encoder({"event": "fetched", "items": items})
    await manager.broadcast(message)
    await publish("prices.updates", message)
    return items


async def fetch_prices_loop() -> None:
    settings = get_settings()
    interval = settings.FETCH_INTERVAL_SECONDS
    while True:
        await fetch_prices_once()
        await asyncio.sleep(interval)

