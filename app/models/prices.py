from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.db.session import Base


class MetalPrice(Base):
    __tablename__ = "metal_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(16), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    source = Column(String(128), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)

