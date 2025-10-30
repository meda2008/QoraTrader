from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Backtest Schemas
class BacktestTaskBase(BaseModel):
    strategy_id: uuid.UUID
    task_name: str
    status: Optional[str] = "排队中"  # 排队中|运行中|已完成|已失败
    start_time: str
    end_time: str
    initial_funds: float
    parameters: Optional[Dict[str, Any]] = None

class BacktestTaskCreate(BacktestTaskBase):
    pass

class BacktestTask(BacktestTaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BacktestReportBase(BaseModel):
    strategy_id: uuid.UUID
    backtest_name: str
    start_time: str
    end_time: str
    initial_funds: float
    final_funds: Optional[float] = None
    total_return: Optional[float] = None
    annualized_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    profit_loss_ratio: Optional[float] = None
    trade_count: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    detailed_trades: Optional[List[Dict[str, Any]]] = None

class BacktestReportCreate(BacktestReportBase):
    pass

class BacktestReport(BacktestReportBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True