from __future__ import annotations

import asyncio
import logging
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


async def _fetch_external_prices() -> Dict[str, float]:
    prices = {}

    symbols = {
        "XAU": "GC=F", 
        "XAG": "SI=F",
        "BRENT": "BZ=F"
    }
    
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for symbol_key, yahoo_symbol in symbols.items():
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
                response = await client.get(
                    url,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "Mozilla/5.0"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("chart", {}).get("result", [])
                    if result:
                        meta = result[0].get("meta", {})
                        regular_market_price = meta.get("regularMarketPrice")
                        previous_close = meta.get("previousClose")
                        
                        price = regular_market_price or previous_close
                        prices[symbol_key] = round(float(price), 2)
                
                if symbol_key not in prices:
                    raise ValueError(f"Не удалось получить цену для {symbol_key}")
                    
            except Exception as e:
                logger = logging.getLogger("app")
                logger.error(f"Ошибка при получении цены для {symbol_key} ({yahoo_symbol}): {e}")
    
    return prices


async def fetch_prices_once() -> List[dict[str, Any]]:
    raw_prices = await _fetch_external_prices()
    now = datetime.utcnow()
    payloads = [
        PriceCreate(
            symbol=symbol, 
            price=price, 
            currency="USD", 
            source="Yahoo Finance API (real-time market data)", 
            fetched_at=now
        )
        for symbol, price in raw_prices.items()
    ]

    async with AsyncSessionLocal() as session:
        service = PricesService(session)
        stored = await service.upsert_prices(payloads)

    items = [PriceRead.from_orm(p).dict() for p in stored]
    message = jsonable_encoder({"event": "fetched", "items": items})
    #await manager.broadcast(message)
    await publish("prices.updates", message)
    return items


async def fetch_prices_loop() -> None:
    logger = logging.getLogger("app")
    
    settings = get_settings()
    interval = settings.FETCH_INTERVAL_SECONDS
    while True:
        try:
            await fetch_prices_once()
        except Exception as e:
            logger.error(f"Error in fetch_prices_loop: {e}", exc_info=True)
        await asyncio.sleep(interval)