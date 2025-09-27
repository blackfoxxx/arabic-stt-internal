"""
Transcription service for managing transcription jobs
"""

import structlog
from typing import Dict, Any, Optional
from celery import current_app

logger = structlog.get_logger(__name__)


class TranscriptionService:
    """Service for managing transcription workflows"""
    
    def __init__(self):
        self.celery_app = current_app
    
    async def queue_transcription_job(self, job_id: str) -> bool:
        """Queue transcription job for processing"""
        
        try:
            # Import here to avoid circular imports
            from app.worker.tasks.transcription import transcribe_audio_task
            
            # Get job details from database
            from app.core.database import get_sync_db
            from app.models.job import Job
            
            with get_sync_db() as db:
                job = db.query(Job).filter(Job.id == job_id).first()
                if not job:
                    logger.error("Job not found for queuing", job_id=job_id)
                    return False
                
                media_file_path = job.media_file.file_path
                config = job.parameters
            
            # Queue the task
            task = transcribe_audio_task.delay(
                job_id=job_id,
                media_file_path=media_file_path,
                config=config
            )
            
            # Update job with Celery task ID
            with get_sync_db() as db:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.celery_task_id = task.id
                    db.commit()
            
            logger.info("Transcription job queued successfully", 
                       job_id=job_id, task_id=task.id)
            
            return True
            
        except Exception as e:
            logger.error("Failed to queue transcription job", 
                        job_id=job_id, error=str(e))
            return False
    
    async def estimate_transcription_cost(
        self, 
        media_file_id: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate transcription cost and processing time"""
        
        try:
            from app.worker.tasks.transcription import estimate_transcription_cost
            
            # Queue estimation task
            task = estimate_transcription_cost.delay(media_file_id, config)
            result = task.get(timeout=30)  # 30 second timeout for estimation
            
            return result
            
        except Exception as e:
            logger.error("Cost estimation failed", error=str(e))
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_processing_status(self, job_id: str) -> Dict[str, Any]:
        """Get real-time processing status"""
        
        try:
            from app.core.database import get_sync_db
            from app.models.job import Job
            
            with get_sync_db() as db:
                job = db.query(Job).filter(Job.id == job_id).first()
                if not job:
                    return {"status": "not_found"}
                
                status_info = {
                    "job_id": job_id,
                    "status": job.status.value,
                    "progress": float(job.progress),
                    "estimated_completion": None,
                    "current_step": None
                }
                
                # Get detailed status from Celery if job is active
                if job.celery_task_id and job.is_active:
                    try:
                        from celery.result import AsyncResult
                        task_result = AsyncResult(job.celery_task_id)
                        
                        if task_result.state == "PROGRESS":
                            task_info = task_result.info or {}
                            status_info.update({
                                "current_step": task_info.get("step"),
                                "progress": task_info.get("progress", job.progress),
                                "eta_seconds": task_info.get("eta_seconds")
                            })
                    except Exception as e:
                        logger.warning("Failed to get Celery task status", 
                                      task_id=job.celery_task_id, error=str(e))
                
                return status_info
                
        except Exception as e:
            logger.error("Failed to get processing status", job_id=job_id, error=str(e))
            return {"status": "error", "error": str(e)}