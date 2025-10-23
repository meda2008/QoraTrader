from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.models.base import AccountStatus, RiskLevel, AccountType

class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_type: AccountType
    status: AccountStatus
    balance: float
    available_balance: float
    market_value: float
    total_pnl: float
    daily_pnl: float
    risk_level: RiskLevel
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True