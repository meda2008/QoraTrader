from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(String, nullable=False)  # semantic version
    status = Column(String, nullable=False, default="未激活")  # 未激活|已激活|暂停|已停止|异常
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    config = Column(String)  # JSON config as string
    code_path = Column(String)  # Path to strategy code file
    performance_metrics = Column(String)  # JSON metrics as string
    backtest_result_id = Column(PostgresUUID(as_uuid=True), ForeignKey("backtest_reports.id"))

    # Relationship
    backtest_report = relationship("BacktestReport", back_populates="strategy")
    orders = relationship("Order", back_populates="strategy")
    positions = relationship("Position", back_populates="strategy")
    trades = relationship("Trade", back_populates="strategy")
    risk_params = relationship("RiskParams", back_populates="strategy", uselist=False, cascade="all, delete-orphan")