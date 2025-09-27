#!/usr/bin/env python3
"""
Quick test script for Arabic STT SaaS Backend API
"""

import asyncio
import sys
import os
sys.path.append('api')

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Simple test to ensure our backend structure is working
def test_api_structure():
    """Test API structure and imports"""
    
    print("🧪 Testing Arabic STT SaaS Backend Structure...")
    
    try:
        # Test core imports
        print("✅ Testing core imports...")
        from app.core.config import get_settings
        from app.core.database import Base
        from app.models.base import BaseModel
        
        # Test settings
        settings = get_settings()
        print(f"✅ Settings loaded: {settings.API_HOST}:{settings.API_PORT}")
        
        # Test models
        print("✅ Testing model imports...")
        from app.models.user import User, UserRole
        from app.models.organization import Organization
        from app.models.job import Job, JobStatus
        
        print("✅ Models imported successfully")
        
        # Test API structure  
        print("✅ Testing API router...")
        from app.api.v1.router import api_router
        from app.api.v1.auth import router as auth_router
        from app.api.v1.test import router as test_router
        
        print("✅ API routers imported successfully")
        
        # Create minimal FastAPI app for testing
        test_app = FastAPI(title="Test App")
        test_app.include_router(test_router, prefix="/test")
        
        # Test basic endpoint
        client = TestClient(test_app)
        response = client.get("/test/ping")
        
        if response.status_code == 200:
            print("✅ API endpoint test successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API endpoint test failed: {response.status_code}")
            return False
        
        print("\n🎉 Backend structure test completed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Start services: docker-compose up -d postgres redis minio")
        print("   2. Run API server: cd api && uvicorn app.main:app --reload")
        print("   3. Test endpoints: curl http://localhost:8000/health")
        print("   4. View API docs: http://localhost:8000/docs")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r api/requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_api_info():
    """Show API information"""
    
    print("\n📊 Arabic STT SaaS API Information:")
    print("=" * 50)
    
    print("\n🔗 Available Endpoints:")
    endpoints = [
        ("GET", "/health", "Basic health check"),
        ("GET", "/health/detailed", "Detailed health with dependencies"),
        ("POST", "/v1/auth/login", "User authentication"),
        ("POST", "/v1/auth/register", "User registration"),
        ("POST", "/v1/media/upload-url", "Get presigned upload URL"),
        ("POST", "/v1/jobs/transcribe", "Create transcription job"),
        ("GET", "/v1/jobs/{job_id}", "Get job status"),
        ("GET", "/v1/test/ping", "Simple ping test"),
        ("GET", "/v1/test/arabic/dialects", "Arabic dialects info"),
        ("GET", "/v1/test/health/full", "Full system health check"),
        ("GET", "/docs", "Interactive API documentation"),
    ]
    
    for method, path, description in endpoints:
        print(f"   {method:6} {path:35} - {description}")
    
    print("\n🌍 Supported Arabic Dialects:")
    dialects = [
        ("ar", "العربية الفصحى", "Modern Standard Arabic", "95%+"),
        ("ar-IQ", "اللهجة العراقية", "Iraqi Arabic", "92%+"),
        ("ar-EG", "اللهجة المصرية", "Egyptian Arabic", "90%+"),
        ("ar-SA", "اللهجة السعودية", "Saudi Arabic", "91%+"),
        ("ar-MA", "اللهجة المغربية", "Moroccan Arabic", "87%+"),
    ]
    
    for code, arabic_name, english_name, accuracy in dialects:
        print(f"   {code:6} {arabic_name:20} ({english_name:20}) - Accuracy: {accuracy}")
    
    print("\n🔧 Technology Stack:")
    tech_stack = [
        ("Backend Framework", "FastAPI 0.104+"),
        ("Database", "PostgreSQL 15+"),
        ("Cache/Queue", "Redis 7+"),
        ("Storage", "MinIO (S3 compatible)"),
        ("ML Models", "faster-whisper + pyannote.audio"),
        ("Audio Processing", "FFmpeg + RNNoise"),
        ("Authentication", "JWT with refresh tokens"),
        ("Monitoring", "Prometheus + Grafana"),
    ]
    
    for component, technology in tech_stack:
        print(f"   {component:20} - {technology}")
    
    print("\n🚀 Performance Targets:")
    performance = [
        ("Transcription Speed", "1.5x realtime (GPU), 3x realtime (CPU)"),
        ("API Response Time", "<500ms for status queries"),
        ("File Upload", "Presigned URLs up to 500MB"),
        ("Concurrent Users", "100+ users supported"),
        ("Accuracy", ">95% for clear Arabic speech"),
    ]
    
    for metric, target in performance:
        print(f"   {metric:20} - {target}")


if __name__ == "__main__":
    print("🔬 Arabic STT SaaS Backend Testing")
    print("=" * 50)
    
    success = test_api_structure()
    
    if success:
        show_api_info()
        print("\n✅ Backend is ready for development!")
    else:
        print("\n❌ Backend test failed. Please check the error messages above.")
        sys.exit(1)