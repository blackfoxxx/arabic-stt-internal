#!/usr/bin/env python3
"""
Test script to verify improved transcription quality
"""
import requests
import json
import time
from pathlib import Path

def test_improved_transcription():
    """Test the improved transcription processing"""
    
    # Check if GPU server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ GPU server is not running properly")
            return
        print("✅ GPU server is running")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to GPU server: {e}")
        return
    
    # Find the most recent transcript
    try:
        # Try to get the specific transcript we know exists
        transcript_id = "transcript_1759031089"
        response = requests.get(f"http://localhost:8000/v1/transcripts/{transcript_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            segments = data.get('segments', [])
            
            print(f"\n📊 Transcript Analysis for {transcript_id}:")
            print(f"Total segments: {len(segments)}")
            
            if segments:
                # Analyze confidence scores
                confidences = [seg.get('confidence', 0) for seg in segments]
                avg_confidence = sum(confidences) / len(confidences)
                low_confidence_count = sum(1 for c in confidences if c < 0.3)
                
                print(f"Average confidence: {avg_confidence:.2f}")
                print(f"Low confidence segments (< 0.3): {low_confidence_count}")
                
                # Check for repetitive segments
                texts = [seg.get('text', '').strip() for seg in segments]
                unique_texts = set(texts)
                repetition_ratio = 1 - (len(unique_texts) / len(texts))
                
                print(f"Text repetition ratio: {repetition_ratio:.2f}")
                
                # Show sample segments around the problematic area (segments 346-348)
                print(f"\n🔍 Sample segments around position 346-348:")
                start_idx = max(0, 340)
                end_idx = min(len(segments), 355)
                
                for i in range(start_idx, end_idx):
                    if i < len(segments):
                        seg = segments[i]
                        print(f"  Segment {i+1}: {seg.get('start', 0):.2f}s-{seg.get('end', 0):.2f}s")
                        print(f"    Text: '{seg.get('text', '').strip()}'")
                        print(f"    Confidence: {seg.get('confidence', 0):.2f}")
                        print(f"    Speaker: {seg.get('speaker_id', 'N/A')}")
                        print()
                
                # Save improved results
                output_file = f"IMPROVED_TRANSCRIPTION_{transcript_id}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Improved Arabic Transcription Results\n")
                    f.write(f"=====================================\n\n")
                    f.write(f"Transcript ID: {transcript_id}\n")
                    f.write(f"Total Segments: {len(segments)}\n")
                    f.write(f"Average Confidence: {avg_confidence:.2f}\n")
                    f.write(f"Low Confidence Segments: {low_confidence_count}\n")
                    f.write(f"Text Repetition Ratio: {repetition_ratio:.2f}\n\n")
                    f.write("Segments:\n")
                    f.write("---------\n\n")
                    
                    for i, seg in enumerate(segments):
                        f.write(f"Segment {i+1}:\n")
                        f.write(f"  Time: {seg.get('start', 0):.2f}s - {seg.get('end', 0):.2f}s\n")
                        f.write(f"  Text: {seg.get('text', '').strip()}\n")
                        f.write(f"  Confidence: {seg.get('confidence', 0):.2f}\n")
                        f.write(f"  Speaker: {seg.get('speaker_id', 'N/A')}\n\n")
                
                print(f"✅ Improved transcription saved to: {output_file}")
                
            else:
                print("❌ No segments found in transcript")
        else:
            print(f"❌ Could not retrieve transcript: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error retrieving transcript: {e}")

if __name__ == "__main__":
    test_improved_transcription()