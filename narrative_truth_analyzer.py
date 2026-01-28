#!/usr/bin/env python3
"""
Narrative Truth Analysis Module
Advanced truth detection and narrative coherence analysis for Arabic text
Integrates with the Advanced Sentiment Analyzer
"""

import re
import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import ollama

@dataclass
class TruthIndicator:
    """Individual truth indicator analysis"""
    indicator_type: str  # certainty, uncertainty, temporal, contradiction
    text: str
    position: int
    confidence: float
    impact_score: float

@dataclass
class NarrativeCoherence:
    """Detailed narrative coherence analysis"""
    overall_score: float
    temporal_consistency: float
    logical_flow: float
    detail_consistency: float
    emotional_consistency: float
    contradictions: List[str]
    supporting_evidence: List[str]

@dataclass
class DeceptionMarkers:
    """Deception detection markers"""
    linguistic_complexity: float
    detail_overload: float
    emotional_inconsistency: float
    temporal_vagueness: float
    defensive_language: float
    overall_deception_likelihood: float

@dataclass
class NarrativeTruthResult:
    """Complete narrative truth analysis result"""
    text: str
    truth_likelihood: float
    confidence_score: float
    narrative_coherence: NarrativeCoherence
    deception_markers: DeceptionMarkers
    truth_indicators: List[TruthIndicator]
    credibility_factors: Dict[str, float]
    analysis_summary: str
    processing_time: float

