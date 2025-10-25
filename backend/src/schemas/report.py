from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ReportTypeEnum(str, Enum):
    BACKTEST = "backtest"
    LIVE_TRADING = "live_trading"
    RISK_ANALYSIS = "risk_analysis"
    PERFORMANCE_ATTRIBUTION = "performance_attribution"

class ReportBase(BaseModel):
    strategy_id: str
    report_type: ReportTypeEnum
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    alpha: float
    beta: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    data: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None

class ReportInDBBase(ReportBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Report(ReportInDBBase):
    pass

class ReportResponse(ReportInDBBase):
    pass