#!/usr/bin/env python3
"""
Analyze Transcription Results
Uses the Arabic Text Analyzer to process existing transcription results
with grammar checking, sentence validation, and sentiment analysis
"""

import json
import sys
from pathlib import Path
from arabic_text_analyzer import ArabicTextAnalyzer

def load_transcription_results(file_path: str):
    """Load transcription results from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading transcription file: {e}")
        return None

def extract_text_from_transcription(transcription_data):
    """Extract text content from transcription data"""
    texts = []
    
    if isinstance(transcription_data, dict):
        # Check for nested transcript structure (new format)
        if 'transcript' in transcription_data and isinstance(transcription_data['transcript'], dict):
            transcript = transcription_data['transcript']
            if 'segments' in transcript:
                segments = transcript['segments']
                for segment in segments:
                    if isinstance(segment, dict) and 'text' in segment:
                        text = segment['text'].strip()
                        if text:
                            texts.append(text)
        
        # Check for segments in the transcription (old format)
        elif 'segments' in transcription_data:
            segments = transcription_data['segments']
            for segment in segments:
                if isinstance(segment, dict) and 'text' in segment:
                    text = segment['text'].strip()
                    if text:
                        texts.append(text)
        
        # Check for transcript field (old format)
        elif 'transcript' in transcription_data:
            transcript = transcription_data['transcript']
            if isinstance(transcript, list):
                for item in transcript:
                    if isinstance(item, dict) and 'text' in item:
                        text = item['text'].strip()
                        if text:
                            texts.append(text)
            elif isinstance(transcript, str):
                texts.append(transcript.strip())
    
    elif isinstance(transcription_data, list):
        # Direct list of segments
        for segment in transcription_data:
            if isinstance(segment, dict) and 'text' in segment:
                text = segment['text'].strip()
                if text:
                    texts.append(text)
    
    return texts

def analyze_transcription_file(file_path: str, analyzer: ArabicTextAnalyzer):
    """Analyze a transcription file"""
    print(f"\n🔍 Analyzing transcription file: {file_path}")
    
    # Load transcription data
    transcription_data = load_transcription_results(file_path)
    if not transcription_data:
        return None
    
    # Extract text segments
    texts = extract_text_from_transcription(transcription_data)
    if not texts:
        print("❌ No text content found in transcription file")
        return None
    
    print(f"📝 Found {len(texts)} text segments")
    
    # Combine all text segments
    combined_text = ' '.join(texts)
    print(f"📊 Total text length: {len(combined_text)} characters")
    
    # Generate analysis filename based on original file
    original_name = Path(file_path).stem
    analysis_name = f"analysis_{original_name}"
    
    # Analyze the combined text
    results = analyzer.analyze_text(combined_text, analysis_name)
    
    return results

def main():
    """Main function to analyze transcription results"""
    print("🎯 Arabic Transcription Analysis Tool")
    print("=" * 50)
    
    # Initialize the analyzer
    print("🚀 Initializing Arabic Text Analyzer...")
    analyzer = ArabicTextAnalyzer(output_dir="transcription_analysis")
    
    # Find transcription files in the current directory
    current_dir = Path(".")
    transcription_files = []
    
    # Look for common transcription file patterns
    patterns = [
        "*transcript*.json",
        "*transcription*.json",
        "*results*.json",
        "test_results_*.json"
    ]
    
    for pattern in patterns:
        transcription_files.extend(current_dir.glob(pattern))
    
    if not transcription_files:
        print("❌ No transcription files found in current directory")
        print("Looking for files matching patterns:")
        for pattern in patterns:
            print(f"  - {pattern}")
        return
    
    print(f"📁 Found {len(transcription_files)} transcription files:")
    for i, file_path in enumerate(transcription_files, 1):
        print(f"  {i}. {file_path.name}")
    
    # Analyze each transcription file
    analysis_results = []
    for file_path in transcription_files:
        try:
            result = analyze_transcription_file(str(file_path), analyzer)
            if result:
                analysis_results.append({
                    'file': str(file_path),
                    'analysis': result
                })
                
                print(f"✅ Analysis complete for {file_path.name}")
                print(f"   📊 Sentences: {result['total_sentences']}")
                print(f"   🎭 Overall sentiment: {result['summary']['overall_sentiment']}")
                print(f"   ⚠️  Issues: {result['summary']['validation_issues']}")
                
        except Exception as e:
            print(f"❌ Error analyzing {file_path.name}: {e}")
    
    # Summary
    print(f"\n📋 Analysis Summary")
    print("=" * 30)
    print(f"Files analyzed: {len(analysis_results)}")
    
    if analysis_results:
        total_sentences = sum(r['analysis']['total_sentences'] for r in analysis_results)
        total_issues = sum(r['analysis']['summary']['validation_issues'] for r in analysis_results)
        
        print(f"Total sentences: {total_sentences}")
        print(f"Total validation issues: {total_issues}")
        
        # Sentiment distribution across all files
        all_sentiments = {}
        for result in analysis_results:
            sentiment_dist = result['analysis']['summary']['sentiment_distribution']
            for sentiment, count in sentiment_dist.items():
                all_sentiments[sentiment] = all_sentiments.get(sentiment, 0) + count
        
        if all_sentiments:
            print(f"Overall sentiment distribution: {all_sentiments}")
        
        print(f"\n📁 Analysis files saved in: transcription_analysis/")
        print("Each sentence has been analyzed separately with detailed results.")

if __name__ == "__main__":
    main()