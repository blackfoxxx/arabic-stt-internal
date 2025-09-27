"""
Project model
"""

from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import SoftDeleteModel, AuditableModel


class Project(SoftDeleteModel, AuditableModel):
    """Project model for organizing media files and transcripts"""
    
    __tablename__ = "projects"
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Project details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Project settings
    settings = Column(JSON, default=dict)
    
    # Relationships
    organization = relationship("Organization", back_populates="projects")
    media_files = relationship("MediaFile", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"
    
    @property
    def media_count(self) -> int:
        """Get count of media files in project"""
        return len([mf for mf in self.media_files if not mf.is_deleted])
    
    @property
    def total_duration(self) -> float:
        """Get total duration of all media files"""
        return sum([
            mf.duration_seconds or 0 
            for mf in self.media_files 
            if not mf.is_deleted and mf.duration_seconds
        ])
    
    def get_setting(self, key: str, default=None):
        """Get project setting"""
        if not self.settings:
            return default
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value):
        """Set project setting"""
        if not self.settings:
            self.settings = {}
        self.settings[key] = value
    
    @classmethod
    def get_by_organization(cls, db, organization_id: str):
        """Get projects by organization"""
        return db.query(cls).filter(
            cls.organization_id == organization_id,
            ~cls.is_deleted
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_name(cls, db, organization_id: str, name: str):
        """Get project by name within organization"""
        return db.query(cls).filter(
            cls.organization_id == organization_id,
            cls.name == name,
            ~cls.is_deleted
        ).first()