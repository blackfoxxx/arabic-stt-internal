#!/usr/bin/env python3
"""
Advanced Sentiment Analysis Framework for Arabic Text
Features: Attention Analysis, Narrative Truth Detection, Deep Emotional Analysis
Primary Model: Aya 35B for enhanced Arabic understanding
"""

import os
import sys
import json
import time
import re
import ollama
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import math

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

@dataclass
class EmotionScore:
    """Detailed emotion scoring"""
    joy: float = 0.0
    sadness: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    surprise: float = 0.0
    disgust: float = 0.0
    trust: float = 0.0
    anticipation: float = 0.0
    
    def dominant_emotion(self) -> str:
        """Get the dominant emotion"""
        emotions = asdict(self)
        return max(emotions.keys(), key=lambda k: emotions[k])
    
    def emotional_intensity(self) -> float:
        """Calculate overall emotional intensity"""
        return sum(asdict(self).values()) / len(asdict(self))

@dataclass
class AttentionWeight:
    """Attention weight for text segments"""
    text: str
    weight: float
    position: int
    context_relevance: float
    emotional_impact: float

@dataclass
class NarrativeAnalysis:
    """Narrative structure and truth analysis"""
    coherence_score: float
    consistency_score: float
    truth_likelihood: float
    narrative_flow: str  # linear, circular, fragmented
    temporal_markers: List[str]
    contradiction_indicators: List[str]
    certainty_markers: List[str]
    uncertainty_markers: List[str]

@dataclass
class AdvancedSentimentResult:
    """Comprehensive sentiment analysis result"""
    text: str
    overall_sentiment: str
    sentiment_confidence: float
    emotion_scores: EmotionScore
    attention_weights: List[AttentionWeight]
    narrative_analysis: NarrativeAnalysis
    key_phrases: List[str]
    emotional_trajectory: List[Tuple[int, float]]  # (position, sentiment_score)
    linguistic_patterns: Dict[str, Any]
    processing_time: float
    model_used: str

