"""
Training API Endpoints for LLM Training Service
Provides REST API interface for training data collection and model fine-tuning
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime

from llm_training_service import LLMTrainingService, TrainingConfig
from audio_training_service import AudioEnhancedTrainingService
from speaker_adaptation_service import get_speaker_adaptation_service

# Initialize services
training_service = LLMTrainingService()
audio_training_service = AudioEnhancedTrainingService()
speaker_service = get_speaker_adaptation_service()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Arabic STT LLM Training API",
    description="API for training and fine-tuning LLM models for Arabic text processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class TranscriptionFeedbackRequest(BaseModel):
    original_text: str
    corrected_text: str
    user_id: Optional[str] = "anonymous"
    quality_score: Optional[float] = None

class DialectSampleRequest(BaseModel):
    standard_text: str
    dialect_text: str
    dialect_name: str
    quality_score: Optional[float] = None

class TrainingConfigRequest(BaseModel):
    model_name: str = "llama3.1:8b"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    learning_rate: float = 5e-4
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    max_length: int = 512

class TrainingFiltersRequest(BaseModel):
    data_type: Optional[str] = None
    dialect: Optional[str] = None
    min_quality: Optional[float] = 0.7
    limit: Optional[int] = None

class TrainingSessionRequest(BaseModel):
    config: TrainingConfigRequest
    filters: Optional[TrainingFiltersRequest] = None

# Global variable to track training status
current_training_status = {
    "is_training": False,
    "session_id": None,
    "progress": 0,
    "status": "idle"
}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Arabic STT LLM Training API",
        "version": "1.0.0",
        "endpoints": {
            "feedback": "/api/feedback/transcription",
            "dialect": "/api/data/dialect",
            "training": "/api/training/start",
            "status": "/api/training/status",
            "statistics": "/api/data/statistics"
        }
    }

@app.post("/api/feedback/transcription")
async def submit_transcription_feedback(request: TranscriptionFeedbackRequest):
    """Submit transcription correction feedback for training"""
    try:
        success = await training_service.collect_transcription_feedback(
            original_text=request.original_text,
            corrected_text=request.corrected_text,
            user_id=request.user_id,
            quality_score=request.quality_score
        )
        
        if success:
            return {
                "success": True,
                "message": "Transcription feedback collected successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to collect feedback")
            
    except Exception as e:
        logger.error(f"Error collecting transcription feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/dialect")
async def submit_dialect_sample(request: DialectSampleRequest):
    """Submit dialect adaptation sample for training"""
    try:
        success = await training_service.collect_dialect_sample(
            standard_text=request.standard_text,
            dialect_text=request.dialect_text,
            dialect_name=request.dialect_name,
            quality_score=request.quality_score
        )
        
        if success:
            return {
                "success": True,
                "message": "Dialect sample collected successfully",
                "dialect": request.dialect_name,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to collect dialect sample")
            
    except Exception as e:
        logger.error(f"Error collecting dialect sample: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/statistics")
async def get_training_statistics():
    """Get statistics about collected training data"""
    try:
        stats = training_service.get_training_statistics()
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting training statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_training_session(config: TrainingConfig, filters: Dict[str, Any] = None):
    """Background task to run training session"""
    global current_training_status
    
    try:
        current_training_status.update({
            "is_training": True,
            "status": "preparing",
            "progress": 0
        })
        
        # Convert filters if provided
        training_filters = {}
        if filters:
            if filters.get("data_type"):
                training_filters["data_type"] = TrainingDataType(filters["data_type"])
            if filters.get("dialect"):
                training_filters["dialect"] = filters["dialect"]
            if filters.get("min_quality"):
                training_filters["min_quality"] = filters["min_quality"]
            if filters.get("limit"):
                training_filters["limit"] = filters["limit"]
        
        current_training_status["status"] = "training"
        current_training_status["progress"] = 10
        
        # Start training
        results = await training_service.start_training_session(config, training_filters)
        
        if results["success"]:
            current_training_status.update({
                "is_training": False,
                "status": "completed",
                "progress": 100,
                "session_id": results["session_id"],
                "results": results
            })
        else:
            current_training_status.update({
                "is_training": False,
                "status": "failed",
                "progress": 0,
                "error": results.get("error")
            })
            
    except Exception as e:
        logger.error(f"Training session failed: {e}")
        current_training_status.update({
            "is_training": False,
            "status": "failed",
            "progress": 0,
            "error": str(e)
        })

@app.post("/api/training/start")
async def start_training(request: TrainingSessionRequest, background_tasks: BackgroundTasks):
    """Start a new training session"""
    global current_training_status
    
    if current_training_status["is_training"]:
        raise HTTPException(
            status_code=409, 
            detail="Training session already in progress"
        )
    
    try:
        # Convert request to TrainingConfig
        config = TrainingConfig(
            model_name=request.config.model_name,
            num_train_epochs=request.config.num_train_epochs,
            per_device_train_batch_size=request.config.per_device_train_batch_size,
            learning_rate=request.config.learning_rate,
            lora_r=request.config.lora_r,
            lora_alpha=request.config.lora_alpha,
            lora_dropout=request.config.lora_dropout,
            max_length=request.config.max_length,
            output_dir=f"./trained_models/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Start training in background
        background_tasks.add_task(
            run_training_session, 
            config, 
            request.filters.model_dump() if request.filters else None
        )
        
        return {
            "success": True,
            "message": "Training session started",
            "config": request.config.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting training: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/training/status")
async def get_training_status():
    """Get current training session status"""
    return {
        "success": True,
        "status": current_training_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/training/stop")
async def stop_training():
    """Stop current training session"""
    global current_training_status
    
    if not current_training_status["is_training"]:
        raise HTTPException(status_code=400, detail="No training session in progress")
    
    # Note: In a real implementation, you'd need to properly cancel the training task
    current_training_status.update({
        "is_training": False,
        "status": "stopped",
        "progress": 0
    })
    
    return {
        "success": True,
        "message": "Training session stopped",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/models/available")
async def get_available_models():
    """Get list of available models for training"""
    return {
        "success": True,
        "models": [
            {
                "name": "llama3.1:8b",
                "description": "Llama 3.1 8B - Fast training, good for experimentation",
                "recommended_batch_size": 4,
                "memory_requirement": "16GB VRAM"
            },
            {
                "name": "llama3.1:70b-instruct-q4_K_M",
                "description": "Llama 3.1 70B Quantized - High quality, slower training",
                "recommended_batch_size": 1,
                "memory_requirement": "24GB VRAM"
            },
            {
                "name": "aya:35b-23-q4_K_M",
                "description": "Aya 35B - Specialized for multilingual including Arabic",
                "recommended_batch_size": 2,
                "memory_requirement": "20GB VRAM"
            }
        ]
    }

# New Audio Training Endpoints

class AudioTrainingRequest(BaseModel):
    audio_file_path: str
    transcript_text: str
    corrected_text: Optional[str] = None
    confidence_score: Optional[float] = 0.0
    speaker_id: Optional[str] = None
    dialect: str = "standard"

class ProcessResultsRequest(BaseModel):
    results_directory: Optional[str] = "."
    auto_process: Optional[bool] = True

@app.post("/api/audio/training/add")
async def add_audio_training_sample(request: AudioTrainingRequest):
    """Add audio training sample with automatic feature extraction"""
    try:
        from audio_training_service import AudioTrainingDataPoint
        
        data_point = AudioTrainingDataPoint(
            audio_file_path=request.audio_file_path,
            transcript_text=request.transcript_text,
            corrected_text=request.corrected_text,
            confidence_score=request.confidence_score,
            speaker_id=request.speaker_id,
            dialect=request.dialect
        )
        
        success = audio_training_service.audio_data_manager.add_audio_training_sample(data_point)
        
        if success:
            return {
                "success": True,
                "message": "Audio training sample added successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add audio training sample")
            
    except Exception as e:
        logger.error(f"Error adding audio training sample: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio/training/process-results")
async def process_multimodal_results(request: ProcessResultsRequest):
    """Process multimodal analysis results for automatic training data collection"""
    try:
        feedback_count = audio_training_service.create_feedback_from_multimodal_results(
            results_dir=request.results_directory
        )
        
        return {
            "success": True,
            "message": f"Processed {feedback_count} multimodal results",
            "feedback_count": feedback_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing multimodal results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/training/statistics")
async def get_audio_training_statistics():
    """Get comprehensive audio training statistics"""
    try:
        stats = audio_training_service.get_audio_training_statistics()
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting audio training statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio/training/continuous-learning/start")
async def start_continuous_learning():
    """Start continuous learning process"""
    try:
        result = audio_training_service.start_continuous_learning()
        return {
            "success": True,
            "message": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting continuous learning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/types")
async def get_data_types():
    """Get available training data types"""
    return {
        "success": True,
        "data_types": [
            {
                "value": "transcription_correction",
                "label": "Transcription Correction",
                "description": "Corrections to transcribed text"
            },
            {
                "value": "grammar_enhancement",
                "label": "Grammar Enhancement",
                "description": "Grammar and language improvements"
            },
            {
                "value": "dialect_adaptation",
                "label": "Dialect Adaptation",
                "description": "Adaptation between dialects and standard Arabic"
            },
            {
                "value": "speaker_adaptation",
                "label": "Speaker Adaptation",
                "description": "Personalized training for individual speakers"
            },
            {
                "value": "audio_quality_assessment",
                "label": "Audio Quality Assessment",
                "description": "Training for better audio quality scoring"
            }
        ]
    }

# Speaker Adaptation Endpoints
@app.post("/api/speaker/training/add")
async def add_speaker_training_data(request: dict):
    """Add speaker-specific training data"""
    try:
        required_fields = ['audio_features', 'transcription']
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        speaker_id = speaker_service.add_speaker_training_data(
            audio_features=request['audio_features'],
            transcription=request['transcription'],
            corrected_transcription=request.get('corrected_transcription'),
            confidence_score=request.get('confidence_score', 0.0),
            dialect=request.get('dialect', 'unknown'),
            session_id=request.get('session_id', 'default')
        )
        
        return {
            "success": True,
            "speaker_id": speaker_id,
            "message": "Speaker training data added successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error adding speaker training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speaker/recommendations/{speaker_id}")
async def get_speaker_recommendations(speaker_id: str):
    """Get personalized recommendations for a speaker"""
    try:
        recommendations = speaker_service.get_speaker_adaptation_recommendations(speaker_id)
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="Speaker not found")
        
        return {
            "success": True,
            "speaker_id": speaker_id,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting speaker recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speaker/statistics")
async def get_speaker_statistics():
    """Get comprehensive speaker adaptation statistics"""
    try:
        stats = speaker_service.get_speaker_statistics()
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting speaker statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speaker/profiles")
async def get_all_speaker_profiles():
    """Get all speaker profiles summary"""
    try:
        profiles = speaker_service.speaker_service.get_all_speaker_profiles()
        
        # Convert to summary format
        profiles_summary = {}
        for speaker_id, profile in profiles.items():
            profiles_summary[speaker_id] = {
                "speaker_id": speaker_id,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat(),
                "adaptation_sessions": len(profile.adaptation_history),
                "preferred_dialect": max(profile.dialect_preferences.items(), 
                                       key=lambda x: x[1])[0] if profile.dialect_preferences else None,
                "average_quality": profile.quality_metrics.get('average_quality', 0.0),
                "voice_characteristics": profile.voice_characteristics
            }
        
        return {
            "success": True,
            "profiles": profiles_summary,
            "total_speakers": len(profiles_summary),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting speaker profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)