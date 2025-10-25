from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.models.base import Base
from datetime import datetime
import uuid
from enum import Enum as PyEnum

class UserRole(PyEnum):
    ADMIN = "管理员"
    STRATEGIST = "策略师"
    TRADER = "交易员"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(Enum(UserRole))
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    strategies = relationship("Strategy", back_populates="user")
    accounts = relationship("Account", back_populates="user")