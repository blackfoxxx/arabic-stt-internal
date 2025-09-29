"""
API Key model
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel


class ApiKey(BaseModel):
    """API Key model for authentication"""
    
    __tablename__ = "api_keys"
    
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Key details
    name = Column(String(255), nullable=False)
    key_prefix = Column(String(16), nullable=False, unique=True, index=True)
    key_hash = Column(String(64), nullable=False)
    
    # Status and expiration
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")