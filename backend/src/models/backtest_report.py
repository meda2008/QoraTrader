from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class BacktestReport(Base):
    __tablename__ = "backtest_reports"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(PostgresUUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    backtest_name = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    initial_funds = Column(Float, nullable=False)
    final_funds = Column(Float)
    total_return = Column(Float)  # Total return percentage
    annualized_return = Column(Float)  # Annualized return percentage
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)  # Win rate percentage
    profit_loss_ratio = Column(Float)  # Average profit/loss ratio
    max_consecutive_wins = Column(Integer)
    max_consecutive_losses = Column(Integer)
    trade_count = Column(Integer)
    parameters = Column(String)  # JSON parameters as string
    detailed_trades = Column(String)  # JSON detailed trades as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    strategy = relationship("Strategy", back_populates="backtest_report")