#!/usr/bin/env python3
"""
Local Arabic Text Analyzer Service
Uses only local models - no external APIs or paid services
Combines grammar checking, sentence validation, and sentiment analysis
Processes text per sentence with separate file outputs
"""

import os
import json
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path

# For local models
try:
    from transformers import (
        pipeline, 
        AutoTokenizer, 
        AutoModelForSequenceClassification,
        AutoModelForCausalLM,
        T5ForConditionalGeneration,
        T5Tokenizer
    )
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. Install with: pip install transformers torch")

# For Arabic text processing
try:
    import nltk
    from nltk.tokenize import sent_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: nltk not available. Install with: pip install nltk")

class LocalArabicTextAnalyzer:
    """
    Comprehensive Arabic text analysis service using only local models:
    - Local grammar and spelling checking using T5 and BERT models
    - Sentence validation with Arabic linguistic rules
    - Sentiment analysis using local Arabic BERT models
    - Per-sentence processing with separate outputs
    - No external APIs or paid services required
    """
    
    def __init__(self, output_dir: str = "analysis_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize local models
        self.grammar_models = {}
        self.sentiment_models = {}
        self.arabic_models = {}
        
        self._initialize_local_models()
        
        # Arabic sentence patterns for validation
        self.arabic_patterns = {
            'has_arabic': re.compile(r'[\u0600-\u06FF]'),
            'sentence_end': re.compile(r'[.!?؟]'),
            'incomplete_sentence': re.compile(r'^[و|ف|ب|ل|ك|من|إلى|على|في|عن|مع|بعد|قبل|تحت|فوق]'),
            'diacritics': re.compile(r'[\u064B-\u0652]'),
            'numbers': re.compile(r'[0-9٠-٩]'),
            'punctuation': re.compile(r'[،؛؟!.]'),
        }
        
    def _initialize_local_models(self):
        """Initialize all local models for Arabic text analysis"""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.warning("Transformers not available. Limited functionality.")
            return
            
        # Initialize grammar correction models
        self._load_grammar_models()
        
        # Initialize sentiment analysis models
        self._load_sentiment_models()
        
        # Initialize Arabic language models
        self._load_arabic_models()
        
    def _load_grammar_models(self):
        """Load local grammar correction models"""
        try:
            # T5-based grammar correction (English-trained but can work for Arabic structure)
            self.logger.info("Loading T5 grammar correction model...")
            self.grammar_models['t5_grammar'] = pipeline(
                'text2text-generation',
                model='vennify/t5-base-grammar-correction',
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("✅ T5 grammar model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load T5 grammar model: {e}")
            
        try:
            # Arabic BERT for masked language modeling (grammar checking)
            self.logger.info("Loading Arabic BERT for grammar analysis...")
            self.grammar_models['arabic_bert'] = pipeline(
                'fill-mask',
                model='asafaya/bert-base-arabic',
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("✅ Arabic BERT grammar model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load Arabic BERT grammar model: {e}")
    
    def _load_sentiment_models(self):
        """Load local sentiment analysis models"""
        try:
            # CAMeLBERT-DA for dialectal Arabic sentiment
            self.logger.info("Loading CAMeLBERT-DA sentiment model...")
            self.sentiment_models['camelbert'] = pipeline(
                'text-classification',
                model='CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment',
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("✅ CAMeLBERT-DA model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load CAMeLBERT-DA model: {e}")
            
        try:
            # AraBERT for general Arabic sentiment
            self.logger.info("Loading AraBERT sentiment model...")
            self.sentiment_models['arabert'] = pipeline(
                'text-classification',
                model='aubmindlab/bert-base-arabertv02',
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("✅ AraBERT model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load AraBERT model: {e}")
    
    def _load_arabic_models(self):
        """Load additional Arabic language models for advanced analysis"""
        try:
            # CAMeLBERT for general Arabic understanding
            self.logger.info("Loading CAMeLBERT for text analysis...")
            self.arabic_models['camelbert_general'] = pipeline(
                'fill-mask',
                model='CAMeL-Lab/bert-base-arabic-camelbert-da',
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("✅ CAMeLBERT general model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load CAMeLBERT general model: {e}")
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split Arabic text into sentences"""
        if NLTK_AVAILABLE:
            try:
                # Try NLTK sentence tokenization
                sentences = sent_tokenize(text, language='arabic')
                return [s.strip() for s in sentences if s.strip()]
            except:
                pass
        
        # Fallback: simple sentence splitting
        sentences = re.split(r'[.!?؟]\s*', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def check_grammar_local_t5(self, text: str) -> Dict[str, Any]:
        """
        Check grammar using local T5 model
        """
        if 't5_grammar' not in self.grammar_models:
            return {
                'service': 'local_t5',
                'status': 'unavailable',
                'message': 'T5 grammar model not loaded',
                'suggestions': [],
                'corrected_text': text
            }
        
        try:
            # For Arabic text, we'll use a different approach
            # T5 model expects "grammar: " prefix
            input_text = f"grammar: {text}"
            result = self.grammar_models['t5_grammar'](
                input_text, 
                max_length=len(text) + 50,
                num_beams=3,
                early_stopping=True
            )
            
            corrected_text = result[0]['generated_text'] if result else text
            
            # Simple comparison to find differences
            suggestions = []
            if corrected_text != text and corrected_text.strip():
                suggestions.append({
                    'original': text,
                    'suggestion': corrected_text,
                    'type': 'grammar_correction'
                })
            
            return {
                'service': 'local_t5',
                'status': 'completed',
                'message': 'Grammar checked using local T5 model',
                'suggestions': suggestions,
                'corrected_text': corrected_text,
                'confidence': 0.8 if suggestions else 0.9
            }
            
        except Exception as e:
            return {
                'service': 'local_t5',
                'status': 'error',
                'message': f'T5 grammar check failed: {str(e)}',
                'suggestions': [],
                'corrected_text': text
            }
    
    def check_grammar_arabic_bert(self, text: str) -> Dict[str, Any]:
        """
        Check grammar using Arabic BERT masked language modeling
        """
        if 'arabic_bert' not in self.grammar_models:
            return {
                'service': 'arabic_bert',
                'status': 'unavailable',
                'message': 'Arabic BERT model not loaded',
                'suggestions': [],
                'corrected_text': text
            }
        
        try:
            suggestions = []
            words = text.split()
            
            # Check each word by masking it and seeing if BERT suggests something different
            for i, word in enumerate(words):
                if len(word) > 2 and self.arabic_patterns['has_arabic'].search(word):
                    # Create masked version
                    masked_words = words.copy()
                    masked_words[i] = '[MASK]'
                    masked_text = ' '.join(masked_words)
                    
                    try:
                        # Get BERT predictions
                        predictions = self.grammar_models['arabic_bert'](masked_text)
                        
                        if predictions and len(predictions) > 0:
                            top_prediction = predictions[0]
                            suggested_word = top_prediction['token_str']
                            confidence = top_prediction['score']
                            
                            # If BERT suggests a different word with high confidence
                            if (suggested_word != word and 
                                confidence > 0.3 and 
                                self.arabic_patterns['has_arabic'].search(suggested_word)):
                                
                                suggestions.append({
                                    'position': i,
                                    'original': word,
                                    'suggestion': suggested_word,
                                    'confidence': confidence,
                                    'type': 'word_correction'
                                })
                    except:
                        continue
            
            # Apply suggestions to create corrected text
            corrected_words = words.copy()
            for suggestion in suggestions:
                if suggestion['confidence'] > 0.5:  # Only apply high-confidence suggestions
                    corrected_words[suggestion['position']] = suggestion['suggestion']
            
            corrected_text = ' '.join(corrected_words)
            
            return {
                'service': 'arabic_bert',
                'status': 'completed',
                'message': f'Grammar checked using Arabic BERT - found {len(suggestions)} suggestions',
                'suggestions': suggestions,
                'corrected_text': corrected_text,
                'confidence': 0.7
            }
            
        except Exception as e:
            return {
                'service': 'arabic_bert',
                'status': 'error',
                'message': f'Arabic BERT grammar check failed: {str(e)}',
                'suggestions': [],
                'corrected_text': text
            }
    
    def validate_sentence_structure(self, sentence: str) -> Dict[str, Any]:
        """Enhanced Arabic sentence structure validation"""
        validation = {
            'is_valid': True,
            'issues': [],
            'suggestions': [],
            'metrics': {}
        }
        
        # Check if sentence contains Arabic text
        if not self.arabic_patterns['has_arabic'].search(sentence):
            validation['is_valid'] = False
            validation['issues'].append('No Arabic text detected')
        
        # Check sentence length
        if len(sentence.strip()) < 3:
            validation['is_valid'] = False
            validation['issues'].append('Sentence too short')
        elif len(sentence.strip()) > 500:
            validation['issues'].append('Sentence very long - consider splitting')
        
        # Check for proper sentence ending
        if not self.arabic_patterns['sentence_end'].search(sentence):
            validation['issues'].append('Missing sentence ending punctuation')
            validation['suggestions'].append('Add proper punctuation (. ! ? ؟)')
        
        # Check for incomplete sentences (starting with conjunctions)
        if self.arabic_patterns['incomplete_sentence'].match(sentence.strip()):
            validation['issues'].append('Sentence may be incomplete (starts with conjunction)')
            validation['suggestions'].append('Consider if this is a complete thought')
        
        # Check for excessive diacritics
        diacritics_count = len(self.arabic_patterns['diacritics'].findall(sentence))
        if diacritics_count > len(sentence) * 0.3:
            validation['issues'].append('Excessive diacritics detected')
            validation['suggestions'].append('Consider removing some diacritics for readability')
        
        # Calculate metrics
        validation['metrics'] = {
            'length': len(sentence),
            'word_count': len(sentence.split()),
            'arabic_ratio': len(self.arabic_patterns['has_arabic'].findall(sentence)) / len(sentence) if sentence else 0,
            'diacritics_count': diacritics_count,
            'punctuation_count': len(self.arabic_patterns['punctuation'].findall(sentence))
        }
        
        return validation
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using local Arabic models"""
        results = {
            'text': text,
            'models': {},
            'consensus': None,
            'confidence': 0.0
        }
        
        if not TRANSFORMERS_AVAILABLE or not self.sentiment_models:
            return {
                'text': text,
                'error': 'No sentiment models available',
                'models': {}
            }
        
        # Analyze with each available model
        for model_name, model in self.sentiment_models.items():
            try:
                # Truncate text if too long for the model
                max_length = 512  # Most BERT models have 512 token limit
                truncated_text = text[:max_length] if len(text) > max_length else text
                
                result = model(truncated_text)
                if result and len(result) > 0:
                    results['models'][model_name] = {
                        'label': result[0]['label'],
                        'score': result[0]['score'],
                        'confidence': result[0]['score']
                    }
            except Exception as e:
                results['models'][model_name] = {
                    'error': str(e)
                }
        
        # Determine consensus sentiment
        sentiments = []
        confidences = []
        
        for model_result in results['models'].values():
            if 'label' in model_result:
                sentiments.append(model_result['label'])
                confidences.append(model_result['confidence'])
        
        if sentiments:
            # Weighted consensus based on confidence
            sentiment_scores = {}
            for sentiment, confidence in zip(sentiments, confidences):
                if sentiment not in sentiment_scores:
                    sentiment_scores[sentiment] = []
                sentiment_scores[sentiment].append(confidence)
            
            # Calculate average confidence for each sentiment
            avg_scores = {}
            for sentiment, scores in sentiment_scores.items():
                avg_scores[sentiment] = sum(scores) / len(scores)
            
            results['consensus'] = max(avg_scores, key=avg_scores.get)
            results['confidence'] = avg_scores[results['consensus']]
        
        return results
    
    def analyze_sentence(self, sentence: str, sentence_id: int) -> Dict[str, Any]:
        """Comprehensive analysis of a single sentence using only local models"""
        self.logger.info(f"Analyzing sentence {sentence_id}: {sentence[:50]}...")
        
        analysis = {
            'sentence_id': sentence_id,
            'text': sentence,
            'timestamp': datetime.now().isoformat(),
            'grammar_check': {},
            'sentence_validation': {},
            'sentiment_analysis': {}
        }
        
        # Local grammar checking
        try:
            analysis['grammar_check'] = {
                't5_local': self.check_grammar_local_t5(sentence),
                'arabic_bert': self.check_grammar_arabic_bert(sentence)
            }
        except Exception as e:
            analysis['grammar_check'] = {'error': str(e)}
        
        # Sentence validation
        try:
            analysis['sentence_validation'] = self.validate_sentence_structure(sentence)
        except Exception as e:
            analysis['sentence_validation'] = {'error': str(e)}
        
        # Sentiment analysis
        try:
            analysis['sentiment_analysis'] = self.analyze_sentiment(sentence)
        except Exception as e:
            analysis['sentiment_analysis'] = {'error': str(e)}
        
        return analysis
    
    def save_sentence_analysis(self, analysis: Dict[str, Any], base_filename: str):
        """Save individual sentence analysis to separate file"""
        sentence_id = analysis['sentence_id']
        filename = f"{base_filename}_sentence_{sentence_id:03d}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved sentence {sentence_id} analysis to {filepath}")
        return filepath
    
    def analyze_text(self, text: str, base_filename: str = None) -> Dict[str, Any]:
        """
        Analyze complete text with per-sentence processing using only local models
        """
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"local_arabic_analysis_{timestamp}"
        
        self.logger.info(f"Starting LOCAL analysis of text ({len(text)} characters)")
        
        # Split text into sentences
        sentences = self.split_into_sentences(text)
        self.logger.info(f"Split into {len(sentences)} sentences")
        
        # Overall analysis results
        overall_results = {
            'analysis_id': base_filename,
            'timestamp': datetime.now().isoformat(),
            'analyzer_type': 'local_only',
            'input_text': text,
            'total_sentences': len(sentences),
            'sentence_files': [],
            'summary': {
                'grammar_issues': 0,
                'validation_issues': 0,
                'sentiment_distribution': {},
                'overall_sentiment': None,
                'local_models_used': list(self.grammar_models.keys()) + list(self.sentiment_models.keys())
            }
        }
        
        # Analyze each sentence
        for i, sentence in enumerate(sentences, 1):
            if sentence.strip():  # Skip empty sentences
                analysis = self.analyze_sentence(sentence, i)
                
                # Save individual sentence analysis
                sentence_file = self.save_sentence_analysis(analysis, base_filename)
                overall_results['sentence_files'].append(str(sentence_file))
                
                # Update summary statistics
                if 'issues' in analysis.get('sentence_validation', {}):
                    overall_results['summary']['validation_issues'] += len(
                        analysis['sentence_validation']['issues']
                    )
                
                # Count grammar suggestions
                grammar_check = analysis.get('grammar_check', {})
                for service_result in grammar_check.values():
                    if isinstance(service_result, dict) and 'suggestions' in service_result:
                        overall_results['summary']['grammar_issues'] += len(service_result['suggestions'])
                
                # Track sentiment distribution
                sentiment_result = analysis.get('sentiment_analysis', {})
                if 'consensus' in sentiment_result:
                    sentiment = sentiment_result['consensus']
                    overall_results['summary']['sentiment_distribution'][sentiment] = \
                        overall_results['summary']['sentiment_distribution'].get(sentiment, 0) + 1
        
        # Determine overall sentiment
        sentiment_dist = overall_results['summary']['sentiment_distribution']
        if sentiment_dist:
            overall_results['summary']['overall_sentiment'] = max(
                sentiment_dist, key=sentiment_dist.get
            )
        
        # Save overall results
        overall_file = self.output_dir / f"{base_filename}_overall.json"
        with open(overall_file, 'w', encoding='utf-8') as f:
            json.dump(overall_results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"LOCAL analysis complete. Overall results saved to {overall_file}")
        self.logger.info(f"Individual sentence files: {len(overall_results['sentence_files'])}")
        self.logger.info(f"Models used: {overall_results['summary']['local_models_used']}")
        
        return overall_results

def main():
    """Example usage of the Local Arabic Text Analyzer"""
    # Sample Arabic text for testing
    sample_text = """
    مرحباً بكم في نظام تحليل النصوص العربية المحلي. هذا النظام يعمل بدون إنترنت أو خدمات خارجية.
    يستخدم النظام نماذج محلية فقط لفحص القواعد والمشاعر. جميع العمليات تتم على جهازك المحلي.
    نأمل أن يكون هذا النظام مفيداً لكم في تحليل النصوص العربية بخصوصية تامة.
    """
    
    # Initialize local analyzer
    analyzer = LocalArabicTextAnalyzer()
    
    # Analyze the text
    results = analyzer.analyze_text(sample_text, "local_sample_analysis")
    
    print(f"\n✅ LOCAL Analysis Complete!")
    print(f"📊 Total sentences analyzed: {results['total_sentences']}")
    print(f"📁 Individual sentence files: {len(results['sentence_files'])}")
    print(f"🎭 Overall sentiment: {results['summary']['overall_sentiment']}")
    print(f"⚠️  Validation issues: {results['summary']['validation_issues']}")
    print(f"🔧 Grammar suggestions: {results['summary']['grammar_issues']}")
    print(f"📈 Sentiment distribution: {results['summary']['sentiment_distribution']}")
    print(f"🏠 Local models used: {results['summary']['local_models_used']}")
    print(f"🔒 Privacy: All processing done locally - no external APIs used!")

if __name__ == "__main__":
    main()