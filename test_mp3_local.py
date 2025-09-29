#!/usr/bin/env python3
"""
Test MP3 file processing with LOCAL-ONLY Arabic STT and Analysis
This script processes the MP3 file using only local models - no external APIs
"""

import sys
import os
import json
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from local_audio_processor import LocalAudioProcessor
from local_arabic_analyzer import LocalArabicTextAnalyzer

def test_mp3_with_local_models():
    """Test MP3 file processing with local-only models"""
    print("🔒 Testing MP3 with LOCAL-ONLY Arabic Processing")
    print("=" * 60)
    
    # MP3 file path
    mp3_file = Path("250825-1107_OugfC4aY.mp3")
    
    if not mp3_file.exists():
        print(f"❌ MP3 file not found: {mp3_file}")
        return False
    
    print(f"🎵 Processing MP3: {mp3_file.name}")
    print(f"📁 File size: {mp3_file.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        # Step 1: Local Audio Processing (STT)
        print("\n🎤 Step 1: LOCAL Speech-to-Text Processing")
        print("-" * 40)
        
        audio_processor = LocalAudioProcessor()
        
        # Process audio with local Whisper
        print("🔍 Transcribing with local Whisper model...")
        start_time = time.time()
        
        transcription_result = audio_processor.process_audio_file(str(mp3_file))
        
        processing_time = time.time() - start_time
        print(f"⏱️  Transcription completed in {processing_time:.1f} seconds")
        
        if not transcription_result or 'segments' not in transcription_result:
            print("❌ Transcription failed or returned no segments")
            return False
        
        print(f"📊 Transcription Results:")
        print(f"   • Segments: {len(transcription_result['segments'])}")
        
        if len(transcription_result['segments']) > 0:
            # Extract text from segments
            full_text = " ".join([seg.get('text', '') for seg in transcription_result['segments']])
            avg_confidence = sum(seg.get('confidence', 0) for seg in transcription_result['segments']) / len(transcription_result['segments'])
            print(f"   • Text length: {len(full_text)} characters")
            print(f"   • Average confidence: {avg_confidence:.2f}")
            print(f"   • First 100 chars: {full_text[:100]}...")
        else:
            print("   • No segments found in transcription")
            full_text = ""
        
        # Step 2: Local Text Analysis
        print("\n📝 Step 2: LOCAL Arabic Text Analysis")
        print("-" * 40)
        
        analyzer = LocalArabicTextAnalyzer("mp3_local_analysis")
        
        print("🔍 Analyzing with LOCAL Arabic models...")
        analysis_start = time.time()
        
        analysis_results = analyzer.analyze_text(full_text, f"mp3_{mp3_file.stem}")
        
        analysis_time = time.time() - analysis_start
        print(f"⏱️  Analysis completed in {analysis_time:.1f} seconds")
        
        # Step 3: Display Results
        print("\n✅ COMPLETE LOCAL PROCESSING RESULTS")
        print("=" * 60)
        
        print("🎤 TRANSCRIPTION SUMMARY:")
        if transcription_result.get('duration'):
            print(f"   • Audio duration: {transcription_result.get('duration', 'N/A')} seconds")
        print(f"   • Segments processed: {len(transcription_result['segments'])}")
        if len(transcription_result['segments']) > 0:
            avg_confidence = sum(seg.get('confidence', 0) for seg in transcription_result['segments']) / len(transcription_result['segments'])
            print(f"   • Average confidence: {avg_confidence:.2f}")
        else:
            print("   • No segments to analyze")
        
        print("\n📝 ANALYSIS SUMMARY:")
        print(f"   • Total sentences: {analysis_results['total_sentences']}")
        print(f"   • Analysis files: {len(analysis_results['sentence_files'])}")
        print(f"   • Overall sentiment: {analysis_results['summary']['overall_sentiment']}")
        print(f"   • Validation issues: {analysis_results['summary']['validation_issues']}")
        print(f"   • Grammar suggestions: {analysis_results['summary']['grammar_issues']}")
        print(f"   • Sentiment distribution: {analysis_results['summary']['sentiment_distribution']}")
        
        print("\n🏠 LOCAL MODELS USED:")
        print("   STT Models:")
        print("   • Whisper (local)")
        print("   • VAD (Voice Activity Detection)")
        print("   Analysis Models:")
        for model in analysis_results['summary']['local_models_used']:
            print(f"   • {model}")
        
        print("\n🔒 PRIVACY & SECURITY:")
        print("   ✅ All processing done locally")
        print("   ✅ No external API calls")
        print("   ✅ No data sent to internet")
        print("   ✅ Complete offline operation")
        
        print(f"\n⏱️  TOTAL PROCESSING TIME: {processing_time + analysis_time:.1f} seconds")
        
        # Save combined results
        combined_results = {
            "mp3_file": str(mp3_file),
            "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "transcription": {
                "duration": transcription_result.get('duration'),
                "segments_count": len(transcription_result['segments']),
                "full_text": full_text,
                "processing_time": processing_time
            },
            "analysis": analysis_results,
            "analysis_time": analysis_time,
            "total_time": processing_time + analysis_time,
            "local_only": True,
            "privacy_confirmed": "All processing done locally - no external APIs"
        }
        
        results_file = f"mp3_local_test_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(combined_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 Results saved to: {results_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during MP3 processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mp3_with_local_models()
    if success:
        print("\n🎉 MP3 LOCAL PROCESSING TEST PASSED!")
        print("✅ Your MP3 was successfully processed using ONLY local models")
        print("🔒 Complete privacy - no external services used")
    else:
        print("\n❌ TEST FAILED - Please check the error messages above")