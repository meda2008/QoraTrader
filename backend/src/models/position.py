from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class Position(Base):
    __tablename__ = "positions"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(PostgresUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    strategy_id = Column(PostgresUUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String, nullable=False)  # Trading symbol (e.g. stock code)
    direction = Column(String, nullable=False)  # 多头|空头
    position_quantity = Column(Integer, default=0)
    available_quantity = Column(Integer, default=0)  # Available for trading
    position_cost = Column(Float)  # Cost price
    current_price = Column(Float)  # Latest price
    floating_pnl = Column(Float)  # Floating profit and loss
    pnl_ratio = Column(Float)  # PnL ratio
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    account = relationship("Account", back_populates="positions")
    strategy = relationship("Strategy", back_populates="positions")