class NarrativeTruthAnalyzer:
    """Advanced narrative truth and coherence analyzer"""
    
    def __init__(self, model_name: str = "aya:8b"):
        self.model_name = model_name
        
        # Arabic truth/deception linguistic patterns
        self.truth_patterns = {
            'high_certainty': [
                'بالتأكيد', 'قطعاً', 'يقيناً', 'حتماً', 'لا شك', 'بلا ريب',
                'أؤكد لك', 'أقسم', 'والله', 'بالله', 'أشهد'
            ],
            'medium_certainty': [
                'أعتقد', 'أظن', 'في رأيي', 'حسب علمي', 'على ما أذكر',
                'إذا لم أكن مخطئاً', 'على الأرجح'
            ],
            'uncertainty': [
                'ربما', 'قد', 'لعل', 'عسى', 'يمكن', 'محتمل', 'لست متأكداً',
                'لا أدري', 'لا أعرف بالضبط', 'تقريباً', 'حوالي'
            ],
            'temporal_precision': [
                'في الساعة', 'يوم', 'شهر', 'سنة', 'صباحاً', 'مساءً',
                'الأمس', 'اليوم', 'غداً', 'الآن', 'حالياً'
            ],
            'temporal_vague': [
                'منذ فترة', 'قبل مدة', 'في وقت ما', 'ذات مرة', 'في الماضي',
                'مؤخراً', 'قريباً', 'لاحقاً', 'بعد ذلك'
            ],
            'defensive': [
                'لماذا أكذب', 'أقول الحقيقة', 'صدقني', 'ثق بي', 'أقسم لك',
                'لا أخفي شيئاً', 'بصراحة', 'بكل صدق'
            ],
            'contradictory': [
                'لكن', 'غير أن', 'إلا أن', 'بيد أن', 'مع ذلك', 'رغم ذلك',
                'على العكس', 'بالعكس', 'في الواقع', 'الحقيقة أن'
            ]
        }
        
        # Emotional consistency markers
        self.emotional_markers = {
            'positive': ['فرح', 'سعادة', 'بهجة', 'حب', 'إعجاب', 'رضا'],
            'negative': ['حزن', 'غضب', 'خوف', 'قلق', 'استياء', 'كراهية'],
            'neutral': ['عادي', 'طبيعي', 'مقبول', 'لا بأس', 'معقول']
        }
    
    def extract_truth_indicators(self, text: str) -> List[TruthIndicator]:
        """Extract and analyze truth indicators from text"""
        indicators = []
        words = text.split()
        
        for category, patterns in self.truth_patterns.items():
            for pattern in patterns:
                matches = [(m.start(), m.end()) for m in re.finditer(re.escape(pattern), text)]
                
                for start, end in matches:
                    # Calculate position in text (0-1)
                    position = start / len(text) if len(text) > 0 else 0
                    
                    # Calculate confidence based on pattern strength
                    confidence_map = {
                        'high_certainty': 0.9,
                        'medium_certainty': 0.6,
                        'uncertainty': 0.3,
                        'temporal_precision': 0.8,
                        'temporal_vague': 0.2,
                        'defensive': 0.1,  # Defensive language reduces credibility
                        'contradictory': 0.2
                    }
                    confidence = confidence_map.get(category, 0.5)
                    
                    # Calculate impact score based on context
                    surrounding_text = text[max(0, start-50):min(len(text), end+50)]
                    impact_score = min(len(surrounding_text.split()) / 20, 1.0)
                    
                    indicators.append(TruthIndicator(
                        indicator_type=category,
                        text=pattern,
                        position=position,
                        confidence=confidence,
                        impact_score=impact_score
                    ))
        
        return indicators
    
    def analyze_temporal_consistency(self, text: str) -> float:
        """Analyze temporal consistency in the narrative"""
        # Extract temporal markers
        precise_temporal = sum(1 for pattern in self.truth_patterns['temporal_precision'] 
                              if pattern in text)
        vague_temporal = sum(1 for pattern in self.truth_patterns['temporal_vague'] 
                            if pattern in text)
        
        total_temporal = precise_temporal + vague_temporal
        if total_temporal == 0:
            return 0.5  # Neutral if no temporal markers
        
        # Higher precision indicates better consistency
        consistency = precise_temporal / total_temporal
        return consistency
    
    def analyze_emotional_consistency(self, text: str) -> float:
        """Analyze emotional consistency throughout the text"""
        sentences = re.split(r'[.!?؟]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 1.0  # Single sentence is consistent by default
        
        sentence_emotions = []
        
        for sentence in sentences:
            pos_count = sum(1 for word in self.emotional_markers['positive'] if word in sentence)
            neg_count = sum(1 for word in self.emotional_markers['negative'] if word in sentence)
            neu_count = sum(1 for word in self.emotional_markers['neutral'] if word in sentence)
            
            total = pos_count + neg_count + neu_count
            if total > 0:
                emotion_vector = (pos_count/total, neg_count/total, neu_count/total)
            else:
                emotion_vector = (0.33, 0.33, 0.33)  # Neutral
            
            sentence_emotions.append(emotion_vector)
        
        # Calculate consistency as inverse of emotional variance
        if len(sentence_emotions) < 2:
            return 1.0
        
        # Calculate average emotional distance between consecutive sentences
        distances = []
        for i in range(len(sentence_emotions) - 1):
            distance = math.sqrt(sum((a - b) ** 2 for a, b in 
                                   zip(sentence_emotions[i], sentence_emotions[i+1])))
            distances.append(distance)
        
        avg_distance = sum(distances) / len(distances) if distances else 0
        consistency = max(0, 1 - avg_distance)  # Convert distance to consistency
        
        return consistency
    
    def analyze_detail_consistency(self, text: str) -> Tuple[float, float]:
        """Analyze detail consistency and detect overload"""
        words = text.split()
        sentences = re.split(r'[.!?؟]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Calculate detail density
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Detect specific details (numbers, names, places, times)
        detail_patterns = [
            r'\d+',  # Numbers
            r'[A-Z][a-z]+',  # Proper nouns (simplified)
            r'في\s+\w+',  # Location markers
            r'الساعة\s+\d+',  # Time markers
        ]
        
        detail_count = sum(len(re.findall(pattern, text)) for pattern in detail_patterns)
        detail_density = detail_count / len(words) if words else 0
        
        # Normal detail density is around 0.1-0.3
        # Too high (>0.5) might indicate overcompensation/deception
        # Too low (<0.05) might indicate vagueness
        
        if detail_density > 0.5:
            detail_overload = min((detail_density - 0.5) * 2, 1.0)
            consistency = max(0, 1 - detail_overload)
        elif detail_density < 0.05:
            consistency = detail_density * 10  # Scale up low values
        else:
            consistency = 1.0  # Normal range
        
        return consistency, detail_density
    
    def calculate_linguistic_complexity(self, text: str) -> float:
        """Calculate linguistic complexity as potential deception indicator"""
        words = text.split()
        sentences = re.split(r'[.!?؟]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not words or not sentences:
            return 0.0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Subordinate clauses (approximated by conjunctions)
        subordinate_markers = ['الذي', 'التي', 'حيث', 'عندما', 'لأن', 'كي', 'لكي']
        subordinate_count = sum(1 for marker in subordinate_markers if marker in text)
        subordinate_density = subordinate_count / len(sentences)
        
        # Normalize complexity score (0-1)
        word_complexity = min(avg_word_length / 8, 1.0)  # 8 chars is high for Arabic
        sentence_complexity = min(avg_sentence_length / 20, 1.0)  # 20 words is complex
        structure_complexity = min(subordinate_density, 1.0)
        
        overall_complexity = (word_complexity + sentence_complexity + structure_complexity) / 3
        
        return overall_complexity
    
    def analyze_narrative_coherence(self, text: str) -> NarrativeCoherence:
        """Comprehensive narrative coherence analysis"""
        # Temporal consistency
        temporal_consistency = self.analyze_temporal_consistency(text)
        
        # Emotional consistency
        emotional_consistency = self.analyze_emotional_consistency(text)
        
        # Detail consistency
        detail_consistency, detail_density = self.analyze_detail_consistency(text)
        
        # Logical flow (based on connectors and transitions)
        logical_connectors = ['لذلك', 'إذن', 'بالتالي', 'نتيجة لذلك', 'من ثم', 'وبعد ذلك']
        connector_count = sum(1 for connector in logical_connectors if connector in text)
        sentences = re.split(r'[.!?؟]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        logical_flow = min(connector_count / max(len(sentences) - 1, 1), 1.0)
        
        # Find contradictions
        contradictions = [pattern for pattern in self.truth_patterns['contradictory'] 
                         if pattern in text]
        
        # Find supporting evidence
        supporting_evidence = [pattern for pattern in self.truth_patterns['high_certainty'] 
                              if pattern in text]
        
        # Overall coherence score
        overall_score = (temporal_consistency * 0.25 + 
                        emotional_consistency * 0.25 + 
                        detail_consistency * 0.25 + 
                        logical_flow * 0.25)
        
        return NarrativeCoherence(
            overall_score=overall_score,
            temporal_consistency=temporal_consistency,
            logical_flow=logical_flow,
            detail_consistency=detail_consistency,
            emotional_consistency=emotional_consistency,
            contradictions=contradictions,
            supporting_evidence=supporting_evidence
        )
    
    def analyze_deception_markers(self, text: str, coherence: NarrativeCoherence) -> DeceptionMarkers:
        """Analyze potential deception markers"""
        # Linguistic complexity
        linguistic_complexity = self.calculate_linguistic_complexity(text)
        
        # Detail overload
        _, detail_density = self.analyze_detail_consistency(text)
        detail_overload = max(0, min((detail_density - 0.3) * 2, 1.0))
        
        # Emotional inconsistency (inverse of consistency)
        emotional_inconsistency = 1 - coherence.emotional_consistency
        
        # Temporal vagueness
        vague_temporal = sum(1 for pattern in self.truth_patterns['temporal_vague'] 
                            if pattern in text)
        precise_temporal = sum(1 for pattern in self.truth_patterns['temporal_precision'] 
                              if pattern in text)
        total_temporal = vague_temporal + precise_temporal
        temporal_vagueness = vague_temporal / max(total_temporal, 1)
        
        # Defensive language
        defensive_count = sum(1 for pattern in self.truth_patterns['defensive'] 
                             if pattern in text)
        words = text.split()
        defensive_language = min(defensive_count / max(len(words) / 20, 1), 1.0)
        
        # Overall deception likelihood
        deception_factors = [
            linguistic_complexity * 0.15,
            detail_overload * 0.25,
            emotional_inconsistency * 0.25,
            temporal_vagueness * 0.20,
            defensive_language * 0.15
        ]
        
        overall_deception_likelihood = sum(deception_factors)
        
        return DeceptionMarkers(
            linguistic_complexity=linguistic_complexity,
            detail_overload=detail_overload,
            emotional_inconsistency=emotional_inconsistency,
            temporal_vagueness=temporal_vagueness,
            defensive_language=defensive_language,
            overall_deception_likelihood=overall_deception_likelihood
        )
    
    def generate_llm_analysis(self, text: str) -> str:
        """Generate LLM-based narrative truth analysis"""
        try:
            prompt = f"""أنت خبير في تحليل صدق النصوص والسرد العربي. قم بتحليل النص التالي من ناحية الصدق والتماسك السردي:

النص:
{text}

المطلوب تحليل شامل يتضمن:

1. مؤشرات الصدق:
   - مستوى اليقين في الكلام
   - التماسك الزمني
   - التفاصيل المنطقية

2. مؤشرات عدم الصدق المحتملة:
   - التناقضات
   - الغموض المتعمد
   - الإفراط في التفاصيل
   - اللغة الدفاعية

3. التقييم العام:
   - احتمالية الصدق (من 0 إلى 1)
   - مستوى الثقة في التحليل
   - التوصيات

قدم تحليلاً مفصلاً باللغة العربية."""

            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': 0.2,
                    'top_p': 0.8,
                    'max_tokens': 1024
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            return f"خطأ في التحليل: {str(e)}"
    
    def analyze_comprehensive(self, text: str) -> NarrativeTruthResult:
        """Perform comprehensive narrative truth analysis"""
        import time
        start_time = time.time()
        
        # Extract truth indicators
        truth_indicators = self.extract_truth_indicators(text)
        
        # Analyze narrative coherence
        narrative_coherence = self.analyze_narrative_coherence(text)
        
        # Analyze deception markers
        deception_markers = self.analyze_deception_markers(text, narrative_coherence)
        
        # Calculate overall truth likelihood
        # Combine coherence score with deception likelihood (inverse)
        truth_likelihood = (narrative_coherence.overall_score * 0.6 + 
                           (1 - deception_markers.overall_deception_likelihood) * 0.4)
        
        # Calculate confidence based on amount of evidence
        evidence_count = len(truth_indicators)
        confidence_score = min(evidence_count / 10, 1.0)  # More indicators = higher confidence
        
        # Calculate credibility factors
        credibility_factors = {
            'temporal_consistency': narrative_coherence.temporal_consistency,
            'emotional_consistency': narrative_coherence.emotional_consistency,
            'detail_consistency': narrative_coherence.detail_consistency,
            'logical_flow': narrative_coherence.logical_flow,
            'linguistic_naturalness': 1 - deception_markers.linguistic_complexity,
            'defensive_language_absence': 1 - deception_markers.defensive_language
        }
        
        # Generate LLM analysis summary
        analysis_summary = self.generate_llm_analysis(text)
        
        processing_time = time.time() - start_time
        
        return NarrativeTruthResult(
            text=text,
            truth_likelihood=truth_likelihood,
            confidence_score=confidence_score,
            narrative_coherence=narrative_coherence,
            deception_markers=deception_markers,
            truth_indicators=truth_indicators,
            credibility_factors=credibility_factors,
            analysis_summary=analysis_summary,
            processing_time=processing_time
        )

def main():
    """Test the narrative truth analyzer"""
    # Sample Arabic text for testing
    sample_text = """
    شكراً لكم. بعد ما أعرف، لا لا، ما عادي، ما عندي شي ما أخبرتك به، ولكن لدي يوم نيئ عندما أرى بناتي، إن شاء الله، والله إن شاء الله رحمة الله عز وجل. لا لا، لم أتواصل معهم، لا أعرف كل شيء، فقط أخبرتني أنني سأرى بناتي قبل التنفيذ.
    """
    
    analyzer = NarrativeTruthAnalyzer()
    
    print("🔍 Starting Narrative Truth Analysis")
    print("=" * 80)
    
    result = analyzer.analyze_comprehensive(sample_text)
    
    print("\n📊 NARRATIVE TRUTH ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Truth Likelihood: {result.truth_likelihood:.3f}")
    print(f"Confidence Score: {result.confidence_score:.3f}")
    print(f"Overall Coherence: {result.narrative_coherence.overall_score:.3f}")
    print(f"Deception Likelihood: {result.deception_markers.overall_deception_likelihood:.3f}")
    print(f"Processing Time: {result.processing_time:.2f}s")
    
    print(f"\n🎯 CREDIBILITY FACTORS:")
    for factor, score in result.credibility_factors.items():
        print(f"  {factor}: {score:.3f}")
    
    print(f"\n⚠️  TRUTH INDICATORS FOUND: {len(result.truth_indicators)}")
    for indicator in result.truth_indicators[:5]:  # Show top 5
        print(f"  {indicator.indicator_type}: '{indicator.text}' (confidence: {indicator.confidence:.2f})")
    
    # Save results
    import json
    import time
    timestamp = int(time.time())
    results_file = f"narrative_truth_analysis_{timestamp}.json"
    
    result_dict = {
        'text': result.text,
        'truth_likelihood': result.truth_likelihood,
        'confidence_score': result.confidence_score,
        'narrative_coherence': asdict(result.narrative_coherence),
        'deception_markers': asdict(result.deception_markers),
        'truth_indicators': [asdict(ti) for ti in result.truth_indicators],
        'credibility_factors': result.credibility_factors,
        'analysis_summary': result.analysis_summary,
        'processing_time': result.processing_time,
        'analysis_timestamp': time.time()
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")

if __name__ == "__main__":
    main()