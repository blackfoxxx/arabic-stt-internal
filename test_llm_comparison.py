#!/usr/bin/env python3
"""
LLM Model Comparison Test for Arabic STT
Tests transcription quality with different LLM models on a specific audio file
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import local modules
from gpu_arabic_server import GPUArabicProcessor
import ollama

class LLMComparisonTester:
    def __init__(self, audio_file_path: str):
        self.audio_file_path = audio_file_path
        self.results = {
            "audio_file": audio_file_path,
            "test_timestamp": datetime.now().isoformat(),
            "transcriptions": {},
            "analysis": {},
            "comparison": {}
        }
        
        # Initialize services
        self.stt_processor = GPUArabicProcessor()
        
        # Available models for testing
        self.models_to_test = [
            "llama3.1:8b",           # Current default
            "llama3.1:70b-instruct-q4_K_M",  # New 70B model
            "aya:35b-23-q4_K_M"      # New Aya model
        ]
    
    def test_baseline_transcription(self) -> dict:
        """Test transcription with current system (no LLM enhancement)"""
        print("🎯 Testing baseline transcription (no LLM enhancement)...")
        
        try:
            # Process audio file with current system
            options = {
                'model': 'large-v3',
                'language': 'ar'
            }
            
            start_time = time.time()
            result = self.stt_processor.process_audio_file(self.audio_file_path, options)
            processing_time = time.time() - start_time
            
            if result.get("status") == "completed":
                segments = result.get("segments", [])
                full_transcription = " ".join([seg.get("text", "") for seg in segments])
                avg_confidence = sum(seg.get("confidence", 0) for seg in segments) / len(segments) if segments else 0
                
                baseline_result = {
                    "transcription": full_transcription,
                    "segments": segments,
                    "confidence": avg_confidence,
                    "word_count": len(full_transcription.split()) if full_transcription else 0,
                    "character_count": len(full_transcription) if full_transcription else 0,
                    "processing_time": processing_time,
                    "model_used": result.get("model_used", "unknown"),
                    "device": result.get("device", "unknown"),
                    "success": True
                }
                
                print(f"✅ Baseline transcription completed")
                print(f"   Word count: {baseline_result['word_count']}")
                print(f"   Confidence: {avg_confidence:.2f}")
                print(f"   Processing time: {processing_time:.2f}s")
                
                return baseline_result
            else:
                print(f"❌ Baseline transcription failed: {result}")
                return {"success": False, "error": "Transcription failed"}
                
        except Exception as e:
            print(f"❌ Error in baseline transcription: {e}")
            return {"success": False, "error": str(e)}
    
    def test_llm_enhanced_transcription(self, model_name: str) -> dict:
        """Test transcription with LLM enhancement using specified model"""
        print(f"🤖 Testing LLM-enhanced transcription with {model_name}...")
        
        try:
            # First get baseline transcription
            baseline = self.test_baseline_transcription()
            if not baseline.get("success"):
                return {"success": False, "error": "Failed to get baseline transcription"}
            
            original_text = baseline["transcription"]
            
            # Test if model is available
            try:
                available_models = ollama.list()
                model_names = [model['name'] for model in available_models.get('models', [])]
                if model_name not in model_names:
                    return {"success": False, "error": f"Model {model_name} not available"}
            except Exception as e:
                return {"success": False, "error": f"Failed to check model availability: {e}"}
            
            # Enhance transcription with LLM
            start_time = time.time()
            
            # Create enhancement prompt
            enhancement_prompt = f"""
أنت خبير في تحسين النصوص العربية المنسوخة من الصوت. يرجى تحسين النص التالي:

النص الأصلي: {original_text}

يرجى:
1. تصحيح الأخطاء الإملائية والنحوية
2. تحسين علامات الترقيم
3. ضمان التدفق الطبيعي للنص
4. الحفاظ على المعنى الأصلي

