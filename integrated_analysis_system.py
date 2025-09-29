#!/usr/bin/env python3
"""
Integrated Advanced Analysis System
Combines sentiment analysis, attention mechanisms, and narrative truth detection
Primary Model: Aya 35B for enhanced Arabic understanding
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our custom analyzers
from advanced_sentiment_analyzer import AdvancedArabicSentimentAnalyzer, AdvancedSentimentResult
from narrative_truth_analyzer import NarrativeTruthAnalyzer, NarrativeTruthResult

@dataclass
class IntegratedAnalysisResult:
    """Complete integrated analysis result"""
    text: str
    sentiment_analysis: AdvancedSentimentResult
    truth_analysis: NarrativeTruthResult
    combined_insights: Dict[str, Any]
    overall_assessment: Dict[str, float]
    recommendations: List[str]
    processing_time: float
    analysis_timestamp: str

class IntegratedAnalysisSystem:
    """Integrated system combining sentiment and truth analysis"""
    
    def __init__(self, primary_model: str = "aya:35b-23-q4_K_M"):
        self.primary_model = primary_model
        self.sentiment_analyzer = AdvancedArabicSentimentAnalyzer(primary_model)
        self.truth_analyzer = NarrativeTruthAnalyzer(primary_model)
    
    def generate_combined_insights(self, sentiment_result: AdvancedSentimentResult, 
                                 truth_result: NarrativeTruthResult) -> Dict[str, Any]:
        """Generate combined insights from both analyses"""
        insights = {}
        
        # Emotional-Truth Correlation
        emotional_intensity = sentiment_result.emotion_scores.emotional_intensity()
        truth_likelihood = truth_result.truth_likelihood
        
        # High emotion + low truth might indicate deception or distress
        # Low emotion + high truth might indicate factual reporting
        # High emotion + high truth might indicate genuine emotional experience
        
        if emotional_intensity > 0.6 and truth_likelihood < 0.4:
            emotional_truth_pattern = "high_emotion_low_truth"
            pattern_interpretation = "Possible emotional manipulation or deceptive content"
        elif emotional_intensity < 0.3 and truth_likelihood > 0.7:
            emotional_truth_pattern = "low_emotion_high_truth"
            pattern_interpretation = "Likely factual, objective reporting"
        elif emotional_intensity > 0.6 and truth_likelihood > 0.6:
            emotional_truth_pattern = "high_emotion_high_truth"
            pattern_interpretation = "Genuine emotional experience with truthful content"
        elif emotional_intensity < 0.3 and truth_likelihood < 0.4:
            emotional_truth_pattern = "low_emotion_low_truth"
            pattern_interpretation = "Possible disengagement or uncertain content"
        else:
            emotional_truth_pattern = "moderate_mixed"
            pattern_interpretation = "Mixed emotional and truth indicators"
        
        insights['emotional_truth_pattern'] = {
            'pattern': emotional_truth_pattern,
            'interpretation': pattern_interpretation,
            'emotional_intensity': emotional_intensity,
            'truth_likelihood': truth_likelihood
        }
        
        # Attention-Truth Correlation
        top_attention = sentiment_result.attention_weights[0] if sentiment_result.attention_weights else None
        if top_attention:
            # Check if high-attention content aligns with truth indicators
            high_attention_text = top_attention.text
            truth_indicators_in_attention = sum(1 for indicator in truth_result.truth_indicators 
                                              if indicator.text in high_attention_text)
            
            insights['attention_truth_alignment'] = {
                'high_attention_text': high_attention_text,
                'truth_indicators_count': truth_indicators_in_attention,
                'attention_weight': top_attention.weight,
                'alignment_score': truth_indicators_in_attention / max(len(truth_result.truth_indicators), 1)
            }
        
        # Narrative Coherence vs Emotional Trajectory
        narrative_coherence = truth_result.narrative_coherence.overall_score
        emotional_trajectory = sentiment_result.emotional_trajectory
        
        if emotional_trajectory:
            # Calculate emotional stability (low variance = stable)
            emotion_values = [point[1] for point in emotional_trajectory]
            emotion_variance = sum((x - sum(emotion_values)/len(emotion_values))**2 
                                 for x in emotion_values) / len(emotion_values) if emotion_values else 0
            emotional_stability = max(0, 1 - emotion_variance)
            
            insights['coherence_stability_correlation'] = {
                'narrative_coherence': narrative_coherence,
                'emotional_stability': emotional_stability,
                'correlation_strength': abs(narrative_coherence - emotional_stability),
                'interpretation': "High correlation suggests authentic narrative" if 
                                abs(narrative_coherence - emotional_stability) < 0.3 else 
                                "Low correlation may indicate inconsistencies"
            }
        
        # Key Phrases vs Truth Indicators
        key_phrases = sentiment_result.key_phrases
        truth_phrases = [indicator.text for indicator in truth_result.truth_indicators]
        
        phrase_overlap = len(set(key_phrases) & set(truth_phrases))
        insights['phrase_truth_overlap'] = {
            'key_phrases': key_phrases,
            'truth_phrases': truth_phrases,
            'overlap_count': phrase_overlap,
            'overlap_ratio': phrase_overlap / max(len(key_phrases), 1)
        }
        
        return insights
    
    def calculate_overall_assessment(self, sentiment_result: AdvancedSentimentResult,
                                   truth_result: NarrativeTruthResult,
                                   combined_insights: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall assessment scores"""
        assessment = {}
        
        # Credibility Score (0-1)
        credibility_factors = [
            truth_result.truth_likelihood * 0.4,
            truth_result.narrative_coherence.overall_score * 0.3,
            (1 - truth_result.deception_markers.overall_deception_likelihood) * 0.3
        ]
        assessment['credibility'] = sum(credibility_factors)
        
        # Emotional Authenticity (0-1)
        emotional_consistency = truth_result.narrative_coherence.emotional_consistency
        emotional_intensity = sentiment_result.emotion_scores.emotional_intensity()
        sentiment_confidence = sentiment_result.sentiment_confidence
        
        authenticity_factors = [
            emotional_consistency * 0.4,
            min(emotional_intensity, 0.8) * 0.3,  # Cap intensity to avoid over-weighting
            sentiment_confidence * 0.3
        ]
        assessment['emotional_authenticity'] = sum(authenticity_factors)
        
        # Narrative Quality (0-1)
        narrative_factors = [
            truth_result.narrative_coherence.overall_score * 0.5,
            truth_result.narrative_coherence.logical_flow * 0.3,
            truth_result.narrative_coherence.detail_consistency * 0.2
        ]
        assessment['narrative_quality'] = sum(narrative_factors)
        
        # Overall Reliability (0-1)
        reliability_factors = [
            assessment['credibility'] * 0.4,
            assessment['emotional_authenticity'] * 0.3,
            assessment['narrative_quality'] * 0.3
        ]
        assessment['overall_reliability'] = sum(reliability_factors)
        
        # Attention Relevance (0-1)
        if sentiment_result.attention_weights:
            avg_attention_weight = sum(aw.weight for aw in sentiment_result.attention_weights) / len(sentiment_result.attention_weights)
            avg_context_relevance = sum(aw.context_relevance for aw in sentiment_result.attention_weights) / len(sentiment_result.attention_weights)
            assessment['attention_relevance'] = (avg_attention_weight + avg_context_relevance) / 2
        else:
            assessment['attention_relevance'] = 0.0
        
        return assessment
    
    def generate_recommendations(self, sentiment_result: AdvancedSentimentResult,
                               truth_result: NarrativeTruthResult,
                               assessment: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Credibility recommendations
        if assessment['credibility'] < 0.4:
            recommendations.append("⚠️ Low credibility detected. Verify facts and cross-reference sources.")
            if truth_result.deception_markers.defensive_language > 0.3:
                recommendations.append("🛡️ Defensive language patterns detected. Consider additional verification.")
        elif assessment['credibility'] > 0.7:
            recommendations.append("✅ High credibility indicators. Content appears trustworthy.")
        
        # Emotional authenticity recommendations
        if assessment['emotional_authenticity'] < 0.4:
            recommendations.append("😐 Low emotional authenticity. Content may lack genuine emotional expression.")
        elif assessment['emotional_authenticity'] > 0.7:
            recommendations.append("💝 High emotional authenticity. Genuine emotional content detected.")
        
        # Narrative quality recommendations
        if assessment['narrative_quality'] < 0.4:
            recommendations.append("📝 Poor narrative structure. Content lacks coherence and logical flow.")
            if truth_result.narrative_coherence.logical_flow < 0.3:
                recommendations.append("🔗 Add logical connectors to improve narrative flow.")
        elif assessment['narrative_quality'] > 0.7:
            recommendations.append("📖 Well-structured narrative with good coherence and flow.")
        
        # Attention recommendations
        if assessment['attention_relevance'] < 0.4:
            recommendations.append("🎯 Low attention relevance. Key content may not be emphasized effectively.")
        elif assessment['attention_relevance'] > 0.7:
            recommendations.append("🌟 High attention relevance. Key points are well-emphasized.")
        
        # Overall reliability recommendations
        if assessment['overall_reliability'] < 0.4:
            recommendations.append("🚨 Overall low reliability. Exercise caution and seek additional verification.")
        elif assessment['overall_reliability'] > 0.7:
            recommendations.append("🏆 High overall reliability. Content appears credible and well-structured.")
        
        # Specific pattern recommendations
        dominant_emotion = sentiment_result.emotion_scores.dominant_emotion()
        if dominant_emotion in ['sadness', 'fear'] and assessment['credibility'] > 0.6:
            recommendations.append("💙 Genuine distress detected. Consider providing support or assistance.")
        elif dominant_emotion == 'anger' and truth_result.deception_markers.emotional_inconsistency > 0.5:
            recommendations.append("🔥 Anger with emotional inconsistency. Verify claims carefully.")
        
        return recommendations
    
    def analyze_comprehensive(self, text: str) -> IntegratedAnalysisResult:
        """Perform comprehensive integrated analysis"""
        start_time = time.time()
        
        print("🚀 Starting Integrated Advanced Analysis")
        print("=" * 80)
        
        # Perform sentiment analysis
        print("💭 Performing advanced sentiment analysis...")
        sentiment_result = self.sentiment_analyzer.analyze_comprehensive(text)
        
        # Perform truth analysis
        print("🔍 Performing narrative truth analysis...")
        truth_result = self.truth_analyzer.analyze_comprehensive(text)
        
        # Generate combined insights
        print("🧠 Generating combined insights...")
        combined_insights = self.generate_combined_insights(sentiment_result, truth_result)
        
        # Calculate overall assessment
        print("📊 Calculating overall assessment...")
        overall_assessment = self.calculate_overall_assessment(sentiment_result, truth_result, combined_insights)
        
        # Generate recommendations
        print("💡 Generating recommendations...")
        recommendations = self.generate_recommendations(sentiment_result, truth_result, overall_assessment)
        
        processing_time = time.time() - start_time
        
        return IntegratedAnalysisResult(
            text=text,
            sentiment_analysis=sentiment_result,
            truth_analysis=truth_result,
            combined_insights=combined_insights,
            overall_assessment=overall_assessment,
            recommendations=recommendations,
            processing_time=processing_time,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def print_analysis_summary(self, result: IntegratedAnalysisResult):
        """Print a comprehensive analysis summary"""
        print("\n" + "="*80)
        print("📋 INTEGRATED ANALYSIS SUMMARY")
        print("="*80)
        
        # Overall Assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        for metric, score in result.overall_assessment.items():
            status = "🟢" if score > 0.7 else "🟡" if score > 0.4 else "🔴"
            print(f"  {status} {metric.replace('_', ' ').title()}: {score:.3f}")
        
        # Key Insights
        print(f"\n🧠 KEY INSIGHTS:")
        emotional_truth = result.combined_insights.get('emotional_truth_pattern', {})
        print(f"  Pattern: {emotional_truth.get('pattern', 'unknown')}")
        print(f"  Interpretation: {emotional_truth.get('interpretation', 'N/A')}")
        
        # Sentiment Summary
        print(f"\n💭 SENTIMENT ANALYSIS:")
        print(f"  Overall Sentiment: {result.sentiment_analysis.overall_sentiment}")
        print(f"  Dominant Emotion: {result.sentiment_analysis.emotion_scores.dominant_emotion()}")
        print(f"  Emotional Intensity: {result.sentiment_analysis.emotion_scores.emotional_intensity():.3f}")
        
        # Truth Analysis Summary
        print(f"\n🔍 TRUTH ANALYSIS:")
        print(f"  Truth Likelihood: {result.truth_analysis.truth_likelihood:.3f}")
        print(f"  Narrative Coherence: {result.truth_analysis.narrative_coherence.overall_score:.3f}")
        print(f"  Deception Likelihood: {result.truth_analysis.deception_markers.overall_deception_likelihood:.3f}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")
        
        print(f"\n⏱️  Total Processing Time: {result.processing_time:.2f}s")
        print(f"🤖 Model Used: {result.sentiment_analysis.model_used}")

def main():
    """Test the integrated analysis system"""
    # Sample Arabic text for testing
    sample_text = """
    شكراً لكم. بعد ما أعرف، لا لا، ما عادي، ما عندي شي ما أخبرتك به، ولكن لدي يوم نيئ عندما أرى بناتي، إن شاء الله، والله إن شاء الله رحمة الله عز وجل. لا لا، لم أتواصل معهم، لا أعرف كل شيء، فقط أخبرتني أنني سأرى بناتي قبل التنفيذ.
    """
    
    # Initialize the integrated system
    system = IntegratedAnalysisSystem()
    
    # Perform comprehensive analysis
    result = system.analyze_comprehensive(sample_text)
    
    # Print summary
    system.print_analysis_summary(result)
    
    # Save detailed results
    timestamp = int(time.time())
    results_file = f"integrated_analysis_results_{timestamp}.json"
    
    # Convert result to dict for JSON serialization
    result_dict = {
        'text': result.text,
        'sentiment_analysis': {
            'overall_sentiment': result.sentiment_analysis.overall_sentiment,
            'sentiment_confidence': result.sentiment_analysis.sentiment_confidence,
            'emotion_scores': asdict(result.sentiment_analysis.emotion_scores),
            'attention_weights': [asdict(aw) for aw in result.sentiment_analysis.attention_weights],
            'narrative_analysis': asdict(result.sentiment_analysis.narrative_analysis),
            'key_phrases': result.sentiment_analysis.key_phrases,
            'emotional_trajectory': result.sentiment_analysis.emotional_trajectory,
            'linguistic_patterns': result.sentiment_analysis.linguistic_patterns,
            'processing_time': result.sentiment_analysis.processing_time,
            'model_used': result.sentiment_analysis.model_used
        },
        'truth_analysis': {
            'truth_likelihood': result.truth_analysis.truth_likelihood,
            'confidence_score': result.truth_analysis.confidence_score,
            'narrative_coherence': asdict(result.truth_analysis.narrative_coherence),
            'deception_markers': asdict(result.truth_analysis.deception_markers),
            'truth_indicators': [asdict(ti) for ti in result.truth_analysis.truth_indicators],
            'credibility_factors': result.truth_analysis.credibility_factors,
            'analysis_summary': result.truth_analysis.analysis_summary,
            'processing_time': result.truth_analysis.processing_time
        },
        'combined_insights': result.combined_insights,
        'overall_assessment': result.overall_assessment,
        'recommendations': result.recommendations,
        'processing_time': result.processing_time,
        'analysis_timestamp': result.analysis_timestamp
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")

if __name__ == "__main__":
    main()