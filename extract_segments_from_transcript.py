import json
import re

def extract_segments_from_full_transcript():
    """Extract structured segments from the latest transcript file"""
    
    # Find the latest transcript and results files
    import os
    
    # Find latest transcript file
    transcript_files = [f for f in os.listdir('.') if f.startswith('full_transcript_') and f.endswith('.json')]
    if not transcript_files:
        print("❌ No transcript files found")
        return
    transcript_file = max(transcript_files, key=lambda x: os.path.getctime(x))
    
    # Find latest results file
    results_files = [f for f in os.listdir('.') if f.startswith('multimodal_analysis_results_') and f.endswith('.json')]
    if not results_files:
        print("❌ No multimodal results files found")
        return
    results_file = max(results_files, key=lambda x: os.path.getctime(x))
    
    print(f"📄 Using transcript: {transcript_file}")
    print(f"📄 Using results: {results_file}")
    
    # Load the full transcript
    with open(transcript_file, 'r', encoding='utf-8') as f:
        full_transcript = json.load(f)
    
    # Load existing multimodal results
    with open(results_file, 'r', encoding='utf-8') as f:
        multimodal_results = json.load(f)
    
    # Extract segments from the full transcription text
    full_text = full_transcript.get('full_transcription', '')
    
    # Split text into sentences and create segments
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Calculate approximate timing based on total duration
    total_duration = full_transcript.get('duration', 3903.2163125)
    total_segments = len(sentences)
    
    segments = []
    current_time = 0.0
    
    for i, sentence in enumerate(sentences):
        # Estimate segment duration based on text length
        words_count = len(sentence.split())
        # Average speaking rate: ~2-3 words per second in Arabic
        segment_duration = max(1.0, words_count / 2.5)
        
        # Adjust for remaining time
        if i == len(sentences) - 1:
            segment_duration = total_duration - current_time
        
        # Assign speaker based on content patterns (simple heuristic)
        speaker_id = "SPEAKER_00"
        if any(word in sentence for word in ["نعم", "أجل", "صحيح", "طبعا"]):
            speaker_id = "SPEAKER_01"
        elif any(word in sentence for word in ["لا", "كلا", "ليس"]):
            speaker_id = "SPEAKER_02"
        
        segment = {
            "id": f"seg_{i+1}",
            "start": round(current_time, 2),
            "end": round(current_time + segment_duration, 2),
            "text": sentence,
            "confidence": 0.85,  # Default confidence
            "speaker_id": speaker_id
        }
        
        segments.append(segment)
        current_time += segment_duration
    
    # Update multimodal results with segments
    multimodal_results['segments'] = segments
    
    # Update transcription info
    if 'transcription_info' not in multimodal_results:
        multimodal_results['transcription_info'] = {}
    
    multimodal_results['transcription_info']['total_segments'] = len(segments)
    
    # Save updated results
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(multimodal_results, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully extracted {len(segments)} segments from transcript")
    print(f"Total duration: {total_duration:.2f} seconds")
    print(f"Average segment duration: {total_duration/len(segments):.2f} seconds")
    
    # Show first few segments as preview
    print("\nFirst 3 segments:")
    for i, segment in enumerate(segments[:3]):
        print(f"Segment {i+1}: {segment['start']:.2f}s - {segment['end']:.2f}s")
        print(f"  Speaker: {segment['speaker_id']}")
        print(f"  Text: {segment['text'][:100]}...")
        print()

def main():
    extract_segments_from_full_transcript()

if __name__ == "__main__":
    main()