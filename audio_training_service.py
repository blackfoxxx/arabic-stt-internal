"""
Audio-Based Training Service
Integrates audio processing with LLM training for enhanced Arabic STT system
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import librosa
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import whisper

from llm_training_service import (
    LLMTrainingService, 
    TrainingDataType, 
    TrainingDataPoint,
    TrainingDataManager
)

@dataclass
class AudioTrainingDataPoint:
    """Enhanced training data point that includes audio features"""
    audio_file_path: str
    transcript_text: str
    corrected_text: Optional[str] = None
    confidence_score: float = 0.0
    speaker_id: Optional[str] = None
    dialect: str = "standard"
    audio_duration: float = 0.0
    audio_quality_score: float = 0.0
    noise_level: float = 0.0
    speech_rate: float = 0.0
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class AudioFeatureExtractor:
    """Extract audio features for training enhancement"""
    
    def __init__(self):
        self.sample_rate = 16000
        
    def extract_features(self, audio_path: str) -> Dict[str, float]:
        """Extract comprehensive audio features"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Basic features
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Audio quality metrics
            rms_energy = np.sqrt(np.mean(y**2))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            
            # Speech rate estimation (rough approximation)
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            speech_rate = len(onset_frames) / duration if duration > 0 else 0
            
            # Noise estimation
            noise_level = self._estimate_noise_level(y)
            
            return {
                'duration': duration,
                'rms_energy': float(rms_energy),
                'zero_crossing_rate': float(np.mean(zero_crossing_rate)),
                'spectral_centroid': float(np.mean(spectral_centroids)),
                'spectral_rolloff': float(np.mean(spectral_rolloff)),
                'speech_rate': speech_rate,
                'noise_level': noise_level,
                'audio_quality_score': self._calculate_quality_score(rms_energy, noise_level, zero_crossing_rate)
            }
            
        except Exception as e:
            print(f"Error extracting features from {audio_path}: {e}")
            return {
                'duration': 0.0,
                'rms_energy': 0.0,
                'zero_crossing_rate': 0.0,
                'spectral_centroid': 0.0,
                'spectral_rolloff': 0.0,
                'speech_rate': 0.0,
                'noise_level': 1.0,
                'audio_quality_score': 0.0
            }
    
    def _estimate_noise_level(self, y: np.ndarray) -> float:
        """Estimate noise level in audio signal"""
        # Simple noise estimation using energy in silent regions
        frame_length = 2048
        hop_length = 512
        
        # Calculate RMS energy for each frame
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Assume bottom 20% of energy frames are noise
        noise_threshold = np.percentile(rms, 20)
        noise_level = noise_threshold / (np.max(rms) + 1e-8)
        
        return float(noise_level)
    
    def _calculate_quality_score(self, rms_energy: float, noise_level: float, zcr: float) -> float:
        """Calculate overall audio quality score"""
        # Normalize and combine metrics
        energy_score = min(rms_energy * 10, 1.0)  # Higher energy = better
        noise_score = 1.0 - noise_level  # Lower noise = better
        clarity_score = 1.0 - min(zcr * 2, 1.0)  # Lower ZCR = clearer speech
        
        # Weighted combination
        quality_score = (energy_score * 0.4 + noise_score * 0.4 + clarity_score * 0.2)
        return float(np.clip(quality_score, 0.0, 1.0))

