from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi.encoders import jsonable_encoder
from nats.aio.client import Client as NATS

from app.config import get_settings
from app.ws.connections import manager

nats_client: Optional[NATS] = None
logger = logging.getLogger("app.nats")


async def connect_nats() -> Optional[NATS]:
    global nats_client
    settings = get_settings()
    client = NATS()
    try:
        logger.info("Connecting to NATS: %s", settings.NATS_URL)
        await client.connect(servers=[settings.NATS_URL])
        logger.info("NATS connected")
    except Exception as e:
        logger.exception("NATS connection failed: %s", e)
        return None

    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
        except Exception:
            data = {"raw": msg.data.decode(errors="ignore")}
        logger.info("NATS message received on %s", msg.subject)
        await manager.broadcast({"event": "nats_message", "data": data})

    await client.subscribe("prices.updates", cb=message_handler)
    logger.info("Subscribed to NATS subject: prices.updates")

    nats_client = client
    return nats_client


async def disconnect_nats() -> None:
    global nats_client
    if nats_client:
        logger.info("Disconnecting NATS (drain)")
        await nats_client.drain()
        nats_client = None
        logger.info("NATS disconnected")


async def publish(subject: str, data: dict) -> None:
    if not nats_client or not nats_client.is_connected:
        logger.warning("Publish skipped (NATS not connected). Subject=%s", subject)
        return
    payload = json.dumps(jsonable_encoder(data)).encode()
    await nats_client.publish(subject, payload)
    logger.info("Published to NATS. Subject=%s", subject)
