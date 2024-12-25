from src.log_config import loggerUpdater
from src.updater.models.base import BaseModelWithORM

from sqlalchemy import Column, Float, DateTime, func
from src.updater.models.base import Base
from datetime import datetime, timezone

class EURUSD_M15(Base):
    __tablename__ = 'EURUSD_M15'  # Name of the table in the database

    # timestamp = Column(UtcDateTime(), primary_key=True, index=True, unique=True)  # Use UtcDateTime for UTC timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, primary_key=True, index=True, unique=True)  # Use UtcDateTime for UTC timestamps
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    open = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<MarketData(timestamp={self.timestamp}, high={self.high}, low={self.low}, close={self.close}, open={self.open}, volume={self.volume})>"


class EURUSD_M15_Pydantic(BaseModelWithORM):
    timestamp: datetime
    high: float | None = None
    low: float | None = None
    close: float | None = None
    open: float | None = None
    volume: float | None = None
    created_at: datetime | None = None
