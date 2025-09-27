#!/usr/bin/env python3
"""
Backend API testing script
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health(self) -> Dict[str, Any]:
        """Test basic health endpoint"""
        print("🔍 Testing health endpoint...")
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                data = await response.json()
                if response.status == 200 and data.get("status") == "healthy":
                    print("✅ Health check passed")
                    return {"status": "pass", "data": data}
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return {"status": "fail", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_detailed_health(self) -> Dict[str, Any]:
        """Test detailed health endpoint"""
        print("🔍 Testing detailed health endpoint...")
        
        try:
            async with self.session.get(f"{self.base_url}/health/detailed") as response:
                data = await response.json()
                if response.status == 200:
                    print("✅ Detailed health check passed")
                    print(f"   Database: {data.get('checks', {}).get('database', 'unknown')}")
                    print(f"   Redis: {data.get('checks', {}).get('redis', 'unknown')}")
                    print(f"   Storage: {data.get('checks', {}).get('storage', 'unknown')}")
                    return {"status": "pass", "data": data}
                else:
                    print(f"❌ Detailed health check failed: {response.status}")
                    return {"status": "fail", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Detailed health check error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_registration(self) -> Dict[str, Any]:
        """Test user registration"""
        print("🔍 Testing user registration...")
        
        test_user = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "testpassword123",
            "first_name": "أحمد", 
            "last_name": "التجريبي",
            "organization_name": "شركة التجريب"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/v1/auth/register",
                json=test_user
            ) as response:
                data = await response.json()
                if response.status == 200 and data.get("access_token"):
                    print("✅ User registration passed")
                    self.auth_token = data.get("access_token")
                    return {"status": "pass", "data": data, "user": test_user}
                else:
                    print(f"❌ User registration failed: {response.status}")
                    print(f"   Response: {data}")
                    return {"status": "fail", "error": f"HTTP {response.status}", "response": data}
        except Exception as e:
            print(f"❌ User registration error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_protected_endpoint(self) -> Dict[str, Any]:
        """Test protected endpoint with authentication"""
        print("🔍 Testing protected endpoint...")
        
        if not self.auth_token:
            return {"status": "skip", "error": "No auth token available"}
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(
                f"{self.base_url}/v1/auth/me",
                headers=headers
            ) as response:
                data = await response.json()
                if response.status == 200 and data.get("email"):
                    print("✅ Protected endpoint test passed")
                    return {"status": "pass", "data": data}
                else:
                    print(f"❌ Protected endpoint test failed: {response.status}")
                    return {"status": "fail", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Protected endpoint error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_metrics(self) -> Dict[str, Any]:
        """Test metrics endpoint"""
        print("🔍 Testing metrics endpoint...")
        
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    content = await response.text()
                    if "api_requests_total" in content:
                        print("✅ Metrics endpoint test passed")
                        return {"status": "pass", "data": "metrics_available"}
                    else:
                        print("❌ Metrics content invalid")
                        return {"status": "fail", "error": "invalid_metrics"}
                else:
                    print(f"❌ Metrics endpoint failed: {response.status}")
                    return {"status": "fail", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Metrics endpoint error: {e}")
            return {"status": "error", "error": str(e)}

async def run_tests():
    """Run all backend tests"""
    print("🚀 Starting Arabic STT SaaS Backend Tests")
    print("=" * 50)
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "tests": []
    }
    
    async with APITester() as tester:
        # Test health endpoint
        result = await tester.test_health()
        results["tests"].append({"name": "Health Check", **result})
        results["total"] += 1
        if result["status"] == "pass":
            results["passed"] += 1
        elif result["status"] == "fail":
            results["failed"] += 1
        else:
            results["errors"] += 1
        
        # Test detailed health
        result = await tester.test_detailed_health()
        results["tests"].append({"name": "Detailed Health Check", **result})
        results["total"] += 1
        if result["status"] == "pass":
            results["passed"] += 1
        elif result["status"] == "fail":
            results["failed"] += 1
        else:
            results["errors"] += 1
        
        # Test metrics
        result = await tester.test_metrics()
        results["tests"].append({"name": "Metrics Endpoint", **result})
        results["total"] += 1
        if result["status"] == "pass":
            results["passed"] += 1
        elif result["status"] == "fail":
            results["failed"] += 1
        else:
            results["errors"] += 1
        
        # Test registration
        result = await tester.test_registration()
        results["tests"].append({"name": "User Registration", **result})
        results["total"] += 1
        if result["status"] == "pass":
            results["passed"] += 1
        elif result["status"] == "fail":
            results["failed"] += 1
        else:
            results["errors"] += 1
        
        # Test protected endpoint
        result = await tester.test_protected_endpoint()
        results["tests"].append({"name": "Protected Endpoint", **result})
        results["total"] += 1
        if result["status"] == "pass":
            results["passed"] += 1
        elif result["status"] == "fail":
            results["failed"] += 1
        elif result["status"] == "skip":
            results["skipped"] += 1
        else:
            results["errors"] += 1
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"Total Tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"🔥 Errors: {results['errors']}")
    print(f"⏭️  Skipped: {results['skipped']}")
    
    if results['failed'] > 0 or results['errors'] > 0:
        print("\n❌ Some tests failed. Check the API service logs.")
        return False
    else:
        print("\n🎉 All tests passed! Backend is working correctly.")
        return True

if __name__ == "__main__":
    success = asyncio.run(run_tests())
    exit(0 if success else 1)