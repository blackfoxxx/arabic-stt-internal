"""
Speaker diarization processing using pyannote.audio
"""

import os
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import torch
import structlog
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from pyannote.core import Annotation, Segment

logger = structlog.get_logger(__name__)


@dataclass
class Speaker:
    """Speaker information"""
    id: str
    label: str
    display_name: Optional[str] = None
    total_speaking_time: float = 0.0
    segments_count: int = 0
    confidence_score: float = 0.0


@dataclass
class SpeakerTurn:
    """Speaker turn with timing"""
    start: float
    end: float
    speaker: str
    confidence: float = 0.0


@dataclass
class DiarizationResult:
    """Complete diarization result"""
    speakers: List[Speaker]
    turns: List[SpeakerTurn]
    processing_time: float
    total_speakers: int
    total_speech_time: float


class DiarizationProcessor:
    """Speaker diarization processor using pyannote.audio"""
    
    def __init__(self, model_name: str = "pyannote/speaker-diarization-3.1"):
        self.model_name = model_name
        self.pipeline: Optional[Pipeline] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Arabic-specific diarization parameters
        self.arabic_config = {
            "segmentation": {
                "threshold": 0.4424,  # Optimized for Arabic speech patterns
                "min_duration_on": 0.2,   # Minimum speech duration
                "min_duration_off": 0.1   # Minimum silence duration
            },
            "clustering": {
                "method": "centroid",
                "min_cluster_size": 12,    # Minimum samples per speaker
                "threshold": 0.7,          # Clustering threshold
            }
        }
        
        logger.info("Diarization processor initialized", 
                   model=model_name, device=self.device)
    
    def _load_pipeline(self):
        """Load diarization pipeline"""
        if self.pipeline is None:
            try:
                logger.info("Loading diarization pipeline", model=self.model_name)
                
                # Check for HuggingFace token
                hf_token = os.getenv("HUGGINGFACE_TOKEN")
                if not hf_token:
                    logger.warning("No HuggingFace token provided - using public models only")
                
                self.pipeline = Pipeline.from_pretrained(
                    self.model_name,
                    use_auth_token=hf_token
                )
                
                # Configure for Arabic speech
                self.pipeline.instantiate(self.arabic_config)
                
                # Move to appropriate device
                if self.device == "cuda" and torch.cuda.is_available():
                    self.pipeline.to(torch.device("cuda"))
                
                logger.info("Diarization pipeline loaded successfully")
                
            except Exception as e:
                logger.error("Failed to load diarization pipeline", error=str(e))
                raise
    
    def diarize(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
        min_speakers: int = 1,
        max_speakers: int = 10
    ) -> Optional[DiarizationResult]:
        """
        Perform speaker diarization on audio file
        
        Args:
            audio_path: Path to audio file
            num_speakers: Expected number of speakers (optional)
            min_speakers: Minimum number of speakers
            max_speakers: Maximum number of speakers
        
        Returns:
            DiarizationResult with speaker information
        """
        
        start_time = time.time()
        
        try:
            # Load pipeline if not already loaded
            self._load_pipeline()
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            logger.info("Starting speaker diarization", 
                       audio_path=audio_path, 
                       num_speakers=num_speakers,
                       model=self.model_name)
            
            # Configure pipeline for specific number of speakers
            if num_speakers:
                # Fixed number of speakers
                self.pipeline.instantiate({
                    **self.arabic_config,
                    "clustering": {
                        **self.arabic_config["clustering"],
                        "num_clusters": num_speakers
                    }
                })
            else:
                # Auto-detect number of speakers
                self.pipeline.instantiate({
                    **self.arabic_config,
                    "clustering": {
                        **self.arabic_config["clustering"],
                        "min_clusters": min_speakers,
                        "max_clusters": max_speakers
                    }
                })
            
            # Run diarization with progress tracking
            with ProgressHook() as hook:
                diarization: Annotation = self.pipeline(audio_path, hook=hook)
            
            # Process results
            speakers_data = {}
            speaker_turns = []
            
            # Extract speaker information
            for segment, _, speaker_label in diarization.itertracks(yield_label=True):
                speaker_id = speaker_label
                duration = segment.end - segment.start
                
                # Initialize speaker data if not exists
                if speaker_id not in speakers_data:
                    speakers_data[speaker_id] = {
                        "total_time": 0.0,
                        "segments": 0,
                        "confidences": []
                    }
                
                # Update speaker statistics
                speakers_data[speaker_id]["total_time"] += duration
                speakers_data[speaker_id]["segments"] += 1
                
                # Create speaker turn
                speaker_turn = SpeakerTurn(
                    start=segment.start,
                    end=segment.end,
                    speaker=speaker_id,
                    confidence=0.8  # Default confidence (pyannote doesn't provide per-segment confidence)
                )
                speaker_turns.append(speaker_turn)
                speakers_data[speaker_id]["confidences"].append(0.8)
            
            # Create speaker objects
            speakers = []
            for speaker_id, data in speakers_data.items():
                avg_confidence = (
                    sum(data["confidences"]) / len(data["confidences"])
                    if data["confidences"] else 0.0
                )
                
                speaker = Speaker(
                    id=speaker_id,
                    label=speaker_id,
                    display_name=f"متحدث {speaker_id.split('_')[-1]}",
                    total_speaking_time=data["total_time"],
                    segments_count=data["segments"],
                    confidence_score=avg_confidence
                )
                speakers.append(speaker)
            
            # Calculate total speech time
            total_speech_time = sum(turn.end - turn.start for turn in speaker_turns)
            
            processing_time = time.time() - start_time
            
            result = DiarizationResult(
                speakers=speakers,
                turns=speaker_turns,
                processing_time=processing_time,
                total_speakers=len(speakers),
                total_speech_time=total_speech_time
            )
            
            logger.info("Diarization completed successfully",
                       speakers_found=len(speakers),
                       turns_count=len(speaker_turns),
                       processing_time=processing_time,
                       total_speech_time=total_speech_time)
            
            return result
            
        except Exception as e:
            logger.error("Diarization failed", 
                        audio_path=audio_path, model=self.model_name, error=str(e))
            return None
    
    def optimize_for_arabic_patterns(self, audio_path: str) -> Dict[str, Any]:
        """Optimize diarization parameters for Arabic speech patterns"""
        
        try:
            # Analyze audio characteristics
            import librosa
            
            y, sr = librosa.load(audio_path, sr=16000)
            duration = len(y) / sr
            
            # Detect speech characteristics
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # Adjust parameters based on audio characteristics
            optimized_config = self.arabic_config.copy()
            
            # Adjust for speech tempo (Arabic can have varied pacing)
            if tempo > 120:  # Fast speech
                optimized_config["segmentation"]["min_duration_on"] = 0.15
                optimized_config["segmentation"]["min_duration_off"] = 0.05
            elif tempo < 80:  # Slow speech
                optimized_config["segmentation"]["min_duration_on"] = 0.3
                optimized_config["segmentation"]["min_duration_off"] = 0.15
            
            # Adjust for audio quality
            avg_zcr = float(zero_crossing_rate.mean())
            if avg_zcr > 0.1:  # Noisy audio
                optimized_config["segmentation"]["threshold"] = 0.5  # Higher threshold
            elif avg_zcr < 0.05:  # Clean audio
                optimized_config["segmentation"]["threshold"] = 0.4  # Lower threshold
            
            logger.info("Arabic diarization optimization applied",
                       tempo=tempo, avg_zcr=avg_zcr, duration=duration)
            
            return optimized_config
            
        except Exception as e:
            logger.warning("Could not optimize for Arabic patterns, using defaults", error=str(e))
            return self.arabic_config


