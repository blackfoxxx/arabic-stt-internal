
import json
import time
import os

transcript_id = "transcript_1769563542"
timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

multimodal_results = {
    "text_content": "هذا نص تجريبي تم إنشاؤه لاختبار النظام. يحتوي على تحليل متعدد الوسائط.",
    "full_transcription": "هذا نص تجريبي تم إنشاؤه لاختبار النظام. يحتوي على تحليل متعدد الوسائط. نأمل أن يعمل هذا بشكل صحيح.",
    "segments": [
        {
            "id": "seg_1",
            "start": 0.0,
            "end": 2.5,
            "text": "هذا نص تجريبي",
            "confidence": 0.95,
            "speaker_id": "SPEAKER_01"
        },
        {
            "id": "seg_2",
            "start": 2.5,
            "end": 5.0,
            "text": "تم إنشاؤه لاختبار النظام",
            "confidence": 0.92,
            "speaker_id": "SPEAKER_01"
        }
    ],
    "audio_file": "test_audio.mp3",
    "transcription_info": {
        "model_used": "large-v3",
        "language": "ar",
        "processing_date": timestamp,
        "total_duration": "00:00:05",
        "total_characters": 50,
        "total_words": 10,
        "total_segments": 2
    },
    "final_assessment": {
        "overall_credibility": 0.88,
        "emotional_authenticity": 0.9,
        "stress_level": 0.2,
        "deception_likelihood": 0.1,
        "cognitive_clarity": 0.95,
        "multimodal_consistency": 0.92,
        "voice_quality": 0.85,
        "narrative_coherence": 0.9,
        "confidence_score": 0.93,
        "psychological_wellness": 0.8
    },
    "recommendations": [
        "النص يبدو موثوقاً وعالي المصداقية",
        "لا توجد مؤشرات قوية على الخداع",
        "نبرة الصوت متسقة مع المحتوى"
    ],
    "processing_time": 1.5,
    "analysis_timestamp": timestamp,
    "summary": {
        "overall_sentiment": "Positive",
        "sentiment_confidence": 0.85,
        "truth_likelihood": 0.9,
        "truth_confidence": 0.88,
        "voice_quality": 0.85,
        "stress_level": 0.2,
        "deception_likelihood": 0.1,
        "emotional_authenticity": 0.9,
        "multimodal_consistency": 0.92
    }
}

enhanced_truth_results = {
    "overall_truth_likelihood": 0.89,
    "confidence_level": 0.92,
    "credibility_score": 0.90,
    "linguistic_truth_result": {
        "truth_likelihood": 0.88,
        "confidence_score": 0.91,
        "narrative_coherence": {
            "overall_score": 0.92,
            "temporal_consistency": 0.95,
            "logical_flow": 0.90,
            "detail_consistency": 0.88,
            "emotional_consistency": 0.92,
            "contradictions": [],
            "supporting_evidence": ["تسلسل زمني منطقي", "تطابق المشاعر مع الكلمات"]
        },
        "deception_markers": {
            "linguistic_complexity": 0.1,
            "detail_overload": 0.2,
            "emotional_inconsistency": 0.1,
            "temporal_vagueness": 0.1,
            "defensive_language": 0.1,
            "overall_deception_likelihood": 0.1
        },
        "truth_indicators": [
            {
                "indicator_type": "consistency",
                "text": "تسلسل زمني منطقي",
                "position": 0,
                "confidence": 0.9,
                "impact_score": 0.8
            }
        ]
    },
    "acoustic_truth_result": {
        "truth_likelihood": 0.85,
        "truth_indicators": ["نبرة صوت ثابتة", "تطابق النغمة مع المعنى"],
        "deception_indicators": []
    }
}

with open(f"multimodal_analysis_results_{transcript_id.replace('transcript_', '')}.json", "w", encoding="utf-8") as f:
    json.dump(multimodal_results, f, ensure_ascii=False, indent=2)

with open(f"enhanced_truth_detection_{transcript_id.replace('transcript_', '')}.json", "w", encoding="utf-8") as f:
    json.dump(enhanced_truth_results, f, ensure_ascii=False, indent=2)

print(f"Created files for {transcript_id}")
