#!/usr/bin/env python3
"""
Debug MP3 Processing - Investigate why no segments are produced
"""

import sys
import os
import json
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from local_audio_processor import LocalAudioProcessor

def debug_mp3_processing():
    """Debug MP3 file processing step by step"""
    print("🔍 DEBUG: MP3 Processing Investigation")
    print("=" * 60)
    
    # MP3 file path
    mp3_file = Path("250825-1107_OugfC4aY.mp3")
    
    if not mp3_file.exists():
        print(f"❌ MP3 file not found: {mp3_file}")
        return False
    
    print(f"🎵 Debugging MP3: {mp3_file.name}")
    print(f"📁 File size: {mp3_file.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        # Initialize processor
        print("\n🤖 Step 1: Initialize Audio Processor")
        print("-" * 40)
        
        audio_processor = LocalAudioProcessor()
        
        # Check what models are available
        print("\n📋 Available Models:")
        for model, available in audio_processor.models_available.items():
            status = "✅" if available else "❌"
            print(f"   {status} {model}")
        
        # Check audio file info
        print(f"\n🎵 Step 2: Analyze Audio File")
        print("-" * 40)
        
        try:
            audio_info = audio_processor.analyze_audio_file(str(mp3_file))
            print("Audio Info:")
            for key, value in audio_info.items():
                print(f"   • {key}: {value}")
        except Exception as e:
            print(f"❌ Error analyzing audio: {e}")
            audio_info = {}
        
        # Test Whisper directly if available
        print(f"\n🎤 Step 3: Test Whisper Transcription")
        print("-" * 40)
        
        if audio_processor.models_available["faster_whisper"]:
            print("✅ faster-whisper is available, testing transcription...")
            
            try:
                # Test with minimal options
                options = {
                    "model": "base",  # Use smaller model for testing
                    "language": "ar"
                }
                
                transcription = audio_processor.transcribe_with_whisper(str(mp3_file), options)
                
                print("Transcription Results:")
                print(f"   • Segments: {len(transcription.get('segments', []))}")
                print(f"   • Language: {transcription.get('language', 'Unknown')}")
                print(f"   • Confidence: {transcription.get('confidence', 0):.2f}")
                
                if transcription.get('segments'):
                    print("   • First segment:")
                    first_seg = transcription['segments'][0]
                    for key, value in first_seg.items():
                        print(f"     - {key}: {value}")
                else:
                    print("   • No segments found")
                    
                    # Try with different options
                    print("\n🔄 Trying with different options...")
                    options_alt = {
                        "model": "small",
                        "language": None,  # Auto-detect
                        "task": "transcribe"
                    }
                    
                    transcription_alt = audio_processor.transcribe_with_whisper(str(mp3_file), options_alt)
                    print(f"   • Alternative attempt segments: {len(transcription_alt.get('segments', []))}")
                
            except Exception as e:
                print(f"❌ Error in Whisper transcription: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ faster-whisper not available")
        
        # Test fallback processing
        print(f"\n🔄 Step 4: Test Fallback Processing")
        print("-" * 40)
        
        try:
            fallback_result = audio_processor._fallback_transcription(str(mp3_file), "ar")
            print("Fallback Results:")
            print(f"   • Segments: {len(fallback_result.get('segments', []))}")
            if fallback_result.get('segments'):
                print(f"   • First segment text: {fallback_result['segments'][0].get('text', 'N/A')}")
        except Exception as e:
            print(f"❌ Error in fallback: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_mp3_processing()
    if success:
        print("\n✅ DEBUG COMPLETED")
    else:
        print("\n❌ DEBUG FAILED")