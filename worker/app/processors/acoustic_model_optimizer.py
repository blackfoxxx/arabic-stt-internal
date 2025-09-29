"""
Acoustic Model Optimizer for Iraqi Arabic Dialect
Fine-tunes model parameters for Iraqi-specific pronunciation patterns
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class IraqiPhonemeMapping:
    """Mapping for Iraqi-specific phonemes and their variations"""
    standard_phoneme: str
    iraqi_variants: List[str]
    frequency_weight: float
    context_patterns: List[str]

@dataclass
class AcousticOptimization:
    """Acoustic model optimization parameters"""
    temperature_adjustments: Dict[str, float]
    beam_size_modifications: Dict[str, int]
    probability_thresholds: Dict[str, float]
    context_weights: Dict[str, float]
    phoneme_mappings: List[IraqiPhonemeMapping]

class AcousticModelOptimizer:
    """
    Optimizes acoustic model parameters for Iraqi Arabic dialect
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "acoustic_optimization_config.json"
        self.iraqi_phoneme_mappings = self._initialize_iraqi_phonemes()
        self.optimization_params = self._load_optimization_config()
        
        logger.info("Acoustic Model Optimizer initialized for Iraqi Arabic")
    
    def _initialize_iraqi_phonemes(self) -> List[IraqiPhonemeMapping]:
        """Initialize Iraqi-specific phoneme mappings"""
        return [
            # گ sound (hard G) - distinctive Iraqi phoneme
            IraqiPhonemeMapping(
                standard_phoneme="ك",
                iraqi_variants=["گ", "غ", "ج"],
                frequency_weight=0.85,
                context_patterns=["گال", "گلب", "گدام", "گوة", "گليل"]
            ),
            
            # ڤ sound (V) - Iraqi pronunciation
            IraqiPhonemeMapping(
                standard_phoneme="ف",
                iraqi_variants=["ڤ", "ب"],
                frequency_weight=0.75,
                context_patterns=["ڤيديو", "ڤيلا", "ڤيتامين", "ڤولت"]
            ),
            
            # پ sound (P) - borrowed words
            IraqiPhonemeMapping(
                standard_phoneme="ب",
                iraqi_variants=["پ"],
                frequency_weight=0.65,
                context_patterns=["پاسپورت", "پيتزا", "پروفيسور", "پارك"]
            ),
            
            # چ sound (CH) - Iraqi pronunciation
            IraqiPhonemeMapping(
                standard_phoneme="ش",
                iraqi_variants=["چ", "ج"],
                frequency_weight=0.80,
                context_patterns=["چاي", "چوب", "چلب", "چگد", "چان"]
            ),
            
            # ۆ sound (O) - Iraqi vowel
            IraqiPhonemeMapping(
                standard_phoneme="و",
                iraqi_variants=["ۆ", "او"],
                frequency_weight=0.70,
                context_patterns=["مۆت", "كۆن", "بۆن", "دۆر"]
            ),
            
            # ڵ sound (LL) - Iraqi L variation
            IraqiPhonemeMapping(
                standard_phoneme="ل",
                iraqi_variants=["ڵ"],
                frequency_weight=0.75,
                context_patterns=["ڵيش", "ڵيل", "ڵون", "ڵوك"]
            ),
            
            # ێ sound (E) - Iraqi vowel
            IraqiPhonemeMapping(
                standard_phoneme="ي",
                iraqi_variants=["ێ", "اي"],
                frequency_weight=0.65,
                context_patterns=["مێز", "كێف", "بێت", "دێر"]
            )
        ]
    
    def _load_optimization_config(self) -> AcousticOptimization:
        """Load or create acoustic optimization configuration"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                logger.info("Loaded existing acoustic optimization config")
                return self._parse_config(config_data)
            except Exception as e:
                logger.warning("Failed to load config, using defaults", error=str(e))
        
        # Create default optimization parameters
        return self._create_default_optimization()
    
    def _create_default_optimization(self) -> AcousticOptimization:
        """Create default acoustic optimization parameters for Iraqi Arabic"""
        return AcousticOptimization(
            temperature_adjustments={
                "high_confidence": 0.0,  # Deterministic for clear speech
                "medium_confidence": 0.1,  # Slight variation for unclear speech
                "low_confidence": 0.3,  # More exploration for difficult audio
                "iraqi_context": 0.05  # Lower temperature for Iraqi patterns
            },
            beam_size_modifications={
                "iraqi_phonemes_detected": 8,  # Larger beam for Iraqi sounds
                "standard_arabic": 5,  # Standard beam size
                "mixed_dialect": 6,  # Medium beam for mixed content
                "technical_terms": 7  # Larger beam for technical vocabulary
            },
            probability_thresholds={
                "iraqi_phoneme_boost": 0.15,  # Boost Iraqi phoneme probabilities
                "context_matching": 0.10,  # Boost contextually appropriate words
                "dialect_consistency": 0.08,  # Maintain dialect consistency
                "common_words": 0.05  # Slight boost for common Iraqi words
            },
            context_weights={
                "previous_iraqi_word": 0.20,  # Strong context from previous Iraqi words
                "phoneme_sequence": 0.15,  # Weight phoneme sequences
                "dialect_pattern": 0.12,  # Weight dialect-specific patterns
                "speaker_consistency": 0.10  # Maintain speaker dialect consistency
            },
            phoneme_mappings=self.iraqi_phoneme_mappings
        )
    
    def optimize_for_iraqi_speech(self, 
                                 base_params: Dict[str, Any],
                                 audio_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimize transcription parameters for Iraqi Arabic speech
        
        Args:
            base_params: Base transcription parameters
            audio_context: Optional context about the audio (quality, speaker, etc.)
            
        Returns:
            Optimized parameters for Iraqi Arabic
        """
        optimized_params = base_params.copy()
        
        # Adjust temperature based on context
        confidence_level = self._assess_confidence_level(audio_context)
        optimized_params["temperature"] = self.optimization_params.temperature_adjustments.get(
            confidence_level, 0.1
        )
        
        # Adjust beam size for Iraqi phoneme detection
        if self._contains_iraqi_phonemes(audio_context):
            optimized_params["beam_size"] = self.optimization_params.beam_size_modifications.get(
                "iraqi_phonemes_detected", 8
            )
        
        # Enhanced initial prompt for Iraqi context
        iraqi_prompt = self._generate_iraqi_prompt(audio_context)
        optimized_params["initial_prompt"] = iraqi_prompt
        
        # Add Iraqi-specific hotwords
        iraqi_hotwords = self._generate_iraqi_hotwords(audio_context)
        if "hotwords" in optimized_params:
            optimized_params["hotwords"].extend(iraqi_hotwords)
        else:
            optimized_params["hotwords"] = iraqi_hotwords
        
        # Adjust probability thresholds
        optimized_params["log_prob_threshold"] = -0.8  # More lenient for dialect variations
        optimized_params["compression_ratio_threshold"] = 2.6  # Allow for Iraqi expressions
        
        # Enable context conditioning for dialect consistency
        optimized_params["condition_on_previous_text"] = True
        optimized_params["prompt_reset_on_temperature"] = 0.3
        
        logger.info("Applied Iraqi Arabic acoustic optimizations", 
                   confidence_level=confidence_level,
                   beam_size=optimized_params.get("beam_size"),
                   temperature=optimized_params.get("temperature"))
        
        return optimized_params
    
    def _assess_confidence_level(self, audio_context: Optional[Dict[str, Any]]) -> str:
        """Assess confidence level based on audio context"""
        if not audio_context:
            return "medium_confidence"
        
        quality_score = audio_context.get("quality_score", 50)
        snr = audio_context.get("snr", 10)
        
        if quality_score >= 80 and snr >= 15:
            return "high_confidence"
        elif quality_score >= 60 and snr >= 10:
            return "medium_confidence"
        else:
            return "low_confidence"
    
    def _contains_iraqi_phonemes(self, audio_context: Optional[Dict[str, Any]]) -> bool:
        """Check if audio likely contains Iraqi phonemes"""
        if not audio_context:
            return True  # Assume Iraqi context by default
        
        # Check for Iraqi dialect indicators
        dialect_hints = audio_context.get("dialect_hints", [])
        iraqi_indicators = ["IQ", "iraqi", "baghdad", "basra", "mosul", "kurdistan"]
        
        return any(hint.lower() in iraqi_indicators for hint in dialect_hints)
    
    def _generate_iraqi_prompt(self, audio_context: Optional[Dict[str, Any]]) -> str:
        """Generate Iraqi-specific initial prompt"""
        base_prompt = "الكلام باللهجة العراقية والعربية"
        
        # Add context-specific elements
        context_elements = []
        
        if audio_context:
            content_type = audio_context.get("content_type", "")
            if "conversation" in content_type.lower():
                context_elements.append("شلونكم شكو ماكو")
            elif "formal" in content_type.lower():
                context_elements.append("الكلام الرسمي")
            elif "technical" in content_type.lower():
                context_elements.append("المصطلحات التقنية")
        
        if context_elements:
            return f"{base_prompt}، {' '.join(context_elements)}"
        
        return f"{base_prompt}، شلونكم شكو ماكو اكو ماكو"
    
    def _generate_iraqi_hotwords(self, audio_context: Optional[Dict[str, Any]]) -> List[str]:
        """Generate Iraqi-specific hotwords based on context"""
        base_hotwords = [
            # Common Iraqi expressions
            "شلونك", "شلونكم", "شكو", "شكو ماكو", "اكو", "ماكو",
            "وين", "شوكت", "چان", "گال", "گلت", "گلنا",
            
            # Iraqi phonetic variations
            "گلب", "گدام", "گوة", "چاي", "چوب", "چلب",
            "ڤيديو", "پاسپورت", "مۆت", "كۆن", "ڵيش", "مێز",
            
            # Regional terms
            "بغداد", "البصرة", "الموصل", "اربيل", "السليمانية",
            "كربلاء", "النجف", "الناصرية", "العمارة", "الديوانية"
        ]
        
        # Add context-specific hotwords
        if audio_context:
            content_type = audio_context.get("content_type", "")
            if "business" in content_type.lower():
                base_hotwords.extend(["شركة", "مشروع", "استثمار", "تجارة"])
            elif "education" in content_type.lower():
                base_hotwords.extend(["مدرسة", "جامعة", "طالب", "استاذ"])
            elif "medical" in content_type.lower():
                base_hotwords.extend(["مستشفى", "دكتور", "مريض", "علاج"])
        
        # Limit to prevent overflow (max 100 hotwords)
        return base_hotwords[:100]
    
    def save_optimization_config(self):
        """Save current optimization configuration"""
        try:
            config_data = {
                "temperature_adjustments": self.optimization_params.temperature_adjustments,
                "beam_size_modifications": self.optimization_params.beam_size_modifications,
                "probability_thresholds": self.optimization_params.probability_thresholds,
                "context_weights": self.optimization_params.context_weights,
                "phoneme_mappings": [
                    {
                        "standard_phoneme": pm.standard_phoneme,
                        "iraqi_variants": pm.iraqi_variants,
                        "frequency_weight": pm.frequency_weight,
                        "context_patterns": pm.context_patterns
                    }
                    for pm in self.optimization_params.phoneme_mappings
                ]
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info("Saved acoustic optimization configuration", path=self.config_path)
            
        except Exception as e:
            logger.error("Failed to save optimization config", error=str(e))
    
    def _parse_config(self, config_data: Dict[str, Any]) -> AcousticOptimization:
        """Parse configuration data into AcousticOptimization object"""
        phoneme_mappings = []
        for pm_data in config_data.get("phoneme_mappings", []):
            phoneme_mappings.append(IraqiPhonemeMapping(
                standard_phoneme=pm_data["standard_phoneme"],
                iraqi_variants=pm_data["iraqi_variants"],
                frequency_weight=pm_data["frequency_weight"],
                context_patterns=pm_data["context_patterns"]
            ))
        
        return AcousticOptimization(
            temperature_adjustments=config_data.get("temperature_adjustments", {}),
            beam_size_modifications=config_data.get("beam_size_modifications", {}),
            probability_thresholds=config_data.get("probability_thresholds", {}),
            context_weights=config_data.get("context_weights", {}),
            phoneme_mappings=phoneme_mappings
        )

# Global optimizer instance
acoustic_optimizer = AcousticModelOptimizer()

def optimize_for_iraqi_dialect(base_params: Dict[str, Any], 
                              audio_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to optimize parameters for Iraqi dialect
    
    Args:
        base_params: Base transcription parameters
        audio_context: Optional audio context information
        
    Returns:
        Optimized parameters for Iraqi Arabic
    """
    return acoustic_optimizer.optimize_for_iraqi_speech(base_params, audio_context)