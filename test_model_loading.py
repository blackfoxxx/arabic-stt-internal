#!/usr/bin/env python3
"""
Test script to verify model loading and inference capabilities
for the Arabic STT LLM training system.
"""

import requests
import json
import time
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8001"
OLLAMA_BASE_URL = "http://localhost:11434"

def test_ollama_model_inference(model_name: str, prompt: str) -> Dict[str, Any]:
    """Test direct Ollama model inference"""
    print(f"🧠 Testing {model_name} inference...")
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {model_name} inference successful")
            print(f"   Response: {result.get('response', '')[:100]}...")
            return {"success": True, "response": result.get('response', '')}
        else:
            print(f"❌ {model_name} inference failed: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ {model_name} inference error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_training_api_model_loading() -> Dict[str, Any]:
    """Test model loading through training API"""
    print("🔄 Testing training API model loading...")
    
    try:
        # Test getting available models
        response = requests.get(f"{API_BASE_URL}/api/models/available")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                models = data.get("models", [])
                print(f"✅ Training API models endpoint working")
                print(f"   Available models: {len(models)}")
                for model in models:
                    print(f"   - {model['name']}: {model['description']}")
                return {"success": True, "models": models}
            else:
                print("❌ Training API models endpoint returned unsuccessful response")
                return {"success": False, "error": "API returned unsuccessful response"}
        else:
            print(f"❌ Training API models endpoint failed: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Training API model loading error: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Run comprehensive model loading tests"""
    print("=" * 60)
    print("🚀 ARABIC STT LLM MODEL LOADING TESTS")
    print("=" * 60)
    
    results = {
        "ollama_tests": {},
        "training_api_tests": {},
        "overall_status": "unknown"
    }
    
    # Test models with Arabic prompts
    test_models = [
        {
            "name": "llama3.1:8b",
            "prompt": "Translate this Arabic text to English: مرحبا بك في نظام التدريب"
        },
        {
            "name": "llama3.1:70b-instruct-q4_K_M", 
            "prompt": "Correct this Arabic transcription: مرحبا بكم في نظام التدريب للذكاء الاصطناعي"
        },
        {
            "name": "aya:35b-23-q4_K_M",
            "prompt": "تحسين هذا النص العربي: مرحبا بك في نظام التدريب"
        }
    ]
    
    print("\n--- OLLAMA DIRECT INFERENCE TESTS ---")
    for model_config in test_models:
        model_name = model_config["name"]
        prompt = model_config["prompt"]
        
        result = test_ollama_model_inference(model_name, prompt)
        results["ollama_tests"][model_name] = result
        
        # Add delay between tests to avoid overwhelming the system
        time.sleep(2)
    
    print("\n--- TRAINING API MODEL LOADING TESTS ---")
    api_result = test_training_api_model_loading()
    results["training_api_tests"] = api_result
    
    # Calculate overall status
    ollama_success = all(test.get("success", False) for test in results["ollama_tests"].values())
    api_success = results["training_api_tests"].get("success", False)
    
    if ollama_success and api_success:
        results["overall_status"] = "passed"
        print("\n🎉 All model loading tests PASSED!")
    else:
        results["overall_status"] = "failed"
        print("\n❌ Some model loading tests FAILED!")
    
    # Save results
    with open("model_loading_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Test results saved to: model_loading_test_results.json")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 MODEL LOADING TEST SUMMARY")
    print("=" * 60)
    
    ollama_passed = sum(1 for test in results["ollama_tests"].values() if test.get("success", False))
    ollama_total = len(results["ollama_tests"])
    
    print(f"Ollama Tests: {ollama_passed}/{ollama_total}")
    print(f"Training API Tests: {'✅' if api_success else '❌'}")
    print(f"Overall Status: {'✅ PASSED' if results['overall_status'] == 'passed' else '❌ FAILED'}")
    
    return results["overall_status"] == "passed"

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)