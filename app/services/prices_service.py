from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prices import MetalPrice
from app.schemas.prices import PriceCreate, PriceUpdate


class PricesService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_price(self, data: PriceCreate) -> MetalPrice:
        obj = MetalPrice(
            symbol=data.symbol,
            price=data.price,
            currency=data.currency,
            source=data.source,
            created_at=data.created_at or datetime.utcnow(),
            fetched_at=data.fetched_at or datetime.utcnow(),
        )
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_price(self, item_id: int) -> Optional[MetalPrice]:
        result = await self.session.execute(
            select(MetalPrice).where(MetalPrice.id == item_id)
        )
        return result.scalar_one_or_none()

    async def list_latest_by_symbol(
        self, symbol: Optional[str] = None
    ) -> List[MetalPrice]:
        stmt = select(MetalPrice).order_by(
            MetalPrice.symbol, MetalPrice.fetched_at.desc()
        )
        if symbol:
            stmt = stmt.where(MetalPrice.symbol == symbol)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        latest: list[MetalPrice] = []
        seen: set[str] = set()
        for row in rows:
            if row.symbol not in seen:
                latest.append(row)
                seen.add(row.symbol)
        return latest

    async def update_price(
        self, item_id: int, data: PriceUpdate
    ) -> Optional[MetalPrice]:
        update_data = {
            k: v
            for k, v in data.dict(exclude_unset=True).items()
            if v is not None
        }
        if not update_data:
            return await self.get_price(item_id)
        update_data.setdefault("fetched_at", datetime.utcnow())
        await self.session.execute(
            update(MetalPrice)
            .where(MetalPrice.id == item_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_price(item_id)

    async def delete_price(self, item_id: int) -> bool:
        result = await self.session.execute(
            delete(MetalPrice).where(MetalPrice.id == item_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def upsert_prices(
        self, prices: Iterable[PriceCreate]
    ) -> List[MetalPrice]:
        stored: list[MetalPrice] = []
        for price in prices:
            stored.append(await self.create_price(price))
        return stored

