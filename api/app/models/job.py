"""
Job model for transcription and processing tasks
"""

import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, JSON, Enum as SQLEnum, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class JobType(str, enum.Enum):
    """Job type enum"""
    TRANSCRIBE = "transcribe"
    DIARIZE = "diarize"
    EXPORT = "export"
    ENHANCE_AUDIO = "enhance_audio"
    EXTRACT_METADATA = "extract_metadata"


class JobStatus(str, enum.Enum):
    """Job status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class JobPriority(int, enum.Enum):
    """Job priority enum"""
    LOW = 0
    NORMAL = 5
    HIGH = 10
    URGENT = 15


class Job(BaseModel):
    """Job model for tracking transcription and processing tasks"""
    
    __tablename__ = "jobs"
    
    # Organization and user
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    media_file_id = Column(UUID(as_uuid=True), ForeignKey("media_files.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Job details
    job_type = Column(SQLEnum(JobType), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    priority = Column(SQLEnum(JobPriority), default=JobPriority.NORMAL, nullable=False)
    
    # Job parameters and configuration
    parameters = Column(JSON, default=dict)
    
    # Progress tracking
    progress = Column(Float, default=0.0)  # 0-100
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_duration_seconds = Column(Integer, nullable=True)
    actual_duration_seconds = Column(Integer, nullable=True)
    
    # Worker information
    worker_id = Column(String(255), nullable=True)
    worker_hostname = Column(String(255), nullable=True)
    
    # Celery task ID
    celery_task_id = Column(String(255), nullable=True, unique=True)
    
    # Results and artifacts
    result = Column(JSON, default=dict)
    artifacts_path = Column(String(1000), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="jobs")
    media_file = relationship("MediaFile", back_populates="jobs")
    user = relationship("User", back_populates="jobs")
    transcripts = relationship("Transcript", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if job is currently active"""
        return self.status in [JobStatus.PENDING, JobStatus.PROCESSING]
    
    @property
    def is_finished(self) -> bool:
        """Check if job is finished (completed, failed, or cancelled)"""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.TIMEOUT]
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration"""
        if not self.actual_duration_seconds:
            return "Unknown"
        
        if self.actual_duration_seconds < 60:
            return f"{self.actual_duration_seconds}s"
        elif self.actual_duration_seconds < 3600:
            minutes = self.actual_duration_seconds // 60
            seconds = self.actual_duration_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = self.actual_duration_seconds // 3600
            minutes = (self.actual_duration_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def start_processing(self, worker_id: str = None, worker_hostname: str = None):
        """Mark job as started"""
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.utcnow()
        self.worker_id = worker_id
        self.worker_hostname = worker_hostname
    
    def complete(self, result: dict = None, artifacts_path: str = None):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress = 100.0
        
        if result:
            self.result = result
        
        if artifacts_path:
            self.artifacts_path = artifacts_path
        
        # Calculate actual duration
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.actual_duration_seconds = int(duration)
    
    def fail(self, error_message: str):
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        
        # Calculate actual duration even for failed jobs
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.actual_duration_seconds = int(duration)
    
    def cancel(self):
        """Cancel job"""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.actual_duration_seconds = int(duration)
    
    def update_progress(self, progress: float, status_message: str = None):
        """Update job progress"""
        self.progress = max(0, min(100, progress))
        
        if status_message:
            if not self.result:
                self.result = {}
            self.result["status_message"] = status_message
    
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return (
            self.status == JobStatus.FAILED and 
            self.retry_count < self.max_retries
        )
    
    def increment_retry(self):
        """Increment retry count and reset for retry"""
        self.retry_count += 1
        self.status = JobStatus.PENDING
        self.error_message = None
        self.started_at = None
        self.completed_at = None
        self.progress = 0.0
        self.worker_id = None
        self.worker_hostname = None
    
    def get_parameter(self, key: str, default=None):
        """Get job parameter"""
        if not self.parameters:
            return default
        return self.parameters.get(key, default)
    
    def set_parameter(self, key: str, value):
        """Set job parameter"""
        if not self.parameters:
            self.parameters = {}
        self.parameters[key] = value
    
    @classmethod
    def get_pending_jobs(cls, db, limit: int = 10):
        """Get pending jobs ordered by priority and creation time"""
        return db.query(cls).filter(
            cls.status == JobStatus.PENDING
        ).order_by(
            cls.priority.desc(),
            cls.created_at.asc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_organization(cls, db, organization_id: str, limit: int = 50):
        """Get jobs by organization"""
        return db.query(cls).filter(
            cls.organization_id == organization_id
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_active_jobs_count(cls, db) -> int:
        """Get count of active jobs"""
        return db.query(cls).filter(
            cls.status.in_([JobStatus.PENDING, JobStatus.PROCESSING])
        ).count()
    
    @classmethod
    def get_by_celery_task_id(cls, db, task_id: str):
        """Get job by Celery task ID"""
        return db.query(cls).filter(cls.celery_task_id == task_id).first()