from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.nats.client import publish
from app.schemas.prices import PriceCreate, PriceRead, PriceUpdate
from app.services.prices_service import PricesService
from app.ws.connections import manager

router = APIRouter()


@router.get("/", response_model=List[PriceRead])
async def list_items(
    symbol: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    service = PricesService(session)
    items = await service.list_latest_by_symbol(symbol=symbol)
    return [PriceRead.from_orm(item) for item in items]


@router.get("/{item_id}", response_model=PriceRead)
async def get_item(item_id: int, session: AsyncSession = Depends(get_session)):
    service = PricesService(session)
    item = await service.get_price(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return PriceRead.from_orm(item)


@router.post("/", response_model=PriceRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: PriceCreate, session: AsyncSession = Depends(get_session)
):
    service = PricesService(session)
    item = await service.create_price(payload)
    data = PriceRead.from_orm(item).dict()
    message = jsonable_encoder({"event": "created", "item": data})
    await manager.broadcast(message)
    await publish("prices.updates", message)
    return data


@router.patch("/{item_id}", response_model=PriceRead)
async def update_item(
    item_id: int, payload: PriceUpdate, session: AsyncSession = Depends(get_session)
):
    service = PricesService(session)
    item = await service.update_price(item_id, payload)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    data = PriceRead.from_orm(item).dict()
    message = jsonable_encoder({"event": "updated", "item": data})
    await manager.broadcast(message)
    await publish("prices.updates", message)
    return data


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, session: AsyncSession = Depends(get_session)):
    service = PricesService(session)
    deleted = await service.delete_price(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    message = jsonable_encoder({"event": "deleted", "id": item_id})
    await manager.broadcast(message)
    await publish("prices.updates", message)
    return None

