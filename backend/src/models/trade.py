from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class Trade(Base):
    __tablename__ = "trades"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(PostgresUUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    strategy_id = Column(PostgresUUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    account_id = Column(PostgresUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    symbol = Column(String, nullable=False)  # Trading symbol (e.g. stock code)
    direction = Column(String, nullable=False)  # 买入|卖出
    trade_price = Column(Float, nullable=False)
    trade_quantity = Column(Integer, nullable=False)
    trade_time = Column(DateTime(timezone=True), server_default=func.now())
    fee = Column(Float, default=0.0)

    # Relationships
    order = relationship("Order", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")
    account = relationship("Account", back_populates="trades")