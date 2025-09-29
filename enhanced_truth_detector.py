#!/usr/bin/env python3
"""
Enhanced Truth Detection Module
Integrates acoustic analysis with narrative truth detection for comprehensive credibility assessment
Combines voice stress indicators, prosodic features, and linguistic patterns
"""

import os
import json
import time
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path

# Import existing analyzers
from narrative_truth_analyzer import NarrativeTruthAnalyzer, NarrativeTruthResult
from acoustic_analyzer import AcousticAnalyzer, AcousticAnalysisResult

@dataclass
class AcousticTruthMarkers:
    """Acoustic markers specifically for truth detection"""
    voice_stress_level: float  # 0-1, higher = more stress
    pitch_variability: float  # 0-1, abnormal variability may indicate deception
    speech_rate_consistency: float  # 0-1, consistent rate = more credible
    pause_pattern_naturalness: float  # 0-1, natural pauses = more credible
    vocal_tension: float  # 0-1, higher tension may indicate stress/deception
    formant_stability: float  # 0-1, stable formants = more natural speech
    jitter_shimmer_ratio: float  # Voice quality indicator
    overall_vocal_authenticity: float  # Combined acoustic authenticity score

@dataclass
class MultimodalTruthCorrelation:
    """Correlations between acoustic and linguistic truth indicators"""
    stress_linguistic_consistency: float  # How well stress matches linguistic uncertainty
    emotion_prosody_alignment: float  # Emotional content vs prosodic features
    certainty_voice_confidence: float  # Linguistic certainty vs vocal confidence
    temporal_speech_consistency: float  # Time references vs speech patterns
    overall_multimodal_coherence: float  # Overall cross-modal consistency

@dataclass
class EnhancedTruthResult:
    """Enhanced truth detection result combining acoustic and linguistic analysis"""
    text: str
    audio_file: Optional[str]
    
    # Core truth metrics
    overall_truth_likelihood: float  # 0-1, combined truth score
    confidence_level: float  # 0-1, confidence in the assessment
    credibility_score: float  # 0-1, overall credibility
    
    # Component analyses
    linguistic_truth_result: NarrativeTruthResult
    acoustic_analysis_result: Optional[AcousticAnalysisResult]
    acoustic_truth_markers: Optional[AcousticTruthMarkers]
    multimodal_correlations: Optional[MultimodalTruthCorrelation]
    
    # Enhanced insights
    deception_likelihood: float  # 0-1, likelihood of deception
    stress_indicators: Dict[str, float]
    authenticity_markers: Dict[str, float]
    behavioral_indicators: List[str]
    
    # Recommendations
    reliability_assessment: str
    investigation_recommendations: List[str]
    confidence_factors: List[str]
    
    processing_time: float
    analysis_timestamp: float

