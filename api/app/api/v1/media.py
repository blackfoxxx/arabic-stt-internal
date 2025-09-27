"""
Media file management endpoints
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.storage import storage, file_validator
from app.core.config import get_settings
from app.models.user import User
from app.models.media import MediaFile, MediaStatus
from app.models.project import Project

router = APIRouter()
settings = get_settings()


# Request/Response schemas
class UploadUrlRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=500)
    content_type: str = Field(..., regex=r'^(audio|video)\/[a-zA-Z0-9][a-zA-Z0-9\-\+]*$')
    file_size: int = Field(..., gt=0, le=settings.MAX_FILE_SIZE_MB * 1024 * 1024)
    project_id: Optional[str] = Field(None, regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
    
    @validator('filename')
    def validate_filename(cls, v):
        valid, result = file_validator.validate_filename(v)
        if not valid:
            raise ValueError(f'Invalid filename: {result}')
        return result
    
    @validator('content_type')
    def validate_content_type(cls, v):
        if v not in settings.ALLOWED_MIME_TYPES:
            raise ValueError(f'Unsupported content type: {v}')
        return v


class UploadUrlResponse(BaseModel):
    upload_url: str
    media_file_id: str
    expires_at: datetime
    max_file_size: int


class MediaFileResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    mime_type: str
    file_size: int
    duration_seconds: Optional[float]
    sample_rate: Optional[int]
    channels: Optional[int]
    status: MediaStatus
    project_id: Optional[str]
    project_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    files: List[MediaFileResponse]
    total: int
    page: int
    size: int
    has_next: bool


@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(
    request: UploadUrlRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate presigned URL for media file upload"""
    
    # Validate project access if specified
    if request.project_id:
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.organization_id == current_user.organization_id,
            ~Project.is_deleted
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    # Check organization limits
    # TODO: Implement usage checking
    
    # Create media file record
    media_file = MediaFile(
        organization_id=current_user.organization_id,
        project_id=uuid.UUID(request.project_id) if request.project_id else None,
        user_id=current_user.id,
        filename=f"{uuid.uuid4()}.{request.filename.split('.')[-1]}",
        original_name=request.filename,
        mime_type=request.content_type,
        file_size=request.file_size,
        status=MediaStatus.UPLOADING
    )
    
    db.add(media_file)
    db.commit()
    db.refresh(media_file)
    
    # Generate object name for storage
    object_name = storage.generate_unique_object_name(
        prefix=f"media/{current_user.organization_id}",
        extension=request.filename.split('.')[-1]
    )
    
    # Update media file with storage path
    media_file.file_path = object_name
    db.commit()
    
    # Generate presigned upload URL
    expires = timedelta(hours=1)
    upload_url = storage.generate_presigned_upload_url(
        bucket=settings.MEDIA_BUCKET,
        object_name=object_name,
        expires=expires,
        content_type=request.content_type
    )
    
    return UploadUrlResponse(
        upload_url=upload_url,
        media_file_id=str(media_file.id),
        expires_at=datetime.utcnow() + expires,
        max_file_size=request.file_size
    )


