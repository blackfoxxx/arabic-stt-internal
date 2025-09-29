#!/usr/bin/env python3
"""
Multimodal Analysis System
Integrates text sentiment analysis, narrative truth detection, and acoustic analysis
for comprehensive voice and content evaluation using Aya 35B as primary LLM
"""

import os
import sys
import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our analysis modules
from advanced_sentiment_analyzer import AdvancedArabicSentimentAnalyzer, AdvancedSentimentResult
from narrative_truth_analyzer import NarrativeTruthAnalyzer, NarrativeTruthResult
from acoustic_analyzer import AcousticAnalyzer, AcousticAnalysisResult

@dataclass
class MultimodalCorrelation:
    """Correlations between different analysis modalities"""
    text_acoustic_emotion_correlation: float
    truth_acoustic_stress_correlation: float
    sentiment_prosody_alignment: float
    deception_multimodal_confidence: float
    overall_consistency_score: float
    cross_modal_insights: Dict[str, Any]

@dataclass
class MultimodalInsights:
    """Advanced insights from multimodal analysis"""
    emotional_authenticity_score: float
    cognitive_load_indicators: float
    stress_deception_likelihood: float
    narrative_acoustic_coherence: float
    speaker_psychological_state: Dict[str, float]
    reliability_assessment: Dict[str, float]
    behavioral_indicators: List[str]

@dataclass
class MultimodalAnalysisResult:
    """Complete multimodal analysis result"""
    text_content: str
    audio_file: str
    sentiment_analysis: AdvancedSentimentResult
    truth_analysis: NarrativeTruthResult
    acoustic_analysis: AcousticAnalysisResult
    multimodal_correlation: MultimodalCorrelation
    multimodal_insights: MultimodalInsights
    final_assessment: Dict[str, float]
    recommendations: List[str]
    processing_time: float
    analysis_timestamp: str