class EnhancedTruthDetector:
    """Enhanced truth detector combining acoustic and linguistic analysis"""
    
    def __init__(self, model_name: str = "aya:35b-23-q4_K_M"):
        self.narrative_analyzer = NarrativeTruthAnalyzer(model_name)
        self.acoustic_analyzer = AcousticAnalyzer()
        
        # Acoustic truth detection thresholds
        self.stress_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
        
        self.authenticity_weights = {
            'linguistic': 0.4,
            'acoustic': 0.35,
            'multimodal_consistency': 0.25
        }
    
    def extract_acoustic_truth_markers(self, acoustic_result: 'AcousticAnalysisResult') -> AcousticTruthMarkers:
        """Extract truth-relevant markers from acoustic analysis"""
        try:
            stress_indicators = acoustic_result.stress_indicators
            deception_markers = acoustic_result.deception_markers
            
            # Extract key acoustic markers
            pitch_variability = deception_markers.pitch_variability_score
            voice_quality = deception_markers.voice_quality_degradation
            hesitation_score = deception_markers.hesitation_markers
            speech_rate_variation = deception_markers.speech_rate_changes
            vocal_tension = deception_markers.vocal_tension_score
            
            # Calculate overall stress level from individual indicators
            overall_stress = (
                stress_indicators.stress_level * 0.3 +
                stress_indicators.voice_tension * 0.25 +
                stress_indicators.emotional_arousal * 0.2 +
                stress_indicators.breathing_irregularity * 0.15 +
                stress_indicators.vocal_effort * 0.1
            )
            
            return AcousticTruthMarkers(
                voice_stress_level=overall_stress,
                pitch_variability=pitch_variability,
                speech_rate_consistency=1.0 - speech_rate_variation,
                pause_pattern_naturalness=1.0 - hesitation_score,
                vocal_tension=vocal_tension,
                formant_stability=1.0 - voice_quality,
                jitter_shimmer_ratio=voice_quality,
                overall_vocal_authenticity=1.0 - ((pitch_variability + voice_quality + vocal_tension) / 3)
            )
        except Exception as e:
            print(f"⚠️ Error extracting acoustic markers: {e}")
            # Return default markers if extraction fails
            return AcousticTruthMarkers(
                voice_stress_level=0.5,
                pitch_variability=0.5,
                speech_rate_consistency=0.5,
                pause_pattern_naturalness=0.5,
                vocal_tension=0.5,
                formant_stability=0.5,
                jitter_shimmer_ratio=0.5,
                overall_vocal_authenticity=0.5
            )
    
    def calculate_multimodal_correlations(self, 
                                        linguistic_result: NarrativeTruthResult,
                                        acoustic_markers: AcousticTruthMarkers) -> MultimodalTruthCorrelation:
        """Calculate correlations between acoustic and linguistic truth indicators"""
        
        # Stress-linguistic consistency
        # High linguistic uncertainty should correlate with high voice stress
        linguistic_uncertainty = 1.0 - linguistic_result.truth_likelihood
        stress_consistency = 1.0 - abs(linguistic_uncertainty - acoustic_markers.voice_stress_level)
        
        # Emotion-prosody alignment
        # Emotional inconsistency in text should correlate with vocal tension
        emotional_inconsistency = linguistic_result.deception_markers.emotional_inconsistency
        emotion_prosody_alignment = 1.0 - abs(emotional_inconsistency - acoustic_markers.vocal_tension)
        
        # Certainty-voice confidence alignment
        # High linguistic certainty should correlate with vocal confidence (low stress)
        certainty_indicators = [ti for ti in linguistic_result.truth_indicators 
                               if ti.indicator_type == 'high_certainty']
        linguistic_certainty = min(len(certainty_indicators) / 5.0, 1.0)  # Normalize
        vocal_confidence = 1.0 - acoustic_markers.voice_stress_level
        certainty_voice_consistency = 1.0 - abs(linguistic_certainty - vocal_confidence)
        
        # Temporal-speech consistency
        # Temporal precision in text should correlate with consistent speech patterns
        temporal_consistency = linguistic_result.narrative_coherence.temporal_consistency
        speech_consistency = acoustic_markers.speech_rate_consistency
        temporal_speech_consistency = 1.0 - abs(temporal_consistency - speech_consistency)
        
        # Overall multimodal coherence
        coherence_factors = [
            stress_consistency,
            emotion_prosody_alignment,
            certainty_voice_consistency,
            temporal_speech_consistency
        ]
        overall_coherence = sum(coherence_factors) / len(coherence_factors)
        
        return MultimodalTruthCorrelation(
            stress_linguistic_consistency=stress_consistency,
            emotion_prosody_alignment=emotion_prosody_alignment,
            certainty_voice_confidence=certainty_voice_consistency,
            temporal_speech_consistency=temporal_speech_consistency,
            overall_multimodal_coherence=overall_coherence
        )
    
    def generate_behavioral_indicators(self, 
                                     linguistic_result: NarrativeTruthResult,
                                     acoustic_markers: Optional[AcousticTruthMarkers],
                                     correlations: Optional[MultimodalTruthCorrelation]) -> List[str]:
        """Generate behavioral indicators based on analysis"""
        indicators = []
        
        # Linguistic indicators
        if linguistic_result.deception_markers.defensive_language > 0.3:
            indicators.append("🚨 High defensive language usage detected")
        
        if linguistic_result.deception_markers.detail_overload > 0.4:
            indicators.append("⚠️ Excessive detail provision (possible overcompensation)")
        
        if linguistic_result.narrative_coherence.temporal_consistency < 0.3:
            indicators.append("🕐 Poor temporal consistency in narrative")
        
        # Acoustic indicators
        if acoustic_markers:
            if acoustic_markers.voice_stress_level > 0.7:
                indicators.append("😰 High voice stress levels detected")
            
            if acoustic_markers.vocal_tension > 0.6:
                indicators.append("🎤 Significant vocal tension observed")
            
            if acoustic_markers.pitch_variability > 0.5:
                indicators.append("📊 Abnormal pitch variability patterns")
            
            if acoustic_markers.speech_rate_consistency < 0.4:
                indicators.append("⏱️ Inconsistent speech rate patterns")
        
        # Multimodal indicators
        if correlations:
            if correlations.overall_multimodal_coherence < 0.4:
                indicators.append("🔄 Poor consistency between voice and content")
            
            if correlations.emotion_prosody_alignment < 0.3:
                indicators.append("😕 Emotional content doesn't match vocal expression")
        
        return indicators
    
    def generate_recommendations(self, result: EnhancedTruthResult) -> Tuple[List[str], List[str]]:
        """Generate investigation recommendations and confidence factors"""
        recommendations = []
        confidence_factors = []
        
        # Investigation recommendations
        if result.overall_truth_likelihood < 0.4:
            recommendations.append("🔍 Recommend detailed follow-up investigation")
            recommendations.append("📋 Verify specific claims and timeline details")
        
        if result.deception_likelihood > 0.6:
            recommendations.append("⚠️ High deception risk - cross-reference with other sources")
        
        if result.acoustic_truth_markers and result.acoustic_truth_markers.voice_stress_level > 0.7:
            recommendations.append("🎤 Consider additional audio analysis or re-interview")
        
        if result.multimodal_correlations and result.multimodal_correlations.overall_multimodal_coherence < 0.4:
            recommendations.append("🔄 Investigate inconsistencies between verbal and vocal cues")
        
        # Confidence factors
        if result.confidence_level > 0.7:
            confidence_factors.append("✅ High confidence due to sufficient evidence")
        
        if result.linguistic_truth_result.narrative_coherence.overall_score > 0.7:
            confidence_factors.append("📝 Strong narrative coherence supports assessment")
        
        if result.acoustic_truth_markers and result.acoustic_truth_markers.overall_vocal_authenticity > 0.7:
            confidence_factors.append("🎵 Vocal patterns support authenticity")
        
        if result.multimodal_correlations and result.multimodal_correlations.overall_multimodal_coherence > 0.6:
            confidence_factors.append("🔄 Good consistency between modalities")
        
        return recommendations, confidence_factors
    
    def assess_reliability(self, truth_likelihood: float, confidence: float, deception_likelihood: float) -> str:
        """Generate overall reliability assessment"""
        if truth_likelihood > 0.8 and confidence > 0.7:
            return "🟢 HIGH RELIABILITY - Statement appears highly credible"
        elif truth_likelihood > 0.6 and confidence > 0.5:
            return "🟡 MODERATE RELIABILITY - Statement has reasonable credibility"
        elif truth_likelihood > 0.4:
            return "🟠 LOW RELIABILITY - Statement has questionable credibility"
        else:
            return "🔴 VERY LOW RELIABILITY - Statement appears highly questionable"
    
    def analyze_comprehensive(self, text: str, audio_file: Optional[str] = None) -> EnhancedTruthResult:
        """Perform comprehensive enhanced truth detection analysis"""
        start_time = time.time()
        
        print(f"🔍 Starting Enhanced Truth Detection Analysis...")
        print(f"📝 Text length: {len(text)} characters")
        if audio_file:
            print(f"🎵 Audio file: {audio_file}")
        
        # Perform linguistic analysis
        print("📊 Analyzing linguistic patterns...")
        linguistic_result = self.narrative_analyzer.analyze_comprehensive(text)
        
        # Perform acoustic analysis if audio is available
        acoustic_result = None
        acoustic_markers = None
        correlations = None
        
        if audio_file and os.path.exists(audio_file):
            print("🎤 Analyzing acoustic features...")
            try:
                acoustic_result = self.acoustic_analyzer.analyze_audio(audio_file)
                acoustic_markers = self.extract_acoustic_truth_markers(acoustic_result)
                correlations = self.calculate_multimodal_correlations(linguistic_result, acoustic_markers)
                print("✅ Acoustic analysis completed")
            except Exception as e:
                print(f"⚠️ Acoustic analysis failed: {e}")
        
        # Calculate enhanced truth metrics
        print("🧮 Calculating enhanced truth metrics...")
        
        # Base truth likelihood from linguistic analysis
        linguistic_truth = linguistic_result.truth_likelihood
        
        # Adjust with acoustic evidence if available
        if acoustic_markers:
            acoustic_truth = acoustic_markers.overall_vocal_authenticity
            multimodal_consistency = correlations.overall_multimodal_coherence if correlations else 0.5
            
            # Weighted combination
            overall_truth_likelihood = (
                linguistic_truth * self.authenticity_weights['linguistic'] +
                acoustic_truth * self.authenticity_weights['acoustic'] +
                multimodal_consistency * self.authenticity_weights['multimodal_consistency']
            )
        else:
            overall_truth_likelihood = linguistic_truth
        
        # Calculate confidence level
        evidence_factors = [linguistic_result.confidence_score]
        if acoustic_markers:
            evidence_factors.append(min(acoustic_markers.overall_vocal_authenticity * 1.2, 1.0))
        if correlations:
            evidence_factors.append(correlations.overall_multimodal_coherence)
        
        confidence_level = sum(evidence_factors) / len(evidence_factors)
        
        # Calculate credibility score (combines truth likelihood and confidence)
        credibility_score = (overall_truth_likelihood * 0.7 + confidence_level * 0.3)
        
        # Calculate deception likelihood
        linguistic_deception = linguistic_result.deception_markers.overall_deception_likelihood
        if acoustic_markers:
            acoustic_deception = (acoustic_markers.voice_stress_level + acoustic_markers.vocal_tension) / 2
            deception_likelihood = (linguistic_deception + acoustic_deception) / 2
        else:
            deception_likelihood = linguistic_deception
        
        # Generate stress indicators
        stress_indicators = {
            'linguistic_stress': linguistic_result.deception_markers.emotional_inconsistency,
            'temporal_stress': linguistic_result.deception_markers.temporal_vagueness,
            'defensive_stress': linguistic_result.deception_markers.defensive_language
        }
        
        if acoustic_markers:
            stress_indicators.update({
                'vocal_stress': acoustic_markers.voice_stress_level,
                'vocal_tension': acoustic_markers.vocal_tension,
                'speech_inconsistency': 1.0 - acoustic_markers.speech_rate_consistency
            })
        
        # Generate authenticity markers
        authenticity_markers = {
            'narrative_coherence': linguistic_result.narrative_coherence.overall_score,
            'temporal_consistency': linguistic_result.narrative_coherence.temporal_consistency,
            'emotional_consistency': linguistic_result.narrative_coherence.emotional_consistency
        }
        
        if acoustic_markers:
            authenticity_markers.update({
                'vocal_authenticity': acoustic_markers.overall_vocal_authenticity,
                'speech_naturalness': acoustic_markers.pause_pattern_naturalness,
                'voice_stability': acoustic_markers.formant_stability
            })
        
        # Generate behavioral indicators
        behavioral_indicators = self.generate_behavioral_indicators(
            linguistic_result, acoustic_markers, correlations
        )
        
        # Generate recommendations and confidence factors
        processing_time = time.time() - start_time
        
        # Create preliminary result for recommendation generation
        preliminary_result = EnhancedTruthResult(
            text=text,
            audio_file=audio_file,
            overall_truth_likelihood=overall_truth_likelihood,
            confidence_level=confidence_level,
            credibility_score=credibility_score,
            linguistic_truth_result=linguistic_result,
            acoustic_analysis_result=acoustic_result,
            acoustic_truth_markers=acoustic_markers,
            multimodal_correlations=correlations,
            deception_likelihood=deception_likelihood,
            stress_indicators=stress_indicators,
            authenticity_markers=authenticity_markers,
            behavioral_indicators=behavioral_indicators,
            reliability_assessment="",
            investigation_recommendations=[],
            confidence_factors=[],
            processing_time=processing_time,
            analysis_timestamp=time.time()
        )
        
        # Generate final assessments
        recommendations, confidence_factors = self.generate_recommendations(preliminary_result)
        reliability_assessment = self.assess_reliability(
            overall_truth_likelihood, confidence_level, deception_likelihood
        )
        
        # Create final result
        final_result = EnhancedTruthResult(
            text=text,
            audio_file=audio_file,
            overall_truth_likelihood=overall_truth_likelihood,
            confidence_level=confidence_level,
            credibility_score=credibility_score,
            linguistic_truth_result=linguistic_result,
            acoustic_analysis_result=acoustic_result,
            acoustic_truth_markers=acoustic_markers,
            multimodal_correlations=correlations,
            deception_likelihood=deception_likelihood,
            stress_indicators=stress_indicators,
            authenticity_markers=authenticity_markers,
            behavioral_indicators=behavioral_indicators,
            reliability_assessment=reliability_assessment,
            investigation_recommendations=recommendations,
            confidence_factors=confidence_factors,
            processing_time=processing_time,
            analysis_timestamp=time.time()
        )
        
        print(f"✅ Enhanced truth detection completed in {processing_time:.2f}s")
        return final_result

