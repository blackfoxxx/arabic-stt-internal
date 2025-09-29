#!/usr/bin/env python3
"""
Test Script for LLM Training System
Tests the training service, API endpoints, and data collection functionality
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any

# Test configuration
API_BASE = "http://localhost:8001/api"
TEST_DATA = {
    "transcription_samples": [
        {
            "original": "هذا نص عربي مع بعض الاخطاء",
            "corrected": "هذا نص عربي مع بعض الأخطاء",
            "quality": 0.9
        },
        {
            "original": "الكلام مش واضح كتير",
            "corrected": "الكلام غير واضح كثيراً",
            "quality": 0.8
        },
        {
            "original": "انا رايح البيت",
            "corrected": "أنا ذاهب إلى البيت",
            "quality": 0.85
        }
    ],
    "dialect_samples": [
        {
            "standard": "أنا ذاهب إلى المنزل",
            "dialect": "أني رايح البيت",
            "dialect_name": "iraqi",
            "quality": 0.9
        },
        {
            "standard": "كيف حالك اليوم؟",
            "dialect": "شلونك اليوم؟",
            "dialect_name": "iraqi",
            "quality": 0.95
        },
        {
            "standard": "هل تريد أن تأكل؟",
            "dialect": "تريد تاكل؟",
            "dialect_name": "iraqi",
            "quality": 0.8
        }
    ]
}

class TrainingSystemTester:
    """Test suite for the LLM training system"""
    
    def __init__(self):
        self.results = {
            "api_tests": {},
            "data_collection_tests": {},
            "training_tests": {},
            "overall_status": "pending"
        }
    
    def test_api_availability(self) -> bool:
        """Test if the training API is running and accessible"""
        print("🔍 Testing API availability...")
        
        try:
            response = requests.get(f"{API_BASE}/../", timeout=5)
            if response.status_code == 200:
                print("✅ Training API is accessible")
                self.results["api_tests"]["availability"] = True
                return True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                self.results["api_tests"]["availability"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ API is not accessible: {e}")
            self.results["api_tests"]["availability"] = False
            return False
    
    def test_statistics_endpoint(self) -> bool:
        """Test the statistics endpoint"""
        print("📊 Testing statistics endpoint...")
        
        try:
            response = requests.get(f"{API_BASE}/data/statistics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stats = data.get("statistics", {})
                    print(f"✅ Statistics retrieved: {stats.get('total_samples', 0)} total samples")
                    self.results["api_tests"]["statistics"] = True
                    return True
                else:
                    print("❌ Statistics endpoint returned unsuccessful response")
                    self.results["api_tests"]["statistics"] = False
                    return False
            else:
                print(f"❌ Statistics endpoint returned status: {response.status_code}")
                self.results["api_tests"]["statistics"] = False
                return False
        except Exception as e:
            print(f"❌ Error testing statistics endpoint: {e}")
            self.results["api_tests"]["statistics"] = False
            return False
    
    def test_transcription_feedback(self) -> bool:
        """Test transcription feedback submission"""
        print("📝 Testing transcription feedback submission...")
        
        success_count = 0
        total_samples = len(TEST_DATA["transcription_samples"])
        
        for i, sample in enumerate(TEST_DATA["transcription_samples"]):
            try:
                payload = {
                    "original_text": sample["original"],
                    "corrected_text": sample["corrected"],
                    "quality_score": sample["quality"],
                    "user_id": f"test_user_{i}"
                }
                
                response = requests.post(
                    f"{API_BASE}/feedback/transcription",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        success_count += 1
                        print(f"✅ Sample {i+1}/{total_samples} submitted successfully")
                    else:
                        print(f"❌ Sample {i+1}/{total_samples} submission failed")
                else:
                    print(f"❌ Sample {i+1}/{total_samples} returned status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error submitting sample {i+1}: {e}")
        
        success_rate = success_count / total_samples
        self.results["data_collection_tests"]["transcription_feedback"] = {
            "success_count": success_count,
            "total_samples": total_samples,
            "success_rate": success_rate
        }
        
        if success_rate >= 0.8:
            print(f"✅ Transcription feedback test passed ({success_count}/{total_samples})")
            return True
        else:
            print(f"❌ Transcription feedback test failed ({success_count}/{total_samples})")
            return False
    
    def test_dialect_samples(self) -> bool:
        """Test dialect sample submission"""
        print("🗣️ Testing dialect sample submission...")
        
        success_count = 0
        total_samples = len(TEST_DATA["dialect_samples"])
        
        for i, sample in enumerate(TEST_DATA["dialect_samples"]):
            try:
                payload = {
                    "standard_text": sample["standard"],
                    "dialect_text": sample["dialect"],
                    "dialect_name": sample["dialect_name"],
                    "quality_score": sample["quality"]
                }
                
                response = requests.post(
                    f"{API_BASE}/data/dialect",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        success_count += 1
                        print(f"✅ Dialect sample {i+1}/{total_samples} submitted successfully")
                    else:
                        print(f"❌ Dialect sample {i+1}/{total_samples} submission failed")
                else:
                    print(f"❌ Dialect sample {i+1}/{total_samples} returned status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error submitting dialect sample {i+1}: {e}")
        
        success_rate = success_count / total_samples
        self.results["data_collection_tests"]["dialect_samples"] = {
            "success_count": success_count,
            "total_samples": total_samples,
            "success_rate": success_rate
        }
        
        if success_rate >= 0.8:
            print(f"✅ Dialect samples test passed ({success_count}/{total_samples})")
            return True
        else:
            print(f"❌ Dialect samples test failed ({success_count}/{total_samples})")
            return False
    
    def test_available_models(self) -> bool:
        """Test available models endpoint"""
        print("🤖 Testing available models endpoint...")
        
        try:
            response = requests.get(f"{API_BASE}/models/available", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    models = data.get("models", [])
                    print(f"✅ Found {len(models)} available models")
                    for model in models:
                        print(f"   - {model.get('name')}: {model.get('description')}")
                    self.results["api_tests"]["available_models"] = True
                    return True
                else:
                    print("❌ Available models endpoint returned unsuccessful response")
                    self.results["api_tests"]["available_models"] = False
                    return False
            else:
                print(f"❌ Available models endpoint returned status: {response.status_code}")
                self.results["api_tests"]["available_models"] = False
                return False
        except Exception as e:
            print(f"❌ Error testing available models endpoint: {e}")
            self.results["api_tests"]["available_models"] = False
            return False
    
    def test_training_status(self) -> bool:
        """Test training status endpoint"""
        print("⚡ Testing training status endpoint...")
        
        try:
            response = requests.get(f"{API_BASE}/training/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    status = data.get("status", {})
                    print(f"✅ Training status retrieved: {status.get('status', 'unknown')}")
                    self.results["api_tests"]["training_status"] = True
                    return True
                else:
                    print("❌ Training status endpoint returned unsuccessful response")
                    self.results["api_tests"]["training_status"] = False
                    return False
            else:
                print(f"❌ Training status endpoint returned status: {response.status_code}")
                self.results["api_tests"]["training_status"] = False
                return False
        except Exception as e:
            print(f"❌ Error testing training status endpoint: {e}")
            self.results["api_tests"]["training_status"] = False
            return False
    
    def test_data_validation(self) -> bool:
        """Test that submitted data is properly stored and retrievable"""
        print("🔍 Testing data validation...")
        
        try:
            # Get updated statistics after data submission
            response = requests.get(f"{API_BASE}/data/statistics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stats = data.get("statistics", {})
                    total_samples = stats.get("total_samples", 0)
                    
                    expected_min_samples = len(TEST_DATA["transcription_samples"]) + len(TEST_DATA["dialect_samples"])
                    
                    if total_samples >= expected_min_samples:
                        print(f"✅ Data validation passed: {total_samples} samples found")
                        self.results["data_collection_tests"]["validation"] = True
                        return True
                    else:
                        print(f"❌ Data validation failed: expected at least {expected_min_samples}, found {total_samples}")
                        self.results["data_collection_tests"]["validation"] = False
                        return False
                else:
                    print("❌ Could not retrieve statistics for validation")
                    self.results["data_collection_tests"]["validation"] = False
                    return False
            else:
                print(f"❌ Statistics endpoint returned status: {response.status_code}")
                self.results["data_collection_tests"]["validation"] = False
                return False
        except Exception as e:
            print(f"❌ Error during data validation: {e}")
            self.results["data_collection_tests"]["validation"] = False
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🚀 Starting LLM Training System Tests")
        print("=" * 50)
        
        # Test API availability first
        if not self.test_api_availability():
            print("\n❌ API is not available. Please start the training API server first:")
            print("   python training_api.py")
            self.results["overall_status"] = "failed"
            return self.results
        
        # Run all tests
        tests = [
            ("Statistics Endpoint", self.test_statistics_endpoint),
            ("Available Models", self.test_available_models),
            ("Training Status", self.test_training_status),
            ("Transcription Feedback", self.test_transcription_feedback),
            ("Dialect Samples", self.test_dialect_samples),
            ("Data Validation", self.test_data_validation),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            if test_func():
                passed_tests += 1
            time.sleep(1)  # Brief pause between tests
        
        # Calculate overall results
        success_rate = passed_tests / total_tests
        
        print("\n" + "=" * 50)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 50)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {success_rate:.1%}")
        
        if success_rate >= 0.8:
            print("✅ Overall Status: PASSED")
            self.results["overall_status"] = "passed"
        else:
            print("❌ Overall Status: FAILED")
            self.results["overall_status"] = "failed"
        
        # Print detailed results
        print("\n📊 Detailed Results:")
        print(json.dumps(self.results, indent=2))
        
        return self.results

def main():
    """Main test execution"""
    print("LLM Training System Test Suite")
    print("Testing Arabic STT Training Infrastructure")
    print()
    
    tester = TrainingSystemTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("training_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Test results saved to: training_test_results.json")
    
    # Exit with appropriate code
    if results["overall_status"] == "passed":
        print("\n🎉 All tests completed successfully!")
        exit(0)
    else:
        print("\n⚠️ Some tests failed. Please check the results and fix issues.")
        exit(1)

if __name__ == "__main__":
    main()