def align_transcription_with_diarization(
    transcription_segments: List,
    diarization_result: DiarizationResult
) -> List[Dict[str, Any]]:
    """Align transcription segments with speaker diarization"""
    
    try:
        aligned_segments = []
        speaker_turns = diarization_result.turns
        
        for transcript_seg in transcription_segments:
            # Find overlapping speaker turns
            overlaps = []
            
            for turn in speaker_turns:
                # Calculate overlap
                overlap_start = max(transcript_seg.start, turn.start)
                overlap_end = min(transcript_seg.end, turn.end)
                overlap_duration = max(0, overlap_end - overlap_start)
                
                if overlap_duration > 0:
                    overlap_ratio = overlap_duration / (transcript_seg.end - transcript_seg.start)
                    overlaps.append({
                        "speaker": turn.speaker,
                        "overlap_ratio": overlap_ratio,
                        "confidence": turn.confidence
                    })
            
            # Assign to speaker with most overlap
            if overlaps:
                best_match = max(overlaps, key=lambda x: x["overlap_ratio"])
                assigned_speaker = best_match["speaker"]
                speaker_confidence = best_match["confidence"]
            else:
                # No overlap found - assign to closest speaker
                assigned_speaker = None
                speaker_confidence = 0.0
                
                if speaker_turns:
                    # Find closest speaker turn
                    distances = []
                    for turn in speaker_turns:
                        if transcript_seg.start >= turn.end:
                            distance = transcript_seg.start - turn.end
                        elif transcript_seg.end <= turn.start:
                            distance = turn.start - transcript_seg.end
                        else:
                            distance = 0  # Overlapping
                        
                        distances.append((turn.speaker, distance, turn.confidence))
                    
                    if distances:
                        assigned_speaker, _, speaker_confidence = min(distances, key=lambda x: x[1])
            
            # Create aligned segment
            aligned_segment = {
                "start": transcript_seg.start,
                "end": transcript_seg.end,
                "text": transcript_seg.text,
                "confidence": transcript_seg.confidence,
                "speaker_id": assigned_speaker,
                "speaker_confidence": speaker_confidence,
                "words": transcript_seg.words,
                "is_aligned": assigned_speaker is not None
            }
            
            aligned_segments.append(aligned_segment)
        
        logger.info("Transcription-diarization alignment completed",
                   segments=len(aligned_segments),
                   aligned_segments=len([s for s in aligned_segments if s["is_aligned"]]))
        
        return aligned_segments
        
    except Exception as e:
        logger.error("Alignment failed", error=str(e))
        return []


# Global diarization processor instance
_diarization_processor = None


def get_diarization_processor() -> DiarizationProcessor:
    """Get cached diarization processor instance"""
    global _diarization_processor
    
    if _diarization_processor is None:
        _diarization_processor = DiarizationProcessor()
    
    return _diarization_processor


def clear_diarization_cache():
    """Clear diarization processor cache"""
    global _diarization_processor
    
    if _diarization_processor and _diarization_processor.pipeline:
        del _diarization_processor.pipeline
        _diarization_processor.pipeline = None
        
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    _diarization_processor = None
    logger.info("Diarization processor cache cleared")