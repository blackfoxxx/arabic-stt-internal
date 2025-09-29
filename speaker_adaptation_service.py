"""
Speaker-Specific Adaptation Training Service

This module implements speaker-specific adaptation training to personalize
the Arabic STT system for individual speakers based on their voice characteristics,
speaking patterns, and dialect preferences.
"""

import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from collections import defaultdict, Counter
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SpeakerProfile:
    """Speaker profile containing voice characteristics and preferences."""
    speaker_id: str
    voice_characteristics: Dict[str, float]  # pitch, tempo, formants, etc.
    dialect_preferences: Dict[str, float]    # dialect confidence scores
    speaking_patterns: Dict[str, Any]        # common phrases, vocabulary
    adaptation_history: List[Dict[str, Any]] # training sessions
    quality_metrics: Dict[str, float]        # accuracy, confidence trends
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpeakerProfile':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

@dataclass
class SpeakerAdaptationData:
    """Training data point for speaker adaptation."""
    speaker_id: str
    audio_features: Dict[str, float]
    transcription: str
    corrected_transcription: Optional[str]
    confidence_score: float
    dialect: str
    session_id: str
    timestamp: datetime
    quality_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class SpeakerIdentificationService:
    """Service for identifying and tracking speakers."""
    
    def __init__(self, db_path: str = "speaker_profiles.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the speaker profiles database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Speaker profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS speaker_profiles (
                speaker_id TEXT PRIMARY KEY,
                profile_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Speaker adaptation data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS speaker_adaptation_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                speaker_id TEXT NOT NULL,
                audio_features TEXT NOT NULL,
                transcription TEXT NOT NULL,
                corrected_transcription TEXT,
                confidence_score REAL NOT NULL,
                dialect TEXT NOT NULL,
                session_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quality_score REAL NOT NULL,
                FOREIGN KEY (speaker_id) REFERENCES speaker_profiles (speaker_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def identify_speaker(self, audio_features: Dict[str, float]) -> str:
        """
        Identify speaker based on audio features.
        Returns existing speaker_id or creates new one.
        """
        # Extract key voice characteristics for identification
        voice_signature = {
            'pitch_mean': audio_features.get('pitch_mean', 0),
            'pitch_std': audio_features.get('pitch_std', 0),
            'formant_f1': audio_features.get('formant_f1', 0),
            'formant_f2': audio_features.get('formant_f2', 0),
            'speaking_rate': audio_features.get('speaking_rate', 0)
        }
        
        # Get all existing speaker profiles
        existing_profiles = self.get_all_speaker_profiles()
        
        # Find best match based on voice characteristics similarity
        best_match_id = None
        best_similarity = 0.0
        similarity_threshold = 0.85  # Threshold for considering speakers the same
        
        for speaker_id, profile in existing_profiles.items():
            similarity = self._calculate_voice_similarity(
                voice_signature, 
                profile.voice_characteristics
            )
            
            if similarity > best_similarity and similarity > similarity_threshold:
                best_similarity = similarity
                best_match_id = speaker_id
        
        if best_match_id:
            logger.info(f"Identified existing speaker: {best_match_id} (similarity: {best_similarity:.3f})")
            return best_match_id
        else:
            # Create new speaker profile
            new_speaker_id = self._generate_speaker_id(voice_signature)
            self._create_new_speaker_profile(new_speaker_id, voice_signature)
            logger.info(f"Created new speaker profile: {new_speaker_id}")
            return new_speaker_id
    
    def _calculate_voice_similarity(self, features1: Dict[str, float], features2: Dict[str, float]) -> float:
        """Calculate similarity between two voice characteristic sets."""
        if not features1 or not features2:
            return 0.0
        
        # Normalize and compare key features
        similarities = []
        
        for key in ['pitch_mean', 'pitch_std', 'formant_f1', 'formant_f2', 'speaking_rate']:
            if key in features1 and key in features2:
                val1, val2 = features1[key], features2[key]
                if val1 == 0 and val2 == 0:
                    similarities.append(1.0)
                elif val1 == 0 or val2 == 0:
                    similarities.append(0.0)
                else:
                    # Calculate normalized similarity (closer to 1 = more similar)
                    diff = abs(val1 - val2) / max(abs(val1), abs(val2))
                    similarity = max(0, 1 - diff)
                    similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _generate_speaker_id(self, voice_signature: Dict[str, float]) -> str:
        """Generate unique speaker ID based on voice characteristics."""
        # Create hash from voice characteristics
        signature_str = json.dumps(voice_signature, sort_keys=True)
        hash_obj = hashlib.md5(signature_str.encode())
        return f"speaker_{hash_obj.hexdigest()[:8]}"
    
    def _create_new_speaker_profile(self, speaker_id: str, voice_characteristics: Dict[str, float]):
        """Create a new speaker profile."""
        now = datetime.now()
        profile = SpeakerProfile(
            speaker_id=speaker_id,
            voice_characteristics=voice_characteristics,
            dialect_preferences={},
            speaking_patterns={},
            adaptation_history=[],
            quality_metrics={},
            created_at=now,
            updated_at=now
        )
        
        self.save_speaker_profile(profile)
    
    def get_speaker_profile(self, speaker_id: str) -> Optional[SpeakerProfile]:
        """Get speaker profile by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT profile_data FROM speaker_profiles WHERE speaker_id = ?', (speaker_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            profile_data = json.loads(result[0])
            return SpeakerProfile.from_dict(profile_data)
        return None
    
    def get_all_speaker_profiles(self) -> Dict[str, SpeakerProfile]:
        """Get all speaker profiles."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT speaker_id, profile_data FROM speaker_profiles')
        results = cursor.fetchall()
        conn.close()
        
        profiles = {}
        for speaker_id, profile_data in results:
            try:
                profile = SpeakerProfile.from_dict(json.loads(profile_data))
                profiles[speaker_id] = profile
            except Exception as e:
                logger.error(f"Error loading profile for {speaker_id}: {e}")
        
        return profiles
    
    def save_speaker_profile(self, profile: SpeakerProfile):
        """Save or update speaker profile."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        profile.updated_at = datetime.now()
        profile_json = json.dumps(profile.to_dict())
        
        cursor.execute('''
            INSERT OR REPLACE INTO speaker_profiles (speaker_id, profile_data, updated_at)
            VALUES (?, ?, ?)
        ''', (profile.speaker_id, profile_json, profile.updated_at))
        
        conn.commit()
        conn.close()

class SpeakerAdaptationTrainingService:
    """Service for speaker-specific adaptation training."""
    
    def __init__(self, db_path: str = "speaker_profiles.db"):
        self.speaker_service = SpeakerIdentificationService(db_path)
        self.db_path = db_path
    
    def add_speaker_training_data(self, 
                                audio_features: Dict[str, float],
                                transcription: str,
                                corrected_transcription: Optional[str] = None,
                                confidence_score: float = 0.0,
                                dialect: str = "unknown",
                                session_id: str = "default") -> str:
        """Add training data for speaker adaptation."""
        
        # Identify speaker
        speaker_id = self.speaker_service.identify_speaker(audio_features)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            transcription, corrected_transcription, confidence_score
        )
        
        # Create adaptation data point
        adaptation_data = SpeakerAdaptationData(
            speaker_id=speaker_id,
            audio_features=audio_features,
            transcription=transcription,
            corrected_transcription=corrected_transcription,
            confidence_score=confidence_score,
            dialect=dialect,
            session_id=session_id,
            timestamp=datetime.now(),
            quality_score=quality_score
        )
        
        # Store in database
        self._store_adaptation_data(adaptation_data)
        
        # Update speaker profile
        self._update_speaker_profile(speaker_id, adaptation_data)
        
        logger.info(f"Added training data for speaker {speaker_id}")
        return speaker_id
    
    def _calculate_quality_score(self, 
                                original: str, 
                                corrected: Optional[str], 
                                confidence: float) -> float:
        """Calculate quality score for the training sample."""
        if not corrected:
            return confidence
        
        # Calculate similarity between original and corrected
        if original == corrected:
            return 1.0
        
        # Simple character-level similarity
        original_chars = set(original.lower())
        corrected_chars = set(corrected.lower())
        
        if not original_chars and not corrected_chars:
            return 1.0
        
        intersection = len(original_chars.intersection(corrected_chars))
        union = len(original_chars.union(corrected_chars))
        
        similarity = intersection / union if union > 0 else 0.0
        
        # Combine with confidence score
        return (similarity + confidence) / 2.0
    
    def _store_adaptation_data(self, data: SpeakerAdaptationData):
        """Store adaptation data in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO speaker_adaptation_data 
            (speaker_id, audio_features, transcription, corrected_transcription, 
             confidence_score, dialect, session_id, timestamp, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.speaker_id,
            json.dumps(data.audio_features),
            data.transcription,
            data.corrected_transcription,
            data.confidence_score,
            data.dialect,
            data.session_id,
            data.timestamp,
            data.quality_score
        ))
        
        conn.commit()
        conn.close()
    
    def _update_speaker_profile(self, speaker_id: str, data: SpeakerAdaptationData):
        """Update speaker profile with new training data."""
        profile = self.speaker_service.get_speaker_profile(speaker_id)
        if not profile:
            return
        
        # Update dialect preferences
        if data.dialect not in profile.dialect_preferences:
            profile.dialect_preferences[data.dialect] = 0.0
        
        # Weighted update based on quality score
        current_pref = profile.dialect_preferences[data.dialect]
        profile.dialect_preferences[data.dialect] = (
            current_pref * 0.9 + data.quality_score * 0.1
        )
        
        # Update speaking patterns (extract common words/phrases)
        words = data.transcription.lower().split()
        if 'common_words' not in profile.speaking_patterns:
            profile.speaking_patterns['common_words'] = {}
        
        for word in words:
            if word not in profile.speaking_patterns['common_words']:
                profile.speaking_patterns['common_words'][word] = 0
            profile.speaking_patterns['common_words'][word] += 1
        
        # Update quality metrics
        if 'average_quality' not in profile.quality_metrics:
            profile.quality_metrics['average_quality'] = data.quality_score
        else:
            current_avg = profile.quality_metrics['average_quality']
            profile.quality_metrics['average_quality'] = (
                current_avg * 0.95 + data.quality_score * 0.05
            )
        
        # Add to adaptation history
        profile.adaptation_history.append({
            'timestamp': data.timestamp.isoformat(),
            'quality_score': data.quality_score,
            'dialect': data.dialect,
            'session_id': data.session_id
        })
        
        # Keep only recent history (last 100 entries)
        if len(profile.adaptation_history) > 100:
            profile.adaptation_history = profile.adaptation_history[-100:]
        
        # Save updated profile
        self.speaker_service.save_speaker_profile(profile)
    
    def get_speaker_adaptation_recommendations(self, speaker_id: str) -> Dict[str, Any]:
        """Get personalized recommendations for a speaker."""
        profile = self.speaker_service.get_speaker_profile(speaker_id)
        if not profile:
            return {}
        
        recommendations = {
            'preferred_dialect': max(profile.dialect_preferences.items(), 
                                   key=lambda x: x[1])[0] if profile.dialect_preferences else None,
            'confidence_threshold': profile.quality_metrics.get('average_quality', 0.5),
            'common_vocabulary': list(profile.speaking_patterns.get('common_words', {}).keys())[:20],
            'adaptation_sessions': len(profile.adaptation_history),
            'voice_characteristics': profile.voice_characteristics
        }
        
        return recommendations
    
    def get_speaker_statistics(self) -> Dict[str, Any]:
        """Get comprehensive speaker adaptation statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic counts
        cursor.execute('SELECT COUNT(DISTINCT speaker_id) FROM speaker_profiles')
        total_speakers = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM speaker_adaptation_data')
        total_adaptations = cursor.fetchone()[0]
        
        # Get quality distribution
        cursor.execute('''
            SELECT 
                AVG(quality_score) as avg_quality,
                COUNT(CASE WHEN quality_score >= 0.8 THEN 1 END) as high_quality,
                COUNT(CASE WHEN quality_score >= 0.6 AND quality_score < 0.8 THEN 1 END) as medium_quality,
                COUNT(CASE WHEN quality_score < 0.6 THEN 1 END) as low_quality
            FROM speaker_adaptation_data
        ''')
        quality_stats = cursor.fetchone()
        
        # Get dialect distribution
        cursor.execute('''
            SELECT dialect, COUNT(*) as count 
            FROM speaker_adaptation_data 
            GROUP BY dialect 
            ORDER BY count DESC
        ''')
        dialect_distribution = dict(cursor.fetchall())
        
        # Get recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        cursor.execute('''
            SELECT COUNT(*) FROM speaker_adaptation_data 
            WHERE timestamp > ?
        ''', (week_ago,))
        recent_activity = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_speakers': total_speakers,
            'total_adaptations': total_adaptations,
            'average_quality': quality_stats[0] if quality_stats[0] else 0.0,
            'quality_distribution': {
                'high': quality_stats[1] or 0,
                'medium': quality_stats[2] or 0,
                'low': quality_stats[3] or 0
            },
            'dialect_distribution': dialect_distribution,
            'recent_activity': recent_activity,
            'speakers_with_multiple_sessions': self._count_active_speakers()
        }
    
    def _count_active_speakers(self) -> int:
        """Count speakers with multiple adaptation sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM (
                SELECT speaker_id FROM speaker_adaptation_data 
                GROUP BY speaker_id 
                HAVING COUNT(*) > 1
            )
        ''')
        
        result = cursor.fetchone()[0]
        conn.close()
        return result

# Service instance
_speaker_adaptation_service = None

def get_speaker_adaptation_service() -> SpeakerAdaptationTrainingService:
    """Get or create the speaker adaptation service instance."""
    global _speaker_adaptation_service
    if _speaker_adaptation_service is None:
        _speaker_adaptation_service = SpeakerAdaptationTrainingService()
    return _speaker_adaptation_service