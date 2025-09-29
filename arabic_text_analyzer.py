#!/usr/bin/env python3
"""
Arabic Text Analysis Service - LOCAL MODELS ONLY
Comprehensive analysis including grammar checking, sentence validation, and sentiment analysis
Uses only local models - no external APIs or paid services
Processes text per sentence with separate file outputs
"""

import os
import json
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path

# Import the new local analyzer
from local_arabic_analyzer import LocalArabicTextAnalyzer

# Optional dependencies for enhanced functionality
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. Install with: pip install transformers torch")

try:
    import nltk
    from nltk.tokenize import sent_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: nltk not available. Install with: pip install nltk")

class ArabicTextAnalyzer:
    """
    Arabic Text Analysis Service - LOCAL MODELS ONLY
    
    This service provides comprehensive Arabic text analysis using only local models:
    - Grammar checking using local T5 and Arabic BERT models
    - Sentence validation with Arabic linguistic rules  
    - Sentiment analysis using local Arabic BERT models (CAMeLBERT, AraBERT)
    - Per-sentence processing with separate outputs
    - No external APIs or paid services required
    
    All processing is done locally for complete privacy and offline capability.
    """
    
    def __init__(self, output_dir: str = "analysis_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize the local analyzer
        self.local_analyzer = LocalArabicTextAnalyzer(str(self.output_dir))
        
        self.logger.info("✅ Arabic Text Analyzer initialized with LOCAL MODELS ONLY")
        self.logger.info("🔒 No external APIs will be used - complete privacy guaranteed")
        
        # Initialize sentiment analysis models
        self.sentiment_models = {}
        self._initialize_sentiment_models()
        
        # Arabic sentence patterns for validation
        self.arabic_patterns = {
            'has_arabic': re.compile(r'[\u0600-\u06FF]'),
            'sentence_end': re.compile(r'[.!?؟]'),
            'incomplete_sentence': re.compile(r'^[و|ف|ب|ل|ك|من|إلى|على|في|عن|مع|بعد|قبل|تحت|فوق]'),
            'diacritics': re.compile(r'[\u064B-\u0652]'),
            'numbers': re.compile(r'[0-9٠-٩]'),
            'punctuation': re.compile(r'[،؛؟!.]'),
        }
        
    def _initialize_sentiment_models(self):
        """Initialize sentiment analysis models"""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.warning("Transformers not available. Sentiment analysis will be limited.")
            return
            
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
            # Alternative Arabic BERT model
            self.logger.info("Loading AraBERT sentiment model...")
            self.sentiment_models['arabert'] = pipeline(
                'text-classification',
                model='aubmindlab/bert-base-arabertv02',
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("✅ AraBERT model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load AraBERT model: {e}")
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split Arabic text into sentences using local methods"""
        return self.local_analyzer.split_into_sentences(text)
    
    def check_grammar_qalam(self, text: str) -> Dict[str, Any]:
        """
        LOCAL REPLACEMENT for Qalam.ai grammar checking
        Uses local T5 model for grammar correction
        """
        return self.local_analyzer.check_grammar_local_t5(text)
    
    def check_grammar_alnnahwi(self, text: str) -> Dict[str, Any]:
        """
        LOCAL REPLACEMENT for Alnnahwi.com grammar checking  
        Uses local Arabic BERT model for grammar analysis
        """
        return self.local_analyzer.check_grammar_arabic_bert(text)
    
    def validate_sentence_structure(self, sentence: str) -> Dict[str, Any]:
        """Enhanced Arabic sentence structure validation using local methods"""
        return self.local_analyzer.validate_sentence_structure(sentence)
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using local Arabic BERT models"""
        return self.local_analyzer.analyze_sentiment(text)
    
    def analyze_sentence(self, sentence: str, sentence_id: int) -> Dict[str, Any]:
        """
        Comprehensive analysis of a single sentence using LOCAL MODELS ONLY
        """
        self.logger.info(f"Analyzing sentence {sentence_id} with LOCAL models: {sentence[:50]}...")
        
        analysis = {
            'sentence_id': sentence_id,
            'text': sentence,
            'timestamp': datetime.now().isoformat(),
            'analyzer_type': 'local_only',
            'grammar_check': {},
            'sentence_validation': {},
            'sentiment_analysis': {}
        }
        
        # LOCAL grammar checking (replaces external APIs)
        try:
            analysis['grammar_check'] = {
                'qalam_local': self.check_grammar_qalam(sentence),  # Now uses local T5
                'alnnahwi_local': self.check_grammar_alnnahwi(sentence)  # Now uses local BERT
            }
        except Exception as e:
            analysis['grammar_check'] = {'error': str(e)}
        
        # Sentence validation (already local)
        try:
            analysis['sentence_validation'] = self.validate_sentence_structure(sentence)
        except Exception as e:
            analysis['sentence_validation'] = {'error': str(e)}
        
        # LOCAL sentiment analysis
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
        Analyze complete text with per-sentence processing using LOCAL MODELS ONLY
        """
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"local_arabic_analysis_{timestamp}"
        
        self.logger.info(f"🔒 Starting LOCAL-ONLY analysis of text ({len(text)} characters)")
        self.logger.info("✅ No external APIs will be contacted - complete privacy guaranteed")
        
        # Use the local analyzer for complete processing
        return self.local_analyzer.analyze_text(text, base_filename)

def main():
    """Example usage of the LOCAL Arabic Text Analyzer"""
    # Sample Arabic text for testing
    sample_text = """
    مرحباً بكم في نظام تحليل النصوص العربية المحلي الجديد. هذا النظام يعمل بدون إنترنت أو خدمات خارجية.
    يستخدم النظام نماذج محلية فقط لفحص القواعد والمشاعر. جميع العمليات تتم على جهازك المحلي.
    نأمل أن يكون هذا النظام مفيداً لكم في تحليل النصوص العربية بخصوصية تامة وبدون تكلفة.
    """
    
    # Initialize local analyzer
    analyzer = ArabicTextAnalyzer()
    
    # Analyze the text
    results = analyzer.analyze_text(sample_text, "local_sample_test")
    
    print(f"\n🔒 LOCAL-ONLY Analysis Complete!")
    print(f"📊 Total sentences analyzed: {results['total_sentences']}")
    print(f"📁 Individual sentence files: {len(results['sentence_files'])}")
    print(f"🎭 Overall sentiment: {results['summary']['overall_sentiment']}")
    print(f"⚠️  Validation issues: {results['summary']['validation_issues']}")
    print(f"🔧 Grammar suggestions: {results['summary']['grammar_issues']}")
    print(f"📈 Sentiment distribution: {results['summary']['sentiment_distribution']}")
    print(f"🏠 Local models used: {results['summary']['local_models_used']}")
    print(f"✅ Privacy: All processing done locally - no external APIs used!")

if __name__ == "__main__":
    main()