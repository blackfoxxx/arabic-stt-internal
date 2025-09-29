import requests
import json
import time

# The exact transcript ID we know exists
transcript_id = "transcript_1759031089"

print(f" Searching for transcript: {transcript_id}")

# Try the GPU server first
try:
    response = requests.get(f"http://localhost:8000/v1/transcripts/{transcript_id}")
    if response.status_code == 200:
        data = response.json()
        if "transcript" in data and data["transcript"].get("segments"):
            print(f" Found in GPU server: {len(data['transcript']['segments'])} segments")
            
            # Save complete results
            with open(f"COMPLETE_TRANSCRIPTION_{transcript_id}.json", "w", encoding="utf-8") as f:
                json.dump(data["transcript"], f, ensure_ascii=False, indent=2)
            
            # Create readable text file
            transcript = data["transcript"]
            text_output = f"""COMPLETE ARABIC TRANSCRIPTION RESULTS
====================================

Transcript ID: {transcript['id']}
GPU Processed: {transcript.get('gpu_processed', False)}
Model Used: {transcript.get('model_used', 'unknown')}
Device: {transcript.get('device', 'unknown')}
Total Segments: {len(transcript['segments'])}

FULL TRANSCRIPTION (ALL SEGMENTS):
=================================

"""
            
            for idx, segment in enumerate(transcript['segments']):
                text_output += f"[{idx+1:03d}] {segment['start']:.2f}s - {segment['end']:.2f}s\n"
                text_output += f"Speaker: {segment.get('speaker_id', 'Unknown')}\n"
                text_output += f"Confidence: {segment.get('confidence', 0)*100:.1f}%\n"
                text_output += f"Text: {segment['text']}\n"
                text_output += "-" * 50 + "\n\n"
            
            with open(f"COMPLETE_TRANSCRIPTION_{transcript_id}.txt", "w", encoding="utf-8") as f:
                f.write(text_output)
            
            print(f" COMPLETE transcription saved to: COMPLETE_TRANSCRIPTION_{transcript_id}.txt")
            print(f" JSON data saved to: COMPLETE_TRANSCRIPTION_{transcript_id}.json")
            exit(0)
        else:
            print(" No segments found in GPU server response")
    else:
        print(f" GPU server returned: {response.status_code}")
except Exception as e:
    print(f" GPU server error: {e}")

# Try the Next.js API
try:
    response = requests.get(f"http://localhost:3000/api/transcripts/{transcript_id}")
    if response.status_code == 200:
        data = response.json()
        if data.get("segments"):
            print(f" Found in Next.js API: {len(data['segments'])} segments")
            
            # Save complete results
            with open(f"COMPLETE_TRANSCRIPTION_{transcript_id}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Create readable text file
            text_output = f"""COMPLETE ARABIC TRANSCRIPTION RESULTS
====================================

Transcript ID: {data['id']}
Filename: {data.get('filename', 'Unknown')}
Status: {data.get('status', 'Unknown')}
Language: {data.get('language', 'ar')}
Model Used: {data.get('model_used', 'Unknown')}
Confidence Score: {data.get('confidence_score', 0)*100:.1f}%
Processing Time: {data.get('processing_time', 0):.2f}s
Total Segments: {len(data['segments'])}

FULL TRANSCRIPTION (ALL SEGMENTS):
=================================

"""
            
            for idx, segment in enumerate(data['segments']):
                text_output += f"[{idx+1:03d}] {segment['start']:.2f}s - {segment['end']:.2f}s\n"
                text_output += f"Speaker: {segment.get('speaker_id', 'Unknown')}\n"
                text_output += f"Confidence: {segment.get('confidence', 0)*100:.1f}%\n"
                text_output += f"Text: {segment['text']}\n"
                text_output += "-" * 50 + "\n\n"
            
            with open(f"COMPLETE_TRANSCRIPTION_{transcript_id}.txt", "w", encoding="utf-8") as f:
                f.write(text_output)
            
            print(f" COMPLETE transcription saved to: COMPLETE_TRANSCRIPTION_{transcript_id}.txt")
            print(f" JSON data saved to: COMPLETE_TRANSCRIPTION_{transcript_id}.json")
            exit(0)
        else:
            print(" No segments found in Next.js API response")
    else:
        print(f" Next.js API returned: {response.status_code}")
except Exception as e:
    print(f" Next.js API error: {e}")

print(" Could not find the complete transcription in any storage location")
