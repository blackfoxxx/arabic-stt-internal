"""
Base model with common fields and utilities
"""

import uuid
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session


@as_declarative()
class Base:
    """Base class for all database models"""
    
    id: Any
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


class BaseModel(Base):
    """Base model with common fields"""
    
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update(self, **kwargs):
        """Update model fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    @classmethod
    def create(cls, db: Session, **kwargs):
        """Create new instance"""
        instance = cls(**kwargs)
        db.add(instance)
        db.flush()
        return instance


class SoftDeleteModel(BaseModel):
    """Base model with soft delete functionality"""
    
    __abstract__ = True
    
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    def soft_delete(self):
        """Mark as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore from soft delete"""
        self.is_deleted = False
        self.deleted_at = None


class AuditableModel(BaseModel):
    """Base model with audit fields"""
    
    __abstract__ = True
    
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    def set_audit_fields(self, user_id: uuid.UUID):
        """Set audit fields"""
        if not self.created_by:
            self.created_by = user_id
        self.updated_by = user_id


class MetadataModel(BaseModel):
    """Base model with metadata field"""
    
    __abstract__ = True
    
    extra_metadata = Column(JSON, nullable=True, default=dict)
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata field"""
        if not self.extra_metadata:
            self.extra_metadata = {}
        self.extra_metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata field"""
        if not self.extra_metadata:
            return default
        return self.extra_metadata.get(key, default)