class AudioTrainingDataManager:
    """Manage audio training data with enhanced features"""
    
    def __init__(self, db_path: str = "audio_training_data.db"):
        self.db_path = db_path
        self.feature_extractor = AudioFeatureExtractor()
        self._init_database()
    
    def _init_database(self):
        """Initialize the audio training database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audio_training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audio_file_path TEXT NOT NULL,
                transcript_text TEXT NOT NULL,
                corrected_text TEXT,
                confidence_score REAL DEFAULT 0.0,
                speaker_id TEXT,
                dialect TEXT DEFAULT 'standard',
                audio_duration REAL DEFAULT 0.0,
                audio_quality_score REAL DEFAULT 0.0,
                noise_level REAL DEFAULT 0.0,
                speech_rate REAL DEFAULT 0.0,
                rms_energy REAL DEFAULT 0.0,
                spectral_centroid REAL DEFAULT 0.0,
                spectral_rolloff REAL DEFAULT 0.0,
                zero_crossing_rate REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_audio_training_sample(self, data_point: AudioTrainingDataPoint) -> bool:
        """Add audio training sample with feature extraction"""
        try:
            # Extract audio features
            features = self.feature_extractor.extract_features(data_point.audio_file_path)
            
            # Update data point with extracted features
            data_point.audio_duration = features['duration']
            data_point.audio_quality_score = features['audio_quality_score']
            data_point.noise_level = features['noise_level']
            data_point.speech_rate = features['speech_rate']
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audio_training_data (
                    audio_file_path, transcript_text, corrected_text, confidence_score,
                    speaker_id, dialect, audio_duration, audio_quality_score, noise_level,
                    speech_rate, rms_energy, spectral_centroid, spectral_rolloff,
                    zero_crossing_rate, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data_point.audio_file_path,
                data_point.transcript_text,
                data_point.corrected_text,
                data_point.confidence_score,
                data_point.speaker_id,
                data_point.dialect,
                data_point.audio_duration,
                data_point.audio_quality_score,
                data_point.noise_level,
                data_point.speech_rate,
                features['rms_energy'],
                features['spectral_centroid'],
                features['spectral_rolloff'],
                features['zero_crossing_rate'],
                data_point.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding audio training sample: {e}")
            return False
    
    def get_training_samples(self, filters: Dict[str, Any] = None) -> List[AudioTrainingDataPoint]:
        """Retrieve audio training samples with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM audio_training_data WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('dialect'):
                query += " AND dialect = ?"
                params.append(filters['dialect'])
            
            if filters.get('min_quality'):
                query += " AND audio_quality_score >= ?"
                params.append(filters['min_quality'])
            
            if filters.get('min_confidence'):
                query += " AND confidence_score >= ?"
                params.append(filters['min_confidence'])
            
            if filters.get('speaker_id'):
                query += " AND speaker_id = ?"
                params.append(filters['speaker_id'])
        
        query += " ORDER BY created_at DESC"
        
        if filters and filters.get('limit'):
            query += " LIMIT ?"
            params.append(filters['limit'])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        samples = []
        for row in rows:
            samples.append(AudioTrainingDataPoint(
                audio_file_path=row[1],
                transcript_text=row[2],
                corrected_text=row[3],
                confidence_score=row[4],
                speaker_id=row[5],
                dialect=row[6],
                audio_duration=row[7],
                audio_quality_score=row[8],
                noise_level=row[9],
                speech_rate=row[10],
                created_at=row[15]
            ))
        
        return samples

