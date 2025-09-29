#!/usr/bin/env python3
"""
Create a test audio file for testing improved transcription
"""
import requests
import json
import os
from pathlib import Path

def create_test_transcription():
    """Create a test transcription using the improved GPU server"""
    
    # Check if we have any existing audio files
    audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
    audio_files = []
    
    # Look for audio files in the current directory and parent directories
    search_dirs = [
        Path('.'),
        Path('..'),
        Path('../..'),
        Path('uploads'),
        Path('../uploads'),
        Path('D:/AI SST/arabic-stt-internal/uploads')
    ]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            for ext in audio_extensions:
                audio_files.extend(list(search_dir.glob(f'*{ext}')))
                audio_files.extend(list(search_dir.glob(f'**/*{ext}')))
    
    if not audio_files:
        print("❌ No audio files found for testing")
        print("Please place an Arabic audio file in the current directory or uploads folder")
        return
    
    # Use the first audio file found
    audio_file = audio_files[0]
    print(f"🎵 Using audio file: {audio_file}")
    
    # Test the improved transcription
    try:
        url = "http://localhost:8000/v1/upload-and-process"
        
        with open(audio_file, 'rb') as f:
            files = {'file': (audio_file.name, f, 'audio/wav')}
            data = {
                'model': 'large-v3',
                'language': 'ar'
            }
            
            print("🔄 Starting improved transcription...")
            response = requests.post(url, files=files, data=data, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                transcript_id = result.get('transcript_id')
                
                print(f"✅ Transcription completed!")
                print(f"📋 Transcript ID: {transcript_id}")
                
                # Get the full results
                if transcript_id:
                    transcript_response = requests.get(f"http://localhost:8000/v1/transcripts/{transcript_id}")
                    if transcript_response.status_code == 200:
                        transcript_data = transcript_response.json()
                        segments = transcript_data.get('segments', [])
                        
                        print(f"\n📊 Improved Transcription Analysis:")
                        print(f"Total segments: {len(segments)}")
                        
                        if segments:
                            # Analyze quality improvements
                            confidences = [seg.get('confidence', 0) for seg in segments]
                            avg_confidence = sum(confidences) / len(confidences)
                            low_confidence_count = sum(1 for c in confidences if c < 0.3)
                            
                            print(f"Average confidence: {avg_confidence:.2f}")
                            print(f"Low confidence segments (< 0.3): {low_confidence_count}")
                            print(f"Percentage of high-quality segments: {((len(segments) - low_confidence_count) / len(segments) * 100):.1f}%")
                            
                            # Check for repetitive segments
                            texts = [seg.get('text', '').strip() for seg in segments]
                            unique_texts = set(texts)
                            repetition_ratio = 1 - (len(unique_texts) / len(texts)) if texts else 0
                            
                            print(f"Text repetition ratio: {repetition_ratio:.2f}")
                            
                            # Show first few segments
                            print(f"\n🔍 First 10 segments:")
                            for i, seg in enumerate(segments[:10]):
                                print(f"  Segment {i+1}: {seg.get('start', 0):.2f}s-{seg.get('end', 0):.2f}s")
                                print(f"    Text: '{seg.get('text', '').strip()}'")
                                print(f"    Confidence: {seg.get('confidence', 0):.2f}")
                                print(f"    Speaker: {seg.get('speaker_id', 'N/A')}")
                                print()
                            
                            # Save results
                            output_file = f"IMPROVED_TEST_TRANSCRIPTION_{transcript_id}.txt"
                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write(f"Improved Arabic Transcription Test Results\n")
                                f.write(f"==========================================\n\n")
                                f.write(f"Audio File: {audio_file.name}\n")
                                f.write(f"Transcript ID: {transcript_id}\n")
                                f.write(f"Total Segments: {len(segments)}\n")
                                f.write(f"Average Confidence: {avg_confidence:.2f}\n")
                                f.write(f"Low Confidence Segments: {low_confidence_count}\n")
                                f.write(f"High Quality Percentage: {((len(segments) - low_confidence_count) / len(segments) * 100):.1f}%\n")
                                f.write(f"Text Repetition Ratio: {repetition_ratio:.2f}\n\n")
                                f.write("Improvements Made:\n")
                                f.write("- Added confidence filtering (removes segments < 0.3 confidence)\n")
                                f.write("- Added duration filtering (removes segments < 0.5 seconds)\n")
                                f.write("- Improved VAD filtering to reduce noise\n")
                                f.write("- Added post-processing to merge similar consecutive segments\n")
                                f.write("- Better speaker diarization with 3 speakers instead of 2\n")
                                f.write("- Reduced repetition with condition_on_previous_text=False\n\n")
                                f.write("All Segments:\n")
                                f.write("=============\n\n")
                                
                                for i, seg in enumerate(segments):
                                    f.write(f"Segment {i+1}:\n")
                                    f.write(f"  Time: {seg.get('start', 0):.2f}s - {seg.get('end', 0):.2f}s\n")
                                    f.write(f"  Text: {seg.get('text', '').strip()}\n")
                                    f.write(f"  Confidence: {seg.get('confidence', 0):.2f}\n")
                                    f.write(f"  Speaker: {seg.get('speaker_id', 'N/A')}\n\n")
                            
                            print(f"✅ Test results saved to: {output_file}")
                            
                            # Also save JSON
                            json_file = f"IMPROVED_TEST_TRANSCRIPTION_{transcript_id}.json"
                            with open(json_file, 'w', encoding='utf-8') as f:
                                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
                            
                            print(f"✅ Raw JSON saved to: {json_file}")
                        
                        else:
                            print("❌ No segments found in improved transcription")
                    else:
                        print(f"❌ Could not retrieve improved transcript: {transcript_response.status_code}")
                
            else:
                print(f"❌ Transcription failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during transcription: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    create_test_transcription()