def main():
    """Test the enhanced truth detector"""
    # Sample Arabic text
    sample_text = """
    شكراً لكم. بعد ما أعرف، لا لا، ما عادي، ما عندي شي ما أخبرتك به، ولكن لدي يوم نيئ عندما أرى بناتي، إن شاء الله، والله إن شاء الله رحمة الله عز وجل. لا لا، لم أتواصل معهم، لا أعرف كل شيء، فقط أخبرتني أنني سأرى بناتي قبل التنفيذ.
    """
    
    # Find audio file
    audio_file = None
    possible_files = ["test_audio_converted.wav", "250825-1107_OugfC4aY.mp3"]
    for file in possible_files:
        if os.path.exists(file):
            audio_file = file
            break
    
    detector = EnhancedTruthDetector()
    
    print("🔍 ENHANCED TRUTH DETECTION ANALYSIS")
    print("=" * 80)
    
    result = detector.analyze_comprehensive(sample_text, audio_file)
    
    print("\n📊 ENHANCED TRUTH DETECTION RESULTS")
    print("=" * 80)
    print(f"Overall Truth Likelihood: {result.overall_truth_likelihood:.3f}")
    print(f"Confidence Level: {result.confidence_level:.3f}")
    print(f"Credibility Score: {result.credibility_score:.3f}")
    print(f"Deception Likelihood: {result.deception_likelihood:.3f}")
    print(f"Processing Time: {result.processing_time:.2f}s")
    
    print(f"\n{result.reliability_assessment}")
    
    print(f"\n🎯 STRESS INDICATORS:")
    for indicator, score in result.stress_indicators.items():
        print(f"  {indicator}: {score:.3f}")
    
    print(f"\n✨ AUTHENTICITY MARKERS:")
    for marker, score in result.authenticity_markers.items():
        print(f"  {marker}: {score:.3f}")
    
    if result.behavioral_indicators:
        print(f"\n⚠️ BEHAVIORAL INDICATORS:")
        for indicator in result.behavioral_indicators:
            print(f"  {indicator}")
    
    if result.investigation_recommendations:
        print(f"\n🔍 INVESTIGATION RECOMMENDATIONS:")
        for rec in result.investigation_recommendations:
            print(f"  {rec}")
    
    if result.confidence_factors:
        print(f"\n✅ CONFIDENCE FACTORS:")
        for factor in result.confidence_factors:
            print(f"  {factor}")
    
    # Save results
    timestamp = int(time.time())
    results_file = f"enhanced_truth_detection_{timestamp}.json"
    
    # Convert result to dictionary for JSON serialization
    def convert_to_serializable(obj):
        """Convert complex objects to JSON serializable format"""
        if hasattr(obj, '__dict__'):
            return {k: convert_to_serializable(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (bool, np.bool_)):
            return bool(obj)
        else:
            return obj
    
    result_dict = convert_to_serializable(asdict(result))
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")

if __name__ == "__main__":
    main()