class MultimodalAnalysisSystem:
    """Comprehensive multimodal analysis system"""
    
    def __init__(self, primary_model: str = "aya:35b-23-q4_K_M"):
        self.primary_model = primary_model
        self.sentiment_analyzer = AdvancedArabicSentimentAnalyzer(primary_model)
        self.truth_analyzer = NarrativeTruthAnalyzer(primary_model)
        self.acoustic_analyzer = AcousticAnalyzer()
        
        print(f"🤖 Multimodal Analysis System initialized with {primary_model}")
        print(f"📊 Available acoustic libraries:")
        print(f"  - Praat-Parselmouth: {'✅' if self.acoustic_analyzer.praat_available else '❌'}")
        print(f"  - pyAudioAnalysis: {'✅' if self.acoustic_analyzer.pyaudio_available else '❌'}")
        print(f"  - openSMILE: {'✅' if self.acoustic_analyzer.opensmile_available else '❌'}")
    
    def calculate_multimodal_correlations(self, sentiment: AdvancedSentimentResult,
                                        truth: NarrativeTruthResult,
                                        acoustic: AcousticAnalysisResult) -> MultimodalCorrelation:
        """Calculate correlations between different analysis modalities"""
        
        # Text-Acoustic Emotion Correlation
        text_emotion_intensity = sentiment.emotion_scores.emotional_intensity()
        acoustic_arousal = acoustic.emotional_state_acoustic.get('arousal', 0.0)
        text_acoustic_emotion_correlation = 1.0 - abs(text_emotion_intensity - acoustic_arousal)
        
        # Truth-Acoustic Stress Correlation
        truth_likelihood = truth.truth_likelihood
        acoustic_stress = acoustic.stress_indicators.stress_level
        # High stress with low truth likelihood might indicate deception
        truth_acoustic_stress_correlation = 1.0 - abs((1.0 - truth_likelihood) - acoustic_stress)
        
        # Sentiment-Prosody Alignment
        text_valence = 0.5  # Default neutral
        if sentiment.overall_sentiment == 'positive':
            text_valence = 0.7
        elif sentiment.overall_sentiment == 'negative':
            text_valence = 0.3
        
        acoustic_valence = acoustic.emotional_state_acoustic.get('valence', 0.5)
        sentiment_prosody_alignment = 1.0 - abs(text_valence - acoustic_valence)
        
        # Deception Multimodal Confidence
        text_deception = 1.0 - truth.truth_likelihood
        acoustic_deception = np.mean([
            acoustic.deception_markers.pitch_variability_score,
            acoustic.deception_markers.voice_quality_degradation,
            acoustic.deception_markers.hesitation_markers,
            acoustic.deception_markers.vocal_tension_score
        ])
        
        deception_alignment = 1.0 - abs(text_deception - acoustic_deception)
        deception_multimodal_confidence = (
            truth.confidence_score * 0.4 +
            acoustic.deception_markers.confidence_score * 0.4 +
            deception_alignment * 0.2
        )
        
        # Overall Consistency Score
        consistency_factors = [
            text_acoustic_emotion_correlation,
            truth_acoustic_stress_correlation,
            sentiment_prosody_alignment,
            deception_multimodal_confidence
        ]
        overall_consistency_score = np.mean(consistency_factors)
        
        # Cross-modal insights
        cross_modal_insights = {
            'emotion_modality_agreement': text_acoustic_emotion_correlation > 0.7,
            'stress_truth_pattern': 'high_stress_low_truth' if acoustic_stress > 0.6 and truth_likelihood < 0.4 else 'normal',
            'sentiment_prosody_mismatch': sentiment_prosody_alignment < 0.5,
            'deception_indicators_aligned': deception_alignment > 0.6,
            'dominant_emotion_text': sentiment.emotion_scores.dominant_emotion(),
            'dominant_emotion_acoustic': 'high_arousal' if acoustic_arousal > 0.6 else 'low_arousal',
            'voice_quality_impact': acoustic.overall_voice_quality,
            'narrative_coherence_impact': truth.narrative_coherence.overall_score
        }
        
        return MultimodalCorrelation(
            text_acoustic_emotion_correlation=text_acoustic_emotion_correlation,
            truth_acoustic_stress_correlation=truth_acoustic_stress_correlation,
            sentiment_prosody_alignment=sentiment_prosody_alignment,
            deception_multimodal_confidence=deception_multimodal_confidence,
            overall_consistency_score=overall_consistency_score,
            cross_modal_insights=cross_modal_insights
        )
    
    def generate_multimodal_insights(self, sentiment: AdvancedSentimentResult,
                                   truth: NarrativeTruthResult,
                                   acoustic: AcousticAnalysisResult,
                                   correlation: MultimodalCorrelation) -> MultimodalInsights:
        """Generate advanced insights from multimodal analysis"""
        
        # Emotional Authenticity Score
        # High when text and acoustic emotions align and narrative is coherent
        emotional_authenticity_factors = [
            correlation.text_acoustic_emotion_correlation * 0.4,
            truth.narrative_coherence.emotional_consistency * 0.3,
            (1.0 - acoustic.deception_markers.voice_quality_degradation) * 0.3
        ]
        emotional_authenticity_score = np.mean(emotional_authenticity_factors)
        
        # Cognitive Load Indicators
        # High cognitive load might indicate deception or stress
        cognitive_load_factors = [
            acoustic.stress_indicators.voice_tension * 0.3,
            acoustic.deception_markers.hesitation_markers * 0.3,
            (1.0 - truth.narrative_coherence.logical_flow) * 0.2,
            acoustic.stress_indicators.vocal_effort * 0.2
        ]
        cognitive_load_indicators = np.mean(cognitive_load_factors)
        
        # Stress-Deception Likelihood
        # Combines multiple stress and deception indicators
        stress_deception_factors = [
            acoustic.stress_indicators.stress_level * 0.25,
            acoustic.deception_markers.pitch_variability_score * 0.25,
            (1.0 - truth.truth_likelihood) * 0.25,
            truth.deception_markers.overall_deception_likelihood * 0.25
        ]
        stress_deception_likelihood = np.mean(stress_deception_factors)
        
        # Narrative-Acoustic Coherence
        # How well the narrative structure aligns with acoustic patterns
        narrative_acoustic_coherence = correlation.overall_consistency_score
        
        # Speaker Psychological State
        speaker_psychological_state = {
            'emotional_stability': 1.0 - acoustic.stress_indicators.emotional_arousal,
            'confidence_level': truth.confidence_score,
            'stress_level': acoustic.stress_indicators.stress_level,
            'authenticity': emotional_authenticity_score,
            'cognitive_clarity': 1.0 - cognitive_load_indicators,
            'emotional_valence': acoustic.emotional_state_acoustic.get('valence', 0.5),
            'voice_control': acoustic.overall_voice_quality,
            'narrative_coherence': truth.narrative_coherence.overall_score
        }
        
        # Reliability Assessment
        reliability_assessment = {
            'content_credibility': truth.truth_likelihood,
            'emotional_credibility': emotional_authenticity_score,
            'acoustic_reliability': acoustic.overall_voice_quality,
            'multimodal_consistency': correlation.overall_consistency_score,
            'deception_risk': stress_deception_likelihood,
            'overall_reliability': np.mean([
                truth.truth_likelihood * 0.3,
                emotional_authenticity_score * 0.3,
                acoustic.overall_voice_quality * 0.2,
                correlation.overall_consistency_score * 0.2
            ])
        }
        
        # Behavioral Indicators
        behavioral_indicators = []
        
        if acoustic.stress_indicators.stress_level > 0.6:
            behavioral_indicators.append("🔴 High stress levels detected in voice")
        
        if acoustic.deception_markers.hesitation_markers > 0.5:
            behavioral_indicators.append("⏸️ Significant hesitation patterns detected")
        
        if correlation.sentiment_prosody_alignment < 0.4:
            behavioral_indicators.append("⚠️ Mismatch between expressed and felt emotions")
        
        if truth.truth_likelihood < 0.4 and acoustic.deception_markers.confidence_score > 0.6:
            behavioral_indicators.append("🚨 Multiple deception indicators present")
        
        if emotional_authenticity_score > 0.7:
            behavioral_indicators.append("✅ High emotional authenticity")
        
        if cognitive_load_indicators > 0.6:
            behavioral_indicators.append("🧠 High cognitive load detected")
        
        if acoustic.stress_indicators.voice_tension > 0.5:
            behavioral_indicators.append("😤 Voice tension indicates stress or effort")
        
        if correlation.overall_consistency_score > 0.7:
            behavioral_indicators.append("🎯 High consistency across all modalities")
        
        return MultimodalInsights(
            emotional_authenticity_score=emotional_authenticity_score,
            cognitive_load_indicators=cognitive_load_indicators,
            stress_deception_likelihood=stress_deception_likelihood,
            narrative_acoustic_coherence=narrative_acoustic_coherence,
            speaker_psychological_state=speaker_psychological_state,
            reliability_assessment=reliability_assessment,
            behavioral_indicators=behavioral_indicators
        )
    
    def calculate_final_assessment(self, insights: MultimodalInsights,
                                 correlation: MultimodalCorrelation) -> Dict[str, float]:
        """Calculate final assessment scores"""
        
        final_assessment = {
            'overall_credibility': insights.reliability_assessment['overall_reliability'],
            'emotional_authenticity': insights.emotional_authenticity_score,
            'stress_level': insights.speaker_psychological_state['stress_level'],
            'deception_likelihood': insights.stress_deception_likelihood,
            'cognitive_clarity': insights.speaker_psychological_state['cognitive_clarity'],
            'multimodal_consistency': correlation.overall_consistency_score,
            'voice_quality': insights.speaker_psychological_state['voice_control'],
            'narrative_coherence': insights.speaker_psychological_state['narrative_coherence'],
            'confidence_score': insights.speaker_psychological_state['confidence_level'],
            'psychological_wellness': np.mean([
                insights.speaker_psychological_state['emotional_stability'],
                insights.speaker_psychological_state['cognitive_clarity'],
                1.0 - insights.speaker_psychological_state['stress_level']
            ])
        }
        
        return final_assessment
    
    def generate_recommendations(self, insights: MultimodalInsights,
                               assessment: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations based on multimodal analysis"""
        recommendations = []
        
        # Credibility recommendations
        if assessment['overall_credibility'] < 0.4:
            recommendations.append("🚨 Low overall credibility - requires thorough verification")
        elif assessment['overall_credibility'] > 0.7:
            recommendations.append("✅ High credibility across all modalities")
        
        # Emotional authenticity recommendations
        if assessment['emotional_authenticity'] < 0.4:
            recommendations.append("😐 Emotional expression may not be authentic")
        elif assessment['emotional_authenticity'] > 0.7:
            recommendations.append("💝 Genuine emotional expression detected")
        
        # Stress and wellness recommendations
        if assessment['stress_level'] > 0.6:
            recommendations.append("😰 High stress detected - consider supportive approach")
            if assessment['psychological_wellness'] < 0.4:
                recommendations.append("🏥 Psychological support may be beneficial")
        
        # Deception recommendations
        if assessment['deception_likelihood'] > 0.6:
            recommendations.append("🕵️ Multiple deception indicators - verify claims carefully")
            if insights.cognitive_load_indicators > 0.6:
                recommendations.append("🧠 High cognitive load suggests effortful processing")
        
        # Voice quality recommendations
        if assessment['voice_quality'] < 0.5:
            recommendations.append("🎤 Poor voice quality may affect analysis reliability")
        
        # Consistency recommendations
        if assessment['multimodal_consistency'] < 0.4:
            recommendations.append("⚠️ Inconsistencies between text and voice analysis")
        elif assessment['multimodal_consistency'] > 0.7:
            recommendations.append("🎯 High consistency across all analysis modalities")
        
        # Specific behavioral recommendations
        for indicator in insights.behavioral_indicators:
            if "High stress" in indicator:
                recommendations.append("🧘 Stress management techniques may be helpful")
            elif "Mismatch between expressed and felt emotions" in indicator:
                recommendations.append("💭 Explore underlying emotional state")
            elif "High cognitive load" in indicator:
                recommendations.append("🎯 Simplify communication or provide processing time")
        
        return recommendations
    
    def analyze_multimodal(self, text_content: str, audio_file: str) -> MultimodalAnalysisResult:
        """Perform comprehensive multimodal analysis"""
        start_time = time.time()
        
        print("🚀 Starting Multimodal Analysis")
        print("=" * 80)
        print(f"📝 Text: {text_content[:100]}...")
        print(f"🎵 Audio: {audio_file}")
        
        # Perform text-based analyses
        print("\n💭 Performing sentiment analysis...")
        sentiment_result = self.sentiment_analyzer.analyze_comprehensive(text_content)
        
        print("🔍 Performing truth analysis...")
        truth_result = self.truth_analyzer.analyze_comprehensive(text_content)
        
        # Perform acoustic analysis
        print("🎵 Performing acoustic analysis...")
        acoustic_result = self.acoustic_analyzer.analyze_audio(audio_file)
        
        # Calculate multimodal correlations
        print("🔗 Calculating multimodal correlations...")
        correlation = self.calculate_multimodal_correlations(
            sentiment_result, truth_result, acoustic_result
        )
        
        # Generate multimodal insights
        print("🧠 Generating multimodal insights...")
        insights = self.generate_multimodal_insights(
            sentiment_result, truth_result, acoustic_result, correlation
        )
        
        # Calculate final assessment
        print("📊 Calculating final assessment...")
        final_assessment = self.calculate_final_assessment(insights, correlation)
        
        # Generate recommendations
        print("💡 Generating recommendations...")
        recommendations = self.generate_recommendations(insights, final_assessment)
        
        processing_time = time.time() - start_time
        
        return MultimodalAnalysisResult(
            text_content=text_content,
            audio_file=audio_file,
            sentiment_analysis=sentiment_result,
            truth_analysis=truth_result,
            acoustic_analysis=acoustic_result,
            multimodal_correlation=correlation,
            multimodal_insights=insights,
            final_assessment=final_assessment,
            recommendations=recommendations,
            processing_time=processing_time,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def print_multimodal_summary(self, result: MultimodalAnalysisResult):
        """Print comprehensive multimodal analysis summary"""
        print("\n" + "="*80)
        print("🎯 MULTIMODAL ANALYSIS SUMMARY")
        print("="*80)
        
        # Final Assessment
        print(f"\n📊 FINAL ASSESSMENT:")
        for metric, score in result.final_assessment.items():
            if metric in ['deception_likelihood', 'stress_level']:
                status = "🔴" if score > 0.7 else "🟡" if score > 0.4 else "🟢"
            else:
                status = "🟢" if score > 0.7 else "🟡" if score > 0.4 else "🔴"
            print(f"  {status} {metric.replace('_', ' ').title()}: {score:.3f}")
        
        # Multimodal Correlations
        print(f"\n🔗 MULTIMODAL CORRELATIONS:")
        print(f"  Text-Acoustic Emotion: {result.multimodal_correlation.text_acoustic_emotion_correlation:.3f}")
        print(f"  Truth-Stress Alignment: {result.multimodal_correlation.truth_acoustic_stress_correlation:.3f}")
        print(f"  Sentiment-Prosody Match: {result.multimodal_correlation.sentiment_prosody_alignment:.3f}")
        print(f"  Overall Consistency: {result.multimodal_correlation.overall_consistency_score:.3f}")
        
        # Psychological State
        print(f"\n🧠 SPEAKER PSYCHOLOGICAL STATE:")
        for state, value in result.multimodal_insights.speaker_psychological_state.items():
            status = "🟢" if value > 0.7 else "🟡" if value > 0.4 else "🔴"
            print(f"  {status} {state.replace('_', ' ').title()}: {value:.3f}")
        
        # Behavioral Indicators
        print(f"\n🎭 BEHAVIORAL INDICATORS:")
        for i, indicator in enumerate(result.multimodal_insights.behavioral_indicators, 1):
            print(f"  {i}. {indicator}")
        
        # Key Insights
        print(f"\n🔍 KEY INSIGHTS:")
        cross_modal = result.multimodal_correlation.cross_modal_insights
        print(f"  Emotion Agreement: {'✅' if cross_modal.get('emotion_modality_agreement') else '❌'}")
        print(f"  Stress-Truth Pattern: {cross_modal.get('stress_truth_pattern', 'unknown')}")
        print(f"  Sentiment-Prosody Mismatch: {'⚠️' if cross_modal.get('sentiment_prosody_mismatch') else '✅'}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Processing Summary
        print(f"\n⏱️ PROCESSING SUMMARY:")
        print(f"  Total Time: {result.processing_time:.2f}s")
        print(f"  Sentiment Analysis: {result.sentiment_analysis.processing_time:.2f}s")
        print(f"  Truth Analysis: {result.truth_analysis.processing_time:.2f}s")
        print(f"  Acoustic Analysis: {result.acoustic_analysis.processing_time:.2f}s")
        print(f"  Model Used: {result.sentiment_analysis.model_used}")

def main():
    """Test the multimodal analysis system"""
    # Check for command line arguments
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        if not os.path.exists(audio_file):
            print(f"❌ Audio file not found: {audio_file}")
            return
        print(f"🎵 Using specified audio file: {audio_file}")
    else:
        # Fallback to checking for default audio files
        audio_files = [
            "test_audio_converted.wav",
            "250825-1107_OugfC4aY.mp3",
            "250825_1107.mp3",
            "test_audio.wav"
        ]
        
        audio_file = None
        for file in audio_files:
            if os.path.exists(file):
                audio_file = file
                break
        
        if not audio_file:
            print("❌ No audio file found for multimodal analysis")
            print("Usage: python multimodal_analysis_system.py <audio_file>")
            return
        print(f"🎵 Using default audio file: {audio_file}")
    
    # Sample Arabic text (this would normally come from transcription)
    sample_text = """
    شكراً لكم. بعد ما أعرف، لا لا، ما عادي، ما عندي شي ما أخبرتك به، ولكن لدي يوم نيئ عندما أرى بناتي، إن شاء الله، والله إن شاء الله رحمة الله عز وجل. لا لا، لم أتواصل معهم، لا أعرف كل شيء، فقط أخبرتني أنني سأرى بناتي قبل التنفيذ.
    """
    
    # Initialize system
    system = MultimodalAnalysisSystem()
    
    # Perform multimodal analysis
    result = system.analyze_multimodal(sample_text, audio_file)
    
    # Print summary
    system.print_multimodal_summary(result)
    
    # Save detailed results
    timestamp = int(time.time())
    results_file = f"multimodal_analysis_results_{timestamp}.json"
    
    # Convert result to dict for JSON serialization
    def convert_to_json_serializable(obj):
        """Convert objects to JSON serializable format"""
        if isinstance(obj, dict):
            return {k: convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (bool, np.bool_)):
            return bool(obj)
        elif hasattr(obj, '__dict__'):
            return convert_to_json_serializable(obj.__dict__)
        else:
            return obj
    
    # Create a simplified result dict to avoid complex nested objects
    result_dict = {
        'text_content': result.text_content,
        'audio_file': result.audio_file,
        'final_assessment': result.final_assessment,
        'recommendations': result.recommendations,
        'processing_time': result.processing_time,
        'analysis_timestamp': result.analysis_timestamp,
        'summary': {
            'overall_sentiment': result.sentiment_analysis.overall_sentiment,
            'sentiment_confidence': result.sentiment_analysis.sentiment_confidence,
            'truth_likelihood': result.truth_analysis.truth_likelihood,
            'truth_confidence': result.truth_analysis.confidence_score,
            'voice_quality': result.acoustic_analysis.overall_voice_quality,
            'stress_level': result.acoustic_analysis.stress_indicators.stress_level,
            'deception_likelihood': result.multimodal_insights.stress_deception_likelihood,
            'emotional_authenticity': result.multimodal_insights.emotional_authenticity_score,
            'multimodal_consistency': result.multimodal_correlation.overall_consistency_score
        }
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(convert_to_json_serializable(result_dict), f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")

if __name__ == "__main__":
    main()