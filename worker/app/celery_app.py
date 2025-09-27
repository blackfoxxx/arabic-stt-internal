"""
Celery application configuration for Arabic STT workers
"""

import os
from celery import Celery
from celery.signals import worker_ready, worker_shutdown, task_prerun, task_postrun
import structlog

# Configure logging
logger = structlog.get_logger(__name__)

# Create Celery app
celery_app = Celery("arabic-stt-worker")

# Configuration
celery_app.conf.update(
    # Broker settings
    broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    
    # Task settings
    task_serializer="pickle",  # Support complex objects
    accept_content=["pickle", "json"],
    result_serializer="pickle",
    timezone="UTC",
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Process one task at a time for memory management
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Task routing
    task_routes={
        "app.tasks.transcription.*": {"queue": "transcription"},
        "app.tasks.diarization.*": {"queue": "diarization"},
        "app.tasks.export.*": {"queue": "export"},
        "app.tasks.cleanup.*": {"queue": "cleanup"}
    },
    
    # Result expiration
    result_expires=3600,  # 1 hour
    
    # Task soft/hard time limits
    task_soft_time_limit=1800,  # 30 minutes soft limit
    task_time_limit=2400,       # 40 minutes hard limit
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Worker pool settings
    worker_pool="threads",  # Use threads for I/O bound tasks
    worker_concurrency=int(os.getenv("MAX_CONCURRENT_JOBS", "2")),
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Security
    worker_hijack_root_logger=False,
    worker_log_color=False,
    
    # Task annotations for monitoring
    task_annotations={
        "app.tasks.transcription.transcribe_audio": {"rate_limit": "10/m"},
        "app.tasks.diarization.diarize_speakers": {"rate_limit": "5/m"},
    }
)

# Import tasks to register them
from app.tasks import transcription, diarization, export, cleanup


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Worker ready signal handler"""
    logger.info("Arabic STT worker ready", worker_id=sender.hostname)
    
    # Download required models on startup
    from app.utils.model_manager import ModelManager
    model_manager = ModelManager()
    
    try:
        # Download default ASR model
        default_model = os.getenv("DEFAULT_ASR_MODEL", "large-v3")
        model_manager.ensure_model_available(f"openai/whisper-{default_model}")
        logger.info("ASR model ready", model=default_model)
        
        # Download diarization model
        model_manager.ensure_model_available("pyannote/speaker-diarization-3.1")
        logger.info("Diarization model ready")
        
    except Exception as e:
        logger.error("Failed to download models on startup", error=str(e))


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Worker shutdown signal handler"""
    logger.info("Arabic STT worker shutting down", worker_id=sender.hostname)


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Task prerun signal handler"""
    logger.info("Task starting", task_id=task_id, task_name=task.name)


@task_postrun.connect 
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """Task postrun signal handler"""
    logger.info("Task completed", task_id=task_id, task_name=task.name, state=state)


# Error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing"""
    logger.info("Debug task executed", task_id=self.request.id)
    return {"status": "debug_ok", "worker": self.request.hostname}


# Health check task
@celery_app.task
def health_check():
    """Health check task"""
    return {
        "status": "healthy",
        "timestamp": str(datetime.utcnow()),
        "worker": "arabic-stt-worker"
    }


# Configure task discovery
celery_app.autodiscover_tasks([
    "app.tasks.transcription",
    "app.tasks.diarization", 
    "app.tasks.export",
    "app.tasks.cleanup"
])

if __name__ == "__main__":
    celery_app.start()