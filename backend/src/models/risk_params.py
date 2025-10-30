from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class RiskParams(Base):
    __tablename__ = "risk_params"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(PostgresUUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False, unique=True)
    account_risk = Column(String)  # JSON account risk params as string
    stock_risk = Column(String)  # JSON stock risk params as string
    global_risk = Column(String)  # JSON global risk params as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    strategy = relationship("Strategy", back_populates="risk_params")