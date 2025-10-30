from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# Order Schemas
class OrderBase(BaseModel):
    strategy_id: uuid.UUID
    account_id: uuid.UUID
    symbol: str
    direction: str  # 买入|卖出
    order_type: str  # 市价单|限价单|止损单等
    price: Optional[float] = None  # Price for limit orders
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    price: Optional[float] = None
    quantity: Optional[int] = None

class Order(OrderBase):
    id: uuid.UUID
    exchange_order_id: Optional[str]
    status: str  # 未提交|已提交|部分成交|完全成交|已取消|已拒绝
    filled_quantity: int
    average_fill_price: Optional[float]
    submit_time: datetime
    update_time: Optional[datetime] = None
    cancel_time: Optional[datetime] = None

    class Config:
        from_attributes = True