class AdvancedArabicSentimentAnalyzer:
    """Advanced sentiment analyzer with deep analysis capabilities"""
    
    def __init__(self, primary_model: str = "aya:8b"):
        self.primary_model = primary_model
        self.fallback_models = ["llama3.1:8b"]
        
        # Arabic linguistic patterns
        self.arabic_emotion_keywords = {
            'joy': ['فرح', 'سعادة', 'بهجة', 'سرور', 'حبور', 'ابتهاج', 'انشراح'],
            'sadness': ['حزن', 'أسى', 'كآبة', 'غم', 'هم', 'كرب', 'أسف'],
            'anger': ['غضب', 'سخط', 'حنق', 'زعل', 'استياء', 'نقمة', 'ثورة'],
            'fear': ['خوف', 'فزع', 'رعب', 'هلع', 'جزع', 'وجل', 'قلق'],
            'surprise': ['دهشة', 'استغراب', 'تعجب', 'ذهول', 'انبهار', 'صدمة'],
            'disgust': ['اشمئزاز', 'نفور', 'كراهية', 'قرف', 'استقذار'],
            'trust': ['ثقة', 'أمان', 'اطمئنان', 'يقين', 'وثوق', 'اعتماد'],
            'anticipation': ['ترقب', 'انتظار', 'توقع', 'تطلع', 'أمل', 'رجاء']
        }
        
        # Truth/deception indicators
        self.truth_indicators = {
            'certainty': ['بالتأكيد', 'قطعاً', 'يقيناً', 'حتماً', 'لا شك', 'بلا ريب'],
            'uncertainty': ['ربما', 'قد', 'لعل', 'عسى', 'يمكن', 'محتمل', 'أظن', 'أعتقد'],
            'temporal': ['أمس', 'اليوم', 'غداً', 'الآن', 'حالياً', 'سابقاً', 'لاحقاً'],
            'contradiction': ['لكن', 'غير أن', 'إلا أن', 'بيد أن', 'مع ذلك', 'رغم ذلك']
        }
        
        # Narrative flow patterns
        self.narrative_patterns = {
            'linear': ['أولاً', 'ثانياً', 'ثالثاً', 'بعد ذلك', 'ثم', 'أخيراً'],
            'circular': ['كما ذكرت', 'كما قلت', 'مرة أخرى', 'مجدداً'],
            'fragmented': ['فجأة', 'بشكل مفاجئ', 'دون سابق إنذار', 'من العدم']
        }
    
    def check_model_availability(self, model_name: str) -> bool:
        """Check if model is available"""
        try:
            available_models = ollama.list()
            # The response has a 'models' attribute that contains a list of Model objects
            model_names = [model.model for model in available_models.models]
            return model_name in model_names
        except Exception as e:
            print(f"Error checking model availability: {e}")
            return False
    
    def get_available_model(self) -> str:
        """Get the best available model"""
        models_to_try = [self.primary_model] + self.fallback_models
        
        for model in models_to_try:
            if self.check_model_availability(model):
                return model
        
        raise Exception("No suitable models available for analysis")
    
    def extract_attention_weights(self, text: str, model_name: str) -> List[AttentionWeight]:
        """Extract attention weights for different text segments"""
        try:
            # Split text into sentences
            sentences = re.split(r'[.!?؟]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            attention_weights = []
            
            for i, sentence in enumerate(sentences):
                # Calculate attention weight based on multiple factors
                emotional_words = sum(1 for emotion_list in self.arabic_emotion_keywords.values() 
                                    for word in emotion_list if word in sentence)
                
                # Length factor (moderate length gets higher attention)
                length_factor = min(len(sentence.split()) / 10, 1.0)
                
                # Position factor (beginning and end get higher attention)
                position_factor = 1.0 - abs(i - len(sentences)/2) / (len(sentences)/2) if len(sentences) > 1 else 1.0
                
                # Emotional impact
                emotional_impact = emotional_words / max(len(sentence.split()), 1)
                
                # Context relevance (based on keyword density)
                context_relevance = min(emotional_words / 3, 1.0)
                
                # Combined weight
                weight = (length_factor * 0.3 + position_factor * 0.3 + 
                         emotional_impact * 0.4) * (1 + context_relevance)
                
                attention_weights.append(AttentionWeight(
                    text=sentence,
                    weight=weight,
                    position=i,
                    context_relevance=context_relevance,
                    emotional_impact=emotional_impact
                ))
            
            return sorted(attention_weights, key=lambda x: x.weight, reverse=True)
            
        except Exception as e:
            print(f"Error extracting attention weights: {e}")
            return []
    
    def analyze_narrative_structure(self, text: str) -> NarrativeAnalysis:
        """Analyze narrative structure and truth indicators"""
        try:
            # Count different types of markers
            certainty_count = sum(1 for marker in self.truth_indicators['certainty'] if marker in text)
            uncertainty_count = sum(1 for marker in self.truth_indicators['uncertainty'] if marker in text)
            temporal_count = sum(1 for marker in self.truth_indicators['temporal'] if marker in text)
            contradiction_count = sum(1 for marker in self.truth_indicators['contradiction'] if marker in text)
            
            # Determine narrative flow
            linear_score = sum(1 for pattern in self.narrative_patterns['linear'] if pattern in text)
            circular_score = sum(1 for pattern in self.narrative_patterns['circular'] if pattern in text)
            fragmented_score = sum(1 for pattern in self.narrative_patterns['fragmented'] if pattern in text)
            
            flow_scores = {'linear': linear_score, 'circular': circular_score, 'fragmented': fragmented_score}
            narrative_flow = max(flow_scores.keys(), key=lambda k: flow_scores[k])
            
            # Calculate coherence (based on logical flow markers)
            total_words = len(text.split())
            coherence_score = min((linear_score + temporal_count) / max(total_words / 50, 1), 1.0)
            
            # Calculate consistency (inverse of contradictions)
            consistency_score = max(1.0 - (contradiction_count / max(total_words / 30, 1)), 0.0)
            
            # Calculate truth likelihood
            certainty_ratio = certainty_count / max(certainty_count + uncertainty_count, 1)
            truth_likelihood = (certainty_ratio * 0.4 + coherence_score * 0.3 + 
                              consistency_score * 0.3)
            
            return NarrativeAnalysis(
                coherence_score=coherence_score,
                consistency_score=consistency_score,
                truth_likelihood=truth_likelihood,
                narrative_flow=narrative_flow,
                temporal_markers=[marker for marker in self.truth_indicators['temporal'] if marker in text],
                contradiction_indicators=[marker for marker in self.truth_indicators['contradiction'] if marker in text],
                certainty_markers=[marker for marker in self.truth_indicators['certainty'] if marker in text],
                uncertainty_markers=[marker for marker in self.truth_indicators['uncertainty'] if marker in text]
            )
            
        except Exception as e:
            print(f"Error analyzing narrative structure: {e}")
            return NarrativeAnalysis(0.5, 0.5, 0.5, "unknown", [], [], [], [])
    
    def extract_emotional_trajectory(self, text: str) -> List[Tuple[int, float]]:
        """Extract emotional trajectory throughout the text"""
        try:
            sentences = re.split(r'[.!?؟]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            trajectory = []
            
            for i, sentence in enumerate(sentences):
                # Calculate sentiment score for this sentence
                positive_words = 0
                negative_words = 0
                
                # Count emotional words
                for emotion, words in self.arabic_emotion_keywords.items():
                    count = sum(1 for word in words if word in sentence)
                    if emotion in ['joy', 'trust', 'anticipation']:
                        positive_words += count
                    elif emotion in ['sadness', 'anger', 'fear', 'disgust']:
                        negative_words += count
                
                # Calculate sentiment score (-1 to 1)
                total_emotional = positive_words + negative_words
                if total_emotional > 0:
                    sentiment_score = (positive_words - negative_words) / total_emotional
                else:
                    sentiment_score = 0.0
                
                trajectory.append((i, sentiment_score))
            
            return trajectory
            
        except Exception as e:
            print(f"Error extracting emotional trajectory: {e}")
            return []
    
    def analyze_with_llm(self, text: str, model_name: str) -> Dict[str, Any]:
        """Perform deep sentiment analysis using LLM"""
        try:
            prompt = f"""أنت خبير في تحليل المشاعر والنصوص العربية. قم بتحليل النص التالي تحليلاً عميقاً:

النص:
{text}

المطلوب تحليل شامل يتضمن:

1. التحليل العاطفي العميق:
   - المشاعر الأساسية (فرح، حزن، غضب، خوف، دهشة، اشمئزاز، ثقة، ترقب)
   - شدة كل مشاعر من 0 إلى 1
   - المشاعر المهيمنة

2. تحليل الانتباه والتركيز:
   - العبارات الأكثر أهمية
   - الكلمات المفتاحية العاطفية
   - نقاط التركيز الرئيسية

3. تحليل السرد والصدق:
   - مستوى التماسك في السرد
   - مؤشرات الصدق أو عدم الصدق
   - التناقضات إن وجدت
   - مستوى اليقين في الكلام

4. الأنماط اللغوية:
   - استخدام الزمن (ماضي، حاضر، مستقبل)
   - مستوى الرسمية
   - التعقيد اللغوي

قدم التحليل في شكل JSON منظم باللغة العربية."""

            response = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': 0.3,
                    'top_p': 0.9,
                    'max_tokens': 2048
                }
            )
            
            # Try to extract JSON from response
            response_text = response['message']['content']
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # If no valid JSON, return structured interpretation
            return {
                "raw_analysis": response_text,
                "model_response": True
            }
            
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            return {"error": str(e)}
    
    def calculate_emotion_scores(self, text: str, llm_analysis: Dict[str, Any]) -> EmotionScore:
        """Calculate detailed emotion scores"""
        try:
            # Initialize with keyword-based analysis
            emotion_scores = EmotionScore()
            
            # Count emotion keywords
            total_words = len(text.split())
            for emotion, keywords in self.arabic_emotion_keywords.items():
                count = sum(1 for keyword in keywords if keyword in text)
                score = min(count / max(total_words / 20, 1), 1.0)
                setattr(emotion_scores, emotion, score)
            
            # Enhance with LLM analysis if available
            if 'emotions' in llm_analysis or 'المشاعر' in llm_analysis:
                # Try to extract emotion scores from LLM response
                pass  # Implementation depends on LLM response format
            
            return emotion_scores
            
        except Exception as e:
            print(f"Error calculating emotion scores: {e}")
            return EmotionScore()
    
    def extract_key_phrases(self, text: str, attention_weights: List[AttentionWeight]) -> List[str]:
        """Extract key phrases based on attention weights and emotional content"""
        try:
            key_phrases = []
            
            # Get top attention sentences
            top_sentences = sorted(attention_weights, key=lambda x: x.weight, reverse=True)[:3]
            
            for attention in top_sentences:
                # Extract meaningful phrases from high-attention sentences
                words = attention.text.split()
                if len(words) >= 3:
                    # Look for emotional phrases
                    for i in range(len(words) - 2):
                        phrase = ' '.join(words[i:i+3])
                        # Check if phrase contains emotional content
                        has_emotion = any(keyword in phrase 
                                        for emotion_list in self.arabic_emotion_keywords.values() 
                                        for keyword in emotion_list)
                        if has_emotion:
                            key_phrases.append(phrase)
            
            # Remove duplicates and return top phrases
            return list(set(key_phrases))[:5]
            
        except Exception as e:
            print(f"Error extracting key phrases: {e}")
            return []
    
    def analyze_linguistic_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze linguistic patterns in the text"""
        try:
            words = text.split()
            sentences = re.split(r'[.!?؟]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Basic statistics
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Temporal analysis
            past_markers = ['كان', 'كانت', 'فعل', 'حدث', 'وقع']
            present_markers = ['الآن', 'حالياً', 'يحدث', 'يفعل']
            future_markers = ['سوف', 'سيكون', 'غداً', 'مستقبلاً']
            
            past_count = sum(1 for marker in past_markers if marker in text)
            present_count = sum(1 for marker in present_markers if marker in text)
            future_count = sum(1 for marker in future_markers if marker in text)
            
            # Determine dominant tense
            tense_counts = {'past': past_count, 'present': present_count, 'future': future_count}
            dominant_tense = max(tense_counts.keys(), key=lambda k: tense_counts[k])
            
            # Formality level (based on formal vs informal words)
            formal_markers = ['إن', 'أن', 'لكن', 'غير أن', 'بيد أن']
            informal_markers = ['يعني', 'طيب', 'أوكي', 'ماشي']
            
            formal_count = sum(1 for marker in formal_markers if marker in text)
            informal_count = sum(1 for marker in informal_markers if marker in text)
            
            formality_score = formal_count / max(formal_count + informal_count, 1)
            
            return {
                'avg_sentence_length': avg_sentence_length,
                'avg_word_length': avg_word_length,
                'sentence_count': len(sentences),
                'word_count': len(words),
                'dominant_tense': dominant_tense,
                'tense_distribution': tense_counts,
                'formality_score': formality_score,
                'complexity_score': min(avg_sentence_length / 10, 1.0)
            }
            
        except Exception as e:
            print(f"Error analyzing linguistic patterns: {e}")
            return {}
    
    def analyze_comprehensive(self, text: str) -> AdvancedSentimentResult:
        """Perform comprehensive sentiment analysis"""
        start_time = time.time()
        
        try:
            # Get available model
            model_name = self.get_available_model()
            print(f"🤖 Using model: {model_name}")
            
            # Perform LLM analysis
            print("🧠 Performing deep LLM analysis...")
            llm_analysis = self.analyze_with_llm(text, model_name)
            
            # Extract attention weights
            print("🎯 Extracting attention weights...")
            attention_weights = self.extract_attention_weights(text, model_name)
            
            # Analyze narrative structure
            print("📖 Analyzing narrative structure...")
            narrative_analysis = self.analyze_narrative_structure(text)
            
            # Calculate emotion scores
            print("💭 Calculating emotion scores...")
            emotion_scores = self.calculate_emotion_scores(text, llm_analysis)
            
            # Extract emotional trajectory
            print("📈 Extracting emotional trajectory...")
            emotional_trajectory = self.extract_emotional_trajectory(text)
            
            # Extract key phrases
            print("🔑 Extracting key phrases...")
            key_phrases = self.extract_key_phrases(text, attention_weights)
            
            # Analyze linguistic patterns
            print("🔤 Analyzing linguistic patterns...")
            linguistic_patterns = self.analyze_linguistic_patterns(text)
            
            # Determine overall sentiment
            avg_emotion_score = emotion_scores.emotional_intensity()
            dominant_emotion = emotion_scores.dominant_emotion()
            
            # Map dominant emotion to sentiment
            positive_emotions = ['joy', 'trust', 'anticipation']
            negative_emotions = ['sadness', 'anger', 'fear', 'disgust']
            
            if dominant_emotion in positive_emotions:
                overall_sentiment = "positive"
            elif dominant_emotion in negative_emotions:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
            
            # Calculate sentiment confidence
            sentiment_confidence = min(avg_emotion_score * narrative_analysis.coherence_score, 1.0)
            
            processing_time = time.time() - start_time
            
            return AdvancedSentimentResult(
                text=text,
                overall_sentiment=overall_sentiment,
                sentiment_confidence=sentiment_confidence,
                emotion_scores=emotion_scores,
                attention_weights=attention_weights,
                narrative_analysis=narrative_analysis,
                key_phrases=key_phrases,
                emotional_trajectory=emotional_trajectory,
                linguistic_patterns=linguistic_patterns,
                processing_time=processing_time,
                model_used=model_name
            )
            
        except Exception as e:
            print(f"❌ Error in comprehensive analysis: {e}")
            # Return basic result on error
            return AdvancedSentimentResult(
                text=text,
                overall_sentiment="unknown",
                sentiment_confidence=0.0,
                emotion_scores=EmotionScore(),
                attention_weights=[],
                narrative_analysis=NarrativeAnalysis(0.0, 0.0, 0.0, "unknown", [], [], [], []),
                key_phrases=[],
                emotional_trajectory=[],
                linguistic_patterns={},
                processing_time=time.time() - start_time,
                model_used="error"
            )

def main():
    """Test the advanced sentiment analyzer"""
    # Sample Arabic text for testing
    sample_text = """
    شكراً لكم. بعد ما أعرف، لا لا، ما عادي، ما عندي شي ما أخبرتك به، ولكن لدي يوم نيئ عندما أرى بناتي، إن شاء الله، والله إن شاء الله رحمة الله عز وجل. لا لا، لم أتواصل معهم، لا أعرف كل شيء، فقط أخبرتني أنني سأرى بناتي قبل التنفيذ.
    """
    
    analyzer = AdvancedArabicSentimentAnalyzer()
    
    print("🚀 Starting Advanced Arabic Sentiment Analysis")
    print("=" * 80)
    
    result = analyzer.analyze_comprehensive(sample_text)
    
    print("\n📊 ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Overall Sentiment: {result.overall_sentiment}")
    print(f"Confidence: {result.sentiment_confidence:.3f}")
    print(f"Dominant Emotion: {result.emotion_scores.dominant_emotion()}")
    print(f"Emotional Intensity: {result.emotion_scores.emotional_intensity():.3f}")
    print(f"Truth Likelihood: {result.narrative_analysis.truth_likelihood:.3f}")
    print(f"Narrative Coherence: {result.narrative_analysis.coherence_score:.3f}")
    print(f"Processing Time: {result.processing_time:.2f}s")
    print(f"Model Used: {result.model_used}")
    
    # Save results
    timestamp = int(time.time())
    results_file = f"advanced_sentiment_analysis_{timestamp}.json"
    
    # Convert result to dict for JSON serialization
    result_dict = {
        'text': result.text,
        'overall_sentiment': result.overall_sentiment,
        'sentiment_confidence': result.sentiment_confidence,
        'emotion_scores': asdict(result.emotion_scores),
        'attention_weights': [asdict(aw) for aw in result.attention_weights],
        'narrative_analysis': asdict(result.narrative_analysis),
        'key_phrases': result.key_phrases,
        'emotional_trajectory': result.emotional_trajectory,
        'linguistic_patterns': result.linguistic_patterns,
        'processing_time': result.processing_time,
        'model_used': result.model_used,
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")

if __name__ == "__main__":
    main()