from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

# Strategy Schemas
class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: str
    status: Optional[str] = "未激活"  # 未激活|已激活|暂停|已停止|异常
    config: Optional[Dict[str, Any]] = None
    code_path: Optional[str] = None

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    code_path: Optional[str] = None

class Strategy(StrategyBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    backtest_result_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True