النص المحسن:
"""
            
            # Get LLM enhancement
            try:
                response = ollama.chat(
                    model=model_name,
                    messages=[{
                        'role': 'user',
                        'content': enhancement_prompt
                    }],
                    options={
                        'temperature': 0.3,
                        'top_p': 0.9,
                        'max_tokens': 2048
                    }
                )
                
                enhanced_text = response['message']['content'].strip()
                processing_time = time.time() - start_time
                
                # Calculate improvement metrics
                original_words = len(original_text.split()) if original_text else 0
                enhanced_words = len(enhanced_text.split()) if enhanced_text else 0
                
                result = {
                    "model_name": model_name,
                    "original_transcription": original_text,
                    "enhanced_transcription": enhanced_text,
                    "original_word_count": original_words,
                    "enhanced_word_count": enhanced_words,
                    "original_character_count": len(original_text) if original_text else 0,
                    "enhanced_character_count": len(enhanced_text) if enhanced_text else 0,
                    "llm_processing_time": processing_time,
                    "baseline_confidence": baseline.get("confidence", 0),
                    "success": True
                }
                
                print(f"✅ LLM enhancement completed with {model_name}")
                print(f"   Original words: {original_words}")
                print(f"   Enhanced words: {enhanced_words}")
                print(f"   Processing time: {processing_time:.2f}s")
                
                return result
                
            except Exception as e:
                print(f"❌ LLM enhancement failed with {model_name}: {e}")
                return {"success": False, "error": f"LLM enhancement failed: {e}"}
                
        except Exception as e:
            print(f"❌ Error in LLM enhanced transcription: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_transcription_quality(self, transcription: str, model_name: str) -> dict:
        """Analyze transcription quality metrics"""
        if not transcription:
            return {"error": "Empty transcription"}
        
        # Basic quality metrics
        words = transcription.split()
        sentences = transcription.split('.')
        
        # Arabic text analysis
        arabic_chars = sum(1 for char in transcription if '\u0600' <= char <= '\u06FF')
        total_chars = len(transcription.replace(' ', ''))
        arabic_ratio = arabic_chars / total_chars if total_chars > 0 else 0
        
        # Punctuation analysis
        punctuation_count = sum(1 for char in transcription if char in '.,!?;:')
        punctuation_ratio = punctuation_count / len(words) if words else 0
        
        analysis = {
            "model_name": model_name,
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "character_count": len(transcription),
            "arabic_character_ratio": arabic_ratio,
            "punctuation_ratio": punctuation_ratio,
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0
        }
        
        return analysis
    
    def compare_results(self) -> dict:
        """Compare results across all models"""
        print("📊 Comparing results across all models...")
        
        comparison = {
            "best_model": None,
            "metrics_comparison": {},
            "quality_ranking": [],
            "recommendations": []
        }
        
        # Extract transcriptions for comparison
        transcriptions = {}
        for model, result in self.results["transcriptions"].items():
            if result.get("success"):
                if model == "baseline":
                    transcriptions[model] = result["transcription"]
                else:
                    transcriptions[model] = result["enhanced_transcription"]
        
        # Compare word counts
        word_counts = {}
        for model, text in transcriptions.items():
            word_counts[model] = len(text.split()) if text else 0
        
        comparison["word_counts"] = word_counts
        
        # Compare processing times
        processing_times = {}
        for model, result in self.results["transcriptions"].items():
            if result.get("success"):
                if model == "baseline":
                    processing_times[model] = result.get("processing_time", 0)
                else:
                    processing_times[model] = result.get("llm_processing_time", 0)
        
        comparison["processing_times"] = processing_times
        
        # Quality analysis comparison
        quality_scores = {}
        for model, analysis in self.results["analysis"].items():
            if not analysis.get("error"):
                # Simple quality score based on multiple factors
                score = (
                    analysis["arabic_character_ratio"] * 0.3 +
                    min(analysis["punctuation_ratio"], 0.1) * 10 * 0.2 +
                    min(analysis["avg_word_length"] / 6, 1) * 0.2 +
                    min(analysis["word_count"] / 100, 1) * 0.3
                )
                quality_scores[model] = score
        
        comparison["quality_scores"] = quality_scores
        
        # Determine best model
        if quality_scores:
            best_model = max(quality_scores.keys(), key=lambda k: quality_scores[k])
            comparison["best_model"] = best_model
            comparison["quality_ranking"] = sorted(quality_scores.keys(), 
                                                 key=lambda k: quality_scores[k], 
                                                 reverse=True)
        
        # Generate recommendations
        recommendations = []
        if "aya:35b-23-q4_K_M" in quality_scores:
            recommendations.append("Aya 35B model shows good Arabic language understanding")
        if "llama3.1:70b-instruct-q4_K_M" in quality_scores:
            recommendations.append("Llama 3.1 70B provides comprehensive language processing")
        
        comparison["recommendations"] = recommendations
        
        return comparison
    
    def run_comprehensive_test(self):
        """Run comprehensive LLM comparison test"""
        print("=" * 80)
        print("🧪 ARABIC STT LLM MODEL COMPARISON TEST")
        print("=" * 80)
        print(f"📁 Audio file: {self.audio_file_path}")
        print(f"🕒 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test baseline transcription
        print("--- BASELINE TRANSCRIPTION ---")
        baseline_result = self.test_baseline_transcription()
        self.results["transcriptions"]["baseline"] = baseline_result
        
        if baseline_result.get("success"):
            self.results["analysis"]["baseline"] = self.analyze_transcription_quality(
                baseline_result["transcription"], "baseline"
            )
        
        print()
        
        # Test each LLM model
        for model_name in self.models_to_test:
            print(f"--- {model_name.upper()} MODEL TEST ---")
            
            llm_result = self.test_llm_enhanced_transcription(model_name)
            self.results["transcriptions"][model_name] = llm_result
            
            if llm_result.get("success"):
                self.results["analysis"][model_name] = self.analyze_transcription_quality(
                    llm_result["enhanced_transcription"], model_name
                )
            
            print()
            time.sleep(2)  # Brief pause between tests
        
        # Compare results
        print("--- COMPARISON ANALYSIS ---")
        self.results["comparison"] = self.compare_results()
        
        # Save results
        timestamp = int(time.time())
        results_file = f"llm_comparison_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to: {results_file}")
        
        # Print summary
        self.print_summary()
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        
        # Transcription success rates
        successful_tests = sum(1 for result in self.results["transcriptions"].values() 
                             if result.get("success"))
        total_tests = len(self.results["transcriptions"])
        
        print(f"✅ Successful transcriptions: {successful_tests}/{total_tests}")
        
        # Best performing model
        best_model = self.results["comparison"].get("best_model")
        if best_model:
            print(f"🏆 Best performing model: {best_model}")
        
        # Quality ranking
        ranking = self.results["comparison"].get("quality_ranking", [])
        if ranking:
            print("📊 Quality ranking:")
            for i, model in enumerate(ranking, 1):
                score = self.results["comparison"]["quality_scores"].get(model, 0)
                print(f"   {i}. {model}: {score:.3f}")
        
        # Processing times
        times = self.results["comparison"].get("processing_times", {})
        if times:
            print("⏱️  Processing times:")
            for model, time_taken in times.items():
                print(f"   {model}: {time_taken:.2f}s")
        
        print("=" * 80)

def main():
    """Main function"""
    audio_file = "250825-1107_OugfC4aY.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    # Run comprehensive test
    tester = LLMComparisonTester(audio_file)
    results = tester.run_comprehensive_test()
    
    return results

if __name__ == "__main__":
    main()