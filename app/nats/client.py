from __future__ import annotations

import json
from typing import Optional

from fastapi.encoders import jsonable_encoder
from nats.aio.client import Client as NATS

from app.config import get_settings
from app.ws.connections import manager

nats_client: Optional[NATS] = None


async def connect_nats() -> Optional[NATS]:
    global nats_client
    settings = get_settings()
    client = NATS()
    try:
        await client.connect(servers=[settings.NATS_URL])
    except Exception:
        return None

    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
        except Exception:
            data = {"raw": msg.data.decode(errors="ignore")}
        await manager.broadcast({"event": "nats_message", "data": data})

    await client.subscribe("prices.updates", cb=message_handler)
    nats_client = client
    return nats_client


async def disconnect_nats() -> None:
    global nats_client
    if nats_client:
        await nats_client.drain()
        nats_client = None


async def publish(subject: str, data: dict) -> None:
    """Publish dictionary payload to NATS as JSON."""
    if not nats_client or not nats_client.is_connected:
        return
    payload = json.dumps(jsonable_encoder(data)).encode()
    await nats_client.publish(subject, payload)

