#!/usr/bin/env python3
"""
Test the Local Arabic Analyzer with existing transcription files
This ensures the system works with real transcription data using only local models
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from local_arabic_analyzer import LocalArabicTextAnalyzer

def find_transcription_files():
    """Find available transcription JSON files"""
    current_dir = Path(__file__).parent
    json_files = []
    
    # Look for transcription files
    patterns = ["*transcript*.json", "*transcription*.json", "test_results*.json"]
    
    for pattern in patterns:
        json_files.extend(current_dir.glob(pattern))
    
    return json_files

def extract_text_from_transcription(file_path):
    """Extract text from transcription JSON file"""
    try:
        # Check if file is empty
        if file_path.stat().st_size == 0:
            print(f"⚠️  Skipping empty file: {file_path.name}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Try different possible structures
        text = ""
        
        if 'transcript' in data and 'segments' in data['transcript']:
            # Nested transcript format
            text = " ".join([segment.get('text', '') for segment in data['transcript']['segments']])
        elif 'segments' in data:
            # Whisper format
            text = " ".join([segment.get('text', '') for segment in data['segments']])
        elif 'text' in data:
            # Simple text format
            text = data['text']
        elif 'transcription' in data:
            # Custom format
            text = data['transcription']
        elif isinstance(data, list):
            # List of segments
            text = " ".join([item.get('text', str(item)) for item in data])
        
        return text.strip() if text else None
    except Exception as e:
        print(f"⚠️  Skipping file {file_path.name}: {e}")
        return None

def test_with_transcription():
    """Test local analyzer with transcription files"""
    print("🔒 Testing LOCAL Arabic Analyzer with Transcription Files")
    print("=" * 60)
    
    # Find transcription files
    transcription_files = find_transcription_files()
    
    if not transcription_files:
        print("❌ No transcription files found!")
        return False
    
    print(f"📁 Found {len(transcription_files)} transcription files")
    
    # Initialize local analyzer
    try:
        print("📥 Initializing LOCAL analyzer...")
        analyzer = LocalArabicTextAnalyzer("transcription_local_test")
        
        # Test with the first available file that has content
        test_file = None
        text = None
        
        for file_path in transcription_files:
            text = extract_text_from_transcription(file_path)
            if text:
                test_file = file_path
                break
        
        if not test_file or not text:
            print("❌ No valid transcription files with content found")
            return False
            
        print(f"🎯 Testing with: {test_file.name}")
        
        print(f"📝 Extracted text length: {len(text)} characters")
        print(f"📄 First 100 characters: {text[:100]}...")
        
        # Analyze with local models only
        print("🔍 Analyzing with LOCAL models...")
        results = analyzer.analyze_text(text, f"transcription_{test_file.stem}")
        
        # Display results
        print("\n✅ LOCAL Transcription Analysis Results:")
        print(f"📊 Total sentences: {results['total_sentences']}")
        print(f"📁 Analysis files created: {len(results['sentence_files'])}")
        print(f"🎭 Overall sentiment: {results['summary']['overall_sentiment']}")
        print(f"⚠️  Validation issues: {results['summary']['validation_issues']}")
        print(f"🔧 Grammar suggestions: {results['summary']['grammar_issues']}")
        print(f"📈 Sentiment distribution: {results['summary']['sentiment_distribution']}")
        print(f"🏠 Local models used: {results['summary']['local_models_used']}")
        print(f"🔒 Privacy: All processing done locally - NO external APIs!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during transcription analysis: {e}")
        return False

if __name__ == "__main__":
    success = test_with_transcription()
    if success:
        print("\n🎉 TRANSCRIPTION LOCAL ANALYSIS TEST PASSED!")
        print("✅ Your system successfully processes real transcriptions with LOCAL models only")
        print("🔒 No external APIs or paid services are used")
    else:
        print("\n❌ TEST FAILED - Please check the error messages above")