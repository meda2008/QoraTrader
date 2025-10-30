from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UUID, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class Order(Base):
    __tablename__ = "orders"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(PostgresUUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    exchange_order_id = Column(String)  # Order ID from exchange
    account_id = Column(PostgresUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    symbol = Column(String, nullable=False)  # Trading symbol (e.g. stock code)
    direction = Column(String, nullable=False)  # 买入|卖出
    order_type = Column(String, nullable=False)  # 市价单|限价单|止损单等
    status = Column(String, nullable=False)  # 未提交|已提交|部分成交|完全成交|已取消|已拒绝
    price = Column(Float)  # Price for limit orders
    quantity = Column(Integer, nullable=False)
    filled_quantity = Column(Integer, default=0)
    average_fill_price = Column(Float)
    submit_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), onupdate=func.now())
    cancel_time = Column(DateTime(timezone=True))

    # Relationships
    strategy = relationship("Strategy", back_populates="orders")
    account = relationship("Account", back_populates="orders")
    trades = relationship("Trade", back_populates="order")