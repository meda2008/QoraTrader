from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UUID, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..models.base import Base
import uuid

class BacktestTask(Base):
    __tablename__ = "backtest_tasks"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(PostgresUUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    task_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="排队中")  # 排队中|运行中|已完成|已失败
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    initial_funds = Column(Float, nullable=False)
    parameters = Column(JSON)  # JSON parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    strategy = relationship("Strategy")