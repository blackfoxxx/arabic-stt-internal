#!/usr/bin/env python3
"""
Test script for Llama 3.1 70B model with Arabic content
This script will test the new 70B model once it's downloaded
"""

import asyncio
import time
from llm_service import OllamaLLMService, LLMConfig

# Test Arabic content samples
ARABIC_TEST_SAMPLES = [
    {
        "name": "Modern Standard Arabic",
        "text": "هذا النص يحتوي على أخطاء نحوية وإملائية يجب تصحيحها لتحسين جودة المحتوى",
        "expected_improvements": ["grammar correction", "spelling fixes"]
    },
    {
        "name": "Iraqi Arabic Dialect", 
        "text": "شلونك صديقي، شنو اخبارك اليوم؟ اني بخير والحمد لله",
        "expected_improvements": ["dialect recognition", "informal to formal"]
    },
    {
        "name": "Technical Arabic",
        "text": "الذكاء الاصطناعي والتعلم الآلي يساعدان في تطوير التقنيات الحديثة",
        "expected_improvements": ["technical terminology", "clarity"]
    },
    {
        "name": "Mixed Content",
        "text": "السلام عليكم، I need to process this mixed Arabic-English text properly",
        "expected_improvements": ["language detection", "mixed content handling"]
    }
]

async def test_model_availability():
    """Test if the 70B model is available"""
    print("🔍 Testing model availability...")
    
    service = OllamaLLMService()
    
    try:
        # Check if service is available
        is_available = await service.is_available()
        if not is_available:
            print("❌ Ollama service is not available")
            return False
            
        # Get available models
        models = await service.get_available_models()
        print(f"📋 Available models: {models}")
        
        # Check for our target models
        target_models = ["llama3.1:70b-instruct-q4_K_M", "llama3.1:8b", "aya:35b-23-q4_K_M"]
        available_targets = [model for model in target_models if model in models]
        
        print(f"✅ Target models available: {available_targets}")
        return len(available_targets) > 0
        
    except Exception as e:
        print(f"❌ Error checking availability: {e}")
        return False

async def test_arabic_quality(model_name: str):
    """Test Arabic text processing quality"""
    print(f"\n🧪 Testing Arabic quality with {model_name}...")
    
    # Create service with specific model
    config = LLMConfig()
    config.model = model_name
    service = OllamaLLMService(config)
    
    results = []
    
    for sample in ARABIC_TEST_SAMPLES:
        print(f"\n📝 Testing: {sample['name']}")
        print(f"Input: {sample['text']}")
        
        # Test grammar correction
        system_prompt = """أنت خبير في اللغة العربية. مهمتك تصحيح النص العربي وتحسين جودته مع الحفاظ على المعنى الأصلي.
قم بتصحيح الأخطاء النحوية والإملائية وتحسين التركيب اللغوي."""
        
        start_time = time.time()
        
        try:
            response = await service.generate_text(
                prompt=f"صحح هذا النص العربي: {sample['text']}",
                system_prompt=system_prompt
            )
            
            processing_time = time.time() - start_time
            
            if response.success:
                print(f"✅ Output: {response.content}")
                print(f"⏱️  Processing time: {processing_time:.2f}s")
                
                results.append({
                    "sample": sample['name'],
                    "success": True,
                    "processing_time": processing_time,
                    "input_length": len(sample['text']),
                    "output_length": len(response.content)
                })
            else:
                print(f"❌ Error: {response.error}")
                results.append({
                    "sample": sample['name'],
                    "success": False,
                    "error": response.error
                })
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "sample": sample['name'],
                "success": False,
                "error": str(e)
            })
    
    return results

async def performance_comparison():
    """Compare performance between 70B and 8B models"""
    print("\n⚡ Performance Comparison: 70B vs 8B")
    
    models_to_test = []
    
    # Check which models are available
    service = OllamaLLMService()
    available_models = await service.get_available_models()
    
    if "llama3.1:70b-instruct-q4_K_M" in available_models:
        models_to_test.append("llama3.1:70b-instruct-q4_K_M")
    if "llama3.1:8b" in available_models:
        models_to_test.append("llama3.1:8b")
    
    if not models_to_test:
        print("❌ No target models available for comparison")
        return
    
    comparison_results = {}
    
    for model in models_to_test:
        print(f"\n🔄 Testing {model}...")
        results = await test_arabic_quality(model)
        
        # Calculate average processing time
        successful_results = [r for r in results if r['success']]
        if successful_results:
            avg_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
            success_rate = len(successful_results) / len(results) * 100
            
            comparison_results[model] = {
                "avg_processing_time": avg_time,
                "success_rate": success_rate,
                "total_tests": len(results)
            }
    
    # Print comparison
    print("\n📊 Performance Summary:")
    for model, stats in comparison_results.items():
        print(f"  {model}:")
        print(f"    Average time: {stats['avg_processing_time']:.2f}s")
        print(f"    Success rate: {stats['success_rate']:.1f}%")

async def main():
    """Main test function"""
    print("🚀 Starting LLM Model Testing...")
    print("=" * 50)
    
    # Test 1: Check availability
    if not await test_model_availability():
        print("\n⏳ Models are still downloading. Please wait and run this test again.")
        return
    
    # Test 2: Performance comparison
    await performance_comparison()
    
    print("\n✅ Testing completed!")
    print("\n💡 Tips:")
    print("  - 70B model provides better Arabic understanding but slower processing")
    print("  - 8B model is faster for high-volume processing")
    print("  - Use dialect_model parameter for Iraqi Arabic content")

if __name__ == "__main__":
    asyncio.run(main())