class AudioEnhancedTrainingService:
    """Enhanced training service that integrates audio analysis with LLM training"""
    
    def __init__(self):
        self.llm_service = LLMTrainingService()
        self.audio_data_manager = AudioTrainingDataManager()
        self.llm_data_manager = TrainingDataManager()
    
    def process_transcription_result(self, result_file: str) -> bool:
        """Process transcription results and extract training data"""
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            # Extract relevant information
            audio_file = result_data.get('audio_file', '')
            transcript = result_data.get('transcript', {})
            
            if not audio_file or not transcript:
                return False
            
            # Create audio training data point
            audio_data_point = AudioTrainingDataPoint(
                audio_file_path=audio_file,
                transcript_text=transcript.get('text', ''),
                confidence_score=transcript.get('confidence', 0.0),
                speaker_id=transcript.get('speaker_id'),
                dialect=result_data.get('detected_dialect', 'standard')
            )
            
            # Add to audio training database
            success = self.audio_data_manager.add_audio_training_sample(audio_data_point)
            
            # Also add to LLM training if we have quality metrics
            if success and audio_data_point.confidence_score > 0.7:
                llm_data_point = TrainingDataPoint(
                    data_type=TrainingDataType.QUALITY_ASSESSMENT,
                    input_text=audio_data_point.transcript_text,
                    target_text=f"Confidence: {audio_data_point.confidence_score:.2f}",
                    quality_score=audio_data_point.audio_quality_score,
                    dialect=audio_data_point.dialect
                )
                self.llm_data_manager.add_training_data(llm_data_point)
            
            return success
            
        except Exception as e:
            print(f"Error processing transcription result: {e}")
            return False
    
    def create_feedback_from_multimodal_results(self, results_dir: str = ".") -> int:
        """Automatically create training feedback from multimodal analysis results"""
        feedback_count = 0
        
        try:
            # Find all multimodal result files
            for file_path in Path(results_dir).glob("multimodal_analysis_results_*.json"):
                if self.process_transcription_result(str(file_path)):
                    feedback_count += 1
            
            return feedback_count
            
        except Exception as e:
            print(f"Error creating feedback from multimodal results: {e}")
            return 0
    
    def get_audio_training_statistics(self) -> Dict[str, Any]:
        """Get comprehensive training statistics including audio metrics"""
        conn = sqlite3.connect(self.audio_data_manager.db_path)
        cursor = conn.cursor()
        
        # Basic statistics
        cursor.execute("SELECT COUNT(*) FROM audio_training_data")
        total_samples = cursor.fetchone()[0]
        
        # Quality distribution
        cursor.execute("""
            SELECT 
                AVG(audio_quality_score) as avg_quality,
                AVG(confidence_score) as avg_confidence,
                AVG(audio_duration) as avg_duration,
                COUNT(DISTINCT speaker_id) as unique_speakers,
                COUNT(DISTINCT dialect) as unique_dialects
            FROM audio_training_data
        """)
        
        stats = cursor.fetchone()
        
        # Dialect distribution
        cursor.execute("SELECT dialect, COUNT(*) FROM audio_training_data GROUP BY dialect")
        dialect_dist = dict(cursor.fetchall())
        
        # Quality ranges
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN audio_quality_score >= 0.8 THEN 1 ELSE 0 END) as high_quality,
                SUM(CASE WHEN audio_quality_score >= 0.6 AND audio_quality_score < 0.8 THEN 1 ELSE 0 END) as medium_quality,
                SUM(CASE WHEN audio_quality_score < 0.6 THEN 1 ELSE 0 END) as low_quality
            FROM audio_training_data
        """)
        
        quality_dist = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_audio_samples': total_samples,
            'average_quality_score': float(stats[0] or 0),
            'average_confidence_score': float(stats[1] or 0),
            'average_duration': float(stats[2] or 0),
            'unique_speakers': int(stats[3] or 0),
            'unique_dialects': int(stats[4] or 0),
            'dialect_distribution': dialect_dist,
            'quality_distribution': {
                'high': int(quality_dist[0] or 0),
                'medium': int(quality_dist[1] or 0),
                'low': int(quality_dist[2] or 0)
            }
        }
    
    def start_continuous_learning(self, auto_process_interval: int = 3600) -> str:
        """Start continuous learning process that automatically processes new results"""
        # This would be implemented as a background service
        # For now, we'll create a method that can be called periodically
        
        feedback_count = self.create_feedback_from_multimodal_results()
        
        if feedback_count > 10:  # Only train if we have enough new samples
            # Start training with the new data
            training_session = self.llm_service.start_training_session(
                filters={'min_quality': 0.7, 'limit': 1000}
            )
            return f"Started continuous learning session: {training_session}"
        
        return f"Processed {feedback_count} new samples, not enough for training yet"