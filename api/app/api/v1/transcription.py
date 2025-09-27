"""
Real audio transcription endpoint with AI processing
"""

import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.media import MediaFile
from app.models.job import Job, JobStatus
from app.core.storage import get_storage_client

logger = structlog.get_logger(__name__)
router = APIRouter()


class TranscriptionRequest(BaseModel):
    media_id: str = Field(..., description="Media file ID")
    language: str = Field(default="ar", description="Language code")
    model: str = Field(default="large-v3", description="Whisper model")
    diarization: bool = Field(default=True, description="Enable speaker diarization")
    enhancement_level: str = Field(default="medium", description="Audio enhancement level")
    custom_vocabulary: List[str] = Field(default_factory=list, description="Custom vocabulary")
    num_speakers: Optional[int] = Field(None, description="Expected number of speakers")


class TranscriptionResponse(BaseModel):
    success: bool
    message: str
    job_id: str
    status: str
    estimated_duration: int
    ai_processing_info: dict


@router.post("/transcribe", response_model=TranscriptionResponse)
async def create_transcription_job(
    request: TranscriptionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create real audio transcription job with AI processing
    """
    
    try:
        # Validate media file exists
        media_file = db.query(MediaFile).filter(
            MediaFile.id == request.media_id,
            MediaFile.organization_id == current_user.organization_id
        ).first()
        
        if not media_file:
            raise HTTPException(
                status_code=404,
                detail="الملف الصوتي غير موجود"
            )
        
        if media_file.status != "uploaded":
            raise HTTPException(
                status_code=400,
                detail="الملف ليس جاهزاً للمعالجة"
            )
        
        # Validate model
        valid_models = ["large-v3", "medium", "small"]
        if request.model not in valid_models:
            raise HTTPException(
                status_code=400,
                detail=f"نموذج غير صحيح. المتاح: {', '.join(valid_models)}"
            )
        
        # Create job record
        job = Job(
            organization_id=current_user.organization_id,
            media_file_id=media_file.id,
            user_id=current_user.id,
            job_type="transcribe",
            status=JobStatus.PENDING,
            parameters={
                "language": request.language,
                "model": request.model,
                "diarization": request.diarization,
                "enhancement_level": request.enhancement_level,
                "custom_vocabulary": request.custom_vocabulary[:50],  # Limit vocabulary
                "num_speakers": request.num_speakers
            }
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Estimate processing duration based on model and file size
        duration_estimates = {
            "large-v3": 180,  # 3 minutes
            "medium": 120,    # 2 minutes  
            "small": 60       # 1 minute
        }
        
        estimated_duration = duration_estimates.get(request.model, 120)
        
        # Add enhancement time
        enhancement_time = {
            "high": 60,
            "medium": 30,
            "light": 15
        }.get(request.enhancement_level, 30)
        
        total_estimate = estimated_duration + enhancement_time
        
        # Queue the actual transcription task
        try:
            # Import Celery task
            from worker.app.tasks.transcription import process_arabic_transcription
            
            # Get file path from storage
            storage_client = get_storage_client()
            bucket_name = os.getenv("MEDIA_BUCKET", "arabic-stt-media")
            
            # Create local temp file for processing
            temp_file_path = f"/tmp/processing/{media_file.filename}"
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            
            # Download file from storage to temp location
            try:
                data = storage_client.get_object(bucket_name, media_file.filename)
                with open(temp_file_path, 'wb') as f:
                    for chunk in data.stream(32*1024):
                        f.write(chunk)
                
                logger.info("File downloaded for processing", 
                           path=temp_file_path, size=os.path.getsize(temp_file_path))
                
            except Exception as e:
                logger.error("Failed to download file for processing", error=str(e))
                # Use demo processing if file download fails
                temp_file_path = media_file.file_path
            
            # Start real AI processing task
            task_result = process_arabic_transcription.delay(
                job_id=str(job.id),
                media_file_id=str(media_file.id),
                audio_file_path=temp_file_path,
                processing_options=job.parameters
            )
            
            # Update job with task ID
            job.worker_id = task_result.id
            job.status = JobStatus.PROCESSING
            db.commit()
            
            logger.info("Real AI transcription task queued",
                       job_id=job.id, task_id=task_result.id, model=request.model)
            
        except Exception as e:
            logger.error("Failed to queue transcription task", error=str(e))
            # Update job status to failed
            job.status = JobStatus.FAILED
            job.error_message = f"فشل في بدء المعالجة: {str(e)}"
            db.commit()
            
            raise HTTPException(
                status_code=500,
                detail="فشل في بدء معالجة التفريغ"
            )
        
        # Prepare response
        ai_processing_info = {
            "model_selected": request.model,
            "language_optimized": request.language,
            "diarization_enabled": request.diarization,
            "enhancement_level": request.enhancement_level,
            "custom_vocabulary_count": len(request.custom_vocabulary),
            "features_enabled": [
                "audio_enhancement",
                "arabic_asr",
                "speaker_diarization" if request.diarization else None,
                "text_postprocessing",
                "quality_assessment"
            ],
            "ai_models_used": [
                f"faster-whisper-{request.model}",
                "pyannote.audio-3.1" if request.diarization else None,
                "RNNoise" if request.enhancement_level != "light" else None
            ],
            "processing_pipeline": [
                "تحسين جودة الصوت وإزالة الضوضاء",
                f"تحويل الكلام إلى نص باستخدام Whisper {request.model}",
                "فصل المتحدثين باستخدام pyannote.audio" if request.diarization else None,
                "معالجة النص العربي وتحسين الجودة",
                "حفظ النتائج وإنشاء ملفات التصدير"
            ],
            "estimated_steps": 5 if request.diarization else 4,
            "gpu_acceleration": os.getenv("GPU_ENABLED", "false").lower() == "true"
        }
        
        # Filter out None values
        ai_processing_info["features_enabled"] = [f for f in ai_processing_info["features_enabled"] if f]
        ai_processing_info["ai_models_used"] = [m for m in ai_processing_info["ai_models_used"] if m]
        ai_processing_info["processing_pipeline"] = [p for p in ai_processing_info["processing_pipeline"] if p]
        
        return TranscriptionResponse(
            success=True,
            message="تم إنشاء مهمة التفريغ بنجاح وبدأت المعالجة الفعلية",
            job_id=str(job.id),
            status="processing",
            estimated_duration=total_estimate,
            ai_processing_info=ai_processing_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Transcription job creation failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="حدث خطأ في إنشاء مهمة التفريغ"
        )


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real job status from database and Celery"""
    
    try:
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.organization_id == current_user.organization_id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail="المهمة غير موجودة"
            )
        
        # Get real-time status from Celery if task is running
        task_status = None
        task_result = None
        
        if job.worker_id and job.status == JobStatus.PROCESSING:
            try:
                from app.celery_app import celery_app
                
                # Get task status from Celery
                task = celery_app.AsyncResult(job.worker_id)
                task_status = task.status
                task_result = task.result if task.ready() else None
                
                # Update job progress if available
                if task_result and isinstance(task_result, dict):
                    if "progress" in task_result:
                        job.progress = task_result["progress"]
                    if task_status == "SUCCESS":
                        job.status = JobStatus.COMPLETED
                        job.completed_at = datetime.utcnow()
                    elif task_status == "FAILURE":
                        job.status = JobStatus.FAILED
                        job.error_message = str(task_result.get("error", "معالجة فشلت"))
                
                db.commit()
                
            except Exception as e:
                logger.warning("Could not get Celery task status", error=str(e))
        
        # Prepare response
        response = {
            "job": {
                "id": str(job.id),
                "media_file_id": str(job.media_file_id),
                "status": job.status.value,
                "progress": job.progress or 0,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message,
                "parameters": job.parameters,
                "worker_id": job.worker_id
            },
            "ai_processing": {
                "celery_task_status": task_status,
                "real_ai_processing": job.worker_id is not None,
                "model_loading": task_status == "PENDING",
                "processing_active": task_status == "PROGRESS",
                "gpu_enabled": os.getenv("GPU_ENABLED", "false").lower() == "true"
            }
        }
        
        # Add result if job is completed
        if job.status == JobStatus.COMPLETED and task_result:
            response["result"] = task_result
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job status", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="حدث خطأ في استرجاع حالة المهمة"
        )