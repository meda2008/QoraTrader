from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.models.base import AccountType

class UserBase(BaseModel):
    username: str
    email: str
    role: str  # 'admin', 'strategist', 'trader'


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True