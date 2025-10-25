from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.models.base import Base
from datetime import datetime
import uuid

class ReportType(Base):
    __tablename__ = "report_types"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String, ForeignKey("strategies.id"))
    report_type_id = Column(String, ForeignKey("report_types.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    initial_capital = Column(Numeric)
    final_capital = Column(Numeric)
    total_return = Column(Numeric)
    annual_return = Column(Numeric)
    sharpe_ratio = Column(Numeric)
    sortino_ratio = Column(Numeric)
    calmar_ratio = Column(Numeric)
    max_drawdown = Column(Numeric)
    win_rate = Column(Numeric)
    profit_factor = Column(Numeric)
    alpha = Column(Numeric)
    beta = Column(Numeric)
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    strategy = relationship("Strategy", back_populates="reports")
    report_type = relationship("ReportType")