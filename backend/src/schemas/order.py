from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.models.base import OrderStatus, OrderSide, OrderType

class OrderBase(BaseModel):
    strategy_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[float] = 0  # 0 for market orders

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    quantity: Optional[float] = None
    price: Optional[float] = None

class OrderResponse(OrderBase):
    id: str
    status: OrderStatus
    exchange_order_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    executed_at: Optional[datetime]

    class Config:
        from_attributes = True