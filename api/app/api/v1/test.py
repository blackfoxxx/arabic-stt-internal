"""
Test endpoints for development and health checking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import time
import uuid

from app.core.database import get_db, db_monitor
from app.core.redis import get_redis_health, cache
from app.core.storage import get_storage_health
from app.core.auth import get_optional_user
from app.models.user import User

router = APIRouter()


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": time.time()}


@router.get("/health/full")
async def full_health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for all services"""
    
    health_status = {
        "status": "healthy",
        "service": "Arabic STT SaaS API",
        "version": "1.0.0",
        "timestamp": time.time(),
        "checks": {}
    }
    
    try:
        # Database health
        try:
            # Test database connection with a simple query
            db.execute("SELECT 1")
            health_status["checks"]["database"] = {
                "status": "healthy",
                "response_time_ms": 0  # Would measure actual time in production
            }
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Redis health
        try:
            redis_healthy = await get_redis_health()
            health_status["checks"]["redis"] = {
                "status": "healthy" if redis_healthy else "unhealthy"
            }
        except Exception as e:
            health_status["checks"]["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Storage health
        try:
            storage_healthy = await get_storage_health()
            health_status["checks"]["storage"] = {
                "status": "healthy" if storage_healthy else "unhealthy"
            }
        except Exception as e:
            health_status["checks"]["storage"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Worker health (check Redis queue)
        try:
            from app.core.redis import job_queue
            queue_length = await job_queue.get_queue_length()
            active_jobs = await job_queue.get_active_jobs()
            
            health_status["checks"]["worker"] = {
                "status": "healthy",
                "queue_length": queue_length,
                "active_jobs": active_jobs
            }
        except Exception as e:
            health_status["checks"]["worker"] = {
                "status": "unknown",
                "error": str(e)
            }
        
        # Overall status
        all_healthy = all(
            check.get("status") == "healthy" 
            for check in health_status["checks"].values()
        )
        health_status["status"] = "healthy" if all_healthy else "degraded"
        
    except Exception as e:
        health_status["status"] = "unhealthy" 
        health_status["error"] = str(e)
    
    return health_status


@router.get("/database/stats")
async def database_stats(
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get database statistics"""
    
    try:
        # Get connection stats
        connection_stats = await db_monitor.get_connection_stats()
        
        # Get database size
        db_size = await db_monitor.get_database_size()
        
        # Get table sizes
        table_sizes = await db_monitor.get_table_sizes()
        
        # Get slow queries (admin only)
        slow_queries = []
        if current_user and current_user.is_admin:
            slow_queries = await db_monitor.get_slow_queries()
        
        return {
            "status": "healthy",
            "connection_stats": connection_stats,
            "database_size": db_size,
            "table_sizes": table_sizes[:10],  # Top 10 largest tables
            "slow_queries": slow_queries
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/system/info")
async def system_info():
    """Get system information"""
    
    import psutil
    import platform
    
    try:
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory info
        memory = psutil.virtual_memory()
        
        # Disk info
        disk = psutil.disk_usage('/')
        
        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "architecture": platform.machine(),
                "python_version": platform.python_version()
            },
            "cpu": {
                "count": cpu_count,
                "usage_percent": cpu_percent
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 1)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/cache/test")
async def test_cache():
    """Test Redis cache functionality"""
    
    try:
        test_key = f"test_cache_{uuid.uuid4().hex[:8]}"
        test_value = {
            "message": "Hello from Arabic STT Cache",
            "timestamp": time.time(),
            "data": ["item1", "item2", "item3"]
        }
        
        # Test cache set
        set_success = await cache.set(test_key, test_value, expire=60)
        if not set_success:
            return {"status": "error", "message": "Failed to set cache value"}
        
        # Test cache get
        retrieved_value = await cache.get(test_key)
        if retrieved_value != test_value:
            return {"status": "error", "message": "Cache value mismatch"}
        
        # Test cache delete
        delete_success = await cache.delete(test_key)
        if not delete_success:
            return {"status": "error", "message": "Failed to delete cache value"}
        
        # Verify deletion
        deleted_value = await cache.get(test_key)
        if deleted_value is not None:
            return {"status": "error", "message": "Cache value not properly deleted"}
        
        return {
            "status": "success",
            "message": "Cache test completed successfully",
            "operations": ["set", "get", "delete", "verify_deletion"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": "Cache test failed",
            "error": str(e)
        }


@router.get("/arabic/test")
async def test_arabic_support():
    """Test Arabic text handling"""
    
    arabic_test_data = {
        "simple_text": "مرحباً بكم في منصة التفريغ الصوتي العربية",
        "dialects": {
            "msa": "أهلاً وسهلاً، كيف حالكم اليوم؟",
            "iraqi": "شلونكم، شكو ماكو اليوم؟",
            "egyptian": "إزيكم، عاملين إيه النهاردة؟",
            "gulf": "شلونكم، شفيكم اليوم؟"
        },
        "technical_terms": [
            "الذكاء الاصطناعي",
            "التعلم الآلي", 
            "معالجة اللغات الطبيعية",
            "التفريغ الصوتي",
            "فصل المتحدثين"
        ],
        "numbers": {
            "arabic_numerals": "١٢٣٤٥٦٧٨٩٠",
            "mixed": "لديه ١٠ سنوات من الخبرة في ٥ مجالات مختلفة"
        },
        "rtl_test": "هذا نص تجريبي (with English) للتأكد من دعم RTL",
        "diacritics": "مَرْحَباً بِكُمْ فِي مَنَصَّةِ التَّفْرِيغِ الصَّوْتِيِّ العَرَبِيَّةِ"
    }
    
    # Test text processing
    try:
        processed_data = {}
        
        for key, value in arabic_test_data.items():
            if isinstance(value, str):
                processed_data[key] = {
                    "original": value,
                    "length": len(value),
                    "word_count": len(value.split()),
                    "contains_arabic": any('\u0600' <= char <= '\u06FF' for char in value),
                    "contains_diacritics": any('\u064B' <= char <= '\u065F' for char in value)
                }
            else:
                processed_data[key] = value
        
        return {
            "status": "success",
            "message": "Arabic text processing test completed",
            "test_data": processed_data,
            "encoding": "UTF-8",
            "rtl_support": True
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": "Arabic text processing test failed",
            "error": str(e)
        }


@router.post("/audio/validate")
async def validate_audio_endpoint():
    """Test audio validation endpoint"""
    
    # Mock audio validation for API testing
    mock_audio_info = {
        "filename": "test_arabic_audio.wav",
        "duration_seconds": 120.5,
        "sample_rate": 16000,
        "channels": 1,
        "file_size_bytes": 3841000,
        "mime_type": "audio/wav",
        "quality_score": 0.85,
        "estimated_transcription_time": 180.75,
        "supported_languages": ["ar", "ar-IQ", "ar-EG"],
        "recommended_model": "large-v3"
    }
    
    return {
        "status": "success",
        "message": "Audio validation test completed",
        "audio_info": mock_audio_info,
        "processing_estimate": {
            "transcription_time": "~3 minutes",
            "diarization_time": "~1 minute", 
            "total_time": "~4 minutes",
            "confidence": "High (Arabic optimized)"
        }
    }


@router.post("/transcription/simulate")
async def simulate_transcription():
    """Simulate transcription process for testing"""
    
    # Mock transcription result
    mock_result = {
        "job_id": str(uuid.uuid4()),
        "status": "completed",
        "language_detected": "ar",
        "confidence_score": 0.92,
        "processing_time_seconds": 245.3,
        "model_used": "large-v3",
        "segments": [
            {
                "id": 0,
                "start_time": 0.0,
                "end_time": 3.5,
                "text": "السلام عليكم ورحمة الله وبركاته",
                "confidence": 0.95,
                "speaker_id": "SPEAKER_00",
                "words": [
                    {"word": "السلام", "start": 0.0, "end": 0.8, "confidence": 0.96},
                    {"word": "عليكم", "start": 0.8, "end": 1.3, "confidence": 0.94},
                    {"word": "ورحمة", "start": 1.3, "end": 1.8, "confidence": 0.93},
                    {"word": "الله", "start": 1.8, "end": 2.2, "confidence": 0.98},
                    {"word": "وبركاته", "start": 2.2, "end": 3.5, "confidence": 0.94}
                ]
            },
            {
                "id": 1,
                "start_time": 4.0,
                "end_time": 8.2,
                "text": "مرحباً بكم في هذا الاجتماع المهم",
                "confidence": 0.89,
                "speaker_id": "SPEAKER_00",
                "words": [
                    {"word": "مرحباً", "start": 4.0, "end": 4.6, "confidence": 0.91},
                    {"word": "بكم", "start": 4.6, "end": 4.9, "confidence": 0.88},
                    {"word": "في", "start": 4.9, "end": 5.1, "confidence": 0.87},
                    {"word": "هذا", "start": 5.1, "end": 5.4, "confidence": 0.90},
                    {"word": "الاجتماع", "start": 5.4, "end": 6.2, "confidence": 0.89},
                    {"word": "المهم", "start": 6.2, "end": 8.2, "confidence": 0.88}
                ]
            },
            {
                "id": 2,
                "start_time": 9.0,
                "end_time": 12.5,
                "text": "شكراً لكم على الحضور",
                "confidence": 0.94,
                "speaker_id": "SPEAKER_01",
                "words": [
                    {"word": "شكراً", "start": 9.0, "end": 9.5, "confidence": 0.95},
                    {"word": "لكم", "start": 9.5, "end": 9.8, "confidence": 0.93},
                    {"word": "على", "start": 9.8, "end": 10.1, "confidence": 0.94},
                    {"word": "الحضور", "start": 10.1, "end": 12.5, "confidence": 0.93}
                ]
            }
        ],
        "speakers": [
            {
                "id": "SPEAKER_00",
                "label": "SPEAKER_00",
                "display_name": "المتحدث الأول",
                "total_speaking_time": 11.7,
                "segments_count": 2,
                "confidence_score": 0.92
            },
            {
                "id": "SPEAKER_01", 
                "label": "SPEAKER_01",
                "display_name": "المتحدث الثاني",
                "total_speaking_time": 3.5,
                "segments_count": 1,
                "confidence_score": 0.94
            }
        ],
        "summary": {
            "total_duration": 12.5,
            "total_segments": 3,
            "total_speakers": 2,
            "word_count": 15,
            "average_confidence": 0.92,
            "processing_realtime_factor": 1.8
        }
    }
    
    return {
        "status": "success",
        "message": "Transcription simulation completed",
        "result": mock_result
    }


@router.get("/export/formats")
async def test_export_formats():
    """Test export format capabilities"""
    
    export_formats = {
        "txt": {
            "name": "نص عادي",
            "description": "نص عادي بدون توقيتات",
            "extension": ".txt",
            "mime_type": "text/plain",
            "supports_speakers": True,
            "supports_timestamps": False,
            "sample": "المتحدث الأول:\nالسلام عليكم ورحمة الله وبركاته\n\nالمتحدث الثاني:\nشكراً لكم على الحضور"
        },
        "srt": {
            "name": "ترجمات SRT",
            "description": "ترجمات للفيديو مع توقيتات",
            "extension": ".srt",
            "mime_type": "text/srt",
            "supports_speakers": True,
            "supports_timestamps": True,
            "sample": "1\n00:00:00,000 --> 00:00:03,500\nالمتحدث الأول: السلام عليكم ورحمة الله وبركاته\n\n2\n00:00:09,000 --> 00:00:12,500\nالمتحدث الثاني: شكراً لكم على الحضور"
        },
        "vtt": {
            "name": "ترجمات VTT",
            "description": "ترجمات الويب مع توقيتات",
            "extension": ".vtt", 
            "mime_type": "text/vtt",
            "supports_speakers": True,
            "supports_timestamps": True,
            "sample": "WEBVTT\n\n00:00:00.000 --> 00:00:03.500\n<v المتحدث الأول>السلام عليكم ورحمة الله وبركاته\n\n00:00:09.000 --> 00:00:12.500\n<v المتحدث الثاني>شكراً لكم على الحضور"
        },
        "docx": {
            "name": "مستند Word",
            "description": "مستند Word منسق مع معلومات المتحدثين",
            "extension": ".docx",
            "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "supports_speakers": True,
            "supports_timestamps": True,
            "sample": "[Word document with formatted Arabic text, speaker labels, and timestamps]"
        },
        "json": {
            "name": "JSON",
            "description": "بيانات كاملة بصيغة JSON",
            "extension": ".json",
            "mime_type": "application/json",
            "supports_speakers": True,
            "supports_timestamps": True,
            "sample": '{"segments": [{"start": 0.0, "end": 3.5, "text": "السلام عليكم", "speaker": "المتحدث الأول"}]}'
        }
    }
    
    return {
        "status": "success",
        "message": "Export formats test completed",
        "formats": export_formats,
        "total_formats": len(export_formats)
    }


@router.get("/arabic/dialects")
async def test_arabic_dialects():
    """Test Arabic dialect support information"""
    
    dialects = {
        "ar": {
            "name": "العربية الفصحى",
            "english_name": "Modern Standard Arabic",
            "code": "ar",
            "accuracy": "95%+",
            "model_optimization": "Highest priority",
            "use_cases": ["News", "Formal speeches", "Educational content"],
            "sample_text": "أعلنت الحكومة اليوم عن خطة جديدة للتنمية الاقتصادية"
        },
        "ar-IQ": {
            "name": "اللهجة العراقية", 
            "english_name": "Iraqi Arabic",
            "code": "ar-IQ",
            "accuracy": "92%+",
            "model_optimization": "Specialized optimization",
            "use_cases": ["Conversations", "Interviews", "Local media"],
            "sample_text": "شلونك اخوي، شكو ماكو اليوم؟",
            "special_features": ["Custom vocabulary", "Pronunciation variants", "Cultural context"]
        },
        "ar-EG": {
            "name": "اللهجة المصرية",
            "english_name": "Egyptian Arabic", 
            "code": "ar-EG",
            "accuracy": "90%+",
            "model_optimization": "Standard optimization",
            "use_cases": ["Media", "Entertainment", "Conversations"],
            "sample_text": "إزيك، عامل إيه النهاردة؟"
        },
        "ar-SA": {
            "name": "اللهجة السعودية",
            "english_name": "Saudi Arabic",
            "code": "ar-SA", 
            "accuracy": "91%+",
            "model_optimization": "Gulf region optimization",
            "use_cases": ["Business", "Official communications"],
            "sample_text": "كيف الحال، شفيك اليوم؟"
        },
        "ar-MA": {
            "name": "اللهجة المغربية",
            "english_name": "Moroccan Arabic",
            "code": "ar-MA",
            "accuracy": "87%+", 
            "model_optimization": "Maghrebi optimization",
            "use_cases": ["Local conversations", "Regional media"],
            "sample_text": "كيداير، أش خبار؟"
        }
    }
    
    return {
        "status": "success",
        "message": "Arabic dialects support information",
        "supported_dialects": dialects,
        "total_dialects": len(dialects),
        "primary_dialect": "ar-IQ",
        "recommendations": {
            "best_quality": "ar (MSA)",
            "iraqi_optimized": "ar-IQ", 
            "general_purpose": "ar",
            "fastest_processing": "ar with small model"
        }
    }


@router.get("/features/demo")
async def demo_features():
    """Demonstrate platform features"""
    
    features_demo = {
        "audio_processing": {
            "supported_formats": ["MP3", "WAV", "MP4", "M4A", "FLAC", "OGG"],
            "max_file_size": "500MB",
            "max_duration": "3 hours",
            "enhancement": ["Noise reduction", "Audio normalization", "Quality optimization"],
            "sample_processing_time": "~1.5x realtime for large-v3 model"
        },
        "transcription": {
            "models": ["Whisper large-v3", "Whisper medium", "Whisper small"],
            "languages": ["Arabic (all dialects)", "English", "Mixed Arabic-English"],
            "accuracy": "95%+ for clear speech",
            "features": ["Word-level timestamps", "Confidence scores", "Custom vocabulary"]
        },
        "speaker_diarization": {
            "technology": "pyannote.audio 3.1",
            "max_speakers": "10 speakers",
            "accuracy": "90%+ speaker identification",
            "features": ["Automatic speaker detection", "Custom speaker names", "Speaking time statistics"]
        },
        "editor": {
            "interface": "RTL-optimized for Arabic",
            "features": ["Waveform visualization", "Inline text editing", "Speaker labeling", "Search & replace"],
            "collaboration": ["Multi-user editing", "Version control", "Auto-save"],
            "accessibility": ["Keyboard shortcuts", "Screen reader support"]
        },
        "export": {
            "formats": ["TXT", "SRT", "VTT", "DOCX", "JSON"],
            "customization": ["Speaker labels", "Timestamp formats", "Text formatting"],
            "integration": ["Video editing software", "LMS platforms", "CRM systems"]
        },
        "api": {
            "version": "v1",
            "authentication": "JWT + API Keys",
            "rate_limiting": "1000 requests/hour",
            "webhooks": ["Job completion", "Export ready", "Error notifications"],
            "documentation": "OpenAPI 3.1 specification"
        }
    }
    
    return {
        "status": "success",
        "message": "Platform features demonstration",
        "features": features_demo,
        "live_demo_url": "${window.location.origin}",
        "documentation_url": "${window.location.origin}/docs"
    }