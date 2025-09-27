"""
Arabic ASR processing using faster-whisper
"""

import os
import time
from typing import Dict, List, Any, Optional, NamedTuple
from dataclasses import dataclass
import torch
import structlog
from faster_whisper import WhisperModel

logger = structlog.get_logger(__name__)


@dataclass
class WordTimestamp:
    """Word-level timestamp information"""
    word: str
    start: float
    end: float
    confidence: float


@dataclass
class TranscriptSegment:
    """Transcript segment with metadata"""
    start: float
    end: float
    text: str
    confidence: float
    words: List[WordTimestamp]
    speaker_id: Optional[str] = None


@dataclass
class TranscriptionResult:
    """Complete transcription result"""
    segments: List[TranscriptSegment]
    language: str
    confidence: float
    processing_time: float
    model_used: str
    audio_duration: Optional[float] = None


class ASRProcessor:
    """Arabic Speech Recognition processor using faster-whisper"""
    
    def __init__(self, model_name: str = "large-v3"):
        self.model_name = model_name
        self.model: Optional[WhisperModel] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if torch.cuda.is_available() else "int8"
        
        # Arabic-specific configuration
        self.arabic_config = {
            "large-v3": {
                "initial_prompt": "التحدث باللغة العربية الفصحى والعامية",
                "temperature": 0.0,
                "compression_ratio_threshold": 2.4,
                "log_prob_threshold": -1.0,
                "no_speech_threshold": 0.6,
                "beam_size": 5
            },
            "medium": {
                "initial_prompt": "الكلام باللغة العربية",
                "temperature": 0.0,
                "compression_ratio_threshold": 2.2,
                "log_prob_threshold": -1.2,
                "no_speech_threshold": 0.65,
                "beam_size": 4
            },
            "small": {
                "initial_prompt": "العربية",
                "temperature": 0.1,
                "compression_ratio_threshold": 2.0,
                "log_prob_threshold": -1.5,
                "no_speech_threshold": 0.7,
                "beam_size": 3
            }
        }
        
        logger.info("ASR Processor initialized", 
                   model=model_name, device=self.device, compute_type=self.compute_type)
    
    def _load_model(self):
        """Load Whisper model"""
        if self.model is None:
            try:
                logger.info("Loading Whisper model", model=self.model_name)
                
                self.model = WhisperModel(
                    self.model_name,
                    device=self.device,
                    compute_type=self.compute_type,
                    cpu_threads=os.cpu_count() if self.device == "cpu" else 0,
                    num_workers=1  # Single worker to avoid memory issues
                )
                
                logger.info("Whisper model loaded successfully", 
                           model=self.model_name, device=self.device)
                
            except Exception as e:
                logger.error("Failed to load Whisper model", 
                           model=self.model_name, error=str(e))
                raise
    
    def transcribe(
        self,
        audio_path: str,
        language: str = "ar",
        **kwargs
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe Arabic audio file
        
        Args:
            audio_path: Path to audio file
            language: Language code (ar, ar-IQ, ar-EG, etc.)
            **kwargs: Additional transcription options
        
        Returns:
            TranscriptionResult with segments and metadata
        """
        
        start_time = time.time()
        
        try:
            # Load model if not already loaded
            self._load_model()
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            logger.info("Starting transcription", 
                       audio_path=audio_path, language=language, model=self.model_name)
            
            # Get Arabic-specific configuration
            base_config = self.arabic_config.get(self.model_name, {})
            
            # Merge with user-provided options
            transcribe_options = {
                "language": language[:2],  # Use base language code (ar)
                "task": "transcribe",
                "word_timestamps": True,
                "condition_on_previous_text": True,
                "prompt_reset_on_temperature": 0.5,
                **base_config,
                **kwargs  # User options override defaults
            }
            
            # Optimize for Arabic dialects
            if language.startswith("ar-"):
                dialect = language.split("-")[1]
                transcribe_options = self._optimize_for_dialect(transcribe_options, dialect)
            
            logger.info("Transcription configuration", config=transcribe_options)
            
            # Perform transcription
            segments, info = self.model.transcribe(audio_path, **transcribe_options)
            
            # Process segments
            processed_segments = []
            total_confidence = 0.0
            segment_count = 0
            
            for segment in segments:
                # Extract word-level timestamps
                words = []
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        words.append(WordTimestamp(
                            word=word.word,
                            start=word.start,
                            end=word.end,
                            confidence=getattr(word, 'probability', 0.0)
                        ))
                
                # Create segment
                transcript_segment = TranscriptSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                    confidence=getattr(segment, 'avg_logprob', 0.0),
                    words=words
                )
                
                processed_segments.append(transcript_segment)
                
                # Track overall confidence
                total_confidence += transcript_segment.confidence
                segment_count += 1
            
            # Calculate overall confidence
            overall_confidence = (
                total_confidence / segment_count if segment_count > 0 else 0.0
            )
            
            # Convert to 0-1 scale (Whisper uses log probabilities)
            overall_confidence = max(0.0, min(1.0, (overall_confidence + 5) / 5))
            
            processing_time = time.time() - start_time
            
            # Get audio duration
            audio_duration = None
            if hasattr(info, 'duration'):
                audio_duration = info.duration
            
            result = TranscriptionResult(
                segments=processed_segments,
                language=info.language,
                confidence=overall_confidence,
                processing_time=processing_time,
                model_used=self.model_name,
                audio_duration=audio_duration
            )
            
            logger.info("Transcription completed successfully",
                       segments_count=len(processed_segments),
                       confidence=overall_confidence,
                       processing_time=processing_time,
                       language_detected=info.language)
            
            return result
            
        except Exception as e:
            logger.error("Transcription failed", 
                        audio_path=audio_path, model=self.model_name, error=str(e))
            return None
    
    def _optimize_for_dialect(self, config: Dict[str, Any], dialect: str) -> Dict[str, Any]:
        """Optimize configuration for specific Arabic dialect"""
        
        optimized_config = config.copy()
        
        if dialect.upper() == "IQ":  # Iraqi Arabic
            optimized_config.update({
                "initial_prompt": "الكلام باللهجة العراقية",
                "temperature": 0.1,  # Slightly higher for dialect variations
                "compression_ratio_threshold": 2.2,
                "log_prob_threshold": -1.2
            })
            
            # Add Iraqi-specific vocabulary
            iraqi_terms = ["شلون", "شكو", "ماكو", "اكو", "وين", "شنو"]
            existing_hotwords = config.get("hotwords", "").split()
            optimized_config["hotwords"] = " ".join(existing_hotwords + iraqi_terms)
            
        elif dialect.upper() == "EG":  # Egyptian Arabic
            optimized_config.update({
                "initial_prompt": "الكلام باللهجة المصرية",
                "temperature": 0.05,
                "compression_ratio_threshold": 2.3
            })
            
        elif dialect.upper() in ["SA", "AE", "KW", "QA", "BH"]:  # Gulf Arabic
            optimized_config.update({
                "initial_prompt": "الكلام باللهجة الخليجية",
                "temperature": 0.05,
                "compression_ratio_threshold": 2.5
            })
            
        elif dialect.upper() in ["MA", "TN", "DZ"]:  # Maghrebi Arabic
            optimized_config.update({
                "initial_prompt": "الكلام باللهجة المغاربية", 
                "temperature": 0.15,  # Higher variation in Maghrebi
                "compression_ratio_threshold": 2.0,
                "log_prob_threshold": -1.5
            })
        
        return optimized_config
    
    def transcribe_with_vad(
        self,
        audio_path: str,
        vad_segments: List[Dict[str, float]],
        **kwargs
    ) -> Optional[TranscriptionResult]:
        """Transcribe audio using pre-computed VAD segments"""
        
        try:
            if not vad_segments:
                # Fall back to full transcription
                return self.transcribe(audio_path, **kwargs)
            
            self._load_model()
            
            all_segments = []
            total_processing_time = 0.0
            
            # Process each VAD segment
            for vad_segment in vad_segments:
                start_time = vad_segment["start"]
                end_time = vad_segment["end"]
                
                # Skip very short segments
                if end_time - start_time < 0.5:
                    continue
                
                logger.debug("Processing VAD segment", start=start_time, end=end_time)
                
                # Transcribe segment
                segment_start = time.time()
                segments, info = self.model.transcribe(
                    audio_path,
                    **kwargs,
                    offset=start_time,
                    duration=end_time - start_time
                )
                segment_processing_time = time.time() - segment_start
                total_processing_time += segment_processing_time
                
                # Adjust timestamps to global timeline
                for segment in segments:
                    adjusted_segment = TranscriptSegment(
                        start=segment.start + start_time,
                        end=segment.end + start_time,
                        text=segment.text.strip(),
                        confidence=getattr(segment, 'avg_logprob', 0.0),
                        words=[]  # Word timestamps would need similar adjustment
                    )
                    all_segments.append(adjusted_segment)
            
            # Calculate overall confidence
            overall_confidence = (
                sum(seg.confidence for seg in all_segments) / len(all_segments)
                if all_segments else 0.0
            )
            overall_confidence = max(0.0, min(1.0, (overall_confidence + 5) / 5))
            
            result = TranscriptionResult(
                segments=all_segments,
                language=kwargs.get("language", "ar"),
                confidence=overall_confidence,
                processing_time=total_processing_time,
                model_used=self.model_name
            )
            
            logger.info("VAD-based transcription completed",
                       vad_segments=len(vad_segments),
                       output_segments=len(all_segments),
                       processing_time=total_processing_time)
            
            return result
            
        except Exception as e:
            logger.error("VAD-based transcription failed", error=str(e))
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        
        if not self.model:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_name": self.model_name,
            "device": self.device,
            "compute_type": self.compute_type,
            "languages_supported": ["ar", "en", "fr", "es"],  # Common languages
            "arabic_dialects": ["ar", "ar-IQ", "ar-EG", "ar-SA", "ar-MA"],
            "max_audio_length": 1800,  # 30 minutes recommended max
            "memory_usage_mb": self._get_memory_usage()
        }
    
    def _get_memory_usage(self) -> float:
        """Get approximate memory usage"""
        if self.device == "cuda" and torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024 / 1024  # MB
        else:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # MB
    
    def benchmark_model(self, test_audio_path: str) -> Dict[str, Any]:
        """Benchmark model performance"""
        
        try:
            # Transcribe test audio
            start_time = time.time()
            result = self.transcribe(test_audio_path, language="ar")
            processing_time = time.time() - start_time
            
            if not result:
                return {"status": "failed", "error": "Transcription failed"}
            
            # Calculate metrics
            audio_duration = result.audio_duration or 60  # Default if not available
            realtime_factor = processing_time / audio_duration
            
            return {
                "status": "completed",
                "model": self.model_name,
                "device": self.device,
                "audio_duration": audio_duration,
                "processing_time": processing_time,
                "realtime_factor": realtime_factor,
                "segments_count": len(result.segments),
                "confidence": result.confidence,
                "performance_rating": self._rate_performance(realtime_factor, result.confidence)
            }
            
        except Exception as e:
            logger.error("Model benchmarking failed", error=str(e))
            return {"status": "error", "error": str(e)}
    
    def _rate_performance(self, realtime_factor: float, confidence: float) -> str:
        """Rate model performance"""
        
        # Performance scoring
        speed_score = 1.0 if realtime_factor <= 1.0 else 1.0 / realtime_factor
        quality_score = confidence
        
        overall_score = (speed_score + quality_score) / 2
        
        if overall_score >= 0.9:
            return "excellent"
        elif overall_score >= 0.7:
            return "good"
        elif overall_score >= 0.5:
            return "fair"
        else:
            return "poor"
    
    def clear_model_cache(self):
        """Clear model from memory"""
        if self.model:
            del self.model
            self.model = None
            
            # Clear GPU cache if using CUDA
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Model cache cleared")


class ArabicGlossaryProcessor:
    """Arabic glossary and vocabulary processing"""
    
    def __init__(self, glossary_path: Optional[str] = None):
        self.glossary = self._load_default_glossary()
        
        if glossary_path and os.path.exists(glossary_path):
            self.load_custom_glossary(glossary_path)
    
    def _load_default_glossary(self) -> Dict[str, Dict[str, Any]]:
        """Load default Arabic glossary"""
        return {
            # Religious terms
            "الله": {"replacement": "الله", "boost": 2.0, "category": "religious"},
            "إنشاء الله": {"replacement": "إن شاء الله", "boost": 1.5, "category": "religious"},
            "ما شاء الله": {"replacement": "ما شاء الله", "boost": 1.5, "category": "religious"},
            "بسم الله": {"replacement": "بسم الله", "boost": 1.5, "category": "religious"},
            
            # Iraqi dialect
            "شلون": {"replacement": "شلون", "boost": 1.5, "dialect": "iraqi"},
            "شكو ماكو": {"replacement": "شكو ماكو", "boost": 1.5, "dialect": "iraqi"},
            "اكو": {"replacement": "اكو", "boost": 1.3, "dialect": "iraqi"},
            "ماكو": {"replacement": "ماكو", "boost": 1.3, "dialect": "iraqi"},
            "وين": {"replacement": "وين", "boost": 1.3, "dialect": "iraqi"},
            "شنو": {"replacement": "شنو", "boost": 1.3, "dialect": "iraqi"},
            
            # Common names
            "محمد": {"replacement": "محمد", "boost": 1.5, "category": "names"},
            "أحمد": {"replacement": "أحمد", "boost": 1.3, "category": "names"},
            "فاطمة": {"replacement": "فاطمة", "boost": 1.3, "category": "names"},
            "عائشة": {"replacement": "عائشة", "boost": 1.3, "category": "names"},
            
            # Technical terms
            "كمبيوتر": {"replacement": "حاسوب", "boost": 1.2, "category": "technology"},
            "انترنت": {"replacement": "إنترنت", "boost": 1.2, "category": "technology"},
            "موبايل": {"replacement": "هاتف محمول", "boost": 1.2, "category": "technology"}
        }
    
    def load_custom_glossary(self, glossary_path: str):
        """Load custom glossary from JSON file"""
        try:
            import json
            with open(glossary_path, 'r', encoding='utf-8') as f:
                custom_glossary = json.load(f)
                self.glossary.update(custom_glossary)
            
            logger.info("Custom glossary loaded", entries=len(custom_glossary))
            
        except Exception as e:
            logger.error("Failed to load custom glossary", error=str(e))
    
    def get_boost_terms(self, dialect: Optional[str] = None, category: Optional[str] = None) -> List[str]:
        """Get terms to boost during transcription"""
        
        boost_terms = []
        
        for term, entry in self.glossary.items():
            include = True
            
            if dialect and entry.get("dialect") and entry["dialect"] != dialect:
                include = False
            
            if category and entry.get("category") and entry["category"] != category:
                include = False
            
            if include and entry.get("boost", 1.0) > 1.0:
                boost_terms.append(term)
        
        return boost_terms
    
    def apply_post_processing(self, text: str, dialect: Optional[str] = None) -> str:
        """Apply glossary-based post-processing"""
        
        import re
        result = text
        
        for term, entry in self.glossary.items():
            if dialect and entry.get("dialect") and entry["dialect"] != dialect:
                continue
            
            if entry["replacement"] != term:
                # Use word boundaries for accurate replacement
                pattern = r'\b' + re.escape(term) + r'\b'
                result = re.sub(pattern, entry["replacement"], result, flags=re.IGNORECASE)
        
        return result


# Global processor instance (cached for model reuse)
_asr_processor_cache = {}


def get_asr_processor(model_name: str = "large-v3") -> ASRProcessor:
    """Get cached ASR processor instance"""
    
    if model_name not in _asr_processor_cache:
        _asr_processor_cache[model_name] = ASRProcessor(model_name)
    
    return _asr_processor_cache[model_name]


def clear_asr_cache():
    """Clear all cached ASR processors"""
    global _asr_processor_cache
    
    for processor in _asr_processor_cache.values():
        processor.clear_model_cache()
    
    _asr_processor_cache.clear()
    logger.info("ASR processor cache cleared")