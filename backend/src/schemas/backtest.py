from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BacktestBase(BaseModel):
    strategy_id: str
    start_date: datetime
    end_date: datetime
    initial_capital: float

class BacktestCreate(BacktestBase):
    pass

class BacktestResponse(BacktestBase):
    id: str
    final_capital: float
    total_return: Optional[float] = None
    annual_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    total_trades: Optional[int] = None
    winning_trades: Optional[int] = None
    losing_trades: Optional[int] = None
    data: Optional[str] = None  # JSON string for detailed results
    created_at: datetime

    class Config:
        from_attributes = True