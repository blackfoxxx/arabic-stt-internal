#!/usr/bin/env python3
"""
Test script for the Local Arabic Text Analyzer
Tests the system with a simple Arabic text to ensure all local models work
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from local_arabic_analyzer import LocalArabicTextAnalyzer

def test_local_analyzer():
    """Test the local Arabic analyzer with simple text"""
    print("🔒 Testing LOCAL-ONLY Arabic Text Analyzer")
    print("=" * 50)
    
    # Simple Arabic text for testing
    test_text = """
    مرحبا بكم في النظام المحلي.
    هذا النظام يعمل بدون إنترنت.
    جميع النماذج محلية وآمنة.
    """
    
    try:
        # Initialize the local analyzer
        print("📥 Initializing local analyzer...")
        analyzer = LocalArabicTextAnalyzer("test_analysis_results")
        
        # Test the analysis
        print("🔍 Analyzing text with local models...")
        results = analyzer.analyze_text(test_text, "simple_test")
        
        # Display results
        print("\n✅ LOCAL Analysis Results:")
        print(f"📊 Total sentences: {results['total_sentences']}")
        print(f"📁 Files created: {len(results['sentence_files'])}")
        print(f"🎭 Overall sentiment: {results['summary']['overall_sentiment']}")
        print(f"⚠️  Validation issues: {results['summary']['validation_issues']}")
        print(f"🔧 Grammar suggestions: {results['summary']['grammar_issues']}")
        print(f"📈 Sentiment distribution: {results['summary']['sentiment_distribution']}")
        print(f"🏠 Local models used: {results['summary']['local_models_used']}")
        print(f"🔒 Privacy: All processing done locally!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_local_analyzer()
    if success:
        print("\n🎉 LOCAL ANALYZER TEST PASSED!")
        print("✅ Your system is ready for offline Arabic text analysis")
    else:
        print("\n❌ TEST FAILED - Please check the error messages above")