@router.post("/upload-complete/{media_file_id}")
async def upload_complete(
    media_file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark upload as complete and trigger processing"""
    
    # Get media file
    media_file = db.query(MediaFile).filter(
        MediaFile.id == media_file_id,
        MediaFile.organization_id == current_user.organization_id
    ).first()
    
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    if media_file.status != MediaStatus.UPLOADING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Media file not in uploading status"
        )
    
    # Verify file exists in storage
    if not storage.file_exists(settings.MEDIA_BUCKET, media_file.file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File not found in storage"
        )
    
    # Get file info and update metadata
    file_info = storage.get_file_info(settings.MEDIA_BUCKET, media_file.file_path)
    if file_info:
        media_file.file_size = file_info["size"]
        
        # Extract audio metadata (this would be done by a worker in production)
        # For now, just update status
        media_file.status = MediaStatus.UPLOADED
    
    db.commit()
    
    return {"message": "Upload completed successfully", "media_file_id": str(media_file.id)}


@router.get("/{media_file_id}", response_model=MediaFileResponse)
async def get_media_file(
    media_file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get media file details"""
    
    media_file = db.query(MediaFile).filter(
        MediaFile.id == media_file_id,
        MediaFile.organization_id == current_user.organization_id
    ).first()
    
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    # Get project name if available
    project_name = None
    if media_file.project_id:
        project = db.query(Project).filter(Project.id == media_file.project_id).first()
        project_name = project.name if project else None
    
    return MediaFileResponse(
        id=str(media_file.id),
        filename=media_file.filename,
        original_name=media_file.original_name,
        mime_type=media_file.mime_type,
        file_size=media_file.file_size,
        duration_seconds=media_file.duration_seconds,
        sample_rate=media_file.sample_rate,
        channels=media_file.channels,
        status=media_file.status,
        project_id=str(media_file.project_id) if media_file.project_id else None,
        project_name=project_name,
        created_at=media_file.created_at,
        updated_at=media_file.updated_at
    )


@router.get("/", response_model=MediaListResponse)
async def list_media_files(
    page: int = 1,
    size: int = 20,
    project_id: Optional[str] = None,
    status: Optional[MediaStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List media files"""
    
    # Build query
    query = db.query(MediaFile).filter(
        MediaFile.organization_id == current_user.organization_id,
        ~MediaFile.is_deleted
    )
    
    # Apply filters
    if project_id:
        query = query.filter(MediaFile.project_id == project_id)
    
    if status:
        query = query.filter(MediaFile.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    media_files = query.order_by(MediaFile.created_at.desc()).offset(offset).limit(size).all()
    
    # Convert to response format
    files = []
    for media_file in media_files:
        project_name = None
        if media_file.project_id:
            project = db.query(Project).filter(Project.id == media_file.project_id).first()
            project_name = project.name if project else None
        
        files.append(MediaFileResponse(
            id=str(media_file.id),
            filename=media_file.filename,
            original_name=media_file.original_name,
            mime_type=media_file.mime_type,
            file_size=media_file.file_size,
            duration_seconds=media_file.duration_seconds,
            sample_rate=media_file.sample_rate,
            channels=media_file.channels,
            status=media_file.status,
            project_id=str(media_file.project_id) if media_file.project_id else None,
            project_name=project_name,
            created_at=media_file.created_at,
            updated_at=media_file.updated_at
        ))
    
    return MediaListResponse(
        files=files,
        total=total,
        page=page,
        size=size,
        has_next=offset + size < total
    )


@router.delete("/{media_file_id}")
async def delete_media_file(
    media_file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete media file"""
    
    media_file = db.query(MediaFile).filter(
        MediaFile.id == media_file_id,
        MediaFile.organization_id == current_user.organization_id
    ).first()
    
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    # Check if file has active jobs
    from app.models.job import Job, JobStatus
    active_jobs = db.query(Job).filter(
        Job.media_file_id == media_file.id,
        Job.status.in_([JobStatus.PENDING, JobStatus.PROCESSING])
    ).count()
    
    if active_jobs > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete media file with active jobs"
        )
    
    # Soft delete media file
    media_file.soft_delete()
    
    # Delete file from storage (background task in production)
    try:
        storage.delete_file(settings.MEDIA_BUCKET, media_file.file_path)
        if media_file.processed_path:
            storage.delete_file(settings.PROCESSED_BUCKET, media_file.processed_path)
    except Exception as e:
        # Log error but don't fail the request
        import structlog
        logger = structlog.get_logger(__name__)
        logger.error("Failed to delete files from storage", error=str(e))
    
    db.commit()
    
    return {"message": "Media file deleted successfully"}


@router.get("/{media_file_id}/download-url")
async def get_download_url(
    media_file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get presigned download URL for media file"""
    
    media_file = db.query(MediaFile).filter(
        MediaFile.id == media_file_id,
        MediaFile.organization_id == current_user.organization_id
    ).first()
    
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    # Generate download URL
    download_url = storage.generate_presigned_download_url(
        bucket=settings.MEDIA_BUCKET,
        object_name=media_file.file_path,
        expires=timedelta(hours=1)
    )
    
    return {
        "download_url": download_url,
        "expires_at": datetime.utcnow() + timedelta(hours=1),
        "filename": media_file.original_name
    }