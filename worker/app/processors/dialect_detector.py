"""
Arabic Dialect Detection Service
Automatically detects Iraqi Arabic vs MSA and other dialects
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DialectDetectionResult:
    """Result of dialect detection analysis"""
    detected_dialect: str
    confidence: float
    dialect_features: Dict[str, int]
    recommendations: Dict[str, str]

class ArabicDialectDetector:
    """
    Automatic Arabic dialect detection service
    Identifies Iraqi Arabic vs MSA and other major dialects
    """
    
    def __init__(self):
        # Iraqi Arabic distinctive features
        self.iraqi_patterns = {
            # Distinctive Iraqi phonemes and words
            'iraqi_phonemes': [
                r'گ[اوي]', r'چ[اني]', r'پ[اي]', r'ڤ[اي]', 
                r'ۆ[نل]', r'ڵ[اه]', r'ێ[شن]'
            ],
            'iraqi_expressions': [
                r'شلون[كم]?', r'شكو\s*ماكو', r'اكو', r'ماكو',
                r'وين', r'شنو', r'هسه', r'يمعود', r'زين',
                r'مو\s+', r'خوش', r'حلو', r'جان', r'چان'
            ],
            'iraqi_verbs': [
                r'گال', r'گلت', r'گلنا', r'گلتوا',
                r'چان', r'چنت', r'چنا', r'چنتوا'
            ]
        }
        
        # MSA (Modern Standard Arabic) patterns
        self.msa_patterns = {
            'formal_expressions': [
                r'كيف\s+حالكم?', r'أهلاً\s+وسهلاً', r'مرحباً',
                r'تفضلوا?', r'من\s+فضلكم?', r'شكراً\s+لكم?'
            ],
            'formal_verbs': [
                r'قال', r'قلت', r'قلنا', r'قلتم',
                r'كان', r'كنت', r'كنا', r'كنتم'
            ],
            'formal_structures': [
                r'إن\s+', r'أن\s+', r'لكن\s+', r'غير\s+أن',
                r'بالإضافة\s+إلى', r'من\s+ناحية', r'في\s+الواقع'
            ]
        }
        
        # Egyptian Arabic patterns
        self.egyptian_patterns = {
            'egyptian_expressions': [
                r'إزيك', r'عامل\s+إيه', r'النهاردة', r'امبارح',
                r'بكرة', r'دلوقتي', r'كده', r'ازاي'
            ]
        }
        
        # Gulf Arabic patterns
        self.gulf_patterns = {
            'gulf_expressions': [
                r'شلونك', r'شفيك', r'وش\s+أخبارك', r'كيف\s+الحال',
                r'الحين', r'وايد', r'شنو', r'ليش'
            ]
        }
    
    def detect_dialect(self, text: str) -> DialectDetectionResult:
        """
        Detect Arabic dialect from text
        
        Args:
            text: Arabic text to analyze
            
        Returns:
            DialectDetectionResult with detected dialect and confidence
        """
        if not text or not text.strip():
            return DialectDetectionResult(
                detected_dialect="unknown",
                confidence=0.0,
                dialect_features={},
                recommendations={"error": "Empty text provided"}
            )
        
        # Clean and normalize text
        normalized_text = self._normalize_text(text)
        
        # Count dialect features
        feature_counts = {
            'iraqi': self._count_iraqi_features(normalized_text),
            'msa': self._count_msa_features(normalized_text),
            'egyptian': self._count_egyptian_features(normalized_text),
            'gulf': self._count_gulf_features(normalized_text)
        }
        
        # Calculate confidence scores
        total_features = sum(feature_counts.values())
        if total_features == 0:
            return DialectDetectionResult(
                detected_dialect="ar",  # Default to MSA
                confidence=0.3,
                dialect_features=feature_counts,
                recommendations={"suggestion": "No clear dialect markers found, defaulting to MSA"}
            )
        
        # Determine dominant dialect
        dominant_dialect = max(feature_counts.keys(), key=lambda k: feature_counts[k])
        confidence = feature_counts[dominant_dialect] / total_features
        
        # Map to language codes
        dialect_mapping = {
            'iraqi': 'ar-IQ',
            'msa': 'ar',
            'egyptian': 'ar-EG',
            'gulf': 'ar-SA'
        }
        
        detected_code = dialect_mapping.get(dominant_dialect, 'ar')
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            dominant_dialect, confidence, feature_counts
        )
        
        return DialectDetectionResult(
            detected_dialect=detected_code,
            confidence=confidence,
            dialect_features=feature_counts,
            recommendations=recommendations
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize Arabic text for analysis"""
        # Remove diacritics
        text = re.sub(r'[\u064B-\u0652]', '', text)
        # Normalize spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _count_iraqi_features(self, text: str) -> int:
        """Count Iraqi Arabic features in text"""
        count = 0
        for pattern_group in self.iraqi_patterns.values():
            for pattern in pattern_group:
                count += len(re.findall(pattern, text, re.IGNORECASE))
        return count
    
    def _count_msa_features(self, text: str) -> int:
        """Count MSA features in text"""
        count = 0
        for pattern_group in self.msa_patterns.values():
            for pattern in pattern_group:
                count += len(re.findall(pattern, text, re.IGNORECASE))
        return count
    
    def _count_egyptian_features(self, text: str) -> int:
        """Count Egyptian Arabic features in text"""
        count = 0
        for pattern_group in self.egyptian_patterns.values():
            for pattern in pattern_group:
                count += len(re.findall(pattern, text, re.IGNORECASE))
        return count
    
    def _count_gulf_features(self, text: str) -> int:
        """Count Gulf Arabic features in text"""
        count = 0
        for pattern_group in self.gulf_patterns.values():
            for pattern in pattern_group:
                count += len(re.findall(pattern, text, re.IGNORECASE))
        return count
    
    def _generate_recommendations(
        self, 
        dominant_dialect: str, 
        confidence: float, 
        feature_counts: Dict[str, int]
    ) -> Dict[str, str]:
        """Generate processing recommendations based on detection results"""
        
        recommendations = {}
        
        if confidence >= 0.7:
            recommendations["confidence"] = "High confidence detection"
            recommendations["processing"] = f"Use {dominant_dialect}-optimized ASR settings"
        elif confidence >= 0.4:
            recommendations["confidence"] = "Medium confidence detection"
            recommendations["processing"] = f"Use {dominant_dialect} settings with fallback to MSA"
        else:
            recommendations["confidence"] = "Low confidence detection"
            recommendations["processing"] = "Use MSA settings for best compatibility"
        
        # Specific recommendations for Iraqi Arabic
        if dominant_dialect == 'iraqi' and confidence >= 0.5:
            recommendations["model_settings"] = "Enable Iraqi phoneme support (گ، چ، پ، ڤ)"
            recommendations["vocabulary"] = "Use Iraqi-specific hotwords"
            recommendations["prompt"] = "Use Iraqi dialect initial prompt"
        
        return recommendations

# Global instance for easy access
dialect_detector = ArabicDialectDetector()

def detect_arabic_dialect(text: str) -> DialectDetectionResult:
    """
    Convenience function to detect Arabic dialect
    
    Args:
        text: Arabic text to analyze
        
    Returns:
        DialectDetectionResult with detection results
    """
    return dialect_detector.detect_dialect(text)