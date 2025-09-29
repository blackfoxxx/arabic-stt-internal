#!/usr/bin/env python3
"""
LLM Enhancement Test for Arabic STT
Tests how different LLM models enhance Arabic transcription quality
"""

import os
import sys
import json
import time
import ollama
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import local modules
from gpu_arabic_server import GPUArabicProcessor

class LLMEnhancementTester:
    def __init__(self, audio_file_path: str):
        self.audio_file_path = audio_file_path
        self.stt_processor = GPUArabicProcessor()
        
        # Available models for testing
        self.models_to_test = [
            "llama3.1:8b",
            "llama3.1:70b-instruct-q4_K_M", 
            "aya:35b-23-q4_K_M"
        ]
        
        self.results = {
            "audio_file": audio_file_path,
            "test_timestamp": datetime.now().isoformat(),
            "baseline_transcription": {},
            "enhanced_transcriptions": {},
            "comparison": {}
        }
    
    def get_baseline_transcription(self):
        """Get baseline transcription without LLM enhancement"""
        print("🎯 Getting baseline transcription...")
        
        try:
            options = {'model': 'large-v3', 'language': 'ar'}
            start_time = time.time()
            result = self.stt_processor.process_audio_file(self.audio_file_path, options)
            processing_time = time.time() - start_time
            
            if result.get("status") == "completed":
                segments = result.get("segments", [])
                full_text = " ".join([seg.get("text", "") for seg in segments])
                avg_confidence = sum(seg.get("confidence", 0) for seg in segments) / len(segments) if segments else 0
                
                baseline = {
                    "text": full_text,
                    "segments_count": len(segments),
                    "confidence": avg_confidence,
                    "word_count": len(full_text.split()),
                    "character_count": len(full_text),
                    "processing_time": processing_time,
                    "success": True
                }
                
                print(f"✅ Baseline completed: {baseline['word_count']} words, {avg_confidence:.2f} confidence")
                return baseline
            else:
                print(f"❌ Baseline failed: {result}")
                return {"success": False, "error": "Transcription failed"}
                
        except Exception as e:
            print(f"❌ Baseline error: {e}")
            return {"success": False, "error": str(e)}
    
    def enhance_with_llm(self, original_text: str, model_name: str):
        """Enhance transcription using specified LLM model"""
        print(f"🤖 Enhancing with {model_name}...")
        
        try:
            # Create Arabic-specific enhancement prompt
            prompt = f"""أنت خبير في تحسين النصوص العربية المنسوخة من الصوت. يرجى تحسين النص التالي:

النص الأصلي:
{original_text}

المطلوب:
1. تصحيح الأخطاء الإملائية والنحوية
2. تحسين علامات الترقيم والفواصل
3. ضمان التدفق الطبيعي للنص
4. الحفاظ على المعنى الأصلي تماماً
5. تحسين وضوح الجمل والعبارات

النص المحسن:"""

            start_time = time.time()
            
            response = ollama.chat(
                model=model_name,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.2,  # Low temperature for consistency
                    'top_p': 0.9,
                    'max_tokens': 4096
                }
            )
            
            processing_time = time.time() - start_time
            enhanced_text = response['message']['content'].strip()
            
            # Remove any introductory text that might be added by the model
            if "النص المحسن:" in enhanced_text:
                enhanced_text = enhanced_text.split("النص المحسن:")[-1].strip()
            
            result = {
                "model_name": model_name,
                "enhanced_text": enhanced_text,
                "original_word_count": len(original_text.split()),
                "enhanced_word_count": len(enhanced_text.split()),
                "original_char_count": len(original_text),
                "enhanced_char_count": len(enhanced_text),
                "processing_time": processing_time,
                "success": True
            }
            
            print(f"✅ Enhanced with {model_name}: {result['enhanced_word_count']} words ({processing_time:.2f}s)")
            return result
            
        except Exception as e:
            print(f"❌ Enhancement failed with {model_name}: {e}")
            return {"success": False, "error": str(e), "model_name": model_name}
    
    def analyze_enhancement_quality(self, original: str, enhanced: str, model_name: str):
        """Analyze the quality of enhancement"""
        if not original or not enhanced:
            return {"error": "Empty text"}
        
        # Basic metrics
        orig_words = original.split()
        enh_words = enhanced.split()
        
        # Arabic character analysis
        orig_arabic = sum(1 for c in original if '\u0600' <= c <= '\u06FF')
        enh_arabic = sum(1 for c in enhanced if '\u0600' <= c <= '\u06FF')
        
        # Punctuation analysis
        orig_punct = sum(1 for c in original if c in '.,!?;:،؛؟')
        enh_punct = sum(1 for c in enhanced if c in '.,!?;:،؛؟')
        
        # Length changes
        word_change = len(enh_words) - len(orig_words)
        char_change = len(enhanced) - len(original)
        
        analysis = {
            "model_name": model_name,
            "word_count_change": word_change,
            "character_count_change": char_change,
            "arabic_chars_original": orig_arabic,
            "arabic_chars_enhanced": enh_arabic,
            "punctuation_original": orig_punct,
            "punctuation_enhanced": enh_punct,
            "punctuation_improvement": enh_punct - orig_punct,
            "avg_word_length_original": sum(len(w) for w in orig_words) / len(orig_words) if orig_words else 0,
            "avg_word_length_enhanced": sum(len(w) for w in enh_words) / len(enh_words) if enh_words else 0
        }
        
        return analysis
    
    def run_enhancement_test(self):
        """Run comprehensive LLM enhancement test"""
        print("=" * 80)
        print("🧪 ARABIC STT LLM ENHANCEMENT TEST")
        print("=" * 80)
        print(f"📁 Audio file: {self.audio_file_path}")
        print(f"🕒 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Get baseline transcription
        baseline = self.get_baseline_transcription()
        self.results["baseline_transcription"] = baseline
        
        if not baseline.get("success"):
            print("❌ Cannot proceed without baseline transcription")
            return self.results
        
        original_text = baseline["text"]
        print(f"\n📝 Original transcription ({len(original_text)} chars):")
        print(f"   {original_text[:200]}..." if len(original_text) > 200 else f"   {original_text}")
        print()
        
        # Test each LLM model
        for model_name in self.models_to_test:
            print(f"--- {model_name.upper()} ENHANCEMENT ---")
            
            # Enhance with LLM
            enhancement_result = self.enhance_with_llm(original_text, model_name)
            self.results["enhanced_transcriptions"][model_name] = enhancement_result
            
            if enhancement_result.get("success"):
                enhanced_text = enhancement_result["enhanced_text"]
                print(f"📝 Enhanced text ({len(enhanced_text)} chars):")
                print(f"   {enhanced_text[:200]}..." if len(enhanced_text) > 200 else f"   {enhanced_text}")
                
                # Analyze enhancement quality
                analysis = self.analyze_enhancement_quality(original_text, enhanced_text, model_name)
                self.results["enhanced_transcriptions"][model_name]["analysis"] = analysis
                
                print(f"📊 Analysis:")
                print(f"   Word change: {analysis['word_count_change']:+d}")
                print(f"   Punctuation improvement: {analysis['punctuation_improvement']:+d}")
                print(f"   Processing time: {enhancement_result['processing_time']:.2f}s")
            
            print()
            time.sleep(1)  # Brief pause between tests
        
        # Generate comparison
        self.generate_comparison()
        
        # Save results
        timestamp = int(time.time())
        results_file = f"llm_enhancement_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to: {results_file}")
        
        # Print summary
        self.print_summary()
        
        return self.results
    
    def generate_comparison(self):
        """Generate comparison between different enhancements"""
        print("--- ENHANCEMENT COMPARISON ---")
        
        comparison = {
            "successful_enhancements": 0,
            "best_model": None,
            "processing_times": {},
            "quality_scores": {},
            "recommendations": []
        }
        
        baseline_words = self.results["baseline_transcription"].get("word_count", 0)
        
        for model_name, result in self.results["enhanced_transcriptions"].items():
            if result.get("success"):
                comparison["successful_enhancements"] += 1
                comparison["processing_times"][model_name] = result["processing_time"]
                
                # Calculate quality score based on improvements
                analysis = result.get("analysis", {})
                punct_improvement = analysis.get("punctuation_improvement", 0)
                word_change = abs(analysis.get("word_count_change", 0))
                
                # Quality score: punctuation improvement is good, excessive word changes are bad
                quality_score = punct_improvement * 0.5 - (word_change / baseline_words) * 0.3
                comparison["quality_scores"][model_name] = quality_score
        
        # Find best model
        if comparison["quality_scores"]:
            best_model = max(comparison["quality_scores"].keys(), 
                           key=lambda k: comparison["quality_scores"][k])
            comparison["best_model"] = best_model
        
        # Generate recommendations
        if "aya:35b-23-q4_K_M" in comparison["quality_scores"]:
            comparison["recommendations"].append("Aya 35B shows strong Arabic language understanding")
        if "llama3.1:70b-instruct-q4_K_M" in comparison["quality_scores"]:
            comparison["recommendations"].append("Llama 3.1 70B provides comprehensive text processing")
        
        self.results["comparison"] = comparison
        
        print(f"✅ Successful enhancements: {comparison['successful_enhancements']}/{len(self.models_to_test)}")
        if comparison["best_model"]:
            print(f"🏆 Best performing model: {comparison['best_model']}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📋 ENHANCEMENT TEST SUMMARY")
        print("=" * 80)
        
        baseline = self.results["baseline_transcription"]
        if baseline.get("success"):
            print(f"📝 Original transcription: {baseline['word_count']} words, {baseline['confidence']:.2f} confidence")
        
        comparison = self.results["comparison"]
        print(f"✅ Successful enhancements: {comparison['successful_enhancements']}/{len(self.models_to_test)}")
        
        if comparison.get("best_model"):
            print(f"🏆 Best model: {comparison['best_model']}")
        
        # Show processing times
        times = comparison.get("processing_times", {})
        if times:
            print("⏱️  Processing times:")
            for model, time_taken in times.items():
                print(f"   {model}: {time_taken:.2f}s")
        
        # Show quality scores
        scores = comparison.get("quality_scores", {})
        if scores:
            print("📊 Quality scores:")
            sorted_models = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
            for i, model in enumerate(sorted_models, 1):
                print(f"   {i}. {model}: {scores[model]:.3f}")
        
        print("=" * 80)

def main():
    """Main function"""
    audio_file = "250825-1107_OugfC4aY.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    # Run enhancement test
    tester = LLMEnhancementTester(audio_file)
    results = tester.run_enhancement_test()
    
    return results

if __name__ == "__main__":
    main()