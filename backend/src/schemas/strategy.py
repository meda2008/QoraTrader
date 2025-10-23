from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from src.models.base import StrategyStatus

class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    config: Optional[str] = None  # JSON configuration
    code: Optional[str] = None

class StrategyCreate(StrategyBase):
    name: str  # Name is required for creation

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[str] = None
    code: Optional[str] = None
    status: Optional[StrategyStatus] = None

class StrategyResponse(StrategyBase):
    id: str
    user_id: str
    status: StrategyStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True