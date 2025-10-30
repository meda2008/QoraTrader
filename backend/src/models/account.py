from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UUID, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class Account(Base):
    __tablename__ = "accounts"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    account_number = Column(String, nullable=False, unique=True)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String, nullable=False, default="正常")  # 正常|限制|风控|冻结
    total_funds = Column(Float, default=0.0)
    available_funds = Column(Float, default=0.0)
    frozen_funds = Column(Float, default=0.0)
    cumulative_profit = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="accounts")
    orders = relationship("Order", back_populates="account")
    positions = relationship("Position", back_populates="account")
    trades = relationship("Trade", back_populates="account")