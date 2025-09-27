"""
Working media upload endpoint with real file handling
"""

import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import mimetypes
import structlog

from app.core.database import get_db
from app.core.storage import get_storage_client
from app.models.user import User
from app.models.media import MediaFile
from app.core.auth import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/upload")
async def upload_media_file(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload audio/video file directly
    """
    
    try:
        # Validate file type
        allowed_types = [
            'audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/flac', 'audio/ogg',
            'video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"نوع الملف غير مدعوم: {file.content_type}"
            )
        
        # Validate file size (500MB max)
        max_size = 500 * 1024 * 1024  # 500MB
        file_content = await file.read()
        
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"حجم الملف كبير جداً: {len(file_content)} bytes (الحد الأقصى: {max_size})"
            )
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="الملف فارغ"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename or "audio.mp3")[1]
        storage_filename = f"{file_id}{file_extension}"
        
        # Store file in MinIO
        storage_client = get_storage_client()
        
        try:
            # Upload to MinIO
            from io import BytesIO
            storage_client.put_object(
                bucket_name=os.getenv("MEDIA_BUCKET", "arabic-stt-media"),
                object_name=storage_filename,
                data=BytesIO(file_content),
                length=len(file_content),
                content_type=file.content_type
            )
            
            logger.info("File uploaded to storage", 
                       filename=storage_filename, 
                       size=len(file_content))
            
        except Exception as e:
            logger.error("Failed to upload to storage", error=str(e))
            raise HTTPException(
                status_code=500,
                detail="فشل في رفع الملف إلى التخزين"
            )
        
        # Create media file record
        media_file = MediaFile(
            organization_id=current_user.organization_id,
            project_id=project_id,
            user_id=current_user.id,
            filename=storage_filename,
            original_name=file.filename or "audio.mp3",
            mime_type=file.content_type,
            file_size=len(file_content),
            file_path=f"media/{storage_filename}",
            status="uploaded"
        )
        
        db.add(media_file)
        db.commit()
        db.refresh(media_file)
        
        logger.info("Media file record created", 
                   media_id=media_file.id, 
                   filename=file.filename)
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "تم رفع الملف بنجاح",
                "media_file": {
                    "id": str(media_file.id),
                    "filename": storage_filename,
                    "original_name": file.filename,
                    "size": len(file_content),
                    "content_type": file.content_type,
                    "status": "uploaded",
                    "created_at": media_file.created_at.isoformat()
                },
                "ready_for_processing": True,
                "next_step": "يمكنك الآن إنشاء مهمة تفريغ لهذا الملف"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Upload failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="حدث خطأ في رفع الملف"
        )


@router.get("/{media_id}")
async def get_media_file(
    media_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get media file information"""
    
    try:
        media_file = db.query(MediaFile).filter(
            MediaFile.id == media_id,
            MediaFile.organization_id == current_user.organization_id
        ).first()
        
        if not media_file:
            raise HTTPException(
                status_code=404,
                detail="الملف غير موجود"
            )
        
        return {
            "id": str(media_file.id),
            "filename": media_file.filename,
            "original_name": media_file.original_name,
            "size": media_file.file_size,
            "content_type": media_file.mime_type,
            "duration": media_file.duration_seconds,
            "status": media_file.status,
            "created_at": media_file.created_at.isoformat(),
            "ready_for_processing": media_file.status == "uploaded"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get media file", media_id=media_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="حدث خطأ في استرجاع معلومات الملف"
        )