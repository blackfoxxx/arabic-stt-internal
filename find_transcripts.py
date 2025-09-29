import requests
import json
import sys

# Try to get system info first
try:
    response = requests.get("http://localhost:8000/health")
    print("GPU Server Health:", response.json())
except Exception as e:
    print(f"GPU Server not responding: {e}")
    sys.exit(1)

# Since we can't directly access the transcripts dict, let's try common transcript IDs
# Based on the logs, the GPU server generates transcript IDs like "transcript_{timestamp}"
import time
current_time = int(time.time())

# Try recent timestamps (within last hour)
for i in range(3600):  # Last hour
    test_id = f"transcript_{current_time - i}"
    try:
        response = requests.get(f"http://localhost:8000/v1/transcripts/{test_id}")
        data = response.json()
        if "transcript" in data and "segments" in data["transcript"] and len(data["transcript"]["segments"]) > 0:
            print(f" Found transcript: {test_id}")
            print(f" Segments: {len(data['transcript']['segments'])}")
            
            # Save the complete data
            with open(f"found_transcript_{test_id}.json", "w", encoding="utf-8") as f:
                json.dump(data["transcript"], f, ensure_ascii=False, indent=2)
            
            # Create readable text file
            transcript = data["transcript"]
            text_output = f"""Arabic Speech-to-Text Complete Transcription Results
================================================================

Transcript ID: {transcript['id']}
GPU Processed: {transcript.get('gpu_processed', False)}
Model Used: {transcript.get('model_used', 'unknown')}
Device: {transcript.get('device', 'unknown')}
Total Segments: {len(transcript['segments'])}

COMPLETE TRANSCRIPTION WITH ALL SEGMENTS:
=========================================

"""
            
            for idx, segment in enumerate(transcript['segments']):
                text_output += f"[{idx+1:03d}] {segment['start']}s - {segment['end']}s\n"
                text_output += f"Speaker: {segment.get('speaker_id', 'Unknown')}\n"
                text_output += f"Confidence: {segment.get('confidence', 0)*100:.1f}%\n"
                text_output += f"Text: {segment['text']}\n\n"
            
            with open(f"complete_transcription_{test_id}.txt", "w", encoding="utf-8") as f:
                f.write(text_output)
            
            print(f" Complete transcription saved to: complete_transcription_{test_id}.txt")
            print(f" JSON data saved to: found_transcript_{test_id}.json")
            break
    except:
        continue
else:
    print(" No transcripts found in GPU server storage")
