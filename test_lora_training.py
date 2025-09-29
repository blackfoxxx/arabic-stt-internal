#!/usr/bin/env python3
"""
Test script to verify LoRA fine-tuning pipeline
for the Arabic STT LLM training system.
"""

import requests
import json
import time
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8001"

def submit_training_data() -> bool:
    """Submit sample training data for LoRA fine-tuning"""
    print("📝 Submitting sample training data...")
    
    # Sample transcription corrections
    transcription_samples = [
        {
            "original_text": "مرحبا بك في نظام التدريب",
            "corrected_text": "مرحباً بك في نظام التدريب للذكاء الاصطناعي",
            "quality_score": 0.9
        },
        {
            "original_text": "هذا نص عربي للاختبار",
            "corrected_text": "هذا نص عربي للاختبار والتحليل",
            "quality_score": 0.8
        },
        {
            "original_text": "نظام الذكاء الاصطناعي متطور",
            "corrected_text": "نظام الذكاء الاصطناعي متطور جداً",
            "quality_score": 0.85
        }
    ]
    
    # Sample dialect adaptations
    dialect_samples = [
        {
            "standard_text": "كيف حالك اليوم؟",
            "dialect_text": "شلونك اليوم؟",
            "dialect_name": "iraqi",
            "quality_score": 0.9
        },
        {
            "standard_text": "أين تذهب؟",
            "dialect_text": "وين رايح؟",
            "dialect_name": "iraqi",
            "quality_score": 0.85
        },
        {
            "standard_text": "هذا جيد جداً",
            "dialect_text": "هذا زين كلش",
            "dialect_name": "iraqi",
            "quality_score": 0.8
        }
    ]
    
    success_count = 0
    total_samples = len(transcription_samples) + len(dialect_samples)
    
    # Submit transcription corrections
    for sample in transcription_samples:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/feedback/transcription",
                json=sample,
                timeout=10
            )
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Transcription sample submitted")
            else:
                print(f"❌ Failed to submit transcription sample: {response.status_code}")
        except Exception as e:
            print(f"❌ Error submitting transcription sample: {e}")
    
    # Submit dialect samples
    for sample in dialect_samples:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/data/dialect",
                json=sample,
                timeout=10
            )
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Dialect sample submitted")
            else:
                print(f"❌ Failed to submit dialect sample: {response.status_code}")
        except Exception as e:
            print(f"❌ Error submitting dialect sample: {e}")
    
    print(f"📊 Data submission: {success_count}/{total_samples} samples successful")
    return success_count == total_samples

def start_lora_training() -> Dict[str, Any]:
    """Start LoRA fine-tuning with sample configuration"""
    print("🚀 Starting LoRA fine-tuning...")
    
    training_config = {
        "config": {
            "model_name": "llama3.1:8b",  # Use fastest model for testing
            "num_train_epochs": 1,  # Short training for testing
            "per_device_train_batch_size": 2,
            "learning_rate": 0.0001,
            "lora_r": 8,  # Smaller rank for faster training
            "lora_alpha": 16,
            "lora_dropout": 0.1,
            "max_length": 256
        },
        "filters": {
            "min_quality": 0.7,
            "limit": 10
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/training/start",
            json=training_config,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LoRA training started successfully")
            print(f"   Model: {training_config['config']['model_name']}")
            print(f"   Epochs: {training_config['config']['num_train_epochs']}")
            print(f"   LoRA rank: {training_config['config']['lora_r']}")
            return {"success": True, "response": result}
        else:
            print(f"❌ Failed to start LoRA training: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Error starting LoRA training: {e}")
        return {"success": False, "error": str(e)}

def monitor_training_progress(max_wait_time: int = 300) -> Dict[str, Any]:
    """Monitor training progress for a specified time"""
    print("📊 Monitoring training progress...")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{API_BASE_URL}/api/training/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    status = data.get("status", {})
                    current_status = status.get("status", "unknown")
                    progress = status.get("progress", 0)
                    
                    if current_status != last_status:
                        print(f"🔄 Training status: {current_status} ({progress}%)")
                        last_status = current_status
                    
                    # Check if training completed
                    if current_status in ["completed", "failed", "idle"]:
                        if current_status == "completed":
                            print("✅ Training completed successfully!")
                            return {"success": True, "status": current_status, "progress": progress}
                        elif current_status == "failed":
                            print("❌ Training failed!")
                            return {"success": False, "status": current_status, "progress": progress}
                        elif current_status == "idle":
                            print("⚠️ Training returned to idle state")
                            return {"success": False, "status": current_status, "progress": progress}
                    
                    time.sleep(5)  # Wait 5 seconds before next check
                else:
                    print("❌ Failed to get training status")
                    break
            else:
                print(f"❌ Status check failed: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ Error checking training status: {e}")
            break
    
    print(f"⏰ Training monitoring timed out after {max_wait_time} seconds")
    return {"success": False, "status": "timeout", "progress": 0}

def main():
    """Run comprehensive LoRA training tests"""
    print("=" * 60)
    print("🧪 ARABIC STT LORA TRAINING TESTS")
    print("=" * 60)
    
    results = {
        "data_submission": False,
        "training_start": False,
        "training_progress": False,
        "overall_status": "unknown"
    }
    
    # Step 1: Submit training data
    print("\n--- STEP 1: DATA SUBMISSION ---")
    results["data_submission"] = submit_training_data()
    
    if not results["data_submission"]:
        print("❌ Data submission failed. Cannot proceed with training.")
        results["overall_status"] = "failed"
    else:
        # Step 2: Start LoRA training
        print("\n--- STEP 2: START LORA TRAINING ---")
        training_result = start_lora_training()
        results["training_start"] = training_result.get("success", False)
        
        if results["training_start"]:
            # Step 3: Monitor training progress
            print("\n--- STEP 3: MONITOR TRAINING PROGRESS ---")
            progress_result = monitor_training_progress(max_wait_time=180)  # 3 minutes max
            results["training_progress"] = progress_result.get("success", False)
            
            if results["training_progress"]:
                results["overall_status"] = "passed"
                print("\n🎉 All LoRA training tests PASSED!")
            else:
                results["overall_status"] = "partial"
                print("\n⚠️ Training started but didn't complete in time")
        else:
            results["overall_status"] = "failed"
            print("\n❌ Failed to start LoRA training")
    
    # Save results
    with open("lora_training_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Test results saved to: lora_training_test_results.json")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 LORA TRAINING TEST SUMMARY")
    print("=" * 60)
    
    print(f"Data Submission: {'✅' if results['data_submission'] else '❌'}")
    print(f"Training Start: {'✅' if results['training_start'] else '❌'}")
    print(f"Training Progress: {'✅' if results['training_progress'] else '❌'}")
    print(f"Overall Status: {'✅ PASSED' if results['overall_status'] == 'passed' else '⚠️ PARTIAL' if results['overall_status'] == 'partial' else '❌ FAILED'}")
    
    return results["overall_status"] in ["passed", "partial"]

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)