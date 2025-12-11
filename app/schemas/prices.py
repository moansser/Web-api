from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PriceBase(BaseModel):
    symbol: str = Field(..., description="Instrument symbol, e.g. XAU, XAG, BRENT")
    price: float
    currency: str = "USD"
    source: str
    fetched_at: Optional[datetime] = None


class PriceCreate(PriceBase):
    created_at: Optional[datetime] = None


class PriceUpdate(BaseModel):
    price: Optional[float] = None
    currency: Optional[str] = None
    source: Optional[str] = None
    fetched_at: Optional[datetime] = None


class PriceRead(PriceBase):
    id: int
    created_at: datetime
    fetched_at: datetime

    class Config:
        from_attributes = True

