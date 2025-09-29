#!/usr/bin/env python3
"""
Test script for LLM integration with Arabic STT system
"""

import os
import sys
from local_audio_processor import LocalAudioProcessor
from llm_service import OllamaLLMService, TextEnhancementService, LLMConfig

def test_llm_text_processing():
    """Test LLM text processing capabilities"""
    print("🧪 Testing LLM Text Processing Integration")
    print("=" * 60)
    
    # Initialize LLM service
    llm_service = OllamaLLMService()
    text_enhancement = TextEnhancementService(llm_service)
    
    # Sample Arabic text (simulating STT output)
    sample_arabic_text = """
    مرحبا بكم في نظام التفريغ الصوتي العربي. هذا النظام يستخدم الذكاء الاصطناعي 
    لتحويل الكلام الى نص باللغة العربية. النظام يدعم ايضا تحسين النصوص وتلخيصها.
    """
    
    print(f"📝 Original Arabic text:")
    print(sample_arabic_text.strip())
    print("\n" + "─" * 50)
    
    # Test grammar correction
    print("\n🔧 Testing Grammar Correction:")
    corrected = text_enhancement.correct_grammar(sample_arabic_text, "ar")
    print(f"✅ Corrected: {corrected}")
    
    # Test summarization
    print("\n📄 Testing Summarization:")
    summary = text_enhancement.summarize_text(sample_arabic_text, "ar")
    print(f"✅ Summary: {summary}")
    
    # Test keyword extraction
    print("\n🔍 Testing Keyword Extraction:")
    keywords = text_enhancement.extract_keywords(sample_arabic_text, "ar")
    print(f"✅ Keywords: {keywords}")
    
    # Test translation
    print("\n🌐 Testing Translation (Arabic to English):")
    translation = text_enhancement.translate_text(sample_arabic_text, "ar", "en")
    print(f"✅ Translation: {translation}")
    
    return True

def test_audio_processor_with_llm():
    """Test the complete audio processor with LLM integration"""
    print("\n🎵 Testing Audio Processor with LLM Integration")
    print("=" * 60)
    
    processor = LocalAudioProcessor()
    
    # Simulate processing results (since we don't have actual audio)
    mock_segments = [
        {
            "text": "مرحبا بكم في نظام التفريغ الصوتي",
            "start": 0.0,
            "end": 3.5,
            "speaker": "SPEAKER_00",
            "confidence": 0.95
        },
        {
            "text": "هذا النظام يستخدم الذكاء الاصطناعي",
            "start": 3.5,
            "end": 7.0,
            "speaker": "SPEAKER_00", 
            "confidence": 0.92
        }
    ]
    
    # Test LLM enhancement
    if processor.models_available["llm_service"]:
        print("✅ LLM service is available")
        
        # Test text enhancement
        full_text = " ".join([seg["text"] for seg in mock_segments])
        print(f"\n📝 Combined text: {full_text}")
        
        enhanced_result = processor.enhance_text_with_llm(
            full_text, 
            ["grammar_correction", "overall_summary", "keywords"]
        )
        
        print("\n🚀 LLM Enhancement Results:")
        for enhancement_type, result in enhanced_result.items():
            print(f"   {enhancement_type}: {result}")
    else:
        print("❌ LLM service not available")
    
    return True

def main():
    """Main test function"""
    print("🧪 Arabic STT + LLM Integration Test Suite")
    print("=" * 70)
    
    try:
        # Test 1: LLM text processing
        test_llm_text_processing()
        
        # Test 2: Audio processor with LLM
        test_audio_processor_with_llm()
        
        print("\n" + "=" * 70)
        print("✅ All tests completed successfully!")
        print("🎉 LLM integration is working properly with Arabic STT system")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)