from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UUID, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class IndicatorLibrary(Base):
    __tablename__ = "indicator_libraries"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    type = Column(String, nullable=False, default="外部")  # 内置|外部
    status = Column(String, nullable=False, default="激活")  # 激活|停用
    description = Column(Text)
    path = Column(String)  # Path to library file
    supported_indicators = Column(String)  # JSON supported indicators as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())