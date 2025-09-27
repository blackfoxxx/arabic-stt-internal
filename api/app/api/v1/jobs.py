"""
Job management endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.job import Job, JobType, JobStatus, JobPriority
from app.models.media import MediaFile, MediaStatus
from app.services.transcription_service import TranscriptionService

router = APIRouter()


# Request/Response schemas
class TranscribeJobRequest(BaseModel):
    media_id: str = Field(..., regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
    language: str = Field(default="ar", regex=r'^[a-z]{2}(-[A-Z]{2})?$')
    model: str = Field(default="large-v3", regex=r'^(large-v3|medium|small)$')
    diarization: bool = Field(default=True)
    denoise: bool = Field(default=True)
    custom_vocabulary: Optional[List[str]] = Field(default=None, max_items=100)
    priority: JobPriority = Field(default=JobPriority.NORMAL)
    
    @validator('custom_vocabulary')
    def validate_vocabulary(cls, v):
        if v is not None:
            # Filter out empty strings and limit length
            filtered = [word.strip() for word in v if word.strip()]
            if len(filtered) > 100:
                raise ValueError('Custom vocabulary cannot exceed 100 terms')
            return filtered[:100]  # Ensure limit
        return v


class JobResponse(BaseModel):
    id: str
    media_file_id: str
    media_filename: str
    job_type: JobType
    status: JobStatus
    priority: JobPriority
    progress: float
    parameters: dict
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration_seconds: Optional[int]
    actual_duration_seconds: Optional[int]
    worker_id: Optional[str]
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    size: int
    has_next: bool


@router.post("/transcribe", response_model=JobResponse)
async def create_transcription_job(
    request: TranscribeJobRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create transcription job"""
    
    # Get media file
    media_file = db.query(MediaFile).filter(
        MediaFile.id == request.media_id,
        MediaFile.organization_id == current_user.organization_id,
        ~MediaFile.is_deleted
    ).first()
    
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    if media_file.status != MediaStatus.UPLOADED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Media file must be uploaded before transcription"
        )
    
    # Check for existing active jobs
    active_job = db.query(Job).filter(
        Job.media_file_id == media_file.id,
        Job.job_type == JobType.TRANSCRIBE,
        Job.status.in_([JobStatus.PENDING, JobStatus.PROCESSING])
    ).first()
    
    if active_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Media file already has an active transcription job"
        )
    
    # Check organization limits
    # TODO: Implement usage limit checking
    
    # Prepare job parameters
    job_parameters = {
        "language": request.language,
        "model": request.model,
        "diarization": request.diarization,
        "denoise": request.denoise,
        "custom_vocabulary": request.custom_vocabulary or [],
        "audio_enhancement_level": "medium" if request.denoise else "none",
        "initial_prompt": "الكلام باللغة العربية" if request.language.startswith("ar") else None
    }
    
    # Estimate processing duration based on file duration and model
    estimated_duration = None
    if media_file.duration_seconds:
        # Estimation factors based on model and settings
        factor = {
            "large-v3": 1.5,  # 1.5x realtime
            "medium": 1.0,    # 1x realtime  
            "small": 0.7      # 0.7x realtime
        }.get(request.model, 1.0)
        
        if request.diarization:
            factor *= 1.3  # Diarization adds ~30% processing time
        
        if request.denoise:
            factor *= 1.2  # Denoising adds ~20% processing time
        
        estimated_duration = int(media_file.duration_seconds * factor)
    
    # Create job
    job = Job(
        organization_id=current_user.organization_id,
        media_file_id=media_file.id,
        user_id=current_user.id,
        job_type=JobType.TRANSCRIBE,
        status=JobStatus.PENDING,
        priority=request.priority,
        parameters=job_parameters,
        estimated_duration_seconds=estimated_duration
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Queue job for processing (background task)
    transcription_service = TranscriptionService()
    background_tasks.add_task(
        transcription_service.queue_transcription_job,
        job_id=str(job.id)
    )
    
    return JobResponse(
        id=str(job.id),
        media_file_id=str(job.media_file_id),
        media_filename=media_file.original_name,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        progress=job.progress,
        parameters=job.parameters,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        estimated_duration_seconds=job.estimated_duration_seconds,
        actual_duration_seconds=job.actual_duration_seconds,
        worker_id=job.worker_id,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job details"""
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.organization_id == current_user.organization_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return JobResponse(
        id=str(job.id),
        media_file_id=str(job.media_file_id),
        media_filename=job.media_file.original_name,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        progress=job.progress,
        parameters=job.parameters,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        estimated_duration_seconds=job.estimated_duration_seconds,
        actual_duration_seconds=job.actual_duration_seconds,
        worker_id=job.worker_id,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    page: int = 1,
    size: int = 20,
    status: Optional[JobStatus] = None,
    job_type: Optional[JobType] = None,
    media_file_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List jobs"""
    
    # Build query
    query = db.query(Job).filter(
        Job.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if status:
        query = query.filter(Job.status == status)
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    if media_file_id:
        query = query.filter(Job.media_file_id == media_file_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    jobs = query.order_by(Job.created_at.desc()).offset(offset).limit(size).all()
    
    # Convert to response format
    job_responses = []
    for job in jobs:
        job_responses.append(JobResponse(
            id=str(job.id),
            media_file_id=str(job.media_file_id),
            media_filename=job.media_file.original_name,
            job_type=job.job_type,
            status=job.status,
            priority=job.priority,
            progress=job.progress,
            parameters=job.parameters,
            error_message=job.error_message,
            started_at=job.started_at,
            completed_at=job.completed_at,
            estimated_duration_seconds=job.estimated_duration_seconds,
            actual_duration_seconds=job.actual_duration_seconds,
            worker_id=job.worker_id,
            retry_count=job.retry_count,
            max_retries=job.max_retries,
            created_at=job.created_at,
            updated_at=job.updated_at
        ))
    
    return JobListResponse(
        jobs=job_responses,
        total=total,
        page=page,
        size=size,
        has_next=offset + size < total
    )


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel job"""
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.organization_id == current_user.organization_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if not job.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not active and cannot be cancelled"
        )
    
    # Cancel the job
    job.cancel()
    
    # Cancel Celery task if exists
    if job.celery_task_id:
        from app.worker.celery_app import celery_app
        celery_app.control.revoke(job.celery_task_id, terminate=True)
    
    db.commit()
    
    return JobResponse(
        id=str(job.id),
        media_file_id=str(job.media_file_id),
        media_filename=job.media_file.original_name,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        progress=job.progress,
        parameters=job.parameters,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        estimated_duration_seconds=job.estimated_duration_seconds,
        actual_duration_seconds=job.actual_duration_seconds,
        worker_id=job.worker_id,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retry failed job"""
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.organization_id == current_user.organization_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if not job.can_retry():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be retried"
        )
    
    # Reset job for retry
    job.increment_retry()
    db.commit()
    
    # Queue job for processing again
    transcription_service = TranscriptionService()
    background_tasks.add_task(
        transcription_service.queue_transcription_job,
        job_id=str(job.id)
    )
    
    return JobResponse(
        id=str(job.id),
        media_file_id=str(job.media_file_id),
        media_filename=job.media_file.original_name,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        progress=job.progress,
        parameters=job.parameters,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        estimated_duration_seconds=job.estimated_duration_seconds,
        actual_duration_seconds=job.actual_duration_seconds,
        worker_id=job.worker_id,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.get("/stats/summary")
async def get_job_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job statistics summary"""
    
    # Get job counts by status
    from sqlalchemy import func
    
    stats_query = db.query(
        Job.status,
        func.count(Job.id).label('count')
    ).filter(
        Job.organization_id == current_user.organization_id
    ).group_by(Job.status).all()
    
    # Convert to dictionary
    stats = {status.value: 0 for status in JobStatus}
    for status, count in stats_query:
        stats[status.value] = count
    
    # Get recent activity (last 24 hours)
    from datetime import datetime, timedelta
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    
    recent_jobs = db.query(Job).filter(
        Job.organization_id == current_user.organization_id,
        Job.created_at >= recent_cutoff
    ).count()
    
    # Get total processing time
    total_duration = db.query(
        func.sum(Job.actual_duration_seconds)
    ).filter(
        Job.organization_id == current_user.organization_id,
        Job.status == JobStatus.COMPLETED
    ).scalar() or 0
    
    # Get average processing time
    avg_duration = db.query(
        func.avg(Job.actual_duration_seconds)
    ).filter(
        Job.organization_id == current_user.organization_id,
        Job.status == JobStatus.COMPLETED,
        Job.actual_duration_seconds.isnot(None)
    ).scalar() or 0
    
    return {
        "status_counts": stats,
        "recent_jobs_24h": recent_jobs,
        "total_processing_time_seconds": int(total_duration),
        "average_processing_time_seconds": int(avg_duration),
        "success_rate": stats.get("completed", 0) / max(1, sum(stats.values())) * 100
    }


@router.get("/queue/status")
async def get_queue_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get queue status information"""
    
    # Get queue statistics
    pending_jobs = db.query(Job).filter(
        Job.status == JobStatus.PENDING
    ).count()
    
    processing_jobs = db.query(Job).filter(
        Job.status == JobStatus.PROCESSING
    ).count()
    
    # Get organization's position in queue
    org_pending = db.query(Job).filter(
        Job.organization_id == current_user.organization_id,
        Job.status == JobStatus.PENDING
    ).count()
    
    # Calculate estimated wait time
    # Simple estimation based on average processing time and queue position
    avg_processing_time = db.query(
        func.avg(Job.actual_duration_seconds)
    ).filter(
        Job.status == JobStatus.COMPLETED,
        Job.actual_duration_seconds.isnot(None)
    ).scalar() or 60  # Default 60 seconds
    
    estimated_wait_seconds = int(pending_jobs * avg_processing_time / 2)  # Assume 2 concurrent workers
    
    return {
        "queue_length": pending_jobs,
        "processing_jobs": processing_jobs,
        "organization_pending": org_pending,
        "estimated_wait_seconds": estimated_wait_seconds,
        "estimated_wait_formatted": format_duration(estimated_wait_seconds)
    }


def format_duration(seconds: int) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"