from pydantic import BaseModel
from datetime import datetime
from src.models.base import PositionDirection

class PositionResponse(BaseModel):
    id: str
    account_id: str
    strategy_id: str
    symbol: str
    direction: PositionDirection
    volume: float
    available_volume: float
    avg_price: float
    unrealized_pnl: float
    realized_pnl: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True