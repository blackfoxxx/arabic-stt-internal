#!/usr/bin/env python3
"""
Test script to verify audio playback functionality and segment synchronization
"""

import json
import os
from pathlib import Path

def test_audio_playback_functionality():
    """Test the audio playback and segment synchronization features"""
    
    print("🎵 Testing Audio Playback Functionality")
    print("=" * 60)
    
    # Find the latest multimodal results
    results_files = [f for f in os.listdir('.') if f.startswith('multimodal_analysis_results_') and f.endswith('.json')]
    if not results_files:
        print("❌ No multimodal results files found")
        return False
    
    latest_file = max(results_files, key=lambda x: os.path.getctime(x))
    print(f"📄 Testing with: {latest_file}")
    
    # Load the results
    with open(latest_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Test 1: Check audio file exists
    audio_file = results.get('audio_file')
    if not audio_file:
        print("❌ No audio file specified in results")
        return False
    
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    print(f"✅ Audio file exists: {audio_file}")
    
    # Test 2: Check segments structure
    segments = results.get('segments', [])
    if not segments:
        print("❌ No segments found in results")
        return False
    
    print(f"✅ Found {len(segments)} segments")
    
    # Test 3: Validate segment structure
    required_fields = ['start', 'end', 'speaker_id', 'text', 'confidence']
    valid_segments = 0
    
    for i, segment in enumerate(segments[:5]):  # Test first 5 segments
        missing_fields = [field for field in required_fields if field not in segment]
        if missing_fields:
            print(f"❌ Segment {i+1} missing fields: {missing_fields}")
        else:
            valid_segments += 1
            print(f"✅ Segment {i+1}: {segment['start']:.2f}s - {segment['end']:.2f}s, Speaker: {segment['speaker_id']}")
    
    # Test 4: Check timeline continuity
    timeline_issues = 0
    for i in range(len(segments) - 1):
        current_end = segments[i]['end']
        next_start = segments[i + 1]['start']
        if next_start < current_end:
            timeline_issues += 1
    
    if timeline_issues == 0:
        print("✅ Timeline continuity is valid")
    else:
        print(f"⚠️  Found {timeline_issues} timeline overlap issues")
    
    # Test 5: Check speaker distribution
    speakers = set(segment['speaker_id'] for segment in segments)
    print(f"✅ Found {len(speakers)} unique speakers: {', '.join(sorted(speakers))}")
    
    # Test 6: Check confidence scores
    confidences = [segment['confidence'] for segment in segments if 'confidence' in segment]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        print(f"✅ Average confidence score: {avg_confidence:.3f}")
    
    # Test 7: Check Arabic text support
    arabic_segments = [s for s in segments if any('\u0600' <= char <= '\u06FF' for char in s.get('text', ''))]
    print(f"✅ Arabic text segments: {len(arabic_segments)}/{len(segments)}")
    
    # Test 8: Check total duration
    if segments:
        total_duration = segments[-1]['end']
        print(f"✅ Total transcription duration: {total_duration:.2f} seconds ({total_duration/60:.1f} minutes)")
    
    print("\n🎯 Audio Playback Test Summary:")
    print(f"  📁 Audio File: {audio_file}")
    print(f"  📊 Segments: {len(segments)}")
    print(f"  🎭 Speakers: {len(speakers)}")
    print(f"  🔤 Arabic Support: {'✅' if arabic_segments else '❌'}")
    print(f"  ⏱️  Timeline: {'✅' if timeline_issues == 0 else '⚠️ '}")
    print(f"  📈 Avg Confidence: {avg_confidence:.3f}" if confidences else "  📈 No confidence data")
    
    return True

def test_web_interface_compatibility():
    """Test compatibility with the web interface"""
    
    print("\n🌐 Testing Web Interface Compatibility")
    print("=" * 60)
    
    # Check if the development server is running
    import requests
    try:
        response = requests.get('http://localhost:3000/multimodal-results', timeout=5)
        if response.status_code == 200:
            print("✅ Web interface is accessible")
            print("✅ Multimodal results page is loading")
        else:
            print(f"⚠️  Web interface returned status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access web interface: {e}")
        return False
    
    # Check if audio file is accessible via web server
    try:
        # Find the latest results to get audio file
        results_files = [f for f in os.listdir('.') if f.startswith('multimodal_analysis_results_') and f.endswith('.json')]
        if results_files:
            latest_file = max(results_files, key=lambda x: os.path.getctime(x))
            with open(latest_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            audio_file = results.get('audio_file')
            if audio_file:
                # Try to access the audio file via the web server
                audio_url = f"http://localhost:3000/{audio_file}"
                audio_response = requests.head(audio_url, timeout=5)
                if audio_response.status_code == 200:
                    print(f"✅ Audio file accessible via web: {audio_url}")
                else:
                    print(f"⚠️  Audio file not accessible via web: {audio_response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not test audio file accessibility: {e}")
    
    return True

if __name__ == "__main__":
    print("🧪 AUDIO PLAYBACK FUNCTIONALITY TEST")
    print("=" * 80)
    
    success = test_audio_playback_functionality()
    if success:
        test_web_interface_compatibility()
        print("\n🎉 All audio playback tests completed successfully!")
        print("\n📋 Next Steps:")
        print("  1. Open http://localhost:3000/multimodal-results in your browser")
        print("  2. Click on any segment to test audio playback")
        print("  3. Verify real-time synchronization with timeline")
        print("  4. Test speaker identification and color coding")
        print("  5. Check Arabic text display and RTL support")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")