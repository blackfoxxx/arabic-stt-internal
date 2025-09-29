#!/usr/bin/env python3
"""
Test script for specific MP3 file: 250825-1107_OugfC4aY.mp3
Tests the enhanced audio quality system with the user's specific audio file.
"""

import requests
import json
import time
import os
from pathlib import Path

def test_specific_mp3_file():
    """Test the specific MP3 file through the enhanced audio quality system."""
    
    # Configuration
    server_url = "http://localhost:8000"
    mp3_file_path = "250825-1107_OugfC4aY.mp3"
    
    print("🎵 Testing Enhanced Audio Quality System")
    print("=" * 50)
    print(f"📁 File: {mp3_file_path}")
    
    # Check if file exists
    if not os.path.exists(mp3_file_path):
        print(f"❌ Error: File '{mp3_file_path}' not found!")
        print("Please ensure the file is in the current directory.")
        return
    
    # Get file info
    file_size = os.path.getsize(mp3_file_path)
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    try:
        print("\n🚀 Uploading and processing audio...")
        
        # Upload and process the audio file
        with open(mp3_file_path, 'rb') as audio_file:
            files = {'file': (mp3_file_path, audio_file, 'audio/mpeg')}
            data = {
                'language': 'ar',
                'model_size': 'large-v3',
                'enable_diarization': 'true',
                'num_speakers': '3'
            }
            
            start_time = time.time()
            response = requests.post(f"{server_url}/v1/upload-and-process", files=files, data=data)
            processing_time = time.time() - start_time
            
        if response.status_code == 200:
            result = response.json()
            transcript_id = result.get('transcript_id')
            
            print(f"✅ Upload successful!")
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"🆔 Transcript ID: {transcript_id}")
            
            # Wait a moment for processing to complete
            print("\n⏳ Waiting for processing to complete...")
            time.sleep(2)
            
            # Retrieve the full transcript
            print("\n📥 Retrieving transcript...")
            transcript_response = requests.get(f"{server_url}/v1/transcripts/{transcript_id}")
            
            if transcript_response.status_code == 200:
                transcript_data = transcript_response.json()
                
                print("\n📊 TRANSCRIPTION RESULTS")
                print("=" * 50)
                
                # Display processing information
                processing_info = transcript_data.get('processing_info', {})
                print(f"🖥️  GPU Processed: {processing_info.get('gpu_processed', 'Unknown')}")
                print(f"🤖 Model Used: {processing_info.get('model_used', 'Unknown')}")
                print(f"⚡ Processing Method: {processing_info.get('processing_method', 'Unknown')}")
                
                # Display audio quality metrics
                original_quality = transcript_data.get('original_audio_quality', {})
                enhanced_quality = transcript_data.get('enhanced_audio_quality', {})
                
                print(f"\n🎵 AUDIO QUALITY METRICS")
                print("=" * 30)
                print(f"📈 Original Quality: {original_quality.get('overall_quality', 'Unknown')}")
                print(f"📊 Original Score: {original_quality.get('quality_score', 'Unknown')}/100")
                print(f"🔊 Original SNR: {original_quality.get('snr_db', 'Unknown')} dB")
                
                print(f"✨ Enhanced Quality: {enhanced_quality.get('overall_quality', 'Unknown')}")
                print(f"📊 Enhanced Score: {enhanced_quality.get('quality_score', 'Unknown')}/100")
                print(f"🔊 Enhanced SNR: {enhanced_quality.get('snr_db', 'Unknown')} dB")
                
                # Display transcript segments
                transcript = transcript_data.get('transcript', {})
                segments = transcript.get('segments', [])
                
                print(f"\n📝 TRANSCRIPT SEGMENTS")
                print("=" * 30)
                print(f"📊 Total segments: {len(segments)}")
                
                if segments:
                    print(f"⏱️  Total duration: {segments[-1].get('end', 0):.2f} seconds")
                    
                    # Show first few segments
                    print("\n🎤 Sample segments:")
                    for i, segment in enumerate(segments[:5]):
                        start_time = segment.get('start', 0)
                        end_time = segment.get('end', 0)
                        text = segment.get('text', '').strip()
                        confidence = segment.get('avg_logprob', 0)
                        speaker = segment.get('speaker', 'Unknown')
                        
                        print(f"  [{i+1}] {start_time:.1f}s-{end_time:.1f}s | Speaker: {speaker}")
                        print(f"      Confidence: {confidence:.3f} | Text: {text}")
                        print()
                    
                    if len(segments) > 5:
                        print(f"... and {len(segments) - 5} more segments")
                    
                    # Calculate average confidence
                    confidences = [seg.get('avg_logprob', 0) for seg in segments if seg.get('avg_logprob')]
                    if confidences:
                        avg_confidence = sum(confidences) / len(confidences)
                        print(f"\n📊 Average confidence: {avg_confidence:.3f}")
                    
                    # Show full text
                    full_text = ' '.join([seg.get('text', '').strip() for seg in segments])
                    print(f"\n📄 FULL TRANSCRIPT")
                    print("=" * 30)
                    print(full_text[:500] + ("..." if len(full_text) > 500 else ""))
                    
                else:
                    print("⚠️  No segments found in transcript")
                
                # Save detailed results
                output_file = f"test_results_{transcript_id}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(transcript_data, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Detailed results saved to: {output_file}")
                
            else:
                print(f"❌ Failed to retrieve transcript: {transcript_response.status_code}")
                print(transcript_response.text)
        
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the GPU server!")
        print("Please ensure the GPU server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_specific_mp3_file()