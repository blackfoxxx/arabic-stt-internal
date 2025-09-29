"""
Media file model
"""

import enum
from sqlalchemy import Column, String, Integer, Float, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import SoftDeleteModel, AuditableModel


class MediaStatus(str, enum.Enum):
    """Media file status enum"""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"
    DELETED = "deleted"


class MediaFile(SoftDeleteModel, AuditableModel):
    """Media file model"""
    
    __tablename__ = "media_files"
    
    # Organization and project
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    filename = Column(String(500), nullable=False)
    original_name = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Audio/Video metadata
    duration_seconds = Column(Float, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    bitrate = Column(Integer, nullable=True)
    
    # Storage paths
    file_path = Column(String(1000), nullable=False)  # Original file path in MinIO
    processed_path = Column(String(1000), nullable=True)  # Processed audio path
    thumbnail_path = Column(String(1000), nullable=True)  # Video thumbnail path
    
    # Processing status
    status = Column(SQLEnum(MediaStatus), default=MediaStatus.UPLOADING, nullable=False, index=True)
    
    # Additional metadata
    file_metadata = Column(JSON, default=dict)
    
    # Relationships
    organization = relationship("Organization", back_populates="media_files")
    project = relationship("Project", back_populates="media_files")
    user = relationship("User", back_populates="media_files")
    jobs = relationship("Job", back_populates="media_file", cascade="all, delete-orphan")
    transcripts = relationship("Transcript", back_populates="media_file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MediaFile(id={self.id}, filename={self.filename}, status={self.status})>"
    
    @property
    def is_audio(self) -> bool:
        """Check if file is audio"""
        return self.mime_type.startswith("audio/")
    
    @property
    def is_video(self) -> bool:
        """Check if file is video"""
        return self.mime_type.startswith("video/")
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration"""
        if not self.duration_seconds:
            return "Unknown"
        
        hours = int(self.duration_seconds // 3600)
        minutes = int((self.duration_seconds % 3600) // 60)
        seconds = int(self.duration_seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def file_size_formatted(self) -> str:
        """Get formatted file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    def update_status(self, status: MediaStatus, metadata: dict = None):
        """Update media file status"""
        self.status = status
        if metadata:
            if not self.file_metadata:
                self.file_metadata = {}
            self.file_metadata.update(metadata)
    
    def set_audio_metadata(self, duration: float, sample_rate: int, channels: int, bitrate: int = None):
        """Set audio metadata"""
        self.duration_seconds = duration
        self.sample_rate = sample_rate
        self.channels = channels
        if bitrate:
            self.bitrate = bitrate
    
    @classmethod
    def get_by_organization(cls, db, organization_id: str, limit: int = 50):
        """Get media files by organization"""
        return db.query(cls).filter(
            cls.organization_id == organization_id,
            ~cls.is_deleted
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_by_status(cls, db, status: MediaStatus, limit: int = 100):
        """Get media files by status"""
        return db.query(cls).filter(
            cls.status == status,
            ~cls.is_deleted
        ).order_by(cls.created_at.asc()).limit(limit).all()